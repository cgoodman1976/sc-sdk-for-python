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
import xml.sax
import base64

from sclib.exception import SCClientError, SCResponseError
from sclib.connection import SCQueryConnection
from sclib.sc.device import Device
from sclib.sc.user import User
from sclib.sc.scobject import SCObject
from sclib.sc.instance import VirtualMachine, Instance
from sclib.sc.provider import Provider
from sclib.sc.keyrequest import KeyRequest
from sclib.sc.securitygroup import SecurityGroup, SecurityRule, SecurityRuleType

from xml.dom.minidom import parse, parseString
from xml.etree import ElementTree

from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from Crypto import Hash

class Certificate(SCObject):
    def __init__(self, connection):
        SCObject.__init__(self, connection)
        self.level = None
        self.encoding = None
        self.certificate = None
        self.publickey = None
        
    def startElement(self, name, attrs, connection):
        ret = SCObject.startElement(self, name, attrs, connection)
        if ret is not None:
            return ret
        
        if name == 'certificate':
            self.id = attrs['level']
            self.encoding = attrs['encoding']
        else:
            return None

    def endElement(self, name, value, connection):
        if name == 'certificate':
            self.certificate = value
            self.publickey = """-----BEGIN RSA PUBLIC KEY-----\n%s\n-----END RSA PUBLIC KEY-----\n""" % (self.certificate)
        else:
            setattr(self, name, value)
            
    def encryptData(self, data):
        if self.certificate:
            publickey = RSA.importKey(self.publickey).publickey()
            cipher = PKCS1_OAEP.new(publickey, Hash.SHA256)
            encrypted = cipher.encrypt( bytes(data) )
            return base64.b64encode(encrypted)
        return None

class Authentication(SCObject):
    
    ValidAttributes = ['id', 'token', 'expires', 'data', 'accountId']
    def __init__(self, connection):
        SCObject.__init__(self, connection)
        self.id = None
        self.token = None
        self.expires = None
        self.data = None
        self.accountId = None

    def startElement(self, name, attrs, connection):
        ret = SCObject.startElement(self, name, attrs, connection)
        if ret is not None:
            return ret
        
        if name == 'authenticationResult':
            self.id = attrs['id']
            self.token = attrs['token']
            self.expires = attrs['expires']
        else:
            return None

    def endElement(self, name, value, connection):
        setattr(self, name, value)
        
    def buildElements(self, elements=None):
        authentication = ElementTree.Element('authentication')
        
        # build attributes
        for attr in self.ValidAttributes:
            if getattr(self, attr): authentication.attrib[attr] = getattr(self, attr)

        return authentication

        
    def isAuthenticated(self):
        return self.token is not None


class SCConnection(SCQueryConnection):

    REST_PUBLIC_CERTIFICATE = 'PublicCertificate'
    REST_BASIC_AUTH = 'userBasicAuth'
    REST_DEVICE = 'device'
    REST_SECURITY_GROUP = 'SecurityGroup'
    REST_SECURITY_RULE = 'SecurityRule'
    REST_SECURITY_RULE_TYPE = 'SecurityRule'
    REST_USER = 'user'
    REST_VM = 'vm'
    REST_PROVIDER = 'provider'
    REST_KEY_REQUEST = 'keyrequesttree'
    REST_DEVICE_KEY_REQUEST = 'devicekeyrequest'

    def __init__(self, host_base, broker_name=None, broker_passphase=None):
        SCQueryConnection.__init__( self, host_base, broker_name, broker_passphase)
        
        #members
        self.authentication = None
        self.certificate = None
        
    def getCertificate(self):
        params = {}
        certificate = self.get_object( '%s' % (self.REST_PUBLIC_CERTIFICATE),
                                        params, Certificate)
        if certificate is None:
            raise SCResponseError( '4xx' , "Unknown error")

        self.certificate = certificate

        return self.certificate
    
    def basicAuth(self, name, password):
        
        if self.certificate is None:
            self.getCertificate()
        
        params = {}
        # build authentication request
        auth_req = Authentication(self)
        auth_req.data = self.certificate.encryptData(password)
        req_data = ElementTree.tostring(auth_req.buildElements())

        auth = self.get_object( '%s/%s' % (self.REST_BASIC_AUTH, name), 
                                params, Authentication, data=req_data, method='POST')
        if auth:
            self.authentication = auth
            self.headers['X-UserSession'] = self.authentication.token
        return self.authentication
  
    def isAuthenticated(self):
        if self.authentication is None:
            raise SCClientError('Connection abort. Needs Authentication first!')
        
        return True
  
    #===========================================================================
    # # functions - Device
    #===========================================================================
    
    def listAllDevices(self):
        if self.authentication is None: 
            return None
    
        params = {}
        return self.get_list( '%s' % (self.REST_DEVICE), params, 
                              [('device', Device)])

    def getDevice(self, guid):
        if self.authentication is None: 
            return None
    
        params = {}
        return self.get_object( '%s/%s/' % (self.REST_DEVICE, guid), 
                                params, Device)

    #===========================================================================
    # # function - Policy/SecurityGroup
    #===========================================================================
    def listAllSecurityGroup(self):
        if self.authentication is None: 
            return None
    
        params = {}
        return self.get_list( '%s' % (self.REST_SECURITY_GROUP), 
                              params, [('securityGroup', SecurityGroup)])

    def getSecurityGroup(self, id):
        if self.authentication is None: 
            return None
    
        params = {}
        rule = self.get_object( '%s/%s/' % (self.REST_SECURITY_GROUP, id), 
                                params, SecurityGroup)
        return rule

    def listAllSecurityRuleTypes(self):
        if self.authentication is None: 
            return None

        params = {}
        return self.get_list( '%s' % (self.REST_SECURITY_RULE_TYPE), 
                              params, [('securityRuleType', SecurityRuleType)])

    def getSecurityRuleType(self, id):
        if self.authentication is None: 
            return None
    
        params = {}
        rule = self.get_object( '%s/%s/' % (self.REST_SECURITY_RULE_TYPE, id), 
                                params, SecurityRuleType)
        return rule

    #===========================================================================
    # # function - User
    #===========================================================================
    def listAllUsers(self):
        if self.isAuthenticated() is False : 
            return None

        params = {}
        return self.get_list( '%s/' % (self.REST_USER), 
                              params, [('user', User)])
        
    def createUser(self, login, text, usertype='localuser', 
                   firstname='', lastname='', email='', 
                   role='Administrator', MFA='false'):

        if self.isAuthenticated() is False : 
            return None

        params = {}
        user = User(self)
        user.loginname = login
        user.logintext = self.certificate.encryptData(text)
        user.usertype = usertype
        user.firstName = firstname
        user.lastName = lastname
        user.email = email
        user.name = role
        user.MFAStatus = MFA
        user.setRole(role, MFA)
        data = ElementTree.tostring(user.buildElements())
        return self.get_object( '%s' % (self.REST_USER), 
                                params, User, data=data, method='POST')
    
    def getUser(self, id):
        if self.isAuthenticated() is False : 
            return None

        params = {}
        return self.get_object( '%s/%s/' % (self.REST_USER, id), 
                                params, User)
    
    #===========================================================================
    # virtual machine function
    #===========================================================================
    def listAllVM(self):
        if self.isAuthenticated() is False : 
            return None

        params = {}
        return self.get_list( '%s' % (self.REST_VM), 
                              params, [('vm', VirtualMachine)])

    def getVM(self, id):
        if self.isAuthenticated() is False : 
            return None

        params = {}
        return self.get_object( '%s/%s/' % (self.REST_VM, id), 
                                params, VirtualMachine)
    
    #===========================================================================
    # Provider function
    #===========================================================================
    def listAllProvider(self):
        if self.isAuthenticated() is False : 
            return None

        params = {}
        return self.get_list( '%s' % (self.REST_PROVIDER), 
                              params, [('provider', Provider)])

    def getProvider(self, name):
        if self.isAuthenticated() is False : 
            return None

        params = {}
        return self.get_object( '%s/%s/' % (self.REST_PROVIDER, name), 
                                params, Provider)
    
    #---------------------------------------------------------------------------
    # key request
    #---------------------------------------------------------------------------
    def listAllKeyRequest(self):
        if self.isAuthenticated() is False : 
            return None
        
        params = {}
        return self.get_list( '%s' % (self.REST_KEY_REQUEST), 
                              params, [('devicekeyrequest', KeyRequest)])

    def listKeyRequest(self, id):
        if self.isAuthenticated() is False : 
            return None
        
        params = {}
        return self.get_object( '%s/%s/' % (self.REST_KEY_REQUEST, id ), 
                                params, KeyRequest)
