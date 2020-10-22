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
from sklearn.neighbors import NearestNeighbors
import networkx as nx
from pypdevs.infinity import INFINITY

# Import code for DEVS model representation:
from pypdevs.DEVS import *

from pypdevs.infinity import INFINITY
from functools import total_ordering

# np.random.seed(0)

class Parameters:
    TOPOLOGY_FILE = "grafo_muy_grande"
    EMERGENT_MODEL = False
    INITIAL_PROB = 0
    BETA_PROB = 10
    RHO_PROB = 0.9
    TW_SIZE = 5
    TW_TRHD = 50
    TW_BIN_SIZE = 15

DEBUG = True


def enum(**kwargs):
    class Enum(object): pass
    obj = Enum()
    obj.__dict__.update(kwargs)
    return obj

SIRStates = enum(S='Susceptible', I='Infected',  R='Recovered')
ENVProps = enum(DECAY='decay_rate')

class AgentState(object):
    def __init__(self, model, name, id, state):
        """TODO: to be defined1. """
        self._name = name
        self.current_time = 0.0

        self.id = id
        self._state = state
        self.vaccinated = False
        self._to_recover = False
        self._emergence = False
        self.neighbors = -1
        self.free_deg = np.random.poisson(8)
        self.model = model

        if self.state == SIRStates.I:
            self.set_infection_values()
        else:
            self.ta = INFINITY

    def set_infection_values(self): 
    #todo: aca falta filtrar por vecinos susceptibles para tirar la moneda
        prob = 0
        if self.model.OPorts:
            self.neighbors = len(self.model.OPorts)
            prob = (1.0 / (self.neighbors + 1))
        self.to_recover = np.random.random() < prob
        # self.to_recover = np.random.random() >= Parameters.RHO_PROB
        self.ta = np.random.exponential(Parameters.BETA_PROB)

    @property
    def name(self):
        """I'm the 'heading' property."""
        return self._name

    @property
    def state(self):
        """I'm the 'heading' property."""
        return self._state

    @property
    def to_recover(self):
        """I'm the 'heading' property."""
        return self._to_recover

    @to_recover.setter
    def to_recover(self, to_recover):
        self._to_recover = to_recover

    @property
    def emergence(self):
        """I'm the 'heading' property."""
        return self._emergence

    @emergence.setter
    def emergence(self, emergence):
        self._emergence = emergence

    @state.setter
    def state(self, state):
        self._state = state

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
        return "Agent: %s, State: %s" % (str(self.name), str(self.state))


@total_ordering
class Agent(AtomicDEVS):
    """
    A SIR Agent
    """

    def __init__(self, name=None, id=None):
        """
        Constructor (parameterizable).
        """
        # Always call parent class' constructor FIRST:
        AtomicDEVS.__init__(self, name)

        self.in_event = self.addInPort("in_event")
        self.in_ports_dict ={}
        self.out_ports_dict= {}
        # The initial state of the agent.
        state = SIRStates.I if id==0 else SIRStates.S
        self.state = AgentState(self, self.name, id, state)

    def extTransition(self, inputs):
        """
        External Transition Function.
        """
        self.state.current_time += self.elapsed

        # Is it an outreach happening?

        # If an agent is being infected.
        if self.state.state == SIRStates.S :
            self.state.set_infection_values()
            self.state.state = SIRStates.I
        # If it is recovered
        elif self.state.state == SIRStates.R:
            self.state.emergence = 0
            self.state.ta = INFINITY
        # If it is vaccinated
        elif self.state.state == SIRStates.S and (self.state.emergence and Parameters.EMERGENT_MODEL):
            self.state.vaccinated = True
            self.state.ta = INFINITY
        # Any other case
        else:
            self.state.ta -= self.elapsed
        self.y_up = self.state
        return self.state

    def intTransition(self):
        """
        Internal Transition Function.
        """
        self.state.current_time += self.timeAdvance()
        # Emergent behavior is turned off during internal transitions
        self.state.emergence = 0

        # If the coin toss resulted in recovery
        if self.state.to_recover:
            self.state.state = SIRStates.R
            self.state.ta = INFINITY
        else:
            self.state.set_infection_values()
        self.y_up = self.state

        return self.state

    def __lt__(self, other):
        return self.name < other.name

    def __eq__(self, other):
        return self.state.name == other.state.name

    def __ne__(self, other):
        return not self.state.name == other.state.name

    def __lt__(self, other):
        return self.state.name < other.state.name

    def __hash__(self):
        return hash(self.state.name)

    def outputFnc(self):
        if(self.state.to_recover == False):
            if not self.OPorts:
                return {}
            try:
                outport = np.random.choice(self.OPorts)
                return {outport: "infect"}
            except Exception as e:
                print(e)
                print(self.state)
            # Randomly select a neighbor and send an infect message
        return {}

    def add_connections(self, ag_id): 
        inport = self.addInPort(name=ag_id)
        self.in_ports_dict[ag_id] = inport
        outport = self.addOutPort(name=ag_id)
        self.out_ports_dict[ag_id] = outport
        self.state.free_deg -= 1
        return inport, outport

    def modelTransition(self, state):
        state["newly_infected"] = self.state
        return self.state.state == SIRStates.I

    def timeAdvance(self):
        """
        Time-Advance Function.
        """

        # if self.state.state == SIRStates.I
        # Compute 'ta', the time to the next scheduled internal transition,
        # based (typically) on current State.
        return self.state.ta


class Environment(CoupledDEVS):
    def __init__(self, name=None):
        """
        A simple flocking system consisting
        """
        # Always call parent class' constructor FIRST:
        CoupledDEVS.__init__(self, name)

        # Declare the coupled model's output ports:
        # Autonomous, so no output ports

        # Declare the coupled model's sub-models:


        # Children states initialization
        self.nodes_free_deg = {}
        self.create_topology()
        
        self.time_window = {}
        self.agent_states = {}
        # Load the agent states dict:
        for ag in self.agents:
            self.agent_states[ag.state.name] = (ag.state.state , ag.state.emergence, ag.state.vaccinated)

        self.stats = []

        s = i = r = e = 0
        for _, v in self.agent_states.items():
            s += v[0] == SIRStates.S
            i += v[0] == SIRStates.I
            r += v[0] == SIRStates.R
        # e = self.parent.getContextInformation(ENVProps.DECAY, 0) > Parameters.TW_TRHD
        e = False
        vc = 0
        self.stats.append((0, s, i, r, e, vc)) 


        self.points = None
        self.model = None
        self.updatecount = 0

    def create_topology(self):
        G = nx.read_adjlist(Parameters.TOPOLOGY_FILE)
        self.agents = [Agent(name="agent %d" % i, id=i)  for i in range(G.number_of_nodes())]
        #un agente infectado conectado con algunos vecinos S

        for agent in self.agents:
            self.addSubModel(agent)

        for i in G.edges():
            if i[0] == i[1]: continue
            ind0 = int(i[0])
            ind1 = int(i[1])
            a1 = self.agents[ind0]
            a2 = self.agents[ind1]
            out1 = a1.addOutPort("from%d-to-%d" % (ind0, ind1))
            out2 = a2.addOutPort("from%d-to-%d" % (ind1, ind0))

            self.connectPorts(out1, a2.in_event)
            self.connectPorts(out2, a1.in_event)

        for agent in self.agents:
            self.nodes_free_deg[agent]=agent.state.free_deg
        
        self.nodes_free_deg[0]=0
        #self.agents[0].state.state=SIRStates.I
        #set_infection_values(self.agents[0])      

    def globalTransition(self, e_g, x_b_micro, *args, **kwargs):
        super(Environment, self).globalTransition(e_g, x_b_micro, *args, **kwargs)
        for state in x_b_micro: 
            self.nodes_free_deg[state.id] = state.free_deg
            self.agent_states[state.name] = (state.state, state.emergence)
            s = i = r = e = 0
            for _, v in self.agent_states.items():
                s += v[0] == SIRStates.S
                i += v[0] == SIRStates.I
                r += v[0] == SIRStates.R
                e += v[1]
        self.stats.append((e_g, s, i, r, e)) 


    def select(self, immChildren):
        """
        Choose a model to transition from all possible models.
        """
        # Doesn't really matter, as they don't influence each other
        return immChildren[0]

    def modelTransition(self, state): 
        # Sort a random value from the weighted list of nodes
        newly_inf=state["newly_infected"]
        newly_inf_id=newly_inf.id

        newly_inf_deg = self.nodes_free_deg[newly_inf_id]
        grados = list(self.nodes_free_deg.values())

        xk = np.array(grados)
        try:
            xk[newly_inf_id]=0
        except:
            __import__('ipdb').set_trace()

        pk = xk / float(sum(xk))
        
        #esto es para el evento SS
        p=0
        K=0

        deg=newly_inf_deg+K*np.random.binomial(1,p)
        
        selected_agents = np.random.choice(list(self.nodes_free_deg.keys()), deg, p=pk)

        print(np.isin(self.agents[newly_inf_id],selected_agents))
        print(selected_agents)

        # Connect ports from/to that node
        for i in selected_agents:
            i0, o0 = self.agents[newly_inf_id].add_connections(i.state.id)
            i1, o1 = i.add_connections(newly_inf_id)

        #i0, o0 = new_agent.add_connections(selected_agent_id)
        #i1, o1 = self.agents[selected_agent_id].add_connections(new_ag_id)

            self.connectPorts(o0, i1)
            self.connectPorts(o1, i0)

            # Update the nodes free degrees list
            self.nodes_free_deg[i.state.id] = self.nodes_free_deg.get(i.state.id, 0) - 1
            self.nodes_free_deg[newly_inf_id] = 0

        return False


