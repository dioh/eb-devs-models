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

import sys, os
import random
import numpy as np
import pandas as pd
import scipy.spatial.distance as distance
import scipy.spatial as spatial
import scipy.integrate as integrate
import scipy.special as special
from pypdevs.DEVS import *
from pypdevs.infinity import INFINITY

def reverse_exponential(x):
    return np.random.exponential(1/float(x))

def random_color():
    return "RED" if np.random.uniform()<Parameters.RED_PROBABILITY else "GREEN"

def clear():
    os.system("clear")

class Parameters:
    POPULATION_SIZE = 266
    GRID_SIZE = (20,20)
    HAPPINESS_THRESHOLD = 0.65
    RED_PROBABILITY = 0.5
    EMERGENT_MODEL = False

DEBUG = True

def enum(**kwargs):
    class Enum(object): pass
    obj = Enum()
    obj.__dict__.update(kwargs)
    return obj

ENVProps = enum(PERCENTAGE_UNHAPPY = 'P_UNHAPPY', HAPPINESS = 'HAPPINESS', GRID = "GRID", RANDOM_EMPTY_CELL = "RANDOM_EMPTY_CELL")

class AgentState(object):
    def __init__(self, name, id, position, color):
        """TODO: to be defined1. """
        self._name = name
        self.current_time = 0.0
        self.id = id 
        self.ta = 0
        self.position = position
        self.color = color

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
        percentage_unhappy = self.parent.getContextInformation(ENVProps.PERCENTAGE_UNHAPPY)

        grid = self.parent.getContextInformation(ENVProps.GRID)
        clear()
        print "==================================================== "
        print "%.2f %.5f " % (self.current_time, percentage_unhappy)
        print "==================================================== " 
        print "\n".join( [ " ".join( [ c[0] for c in row ] ) for row in grid ] )

        stats = (self.current_time, percentage_unhappy)
        self.stats.append(stats)

    def intTransition(self):
        self.current_time += self.ta
        self.saveLoginfo()

    def timeAdvance(self):
        return self.ta

    def set_values(self):
        self.ta = 0.01 

class Agent(AtomicDEVS):
    def __init__(self, name=None, id=None, position=None, color=None, kwargs=None):
        # Always call parent class' constructor FIRST:
        AtomicDEVS.__init__(self, name)
        self.elapsed = 0 
        self.state = AgentState(name=name, id=id, position=position, color=color) 

    def extTransition(self, inputs): 
        return self.state

    def intTransition(self):
        happy = self.parent.getContextInformation( ENVProps.HAPPINESS, ag_id = self.state.id )
        if not happy:
            empty_cell = self.parent.getContextInformation( ENVProps.RANDOM_EMPTY_CELL, ag_id = self.state.id )
            self.state.position = empty_cell
        return self.state

    def outputFnc(self):
        return {}

    def timeAdvance(self):
        self.state.ta = reverse_exponential(0.5)
        return self.state.ta

class Environment(CoupledDEVS):
    def __init__(self, name=None):
        CoupledDEVS.__init__(self, name)

        self.create_topology() 

        self.log_agent = LogAgent()
        self.log_agent.OPorts = []
        self.log_agent.IPorts = []
        self.addSubModel(self.log_agent)
        self.log_agent.saveLoginfo()

    def create_topology(self):
        self.agents = {}
        self.grid = [ [ None for i in range(Parameters.GRID_SIZE[0]) ] for j in range(Parameters.GRID_SIZE[1]) ]
        agent_positions = random.sample(range(Parameters.GRID_SIZE[0] * Parameters.GRID_SIZE[1]), Parameters.POPULATION_SIZE)
        for i, pos in enumerate(agent_positions):
            ag_id = int(i)
            grid_pos = ( pos / 20, pos % 20 )
            color = random_color()

            agent = Agent(name="agent %s" % i, id=ag_id, position = grid_pos, color = color)
            self.grid[grid_pos[0]][grid_pos[1]] = ag_id
            self.agents[ag_id] = self.addSubModel(agent)

    def agent_happiness(self, ag_id):
        ag_pos = self.agents[ag_id].state.position
        ag_color = self.agents[ag_id].state.color
        directions = [-1, 1]
        moore_neigh = [ ( ag_pos[0]+h, ag_pos[1]+v ) for h in directions for v in directions ]
        moore_neigh = [ p for p in moore_neigh if p[0]>0 and p[1]>0 and p[0]<len(self.grid) and p[1]<len(self.grid[0]) ]
        moore_colors = [ self.agents[ self.grid[p[0]][p[1]] ].state.color for p in moore_neigh if self.grid[p[0]][p[1]] is not None ]
        neigh_matchs = len( [ c for c in moore_colors if c==ag_color ] ) / float(len(moore_colors)) if len(moore_colors)>0 else 0.0
        return neigh_matchs >= Parameters.HAPPINESS_THRESHOLD

    def termination(self, prev, total):
        return self.getContextInformation(ENVProps.PERCENTAGE_UNHAPPY)==0.0 

    def random_empty_cell(self):
        empty_cells = [ (i, j) for i, r in enumerate(self.grid) for j, c in enumerate(r) if c is None ]
        np.random.shuffle( empty_cells )
        return empty_cells[0]

    def globalTransition(self, e_g, x_b_micro, *args, **kwargs):
        super(Environment, self).globalTransition(e_g, x_b_micro, *args, **kwargs)

    def getContextInformation(self, property, *args, **kwargs):
        super(Environment, self).getContextInformation(property)

        if(property == ENVProps.GRID):
            return [ [ self.agents[c].state.color if c is not None else " " for c in row ] for row in self.grid ]
        elif(property == ENVProps.PERCENTAGE_UNHAPPY):
            unhappy = [ ag_id for ag_id in self.agents if not self.agent_happiness(ag_id) ]
            return len( unhappy ) / float( len(self.agents) )
        elif(property == ENVProps.HAPPINESS):
            return self.agent_happiness(kwargs["ag_id"])
        elif(property == ENVProps.RANDOM_EMPTY_CELL):
            ag_pos = self.agents[kwargs["ag_id"]].state.position
            empty_cell = self.random_empty_cell()
            self.grid[ag_pos[0]][ag_pos[1]] = None
            self.grid[empty_cell[0]][empty_cell[1]] = kwargs["ag_id"]
            return empty_cell

    def select(self, immChildren):
        return immChildren[0]

