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

np.random.seed(0)

class Parameters:
    TOPOLOGY_FILE = "graph_tp"
    INITIAL_PROB = 0.005
    BETA_PROB = 5
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
    def __init__(self, name, id, state):
        """TODO: to be defined1. """
        self._name = name
        self.current_time = 0.0

        self._id = id
        self._state = state
        self._to_recover = False
        self._emergence = False
        if self.state == SIRStates.I:
            self.set_infection_values()
        else:
            self.ta = INFINITY

    def set_infection_values(self):
        self.to_recover = np.random.random() >= Parameters.RHO_PROB
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

        # STATE:
        #  Define 'state' attribute (initial sate):
        state = SIRStates.I if np.random.random() < Parameters.INITIAL_PROB else SIRStates.S
        self.state = AgentState(self.name, id, state)


        # ELAPSED TIME:
        #  Initialize 'elapsed time' attribute if required
        #  (by default, value is 0.0):
        # self.elapsed = 1.5
        # with elapsed time initially 1.5 and initially in
        # state "red", which has a time advance of 60,
        # there are 60-1.5 = 58.5time-units  remaining until the first
        # internal transition

        # PORTS:
        #  Declare as many input and output ports as desired
        #  (usually store returned references in local variables):
        None

    def extTransition(self, inputs):
        """
        External Transition Function.
        """
        self.state.current_time += self.elapsed

        if self.state.state == SIRStates.S:
            self.state.set_infection_values()
            self.state.state = SIRStates.I
        elif self.state.state == SIRStates.R:
            self.state.ta = INFINITY
        # else:
        #     self.state.ta -= self.elapsed
        self.y_up = self.state
        return self.state

    def intTransition(self):
        """
        Internal Transition Function.
        """
        self.state.current_time += self.timeAdvance()

        if self.state.to_recover:
            self.state.state = SIRStates.R
            self.state.ta = INFINITY
        else:
            self.state.set_infection_values()

        self.y_up = self.state

        return self.state

    def __lt__(self, other):
        return self.name < other.name


    def outputFnc(self):
        if(self.state.to_recover == False):
            try:
                outport = np.random.choice(self.OPorts)
                return {outport: "infect"}
            except Exception as e:
                print(self.state)
            # Randomly select a neighbor and send an infect message
        return {}


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
        self.create_topology()

        self.time_window = {}
        self.agent_states = {}
        # Load the agent states dict:
        for ag in self.agents:
            self.agent_states[ag.state.name] = (ag.state.state , ag.state.emergence)

        self.stats = []

        s = i = r = e = 0
        for _, v in self.agent_states.items():
            s += v[0] == SIRStates.S
            i += v[0] == SIRStates.I
            r += v[0] == SIRStates.R
            e += v[1]
        self.stats.append((0, s, i, r, e)) 


        self.points = None
        self.model = None
        self.updatecount = 0

    def create_topology(self):
        G = nx.read_adjlist(Parameters.TOPOLOGY_FILE)
        self.agents = [Agent(name="agent %d" % i, id=i)  for i in range(G.number_of_nodes())]


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


    def globalTransition(self, e_g, x_b_micro, *args, **kwargs):
        super(Environment, self).globalTransition(e_g, x_b_micro, *args, **kwargs)
        for state in x_b_micro: 
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


