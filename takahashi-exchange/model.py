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


# np.random.seed(0)
# TODO: Create a complete graph


def reverse_exponential(x):
    return np.random.exponential(1/float(x))

def threshold(t, theta, a, b):
    if t < theta:
        return a
    else:
        return b

class Parameters:
    TOPOLOGY_FILE = ""
    INIT_RESOURCES = 10

DEBUG = True

def enum(**kwargs):
    class Enum(object): pass
    obj = Enum()
    obj.__dict__.update(kwargs)
    return obj

ActionState = enum(P='PROPAGATING', N="NORMAL")

ENVProps = enum(DECAY='decay_rate', GIVERS_GREATER_THAN='Givers')

class AgentState(object):
    # TODO: Implement "clone" method.
    def __init__(self, name, id):
        self._name = name
        self.current_time = 0.0
        self.id = id 
        self.ta = 0

        self.resources = Parameters.INIT_RESOURCES
        TG_MAX = Parameters.INIT_RESOURCES
        self.gg = np.random.randint(0, TG_MAX + 1) 
        self.tg = np.random.uniform(low=0.1, high=2)
        # TODO Implement RV I cant find it.


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

    def __lt__(self, other):
        return self.name < other.name 

    def saveLoginfo(self): 
        pass
        # number_of_cultures = self.parent.getContextInformation(ENVProps.NUMBER_OF_CULTURES)
        # TODO: Change logger
        # stats = (self.current_time, number_of_cultures)
        # self.stats.append(stats) 

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

        self.y_up = None

    def add_connections(self, ag_id): 
        inport = self.addInPort(name=ag_id)
        self.in_ports_dict[ag_id] = inport
        outport = self.addOutPort(name=ag_id)
        self.out_ports_dict[ag_id] = outport
        return inport, outport

    def get_neighbor(self):
        suitable_neighbors = self.parent.getContextInformation(\
                ENVProps.GIVERS_GREATER_THAN,
                bigger_than = self.state.tg * self.state.gg)

        neighbor_to_give = np.random.choice(suitable_neighbors)
        return self.out_ports_dict[neighbor_to_give]

    def extTransition(self, inputs): 
        # TODO: Here it receives the new resources
        # TODO: Check how are the inputs formed
        self.state.resources += inputs
        self.state.current_time += self.elapsed
        self.y_up = {'received': inputs}
        return self.state

    def intTransition(self):
        self.state.current_time += self.state.ta 
        if self.state.giving:
            # If I give I remove the ones I gave.
            self.state.giving = False
            self.state.credits -= self.state.tg
            self.y_up = {'given': self.state.tg}
        return self.state

    def __lt__(self, other):
        return self.name < other.name 

    def outputFnc(self):
        # Here I select the neighbor to send resources:
        # Which of my neighbors has given more than TG * GG
        # credits in the previous gen (if greater than zero)?
        # Pick randomly from this subset.

        ret = {}
        output_port = self.get_neighbor()

        if output_port:
            self.state.giving = True
            ret[output_port] = self.state.gg
        return ret

    def timeAdvance(self):
        self.state.ta = 1
        return self.state.ta

    def modelTransition(self, state):
        return True 

class Environment(CoupledDEVS):
    # TODO: Enable dynamic nature
    # TODO: Create new agents
    def __init__(self, name=None):
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

        # The credits given by each agent in the last generation.
        # Defaults to the max for the start of the simulation.
        self.given_credits = {ag.state.id: Parameters.INIT_RESOURCES \
                for ag in self.agents.values()}

    def modelTransition(self, state): 
        # Create the new generations, destroy the old one
        pass

    def globalTransition(self, e_g, x_b_micro, *args, **kwargs):
        super(Environment, self).globalTransition(e_g, x_b_micro, *args, **kwargs)
        given = x_b_micro.get('given', None)
        received = x_b_micro.get('received', None)

        if given is not None:
            self.given_credits.append(given)
        if received is not None:
            self.received_credits.append(received)
        self.given_credits.update(x_b_micro)

    def getContextInformation(self, property, *args, **kwargs):
        super(Environment, self).getContextInformation(property)
        if property == ENVProps.GIVERS_GREATER_THAN:
            bigger_than = kwargs['bigger_than']
            givers = dict(filter(lambda elem: \
                elem[1] >= bigger_than,
                self.given_credits.items()))
            return givers.keys()

        # a. The mean +/- sd of the given credits
        # b. something else I'm forgetting

        # if(property == ENVProps.NUMBER_OF_CULTURES):
        #     unique_cultures = []
        #     if self.cultures:
        #         unique_cultures = np.unique(np.array(list(self.cultures.values())), axis=0) 
        #     return len(unique_cultures)


    def select(self, immChildren):
        """
        Choose a model to transition from all possible models.
        """
        # Doesn't really matter, as they don't influence each other
        return immChildren[0]

