#!/usr/bin/env python

"Test basic connection"
import unittest
import logging

from tests.unit import config, logging
from sclib.sc.device import Device
from sclib.sc.user import User
from xml.etree import ElementTree
from xml.dom import minidom

class SCConnectionTest(unittest.TestCase):
    def setUp(self):
        from sclib.sc.connection import SCConnection
        self.connection = SCConnection( config.get('connection', 'MS_HOST'),
                                            config.get('connection', 'MS_BROKER_NAME'), 
                                            config.get('connection', 'MS_BROKER_PASSPHASE'), 
                                            config.get('authentication', 'AUTH_NAME'), 
                                            config.get('authentication', 'AUTH_PASSWORD') )

    def testListAllDevice(self):
        devicelist = self.connection.listAllDevices()
        for dev in devicelist:
            xml = ElementTree.tostring(dev.buildElements())
            xml_pretty = minidom.parseString(xml).toprettyxml()
            logging.debug(xml_pretty)
            
    def testUpdateDevice(self):
        userlist = self.connection.listUsers()
        for user in userlist:
            xml = user.buildXML()
            xml_pretty = minidom.parseString(xml).toprettyxml()
            logging.debug(xml_pretty)

if __name__ == '__main__':
    unittest.main()