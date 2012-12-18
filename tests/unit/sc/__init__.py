import unittest
import tests
import sclib

from sclib.sc.connection import SCConnection
from tests.unit import config, logging
from tests.unit.sc.connectionfilter import SCConnectionFilter

class SCBaseTestCase(unittest.TestCase):
    def __init__(self, methodName='runTest'):
        unittest.TestCase.__init__(self, methodName)
        self.connection = None
        self.auth = None

    def setUp(self):
        if not self.connection:
            self.connection = SCConnectionFilter( config.get('connection', 'MS_HOST'),
                                            config.get('connection', 'MS_BROKER_NAME'), 
                                            config.get('connection', 'MS_BROKER_PASSPHASE'))
            self.assertNotEqual(self.connection, None)

        if self.connection and (not self.auth):        
            self.auth = self.connection.basicAuth( config.get('authentication', 'AUTH_NAME'), 
                                              config.get('authentication', 'AUTH_PASSWORD'))
            self.assertNotEqual(self.auth, None)


    def tearDown(self):
        pass