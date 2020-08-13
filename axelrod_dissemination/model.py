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
    TOPOLOGY_FILE = ""
    CULTURE_LENGTH = 5

    EMERGENT_MODEL = False
    INITIAL_PROB = 0.05
    RHO_PROB = 4.0
    TW_SIZE = 5.0
    TW_TRHD = 5.0
    TW_BIN_SIZE = 15.0

    NU = 10
    A = NU
    B = 0
    CI = 10
    CV = 1

    U = staticmethod(threshold)

    RECOVERY_TIME = 5.0
    DEATH_TIME = 30.0 
    RECOVERY_PROB = 0.95 

    VACC_MODEL = False 

    ALPHA_RATE =  0.4
    BETA_RATE = 0.10 
    GAMMA_RATE = 1.0/7

    DEATH_MEAN_TIME = 15.0
    RECOVERY_MEAN_TIME = 7

DEBUG = True


def enum(**kwargs):
    class Enum(object): pass
    obj = Enum()
    obj.__dict__.update(kwargs)
    return obj

ActionState = enum(P='PROPAGATING', N="NORMAL")

ENVProps = enum(DECAY='decay_rate', AGENT_STATES='agent_states', INFECT_RATE= 'infect_rate')

class AgentState(object):
    def __init__(self, name, id, state, kwargs):
        """TODO: to be defined1. """
        self._name = name
        self.current_time = 0.0
        self.id = id 
        self.ta = reverse_exponential(1)

        self.culture = [random.randint(1, 10) for i in range(Parameters.CULTURE_LENGTH)] 
        self.neighbors_culture = {} 
        self.state = ActionState.P 

    @property
    def name(self):
        """I'm the 'heading' property."""
        return self._name

    @property
    def ta(self):
        """I'm the 'heading' property."""
        return self._ta

    @ta.setter
    def ta(self, ta):
        self._ta = ta

    def get(self):
        return(self._name, self._state)

    def __repr__(self):
        return "Agent: %s, culture: %s" % (str(self.name), str(self.culture))

class LogAgent(AtomicDEVS):
    def __init__(self):
        self.set_values()
        self.stats = []
        self.name='logAgent'
        self.state.ta = ta
        self.current_time = 0 
        self.elapsed = 0 
        self.my_input = {}

    def saveLoginfo(self): 
        pass
        # parent_items = self.parent.getContextInformation(ENVProps.AGENT_STATES).items()
        # (unique, counts) = np.unique(np.array([it[1][0] for it in parent_items]), return_counts=True) 
        # frequencies = dict(zip(unique, counts))
        # log_data = [frequencies.get(key, 0) for key in SIRStates.__dict__.values()]
        # log_data.insert(0, self.current_time) 
        # self.stats.append(log_data) 

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

    def add_connections(self, ag_id):
        inport = self.addInPort(name=ag_id)
        self.in_ports_dict[ag_id] = inport
        outport = self.addOutPort(name=ag_id)
        self.out_ports_dict[ag_id] = outport

    def extTransition(self, inputs):
        self.state.current_time += self.elapsed
        return self.state

    def intTransition(self):
        self.state.current_time += self.state.ta 
        return self.state

    def __lt__(self, other):
        return self.name < other.name 

    def outputFnc(self):
        return self.state.outputFnc() 

    def timeAdvance(self):
        ta = 0
        if self.state.action == ActionState.P:
            ta = 0
        elif self.state.action == ActionState.N:
            ta = reverse_exponential(5) 
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

        for i in self.agents:
            self.G.add_node(i.state.id)

        log_agent = LogAgent()
        log_agent.OPorts = []
        log_agent.IPorts = []
        self.addSubModel(log_agent)
        self.agents.append(log_agent)
        log_agent.saveLoginfo()

        self.points = None
        self.model = None
        self.updatecount = 0

    def create_topology(self):
        G = nx.read_gml(Parameters.TOPOLOGY_FILE)
        # G = nx.read_adjlist(Parameters.TOPOLOGY_FILE)
        self.agents = []
        for i, node in G.nodes(data=True): 
            self.agents.append(Agent(name="agent %s" % i, id=int(i), kwargs=node))


        for agent in self.agents:
            self.addSubModel(agent)

        for i in G.edges():
            if i[0] == i[1]: continue
            add_connections
            ind0 = int(i[0])
            ind1 = int(i[1])
            a0 = self.agents[ind0]
            a1 = self.agents[ind1]
            
            i0, o0 = a0.add_connections(ind1)
            i1, o1 = a1.add_connections(ind0)

            self.connectPorts(o0, i1)
            self.connectPorts(o1, i0)

    def saveChildrenState(self, state):
        super(Environment, self).saveChildrenState(state)
        # if not state[0]:
        #     return
        # if state[0].state == SIRStates.I:
        #     bin = int(state[0].current_time) / Parameters.TW_BIN_SIZE
        #     self.time_window[bin] = self.time_window.get(bin, 0) + 1

        # self.targets = {}
        # if state[0].state == SIRStates.E:
        #     node_from = state[0].infected_by
        #     node_to = state[0].id

        #     current_time = state[0].current_time
        #     self.G.add_edge(node_from, node_to,
        #             timestamp=current_time)
        #     self.G.nodes[node_to]['start'] = current_time

        # if state[0].state in (SIRStates.D, SIRStates.R) :
        #     node = state[0].id
        #     current_time = state[0].current_time
        #     self.G.nodes[node]['end'] = current_time

        # self.agent_states[state[0].name] = (state[0].state, state[0].emergence, state[0].vaccinated)

    def getContextInformation(self, property, *args, **kwargs):
        super(Environment, self).getContextInformation(property)

        if(property == ENVProps.DECAY):
            current_time = args[0]
            if len(self.time_window.keys()) <=2:
                return 0

            _, first, second = sorted(self.time_window.keys(), reverse=True)[0:3]

            return self.time_window[first] - self.time_window[second] 

        if(property == ENVProps.AGENT_STATES):
            return self.agent_states


    def select(self, immChildren):
        """
        Choose a model to transition from all possible models.
        """
        # Doesn't really matter, as they don't influence each other
        return immChildren[0]

