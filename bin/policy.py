#!/usr/bin/python
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
from sclib.sc.instance import VirtualMachine, Image

def printPolicy(policy):
    print 'Name: %s' % (policy.name)
    print 'ID: %s' % (policy.id)
    print 'Number of Images: %s' % (policy.imageCount)
    print 'Integrity Check: %s' % (policy.EnableIC)
    print ''

def listAllSecurityGroup():
    policy_list = conn.listAllSecurityGroup()

    # list all virtual machines
    print 'Policies:'
    print '------------------------------------------'
    for policy in policy_list:
        printPolicy(policy)

def listSecurityGroup(id):
    policy = conn.getSecurityGroup(options.id)    
    if policy:
        printPolicy(policy) 
        
    return policy   

def addVM(policy, vmid):
    new_image = Image(policy.connection)
    new_image.id = vmid
    policy.imageList.append(new_image)
    policy.update()


if __name__ == '__main__':

    # commands
    parser = OptionParser(usage="policy [-i policy_id] [-l] [-a vm_id]")
    parser.add_option("-a", "--add_vm", help="Add a virtual machine to Policy", dest="vm", default=False, action='store')
    parser.add_option("-i", "--policy_id", help="", dest="id", default='', action='store')
    parser.add_option("-l", "--list", help="", dest='list', default=False, action='store_true')
    (options, args) = parser.parse_args()


    # begin connection
    conn = sclib.connect_sc( sclib.__config__.get_value('connection', 'MS_HOST'), 
                             sclib.__config__.get_value('connection', 'MS_BROKER_NAME'), 
                             sclib.__config__.get_value('connection', 'MS_BROKER_PASSPHASE'))
    if conn:
        auth = conn.basicAuth( sclib.__config__.get_value('authentication', 'AUTH_NAME'),
                               sclib.__config__.get_value('authentication', 'AUTH_PASSWORD'))

        if options.id:
            # list information of securityGroup
            policy = listSecurityGroup(options.id)
            
            # add a vm into securityGroup (aka policy)
            if options.vm:
                addVM(policy, options.vm)
    
        # dump all securityGroup from your account
        elif options.list:
            listAllSecurityGroup()
        else:
            listAllSecurityGroup()
