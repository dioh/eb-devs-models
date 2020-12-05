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

#np.random.seed(0) # con este anda bien
#np.random.seed(1) # con este rompe

class Parameters:
    TOPOLOGY_FILE = 'grafos_ejemplo/grafo_vacio'
    EMERGENT_MODEL = False
    INITIAL_PROB = 0
    BETA_PROB = 3
    RHO_PROB = 1
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
ENVProps = enum(DECAY='decay_rate', AGENT_STATES='log data')

class LogAgent(AtomicDEVS):
    def __init__(self):
        self.set_values()
        self.state = 'pepe'
        self.stats = []
        self.name='logAgent'
        self.current_time = 0 
        self.elapsed = 0 
        self.my_input = {}

    def saveLoginfo(self): 
        parent_items = self.parent.getContextInformation(ENVProps.AGENT_STATES).items()
        (unique, counts) = np.unique(np.array([it[1][0] for it in parent_items]), return_counts=True) 
        frequencies = dict(zip(unique, counts))
        log_data = [frequencies.get(key, 0) for key in SIRStates.__dict__.values()]
        log_data.insert(0, self.current_time) 
        self.stats.append(log_data)

    def intTransition(self):
        self.current_time += self.ta
        self.saveLoginfo()

    def timeAdvance(self):
        return self.ta

    def set_values(self):
        self.ta = 0.001

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
        self.neighbors = 0
        self.free_deg = np.random.poisson(8) if id!=0 else 0
        self.model = model

        #if self.state == SIRStates.I:
        #    self.set_infection_values()
        #else:
        #if self.state == SIRStates.S:
        self.ta = INFINITY

    def set_infection_values(self): 
        #todo: aca falta filtrar por vecinos susceptibles para tirar la moneda
        prob = 0
        if self.neighbors>0:
            #self.neighbors = len(self.model.out_ports_dict)
            prob = (float(Parameters.RHO_PROB) / (self.neighbors*Parameters.BETA_PROB+Parameters.RHO_PROB))
            self.to_recover = np.random.random() < prob
        # self.to_recover = np.random.random() >= Parameters.RHO_PROB
        #if self.neighbors < 0:
        #    import pdb;pdb.set_trace()
            self.ta = np.random.exponential(float(1)/(self.neighbors*Parameters.BETA_PROB+Parameters.RHO_PROB))
        else:
            self.ta=np.random.exponential(float(1)/Parameters.RHO_PROB)
            
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
            #self.state.set_infection_values()
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

    # def __eq__(self, other):
    #     return self.state.name == other.state.name

    # def __ne__(self, other):
    #     return not self.state.name == other.state.name

    def __lt__(self, other):
        if other.state is None:
            other_name = other.name
        else:
            other_name =other.state.name
        return self.state.name < other_name

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
        self.state.neighbors +=1
        return inport, outport

    def modelTransition(self, state):
        state["newly_infected"] = self.state
        return self.state.state == SIRStates.I

    def timeAdvance(self):
        """
        Time-Advance Function.
        """

        if self.state.state == SIRStates.I:
            self.state.set_infection_values()
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

        # Children states initialization
        self.nodes_free_deg = {}
        self.create_topology()
        self.G = nx.Graph()
        self.time_window = {}
        self.agent_states = {}
        # Load the agent states dict:
        for ag in self.agents:
            self.agent_states[ag.state.name] = (ag.state.state , ag.state.emergence)

        self.stats = []

        self.log_agent = LogAgent()
        self.log_agent.OPorts = []
        self.log_agent.IPorts = []
        self.addSubModel(self.log_agent)
        self.log_agent.saveLoginfo()


    def create_topology(self):
        G = nx.read_adjlist(Parameters.TOPOLOGY_FILE)
        self.agents = [Agent(name="agent %d" % i, id=i) for i in range(G.number_of_nodes())]
        #un agente infectado conectado con algunos vecinos S
        self.G = nx.read_adjlist(Parameters.TOPOLOGY_FILE)

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
        
        self.nodes_free_deg[0]=0
        
        for agent in self.agents:
            self.nodes_free_deg[agent.state.id]=agent.state.free_deg
            agent.state.neighbors = len(agent.OPorts)
            #if agent.state.state == SIRStates.I:
            #    agent.state.set_infection_values()
        
        
        
        self.G = nx.relabel.convert_node_labels_to_integers(self.G)
        self.agents[0].state.state=SIRStates.I
        self.agents[0].state.set_infection_values()      

    def globalTransition(self, e_g, x_b_micro, *args, **kwargs):
        super(Environment, self).globalTransition(e_g, x_b_micro, *args, **kwargs)
        for state in x_b_micro: 
            #self.nodes_free_deg[state.id] = state.free_deg
            self.agent_states[state.name] = (state.state, state.emergence)

    def getContextInformation(self, property, *args, **kwargs):
        super(Environment, self).getContextInformation(property)
        if(property == ENVProps.AGENT_STATES):
            return self.agent_states

    def select(self, immChildren):
        """
        Choose a model to transition from all possible models.
        """
        # Doesn't really matter, as they don't influence each other
        return immChildren[0]

    def modelTransition(self, state): 
        # Sort a random value from the weighted list of nodes
        newly_inf=state["newly_infected"]
        current_time=newly_inf.current_time
        newly_inf_id=newly_inf.id        
        newly_inf_deg = newly_inf.free_deg
        self.nodes_free_deg[newly_inf.id] = 0
        #import pdb;pdb.set_trace()        
        #self.agents[newly_inf_id].state.free_deg = 0 
        grados = list(self.nodes_free_deg.values())
        # if any(np.array(self.nodes_free_deg.values()) < 0):
        #     __import__('ipdb').set_trace()
        #todo Avisar a los agentes los cambios en sus valores de vecinos
        

        xk = np.array(grados)
        xk[newly_inf_id]=0
        
        if sum(xk) == 0:
            return False
        
        
        pk = xk / float(sum(xk))
        #esto es para el evento SS
        p=0
        K=0

        deg=max(0,newly_inf_deg+K*np.random.binomial(1,p))
        
        if deg > sum(pk>0):
            return False
        
        if any(pk < 0):
            import pdb;pdb.set_trace()
        
        selected_agents = np.random.choice(max(0,list(self.nodes_free_deg.keys())), deg, p=pk,replace=False)
        if any([ self.agents[ag].state.free_deg <= 0 for ag in selected_agents]):
            __import__('ipdb').set_trace()

        

        # Connect ports from/to that node
        for i in selected_agents:
            i0, o0 = self.agents[newly_inf_id].add_connections(i)
            i1, o1 = self.agents[i].add_connections(newly_inf_id)

        #i0, o0 = new_agent.add_connections(selected_agent_id)
        #i1, o1 = self.agents[selected_agent_id].add_connections(new_ag_id)

            self.connectPorts(o0, i1)
            self.connectPorts(o1, i0)

            # Update the nodes free degrees list
            self.nodes_free_deg[i] = self.nodes_free_deg[i]-1
            self.G.add_edge(int(newly_inf_id), int(i), timestamp=current_time)
        
        #self.agents[newly_inf_id].state.set_infection_values()
        self.agents[newly_inf_id].state.free_deg = 0
        return False


