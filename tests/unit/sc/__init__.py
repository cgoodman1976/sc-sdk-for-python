import unittest
import tests.unit.sc.test_device as DeviceTest
import tests.unit.sc.test_scconnection as ConnectionTest


class   SCTestSuite(unittest.TestSuite):
    def __init__(self):
        unittest.TestSuite.__init__(self, map(ConnectionTest.SCConnectionTest(), ('testListAllDevice')))
    
if __name__ == '__main__':
    unittest.main()
