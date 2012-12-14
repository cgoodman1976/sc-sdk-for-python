"Test basic connection"
import unittest
import logging

from tests.unit import config, logging
from sclib.sc.user import User
from xml.etree import ElementTree
from xml.dom import minidom

class SCUserTest(unittest.TestCase):
    def setUp(self):
        from sclib.sc.connection import SCConnection
        self.connection = SCConnection( config.get('connection', 'MS_HOST'),
                                        config.get('connection', 'MS_BROKER_NAME'), 
                                        config.get('connection', 'MS_BROKER_PASSPHASE'))

        auth = self.connection.basicAuth( config.get('authentication', 'AUTH_NAME'), 
                                          config.get('authentication', 'AUTH_PASSWORD'))

        self.users = self.connection.listAllUsers()
        self.user = User(self.connection)

    def testUserCreate(self):
        self.user.id = 'xxxxxxxxx'
        response = self.user.create()
        
    def testUserGet(self):
        user = User(self.connection)
        user.id = self.user.id
        response = self.user.get()
        
    def testUserUpdate(self):
        user = User(self.connection)
        user.id = self.user.id
        #TODO - update more field here
        response = user.update()

    def testUserDelete(self):
        user = User(self.user)
        user.id = self.user.id
        #TODO - update more field here
        response = user.update()

if __name__ == '__main__':
    unittest.main()