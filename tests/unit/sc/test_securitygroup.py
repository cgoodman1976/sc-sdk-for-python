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
                default_policy = sec
            elif policy.name == 'TESTING':
                test_policy = sec

        for vm in self.vms:
            new_image = Image(self.connection)
            new_image.id = vm.imageID
            #new_image.msUID = vm.imageGUID
            test_policy.imageList.append(new_image)

        response = None
        test_policy.RevokeIntervalNumber = '59'
        response = test_policy.update()
        self.assertEqual(response.code, 200)

        for vm in self.vms:
            new_image = Image(self.connection)
            new_image.id = vm.imageID
            #new_image.msUID = vm.imageGUID
            default_policy.imageList.append(new_image)

        default_policy.RevokeIntervalNumber = '59'
        response = default_policy.update()
        self.assertEqual(response.code, 200)



        

if __name__ == '__main__':
    unittest.main()