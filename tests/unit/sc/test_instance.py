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

"Test basic instance and vm"
import unittest
from sclib.sc.device import Device
from sclib.sc.instance import VirtualMachine
from sclib.sc.user import User
from tests.unit.sc import SCBaseTestCase

class SCVirtualMachineTest(SCBaseTestCase):
    def setUp(self):
        SCBaseTestCase.setUp(self)

        #===== implement initial code here for each test =====
        pass

    def testUpdateVM(self):
        self.vms = self.connection.listAllVM()

        for vm in self.vms:
            newvm = self.connection.getVM(vm.imageGUID)
            target = VirtualMachine(self.connection)
            target.imageGUID = newvm.imageGUID
            target.href = newvm.href
            target.imageDescription = newvm.href
            target.SecurityGroupGUID = newvm.SecurityGroupGUID
            target.autoProvision = newvm.autoProvision
            updated = target.update()
            self.assertEqual(updated.imageGUID, target.imageGUID)

    def testVM_ListDevices(self):
        self.vms = self.connection.listAllVM()
        for vm in self.vms:
            newvm = self.connection.getVM(vm.imageGUID)
            
            for dev in newvm.devices:
                d = newvm.getDevice(dev.id)

    def testCreateDeleteVM(self):
        pass

if __name__ == '__main__':
    unittest.main()