#!/usr/bin/env python
# Copyright (c) 2012 Trend Micro, Inc. All rights reserved.
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish, dis-
# tribute, sublicense, and/or sell copies of the Software, and to permit
# persons to whom the Software is furnished to do so, subject to the fol-
# lowing conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
# OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABIL-
# ITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT
# SHALL THE AUTHOR BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.
#

"Test basic connection"
import unittest
from sclib.sc.device import Device

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

class SCConnectionTest(unittest.TestCase):
    def setUp(self):
        from sclib.sc.connection import SCConnection
        self.connection = SCConnection( MS_HOST,BROKER_NAME, BROKER_PASSPHASE, 
                                        AUTH_NAME, AUTH_PASSWORD)
    def testListAllDevice(self):
        self.connection.listAllDevices()


if __name__ == '__main__':
    unittest.main()