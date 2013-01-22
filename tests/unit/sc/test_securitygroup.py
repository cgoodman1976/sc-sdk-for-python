"Test basic security group function"
import unittest
import logging

from sclib.sc.securitygroup import SecurityGroup
from sclib.sc.instance import VirtualMachine, Image
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
        rulelist = self.connection.listAllSecurityRuleTypes()
        for rule in rulelist:
            newrule = self.connection.getSecurityRuleType(rule.id)
            self.assertEqual(rule.id, newrule.id)
            xml_pretty = newrule.niceFormat()
            logging.debug(xml_pretty)

    def testAddVM(self):
        policys = self.connection.listAllSecurityGroup()
        self.vms = self.connection.listAllVM()

        default_policy = None
        test_policy = None
        for policy in policys:
            sec = self.connection.getSecurityGroup(policy.id)
            self.assertEqual(policy.id, sec.id)
            xml_pretty = sec.niceFormat()
            logging.debug(xml_pretty)

            if policy.name == 'Default Policy':
                default_policy = policy
            elif policy.name == 'TESTING':
                test_policy = policy

        for vm in self.vms:
            new_image = Image(self.connection)
            new_image.id = vm.imageGUID
            #new_image.msUID = vm.imageGUID
            test_policy.imageList.append(new_image)

        test_policy.RevokeIntervalNumber = '59'
        test_policy.update()

        

if __name__ == '__main__':
    unittest.main()