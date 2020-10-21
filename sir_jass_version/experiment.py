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
import progressbar
import pandas as pd
import fileinput
import tempfile
import fnmatch
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

DURATION = 500
RETRIES = 2
output_columns = ['t','S','I','R','E','V', 'retry']

def run_single(retry=0):
    environ = Environment(name="SIR over CM")
    sim = Simulator(environ)
    initial_states = [(ag.state.name, ag.state.state, 0) for ag in environ.agents] 
    sim.setTerminationTime(DURATION)
    sim.setClassicDEVS()
    sim.setDSDEVS(True)
    # sim.setVerbose(None)
    sim.simulate()
    dataframe = pd.DataFrame(environ.stats)
    dataframe['retry'] = retry
    tmpfile = tempfile.NamedTemporaryFile(mode='w', prefix='sir_model', delete=False)
    dataframe.to_csv(tmpfile, header=False, index=False)
    # dataframe.to_csv("results_%s_emergence_%s_retry_%d.csv" % (Parameters.TOPOLOGY_FILE, Parameters.EMERGENT_MODEL, retry), header=False)


def run_multiple_retries():
    Parameters.TOPOLOGY_FILE = 'grafos_ejemplo/graph_tp'
    # TOPOLOGY_FILE,
    # N,
    # INITIAL_PROB,
    # INFECT_PROB,
    # BETA_PROB,
    # RHO_PROB,
    # RECOV_THRHLD,
    for i in progressbar.progressbar(range(RETRIES)):
        run_single(retry=i)

    filenames = [os.path.join("/tmp", f) for f in fnmatch.filter(os.listdir('/tmp'), 'sir_model*')]
    topology_name = os.path.basename(Parameters.TOPOLOGY_FILE)
    outfilename = "results/sir_model_%s_emergence_%s_retries_%d.csv" % (topology_name, Parameters.EMERGENT_MODEL, RETRIES)
    fin = fileinput.input(filenames)
    with open(outfilename, 'w') as fout:
        fout.write(",".join(output_columns))
        fout.write('\n')

        for line in fin:
            fout.write(line)

    fin.close()
    for file in filenames: os.remove(file)


run_multiple_retries()

#    ======================================================================

# 5. (optional) Extract data from the simulated model
# print("Simulation terminated with traffic light in state %s" % (trafficSystem.trafficLight.state.get()))
