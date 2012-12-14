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

from sclib.sc.scobject import SCObject
from xml.etree import ElementTree

class User(SCObject):
    def __init__(self, connection):
        SCObject.__init__(self, connection)
        #contact information
        self.firstName = None
        self.lastName = None
        self.email = None
        #account information
        self.id = None
        self.accountName = None
        self.role = None
        #user information
        self.loginname = None
        
    def startElement(self, name, attrs, connection):
        ret = SCObject.startElement(self, name, attrs, connection)
        if ret is not None:
            return ret
        
        if name == 'account':
            self.id = attrs['id']
            self.accountName = attrs['name']
            return self
        elif name == 'role':
            self.role = Role(connection)
            return self.role
        else:
            return None

    def endElement(self, name, value, connection):
        if name == 'firstName':
            self.firstName = value
        elif name == 'lastName':
            self.lastName = value
        elif name == 'email':
            self.email = value
        else:
            setattr(self, name, value)
            
    def buildElements(self):
        user = ElementTree.Element('user')
        if self.loginname: user.attrib['loginname'] = self.loginname
        if self.logintext: user.attrib['logintext'] = self.logintext
        if self.usertype: user.attrib['usertype'] = self.usertype
        return user

        
class Role(SCObject):
    def __init__(self,connection):
        SCObject.__init__(self, connection)
        self.MFAStatus = None
        self.name = None
        
    def startElement(self, name, attrs, connection):
        ret = SCObject.startElement(self, name, attrs, connection)
        if ret is not None:
            return ret
        
        if name == 'role':
            self.MFAStatus = attrs['MFAStatus']
            self.name = attrs['name']
        else:
            return None

    def endElement(self, name, value, connection):
        setattr(self, name, value)
            
    def buildElements(self):
        role = ElementTree.Element('role')
        if self.MFAStatus: role.attrib['MFAStatus'] = self.MFAStatus
        if self.name: role.attrib['name'] = self.name
        return role
        
        