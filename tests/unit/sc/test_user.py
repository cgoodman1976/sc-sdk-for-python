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
                                            '1qaz@WSX',
                                            'localuser',
                                            'unit2',
                                            'test2',
                                            'unittest2@securecloud.com',
                                            'Administrator',
                                            'false')
        self.assertNotEqual(user, None)
        if not user:
            # new user needs activation or password included
            res = user.update()
            self.assertNotEqual(res, None)

            res = user.delete()
            self.assertEqual(res, True)
  
    def testUserGet(self):      
        for user in self.users:  
            u = self.connection.getUser(user.id)
            self.assertNotEqual(u, None)
            self.assertEqual(user.id, u.id)
               
if __name__ == '__main__':
    unittest.main()