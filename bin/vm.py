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
from sclib.sc.instance import VirtualMachine

def printVM(vm):
    print 'Name: %s' % (vm.imageName)
    print 'GUID: %s' % (vm.imageGUID)
    print 'ID: %s' % (vm.imageID)
    print 'Encrypted Devices: %s' % (vm.encryptedDeviceCount)
    print ''

def listAllVM():
    vms = conn.listAllVM()

    # list all virtual machines
    print 'Virtual Machines:'
    print '------------------------------------------'
    for vm in vms:
        printVM(vm)

def listVM(id):
    vm = conn.getVM(id)    
    if vm:
        printVM(vm) 
        
    return vm   


if __name__ == '__main__':

    # commands
    parser = OptionParser(usage="vm [-l] [-i vm_id]")
    parser.add_option("-i", "--vm_id", help="", dest="id", default='', action='store')
    parser.add_option("-l", "--list", help="", dest='list', default=False, action='store_true')
    (options, args) = parser.parse_args()

    conn = sclib.connect_sc( sclib.__config__.get_value('connection', 'MS_HOST'), 
                             sclib.__config__.get_value('connection', 'MS_BROKER_NAME'), 
                             sclib.__config__.get_value('connection', 'MS_BROKER_PASSPHASE'))
    if conn:
        auth = conn.basicAuth( sclib.__config__.get_value('authentication', 'AUTH_NAME'),
                               sclib.__config__.get_value('authentication', 'AUTH_PASSWORD'))

        if options.id:
            # list information of securityGroup
            policy = listVM(options.id)
            
    
        # dump all vm from your account
        elif options.list:
            listAllVM()
        else:
            listAllVM()


