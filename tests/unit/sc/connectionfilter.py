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
    #===========================================================================
    # A filter connection class to simulate request. 
    # The class also capture Request and Response into specified result folder.
    #===========================================================================
    def __init__( self, host_base, broker_name=None, broker_passphase=None, 
                  sample_path=None, result_path=None):
        SCConnection.__init__(self, host_base, broker_name, broker_passphase)

        # pseudo sample path
        self.sample_path = sample_path
        self.result_path = result_path
        
        if os.path.isdir(self.result_path) == False:
            os.makedirs(self.result_path)

        
    def make_request(self, action='', params=None, headers=None, data='', method='GET'):

        fake = None
        resfile = reqfile = action.replace('/', '^')
        reqfile = os.path.join(self.result_path, '[Request]-%s %s.xml' % (method, reqfile ) )
        resfile = os.path.join(self.result_path, '[Response]-%s %s.xml' % (method, resfile) )

        if self.sample_path:
            rf = io.open(reqfile, 'r')
            body = rf.read()
            fake = urllib.addinfourl(rf, 'Fake info', regfile, 400)
        else:

            # serialize Request data
            sclib.log.debug("---------- RESTFul Request ---------- " )
            sclib.log.debug('%s %s' % (method, action))
            rf = io.open(reqfile, 'wb')
            if data:
                # Format request data
                formated = self.nice_format(data)
                rf.write(formated)

                # Debug
                sclib.log.debug('DATA = \n%s' % (formated))
            rf.close()

            # make request to securecloud
            response = SCConnection.make_request(self, action, params, headers, data, method)
            if response:
                sclib.log.debug("---------- RESTFul Response (%s) ---------- " % (response.code) )
                body = response.read()
                
                # serialize Response data
                f = io.open(resfile, 'wb')
                if body:
                    # Format response data
                    formated = self.nice_format(body)
                    f.write(formated)

                    # Debug
                    if formated: sclib.log.debug('DATA: \n%s' % (formated))
                f.close()

                #make fake response
                resfp = StringIO.StringIO(body)
                fake = urllib.addinfourl(resfp, response.info(), response.geturl(), response.getcode())
                

            sclib.log.debug("------------------------------------------\n")
        return fake


