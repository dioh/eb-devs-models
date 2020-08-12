#!/usr/bin/env python
# -*- coding: utf-8 -*-

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

import copy
import numpy as np
import scipy.spatial.distance as distance
# import scipy.spatial as spatial
# from sklearn.neighbors import NearestNeighbors
# import networkx as nx
from pypdevs.infinity import INFINITY

# Import code for DEVS model representation:
from pypdevs.DEVS import CoupledDEVS, AtomicDEVS
import random

from sklearn.neighbors import NearestNeighbors



import sqlite3

def init_sqlite3(dbname):
    conn = sqlite3.connect(dbname)
    c = conn.cursor()
    c.execute(
        """CREATE TABLE IF NOT EXISTS mitostate (id INTEGER,
              name VARCHAR(255),
              area VARCHAR(255),
              child INTEGER,

              fusionatedwith INTEGER,
              currenttime INTEGER,
              direction REAL,
              mass REAL,
              oldmass REAL,
              parent INTEGER,
              position_x REAL,
              position_y REAL, 
              requestedstate VARCHAR(50),
              rerun INTEGER,
              state VARCHAR(80),
              ta INTEGER,

              timeunit INTEGER,
              velocity REAL,
              duration INTEGER,
              retry INTEGER,

              fissionprob REAL,
              PRIMARY KEY(id, currenttime, duration, retry, fissionprob, rerun)
                )
        """)
    conn.commit()
    return conn

# np.random.seed(0)
random.seed(0)

class Parameters(object):
    DB_NAME = "mito_experiment.sqlite"
    MASS_TOTAL = 300
    MASS_MAX = 3.0
    MASS_MIN = 0.5

    DURATION = 720
    RETRY = 1

    PROB_FISSION = 0.2

    # Cell areas are define from the innermost area
    # to the outermost.
    RADIUS_CELL_END = 50.0/2
    RADIUS_NUCLEUS_END = 16.6/2
    RADIUS_PERINUCLEAR_END = 25.0/2
    RADIUS_CYTOSOLIC_END = RADIUS_CELL_END

    VEL_CYTOSOLIC = 0.5
    VEL_PERINUCLEAR = 0.22

    RATE_FF = 30
    RATE_INACTIVE_FF_WAKE = RATE_FF
    RATE_MV = 1

    RADIUS = 1

    def as_dict_values(self):
        dict_of_values = copy.deepcopy(self.__dict__)
        for k in dict_of_values.keys():
            new_key = k.replace("_", "")
            dict_of_values[new_key] = dict_of_values.pop(k)

DEBUG = True


def enum(**kwargs):
    class Enum(object):
        pass
    obj = Enum()
    obj.__dict__.update(kwargs)
    return obj


MitoStates = enum(A='Active', I='Inactive')
MitoRequestedStates = enum(FU='Fusionated', FI='Fissionated', N="None")
MitoAreas = enum(N='Nucleus', C='Cytosolic', P='Perinuclear')
ENVProps = enum(FI='fissionate', AREAS='Nuclear areas',
                RATE_FF="Fission Fussion rate",
                RATE_MV="Movement rate",
                NEIGHBOR="Neighboring mito",
                SHOULDFUSION="Determines if it should fussion or not",
                DIDFUSION="Consume fusion agent",
                VELOCITIES="Low and high velocities for mitos")



class MitoState(object):
    def __init__(self, model, name, id, state):
        """TODO: to be defined1. """
        self._name = name
        self.current_time = 0.0

        self._id = id
        self._parent = None
        self._child = None
        self._state = state
        self._ta = Parameters.RATE_MV

        self.requested_state = MitoRequestedStates.N
        self.re_run = False

        # Get a position valid inside the circle defined in Parameters
        rho = random.random() * 2 * np.pi
        radius = (Parameters.RADIUS_NUCLEUS_END +
                  random.random() * (Parameters.RADIUS_CELL_END -
                                     Parameters.RADIUS_NUCLEUS_END))

        x = np.cos(rho) * radius
        y = np.sin(rho) * radius

        self._position = np.array([x, y])
        self._direction = random.random() * 2 * np.pi
        self._time_unit = 1

        self._mass = random.random() * (Parameters.MASS_MAX -
                      Parameters.MASS_MIN) + Parameters.MASS_MIN



        self._old_mass = None

        # This is going to be defined by the interactions with the cell

        self._velocity = None
        self._area = None

    def as_dict_values(self):
        dict_of_values = copy.deepcopy(self.__dict__)
        for k in dict_of_values.keys():
            new_key = k.replace("_", "")
            dict_of_values[new_key] = dict_of_values.pop(k)

        dict_of_values['position_x'] = dict_of_values['position'][0]
        dict_of_values['position_y'] = dict_of_values['position'][1]
        dict_of_values.pop('position')

        return dict_of_values

    @property
    def id(self):
        return self._id

    @property
    def area(self):
        """I'm the 'area' property."""
        return self._area

    @area.setter
    def area(self, area):
        self._area = area

    @property
    def position(self):
        """I'm the 'position' property."""
        return self._position

    @position.setter
    def position(self, position):
        self._position = position

    @property
    def direction(self):
        """I'm the 'direction' property."""
        return self._direction

    @direction.setter
    def direction(self, direction):
        self._direction = direction % (2*np.pi)

    @property
    def time_unit(self):
        """I'm the 'time_unit' property."""
        return self._time_unit

    @time_unit.setter
    def time_unit(self, time_unit):
        self._time_unit = time_unit

    @property
    def velocity(self):
        """I'm the 'velocity' property."""
        return self._velocity

    @velocity.setter
    def velocity(self, velocity):
        self._velocity = velocity

    @property
    def old_mass(self):
        """I'm the 'old_mass' property."""
        return self._old_mass

    @old_mass.setter
    def old_mass(self, old_mass):
        self._old_mass = old_mass

    @property
    def mass(self):
        """I'm the 'mass' property."""
        return self._mass

    @mass.setter
    def mass(self, mass):
        self._mass = mass

    @property
    def name(self):
        """I'm the 'heading' property."""
        return self._name

    @name.setter
    def name(self, name):
        self._name = name

    @property
    def state(self):
        """I'm the 'state' property."""
        return self._state

    @state.setter
    def state(self, state):
        self._state = state

    @property
    def parent(self):
        """I'm the 'heading' property."""
        return self._parent

    @parent.setter
    def parent(self, parent):
        self._parent = parent

    @property
    def child(self):
        """I'm the 'heading' property."""
        return self._child

    @child.setter
    def child(self, child):
        self._child = child

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
        return "Mito: %s, State: %s, ReqState: %s" % (str(self.name), str(self.state), str(self.requested_state))


class Mito(AtomicDEVS):
    """
    A Mitochondria agent
    """

    def __init__(self, parent, name=None, id=None, state=MitoStates.I):
        """
        Constructor (parametrizable).
        """
        # Always call parent class' constructor FIRST:
        AtomicDEVS.__init__(self, name)
        self.state = MitoState(self, name, id, state)

        self.areas = parent.getContextInformation(ENVProps.AREAS)
        self.velocities = parent.getContextInformation(ENVProps.VELOCITIES)

        self.state.direction = self.get_new_direction()
        self.state.area = self.get_area_from_position(self.state.position)
        self.state.velocity = self.get_new_velocity(self.state)

    def get_area_from_position(self, position):
        h = (position[0]**2 + position[1] ** 2) ** 0.5
        if self.areas[0] <= h and h <= self.areas[1]:
            return MitoAreas.P
        if self.areas[1] < h and h <= self.areas[2]:
            return MitoAreas.C

    def get_new_direction(self, state=None, random_direction=True):
        """
        Set the random direction. This is the case for free-movement.
        """

        # TODO: if patch-ahead is not free then rotate 90 to tthe right
        if not random_direction:
            return state.direction + np.pi

        return random.random() * 2 * np.pi

    def get_new_velocity(self, state):
        """
        Set velocity based on the area it is positioned
        """
        area = self.get_area_from_position(state.position)
        if area == MitoAreas.P:
            return self.velocities['P']
        if area == MitoAreas.C:
            return self.velocities['C']

        assert False, "Never reach this line"


    def is_in_allowed_ranges(self, position):
        h = (position[0]**2 + position[1] ** 2) ** 0.5
        # Mitto is after the nucleos but before the cell border
        return (h >= self.areas[0] and h <= self.areas[2])

    def advance(self, state):
        """
        Move the Mito agent forward. Use velocity multiplied by time units to
        stablish the distance to move.

        """
        # TODO: Should we check collisions with other mitos?
        rads = state.direction
        position = [None, None]
        position[0] = (state.position[0] + np.math.cos(rads) *
                state.velocity * state.time_unit)

        position[1] = (state.position[1] + np.math.sin(rads) *
                state.velocity * state.time_unit)

        advanced = False
        if self.is_in_allowed_ranges(position):
            advanced = True
            return position, advanced
        return self.state.position, advanced

    def extTransition(self, inputs):
        """
        External Transition Function.
        """
        self.state.current_time += self.elapsed
        return self.state

    def intTransition(self):
        """
        Internal Transition Function.
        """
        self.state.current_time += self.state.ta
        old_state = self.state.state

        ff_condition_time = self.state.current_time > 0 and (self.state.current_time %
                self.parent.getContextInformation(ENVProps.RATE_FF) == 0)

        # If true then run the Fusion Fission cycle
        fusion_fision_condition = ff_condition_time

        if not fusion_fision_condition:
            # Move condition
            if (self.state.state == MitoStates.A):
                self.state.position, did_advance = self.advance(self.state)
                self.state.area = self.get_area_from_position(self.state.position)
                self.state.velocity = self.get_new_velocity(self.state)
                # According to nlogo code, first move then change direction
                self.state.direction = self.get_new_direction(self.state, did_advance)
                self.state.re_run = False
                return self.state
        else:
            # Fusion/Fission cycle. Check if it is in the first or second phase.
            if not self.state.re_run:
                # Phase 1, this is where all active mitochondrias try to fusion or fissionate.
                # In phase 2 the fusionated will catch up, The mitos that
                # requested FU/FI will revert to a normal state.
                if(self.state.state == MitoStates.A and\
                        self.parent.getContextInformation(ENVProps.SHOULDFUSION,
                                                mito_id=self.state.id)):
                    # If should fusion bump to phase2 straight away.
                    self.state.re_run = True
                    return self.state

                # Run fusion fission rules
                # If an active atomic model meets the fision conditions
                if (self.state.state == MitoStates.A):
                    self.state.re_run = True

                    if(random.random() <= Parameters.PROB_FISSION):
                        if (self.state.mass >= 2* Parameters.MASS_MIN):
                            # Fission rule
                            mass = self.state.mass
                            x_f = random.random()
                            min_mass_div_mass = (Parameters.MASS_MIN / mass)
                            m_1 = (x_f * (0.5 - min_mass_div_mass) + min_mass_div_mass) * mass
                            self.state.old_mass = mass
                            self.state.mass = m_1
                            self.state.requested_state = MitoRequestedStates.FI
                    # elif (random.random() <= (1 - Parameters.PROB_FISSION)):
                    else:
                        closest_mitos = self.parent.getContextInformation(ENVProps.NEIGHBOR,
                                position=self.state.position, mass=self.state.mass)
                        while(closest_mitos):
                            closest_mito = closest_mitos.pop()
                            if closest_mito:
                                assigned_for_fussion = self.parent.getContextInformation(ENVProps.SHOULDFUSION,
                                        mito_id=closest_mito.id)
                                if assigned_for_fussion:
                                    # Retry, cant fusion with this mito
                                    continue
                                if closest_mito.state == MitoStates.A and\
                                        closest_mito.requested_state == MitoRequestedStates.N:
                                    total_mass = self.state.mass + closest_mito.mass
                                    if total_mass <= Parameters.MASS_MAX:
                                        self.state.mass = total_mass
                                        self.state.requested_state = MitoRequestedStates.FU
                                        self.state.fusionated_with = closest_mito.id
                                        break
                    # else:
                    #     self.state.re_run = False
                    return self.state

                if (self.state.state == MitoStates.I):
                    # This is for the inactive models
                    parent_state = self.parent.getContextInformation(ENVProps.FI)
                    if parent_state:
                        self.state.mass = parent_state.old_mass - parent_state.mass
                        self.state.parent = parent_state.id
                        self.state.state = MitoStates.A
                        self.state.requested_state = MitoRequestedStates.N
                        self.state.re_run = False
                    return self.state
            else:
                # Phase2
                # Run the pending actions.
                # Run the checks of SHOULD FUSION / SHOULD FISSION dont run another
                # run of fission fussion
                self.state.re_run = False
                if self.state.requested_state in [MitoRequestedStates.FU,
                        MitoRequestedStates.FI]:
                    # It already fusionated/fissionated now it is a normal agent.
                    self.state.requested_state = MitoRequestedStates.N
                    self.state.state = MitoStates.A
                    return self.state

                if(self.parent.getContextInformation(ENVProps.SHOULDFUSION,
                                                mito_id=self.state.id)):
                    # Change internal state, send to the inactives queue.
                    self.state.state = MitoStates.I
                    self.state.requested_state = MitoRequestedStates.N
                    self.state.mass = 0
                    # TODO: Rethink this. It is upward whatever.
                    self.parent.getContextInformation(ENVProps.DIDFUSION,
                                                                mito_id=self.state.id)
                    return self.state


        return self.state

    def __lt__(self, other):
        return (self.state.state, self.state.re_run, self.state.id) < (other.state.state, other.state.re_run, other.state.id)

    def outputFnc(self):
        """
        The lambda output function

        """
        return {}

    def timeAdvance(self):
        """
        Time-Advance Function.
        """
        ta = None
        if self.state.re_run:
            ta = 0
        elif self.state.state == MitoStates.I:
            ta = self.parent.getContextInformation(ENVProps.RATE_FF)
        elif self.state.state == MitoStates.A:
            ta = self.parent.getContextInformation(ENVProps.RATE_MV)
        self.state.ta = ta

        return self.state.ta


class Cell(CoupledDEVS):
    def __init__(self, name=None):
        """
        A simple flocking system consisting
        """
        # Always call parent class' constructor FIRST:
        CoupledDEVS.__init__(self, name)
        self.conn = init_sqlite3(Parameters.DB_NAME)

        self.mass_total = Parameters.MASS_TOTAL

        self.agent_states = {}
        self.agent_states_list = []
        self.agent_states_dict = {}
        self.agents = []
        self.points = []

        self.model = NearestNeighbors(radius=Parameters.RADIUS)


        self.velocities = {"C": random.random() * 2 * Parameters.VEL_CYTOSOLIC,
                "P": random.random() * 2 * Parameters.VEL_PERINUCLEAR}

        # As seen in nlogo file:
        # set mito-step_far ( (2 * 0.5) / ds * dt ) ;; 0.5 um/s
        # set mito-step_close ( (2 * 0.22) / ds * dt ) ;; 0.22 um/s


        # Instantiate the agents while there is still Mito mass to assign.
        remaining_mass = self.mass_total
        agent_number = 0
        while not remaining_mass <= Parameters.MASS_MIN:
            # Instantiate the agent
            agent = Mito(self, name="mito %d" % agent_number, id=agent_number)

            # If the remaining mass is negative then we can't assign it to the last agent.
            if (remaining_mass - agent.state.mass) < 0:
                # but we know that it is bigger than MASS_MIN so asign it anyway
                agent.state.mass = remaining_mass
            remaining_mass -= agent.state.mass

            # Set agents initial state and save for initial stats.
            agent.state.state = MitoStates.A
            self.agent_states[agent_number] = agent.state.state

            # Add to the agents lists
            self.agents.append(agent)
            agent_number += 1
        self.mass_total = Parameters.MASS_TOTAL - remaining_mass

        self.agents_by_state = {}
        self.agents_by_state[MitoStates.A] = { agent.state.id: agent.state for agent in self.agents }

        # Instantiate the backup agents for fission and fusion.
        n_mito_agents = len(self.agents)

        inactives = []
        for i in range(n_mito_agents, n_mito_agents * 3):
            agent = Mito(self, name="mito %d" % i, id=i)
            agent.state.mass = 0
            agent.state.state = MitoStates.I
            agent.state.ta = Parameters.RATE_INACTIVE_FF_WAKE
            self.agent_states[i] = agent.state.state
            self.agents.append(agent)
            inactives.append(agent)

        # Just in case I need to access the inactive agents...
        self.agents_by_state[MitoStates.I] = { agent.state.id: agent.state for agent in inactives }

        for agent in self.agents:
            self.addSubModel(agent)

        for agent in self.agents:
            # Here we save the state for all agents so we have it logged in t=0
            state = agent.state
            self.agent_states_list.append(state.as_dict_values())

        # TODO: Maybe I should load  agents_by_state initially here.
        # Atributes for the context information
        self.inactive_models = []
        self.to_inactive = {}

        points = np.array([np.array(x.position) for x in self.agents_by_state[MitoStates.A].values()])
        self.model.fit(points)

    def saveChildrenState(self, state):
        super(Cell, self).saveChildrenState(state)

        # Maintain the old and new state to check the changes
        old_state = self.agent_states.get(state[0].id)
        new_state = state[0].state
        if old_state != new_state:
            self.agent_states[state[0].id] = state[0].state

        state_to_save = state[0].as_dict_values()
        state_to_save['duration'] = Parameters.DURATION
        state_to_save['retry'] = Parameters.RETRY
        state_to_save['fissionprob'] = Parameters.PROB_FISSION

        columns = ', '.join(state_to_save.keys())
        placeholders = ', '.join('?' * len(state_to_save))
        sql = 'INSERT OR REPLACE INTO mitostate ({}) VALUES ({})'.format(columns, placeholders)
        try:
            self.conn.cursor().execute(sql, state_to_save.values())
        except Exception as e:
            print("ERROR INSERTANDO %s" % e)

        # Maintain the list of the active agents. This is used to get the
        # points of the active agents.
        modified_agents_state_dict = self.agents_by_state.get(new_state, {})
        modified_agents_state_dict[state[0].id] = state[0]
        self.agents_by_state[new_state] = modified_agents_state_dict

        # remove from the old list.
        if old_state != new_state:
            del self.agents_by_state[old_state][state[0].id]

        points = np.array([np.array(x.position) for x in self.agents_by_state[MitoStates.A].values()])
        try:
            self.model.fit(points)
        except Exception as e:
            print("Empty Active agents list, wait until Fusion/Fission ends")

        if state[0].requested_state == MitoRequestedStates.FI:
            self.inactive_models.append(state[0])

        if state[0].requested_state == MitoRequestedStates.FU and\
                state[0].fusionated_with:
            self.to_inactive[state[0].fusionated_with] = True


    def getContextInformation(self, property, *args, **kwargs):
        super(Cell, self).getContextInformation(property)
        if(property == ENVProps.VELOCITIES):
            return self.velocities

        if(property == ENVProps.SHOULDFUSION):
            return self.to_inactive.get(kwargs['mito_id'], False)

        if(property == ENVProps.DIDFUSION):
            id_agent = kwargs['mito_id']
            self.to_inactive[id_agent] = False

        # TODO: Poner las nuevas properties
        if(property == ENVProps.NEIGHBOR):
            # FIXME: I should filter the inactives from the list.
            mass = kwargs['mass']
            position = kwargs["position"]
            neighbors = self.model.kneighbors([position], return_distance=True)
            distances = neighbors[0][0]

            # Ignore the case where it is alone.
            if len(distances) == 1:
                return

            # Ignore the point with distance zero
            # min_not_zero = np.min(distances[np.nonzero(distances)])
            # We want all points that are different than zero
            i_closest_in_res, = np.where(distances != 0)

            #i_closest_in_res = np.argmin(distances[np.nonzero(distances)])
            i_in_points_array = np.array(neighbors[1][0])[i_closest_in_res]
            try:
                models = np.array(self.agents_by_state[MitoStates.A].values())[i_in_points_array]
                filtered_models = []

                for model in models:
                    # radius_distance = 1 
                    radius_distance = 1 + (mass/2) + (model.mass/2)
                    if distance.euclidean(position, model.position) <= radius_distance:
                        filtered_models.append(model)
                return list(filtered_models)
            except Exception as e:
                raise e
            return

        if(property == ENVProps.AREAS):
            return (Parameters.RADIUS_NUCLEUS_END,
                    Parameters.RADIUS_PERINUCLEAR_END,
                    Parameters.RADIUS_CYTOSOLIC_END)

        if(property == ENVProps.RATE_MV):
            return Parameters.RATE_MV

        if(property == ENVProps.RATE_FF):
            return Parameters.RATE_FF

        if(property == ENVProps.FI):
            if self.inactive_models:
                return self.inactive_models.pop()
            return None

    def select(self, immChildren):
        """
        Choose a model to transition from all possible models.
        """
        immChildren.sort()
        return immChildren[0]
