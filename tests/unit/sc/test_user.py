"Test basic connection"
import unittest
import logging

from tests.unit import config, logging
from tests.unit.sc import SCBaseTestCase
from sclib.sc.device import Device
from sclib.sc.user import User

class SCUserTest(SCBaseTestCase):
    def setUp(self):
        SCBaseTestCase.setUp(self)
        self.users = self.connection.listAllUsers()

        #===== implement initial code here for each test =====
        pass

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