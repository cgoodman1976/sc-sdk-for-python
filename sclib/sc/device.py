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

class Device(SCObject):
    def __init__(self, connection):
        SCObject.__init__(self, connection)
        self.uid = None
        self.id = None
        self.name = None
        self.href = None
        self.deviceType = None
        self.cspDeviceType = None
        self.info = None
        self.lastModified = None
        self.writeAccess = None
        self.provisionState = None
        self.deviceState = None
        self.detachable = None
        self.description = None
        # volume object
        self.volume = None
        # provider object
        self.provider = None
        
    def startElement(self, name, attrs, connection):
        ret = SCObject.startElement(self, name, attrs, connection)
        if ret is not None:
            return ret
        
        if name == 'device':
            self.uid = attrs['msUID']
            self.id = attrs["id"]
            self.name = attrs["name"]
            self.href = attrs["href"]
            self.deviceType = attrs["cspDeviceType"]
            self.info = attrs["info"]
            self.lastModified = attrs["lastModified"]
            self.writeAccess = attrs["writeaccess"]
            self.provisionState = attrs["provisionState"]
            self.deviceState = attrs["deviceStatus"]
            self.detachable = attrs["detachable"]
            return self
        
        elif name == 'volume':
            self.volume = Volume(connection)
            self.volume.startElement(name, attrs, connection)
            return self.volume
        else:
            return None

    def endElement(self, name, value, connection):
        
        if name == 'description':
            self.description = value
        else:
            setattr(self, name, value)

    def buildElements(self):
        
        device = ElementTree.Element('device')
        device.attrib['version'] = '3.5'
        if self.uid:    device.attrib['msUID'] = self.uid
        if self.id:     device.attrib['id'] = self.id
        if self.name:   device.attrib['name'] = self.name
        if self.href:   device.attrib['href'] = self.href
        if self.cspDeviceType:   device.attrib['cspDeviceType'] = self.cspDeviceType
        if self.info:   device.attrib['info'] = self.info
        if self.lastModified:   device.attrib['lastModified'] = self.lastModified
        if self.writeAccess: device.attrib['writeaccess'] = self.writeAccess
        if self.provisionState:   device.attrib['provisionState'] = self.provisionState
        if self.description:
            description = ElementTree.SubElement(device, "description")
            description.text = self.description
        # inner objects
        if self.volume: device.append(self.volume.buildElements())
        if self.provider: device.append(self.provider.buildElements())
            
        return device

    # ---------- function ----------
    
    def update(self):
        # Build XML elements structures
        action = 'device/' + self.uid + '/'
        req_element = self.buildElements()
        data = ElementTree.tostring(req_element)
        response = self.connection.make_request(action, data, method='POST')
        return response
        

class Volume (SCObject):
    def __init__(self, connection):
        self.size = None
        self.mountPoint = None

    def startElement(self, name, attrs, connection):
        ret = SCObject.startElement(self, name, attrs, connection)
        if ret is not None:
            return ret
        
        if name == 'volume':
            self.size = attrs['size']
        else:
            return None

    def endElement(self, name, value, connection):
        
        if name == 'mountPoint':
            self.mountPoint = value
        else:
            setattr(self, name, value)
            
    def buildElements(self):
        volume = ElementTree.Element('volume')
        if self.size: volume.attrib['size'] = self.size
        if self.mountPoint:
            mount_point = ElementTree.SubElement(volume, 'mountPoint')
            mount_point.text = self.mountPoint
        return volume

