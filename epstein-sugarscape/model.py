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

# UTIL FUNCTIONS
np.random.seed(0)

def gini(x):
    """Compute Gini coefficient of array of values"""
    diffsum = 0
    for i, xi in enumerate(x[:-1], 1):
        diffsum += np.sum(np.abs(xi - x[i:]))
    return diffsum / (len(x)**2 * np.mean(x))

def reverse_exponential(x):
    return np.random.exponential(1/float(x))

def uniform(interval):
    return np.random.uniform(interval[0],interval[1])

def clear():
    os.system("clear")

class Parameters:
    #Lattice length _L_ | 50
    GRID_SIZE = (30,30)
    #Growth rate a | 1
    #Number of agents _N_ | 250
    POPULATION_SIZE = 50
    #Agents' initial wealth _w_ 0 distribution | U[5,25]
    INITIAL_WEALTH = (5,25)
    #Agents' metabolic rate _m_ distribution | U[1,4]
    METABOLIC_RATE = (1,2)
    #Agents' vision _v_ distribution | U[1,6]
    VISION = (1,6)
    #Agents' maximum age _max-age_ distribution | U[60,100]
    # Lower GINI_VALUES enables the fasting model
    GINI_THRESHOLD = 0.05
    # Agents with more than WEALTH_TRESHOLD will fast if also above GINI THRESHOLD
    WEALTH_TRESHOLD = 90
    

def enum(**kwargs):
    class Enum(object): pass
    obj = Enum()
    obj.__dict__.update(kwargs)
    return obj

AtomicType = enum(CELL = "CELL", AGENT = "AGENT")
ENVProps = enum(GRID = "GRID", MAX_SUGAR_NEXT_CELL = "MAX_SUGAR_NEXT_CELL", RANDOM_EMPTY_CELL = "RANDOM_EMPTY_CELL", IS_TOP_RICHEST='To richest from the model')
GRIDProps = enum(EMPTY = ' ', OCCUPIED = '*', DEAD = 'D')

class AgentState(object):
    def __init__(self, name, id, position):
        """TODO: to be defined1. """
        self._name = name
        self.id = id 
        self.current_time = 0.0
        self.ta = 0.0
        self.alive = True
        self.setstats( position )
        self.fasting = False

    def setstats(self, position):
        self.age = 0.0
        self.position = position
        self.vision = int(uniform( Parameters.VISION ) )
        self.metabolic_rate = int(uniform( Parameters.METABOLIC_RATE ) )
        self.wealth = int(uniform( Parameters.INITIAL_WEALTH ) )

    def die(self):
        self.alive = False

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
        return "Agent: %s, " % (str(self.name))

class CellState(object):
    def __init__(self, name, id, position, max_capacity):
        """TODO: to be defined1. """
        self._name = name
        self.id = id 
        self.current_time = 0.0
        self.ta = 0.0
        self.position = position
        self.sugar = max_capacity
        self.max_capacity = max_capacity

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
        return "Agent: %s" % (str(self.name))

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
        clear()
        occ_grid, sugar_grid, g, p = self.parent.getContextInformation(ENVProps.GRID)
        print ("\n".join( [ " ".join( [ c for c in r1 ] )+"  "+" ".join( [ str(c) for c in r2 ] ) for r1,r2 in zip(occ_grid,sugar_grid) ] ))
        print ("".join(["="]*Parameters.GRID_SIZE[0]*4))
        print ("Time: %.2f Population: %d Gini coefficient: %.2f" % (self.current_time, p, g))
        print ("".join(["="]*Parameters.GRID_SIZE[0]*4))

        stats = (self.current_time, p)
        self.stats.append(stats)

    def intTransition(self):
        self.current_time += self.ta
        self.saveLoginfo()

    def timeAdvance(self):
        return self.ta

    def set_values(self):
        self.ta = 0.01 

class Cell(AtomicDEVS):
    def __init__(self, name=None, id=None, position=None, max_capacity=1, kwargs=None):
        # Always call parent class' constructor FIRST:
        AtomicDEVS.__init__(self, name)
        self.elapsed = 0 
        self.state = CellState(name=name, id=id, position=position, max_capacity=max_capacity) 

    def extTransition(self, inputs):
        self.state.sugar = 0
        return self.state

    def intTransition(self):
        #if self.state.sugar+self.state.growth_rate <= self.state.max_capacity:
        #    self.state.sugar += self.state.growth_rate
        #elif self.state.sugar < self.state.max_capacity:
        #    self.state.sugar = self.state.max_capacity

        self.state.sugar = self.state.max_capacity

        self.y_up = (AtomicType.CELL, self.state.position, self.state.sugar)

        return self.state

    def outputFnc(self):
        return {}

    def timeAdvance(self):
        self.state.ta = reverse_exponential(0.5)
        return self.state.ta

class Agent(AtomicDEVS):
    def __init__(self, name=None, id=None, position=None, kwargs=None):
        # Always call parent class' constructor FIRST:
        AtomicDEVS.__init__(self, name)
        self.elapsed = 0 
        self.state = AgentState(name=name, id=id, position=position) 
        self.cells_dict = {}

    def extTransition(self, inputs): 
        return self.state

    def intTransition(self):

        #Save position before move        
        last_position = self.state.position

        # Ask enviroment for the next max sugar cell
        next_cell = self.parent.getContextInformation( ENVProps.MAX_SUGAR_NEXT_CELL, pos = self.state.position, vision = self.state.vision )
        if next_cell is not None:
            if not self.state.fasting: 
                cell_pos, cell_sugar = next_cell
                self.state.position = cell_pos
                self.state.wealth+= cell_sugar
        
        # Metabolize
        self.state.wealth-= self.state.metabolic_rate
        self.state.age += self.state.ta

        # Check if agent dies
        #if self.state.age > self.state.max_age or self.state.wealth < 0:
        #    rnd_position = self.parent.getContextInformation( ENVProps.RANDOM_EMPTY_CELL )
        #    self.state.setstats(rnd_position)

        if self.state.wealth < 0:
            self.state.die()

        # Save position movement for enviroment global transition
        self.y_up = ( self.state.id, AtomicType.AGENT, last_position, self.state.position, self.state.alive, self.state.wealth)
        gini_condition, wealth_percentile = self.parent.getContextInformation( ENVProps.IS_TOP_RICHEST)
    
        self.state.fasting = gini_condition and self.state.wealth > wealth_percentile

        return self.state

    def outputFnc(self):
        if not self.state.fasting:
            return {self.cells_dict[self.state.position] : "VACIAR"}
        return {}

    def timeAdvance(self):
        self.state.ta = reverse_exponential(0.5) if self.state.alive else INFINITY
        return self.state.ta

class Environment(CoupledDEVS):
    def __init__(self, name=None):
        CoupledDEVS.__init__(self, name)

        self.create_grid() 
        self.create_agents() 
        self.create_logagent() 


    #########################################################
    # INIT  METHODS #########################################
    #########################################################

    def create_logagent(self):
        self.log_agent = LogAgent()
        self.log_agent.OPorts = []
        self.log_agent.IPorts = []
        self.addSubModel(self.log_agent)
        self.log_agent.saveLoginfo()

    def create_grid(self):
        self.cells = {}
        self.sugar_grid = [ [ 0.0 for i in range(Parameters.GRID_SIZE[0]) ] for j in range(Parameters.GRID_SIZE[1]) ]
        self.occupation_grid = [ [ GRIDProps.EMPTY for i in range(Parameters.GRID_SIZE[0]) ] for j in range(Parameters.GRID_SIZE[1]) ]
        cell_positions = [ (i,j) for i in range(Parameters.GRID_SIZE[0]) for j in range(Parameters.GRID_SIZE[1]) ]
        for i, grid_pos in enumerate(cell_positions):
            ce_id = int(i)
            max_capacity = min(max(int(abs(grid_pos[0]/6-grid_pos[1]/6))+1,0),5)
            cell = Cell(name="cell %d" % i, id=ce_id, position = grid_pos, max_capacity = max_capacity)
            self.sugar_grid[grid_pos[0]][grid_pos[1]] = cell.state.sugar
            self.cells[ce_id] = self.addSubModel(cell)

    def create_agents(self):
        self.agents = {}
        agent_positions = random.sample(range(Parameters.GRID_SIZE[0] * Parameters.GRID_SIZE[1]), Parameters.POPULATION_SIZE)

        self.wealth = {}
        for i, pos in enumerate(agent_positions):
            ag_id = int(i) 
            grid_pos = ( int(pos / Parameters.GRID_SIZE[0]), int(pos % Parameters.GRID_SIZE[1]) )
            agent = Agent(name="agent %d" % i, id=ag_id, position = grid_pos)
            self.occupation_grid[grid_pos[0]][grid_pos[1]] = GRIDProps.OCCUPIED
            self.agents[ag_id] = self.addSubModel(agent)

            self.wealth[ag_id] = agent.state.wealth

            for ce_id, cell in self.cells.items():
                cellinport = cell.addInPort(name=ag_id)
                agtoutport = agent.addOutPort(name=ce_id)
                agent.cells_dict[cell.state.position] = agtoutport
                self.connectPorts(agtoutport, cellinport)


    ##########################################################
    # SUGARSCAPE MODEL METHODS ###############################
    ##########################################################

    def max_sugar_next_cell(self, agent_pos, agent_vision):
        # Select cells in agent vision range
        directions = list(range(1,int(agent_vision)+1)) + list(range(-int(agent_vision),0))
        cells_in_range = [ ( agent_pos[0]+h, agent_pos[1]+v ) for h in directions for v in directions ]
        # Check borders
        cells_in_range=[(i,j) for i,j in cells_in_range if i>=0 and j>=0 and i<len(self.sugar_grid) and j<len(self.sugar_grid[0])]
        # Select non empty
        cells_in_range = [ (i,j) for i,j in cells_in_range if self.occupation_grid[i][j] == GRIDProps.EMPTY ]
        # If all occupied within range, not move
        if len(cells_in_range)==0: return None
        
        # Return the nearest among those with more sugar 
        cells_in_range = [ ((i,j),self.sugar_grid[i][j]) for i,j in cells_in_range ]
        max_sugar = max([ s for p,s in cells_in_range ])
        max_sugar_cells = [ (ij,s) for ij,s in cells_in_range if s==max_sugar ]
        min_distance_cells = [ ((i,j),s,( (i-agent_pos[0])**2 + (j-agent_pos[1])**2 )**0.5) for ((i,j),s) in max_sugar_cells ]
        min_distance = min([ d for p,s,d in min_distance_cells ])
        min_distance_cells = [ (ij,s) for ij,s,d in min_distance_cells if d==min_distance ]
        # Randomly if more than one
        np.random.shuffle( max_sugar_cells )
        return max_sugar_cells[0]

    def random_empty_cell(self):
        empty_cells = [ (i,j) for i,r in enumerate(self.occupation_grid) for j, c in enumerate(r) if not c == GRIDProps.OCCUPIED ]
        np.random.shuffle( empty_cells )
        empty_cell = empty_cells[0]
        return empty_cell

    ##########################################################
    # DEVS/PYDEVS/EB-DEVS METHODS ############################
    ##########################################################

    def termination(self, prev, total):
        return False

    def globalTransition(self, e_g, x_b_micro, *args, **kwargs):
        for x in x_b_micro:
            if x[0] == AtomicType.AGENT:
                agent_id, atomictype, last_pos, actual_pos, agent_alive, agent_wealth = x
                self.occupation_grid[last_pos[0]][last_pos[1]] = GRIDProps.EMPTY
                self.occupation_grid[actual_pos[0]][actual_pos[1]] = GRIDProps.OCCUPIED if agent_alive else GRIDProps.DEAD
                if agent_alive:
                    self.wealth[agent_id] = agent_wealth
                else:
                    if agent_id in self.wealth:
                        del self.wealth[agent_id]
            elif x[0] == AtomicType.CELL:
                atomictype, pos, sugar = x
                self.sugar_grid[pos[0]][pos[1]] = sugar

        super(Environment, self).globalTransition(e_g, x_b_micro, *args, **kwargs)

    def getContextInformation(self, property, *args, **kwargs):
        super(Environment, self).getContextInformation(property)

        if(property == ENVProps.GRID):
            g=gini(np.array([ ag.state.wealth for i,ag in self.agents.items() if ag.state.alive ]))
            p=len([ ag for i,ag in self.agents.items() if ag.state.alive ]) 
            return ( list(self.occupation_grid), list(self.sugar_grid), g, p )
        elif(property == ENVProps.MAX_SUGAR_NEXT_CELL):
            return self.max_sugar_next_cell(kwargs["pos"],kwargs["vision"])
        elif(property == ENVProps.RANDOM_EMPTY_CELL):
            return self.random_empty_cell()
        elif(property == ENVProps.IS_TOP_RICHEST):
            wealth_arr = np.array(self.wealth.values())
            g = gini(wealth_arr)
            return  g > Parameters.GINI_THRESHOLD, np.percentile(wealth_arr, Parameters.WEALTH_TRESHOLD)

    def select(self, immChildren):
        return immChildren[0]

