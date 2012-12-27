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

from sclib.resultset import ResultSet
from sclib.sc.scobject import SCObject
from sclib.sc.device import Device
from xml.etree import ElementTree


class SecurityGroupAction(SCObject):
    def __init__(self, connection):
        SCObject.__init__(self, connection)
        self.action = None
        self.autoDelay = None
        self.enable = None
        

class SecurityGroup(SCObject):
    
    ValidAttributes = [ 'id', 'name', 'href',
                       'isDeletable', 'isNameEditable', 'isResourcePool',
                       'lastModified', 'ruleCount', 'deviceCount', 'imageCount',
                       'EnableIC', 'ICAction', 'PostponeEnable', 
                       'RevokeIntervalType', 'RevokeIntervalNumber']
    
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
            self.rules.marker = name
            return self.rules
        else:
            return None

    def endElement(self, name, value, connection):
        if name == 'description':
            self.description = value
        else:
            setattr(self, name, value)
            
    def buildElements(self, elements=None):
        group = ElementTree.Element('securityGroup')
        
        if elements:
            #===================================================================
            # build selected elements
            #===================================================================
            # build attributes
            for e in elements:
                if e in self.ValidAttributes:
                    if getattr(self, e): group.attrib[e] = getattr(self, e)
                elif e == 'description':
                    description = ElementTree.SubElement(group, "description")
                    description.text = self.description
                elif e == 'securityRuleList':
                    group.append( self.rules.buildElements() )
                # TODO - Add actions
        else:
            #===================================================================
            # build all elements
            #===================================================================
            # build attributes
            for attr in self.ValidAttributes:
                if getattr(self, attr): group.attrib[attr] = getattr(self, attr)
            
            if self.description:
                description = ElementTree.SubElement(group, "description")
                description.text = self.description
            # append inner objects
            if self.rules: group.append( self.rules.buildElements() )
            # TODO - Add actions

        return group

class SecurityRule(SCObject):
    
    ValidAttributes = [ 'id', 'description', 'matchType', 'dataMissing']
    
    def __init__(self, connection):
        SCObject.__init__(self, connection)

        #member initialization
        self.id = None
        self.description = None
        self.matchType = None
        self.dataMissing = None
        # inner objects
        self.ruletype = None
        self.devices = None
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
        elif name == 'deviceList':
            self.devices = ResultSet([('device', Device)])
            self.devices.marker = 'deviceList'
            return self.devices
        elif name == 'securityRuleConditionList':
            self.conditions = ResultSet([('securityRuleCondition', SecurityRuleCondition)])
            self.conditions.marker = 'securityRuleConditionList'
            return self.conditions
        else:
            return None

    def endElement(self, name, value, connection):
        setattr(self, name, value)
    
    def buildElements(self, elements=None):
        rule = ElementTree.Element('securityRule')
        
        if elements:
            #===================================================================
            # build selected elements
            #===================================================================
            # build attributes
            for e in elements:
                if e in self.ValidAttributes:
                    if getattr(self, e): rule.attrib[e] = getattr(self, e)
                elif e == 'securityRuleType':
                    rule.append( self.ruletype.buildElements() )
                elif e == 'securityRuleConditionList':
                    rule.append( self.conditions.buildElements() )
        else:
            #===================================================================
            # build all elements
            #===================================================================
            # build attributes
            for attr in self.ValidAttributes:
                if getattr(self, attr): rule.attrib[attr] = getattr(self, attr)
            
            # append inner objects
            if self.ruletype: rule.append( self.ruletype.buildElements() )
            if self.conditions: rule.append( self.conditions.buildElements() )
            # TODO - Add actions

        return rule
        
    # ----- operation -----
    def update(self):
        pass
        
class SecurityRuleCondition(SCObject):
    ValidAttributes = ['evaluator', 'expectedValue']
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

    def buildElements(self, elements=None):
        condition = ElementTree.Element('securityRuleCondition')
        
        #user info
        if self.evaluator: condition.attrib['evaluator'] = self.evaluator
        if self.expectedValue: condition.attrib['expectedValue'] = self.expectedValue
        #actions
        return condition
    

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
            
    def buildElements(self, element=None):
        type = ElementTree.Element('securityRuleType')
        
        #user info
        if self.id: type.attrib['id'] = self.id
        if self.name: type.attrib['name'] = self.name
        if self.evaluator: type.attrib['evaluator'] = self.evaluator
        if self.context: type.attrib['context'] = self.context
        if self.dataType: type.attrib['dataType'] = self.dataType
        if self.description: type.attrib['description'] = self.description
        #actions
        return type
