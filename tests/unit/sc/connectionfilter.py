import sclib
import os
import io
import datetime
import tests
import copy
import StringIO
import urllib

from sclib.sc.connection import SCConnection
from time import gmtime, strftime

class SCConnectionFilter(SCConnection):
    def __init__(self, host_base, broker_name, broker_passphase, pseudo=False):
        SCConnection.__init__(self, host_base, broker_name, broker_passphase)

        # pseudo connection
        self.pseudo = pseudo
        
        #create datetime string
        time = strftime("%Y-%m-%d", gmtime())
        self.serial_path = os.path.join(os.path.dirname(os.path.abspath(tests.__file__ )), 'unit', 'result', time )
        if os.path.isdir(self.serial_path) == False:
            os.makedirs(self.serial_path)

        
    def make_request(self, action='', params=None, headers=None, data='', method='GET'):

        if self.pseudo == True:
            sample_path = os.path.join(os.path.dirname(os.path.abspath(tests.__file__ )), 'unit', 'sample')
            reqfile = action.replace('/', '^')
            reqfile = os.path.join(sample_path, '[Response]%s.xml' % (reqfile) )
            rf = io.open(reqfile, 'r')
            body = rf.read()
            return body
        
        else:
            reqfile = action.replace('/', '^')
            reqfile = os.path.join(self.serial_path, '[Request(%s)]%s.xml' % (method, reqfile ) )
            resfile = action.replace('/', '^')
            resfile = os.path.join(self.serial_path, '[Response]%s.xml' % (resfile) )

            # serialize Request data
            rf = io.open(reqfile, 'w')
            if (data is not None) and (len(data) != 0):
                rf.write(self.nice_format(data))
            rf.close()

            # make request to securecloud
            response = SCConnection.make_request(self, action, params, headers, data, method)
            if response:
                body = response.read()
                
                #make fake response
                resfp = StringIO.StringIO(body)
                fake = urllib.addinfourl(resfp, response.info(), response.geturl(), response.getcode())
                
                # serialize Response data
                f = io.open(resfile, 'w')
                if (body is not None) and (len(body) != 0):
                    f.write(self.nice_format(body))
                f.close()
                return fake

        return None
