'''
Created on 2012/12/5

@author: bobby_chien
'''
from sclib.sc.scobject import SCObject

class Provider(SCObject):
    def __init__(self):
        self.name = None
        self.href = None
        self.providerLocation = None