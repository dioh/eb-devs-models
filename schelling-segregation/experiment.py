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
import os
import pandas as pd
import tqdm
import networkx as nx
import fileinput
import tempfile
import fnmatch
import shutil
import numpy as np
import seaborn as sns
from matplotlib import pyplot as plt
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

DURATION = 5000
RETRIES = 10

def run_single(retry=0):
    environ = Environment(name="Env%d"%retry)
    sim = Simulator(environ)
    sim.setTerminationTime(DURATION)
    sim.setTerminationCondition(environ.termination)
    sim.setClassicDEVS()
    sim.simulate()

    return environ.log_agent

def run_multiple_retries():
    Parameters.TOPOLOGY_FILE = 'topology/lattice.adj'

    stats = []
    for i in tqdm.tqdm(range(RETRIES)):
        logA = run_single(retry=i)

        stats.append( logA.stats )

    params = "POPULATION_SIZE: %d\n" % model.Parameters.POPULATION_SIZE
    params+= "GRID_SIZE: (%d,%d)\n" % model.Parameters.GRID_SIZE
    params+= "RED_PROBABILITY: %.2f\n" % model.Parameters.RED_PROBABILITY

    avgs = [ 100*np.average([ stats[j][i][1] for j in range(len(stats)) if i<len(stats[j]) ]) for i in range(len(stats[0])) ]
    stds = [ 100*np.std([ stats[j][i][1] for j in range(len(stats)) if i<len(stats[j]) ]) for i in range(len(stats[0])) ]

    x, y = zip(* stats[0])
    plt.errorbar( x, avgs, yerr=stds, label="%.2f" % model.Parameters.HAPPINESS_THRESHOLD )

    return params

fig, ax = plt.subplots()

model.Parameters.POPULATION_SIZE = 200
for ht in [0.20,0.35,0.50,0.65,0.80,0.95]:
	model.Parameters.HAPPINESS_THRESHOLD = ht
	run_multiple_retries()

plt.legend(loc="upper right", fontsize=15, ncol=2)
plt.xlim((0,40))
plt.ylim((0,100))
plt.xticks(fontsize=25)
plt.yticks(fontsize=25)
plt.xlabel("Time", fontsize=35)
plt.ylabel("Unhappy agents (%)", fontsize=35)
plt.tight_layout()
plt.savefig("results/scheling-%d-%d-%d-%.2f-%.2f.png" % (model.Parameters.POPULATION_SIZE, model.Parameters.GRID_SIZE[0], model.Parameters.GRID_SIZE[1], model.Parameters.RED_PROBABILITY, model.Parameters.HAPPINESS_THRESHOLD))
plt.show()

