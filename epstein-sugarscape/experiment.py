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
from matplotlib import pyplot as plt

SMALL_SIZE = 12
MEDIUM_SIZE = 16
BIGGER_SIZE = 20

plt.rc('font', size=SMALL_SIZE)          # controls default text sizes
plt.rc('axes', titlesize=SMALL_SIZE)     # fontsize of the axes title
plt.rc('axes', labelsize=MEDIUM_SIZE)    # fontsize of the x and y labels
plt.rc('xtick', labelsize=SMALL_SIZE)    # fontsize of the tick labels
plt.rc('ytick', labelsize=SMALL_SIZE)    # fontsize of the tick labels
plt.rc('legend', fontsize=SMALL_SIZE)    # legend fontsize
plt.rc('figure', titlesize=BIGGER_SIZE)



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
RETRIES = 10

def run_single(retry=0):
    environ = Environment(name='Env')
    sim = Simulator(environ)
    sim.setTerminationTime(DURATION)
    #sim.setTerminationCondition(environ.termination)
    sim.setClassicDEVS()
    sim.simulate()

    return environ.log_agent

def run_multiple_retries():
    stats = []
    for i in tqdm.tqdm(range(RETRIES)):
        logA = run_single(retry=i)

        stats.append( logA.stats )

    params = "POPULATION_SIZE: %d\n" % model.Parameters.POPULATION_SIZE
    params+= "GRID_SIZE: (%d,%d)\n" % model.Parameters.GRID_SIZE
    params+= "INITIAL_WEALTH: U(%.1f,%.1f)\n" % model.Parameters.INITIAL_WEALTH
    params+= "METABOLIC_RATE: U(%.1f,%.1f)\n" % model.Parameters.METABOLIC_RATE
    params+= "VISION: U(%.1f,%.1f)\n" % model.Parameters.VISION


    t, p, g = zip(* stats[0])
    avgs = [ np.average([ stats[j][i][2] for j in range(len(stats)) if i<len(stats[j]) ]) for i in range(len(stats[0])) ]
    stds = [ np.std([ stats[j][i][2] for j in range(len(stats)) if i<len(stats[j]) ]) for i in range(len(stats[0])) ]
    plt.errorbar( t, avgs, yerr=stds, label="Gini Threshold: %.1f " % model.Parameters.GINI_THRESH )

    return params

fig, ax = plt.subplots()

for gt in [0.2, 0.3, 0.4, 0.5, 0.7, 1.0]:
    model.Parameters.GINI_THRESH = gt
    params = run_multiple_retries()

plt.legend(loc="upper right", ncol=2)
plt.xlabel("Time")
plt.xlim((0,500))
plt.ylabel("Gini coefficient")
# plt.ylim((0.15,0.6))
# plt.ylim((0,1))
plt.yticks(np.arange(0.15, 0.65, 0.05))
#plt.ylabel("Population",fontsize=35)
#plt.ylim((250,400))
# plt.xticks(fontsize=25)
# plt.yticks(fontsize=25)
plt.tight_layout()
outfile = "results/epstein-%d" % model.Parameters.POPULATION_SIZE
outfile+= "-%d_%d" % model.Parameters.GRID_SIZE
outfile+= "-%d_%d" % model.Parameters.INITIAL_WEALTH
outfile+= "-%d_%d" % model.Parameters.METABOLIC_RATE
outfile+= "-%d_%d" % model.Parameters.VISION
plt.savefig(outfile)
plt.show()


