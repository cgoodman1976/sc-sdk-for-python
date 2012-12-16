#!/usr/bin/env python

"Test basic connection"
import unittest
import logging

from tests.unit import config, logging
from sclib.sc.device import Device
from sclib.sc.user import User
from xml.etree import ElementTree
from xml.dom import minidom

from tests.unit.sc.connectionfilter import SCConnectionFilter

class SCConnectionTest(unittest.TestCase):
    def setUp(self):
        from sclib.sc.connection import SCConnection
        self.connection = SCConnectionFilter( config.get('connection', 'MS_HOST'),
                                        config.get('connection', 'MS_BROKER_NAME'), 
                                        config.get('connection', 'MS_BROKER_PASSPHASE'))

        auth = self.connection.basicAuth( config.get('authentication', 'AUTH_NAME'), 
                                          config.get('authentication', 'AUTH_PASSWORD'))
        self.assertNotEqual( auth, None)

    def testListAllDevice(self):
        devicelist = self.connection.listAllDevices()
        for dev in devicelist:
            xml_pretty = dev.niceFormat()
            logging.debug(xml_pretty)
            
    def testListAllUsers(self):
        userlist = self.connection.listAllUsers()
        for user in userlist:
            xml_pretty = user.niceFormat()
            logging.debug(xml_pretty)
            
    def testListAllSecurityGroup(self):
        policylist = self.connection.listAllSecurityGroup()
        for policy in policylist:
            xml_pretty = policy.niceFormat()
            logging.debug(xml_pretty)

if __name__ == '__main__':
    unittest.main()