import unittest

MS_HOST = "https://ms.cloud9.identum.com:7443/broker/API.svc/v3.5/"
MS_PORT = 7448
MS_BROKER_PATH = "/broker/API.svc/v3.5/"

BROKER_NAME = 'bobby'
BROKER_PASSPHASE = 'v5RWh0Lj5j'
AUTH_NAME = 'bobby_chien@trendmicro.com'
AUTH_PASSWORD = '1qaz@WSX'

REQUEST_PARAMS = { "tenant" : 'x23123',
                   }

REQUEST_HEADER = { 'Content-Type' :'application/xml; charset=utf-8',
                   'BrokerName' : BROKER_NAME
                   }
REQUEST_DATA = """<?xml version="1.0" encoding="utf-8"?><authentication 
                    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" 
                    xmlns:xsd="http://www.w3.org/2001/XMLSchema" id="" data="%s" accountId="" />"""

class SCAuthConnectionTest(unittest.TestCase):
    def setUp(self):
        from sclib.connection import SCAuthConnection
        self.connection = SCAuthConnection(MS_HOST,BROKER_NAME, BROKER_PASSPHASE, 
                                      AUTH_NAME, AUTH_PASSWORD)

    def testConnection(self):
        self.assertEqual(self.connection.isConnected(), True)

    def testGetRequest(self):
        self.assertEqual(self.connection.isConnected(), True)
        response = self.connection.make_request('GET', 'PublicCertificate')
        self.assertNotEqual(response, None)

class SCConnectionTestSuite(unittest.TestSuite):
    def __init__(self):
        # add all our test methods to our test suite
        unittest.TestSuite.__init__(self, map(
                HTTPRequestTest, ('test_Status___init__','test_Status_serialize')
                ))
        
if __name__ == "__main__":
    unittest.main()

    