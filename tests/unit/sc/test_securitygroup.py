"Test basic security group function"
import unittest
import logging

from sclib.sc.securitygroup import SecurityGroup
from tests.unit import config, logging
from tests.unit.sc import SCBaseTestCase

class SCSecurityGroupTest(SCBaseTestCase):
    def setUp(self):
        SCBaseTestCase.setUp(self)
        
        #===== implement initial code here for each test =====
        pass

    def testListAllPolicy(self):
        policys = self.connection.listAllSecurityGroup()
        for policy in policys:
            sec = self.connection.getSecurityGroup(policy.id)
            self.assertEqual(policy.id, sec.id)
            xml_pretty = sec.niceFormat()
            logging.debug(xml_pretty)
            
    def testListAllRuleTypes(self):
        rulelist = self.connection.listAllRules()
        for rule in rulelist:
            xml_pretty = rule.niceFormat()
            logging.debug(xml_pretty)


if __name__ == '__main__':
    unittest.main()