# Copyright (c) 2006-2012 Mitch Garnaat http://garnaat.org/
# Copyright (c) 2012 Amazon.com, Inc. or its affiliates.
# Copyright (c) 2010 Google
# Copyright (c) 2008 rPath, Inc.
# Copyright (c) 2009 The Echo Nest Corporation
# Copyright (c) 2010, Eucalyptus Systems, Inc.
# Copyright (c) 2011, Nexenta Systems Inc.
# Copyright (c) 2012, Trend Micro, Inc.
# All rights reserved.
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish, dis-
# tribute, sublicense, and/or sell copies of the Software, and to permit
# persons to whom the Software is furnished to do so, subject to the fol-
# lowing conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
# OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABIL-
# ITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT
# SHALL THE AUTHOR BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.

#
# Parts of this code were copied or derived from sample code supplied by AWS.
# The following notice applies to that code.
#
#  This software code is made available "AS IS" without warranties of any
#  kind.  You may copy, display, modify and redistribute the software
#  code either by itself or as incorporated into your code; provided that
#  you do not remove any proprietary notices.  Your use of this software
#  code is at your own risk and you waive any claim against Amazon
#  Digital Services, Inc. or its affiliates with respect to your use of
#  this software code. (c) 2006 Amazon Digital Services, Inc. or its
#  affiliates.

"""
Handles basic connections to Trend Micro SecureCloud
"""

from __future__ import with_statement
import base64
import errno
import httplib
import os
import Queue
import random
import re
import socket
import sys
import time
import urlparse
import xml.sax
import copy
import logging
import urllib2
from xml.dom.minidom import parse, parseString
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from Crypto import Hash

import sclib

from sclib import __config__, UserAgent
from sclib.sc.scobject import SCObject
from sclib.exception import SCServerError, SCClientError
from sclib.resultset import ResultSet

HAVE_HTTPS_CONNECTION = False
LOG_LEVEL = "DEBUG"
logging.basicConfig(level=LOG_LEVEL)


try:
    import threading
except ImportError:
    import dummy_threading as threading

class HostConnectionPool(object):

    """
    A pool of connections for one remote (host,is_secure).

    When connections are added to the pool, they are put into a
    pending queue.  The _mexe method returns connections to the pool
    before the response body has been read, so they connections aren't
    ready to send another request yet.  They stay in the pending queue
    until they are ready for another request, at which point they are
    returned to the pool of ready connections.

    The pool of ready connections is an ordered list of
    (connection,time) pairs, where the time is the time the connection
    was returned from _mexe.  After a certain period of time,
    connections are considered stale, and discarded rather than being
    reused.  This saves having to wait for the connection to time out
    if AWS has decided to close it on the other end because of
    inactivity.

    Thread Safety:

        This class is used only fram ConnectionPool while it's mutex
        is held.
    """

    def __init__(self):
        self.queue = []

    def size(self):
        """
        Returns the number of connections in the pool for this host.
        Some of the connections may still be in use, and may not be
        ready to be returned by get().
        """
        return len(self.queue)

    def put(self, conn):
        """
        Adds a connection to the pool, along with the time it was
        added.
        """
        self.queue.append((conn, time.time()))

    def get(self):
        """
        Returns the next connection in this pool that is ready to be
        reused.  Returns None of there aren't any.
        """
        # Discard ready connections that are too old.
        self.clean()

        # Return the first connection that is ready, and remove it
        # from the queue.  Connections that aren't ready are returned
        # to the end of the queue with an updated time, on the
        # assumption that somebody is actively reading the response.
        for _ in range(len(self.queue)):
            (conn, _) = self.queue.pop(0)
            if self._conn_ready(conn):
                return conn
            else:
                self.put(conn)
        return None

    def _conn_ready(self, conn):
        """
        There is a nice state diagram at the top of httplib.py.  It
        indicates that once the response headers have been read (which
        _mexe does before adding the connection to the pool), a
        response is attached to the connection, and it stays there
        until it's done reading.  This isn't entirely true: even after
        the client is done reading, the response may be closed, but
        not removed from the connection yet.

        This is ugly, reading a private instance variable, but the
        state we care about isn't available in any public methods.
        """
        response = getattr(conn, '_HTTPConnection__response', None)
        return (response is None) or response.isclosed()

    def clean(self):
        """
        Get rid of stale connections.
        """
        # Note that we do not close the connection here -- somebody
        # may still be reading from it.
        while len(self.queue) > 0 and self._pair_stale(self.queue[0]):
            self.queue.pop(0)

    def _pair_stale(self, pair):
        """
        Returns true of the (connection,time) pair is too old to be
        used.
        """
        (_conn, return_time) = pair
        now = time.time()
        return return_time + ConnectionPool.STALE_DURATION < now


class ConnectionPool(object):

    """
    A connection pool that expires connections after a fixed period of
    time.  This saves time spent waiting for a connection that AWS has
    timed out on the other end.

    This class is thread-safe.
    """

    #
    # The amout of time between calls to clean.
    #

    CLEAN_INTERVAL = 5.0

    #
    # How long before a connection becomes "stale" and won't be reused
    # again.  The intention is that this time is less that the timeout
    # period that AWS uses, so we'll never try to reuse a connection
    # and find that AWS is timing it out.
    #
    # Experimentation in July 2011 shows that AWS starts timing things
    # out after three minutes.  The 60 seconds here is conservative so
    # we should never hit that 3-minute timout.
    #

    STALE_DURATION = 60.0

    def __init__(self):
        # Mapping from (host,is_secure) to HostConnectionPool.
        # If a pool becomes empty, it is removed.
        self.host_to_pool = {}
        # The last time the pool was cleaned.
        self.last_clean_time = 0.0
        self.mutex = threading.Lock()
        ConnectionPool.STALE_DURATION = \
            __config__.getfloat('sclib', 'connection_stale_duration',
                            ConnectionPool.STALE_DURATION)

    def __getstate__(self):
        pickled_dict = copy.copy(self.__dict__)
        pickled_dict['host_to_pool'] = {}
        del pickled_dict['mutex']
        return pickled_dict

    def __setstate__(self, dct):
        self.__init__()

    def size(self):
        """
        Returns the number of connections in the pool.
        """
        return sum(pool.size() for pool in self.host_to_pool.values())

    def get_http_connection(self, host, is_secure):
        """
        Gets a connection from the pool for the named host.  Returns
        None if there is no connection that can be reused. It's the caller's
        responsibility to call close() on the connection when it's no longer
        needed.
        """
        self.clean()
        with self.mutex:
            key = (host, is_secure)
            if key not in self.host_to_pool:
                return None
            return self.host_to_pool[key].get()

    def put_http_connection(self, host, is_secure, conn):
        """
        Adds a connection to the pool of connections that can be
        reused for the named host.
        """
        with self.mutex:
            key = (host, is_secure)
            if key not in self.host_to_pool:
                self.host_to_pool[key] = HostConnectionPool()
            self.host_to_pool[key].put(conn)

    def clean(self):
        """
        Clean up the stale connections in all of the pools, and then
        get rid of empty pools.  Pools clean themselves every time a
        connection is fetched; this cleaning takes care of pools that
        aren't being used any more, so nothing is being gotten from
        them.
        """
        with self.mutex:
            now = time.time()
            if self.last_clean_time + self.CLEAN_INTERVAL < now:
                to_remove = []
                for (host, pool) in self.host_to_pool.items():
                    pool.clean()
                    if pool.size() == 0:
                        to_remove.append(host)
                for host in to_remove:
                    del self.host_to_pool[host]
                self.last_clean_time = now


class HTTPRequest(object):

    def __init__(self, method, host, port, path,
                 params, headers, body):
        """Represents an HTTP request.

        :type method: string
        :param method: The HTTP method name, 'GET', 'POST', 'PUT' etc.

        :type host: string
        :param host: Host to which the request is addressed. eg. abc.com

        :type port: int
        :param port: port on which the request is being sent. Zero means unset,
            in which case default port will be chosen.

        :type path: string
        :param path: URL path that is being accessed.

        :type params: dict
        :param params: HTTP url query parameters, with key as name of
            the param, and value as value of param.

        :type headers: dict
        :param headers: HTTP headers, with key as name of the header and value
            as value of header.

        :type body: string
        :param body: Body of the HTTP request. If not present, will be None or
            empty string ('').
        """
        self.method = method
        self.host = host
        self.port = port
        self.path = path
        self.params = params
        self.req_path = ''
        # chunked Transfer-Encoding should act only on PUT request.
        if headers and 'Transfer-Encoding' in headers and \
                headers['Transfer-Encoding'] == 'chunked' and \
                self.method != 'PUT':
            self.headers = headers.copy()
            del self.headers['Transfer-Encoding']
        else:
            self.headers = headers
        self.body = body

    def __str__(self):
        return (('method:(%s) protocol:(%s) host(%s) port(%s) path(%s) '
                 'req_path(%s) params(%s) headers(%s) body(%s)') % (self.method,
                 self.protocol, self.host, self.port, self.path, self.req_path,
                 self.params, self.headers, self.body))

class HTTPResponse(object):

    def __init__(self, *args, **kwargs):
        httplib.HTTPResponse.__init__(self, *args, **kwargs)
        self._cached_response = ''

    def read(self, amt=None):
        """Read the response.

        This method does not have the same behavior as
        httplib.HTTPResponse.read.  Instead, if this method is called with
        no ``amt`` arg, then the response body will be cached.  Subsequent
        calls to ``read()`` with no args **will return the cached response**.

        """
        if amt is None:
            # The reason for doing this is that many places in sclib call
            # response.read() and except to get the response body that they
            # can then process.  To make sure this always works as they expect
            # we're caching the response so that multiple calls to read()
            # will return the full body.  Note that this behavior only
            # happens if the amt arg is not specified.
            if not self._cached_response:
                self._cached_response = httplib.HTTPResponse.read(self)
            return self._cached_response
        else:
            return httplib.HTTPResponse.read(self, amt)

class SCAuthentication(SCObject):
    def __init__(self, id=None, token=None, expires=None):
        self.id = id
        self.token = token
        self.expires = expires
        
    def parse(self, xml_data):
        xmldata = xml.dom.minidom.parseString(xml_data)
        auth_result = xmldata.getElementsByTagName("authenticationResult")[0]
        self.id = auth_result.attributes["id"].value.strip()
        self.token = auth_result.attributes["token"].value.strip()
        self.expires = auth_result.attributes["expires"].value.strip()
        
    def isAuthenticated(self):
        return self.token != None


class SCAuthConnection:
    def __init__( self, host_base, broker_name=None, broker_passphase=None):

        self.base_url = host_base
        self.broker = broker_name
        self.broker_passphrase = broker_passphase
        self.realm = "securecloud@trend.com"
        
        self.headers = {'Content-Type' : 'application/xml; charset=utf-8',
                        'BrokerName' : self.broker
                        }
        
        self.pwd_mgr = urllib2.HTTPPasswordMgr()
        self.pwd_mgr.add_password(self.realm, self.base_url, self.broker, self.broker_passphrase)
        self.opener = urllib2.build_opener()
        self.opener.add_handler(urllib2.HTTPDigestAuthHandler(self.pwd_mgr))

    # ----- help function ends

    def nice_format(self, data):
        xmlstr = parseString(data)
        pretty_res = xmlstr.toprettyxml()

        return pretty_res

    # ----- help function start -----
    
    def build_request(self, req_url, params=None, headers=None, data=None, method='GET'):
        req = urllib2.Request(req_url)

        # add default headers
        for key, value in self.headers.iteritems():
            req.add_header(key, value)

        # add additional headers
        if headers != None:
            for key, value in headers.iteritems():
                req.add_header(key, value)
            
        if method == 'POST' and data != '':
            req.add_data(data)
        elif method == 'DELETE':
            req.get_method = lambda: 'DELETE'
        else:
            pass
        
        logging.debug("===== Request ===== ")
        logging.debug('method: %s' % (method))
        logging.debug('url = %s' %(req_url))
        if data: logging.debug('data = %s' % (data))
        logging.debug("=================== ")
        return req
        
    def make_request(self, action='', params=None, headers=None, data='', method='GET'):

        logging.debug(">>>>> make_request")
        api_url = self.base_url+ '/' + action
        req = self.build_request(api_url, params, headers, data, method)

        try:
            response = self.opener.open(req)
            body = response.read()
            if response.code == 200:
                sclib.log.debug(self.nice_format(body))
                logging.debug("<<<<< make_request")
                return body
            else:
                if not body:
                    sclib.log.error('Null body %s' % body)
                else:
                    sclib.log.error('%s %s' % (response.status, response.reason))
                    sclib.log.error('%s' % body)
                raise self.ResponseError(response.status, response.reason, body)
        except urllib2.HTTPError, e:
            logging.error(e)

        return None

    def close(self):
        """(Optional) Close any open HTTP connections.  This is non-destructive,
        and making a new request will open a connection again."""

        sclib.log.debug('closing all HTTP connections')
        self._connection = None  # compact field


class SCQueryConnection(SCAuthConnection):

    APIVersion = ''
    ResponseError = SCServerError

    def __init__(self, host_base, broker_name=None, broker_passphase=None):
        SCAuthConnection.__init__(self, host_base, broker_name, broker_passphase)

    def get_utf8_value(self, value):
        return sclib.utils.get_utf8_value(value)

    def build_list_params(self, params, items, label):
        if isinstance(items, str):
            items = [items]
        for i in range(1, len(items) + 1):
            params['%s.%d' % (label, i)] = items[i - 1]

    # generics

    def get_list(self, action, params, markers, headers=None, data='', path='/', parent=None, method='GET'):
        if not parent:
            parent = self
        body = self.make_request(action, headers=headers, data=data, method=method)
        sclib.log.debug(self.nice_format(body))
        if body:
            rs = ResultSet(markers)
            h = sclib.handler.XmlHandler(rs, parent)
            xml.sax.parseString(body, h)
            return rs
        return None

    def get_object(self, action, params, cls, headers=None, data='',path='/', parent=None, method='GET'):
        if not parent:
            parent = self
        body = self.make_request(action, headers=headers, data=data, method=method)
        sclib.log.debug(self.nice_format(body))
        if body:
            obj = cls(parent)
            h = sclib.handler.XmlHandler(obj, parent)
            xml.sax.parseString(body, h)
            return obj
        return None

    def get_status(self, action='GET', headers=None, data='', params=None, path='/', parent=None):
        if not parent:
            parent = self
        body = self.make_request(action)
        sclib.log.debug(body)

        if body:
            rs = ResultSet()
            h = sclib.handler.XmlHandler(rs, parent)
            xml.sax.parseString(body, h)
            return rs.status

        return None
        