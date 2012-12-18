"Test basic connection"
import unittest
import logging

from tests.unit import config, logging
from sclib.sc.device import Device
from sclib.sc.user import User

from sclib.sc.connection import SCConnection
from tests.unit.sc.connectionfilter import SCConnectionFilter

class SCUserTest(unittest.TestCase):
    def setUp(self):
        self.connection = SCConnectionFilter( config.get('connection', 'MS_HOST'),
                                        config.get('connection', 'MS_BROKER_NAME'), 
                                        config.get('connection', 'MS_BROKER_PASSPHASE'))

        self.connection.basicAuth(  config.get('authentication', 'AUTH_NAME'), 
                                    config.get('authentication', 'AUTH_PASSWORD'))

        self.users = self.connection.listAllUsers()

    def testUserCreate(self):
        user = self.connection.createUser( 'unittest2@securecloud.com',
                                            '',
                                            'localuser',
                                            'unit2',
                                            'test2',
                                            'unittest2@securecloud.com',
                                            'Administrator',
                                            'false')
        self.assertNotEqual(user, None)
        if not user:
            # new user needs activation
            res = user.update()
            self.assertNotEqual(res, None)

            res = user.delete()
            self.assertEqual(res, True)
  
    def testUserGet(self):        
        user = self.connection.getUser(self.users[0].id)
        self.assertNotEqual(user, None)
        self.assertEqual(user.id, self.users[0].id)
               
if __name__ == '__main__':
    unittest.main()