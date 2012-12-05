import unittest

MS_HOST = "https://ms.cloud9.identum.com"
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

class HTTPRequestTest(unittest.TestCase):
    def testRequest(self):
        from sclib.connection import HTTPRequest
        request = HTTPRequest("POST", MS_HOST, MS_PORT, MS_BROKER_PATH,
                              REQUEST_PARAMS, REQUEST_HEADER, REQUEST_DATA)
        self.assertEqual(request.method, "POST")
        self.assertEqual(request.port, MS_PORT)

class SCConnectionTestSuite(unittest.TestSuite):
    def __init__(self):
        # add all our test methods to our test suite
        unittest.TestSuite.__init__(self, map(
                HTTPRequestTest, ('test_Status___init__','test_Status_serialize')
                ))
        
if __name__ == "__main__":
    unittest.main()

    