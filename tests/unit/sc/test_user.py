"Test basic connection"
import unittest
import logging

from tests.unit import config, logging
from sclib.sc.user import User

class SCUserTest(unittest.TestCase):
    def setUp(self):
        from sclib.sc.connection import SCConnection
        self.connection = SCConnection( config.get('connection', 'MS_HOST'),
                                        config.get('connection', 'MS_BROKER_NAME'), 
                                        config.get('connection', 'MS_BROKER_PASSPHASE'))

        self.connection.basicAuth(  config.get('authentication', 'AUTH_NAME'), 
                                    config.get('authentication', 'AUTH_PASSWORD'))

        self.users = self.connection.listAllUsers()
        self.user = None

    def testUserCreate(self):
        user = self.connection.createUser( 'unittest@securecloud.com',
                                            'unittest_text',
                                            'localuser',
                                            'unit',
                                            'test',
                                            'unittest@securecloud.com',
                                            'Administrator',
                                            'false')
        self.assertNotEqual(user, None)
        if user is not None: 
            self.user = user
        
    def testUserGet(self):
        self.assertNotEqual(self.user, None)
        
        user = self.connection.getUser(self.users[0].id)
        self.assertNotEqual(user, None)
        self.assertNotEqual(user.id, self.users[0].id)
        
    def testUserUpdate(self):
        res = self.users[0].update()
        self.assertEqual(res, True)
        
        
if __name__ == '__main__':
    unittest.main()