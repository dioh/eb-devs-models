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
import tqdm
import pandas as pd
import networkx as nx
import fileinput
import tempfile
import fnmatch
import shutil
import numpy as np
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

DURATION = 100
RETRIES = 1

output_columns = ['t'] + model.SIRStates.__dict__.keys() + ['retry']

def run_single(retry=0):
    environ = Environment(name="SIR over CM")
    sim = Simulator(environ)
    sim.setTerminationTime(DURATION)
    sim.setClassicDEVS()
    # sim.setVerbose(None)
    sim.simulate()
    dataframe = pd.DataFrame(environ.agents[-1].stats)
    dataframe['retry'] = retry
    tmpfile = tempfile.NamedTemporaryFile(mode='w', prefix='/tmp/csv_sir_model', delete=False)
    dataframe.to_csv(tmpfile, header=False, index=False)

    topology_name = os.path.basename(Parameters.TOPOLOGY_FILE)

    outfilename = "results/sir_model_%s_emergence_%s_graph.gml" % (topology_name, Parameters.EMERGENT_MODEL)
    nx.write_gml(environ.G, outfilename)

    states = [(ag.state.id, ag.state.infected, ag.state.infected_time, ag.state.infected_end_time) for ag in environ.agents[:-1] if ag.state.infected_time > -1]
    outfilenamestates = "results/sir_model_%s_emergence_%s_rt.csv" % (topology_name, Parameters.EMERGENT_MODEL)
    pd.DataFrame(states).to_csv(outfilenamestates)


def run_multiple_retries():
    Parameters.TOPOLOGY_FILE = 'grafos_ejemplo/grafo_prueba.gml'
    Parameters.EMERGENT_MODEL = False

    Parameters.NU = 50
    Parameters.THETA = 20
    Parameters.A = Parameters.NU
    Parameters.B = 0
    Parameters.CI = 10
    Parameters.CV = 1
    # Other available parameters:
    # Parameters.N
    # Parameters.INITIAL_PROB
    # Parameters.INFECT_PROB
    # Parameters.BETA_PROB
    # Parameters.RHO_PROB
    # Parameters.RECOV_THRHLD
    for i in tqdm.tqdm(range(RETRIES)):
        run_single(retry=i)

    filenames = [os.path.join("/tmp", f) for f in fnmatch.filter(os.listdir('/tmp'), 'csv_sir_model*')]
    topology_name = os.path.basename(Parameters.TOPOLOGY_FILE)
    outfilename = "results/sir_model_%s_emergence_%s_retries_%d.csv" % (topology_name, Parameters.EMERGENT_MODEL, RETRIES)
    fin = fileinput.input(filenames)

    if not os.path.exists("results"):
        os.mkdir("results")

    with open(outfilename, 'w') as fout:
        fout.write(",".join(output_columns))
        fout.write('\n')


    with open(outfilename, 'ab') as fout:
        for filename in filenames:
            with open(filename, 'rb') as readfile:
                shutil.copyfileobj(readfile, fout)

    for file in filenames: os.remove(file)


run_multiple_retries()

#    ======================================================================

# 5. (optional) Extract data from the simulated model
# print("Simulation terminated with traffic light in state %s" % (trafficSystem.trafficLight.state.get()))
