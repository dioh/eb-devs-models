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
# import stats
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

ENVProps = enum(DECAY='decay_rate', NUMBER_OF_CULTURES='agent_states', INFECT_RATE= 'infect_rate')

class AgentState(object):
    def __init__(self, name, id, current_time = 0):
        """TODO: to be defined1. """
        self._name = name
        self.current_time = current_time
        self.id = int(id)
        self.ta = self.id 

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
        self.ta = 1
        self.state = "LogAgent"
        self.current_time = 0 
        self.elapsed = 0 
        self.my_input = {}

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
        self.state = AgentState(name=name, id=id, current_time=kwargs.get('current_time', 0.0))
        self.in_ports_dict = {}
        self.out_ports_dict = {}

        self.already_run = False

        self.y_up = (self.state.id, len(self.out_ports_dict.keys()))


    def add_connections(self, ag_id): 
        inport = self.addInPort(name=ag_id)
        self.in_ports_dict[ag_id] = inport
        outport = self.addOutPort(name=ag_id)
        self.out_ports_dict[ag_id] = outport
        return inport, outport

    def extTransition(self, inputs): 
        pass

    def intTransition(self):
        self.state.current_time += self.state.ta 
        self.y_up = (self.state.id, len(self.out_ports_dict.keys()))
        self.already_run = True
        return self.state

    def __lt__(self, other):
        return self.name < other.name 

    def outputFnc(self):
        ret = {}
        return ret

    def timeAdvance(self):
        self.state.ta = self.state.id
        if self.already_run:
            self.state.ta = INFINITY
        return self.state.ta

    def modelTransition(self, state):
        state['current_time'] = self.state.current_time
        return True 

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


        # This agent reads the environment state for logging purposes
        log_agent = LogAgent()
        log_agent.OPorts = []
        log_agent.IPorts = []
        self.addSubModel(log_agent)
        self.agents[-1] = log_agent
        log_agent.saveLoginfo()

        self.points = None
        self.model = None
        self.updatecount = 0
        self.nodes_degrees = {}

    def create_topology(self):
        # Read the topology file
        self.G = nx.read_adjlist(Parameters.TOPOLOGY_FILE)
        self.agents = {}
        # For each node, create an atomic object model of class Agent
        for i, node in self.G.nodes(data=True): 
            ag_id = int(i)
            node['start'] = 0.0
            agent = Agent(name="agent %s" % i, id=ag_id, kwargs=node) 
            self.agents[ag_id] = self.addSubModel(agent)


        # For each edge in the graph, connect the respective atomic models
        for i in self.G.edges():
            # Avoid self-loops
            if i[0] != i[1]:
                # Connect input output ports between agents.
                ind0 = int(i[0])
                ind1 = int(i[1])
                a0 = self.agents[ind0]
                a1 = self.agents[ind1]
                
                i0, o0 = a0.add_connections(ind1)
                i1, o1 = a1.add_connections(ind0)

                self.connectPorts(o0, i1)
                self.connectPorts(o1, i0)

        self.G = nx.relabel.convert_node_labels_to_integers(self.G)



    def globalTransition(self, e_g, x_b_micro, *args, **kwargs):
        super(Environment, self).globalTransition(e_g, x_b_micro, *args, **kwargs)
        self.nodes_degrees.update(x_b_micro)

    def getContextInformation(self, property, *args, **kwargs):
        super(Environment, self).getContextInformation(property)


    def select(self, immChildren):
        """
        Choose a model to transition from all possible models.
        """
        # Doesn't really matter, as they don't influence each other
        return immChildren[0]

    def modelTransition(self, state): 
        # Sort a random value from the weighted list of nodes
        grados = self.nodes_degrees.values()
        xk = np.array(grados)
        pk = xk / float(sum(xk))

        selected_agent_id = np.random.choice(self.nodes_degrees.keys(), 1, p=pk)[0]

        # Create a new node
        current_time = state['current_time']
        # There is a logging agent that we need to leave out from the list of ids.
        new_ag_id = len(self.agents) - 1

        new_agent = Agent(name="agent %s" % new_ag_id, id=new_ag_id,
                kwargs={'current_time':current_time}) 
        self.agents[new_ag_id] = self.addSubModel(new_agent)

        # p_connect_density = stats.rv_discrete(name='custm', values=(self.nodes_degrees.keys(), pk))

        # selected_agent2 = p_connect_density.rvs()

        # Connect ports from/to that node
        i0, o0 = new_agent.add_connections(selected_agent_id)
        i1, o1 = self.agents[selected_agent_id].add_connections(new_ag_id)

        self.connectPorts(o0, i1)
        self.connectPorts(o1, i0)

        # Update the nodes degrees list
        self.nodes_degrees[selected_agent_id] = self.nodes_degrees.get(selected_agent_id, 0) + 1
        self.nodes_degrees[new_ag_id] = self.nodes_degrees.get(selected_agent_id, 0) + 1

        # Update G
        self.G.add_node(int(new_ag_id))
        self.G.add_edge(int(new_ag_id), int(selected_agent_id), timestamp=current_time)
        self.G.nodes[int(new_ag_id)]['start'] = current_time

        return False 

