import unittest
import tests
import sclib
import os

from sclib.sc.connection import SCConnection
from tests.unit import config, logging
from tests.unit.sc.connectionfilter import SCConnectionFilter

class SCBaseTestCase(unittest.TestCase):
    def __init__(self, methodName='runTest'):
        unittest.TestCase.__init__(self, methodName)
        self.connection = None
        self.auth = None
        
        # make sample path
        self.sample_path = os.path.join(os.path.dirname(os.path.abspath(tests.__file__ )), 'unit', 'sample')
        # make result path
        self.result_path = os.path.join(os.path.dirname(os.path.abspath(tests.__file__ )), 'unit', 'result')


    def setUp(self):
        if not self.connection:
            self.connection = SCConnectionFilter( config.get('connection', 'MS_HOST'),
                                                  config.get('connection', 'MS_BROKER_NAME'), 
                                                  config.get('connection', 'MS_BROKER_PASSPHASE'),
                                                  result_path=self.result_path)
            self.assertNotEqual(self.connection, None)

        if self.connection and (not self.auth):        
            self.auth = self.connection.basicAuth( config.get('authentication', 'AUTH_NAME'), 
                                                   config.get('authentication', 'AUTH_PASSWORD'))
            self.assertNotEqual(self.auth, None)

    def testAuthentication(self):
        if self.auth:        
            xml = self.auth.niceFormat()
            logging.debug(xml)
        
    def tearDown(self):
        self.connection.close()
        pass
    
if __name__ == '__main__':
    unittest.main()