import os
import unittest
import ConfigParser
import logging
import tests


config = ConfigParser.SafeConfigParser()
DEFAULT_TEST_CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(tests.__file__ )), "unit/test.cfg")
config.read(DEFAULT_TEST_CONFIG_FILE)

logger = logging
logging.basicConfig(level=config.get('debug', 'level'))


#class SCBaseTestCase(unittest):
#    def setUp(self):
#        pass