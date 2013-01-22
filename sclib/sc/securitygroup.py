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
from sclib.sc.instance import VirtualMachine, Image
from xml.etree import ElementTree


class SecurityGroupAction(SCObject):
    def __init__(self, connection):
        SCObject.__init__(self, connection)
        self.action = None
        self.autoDelay = None
        self.enable = None
        

class SecurityGroup(SCObject):
    
    ValidAttributes = [ 'id', 'name', 'href',
                       'isDeleteble', 'isNameEditable',
                       'lastModified', 'ruleCount', 'imageCount',
                       'EnableIC', 'ICAction', 'PostponeEnable', 
                       'RevokeIntervalType', 'RevokeIntervalNumber']
    
    def __init__(self, connection):
        SCObject.__init__(self, connection)

        #member initialization
        self.id = None
        self.name = None
        self.isDeleteble = None
        self.isNameEditable = None
        self.href = None
        self.lastModified = None
        self.ruleCount = None
        self.imageCount = None
        self.EnableIC = None
        self.ICAction = None
        self.PostponeEnable = None
        self.RevokeIntervalType = None
        self.RevokeIntervalNumber = None
        self.description = None
        #rules
        self.securityRuleList = ResultSet([('securityRule', SecurityRule)])
        self.securityRuleList.marker = 'securityRuleList'
        #action
        self.successAction = None
        self.failedAction = None
        self.integrityAction = None
        #image or vm
        self.imageList = ResultSet( [('image', Image)])
        self.imageList.marker = 'imageList'
        
        
    def startElement(self, name, attrs, connection):
        ret = SCObject.startElement(self, name, attrs, connection)
        if ret is not None:
            return ret
        
        if name == 'securityGroup':
            for key, value in attrs.items():
                setattr(self, key, value)
            return self
        elif name == 'securityRuleList':
            if not self.securityRuleList:
                self.securityRuleList = ResultSet([('securityRule', SecurityRule)])
                self.securityRuleList.marker = name
            return self.securityRuleList
        elif name == 'imageList':
            self.imageList = ResultSet( [('image', Image)])
            self.imageList.marker = name
            return self.imageList
        elif name == 'successAction':
            self.successAction = SecurityGroupAction(connection)
            self.successAction.name = name
            self.successAction.action = attrs['action']
            self.successAction.autoDelay = attrs['autoDelay']
            return self.successAction
        elif name == 'failedAction':
            self.failedAction = SecurityGroupAction(connection)
            self.failedAction.name = name
            self.failedAction.action = attrs['action']
            self.failedAction.autoDelay = attrs['autoDelay']
            return self.failedAction
        else:
            return None

    def endElement(self, name, value, connection):
        if name == 'description':
            self.description = value
        else:
            setattr(self, name, value)
            
    def buildElements(self):
        group = ElementTree.Element('securityGroup')
        
        #===================================================================
        # build Required elements
        # build attributes
        for e in self.ValidAttributes:
            if getattr(self, e): group.attrib[e] = getattr(self, e)

        if self.description:
            description = ElementTree.SubElement(group, "description")
            description.text = self.description

        # actions
        if self.successAction: group.append( self.successAction.buildElements() )
        if self.failedAction: group.append( self.failedAction.buildElements() )

        # append inner objects
        if self.imageList: group.append( self.imageList.buildElements() )
        if self.securityRuleList: group.append( self.securityRuleList.buildElements() )
        # TODO - Add actions

        return group

    # ---------- function ----------
    
    def update(self):
        # Build XML elements structures
        action = '%s/%s/' % (self.connection.REST_SECURITY_GROUP, self.id)
        data = ElementTree.tostring(self.buildElements())
        response = self.connection.make_request(action, data=data, method='POST')
        return response
    

class SecurityRule(SCObject):
    
    ValidAttributes = ['id', 'description', 'matchType', 'dataMissing']
    
    def __init__(self, connection):
        SCObject.__init__(self, connection)

        #member initialization
        self.id = None
        self.description = None
        self.matchType = None
        self.dataMissing = None
        # inner objects
        self.securityRuleType = None
        self.deviceList = None
        self.securityRuleConditionList = None

    def startElement(self, name, attrs, connection):
        ret = SCObject.startElement(self, name, attrs, connection)
        if ret is not None:
            return ret
        
        if name == 'securityRule':
            for key, value in attrs.items():
                setattr(self, key, value)
        elif name == 'securityRuleType':
            self.securityRuleType = SecurityRuleType(connection)
            self.securityRuleType.startElement(name, attrs, connection)
            return self.securityRuleType
        elif name == 'deviceList':
            self.deviceList = ResultSet([('device', Device)])
            self.deviceList.marker = 'deviceList'
            return self.deviceList
        elif name == 'securityRuleConditionList':
            self.securityRuleConditionList = ResultSet([('securityRuleCondition', SecurityRuleCondition)])
            self.securityRuleConditionList.marker = 'securityRuleConditionList'
            return self.securityRuleConditionList
        else:
            return None

    def endElement(self, name, value, connection):
        setattr(self, name, value)
    
    def buildElements(self):
        rule = ElementTree.Element('securityRule')
        
        #===================================================================
        # Required elements
        # build attributes
        for e in self.ValidAttributes:
            if getattr(self, e): rule.attrib[e] = getattr(self, e)

        #===================================================================
        # Optional elements
            
        # append inner objects
        if self.securityRuleType: rule.append( self.securityRuleType.buildElements() )
        if self.securityRuleConditionList: rule.append( self.securityRuleConditionList.buildElements() )
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

    def buildElements(self):
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
            return retn
        
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
        type = ElementTree.Element('securityRuleType')

        # 'Required' fields        
        #user info
        if self.id: type.attrib['id'] = self.id
        if self.name: type.attrib['name'] = self.name
        if self.evaluator: type.attrib['evaluator'] = self.evaluator
        if self.context: type.attrib['context'] = self.context
        if self.dataType: type.attrib['dataType'] = self.dataType
        if self.description: type.attrib['description'] = self.description
        #actions

        return type

class SecurityGroupAction(SCObject):
    ValidAttributes = ['action', 'autoDelay']
    def __init__(self, connection):
        SCObject.__init__(self, connection)

        #member initialization
        self.name = None
        self.action = None
        self.autoDelay = None

    def startElement(self, name, attrs, connection):
        ret = SCObject.startElement(self, name, attrs, connection)
        if ret is not None:
            return ret
        
        return None

    def endElement(self, name, value, connection):
        setattr(self, name, value)

    def buildElements(self):
        action = ElementTree.Element(self.name)
        
        #user info
        if self.action: action.attrib['action'] = self.action
        if self.autoDelay: action.attrib['autoDelay'] = self.autoDelay
        #actions
        return action
