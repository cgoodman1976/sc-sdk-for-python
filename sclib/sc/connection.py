# Copyright (c) 2012 Trend Micro, Inc. All rights reserved.
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

"Handle SecureCloud basic connection to SC Management API"

from sclib.connection import SCQueryConnection

import sclib

LOG_LEVEL = "DEBUG"
REALM = "securecloud@trend.com"

# you need to configure the following
BASE_URL = "https://mapi_server.securecloud.com:8443/broker/api.svc"
BROKER_NAME = "mapi_test"
BROKER_PASS = "EWv6yqULCl"
USER_NAME = "shaodanny@gmail.com"
USER_PASS = "P@ssw0rd@123"

sclib.log.setLevel(level=LOG_LEVEL)

class SCConnection(SCQueryConnection):

    def __init__(self, username=None, password=None, is_secure=True,
                 port=None, proxy=None, proxy_port=None, proxy_user=None, proxy_pass=None,
                 host=None, debug=0):
        
        self.base_url = BASE_URL
        self.user_name = USER_NAME
        self.user_pass = USER_PASS
        self.broker = BROKER_NAME
        self.broker_passphrase = BROKER_PASS
        self.realm = REALM
        self.session_token = self.basic_auth()

        #Call super constructor
        SCQueryConnection.__init__(self, username, password, is_secure, 
                                   port, proxy, proxy_port, proxy_user, proxy_pass, 
                                   host, debug, https_connection_factory, path, 
                                   security_token, validate_certs)

    # ----- help function start -----

    def getText(self, node):
        rc = ""

        if node.nodeType == node.ELEMENT_NODE:
            if node.hasChildNodes():
                nodelist = node.childNodes
                for node in nodelist:
                    if node.nodeType == node.TEXT_NODE:
                        rc = rc + node.data
        elif node.hasChildNodes():
            nodelist = node.childNodes
            for node in nodelist:
                if node.nodeType == node.TEXT_NODE:
                    rc = rc + node.data

        return rc

    def nice_format(self, input):
        xmlstr = parseString(input)
        pretty_res = xmlstr.toprettyxml()

        return pretty_res

    def check_existing_node(self, nodes, id):

        for node in nodes:
            current_id = node.getAttribute("id")
            if(current_id == id):
                return True

        return False

    def get_node(self, nodes, id):

        for node in nodes:
            current_id = node.getAttribute("id")
            if(current_id == id):
                return node

    # ----- help function ends

    def basic_auth(self):

        # get server's public key
        pubkey = self.get_certificate()
        if not pubkey:
            return False

        # encrypt user password
        key = rsa.Key(pubkey)
        pub = key.public
        #print pub.as_string()

        password = bytes(self.user_pass)
        encrypted_password = pub.encrypt(password, None, "sha256", "oaep")
        encrypted_password = base64.b64encode(encrypted_password)

        req_xml = """<?xml version="1.0" encoding="utf-8"?>
                    <authentication xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" 
                    xmlns:xsd="http://www.w3.org/2001/XMLSchema" id="" data="%s" accountId="" />""" % (encrypted_password)
        sclib.log.debug(req_xml)

        auth_url = self.base_url+ '/userBasicAuth/' + self.user_name + "?tenant="
        sclib.log.debug(auth_url)
        pwd_mgr = urllib2.HTTPPasswordMgr()
        pwd_mgr.add_password(self.realm, auth_url, self.broker, self.broker_passphrase)
        opener = urllib2.build_opener()
        opener.add_handler(urllib2.HTTPDigestAuthHandler(pwd_mgr))

        req = urllib2.Request(auth_url)
        req.add_header('Content-Type', 'application/xml; charset=utf-8')
        req.add_header('BrokerName', self.broker)
        req.add_data(req_xml)

        try:
            sc_get_req = opener.open(req)
        except urllib2.HTTPError, e:
            sclib.log.error(e)
            return False
        except urllib2.URLError, e:
            sclib.log.error(e)
            return False

        res = sc_get_req.read()
        #sclib.log.debug(res)

        xmldata = xml.dom.minidom.parseString(res)
        auth_result = xmldata.getElementsByTagName("authenticationResult")[0]
        session_token = auth_result.attributes["token"].value.strip()
        sclib.log.debug("session token : %s" % session_token)


        return session_token


    def get_certificate(self):
        
        # get server side certificate
        sclib.log.debug("==== start get_certificate =====")
        
        auth_url = self.base_url + "/PublicCertificate/"

        pwd_mgr = urllib2.HTTPPasswordMgr()
        pwd_mgr.add_password(self.realm, auth_url, self.broker, self.broker_passphrase)

        opener = urllib2.build_opener()
        opener.add_handler(urllib2.HTTPDigestAuthHandler(pwd_mgr))

        req = urllib2.Request(auth_url)
        req.add_header('Content-Type', 'application/xml; charset=utf-8')
        req.add_header('BrokerName', self.broker)

        try:
            sc_get_req = opener.open(req)
        except urllib2.HTTPError, e:
            sclib.log.error(e)
            return False
        except urllib2.URLError, e:
            sclib.log.error(e)
            return False

        res = sc_get_req.read()
        sclib.log.debug(res)

        try:
            xmldata = xml.dom.minidom.parseString(res)
            certificate_response = xmldata.getElementsByTagName("certificateResponse")[0]
            certificate_list = certificate_response.getElementsByTagName("certificateList")[0]
            certificate_node = certificate_response.getElementsByTagName("certificate")[0]
            certificate = self.getText(certificate_node)
            certificate = """-----BEGIN RSA PUBLIC KEY-----\n%s\n-----END RSA PUBLIC KEY-----\n""" % (certificate)
            certificate = str(certificate)
            #print certificate
        except Exception, e:
            sclib.log.error(e)
            return False

        sclib.log.debug("end get_certificate")        
        return certificate


    def sc_request(self, resource='', method='get', data=''):

        sclib.log.debug("Start sc_request")

        #if not self.session_token:
        #    self.session_token = self.basic_auth()

        pwd_mgr = urllib2.HTTPPasswordMgr()
        api_url = self.base_url+'/'+resource+'/'
        pwd_mgr.add_password(self.realm, api_url, self.broker, self.broker_passphrase)
        opener = urllib2.build_opener()
        opener.add_handler(urllib2.HTTPDigestAuthHandler(pwd_mgr))

        req = urllib2.Request(api_url)

        sclib.log.debug("url:%s" % (api_url))

        if method == 'post' and data != '':
            sclib.log.debug(data)
            req.add_data(data)
        elif method == 'delete':
            req.get_method = lambda: 'DELETE'
        else:
            pass

        req.add_header('Content-Type', 'application/xml; charset=utf-8')
        req.add_header('BrokerName', self.broker)
        req.add_header('X-UserSession', self.session_token)

        try:
            sc_get_req = opener.open(req)
        except urllib2.HTTPError, e:
            sclib.log.error(e)
            return False

        rawstr = sc_get_req.read()

        sclib.log.debug("End sc_request")

        if(method == "delete"):
            if(rawstr == ""):
                return True
            else:
                return False
        else:
            return rawstr


    # ---------------------------------------------------------------------
    
        # image and device
    def listAllDevices(self):
        result = self.sc_request(resource='device')
        if not result:
            return False
        sclib.log.debug(result)
        xmldata = xml.dom.minidom.parseString(result)

        return xmldata

    def getDevice(self, device_id=None):
        
        """
        params = {}
        if device_id:
            params["DeviceId"] = device_id
        rs = self.get_object("device", params, ResultSet)
        """
        
        result = self.sc_request(resource='device/'+device_id)
        if not result:
            return False
        sclib.log.debug(result)
        xmldata = xml.dom.minidom.parseString(result)

        return xmldata

    def listAllImages(self):
        result = self.sc_request(resource='image')
        if not result:
            return False
        sclib.log.debug(result)
        xmldata = xml.dom.minidom.parseString(result)

        return xmldata

    def getImage(self, image_id):
        result = self.sc_request(resource='image/'+image_id)
        if not result:
            return False
        sclib.log.debug(result)
        xmldata = xml.dom.minidom.parseString(result)

        return xmldata

    # policy
    def listAllSecurityGroups(self):
        result = self.sc_request(resource='securityGroup')
        if not result:
            return False
        sclib.log.debug(result)
        xmldata = xml.dom.minidom.parseString(result)

        return xmldata

    def getSecurityGroup(self, sg_id):
        result = self.sc_request(resource='securityGroup/'+sg_id)
        if not result:
            return False
        sclib.log.debug(result)
        xmldata = xml.dom.minidom.parseString(result)

        return xmldata

    def updateSecurityGroup(self, sg_id, sg_data):
        result = self.sc_request(resource='securityGroup/'+sg_id, method="post", data=sg_data)
        if not result:
            return False
        sclib.log.debug(result)
        xmldata = xml.dom.minidom.parseString(result)

        return xmldata
