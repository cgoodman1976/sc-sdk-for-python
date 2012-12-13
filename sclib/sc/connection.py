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

"Handle SecureCloud basic connection to SC Management API"
import xml.sax

from sclib.connection import SCQueryConnection
from sclib.sc.device import Device
from xml.dom.minidom import parse, parseString

class SCConnection(SCQueryConnection):

    def __init__(self, host_base, broker_name=None, broker_passphase=None,
                  auth_name=None, auth_password=None):
        SCQueryConnection.__init__( self, host_base, broker_name, broker_passphase,
                                    auth_name, auth_password)
    
    def listAllDevices(self):
        params = {}
        return self.get_list('device', params, 
                             [('device', Device)], method='GET')
        
        #device_xml = xml.dom.minidom.parseString(response.read())
        #deviceList = device_xml.getElementsByTagName("deviceList")[0]
        #devices = deviceList.getElementsByTagName("device")
        #device = Device()
        #for dev in devices:
        #    device.parse(dev)
        #return device
