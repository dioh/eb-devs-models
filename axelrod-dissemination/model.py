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
    EMERGENT_MODEL = False
    INITIAL_PROB = 0.05
    RHO_PROB = 4.0
    TW_SIZE = 5.0
    TW_TRHD = 5.0
    TW_BIN_SIZE = 15.0
    # THETA = None

    # A = 10.0
    # B = 20.0
    # NU = None # max vaccination rate

    # From SIR V model
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

SIRStates = enum(S='Susceptible',
        E='Exposed',
        I='Infected',
        R='Recovered',
        Q='Quarentained',
        D='Deceased')

ENVProps = enum(DECAY='decay_rate', AGENT_STATES='agent_states', INFECT_RATE= 'infect_rate')

class AgentState(object):
    def __init__(self, model, name, id, state, kwargs):
        """TODO: to be defined1. """
        self._name = name
        self.current_time = 0.0
        self.infected = 0
        self.infected_time = -1
        self.infected_end_time = -1
        self.infected_by = -1

        self.id = id
        self._state = state
        self.vaccinated = False
        self._to_recover = False
        self._emergence = False
        self._to_vaccine = False
        self.neighbors = -1
        self.model = model
        self.cost = 0
        self.kwargs = kwargs

        self.ta = reverse_exponential(1)

        if model.state:
            self.current_time = model.state.current_time 
            self.infected = model.state.infected 
            self.infected_time = model.state.infected_time 
            self.infected_end_time = model.state.infected_end_time
            self.infected_by = model.state.infected_by 
            self.kwargs = model.state.kwargs

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


    def intTransition(self):
        return self

    def extTransition(self, inputs = None):
        return self

    def outputFnc(self):
        return {}


class Susceptible(AgentState):
    def intTransition(self):
        super(Susceptible, self).intTransition() 
        # TODO: Change vaccination clock
        wake_up = reverse_exponential(0.1)
        to_vaccinate = False #have_been_vacc < wake_up
        new_state = self

        if to_vaccinate:
            new_state = Quarentained(self.model, self.name, self.id, SIRStates.Q)

        new_state.set_values()
        return new_state

    def extTransition(self, inputs=None):
        # self.current_time += self.ta
        infected_id = int(inputs.values()[0].split('_')[-1]) 
        new_state = Exposed(self.model, self.name, self.id, infected_id, SIRStates.E, kwargs=None)
        new_state.set_values()
        return new_state

    def set_values(self):
        self.ta = INFINITY #reverse_exponential(0.01)
        self.cost += Parameters.CV/Parameters.NU * self.ta

class Quarentained(AgentState):
    def set_values(self):
        self.cost += Parameters.CV
        self.ta = INFINITY

class Exposed(AgentState):
    def __init__(self, model, name, id, infectious, state, kwargs=None): 
        super(Exposed, self).__init__(model, name, id, state,kwargs=None)
        self.infected_by = infectious 
    
    def intTransition(self):
        super(Exposed, self).intTransition()
        return_state = Infected(self.model, self.name, self.id, SIRStates.I, kwargs=None)
        return_state.set_values()
        return return_state

    def set_values(self):
        # TODO: Maybe should infect aswell
        # With a probability some of the agents will spread the disease
        self.ta = reverse_exponential(Parameters.ALPHA_RATE) 

class Infected(AgentState):
    def __init__(self, model, name, id, state, kwargs):
        super(Infected, self).__init__(model, name, id, state, kwargs)
        self.to_death = np.random.random() < (1 -  Parameters.RECOVERY_PROB)
        self.to_recover = not self.to_death
        self.to_infect = None
        self.infected_time = self.current_time

    def intTransition(self):
        super(Infected, self).intTransition()

        new_state = None
        if self.to_infect:
            new_state = self 
        
        elif self.to_death:
            new_state = Deceased(self.model, self.name, self.id, SIRStates.D, kwargs=None)

        elif self.to_recover:
            new_state = Recovered(self.model, self.name, self.id, SIRStates.R, kwargs=None) 
        else:
            raise Exception("No case for Infected")

        new_state.set_values()
        return new_state

    def outputFnc(self):
        ret_val = {}
        if self.to_infect and self.model.OPorts:
        # if not (self.to_recover or self.to_death) and self.model.OPorts:
            try:

                self.infected = self.infected + 1
                outport = np.random.choice(self.model.OPorts)
                ret_val = {outport: "infect_%d" % self.id}
            except Exception as e:
                print(e)
                print(self.state)
        return ret_val

    def set_values(self):
        self.neighbors = 0

        if self.model.OPorts:
            self.neighbors = len(self.model.OPorts) 

        if self.to_death: 
            # Sort exponential race with death
            exp_rate = Parameters.DEATH_MEAN_TIME + self.neighbors * Parameters.BETA_RATE
            self.to_infect = np.random.random() < (self.neighbors * Parameters.BETA_RATE/exp_rate)
            self.ta = reverse_exponential(exp_rate) 

        if self.to_recover:
            # Sort exponential race with death
            exp_rate = Parameters.GAMMA_RATE + self.neighbors * Parameters.BETA_RATE
            self.to_infect = np.random.random() < ((self.neighbors * Parameters.BETA_RATE)/exp_rate)
            self.ta = reverse_exponential(exp_rate) 

class Deceased(AgentState):
    def __init__(self, model, name, id, state, kwargs=None):
        super(Deceased, self).__init__(model, name, id, state, kwargs=None)
        self.just_once = False
        self.infected_end_time = self.current_time

    def intTransition(self): 
        self.just_once = True
        self.set_values()
        return self 
    
    def set_values(self):
        if not self.just_once:
            self.just_once = True
            self.ta = 1
        else:
            self.ta = INFINITY

class Recovered(AgentState):
    def __init__(self, model, name, id, state, kwargs=None):
        super(Recovered, self).__init__(model, name, id, state,kwargs=None)
        self.just_once = False
        self.infected_end_time = self.current_time

    def intTransition(self): 
        self.just_once = True
        self.set_values()
        return self 
    
    def set_values(self):
        if not self.just_once:
            self.just_once = True
            self.ta = 1
        else:
            self.ta = INFINITY


class LogAgent(AtomicDEVS):
    def __init__(self):
        self.set_values()
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
        self.ta = 1 #0.1

class Agent(AtomicDEVS):
    """
    A SIR Agent """

    def __init__(self, name=None, id=None, kwargs=None):
        """
        Constructor (parameterizable).
        """
        # Always call parent class' constructor FIRST:
        AtomicDEVS.__init__(self, name)
        self.elapsed = 0 

        self.in_event = self.addInPort("in_event")

        # The initial state of the agent.
        state = Infected(self, self.name, id, SIRStates.I, kwargs) if np.random.random() < Parameters.INITIAL_PROB \
                                else Susceptible(self, self.name, id, SIRStates.S, kwargs)
        self.state = state

    def extTransition(self, inputs):
        """
        External Transition Function.
        """
        self.state.current_time += self.model.elapsed
        self.state = self.state.extTransition(inputs)
        return self.state

    def intTransition(self):
        """
        Internal Transition Function.
        """ 
        self.state.current_time += self.state.ta
        self.state = self.state.intTransition()
        return self.state

    def __lt__(self, other):
        return self.name < other.name


    def outputFnc(self):
        return self.state.outputFnc()


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
        self.G = nx.Graph()

        # Declare the coupled model's output ports:
        # Autonomous, so no output ports

        # Declare the coupled model's sub-models:


        # Children states initialization
        self.create_topology() 

        self.time_window = {}
        self.agent_states = {}
        # Load the agent states dict:
        for ag in self.agents:
            self.agent_states[ag.state.name] = (ag.state.state , ag.state.emergence, ag.state.vaccinated)

        for i in self.agents:
            self.G.add_node(i.state.id)

        # self.stats = []

        log_agent = LogAgent()
        log_agent.OPorts = []
        log_agent.IPorts = []
        self.addSubModel(log_agent)
        self.agents.append(log_agent)
        log_agent.saveLoginfo()

        # (unique, counts) = np.unique(np.array([it[1][0] for it in self.agent_states.items()]), return_counts=True) 
        # frequencies = dict(zip(unique, counts))
        # log_data = [frequencies.get(key, 0) for key in SIRStates.__dict__.values()]
        # log_data.insert(0, 0) 
        # self.stats.append(log_data)

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
            ind0 = int(i[0])
            ind1 = int(i[1])
            a1 = self.agents[ind0]
            a2 = self.agents[ind1]
            out1 = a1.addOutPort("from%d-to-%d" % (ind0, ind1))
            out2 = a2.addOutPort("from%d-to-%d" % (ind1, ind0))

            self.connectPorts(out1, a2.in_event)
            self.connectPorts(out2, a1.in_event)

        for ag in self.agents:
            ag.state.neighbors = len(ag.OPorts)
            if ag.state.state == SIRStates.I:
                ag.state.set_values()

    def saveChildrenState(self, state):
        super(Environment, self).saveChildrenState(state)
        if not state[0]:
            return
        if state[0].state == SIRStates.I:
            bin = int(state[0].current_time) / Parameters.TW_BIN_SIZE
            self.time_window[bin] = self.time_window.get(bin, 0) + 1

        self.targets = {}
        if state[0].state == SIRStates.E:
            node_from = state[0].infected_by
            node_to = state[0].id

            current_time = state[0].current_time
            self.G.add_edge(node_from, node_to,
                    timestamp=current_time)
            self.G.nodes[node_to]['start'] = current_time

        if state[0].state in (SIRStates.D, SIRStates.R) :
            node = state[0].id
            current_time = state[0].current_time
            self.G.nodes[node]['end'] = current_time

        self.agent_states[state[0].name] = (state[0].state, state[0].emergence, state[0].vaccinated)

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

