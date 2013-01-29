"Test basic connection"
import unittest
import logging
import base64
import random
import sclib

from tests.unit import config, logging
from tests.unit.sc import SCBaseTestCase
from tests.unit.sc.connectionfilter import SCConnectionFilter
from sclib.sc.device import Device
from sclib.sc.user import User

class SCUserTest(SCBaseTestCase):
    def setUp(self):
        SCBaseTestCase.setUp(self)
        self.users = self.connection.listAllUsers()

    def testCreateUser(self):

        users = []
        for i in range(1, 20):
            email = 'unittest+%s@securecloud.com' % i
            password = 'P@ssw0rd'
            auth = 'localuser'
            name = 'unit%s' % i
            first = 'test%s' % i
            roles = ['Administrator', 'Security Administrator', 
                     'Auditor', 'Key Approver', 'Data Analyst']
            MFA = ['true', 'false']

            user = self.connection.createUser( email,
                                               password,
                                               auth,
                                               name,
                                               first,
                                               email,
                                               roles[random.choice(range(1, len(roles)))],
                                               MFA[random.choice(range(1, len(MFA)))])
            self.assertNotEqual(user, None)
            if user:
                user.firstName = 'Updated'
                user.lastName = roles[random.choice(range(1, len(roles)))]
                user.setRole( roles[random.choice(range(1, len(roles)))],
                              MFA[random.choice(range(1, len(MFA)))] )
                res = user.update()
                self.assertNotEqual(res, None)

                # add into list
                users.append(user)

        # delete all user
        for u in users:
            res = u.delete()
            self.assertEqual(res, True)
  
    def testGetUser(self):      
        for user in self.users:  
            u = self.connection.getUser(user.id)
            self.assertNotEqual(u, None)
            self.assertEqual(user.id, u.id)

    def testChangePassword(self):

        # update passoword and validate
        email = config.get('authentication', 'AUTH_NAME')
        oldPassword = config.get('authentication', 'AUTH_PASSWORD')
        newPassword = '1qaz@WSX'
        res = self.connection.changeUserPassword(oldPassword, newPassword)
        self.assertNotEqual(res, None)

            # reset original password
        res = self.connection.changeUserPassword(newPassword, oldPassword)
        self.assertNotEqual(res, None)

if __name__ == '__main__':
    unittest.main()