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
import numpy as np
import pandas as pd
import scipy.spatial.distance as distance
import scipy.spatial as spatial
import scipy.integrate as integrate
import scipy.special as special
from sklearn.neighbors import NearestNeighbors
import networkx as nx
from pypdevs.infinity import INFINITY

# Import code for DEVS model representation:
from pypdevs.DEVS import *
class Agent(AtomicDEVS):
    def __init__(self, name="", id=0):
        # Always call parent class' constructor FIRST:
        AtomicDEVS.__init__(self, name)
        self.name = "AtomicAgent"
        self.current_time = 0.0
        self.id = id
        self.ta = 1
        self.elapsed = 0
        self.state = True
        self.y_up = self.state

    def extTransition(self, inputs): 
        return

    def intTransition(self):
        self.current_time += self.ta 
        self.state = not self.state
        self.y_up = self.state
        print "state", self.state
        print self.parent.getContextInformation()
        return self.state

    def __lt__(self, other):
        return self.name < other.name 

    def outputFnc(self):
        ret = {}
        return ret

    def timeAdvance(self):
        self.ta = 1
        return self.ta


class Parent(CoupledDEVS):
    def __init__(self, name=None):
        CoupledDEVS.__init__(self, name)
        self.model_id = 2
        agent = Agent()
        self.addSubModel(agent)
        self.children_state = None
        self.parent_state = None
        self.y_up = None

    def globalTransition(self, e_g, x_b_micro, *args, **kwargs):
        super(Parent, self).globalTransition(e_g, x_b_micro, *args, **kwargs)
        self.children_state = x_b_micro
        self.y_up = self.children_state
        self.parent_state = self.parent.getContextInformation('STATE')
        return

    def getContextInformation(self, *args, **kwargs):
        return {"parent": self.children_state, "grandparent": self.parent_state}

class GrandParent(CoupledDEVS):
    def __init__(self, name=None):
        CoupledDEVS.__init__(self, name)
        parent = Parent()
        self.addSubModel(parent)
        self.children_state = None
        self.parent_state = None

    def globalTransition(self, e_g, x_b_micro, *args, **kwargs):
        super(GrandParent, self).globalTransition(e_g, x_b_micro, *args, **kwargs)
        self.children_state = x_b_micro
        return

    def getContextInformation(self, *args, **kwargs):
        return self.children_state

    def select(self, immChildren):
        return immChildren[0]

