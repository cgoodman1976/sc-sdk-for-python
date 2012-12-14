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

from xml.etree import ElementTree

class SCObject(object):

    def __init__(self, connection=None):
        self.connection = connection
        
    # for XML parse
    def startElement(self, name, attrs, connection):
        return None

    # for XML parse
    def endElement(self, name, value, connection):
        setattr(self, name, value)

    # build xml elements structure
    def buildElements(self):
        pass
    
    def buildXML(self, element=None):
        if element: 
            # build xml from element input
            element_data = ElementTree.tostring(element)
            return element_data

        # build from self's elements
        self_element = self.buildElements()
        if self_element is not None:
            data = ElementTree.tostring(self_element)
            return data
