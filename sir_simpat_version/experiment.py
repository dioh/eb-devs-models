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

# Import code for model simulation:
from pypdevs.simulator import Simulator
import itertools
import progressbar
import pandas as pd

# Import the model to be simulated
from model import Environment, Parameters


#    ======================================================================

# 1. Instantiate the (Coupled or Atomic) DEVS at the root of the 
#  hierarchical model. This effectively instantiates the whole model 
#  thanks to the recursion in the DEVS model constructors (__init__).
#

#    ======================================================================

# 2. Link the model to a DEVS Simulator: 
#  i.e., create an instance of the 'Simulator' class,
#  using the model as a parameter.

#    ======================================================================

# 3. Perform all necessary configurations, the most commonly used are:

# A. Termination time (or termination condition)
#    Using a termination condition will execute a provided function at
#    every simulation step, making it possible to check for certain states
#    being reached.
#    It should return True to stop simulation, or Falso to continue.
# def terminate_whenStateIsReached(clock, model):
#     return model.trafficLight.state.get() == "manual"
# sim.setTerminationCondition(terminate_whenStateIsReached)

#    A termination time is prefered over a termination condition,
#    as it is much simpler to use.
#    e.g. to simulate until simulation time 400.0 is reached

# B. Set the use of a tracer to show what happened during the simulation run
#    Both writing to stdout or file is possible:
#    pass None for stdout, or a filename for writing to that file
# sim.setVerbose(None)

# C. Use Classic DEVS instead of Parallel DEVS
#    If your model uses Classic DEVS, this configuration MUST be set as
#    otherwise errors are guaranteed to happen.
#    Without this option, events will be remapped and the select function
#    will never be called.

#    ======================================================================

import model

DURATION = 1000

def run_single():
    environ = Environment(name="SIR over CM")
    sim = Simulator(environ)
    initial_states = [(ag.state.name, ag.state.state, 0) for ag in environ.agents] 
    # sim.setTerminationTime(DURATION)
    sim.setClassicDEVS()
    # sim.setVerbose(None)
    sim.simulate()
    pd.DataFrame(environ.stats, columns=[ 't', "S", "I", "R", "E"]).to_csv("results_%s.csv" % Parameters.TOPOLOGY_FILE)

run_single()

def run_multiple():
    topo = ['grafo']
    n = [10]
    init_prob=[0.1]

    keys = [
            TOPOLOGY_FILE,
            N,
            INITIAL_PROB,
            INFECT_PROB,
            BETA_PROB,
            RHO_PROB,
            RECOV_THRHLD,
            ]

    combinaciones = itertools.product(cohere_cap_p, separate_p, dist_p, 
            radius_p, align_p, cohere_p, supercohere_p)

    parameters_comb_list = [dict(zip(keys, comb)) for comb in combinaciones]


    for params in progressbar.progressbar(parameters_comb_list):

        for k, v in params.items():
            setattr(model.Parameters, k, v)

        flocks = Flock(name="Flocking")
        sim = Simulator(flocks)
        sim.setTerminationTime(DURATION)
        sim.setClassicDEVS()
        sim.simulate()

        filename = ('~/proj/crazydevs/results/historial_flocks_g{0[GRID_SIZE]:d}'
                '_r{0[RADIUS]:d}_d{0[MAX_DIST]:0.1f}'
                '_ac{0[ANTICOHERE_CAP]:d}_septurn{0[MAX_SEPARATE_TURN]:0.2f}'
                '_alignturn{0[MAX_ALIGN_TURN]:0.2f}'
                '_cohturn{0[MAX_COHERE_TURN]:0.2f}'
                '_supercohere{0[SUPERCOHERE_CAP]:0.2f}'
                '.csv'.format(model.Parameters.__dict__))

        flocks.history.to_csv(filename)
#    ======================================================================

# 5. (optional) Extract data from the simulated model
# print("Simulation terminated with traffic light in state %s" % (trafficSystem.trafficLight.state.get()))
