'''
Created on 2012/12/5

@author: bobby_chien
'''

from sclib.sc.scobject import SCObject

class Device(SCObject):
    def __init__(self):
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
        
    def parse(self, device):
        self.uid = device.attributes["msUID"].value.strip()
        self.id = device.attributes["id"].value.strip()
        self.name = device.attributes["name"].value.strip()
        self.href = device.attributes["href"].value.strip()
        self.deviceType = device.attributes["cspDeviceType"].value.strip()
        self.info = device.attributes["info"].value.strip()
        self.lastModified = device.attributes["lastModified"].value.strip()
        self.writeAccess = device.attributes["writeaccess"].value.strip()
        self.provisionState = device.attributes["provisionState"].value.strip()
        self.deviceState = device.attributes["deviceStatus"].value.strip()
        self.detachable = device.attributes["detachable"].value.strip()
        self.description = device.getElementsByTagName("description")
        volume = device.getElementsByTagName("volume")
        self.volumeSize = None #volume.attributes["size"].value.strip()
        self.mountPoint = None #volume.getElementsByTagName("mountPoint").device.attributes["uid"].value.strip()
        self.provider = None


