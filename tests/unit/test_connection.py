import unittest
import sclib
import os
import tests


class SCAuthConnectionTest(unittest.TestCase):
    def __init__(self, methodName='runTest'):
        unittest.TestCase.__init__(self, methodName)
        self.connection = None
        self.auth = None
        
        # make sample path
        self.sample_path = os.path.join(os.path.dirname(os.path.abspath(tests.__file__ )), 'unit', 'sample')
        # make result path
        self.result_path = os.path.join(os.path.dirname(os.path.abspath(tests.__file__ )), 'unit', 'result')

    def setUp(self):

        path = os.path.join(self.result_path, '%s.%s' % (self.__class__.__name__, self._testMethodName) )
        if not os.path.exists(path):
            os.makedirs(path)

    	# enable debug log
        path = os.path.join(self.result_path, '%s.%s' % (self.__class__.__name__, self._testMethodName) )
        logpath = os.path.join(path, 'testCase.log' )
        sclib.set_file_logger(self._testMethodName, logpath, 'DEBUG')

        from sclib.connection import SCAuthConnection
        self.connection = SCAuthConnection( sclib.__config__.get('connection', 'MS_HOST'),
                                            sclib.__config__.get('connection', 'MS_BROKER_NAME'), 
                                            sclib.__config__.get('connection', 'MS_BROKER_PASSPHASE') )

    def testGetRequest(self):
        response = self.connection.make_request('PublicCertificate')
        self.assertNotEqual(response, None)
  
        
if __name__ == "__main__":
    unittest.main()

    