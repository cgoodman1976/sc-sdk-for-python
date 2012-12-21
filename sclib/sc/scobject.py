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
from xml.dom.minidom import parseString

class SCObject(object):
    # Base class of All SecureCloud objects

    def __init__(self, connection=None):
        self.connection = connection
        
    def startElement(self, name, attrs, connection):
        # Mostly parsing XML attributes and begin of elements
        pass

    def endElement(self, name, value, connection):
        # Mostly parsing XML elements
        setattr(self, name, value)

    def buildElements(self, elements=None):
        # To build xml elements structure
        pass
    
    def niceFormat(self):
        # build from self's elements
        element = self.buildElements()
        if element is not None:
            xmlstr = parseString(ElementTree.tostring(element))
            pretty_res = xmlstr.toprettyxml()
            return pretty_res
