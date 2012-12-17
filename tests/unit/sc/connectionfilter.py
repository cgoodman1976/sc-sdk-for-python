import sclib
import os
import io
import datetime
import tests
import copy

from sclib.sc.connection import SCConnection
from time import gmtime, strftime

class SCConnectionFilter(SCConnection):
    def __init__(self, host_base, broker_name, broker_passphase, ):
        SCConnection.__init__(self, host_base, broker_name, broker_passphase)

        #create datetime string
        time = strftime("%Y-%m-%d-%H-%M-%S", gmtime())
        self.serial_path = os.path.join(os.path.dirname(os.path.abspath(tests.__file__ )), 'unit', 'result', time )
        if os.path.isdir(self.serial_path) == False:
            os.makedirs(self.serial_path)

        
    def make_request(self, action='', params=None, headers=None, data='', method='GET'):

        body = SCConnection.make_request(self, action, params, headers, data, method)
    
        # serialize Request data
        reqfile = action.replace('/', '-')
        reqfile = os.path.join(self.serial_path, 'Request(%s)-%s.xml' % (method, reqfile) )
        rf = io.open(reqfile, 'w')
        rf.write(self.nice_format(data))
        rf.close()

        # serialize Response data
        resfile = action.replace('/', '-')
        resfile = os.path.join(self.serial_path, 'Response-%s.xml' % (resfile) )
        f = io.open(resfile, 'w')
        f.write(self.nice_format(body))
        f.close()
        
        return body
