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

class Device(SCObject):
    def __init__(self, connection):
        SCObject.__init__(self, connection)
        self.uid = None
        self.id = None
        self.name = None
        self.href = None
        self.deviceType = None
        self.info = None
        self.lastModified = None
        self.writeAccess = None
        self.provisionState = None
        self.deviceState = None
        self.detachable = None
        self.description = None
        self.volumeSize = None
        self.mountPoint = None
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
            self.size = attrs['size']
        else:
            return None

    def endElement(self, name, value, connection):
        
        if name == 'description':
            self.description = value
        elif name == 'mountPoint':
            self.mountPoint = value
        else:
            setattr(self, name, value)

        #self.description = None#device.getElementsByTagName("description")
        #volume = None# device.getElementsByTagName("volume")
        #self.volumeSize = None #volume.attributes["size"].value.strip()
        #self.mountPoint = None #volume.getElementsByTagName("mountPoint").device.attributes["uid"].value.strip()
        #self.provider = None

