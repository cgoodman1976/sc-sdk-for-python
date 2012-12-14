import unittest
import ConfigParser
import logging

config = ConfigParser.SafeConfigParser()
#config.read('D:\\GitHub\\sc-sdk-for-python\\tests\\unit\\test.cfg')
config.read('/Users/admin/Documents/github/sc-sdk-for-python/tests/unit/test.cfg')

logger = logging
logging.basicConfig(level=config.get('debug', 'level'))


#class SCBaseTestCase(unittest):
#    def setUp(self):
#        pass