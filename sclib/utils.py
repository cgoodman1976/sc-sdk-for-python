# Copyright (c) 2006-2012 Mitch Garnaat http://garnaat.org/
# Copyright (c) 2010, Eucalyptus Systems, Inc.
# Copyright (c) 2012 Amazon.com, Inc. or its affiliates.
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
Some handy utility functions used by several classes.
"""

import socket
import urllib
import urllib2
import imp
import subprocess
import StringIO
import time
import logging.handlers
import sclib
import sclib.provider
import tempfile
import smtplib
import datetime
import re
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText
from email.Utils import formatdate
from email import Encoders
import gzip
import base64
try:
    from hashlib import md5
except ImportError:
    from md5 import md5


try:
    import hashlib
    _hashfn = hashlib.sha512
except ImportError:
    import md5
    _hashfn = md5.md5

# List of Query String Arguments of Interest
qsa_of_interest = ['acl', 'cors', 'defaultObjectAcl', 'location', 'logging',
                   'partNumber', 'policy', 'requestPayment', 'torrent',
                   'versioning', 'versionId', 'versions', 'website',
                   'uploads', 'uploadId', 'response-content-type',
                   'response-content-language', 'response-expires',
                   'response-cache-control', 'response-content-disposition',
                   'response-content-encoding', 'delete', 'lifecycle',
                   'tagging']


_first_cap_regex = re.compile('(.)([A-Z][a-z]+)')
_number_cap_regex = re.compile('([a-z])([0-9]+)')
_end_cap_regex = re.compile('([a-z0-9])([A-Z])')


def unquote_v(nv):
    if len(nv) == 1:
        return nv
    else:
        return (nv[0], urllib.unquote(nv[1]))

def retry_url(url, retry_on_404=True, num_retries=10):
    for i in range(0, num_retries):
        try:
            req = urllib2.Request(url)
            resp = urllib2.urlopen(req)
            return resp.read()
        except urllib2.HTTPError, e:
            # in 2.6 you use getcode(), in 2.5 and earlier you use code
            if hasattr(e, 'getcode'):
                code = e.getcode()
            else:
                code = e.code
            if code == 404 and not retry_on_404:
                return ''
        except urllib2.URLError, e:
            raise e
        except Exception, e:
            pass
        sclib.log.exception('Caught exception reading instance data')
        time.sleep(2**i)
    sclib.log.error('Unable to read instance data, giving up')
    return ''

def find_class(module_name, class_name=None):
    if class_name:
        module_name = "%s.%s" % (module_name, class_name)
    modules = module_name.split('.')
    c = None

    try:
        for m in modules[1:]:
            if c:
                c = getattr(c, m)
            else:
                c = getattr(__import__(".".join(modules[0:-1])), m)
        return c
    except:
        return None

class AuthSMTPHandler(logging.handlers.SMTPHandler):
    """
    This class extends the SMTPHandler in the standard Python logging module
    to accept a username and password on the constructor and to then use those
    credentials to authenticate with the SMTP server.  To use this, you could
    add something like this in your boto config file:

    [handler_hand07]
    class=boto.utils.AuthSMTPHandler
    level=WARN
    formatter=form07
    args=('localhost', 'username', 'password', 'from@abc', ['user1@abc', 'user2@xyz'], 'Logger Subject')
    """

    def __init__(self, mailhost, username, password, fromaddr, toaddrs, subject):
        """
        Initialize the handler.

        We have extended the constructor to accept a username/password
        for SMTP authentication.
        """
        logging.handlers.SMTPHandler.__init__(self, mailhost, fromaddr, toaddrs, subject)
        self.username = username
        self.password = password

    def emit(self, record):
        """
        Emit a record.

        Format the record and send it to the specified addressees.
        It would be really nice if I could add authorization to this class
        without having to resort to cut and paste inheritance but, no.
        """
        try:
            port = self.mailport
            if not port:
                port = smtplib.SMTP_PORT
            smtp = smtplib.SMTP(self.mailhost, port)
            smtp.login(self.username, self.password)
            msg = self.format(record)
            msg = "From: %s\r\nTo: %s\r\nSubject: %s\r\nDate: %s\r\n\r\n%s" % (
                            self.fromaddr,
                            ','.join(self.toaddrs),
                            self.getSubject(record),
                            formatdate(), msg)
            smtp.sendmail(self.fromaddr, self.toaddrs, msg)
            smtp.quit()
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            self.handleError(record)

class Password(object):
    """
    Password object that stores itself as hashed.
    Hash defaults to SHA512 if available, MD5 otherwise.
    """
    hashfunc=_hashfn
    def __init__(self, str=None, hashfunc=None):
        """
        Load the string from an initial value, this should be the raw hashed password.
        """
        self.str = str
        if hashfunc:
            self.hashfunc = hashfunc

    def set(self, value):
        self.str = self.hashfunc(value).hexdigest()

    def __str__(self):
        return str(self.str)

    def __eq__(self, other):
        if other == None:
            return False
        return str(self.hashfunc(other).hexdigest()) == str(self.str)

    def __len__(self):
        if self.str:
            return len(self.str)
        else:
            return 0

def get_utf8_value(value):
    if not isinstance(value, str) and not isinstance(value, unicode):
        value = str(value)
    if isinstance(value, unicode):
        return value.encode('utf-8')
    else:
        return value

def mklist(value):
    if not isinstance(value, list):
        if isinstance(value, tuple):
            value = list(value)
        else:
            value = [value]
    return value

def pythonize_name(name):
    """Convert camel case to a "pythonic" name.

    Examples::

        pythonize_name('CamelCase') -> 'camel_case'
        pythonize_name('already_pythonized') -> 'already_pythonized'
        pythonize_name('HTTPRequest') -> 'http_request'
        pythonize_name('HTTPStatus200Ok') -> 'http_status_200_ok'
        pythonize_name('UPPER') -> 'upper'
        pythonize_name('') -> ''

    """
    s1 = _first_cap_regex.sub(r'\1_\2', name)
    s2 = _number_cap_regex.sub(r'\1_\2', s1)
    return _end_cap_regex.sub(r'\1_\2', s2).lower()


def write_mime_multipart(content, compress=False, deftype='text/plain', delimiter=':'):
    """Description:
    :param content: A list of tuples of name-content pairs. This is used
    instead of a dict to ensure that scripts run in order
    :type list of tuples:

    :param compress: Use gzip to compress the scripts, defaults to no compression
    :type bool:

    :param deftype: The type that should be assumed if nothing else can be figured out
    :type str:

    :param delimiter: mime delimiter
    :type str:

    :return: Final mime multipart
    :rtype: str:
    """
    wrapper = MIMEMultipart()
    for name, con in content:
        definite_type = guess_mime_type(con, deftype)
        maintype, subtype = definite_type.split('/', 1)
        if maintype == 'text':
            mime_con = MIMEText(con, _subtype=subtype)
        else:
            mime_con = MIMEBase(maintype, subtype)
            mime_con.set_payload(con)
            # Encode the payload using Base64
            Encoders.encode_base64(mime_con)
        mime_con.add_header('Content-Disposition', 'attachment', filename=name)
        wrapper.attach(mime_con)
    rcontent = wrapper.as_string()

    if compress:
        buf = StringIO.StringIO()
        gz = gzip.GzipFile(mode='wb', fileobj=buf)
        try:
            gz.write(rcontent)
        finally:
            gz.close()
        rcontent = buf.getvalue()

    return rcontent

def guess_mime_type(content, deftype):
    """Description: Guess the mime type of a block of text
    :param content: content we're finding the type of
    :type str:

    :param deftype: Default mime type
    :type str:

    :rtype: <type>:
    :return: <description>
    """
    #Mappings recognized by cloudinit
    starts_with_mappings={
        '#include' : 'text/x-include-url',
        '#!' : 'text/x-shellscript',
        '#cloud-config' : 'text/cloud-config',
        '#upstart-job'  : 'text/upstart-job',
        '#part-handler' : 'text/part-handler',
        '#cloud-boothook' : 'text/cloud-boothook'
    }
    rtype = deftype
    for possible_type, mimetype in starts_with_mappings.items():
        if content.startswith(possible_type):
            rtype = mimetype
            break
    return(rtype)

def compute_md5(fp, buf_size=8192, size=None):
    """
    Compute MD5 hash on passed file and return results in a tuple of values.

    :type fp: file
    :param fp: File pointer to the file to MD5 hash.  The file pointer
               will be reset to its current location before the
               method returns.

    :type buf_size: integer
    :param buf_size: Number of bytes per read request.

    :type size: int
    :param size: (optional) The Maximum number of bytes to read from
                 the file pointer (fp). This is useful when uploading
                 a file in multiple parts where the file is being
                 split inplace into different parts. Less bytes may
                 be available.

    :rtype: tuple
    :return: A tuple containing the hex digest version of the MD5 hash
             as the first element, the base64 encoded version of the
             plain digest as the second element and the data size as
             the third element.
    """
    return compute_hash(fp, buf_size, size, hash_algorithm=md5)


def compute_hash(fp, buf_size=8192, size=None, hash_algorithm=md5):
    hash_obj = hash_algorithm()
    spos = fp.tell()
    if size and size < buf_size:
        s = fp.read(size)
    else:
        s = fp.read(buf_size)
    while s:
        hash_obj.update(s)
        if size:
            size -= len(s)
            if size <= 0:
                break
        if size and size < buf_size:
            s = fp.read(size)
        else:
            s = fp.read(buf_size)
    hex_digest = hash_obj.hexdigest()
    base64_digest = base64.encodestring(hash_obj.digest())
    if base64_digest[-1] == '\n':
        base64_digest = base64_digest[0:-1]
    # data_size based on bytes read.
    data_size = fp.tell() - spos
    fp.seek(spos)
    return (hex_digest, base64_digest, data_size)
