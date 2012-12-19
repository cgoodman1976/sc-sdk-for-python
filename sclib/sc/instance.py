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

from sclib.resultset import ResultSet
from sclib.sc.scobject import SCObject
from sclib.sc.device import Device
from sclib.sc.provider import Provider


class Instance(SCObject):
    def __init__(self, connection=None):
        pass
    
class VirtualMachine(SCObject):
    def __init__(self, connection):
        # member information
        self.SecurityGroupGUID = None
        self.autoProvision = None
        self.detectedKeyCount = None
        self.encryptedDeviceCount = None
        self.encryptingDeviceCount = None
        self.href = None
        self.imageGUID = None
        self.imageID = None
        self.imageName = None
        self.instanceGUID = None
        self.instanceID = None
        self.lastModified = None
        self.nonEncryptedDeviceCount = None
        self.pendingDeviceCount = None
        self.imageDescription = None
        # provider
        self.provider = None
        # platform
        self.platform = None
        # agent
        self.agent = None
        # device
        self.devices = None
        
        pass

    def startElement(self, name, attrs, connection):
        ret = SCObject.startElement(self, name, attrs, connection)
        if ret is not None:
            return ret
        
        if name == 'vm':
            for key, value in attrs.items():
                setattr(self, key, value)
        elif name == 'provider':
            self.provider = Provider(connection)
            self.provider.startElement(name, attrs, connection)
            return self.provider
        elif name == 'securecloudAgent':
            self.agent = SCAgent(connection)
            self.agent.startElement(name, attrs, connection)
        elif name == 'devices':
            self.devices = ResultSet([('device', Device)])
            self.devices.name = name
            return self.devices
        else:
            return None

    def endElement(self, name, value, connection):
        if name == 'platform':
            self.platform = value
        elif name == 'imageDescription':
            self.imageDescription = value
        else:
            setattr(self, name, value)
            
    def buildElements(self):
        return None

class SCAgent(SCObject):
    def __init__(self, connection):
        # member information
        self.agentStatus = None
        self.agentVersion = None

    def startElement(self, name, attrs, connection):
        ret = SCObject.startElement(self, name, attrs, connection)
        if ret is not None:
            return ret
        
        if name == 'securecloudAgent':
            self.agentStatus = attrs['agentStatus']
            self.agentVersion = attrs['agentVersion']
        else:
            return None

    def endElement(self, name, value, connection):
        setattr(self, name, value)
            
    def buildElements(self):
        agent = ElementTree.Element('agent')
        if self.agentStatus: agent.attrib['agentStatus'] = self.agentStatus
        if self.agentVersion: agent.attrib['agentVersion'] = self.agentVersion
        return agent

    
    