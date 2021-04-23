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
np.random.seed(0)

class Parameters:
    TOPOLOGY_FILE = 'grafos_ejemplo/grafo_vacio'
    EMERGENT_MODEL = False
    INITIAL_PROB = 0
    BETA_PROB = 3
    RHO_PROB = 3 #Gamma
    TW_SIZE = 8
    TW_TRHD = 50
    TW_BIN_SIZE = 15
    p=0.4
    K=0

    QUARANTINE_THRESHOLD = 0.05
    QUARANTINE_ACCEPTATION = 0.03

DEBUG = True


def enum(**kwargs):
    class Enum(object): pass
    obj = Enum()
    obj.__dict__.update(kwargs)
    return obj

SIRStates = enum(S='Susceptible', I='Infected',  R='Recovered')
ENVProps = enum(DECAY='decay_rate', AGENT_STATES='log data', QUARANTINE_CONDITION='If above threshold, agents do quarantine.')

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
        self.ta = 0.05

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
        self.free_deg = np.random.poisson(5) if id!=0 else 0
        self.deg = np.random.poisson(5) 
        self.model = model

        self.neighbors_state = {}
        self.share = True
        self.model_transition = False

        self.ta = INFINITY

    def set_infection_values(self): 
        prob = 0
        neighbors_states = self.neighbors_state.values()
        if len(neighbors_states) >  0 and sum(np.array(neighbors_states) == SIRStates.S) > 0:
            prob = (float(Parameters.RHO_PROB) / (self.deg * Parameters.BETA_PROB+Parameters.RHO_PROB))
            self.to_recover = np.random.random() < prob
            self.ta = np.random.exponential(float(1)/(self.deg * Parameters.BETA_PROB+Parameters.RHO_PROB))
        else:
            self.to_recover = True
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
        self.state.share = False

        for k, v in inputs.items(): 
            if v == 'infect':
                # If an agent is being infected.
                if self.state.state == SIRStates.S\
                        and (
                                (self.parent.getContextInformation(ENVProps.QUARANTINE_CONDITION)\
                                        and np.random.random() < 1- Parameters.QUARANTINE_ACCEPTATION) 
                                or 
                                    not self.parent.getContextInformation(ENVProps.QUARANTINE_CONDITION)):
                    self.state.state = SIRStates.I
                    self.state.model_transition = True
                    self.state.share = True
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
            else:
                self.state.neighbors_state[v[0]] = v[1]
                # self.state.ta -= self.elapsed
        return self.state

    def intTransition(self):
        """
        Internal Transition Function.
        """
        self.state.current_time += self.timeAdvance()
        # Emergent behavior is turned off during internal transitions
        self.state.emergence = 0
        self.state.share = False

        # If the coin toss resulted in recovery
        if self.state.to_recover:
            self.state.state = SIRStates.R
            self.state.to_recover = False
            self.state.share = True
        elif self.state.state == SIRStates.I:
            pass
        else:
            self.state.ta = INFINITY
        self.y_up = self.state

        return self.state

    def __lt__(self, other):
        try:
            if other.state is None:
                other_name = other.name
            else:
                other_name = other.state.name
            return self.state.name < other_name
        except:
            __import__('ipdb').set_trace()

    def __hash__(self):
        return hash(self.state.name)

    def outputFnc(self):
        ret = {}
        if self.state.share:
            for outport in self.OPorts:
                ret[outport] = (self.state.id, self.state.state)
            return ret
        if self.state.state == SIRStates.I and self.state.to_recover == False:
            if not self.OPorts:
                return {}
            susceptible_ids = [model for model, state in self.state.neighbors_state.items() if state == SIRStates.S]
            if not susceptible_ids:
                return {}
            outmodel_id = np.random.choice(susceptible_ids)
            outport_name = str('from%d-to-%d' % (self.state.id, outmodel_id))
            outport = [outport for outport in self.OPorts if outport.name == outport_name]
            if outport:
                ret = {outport[0]: "infect"}
            else:
                __import__('ipdb').set_trace()
            return ret

        return {}

    def add_connections(self, ag_id): 
        inport = self.addInPort(name=ag_id)
        self.in_ports_dict[ag_id] = inport
        outport = self.addOutPort(name="from%d-to-%d" % (self.state.id, ag_id))
        self.out_ports_dict[ag_id] = outport
        self.state.free_deg -= 1
        self.state.neighbors +=1
        return inport, outport

    def timeAdvance(self):
        """
        Time-Advance Function.
        """

        if self.state.share:
            self.state.ta = 0
        elif self.state.state == SIRStates.I:
            self.state.set_infection_values()
        elif self.state.state in (SIRStates.R, SIRStates.S):
            self.state.ta = INFINITY

        # Compute 'ta', the time to the next scheduled internal transition,
        # based (typically) on current State.
        return self.state.ta

    def modelTransition(self, state):
        pass


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

            a1.state.neighbors_state[a2.state.id] = a2.state.state
            a2.state.neighbors_state[a1.state.id] = a1.state.state
        
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

        for ag_state in x_b_micro:
            if ag_state.state == SIRStates.I and not ag_state.to_recover:
                self.globalModelTransition(ag_state)

    def modelTransition(self, state):
        pass

    def getContextInformation(self, property, *args, **kwargs):
        super(Environment, self).getContextInformation(property)
        if(property == ENVProps.AGENT_STATES):
            return self.agent_states

        if(property == ENVProps.QUARANTINE_CONDITION):
            (unique, counts) = np.unique(np.array([it[0] for it in self.agent_states.values()]), return_counts=True) 
            unique_counts_dict = dict(zip(unique, counts))
            infected_number = unique_counts_dict['Infected']

            infected_percentage = infected_number / float(len(self.agents))
            return Parameters.QUARANTINE_THRESHOLD < infected_percentage
            
            

    def select(self, immChildren):
        """
        Choose a model to transition from all possible models.
        """
        # Doesn't really matter, as they don't influence each other
        return immChildren[0]

    def globalModelTransition(self, model_state): 
        # Sort a random value from the weighted list of nodes
        newly_inf = model_state
        current_time=newly_inf.current_time
        newly_inf_id=newly_inf.id        
        newly_inf_deg = newly_inf.free_deg
        self.nodes_free_deg[newly_inf.id] = 0
        grados = list(self.nodes_free_deg.values())

        xk = np.array(grados)
        xk[newly_inf_id]=0
        
        if sum(xk) == 0:
            return False
        
        pk = xk / float(sum(xk))
        #esto es para el evento SS

        deg=max(0, 1 + Parameters.K*np.random.binomial(1,Parameters.p))
        
        if deg > sum(pk>0):
            return False
        
        selected_agents = np.random.choice(max(0,list(self.nodes_free_deg.keys())), int(deg), p=pk,replace=False)

        
        neighbor_states = {}

        # Connect ports from/to that node
        for i in selected_agents:
            i0, o0 = self.agents[newly_inf_id].add_connections(i)
            i1, o1 = self.agents[i].add_connections(newly_inf_id)

            self.connectPorts(o0, i1)
            self.connectPorts(o1, i0)

            # Update the nodes free degrees list
            self.nodes_free_deg[i] = self.nodes_free_deg[i]-1
            self.G.add_edge(int(newly_inf_id), int(i), timestamp=current_time)
            neighbor_states[i] = self.agents[i].state.state
            self.agents[i].state.neighbors_state[newly_inf_id] = self.agents[newly_inf_id].state.state

        self.agents[newly_inf_id].state.neighbors_state = neighbor_states
        self.agents[newly_inf_id].state.free_deg = 0
        return False
