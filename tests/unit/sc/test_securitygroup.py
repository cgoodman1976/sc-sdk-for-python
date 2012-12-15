"Test basic security group function"
import unittest
import logging

from tests.unit import config, logging
from sclib.sc.securitygroup import SecurityGroup

class SCSecurityGroupTest(unittest.TestCase):
    def setUp(self):
        from sclib.sc.connection import SCConnection
        self.connection = SCConnection( config.get('connection', 'MS_HOST'),
                                        config.get('connection', 'MS_BROKER_NAME'), 
                                        config.get('connection', 'MS_BROKER_PASSPHASE'))

        self.connection.basicAuth(  config.get('authentication', 'AUTH_NAME'), 
                                    config.get('authentication', 'AUTH_PASSWORD'))

        self.policys = self.connection.listAllSecurityGroup()

    def testPolicyCreate(self):
        for policy in self.policys:
            xml_pretty = policy.niceFormat()
            logging.debug(xml_pretty)
            
    def testListAllRuleTypes(self):
        rulelist = self.connection.listAllRules()
        for rule in rulelist:
            xml_pretty = rule.niceFormat()
            logging.debug(xml_pretty)


if __name__ == '__main__':
    unittest.main()