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
from sclib.sc.provider import Provider
from xml.etree import ElementTree


class Device(SCObject):

    ValidAttributes = ['id', 'msUID', "name", 'href',
                       'deviceType', 'cspDeviceType', 'deviceState', 'deviceStatus',
                       'info', 'detachable', 'lastModified', 'writeAccess',
                       'EncryptedName', 'partitionType', 'provisionProgress', 'provisionState',
                       'raidLevel']

    def __init__(self, connection, tag='Device'):
        SCObject.__init__(self, connection, tag)
        # Device attributes
        self.id = None
        self.msUID = None
        self.name = None
        self.href = None

        self.deviceType = None
        self.cspDeviceType = None
        self.deviceState = None
        self.deviceStatus = None

        self.info = None
        self.detachable = None
        self.lastModified = None
        self.writeAccess = None

        self.EncryptedName = None
        self.partitionType = None
        self.provisionProgress = None
        self.provisionState = None
        self.raidLevel = None

        # elements
        self.description = None
        self.fileSystem = None

        # subDevices List
        self.__subDevices = ResultSet([('subDevices', Device)], 'subDevices')
        # volume object
        self.volume = None
        # provider object
        self.provider = None
        # partition list
        self.partitionList = None

    # ---------------
    # properties
    # ---------------
    @property
    def subDevices(self):
        return self.__subDevices

    def startElement(self, name, attrs, connection):
        ret = SCObject.startElement(self, name, attrs, connection)
        if ret is not None:
            return ret

        if name == 'device':
            for key, value in attrs.items():
                setattr(self, key, value)

        elif name == 'volume':
            self.volume = Volume(connection)
            self.volume.startElement(name, attrs, connection)
            return self.volume
        elif name == 'provider':
            self.provider = Provider(connection)
            self.provider.startElement(name, attrs, connection)
            return self.provider
        elif name == 'partitionList':
            partitionList = ResultSet([('partition', Partition)], name)
            return self.partitionList
        elif name == 'subDevices':
            self.__subDevices = ResultSet([('subDevices', Device)], name)
            return self.subDevices
        else:
            return None

    def endElement(self, name, value, connection):

        if name == 'description':
            self.description = value
        elif name == 'fileSystem':
            self.fileSystem = value
        else:
            setattr(self, name, value)

    def buildElements(self, elements=None):
        device = ElementTree.Element('device')

        # build attributes
        for e in self.ValidAttributes:
            if getattr(self, e):
                device.attrib[e] = getattr(self, e)

        if self.description:
            ElementTree.SubElement(
                device, 'description').text = self.description
        if self.fileSystem:
            ElementTree.SubElement(device, 'fileSystem').text = self.fileSystem

        # inner objects
        if self.partitionList:
            device.append(self.partitionList.buildElements())
        if self.volume:
            device.append(self.volume.buildElements())
        if self.provider:
            device.append(self.provider.buildElements())
        if self.__subDevices:
            device.append(self.__subDevices.buildElements())

        return device

    # ---------- function ----------

    def cancelEncryption(self):
        # Build XML elements structures
        action = 'vm/%s/device/%s/encrypt' % (self.imageGUID, self.msUID)
        data = self.tostring()
        response = self.connection.make_request(
            action, data=data, method='DELETE')
        return response

    def exportKey(self):
        action = 'vm/%s/device/%s/keyfile/' % (self.imageGUID, self.msUID)
        data = self.tostring()
        response = self.connection.make_request(
            action, data=data, method='POST')
        return response

    def importKey(self):
        action = 'vm/%s/device/%s/key/' % (self.imageGUID, self.msUID)
        data = self.tostring()
        response = self.connection.make_request(
            action, data=data, method='POST')
        return response

    def deleteKey(self):
        action = 'vm/%s/device/%s/key/' % (self.imageGUID, self.msUID)
        data = self.tostring()
        response = self.connection.make_request(
            action, data=data, method='DELETE')
        return response


class Volume (SCObject):

    def __init__(self, connection, tag='Volume'):
        SCObject.__init__(self, connection, tag)
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
        if self.size:
            volume.attrib['size'] = self.size
        if self.mountPoint:
            mount_point = ElementTree.SubElement(volume, 'mountPoint')
            mount_point.text = self.mountPoint
        return volume


class Partition(SCObject):

    ValidAttributes = ['size', 'fileSystem', "mountPoint"]

    def __init__(self, connection, tag='partition'):
        SCObject.__init__(self, connection, tag)
        self.PartitionNumber = None
        self.size = None
        self.fileSystem = None
        self.mountPoint = None

    def startElement(self, name, attrs, connection):
        ret = SCObject.startElement(self, name, attrs, connection)
        if ret is not None:
            return ret

        if name == 'partition':
            self.PartitionNumber = attrs['PartitionNumber']
            self.size = attrs['size']
        else:
            return None

    def endElement(self, name, value, connection):

        if name == 'mountPoint':
            self.mountPoint = value
        if name == 'fileSystem':
            self.fileSystem = value
        else:
            setattr(self, name, value)

    def buildElements(self):
        partition = ElementTree.Element('partition')
        if self.PartitionNumber:
            partition.attrib['PartitionNumber'] = self.PartitionNumber
        if self.size:
            partition.attrib['size'] = self.size
        if self.fileSystem:
            partition.attrib['fileSystem'] = self.fileSystem
        if self.mountPoint:
            partition.attrib['mountPoint'] = self.mountPoint
        return partition
