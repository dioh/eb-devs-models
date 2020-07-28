# Copyright 2014 Modelling, Simulation and Design Lab (MSDL) at 
# McGill University and the University of Antwerp (http://msdl.cs.mcgill.ca/)
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
import random
import scipy.spatial.distance as distance
import scipy.spatial as spatial
# from sklearn.neighbors import NearestNeighbors
from periodic_search import NearestNeighbors
import networkx as nx

# Import code for DEVS model representation:
from pypdevs.DEVS import *
from pypdevs.infinity import INFINITY


# random.seed(9001)
# random.seed(2)
# GRID_SIZE = 100
# FLOCK_SIZE = 200
# TA = 5
# MAX_DIST = 1
# MAX_SEPARATE_TURN = 1.5
# RADIUS = 3
# MAX_ALIGN_TURN = 5
# MAX_COHERE_TURN = 3
# STEP_DIST = 0.5
# DEBUG = True

class Parameters:
    GRID_SIZE = 70 #
    FLOCK_SIZE = 200 #
    ANTICOHERE_CAP = -1 #
    TA = 1
    MAX_SEPARATE_TURN = 0.03 #
    MAX_DIST = 0.5 #
    RADIUS = 5 #
    MAX_ALIGN_TURN = 0.09 #
    MAX_COHERE_TURN = 0.05 #
    STEP_DIST = 1
    SUPERCOHERE_CAP = -1

DEBUG = True

# MAX_SEPARATE_TURN = 1.5
# MAX_DIST = 3
# RADIUS = 3
class ArrayWidthStateRef(np.ndarray):

    def __new__(cls, input_array, state):
        # Input array is an already formed ndarray instance
        # We first cast to be our class type
        obj = np.asarray(input_array).view(cls)
        # add the new attribute to the created instance
        obj.state = state
        # Finally, we must return the newly created object:
        return obj

    def __array_finalize__(self, obj):
        # see InfoArray.__array_finalize__ for comments
        if obj is None: return
        self.state = getattr(obj, 'state', None)

class BirdState(object):

    """Docstring for BirdState. """

    def __init__(self, name, id):
        """TODO: to be defined1. """
        self._name = name

        grid_side_width = ((Parameters.GRID_SIZE ** 2) / Parameters.FLOCK_SIZE) ** (0.5)

        grid_side_amount = Parameters.GRID_SIZE / grid_side_width

        grid_index_y = (id // grid_side_amount) * grid_side_width
        grid_index_x = (id % grid_side_amount) * grid_side_width

        self._coord = np.array((random.random() * grid_side_width + grid_index_x,
                            random.random() * grid_side_width + grid_index_y))

        self._heading = random.random() * 2*np.pi
        self.neighbors = 0
        self.centerofmass_x = 0
        self.centerofmass_y = 0
        self.supercohereflag = False
        self.beh_type = "N"

    @property
    def name(self):
        """I'm the 'heading' property."""
        return self._name

    @property
    def heading(self):
        """I'm the 'heading' property."""
        return self._heading

    @heading.setter
    def heading(self, angle):
        self._heading = angle % (2*np.pi)

    @property
    def coord(self):
        """I'm the 'coord' property."""
        return self._coord

    @coord.setter
    def coord(self, value):
        self._coord = value

    def get(self):
        return(self._coord, self._heading)

    def __repr__(self):
        return "Coord: %s, Head: %s" % (str(self.coord), str(self.heading))


class Bird(AtomicDEVS):
    """
    A traffic light 
    """

    def __init__(self, name=None, id=None):
        """
        Constructor (parameterizable).
        """
        # Always call parent class' constructor FIRST:
        AtomicDEVS.__init__(self, name)
        self.superturns = 30
        self.supercohere_cap = Parameters.SUPERCOHERE_CAP

        self.sctimes = 0

        # STATE:
        #  Define 'state' attribute (initial sate):
        self.state = BirdState(self.name, id) 

        # ELAPSED TIME:
        #  Initialize 'elapsed time' attribute if required
        #  (by default, value is 0.0):
        self.elapsed = 1.5
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
        # Compute the new state 'Snew' based (typically) on current
        # State, Elapsed time parameters and calls to 'self.peek(self.IN)'.

        state = self.state.get()
        raise DEVSException(\
                "No external transition should be called"\
            % state)

    def intTransition(self):
        """
        Internal Transition Function.
        """
        coord = self.state.coord
        heading = self.state.heading

        closest = self.parent.getContextInformation("closest", coord=coord)
        neighbors = self.parent.getContextInformation("neighbors", coord=coord) 
        gettos = self.parent.getContextInformation("gettos", coord=coord) 
        self.state.neighbors = gettos

        if( neighbors is None or len(neighbors) == 0) :
            self.state.beh_type = 'NN'
            self.advance()
            return self.state


        # First transition do nothing but inform position.
        self.state.beh_type = 'VOID'


        if Parameters.ANTICOHERE_CAP  > -1 and Parameters.SUPERCOHERE_CAP > -1:
            assert False, "Super coherence and anti coherence should not happen at the same time"

        if (gettos < Parameters.ANTICOHERE_CAP and Parameters.ANTICOHERE_CAP  > -1):
            self.state.beh_type = 'AC'
            self.anticohere(neighbors)
        elif (gettos < self.supercohere_cap  or (self.state.supercohereflag and self.sctimes <= 4)):
            self.state.beh_type = 'SC'
            self.state.supercohereflag = True

            coherence_cap =  0.5 * np.pi * self.superturns / 20 + Parameters.MAX_COHERE_TURN

            if self.superturns == 0:
                self.sctimes = self.sctimes + 1
                self.superturns = 30 / (1.5 * self.sctimes)
                self.state.supercohereflag = False
                self.supercohere_cap = self.supercohere_cap - 3

            self.superturns = max(0, self.superturns - 1)
            self.supercohere(neighbors, coherence_cap)
        else:
            if not closest:
                self.state.beh_type = 'NC'
                self.advance()
                return self.state
            closest_coord = closest.coord

            self.state.beh_type = 'N'
            if distance.euclidean(np.asarray(closest_coord),
                    np.asarray(self.state.coord)) < Parameters.MAX_DIST:
                self.separate(closest)
            else:
                self.align(neighbors)
                self.cohere(neighbors)

        self.advance()

        return self.state

    def __lt__(self,other):
        return self.name < other.name

    ### Non DEVS methods

    def separate(self, closest):
        """TODO: Docstring for separate.
        :returns: TODO 
        """
        delta =  self.state.heading - closest.heading 
        turn_at_most = min(abs(delta), Parameters.MAX_SEPARATE_TURN)
        self.state.heading = self.state.heading +  np.sign(delta) * turn_at_most #* -1

    def align(self, neighbors):
        """TODO: Docstring for align.

        :f: TODO
        :returns: TODO

        """
        #turn-towards average-flockmate-heading max-align-turn
        # let x-component sum [dx] of flockmates
        # let y-component sum [dy] of flockmates
        # ifelse x-component = 0 and y-component = 0
        # [ report heading ]
        # [ report atan x-component y-component ]

        headings = np.array([ bird.heading for bird in neighbors ])

        rads=headings

        x_sum = np.sum(np.cos(rads))
        y_sum = np.sum(np.sin(rads))

        new_heading = self.state.heading

        if not (x_sum == y_sum == 0):
            # new_heading = np.math.atan2(y_sum / headings.size, x_sum / headings.size)
            new_heading = np.math.atan2(y_sum, x_sum)


        delta = new_heading - self.state.heading
        turn_at_most = min(abs(delta), Parameters.MAX_ALIGN_TURN)

        self.state.heading = self.state.heading + np.sign(delta) * turn_at_most

    def anticohere(self, neighbors):
        x, y = self.state.coord
        coords = np.array([ bird.coord for bird in neighbors ])

        x_mean, y_mean = np.mean(coords, 0)

        towards_x = x_mean #- x
        towards_y = y_mean #- y

        self.state.heading = np.math.atan2(towards_y - self.state.coord[1],
                towards_x - self.state.coord[0]) + np.pi

    def supercohere(self, neighbors, coherence_cap):
        self.cohere(neighbors, coherence_cap)

    def cohere(self, neighbors, cohere_cap = Parameters.MAX_COHERE_TURN):
        """TODO: Docstring for cohere.

        :returns: TODO

        """
        # let x-component mean [sin (towards myself + 180)] of flockmates
        # let y-component mean [cos (towards myself + 180)] of flockmates
        # ifelse x-component = 0 and y-component = 0
        # [ report heading ]
        # [ report atan x-component y-component ]
        x, y = self.state.coord
        coords = np.array([ bird.coord for bird in neighbors ])
        coords = np.append(coords, np.array([self.state.coord]), axis=0)


        x_mean, y_mean = np.mean(coords, 0)

        towards_x = x_mean #- x
        towards_y = y_mean #- y

        self.state.centerofmass_x = towards_x
        self.state.centerofmass_y = towards_y



        new_heading = self.state.heading
        if (x_mean == y_mean == 0):
            return new_heading
        #new_heading = np.math.atan2(towards_y, towards_x)

        new_heading = np.math.atan2(towards_y - self.state.coord[1],
                towards_x - self.state.coord[0]) 

        delta = new_heading - self.state.heading
        turn_at_most = min(abs(delta), cohere_cap)

        self.state.heading = self.state.heading + np.sign(delta) * turn_at_most

    def advance(self, step=Parameters.STEP_DIST):
        """TODO: Docstring for advance.

        :f: TODO
        :returns: TODO

        """
        rads=self.state.heading
        self.state.coord[0] = (self.state.coord[0] + np.math.cos(rads) * step) % Parameters.GRID_SIZE
        self.state.coord[1] = (self.state.coord[1] + np.math.sin(rads) * step) % Parameters.GRID_SIZE


    def outputFnc(self):
        return dict()

    def timeAdvance(self):
        """
        Time-Advance Function.
        """
        # Compute 'ta', the time to the next scheduled internal transition,
        # based (typically) on current State.
        return Parameters.TA


class Flock(CoupledDEVS):
    def __init__(self, name=None):
        """
        A simple flocking system consisting
        """
        # Always call parent class' constructor FIRST:
        CoupledDEVS.__init__(self, name)

        # Declare the coupled model's output ports:
        # Autonomous, so no output ports

        # Declare the coupled model's sub-models:

        # The TrafficLight 
        self.birds = [Bird(name="bird %d" % i, id=i)  for i in range(Parameters.FLOCK_SIZE)]
        for bird in self.birds:
            self.addSubModel(bird)

        self.history = pd.DataFrame([[x.state.name, x.state.coord[0], x.state.coord[1], x.state.heading,
                        -1.5, None, 0, x.state.coord[0], x.state.coord[1], x.state.beh_type] for x in self.birds],
                        columns=['bird', 'x', 'y', 'heading', 't', 'cluster', 'neighbors', 'cm_x', 'cm_y', 'behavior_type'])

        # Children states initialization
        self.states = {}
        self.points = None
        self.model = None
        self.updatecount = 0

    def saveChildrenState(self, state):
        super(Flock, self).saveChildrenState(state)
        self.states[state[0].name] = state[0]
        self.updatecount = self.updatecount + 1

        if self.updatecount % Parameters.FLOCK_SIZE == 0:
            # All birds updated, lets recompute.
            self.points = np.array([ np.array(x.coord) for x in self.states.values() ])

            self.model = NearestNeighbors(radius=Parameters.RADIUS)
            self.model.fit(self.points)

            self.updatecount = 0
            if DEBUG:
                gr = self.model.radius_neighbors_graph()
                df_data = pd.DataFrame([[x.name, x.coord[0], x.coord[1], x.heading,
                                state[1][0], None, x.neighbors, x.centerofmass_x, x.centerofmass_y, x.beh_type] for i, x in enumerate(self.states.values())] ,
                                columns=['bird', 'x', 'y', 'heading', 't', 'cluster', 'neighbors', 'cm_x', 'cm_y', 'behavior_type'])
                self.gettos = nx.number_connected_components(gr)

                for i, sub in enumerate(nx.connected_component_subgraphs(gr)):
                    nodes = (sub.nodes())
                    df_data.ix[list(nodes), "cluster"] = i

                if self.history is None:
                    self.history = df_data
                else:
                    self.history = self.history.append(df_data, ignore_index=True) 


    def getContextInformation(self, property, *args, **kwargs):
        super(Flock, self).getContextInformation(property)

        if not self.model:
            return

        if property == "closest":
            coord = kwargs['coord']
            neighbor = self.model.closest([coord])
            # Ignore the point with distance zero
            if not neighbor:
                return
            return_point = list(self.states.values())[neighbor]
            return return_point

        if property == "neighbors":
            coord = kwargs['coord']
            neighbors = self.model.neighbors(coord)
            return np.array(list(self.states.values()))[neighbors]

        if property == "gettos": 
            return self.gettos


    def select(self, immChildren):
        """
        Choose a model to transition from all possible models.
        """
        # Doesn't really matter, as they don't influence each other
        return immChildren[0]


