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
import urllib
import urlparse
import xml.sax
import copy

import sclib
import sclib.cacerts

from sclib import __config__, UserAgent
from sclib.exception import SCServerError, SCClientError
from sclib.provider import Provider
from sclib.resultset import ResultSet

HAVE_HTTPS_CONNECTION = False

try:
    import threading
except ImportError:
    import dummy_threading as threading

DEFAULT_CA_CERTS_FILE = os.path.join(os.path.dirname(os.path.abspath(sclib.cacerts.__file__ )), "cacerts.txt")

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
                 'params(%s) headers(%s) body(%s)') % (self.method,
                 self.protocol, self.host, self.port, self.path, self.params,
                 self.headers, self.body))

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


class SCAuthConnection(object):
    def __init__(self, host, port=None, path='/',
                 broker=None, broker_passphase=None, auth_name='', auth_password=''):
        """
        :type host: str
        :param host: The host to make the connection to

        :keyword str aws_access_key_id: Your AWS Access Key ID (provided by
            Amazon). If none is specified, the value in your
            ``AWS_ACCESS_KEY_ID`` environmental variable is used.
        :keyword str aws_secret_access_key: Your AWS Secret Access Key
            (provided by Amazon). If none is specified, the value in your
            ``AWS_SECRET_ACCESS_KEY`` environmental variable is used.

        :type is_secure: boolean
        :param is_secure: Whether the connection is over SSL

        :type https_connection_factory: list or tuple
        :param https_connection_factory: A pair of an HTTP connection
            factory and the exceptions to catch.  The factory should have
            a similar interface to L{httplib.HTTPSConnection}.

        :type port: int
        :param port: The port to use to connect

        """
        self.num_retries = 6
        self.http_exceptions = (httplib.HTTPException, socket.error,
                                socket.gaierror)
        # define subclasses of the above that are not retryable.
        self.http_unretryable_exceptions = []

         
        self.host = host
        self.port = port
        self.path = path
        self.broker = broker
        self.broker_passphase = broker_passphase
        self.auth_name = auth_name
        self.auth_password = auth_password
        
        self._pool = ConnectionPool()
        self._connection = (self.server_name(), self.is_secure)
        self._last_rs = None

    def __repr__(self):
        return '%s:%s' % (self.__class__.__name__, self.host)

    def _required_auth_capability(self):
        return []

    def connection(self):
        return self.get_http_connection(*self._connection)

    def get_path(self, path='/'):
        # The default behavior is to suppress consecutive slashes for reasons
        # discussed at
        # https://groups.google.com/forum/#!topic/sclib-dev/-ft0XPUy0y8
        # You can override that behavior with the suppress_consec_slashes param.
        if not self.suppress_consec_slashes:
            return self.path + re.sub('^/*', "", path)
        pos = path.find('?')
        if pos >= 0:
            params = path[pos:]
            path = path[:pos]
        else:
            params = None
        if path[-1] == '/':
            need_trailing = True
        else:
            need_trailing = False
        path_elements = self.path.split('/')
        path_elements.extend(path.split('/'))
        path_elements = [p for p in path_elements if p]
        path = '/' + '/'.join(path_elements)
        if path[-1] != '/' and need_trailing:
            path += '/'
        if params:
            path = path + params
        return path

    def server_name(self, port=None):
        if not port:
            port = self.port
        if port == 80:
            signature_host = self.host
        else:
            # This unfortunate little hack can be attributed to
            # a difference in the 2.6 version of httplib.  In old
            # versions, it would append ":443" to the hostname sent
            # in the Host header and so we needed to make sure we
            # did the same when calculating the V2 signature.  In 2.6
            # (and higher!)
            # it no longer does that.  Hence, this kludge.
            if ((ON_APP_ENGINE and sys.version[:3] == '2.5') or
                    sys.version[:3] in ('2.6', '2.7')) and port == 443:
                signature_host = self.host
            else:
                signature_host = '%s:%d' % (self.host, port)
        return signature_host

    def get_http_connection(self, host, is_secure):
        conn = self._pool.get_http_connection(host, is_secure)
        if conn is not None:
            return conn
        else:
            return self.new_http_connection(host, is_secure)

    def new_http_connection(self, host, is_secure):
        if self.use_proxy:
            host = '%s:%d' % (self.proxy, int(self.proxy_port))
        if host is None:
            host = self.server_name()
        if is_secure:
            sclib.log.debug(
                    'establishing HTTPS connection: host=%s, kwargs=%s',
                    host, self.http_connection_kwargs)
            if self.use_proxy:
                connection = self.proxy_ssl()
            elif self.https_connection_factory:
                connection = self.https_connection_factory(host)
            elif self.https_validate_certificates and HAVE_HTTPS_CONNECTION:
                connection = https_connection.CertValidatingHTTPSConnection(
                        host, ca_certs=self.ca_certificates_file,
                        **self.http_connection_kwargs)
            else:
                connection = httplib.HTTPSConnection(host,
                        **self.http_connection_kwargs)
        else:
            sclib.log.debug('establishing HTTP connection: kwargs=%s' %
                    self.http_connection_kwargs)
            if self.https_connection_factory:
                # even though the factory says https, this is too handy
                # to not be able to allow overriding for http also.
                connection = self.https_connection_factory(host,
                    **self.http_connection_kwargs)
            else:
                connection = httplib.HTTPConnection(host,
                    **self.http_connection_kwargs)
        if self.debug > 1:
            connection.set_debuglevel(self.debug)
        # self.connection must be maintained for backwards-compatibility
        # however, it must be dynamically pulled from the connection pool
        # set a private variable which will enable that
        if host.split(':')[0] == self.host and is_secure == self.is_secure:
            self._connection = (host, is_secure)
        # Set the response class of the http connection to use our custom
        # class.
        connection.response_class = HTTPResponse
        return connection

    def put_http_connection(self, host, is_secure, connection):
        self._pool.put_http_connection(host, is_secure, connection)

    def _mexe(self, request, sender=None, override_num_retries=None,
              retry_handler=None):
        """
        mexe - Multi-execute inside a loop, retrying multiple times to handle
               transient Internet errors by simply trying again.
               Also handles redirects.

        This code was inspired by the S3Utils classes posted to the sclib-users
        Google group by Larry Bates.  Thanks!

        """
        sclib.log.debug('Method: %s' % request.method)
        sclib.log.debug('Path: %s' % request.path)
        sclib.log.debug('Data: %s' % request.body)
        sclib.log.debug('Headers: %s' % request.headers)
        sclib.log.debug('Host: %s' % request.host)
        response = None
        body = None
        e = None
        if override_num_retries is None:
            num_retries = __config__.getint('sclib', 'num_retries', self.num_retries)
        else:
            num_retries = override_num_retries
        i = 0
        connection = self.get_http_connection(request.host, self.is_secure)
        while i <= num_retries:
            # Use binary exponential backoff to desynchronize client requests
            next_sleep = random.random() * (2 ** i)
            try:
                # we now re-sign each request before it is retried
                sclib.log.debug('Token: %s' % self.provider.security_token)
                request.authorize(connection=self)
                if callable(sender):
                    response = sender(connection, request.method, request.path,
                                      request.body, request.headers)
                else:
                    connection.request(request.method, request.path,
                                       request.body, request.headers)
                    response = connection.getresponse()
                location = response.getheader('location')
                # -- gross hack --
                # httplib gets confused with chunked responses to HEAD requests
                # so I have to fake it out
                if request.method == 'HEAD' and getattr(response,
                                                        'chunked', False):
                    response.chunked = 0
                if callable(retry_handler):
                    status = retry_handler(response, i, next_sleep)
                    if status:
                        msg, i, next_sleep = status
                        if msg:
                            sclib.log.debug(msg)
                        time.sleep(next_sleep)
                        continue
                if response.status == 500 or response.status == 503:
                    msg = 'Received %d response.  ' % response.status
                    msg += 'Retrying in %3.1f seconds' % next_sleep
                    sclib.log.debug(msg)
                    body = response.read()
                elif response.status < 300 or response.status >= 400 or \
                        not location:
                    self.put_http_connection(request.host, self.is_secure,
                                             connection)
                    return response
                else:
                    scheme, request.host, request.path, \
                        params, query, fragment = urlparse.urlparse(location)
                    if query:
                        request.path += '?' + query
                    msg = 'Redirecting: %s' % scheme + '://'
                    msg += request.host + request.path
                    sclib.log.debug(msg)
                    connection = self.get_http_connection(request.host,
                                                          scheme == 'https')
                    response = None
                    continue
            except self.http_exceptions, e:
                for unretryable in self.http_unretryable_exceptions:
                    if isinstance(e, unretryable):
                        sclib.log.debug(
                            'encountered unretryable %s exception, re-raising' %
                            e.__class__.__name__)
                        raise e
                sclib.log.debug('encountered %s exception, reconnecting' % \
                                  e.__class__.__name__)
                connection = self.new_http_connection(request.host,
                                                      self.is_secure)
            time.sleep(next_sleep)
            i += 1
        # If we made it here, it's because we have exhausted our retries
        # and stil haven't succeeded.  So, if we have a response object,
        # use it to raise an exception.
        # Otherwise, raise the exception that must have already h#appened.
        if response:
            raise SCServerError(response.status, response.reason, body)
        elif e:
            raise e
        else:
            msg = 'Please report this exception as a Boto Issue!'
            raise SCClientError(msg)

    def build_base_http_request(self, method, path, params=None, headers=None, data=''):
        path = self.get_path(path)
        
        # empty params?
        if params == None:
            params = {}
        else:
            params = params.copy()
            
        # request header?
        if headers == None:
            headers = {}
        else:
            headers = headers.copy()
            
        return HTTPRequest(method, self.host, self.port, self.path, headers, data)

    def make_request(self, method, path, params=None, headers=None, data='', override_num_retries=None):
        """Makes a request to the server, with stock multiple-retry logic."""
        if params is None:
            params = {}
        http_request = self.build_base_http_request(method, path, params, headers, data)
        return self._mexe(http_request, override_num_retries)

    def close(self):
        """(Optional) Close any open HTTP connections.  This is non-destructive,
        and making a new request will open a connection again."""

        sclib.log.debug('closing all HTTP connections')
        self._connection = None  # compact field


class SCQueryConnection(SCAuthConnection):

    APIVersion = ''
    ResponseError = SCServerError

    def __init__(self, aws_access_key_id=None, aws_secret_access_key=None,
                 is_secure=True, port=None, proxy=None, proxy_port=None,
                 proxy_user=None, proxy_pass=None, host=None, debug=0,
                 https_connection_factory=None, path='/', security_token=None,
                 validate_certs=True):
        SCAuthConnection.__init__(self, host, aws_access_key_id,
                                   aws_secret_access_key,
                                   is_secure, port, proxy,
                                   proxy_port, proxy_user, proxy_pass,
                                   debug, https_connection_factory, path,
                                   security_token=security_token,
                                   validate_certs=validate_certs)

    def _required_auth_capability(self):
        return []

    def get_utf8_value(self, value):
        return sclib.utils.get_utf8_value(value)

    def make_request(self, action, params=None, path='/', verb='GET'):
        http_request = self.build_base_http_request(verb, path, None,
                                                    params, {}, '',
                                                    self.server_name())
        if action:
            http_request.params['Action'] = action
        if self.APIVersion:
            http_request.params['Version'] = self.APIVersion
        return self._mexe(http_request)

    def build_list_params(self, params, items, label):
        if isinstance(items, str):
            items = [items]
        for i in range(1, len(items) + 1):
            params['%s.%d' % (label, i)] = items[i - 1]

    # generics

    def get_list(self, action, params, markers, path='/',
                 parent=None, verb='GET'):
        if not parent:
            parent = self
        response = self.make_request(action, params, path, verb)
        body = response.read()
        sclib.log.debug(body)
        if not body:
            sclib.log.error('Null body %s' % body)
            raise self.ResponseError(response.status, response.reason, body)
        elif response.status == 200:
            rs = ResultSet(markers)
            h = sclib.handler.XmlHandler(rs, parent)
            xml.sax.parseString(body, h)
            return rs
        else:
            sclib.log.error('%s %s' % (response.status, response.reason))
            sclib.log.error('%s' % body)
            raise self.ResponseError(response.status, response.reason, body)

    def get_object(self, action, params, cls, path='/',
                   parent=None, verb='GET'):
        if not parent:
            parent = self
        response = self.make_request(action, params, path, verb)
        body = response.read()
        sclib.log.debug(body)
        if not body:
            sclib.log.error('Null body %s' % body)
            raise self.ResponseError(response.status, response.reason, body)
        elif response.status == 200:
            obj = cls(parent)
            h = sclib.handler.XmlHandler(obj, parent)
            xml.sax.parseString(body, h)
            return obj
        else:
            sclib.log.error('%s %s' % (response.status, response.reason))
            sclib.log.error('%s' % body)
            raise self.ResponseError(response.status, response.reason, body)

    def get_status(self, action, params, path='/', parent=None, verb='GET'):
        if not parent:
            parent = self
        response = self.make_request(action, params, path, verb)
        body = response.read()
        sclib.log.debug(body)
        if not body:
            sclib.log.error('Null body %s' % body)
            raise self.ResponseError(response.status, response.reason, body)
        elif response.status == 200:
            rs = ResultSet()
            h = sclib.handler.XmlHandler(rs, parent)
            xml.sax.parseString(body, h)
            return rs.status
        else:
            sclib.log.error('%s %s' % (response.status, response.reason))
            sclib.log.error('%s' % body)
            raise self.ResponseError(response.status, response.reason, body)
