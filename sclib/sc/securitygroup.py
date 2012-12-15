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

from sclib.sc.scobject import SCObject
from sclib.resultset import ResultSet
from xml.etree import ElementTree

class SecurityGroupAction(SCObject):
    def __init__(self, connection):
        SCObject.__init__(self, connection)
        self.action = None
        self.autoDelay = None
        self.enable = None
        

class SecurityGroup(SCObject):
    def __init__(self, connection):
        SCObject.__init__(self, connection)

        #member initialization
        self.id = None
        self.name = None
        self.isDeletable = None
        self.isNameEditable = None
        self.isResourcePool = None
        self.href = None
        self.lastModified = None
        self.ruleCount = None
        self.deviceCount = None
        self.imageCount = None
        self.EnableIC = None
        self.ICAction = None
        self.PostponeEnable = None
        self.RevokeIntervalType = None
        self.RevokeIntervalNumber = None
        self.description = None
        #rules
        self.rules = None
        #action
        self.successAction = None
        self.failedAction = None
        self.integrityAction = None
        
        
    def startElement(self, name, attrs, connection):
        ret = SCObject.startElement(self, name, attrs, connection)
        if ret is not None:
            return ret
        
        if name == 'securityGroup':
            for key, value in attrs.items():
                setattr(self, key, value)
            return self
        elif name == 'securityRuleList':
            self.rules = ResultSet([('securityRule', SecurityRule)])
            return self.rules
        else:
            return None

    def endElement(self, name, value, connection):
        if name == 'description':
            self.description = value
        else:
            setattr(self, name, value)
            
    def buildElements(self):
        group = ElementTree.Element('securityGroup')
        group.attrib['version'] = '3.5'
        
        #user info
        if self.id: group.attrib['id'] = self.id
        if self.name: group.attrib['name'] = self.name
        if self.isDeletable: group.attrib['isDeletable'] = self.isDeletable
        if self.isNameEditable: group.attrib['isNameEditable'] = self.isNameEditable
        if self.isResourcePool: group.attrib['isResourcePool'] = self.isResourcePool
        if self.href: group.attrib['href'] = self.href
        if self.lastModified: group.attrib['lastModified'] = self.lastModified
        if self.ruleCount: group.attrib['ruleCount'] = self.ruleCount
        if self.deviceCount: group.attrib['deviceCount'] = self.deviceCount
        if self.EnableIC: group.attrib['EnableIC'] = self.EnableIC
        if self.ICAction: group.attrib['ICAction'] = self.ICAction
        if self.PostponeEnable: group.attrib['PostponeEnable'] = self.PostponeEnable
        if self.RevokeIntervalType: group.attrib['RevokeIntervalType'] = self.RevokeIntervalType
        if self.RevokeIntervalNumber: group.attrib['RevokeIntervalNumber'] = self.RevokeIntervalNumber
        if self.description: group.attrib['description'] = self.description
        #rules
        if self.rules: group.append(self.rules.buildElement())
                
        #actions
        return group

class SecurityRule(SCObject):
    def __init__(self, connection):
        SCObject.__init__(self, connection)

        #member initialization
        self.id = None
        self.description = None
        self.matchType = None
        self.dataMissing = None
        self.ruletype = None
        self.conditions = None

    def startElement(self, name, attrs, connection):
        ret = SCObject.startElement(self, name, attrs, connection)
        if ret is not None:
            return ret
        
        if name == 'securityRule':
            for key, value in attrs.items():
                setattr(self, key, value)
        elif name == 'securityRuleType':
            self.ruletype = SecurityRuleType(connection)
            self.ruletype.startElement(name, attrs, connection)
            return self.ruletype
        elif name == 'securityRuleConditionList':
            self.conditions = ResultSet([('securityRuleCondition', SecurityRuleCondition)])
            return self.conditions
        else:
            return None

    def endElement(self, name, value, connection):
        setattr(self, name, value)
    
    def buildElement(self):
        group = ElementTree.Element('securityRule')
        group.attrib['version'] = '3.5'
        
        #user info
        if self.id: group.attrib['id'] = self.id
        if self.description: group.attrib['description'] = self.description
        #actions
        return group
        
    # ----- operation -----
    def update(self):
        pass
        
class SecurityRuleCondition(SCObject):
    def __init__(self, connection):
        SCObject.__init__(self, connection)

        #member initialization
        self.evaluator = None
        self.expectedValue = None

    def startElement(self, name, attrs, connection):
        ret = SCObject.startElement(self, name, attrs, connection)
        if ret is not None:
            return ret
        
        if name == 'securityRuleCondition':
            for key, value in attrs.items():
                setattr(self, key, value)
            return self
        else:
            return None

    def endElement(self, name, value, connection):
        setattr(self, name, value)

    

class SecurityRuleType(SCObject):
    def __init__(self, connection):
        SCObject.__init__(self, connection)

        #member initialization
        self.id = None
        self.name = None
        self.evaluator = None
        self.context = None
        self.dataType = None
        self.description = None
        
    def startElement(self, name, attrs, connection):
        ret = SCObject.startElement(self, name, attrs, connection)
        if ret is not None:
            return ret
        
        if name == 'securityRuleType':
            for key, value in attrs.items():
                setattr(self, key, value)
            return self
        else:
            return None

    def endElement(self, name, value, connection):
        if name == 'description':
            self.description = value
        else:
            setattr(self, name, value)
            
    def buildElements(self):
        group = ElementTree.Element('securityRuleType')
        group.attrib['version'] = '3.5'
        
        #user info
        if self.id: group.attrib['id'] = self.id
        if self.name: group.attrib['name'] = self.name
        if self.evaluator: group.attrib['evaluator'] = self.evaluator
        if self.context: group.attrib['context'] = self.context
        if self.dataType: group.attrib['dataType'] = self.dataType
        if self.description: group.attrib['description'] = self.description
        #actions
        return group
