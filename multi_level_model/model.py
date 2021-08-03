#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import sys
import copy
import numpy as np
import pandas as pd
import scipy.spatial.distance as distance
import scipy.spatial as spatial
import scipy.integrate as integrate
import scipy.special as special
from sklearn.neighbors import NearestNeighbors
import networkx as nx
from pypdevs.infinity import INFINITY
import random
import string

# Import code for DEVS model representation:
from pypdevs.DEVS import *
class AgentAlpha(AtomicDEVS):
    def __init__(self, name="", id=0):
        # Always call parent class' constructor FIRST:
        AtomicDEVS.__init__(self, name)
        self.name = "AtomicAlphaAgent" + name
        self.current_time = 0.0
        self.id = id
        self.ta = 1
        self.elapsed = 0
        self.state = random.choice(string.ascii_uppercase)
        self.y_up = self.state


    def intTransition(self):
        self.current_time += self.ta 
        
        self.state = random.choice(string.ascii_uppercase)
        parent_info = self.parent.getContextInformation()
        pms = parent_info['parent']
        pms = ''.join(pms) if pms else ''
        gpms = parent_info['grandparent']
        print('%d,%s,%s,%s,%s' % (self.current_time, self.name,self.state, pms,gpms))
        # print('%d,%s,%s' % (self.current_time, self.name,self.state))
        self.y_up = copy.deepcopy(self.state)
        return self.state
    
    def extTransition(self, arg):
        self.current_time += self.ta 
        
        self.state = random.choice(string.ascii_uppercase)
        parent_info = self.parent.getContextInformation()
        pms = parent_info['parent']
        pms = ''.join(pms) if pms else ''
        gpms = parent_info['grandparent']
        # print('%d,%s,%s' % (self.current_time, self.name,self.state))
        print('%d,%s,%s,%s,%s' % (self.current_time, self.name,self.state, pms,gpms))
        self.y_up = copy.deepcopy(self.state)
        return self.state

    def __lt__(self, other):
        return self.name > other.name 

    def timeAdvance(self):
        if self.name == "AtomicAlphaAgent1":
            return 1
        return INFINITY

    def outputFnc(self):
        ret = {}
        ret[self.OPorts[0]] = self.state
        return ret

class Parent(CoupledDEVS):
    def __init__(self, name=None):
        CoupledDEVS.__init__(self, name)
        self.model_id = 3
        self.name = 'Parent'
        self.agents = []
        agent1 = AgentAlpha('1')
        agent2 = AgentAlpha('2')


        self.agents.append(self.addSubModel(agent1))
        self.agents.append(self.addSubModel(agent2))

        outport = agent1.addOutPort(name='p1')
        inport  = agent2.addInPort(name='p2')
        self.connectPorts(outport, inport)

        self.children_state = []
        self.state = ""
        self.parent_state = ""
        self.y_up = ""

    def globalTransition(self, e_g, x_b_micro, *args, **kwargs):
        super(Parent, self).globalTransition(e_g, x_b_micro, *args, **kwargs)
        # if len(self.children_state) >= 2:
        #     self.children_state.pop()
        self.children_state = x_b_micro
        self.y_up = "".join(self.children_state)
        self.parent_state = copy.deepcopy(self.parent.getContextInformation())
        self.state = self.y_up #+  str(self.parent_state)
        # print("%d,%s,%s" % (e_g, self.name, self.state))
        return

    def getContextInformation(self, *args, **kwargs):
        return {"parent": self.state, "grandparent": self.parent_state}

    def select(self, immChildren):
        return immChildren[0]

class GrandParent(CoupledDEVS):
    def __init__(self, name=None):
        CoupledDEVS.__init__(self, name)
        parent = Parent()

        self.name = 'GrandParent'
        self.addSubModel(parent)
        self.children_state = ""
        self.state = ""

    def globalTransition(self, e_g, x_b_micro, *args, **kwargs):
        super(GrandParent, self).globalTransition(e_g, x_b_micro, *args, **kwargs)
        self.state = x_b_micro[::-1]
        return

    def getContextInformation(self, *args, **kwargs):
        return self.state

    def select(self, immChildren):
        return immChildren[0]

