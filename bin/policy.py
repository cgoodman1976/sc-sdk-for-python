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


import sys
from optparse import OptionParser

import sclib
from sclib.sc.connection import SCConnection
from sclib.sc.securitygroup import SecurityGroup

if __name__ == '__main__':

    parser = OptionParser(usage="vm [-id] [-addvm]")
    parser.add_option("-a", "--add_virtual", help="Add a virtual machine to Policy", dest="vm", default="")
    parser.add_option("-i", "--policy_id", help="", dest="id", default="")
    (options, args) = parser.parse_args()

    conn = sclib.connect_sc( sclib.__config__.get_value('connection', 'MS_HOST'), 
                             sclib.__config__.get_value('connection', 'MS_BROKER_NAME'), 
                             sclib.__config__.get_value('connection', 'MS_BROKER_PASSPHASE'))
    if conn:
        auth = conn.basicAuth( sclib.__config__.get_value('authentication', 'AUTH_NAME'),
                               sclib.__config__.get_value('authentication', 'AUTH_PASSWORD'))

        if options.id:
            policy = conn.getSecurityGroup(id)        
            print 'Policy:'
            print '------------------------------------------'
            print 'Name: %s' % (policy.name)
            print 'ID: %s' % (policy.id)
            print 'Number of Images: %s' % (policy.imageCount)
            print 'Integrity Check: %s' % (policy.EnableIC)
            print ''

        else:
            policy_list = conn.listAllSecurityGroup()

            # list all virtual machines
            print 'Policies:'
            print '------------------------------------------'
            for policy in policy_list:
                print 'Name: %s' % (policy.name)
                print 'ID: %s' % (policy.id)
                print 'Number of Images: %s' % (policy.imageCount)
                print 'Integrity Check: %s' % (policy.EnableIC)
                print ''



