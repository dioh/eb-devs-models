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


# TODO: Verificar los elapsed y current time

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


# np.random.seed(0)

def reverse_exponential(x):
    return np.random.exponential(1/float(x))

def threshold(t, theta, a, b):
    if t < theta:
        return a
    else:
        return b

class Parameters:
    TOPOLOGY_FILE = "topology/lattice.adj"
    CULTURE_LENGTH = 5
    FASHION_RATE = 0.5
    TRAITS = 5

def enum(**kwargs):
    class Enum(object): pass
    obj = Enum()
    obj.__dict__.update(kwargs)
    return obj

ActionState = enum(P='PROPAGATING', N="NORMAL")

ENVProps = enum(DECAY='decay_rate', NUMBER_OF_CULTURES='agent_states', INFECT_RATE= 'infect_rate', FASHION='fashion')

class AgentState(object):
    def __init__(self, name, id):
        self._name = name
        self.current_time = 0.0
        self.id = id 
        self.ta = 0

        self.culture = [np.random.randint(1, Parameters.TRAITS) for i in range(Parameters.CULTURE_LENGTH)] 
        self.neighbors_culture = {} 
        self.action_state = ActionState.P 

    def __repr__(self):
        return "Agent: %s, culture: %s" % (str(self.name), str(self.culture))

class LogAgent(AtomicDEVS):
    def __init__(self):
        self.set_values()
        self.stats = []
        self.name='logAgent'
        self.ta = 1
        self.state = "LogAgent"
        self.current_time = 0 
        self.elapsed = 0 
        self.my_input = {}

    def __lt__(self, other):
        return self.name < other.name 

    def saveLoginfo(self): 
        number_of_cultures = self.parent.getContextInformation(ENVProps.NUMBER_OF_CULTURES)
        stats = (self.current_time, number_of_cultures)
        self.stats.append(stats) 

    def intTransition(self):
        self.current_time += self.ta
        self.saveLoginfo()

    def timeAdvance(self):
        return self.ta

    def set_values(self):
        self.ta = 1 #0.1

class Agent(AtomicDEVS):
    def __init__(self, name=None, id=None, kwargs=None):
        # Always call parent class' constructor FIRST:
        AtomicDEVS.__init__(self, name)
        self.elapsed = 0 
        self.in_event = self.addInPort("in_event")
        self.state = AgentState(name=name, id=id) 
        self.in_ports_dict = {}
        self.out_ports_dict = {}

        self.y_up = (self.state.id, self.state.culture)

    def add_connections(self, ag_id): 
        inport = self.addInPort(name=ag_id)
        self.in_ports_dict[ag_id] = inport
        outport = self.addOutPort(name=ag_id)
        self.out_ports_dict[ag_id] = outport
        return inport, outport

    def similarity_with(self, neighbor_culture):
        return sum(np.array(neighbor_culture) == np.array(self.state.culture))/float(len(self.state.culture))

    def mix_culture(self, neighbor_culture):
        same_culture_index = np.array(neighbor_culture) != np.array(self.state.culture)
        indexes = np.where(same_culture_index == True)
        rand_cult = np.random.choice(indexes[0], 1)[0]
        self.state.culture[rand_cult] = neighbor_culture[rand_cult]

    def get_neighbor(self):
        neighbor_key = np.random.choice(list(self.state.neighbors_culture.keys()), 1)[0]
        neighbor_culture = self.state.neighbors_culture[neighbor_key]
        return neighbor_culture

    def extTransition(self, inputs): 
        self.state.current_time += self.elapsed
        for k, v in inputs.items(): 
            self.state.neighbors_culture[k.name] = v
        return self.state

    def intTransition(self):
        self.state.current_time += self.state.ta 
        self.y_up = None
        if self.state.action_state == ActionState.P:
            self.state.action_state = ActionState.N
            self.y_up = (self.state.id, self.state.culture)
        else:
            toss = np.random.random()

            if toss > Parameters.FASHION_RATE:
                neighbor_culture = self.get_neighbor()
                similarity = self.similarity_with(neighbor_culture)
                if similarity < 1 and np.random.random() < similarity:
                    self.mix_culture(neighbor_culture)
                    self.state.action_state = ActionState.P
            else:
                feature, fashion = self.parent.getContextInformation(ENVProps.FASHION)
                self.state.culture[feature] = fashion
        return self.state

    def __lt__(self, other):
        return self.name < other.name 

    def outputFnc(self):
        ret = {}
        if self.state.action_state == ActionState.P:
            for outport in self.out_ports_dict.values():
                ret[outport] = self.state.culture 

        return ret

    def timeAdvance(self):
        ta = 0
        if self.state.action_state == ActionState.P:
            ta = 0
        elif self.state.action_state == ActionState.N:
            ta = 1 #reverse_exponential(5) + 1
        self.state.ta = ta
        return self.state.ta


class Environment(CoupledDEVS):
    def __init__(self, name=None):
        """
        A simple flocking system consisting
        """
        # Always call parent class' constructor FIRST:
        CoupledDEVS.__init__(self, name)
        self.G = nx.Graph()

        # Children states initialization
        self.create_topology() 


        log_agent = LogAgent()
        log_agent.OPorts = []
        log_agent.IPorts = []
        self.addSubModel(log_agent)
        self.agents[-1] = log_agent
        log_agent.saveLoginfo()

        self.points = None
        self.model = None
        self.updatecount = 0

    def create_topology(self):
        G = nx.read_adjlist(Parameters.TOPOLOGY_FILE)
        # G = nx.read_adjlist(Parameters.TOPOLOGY_FILE)
        self.agents = {}
        for i, node in G.nodes(data=True): 
            ag_id = int(i)
            agent = Agent(name="agent %s" % i, id=ag_id, kwargs=node) 
            self.agents[ag_id] = self.addSubModel(agent)
            self.G.add_node(agent.state.id)

        for i in G.edges():
            if i[0] == i[1]: continue
            ind0 = int(i[0])
            ind1 = int(i[1])
            a0 = self.agents[ind0]
            a1 = self.agents[ind1]
            
            i0, o0 = a0.add_connections(ind1)
            i1, o1 = a1.add_connections(ind0)

            self.connectPorts(o0, i1)
            self.connectPorts(o1, i0)

        self.cultures = {}

    def globalTransition(self, e_g, x_b_micro, *args, **kwargs):
        super(Environment, self).globalTransition(e_g, x_b_micro, *args, **kwargs)
        self.cultures.update(x_b_micro)

    def getContextInformation(self, property, *args, **kwargs):
        super(Environment, self).getContextInformation(property)

        if(property == ENVProps.NUMBER_OF_CULTURES):
            # cultures = [m.state.culture for m in self.agents.values()[:-1]]
            unique_cultures = []
            if self.cultures:
                unique_cultures = np.unique(np.array(list(self.cultures.values())), axis=0) 
            return len(unique_cultures)

        if(property == ENVProps.FASHION):
            # Get a random feature
            mat = np.array(list(self.cultures.values()))
            randind = np.random.randint(Parameters.CULTURE_LENGTH)
            feature = mat[:, randind]           
            fashion_value = np.bincount(feature).argmax()

            return randind, fashion_value


    def select(self, immChildren):
        """
        Choose a model to transition from all possible models.
        """
        # Doesn't really matter, as they don't influence each other
        return immChildren[0]

