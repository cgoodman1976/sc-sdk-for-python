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
        self.serial_path = os.path.join(os.path.dirname(os.path.abspath(tests.__file__ )), "unit/result/%s" % (time) )
        if os.path.isdir(self.serial_path) == False:
            os.makedirs(self.serial_path)

        
    def make_request(self, action='', params=None, headers=None, data='', method='GET'):

        body = SCConnection.make_request(self, action, params, headers, data, method)
    
        # serialization
        filename = action.replace('/', '-')
        filepath = '%s/%s.xml' % (self.serial_path, filename)
        f = io.open(filepath, 'a')
        f.write(self.nice_format(body))
        f.close()
        
        return body
