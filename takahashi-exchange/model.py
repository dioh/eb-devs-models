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
import copy

np.random.seed(0)
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
    EMERGENT_MODEL = False

DEBUG = True

def enum(**kwargs):
    class Enum(object): pass
    obj = Enum()
    obj.__dict__.update(kwargs)
    return obj

ActionState = enum(P='PROPAGATING', N="NORMAL")

ENVProps = enum(DECAY='decay_rate',
        GIVERS_GREATER_THAN='Givers',
        GIVERS_MEAN='Givers Mean values',
        GIVERS_SD='Givers SD values',
        TOTAL_CRED_MEAN='Total credits mean',
        TOTAL_CRED_SD='Total credits sd')

class AgentState(object):
    # TODO: Implement "clone" method.
    # FIXME: should I accumulate the credits I got? 
    def __init__(self, name, id):
        self.name = name
        self.current_time = 0.0
        self.id = id 
        self.ta = 0

        self.giving = False

        self.credits = Parameters.INIT_RESOURCES
        TG_MAX = Parameters.INIT_RESOURCES
        self.gg = np.random.randint(0, TG_MAX + 1) 
        self.tg = np.random.uniform(low=0.1, high=2)

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
        return "Agent: %s, credits: %s" % (str(self.name), str(self.credits))

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
        givers_mean = self.parent.getContextInformation(ENVProps.GIVERS_MEAN)
        stats = (self.current_time, givers_mean)
        self.stats.append(stats) 

    def intTransition(self):
        self.current_time += self.ta
        self.saveLoginfo()

    def timeAdvance(self):
        return self.ta

    def set_values(self):
        self.ta = 0.99 #0.1

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

    def new_instance(self, new_id):
        new_agent_state = copy.deepcopy(self.state)
        agent = Agent(name="agent %s" % new_id, id=new_id) 
        agent.state = new_agent_state
        agent.state.id = new_id
        agent.state.name = "agent %s" % new_id
        return agent

    def reset_state(self):
        self.state.credits = Parameters.INIT_RESOURCES
        # TODO: Include mutation.

    def add_connections(self, ag_id): 
        inport = self.addInPort(name=ag_id)
        self.in_ports_dict[ag_id] = inport
        outport = self.addOutPort(name=ag_id)
        self.out_ports_dict[ag_id] = outport
        return inport, outport

    def get_neighbor(self):
        suitable_neighbors = list(self.parent.getContextInformation(\
                ENVProps.GIVERS_GREATER_THAN,
                bigger_than = self.state.tg * self.state.gg,\
                        avoid_self = self.state.id))

        if suitable_neighbors:
            neighbor_to_give = np.random.choice(suitable_neighbors)
            outport = self.out_ports_dict.get(neighbor_to_give)
            return outport

    def extTransition(self, inputs): 
        credits = list(inputs.values())[0]
        self.state.credits += credits
        self.state.current_time += self.elapsed
        self.y_up = {'received_credits': (self.state.id, credits),
                'total_credits': (self.state.id, self.state.credits)}
        return self.state

    def intTransition(self):
        self.state.current_time += self.state.ta 
        if self.state.giving:
            # If I give I remove the ones I gave.
            self.state.giving = False
            self.state.credits -= self.state.gg
            self.y_up = {'given_credits': (self.state.id, self.state.gg),
                'total_credits': (self.state.id, self.state.credits)}

        return self.state

    def __lt__(self, other):
        return self.name < other.name 

    def outputFnc(self):
        # Here I select the neighbor to send credits:
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
    # TODO: Create new agents
    def __init__(self, name=None):
        # Always call parent class' constructor FIRST:
        CoupledDEVS.__init__(self, name)
        self.G = nx.Graph()

        # Children states initialization
        self.create_topology() 

        self.log_agent = LogAgent()
        self.log_agent.OPorts = []
        self.log_agent.IPorts = []
        self.addSubModel(self.log_agent)
        # self.agents[-1] = log_agent
        self.log_agent.saveLoginfo()

        self.given_credits = {v.state.id: Parameters.INIT_RESOURCES \
                for k, v in self.agents.items() if k != -1}
        self.received_credits = {}
        self.total_credits = {v.state.id: Parameters.INIT_RESOURCES \
                for k, v in self.agents.items() if k != -1}

        # The last agent's id
        self.last_agent_id = len(self.agents) - 1

        # This is used to run the structural changes only once.
        self.updatecount = 0

    def create_topology(self):
        G = nx.read_adjlist(Parameters.TOPOLOGY_FILE)
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
        self.updatecount = self.updatecount + 1
        if self.updatecount < len(self.agents) - 1: # - 1 due to the logging agent...
            return
        self.updatecount = 0

        g_mean = self.getContextInformation(ENVProps.GIVERS_MEAN)
        g_sd = self.getContextInformation(ENVProps.GIVERS_SD)

        to_duplicate = dict(filter(lambda elem: \
                elem[1] >= g_mean + 1 * (g_sd),
                self.total_credits.items()))

        to_eliminate = dict(filter(lambda elem: \
                elem[1] <= g_mean - 1 * (g_sd),
                self.total_credits.items()))

        to_replicate_once = dict(filter(lambda elem: \
                elem[1] > g_mean - 1 * (g_sd) and elem[1] < g_mean + 1 * (g_sd),
                self.total_credits.items()))


        # Remove the ones to eliminate
        for model_id in to_eliminate.keys():
            self.removeSubModel(self.agents[model_id])
            del self.agents[model_id]
            del self.total_credits[model_id]
            # del self.received_credits[model_id]
            del self.given_credits[model_id]

        # Replicate models.
        for model_id in to_replicate_once.keys():
            new_id = self.last_agent_id
            self.last_agent_id += 1
            agent = self.agents[model_id].new_instance(new_id)
            self.agents[new_id] = self.addSubModel(agent)
            
        # Duplicate models.
        for model_id in to_replicate_once.keys():
            new_id = self.last_agent_id
            self.last_agent_id += 1
            agent = self.agents[model_id].new_instance(new_id)
            self.agents[new_id] = self.addSubModel(agent)

            new_id = self.last_agent_id
            self.last_agent_id += 1
            agent = self.agents[model_id].new_instance(new_id)
            self.agents[new_id] = self.addSubModel(agent)

        # Update the resources for each agent
        for ag_id, ag in self.agents.items():
            ag.reset_state()
            self.total_credits[ag_id] = Parameters.INIT_RESOURCES
        self.given_credits = {}
        # __import__('ipdb').set_trace()

        # Connect!!

        return False

    def globalTransition(self, e_g, x_b_micro, *args, **kwargs):
        super(Environment, self).globalTransition(e_g, x_b_micro, *args, **kwargs)

        for elem in x_b_micro:
            for cred_type, (agent_id, credits) in elem.items():
                self.__dict__[cred_type][agent_id] = credits

    def getContextInformation(self, property, *args, **kwargs):
        super(Environment, self).getContextInformation(property)
        if property == ENVProps.GIVERS_GREATER_THAN:
            bigger_than = kwargs['bigger_than']
            avoid_self = kwargs['avoid_self']

            givers = dict(filter(lambda elem: \
                elem[1] >= bigger_than and elem[0] != avoid_self,
                self.given_credits.items()))
            return givers.keys()

        if property == ENVProps.GIVERS_MEAN:
            return np.array(list(self.given_credits.values())).mean()

        if property == ENVProps.GIVERS_SD:
            return np.array(list(self.given_credits.values())).std()

        if property == ENVProps.TOTAL_CRED_MEAN:
            # if len(list(self.total_credits.values())) == 0:
            #     __import__('ipdb').set_trace()
            return np.array(list(self.total_credits.values())).mean()

        if property == ENVProps.TOTAL_CRED_SD:
            return np.array(list(self.total_credits.values())).std()

    def select(self, immChildren):
        """
        Choose a model to transition from all possible models.
        """
        # Doesn't really matter, as they don't influence each other
        return immChildren[0]

