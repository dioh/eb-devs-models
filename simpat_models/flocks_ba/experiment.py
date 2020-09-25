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
import os
import tempfile
import fnmatch
import fileinput

# Import the model to be simulated
from model import Flock


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

DURATION = 250
RETRIES = 20

cohere_cap_p = [-1]
separate_p= [0.03]#, 0.05]
dist_p = [1.5]#, 1.5]
radius_p = [5]#, 7]
align_p = [0.09]
cohere_p = [0.06] #, 0.03]
supercohere_p = [25]

keys = [
        "ANTICOHERE_CAP",
        "MAX_SEPARATE_TURN",
        "MAX_DIST",
        "RADIUS",
        "MAX_ALIGN_TURN",
        "MAX_COHERE_TURN",
        "SUPERCOHERE_CAP",
        ]

combinaciones = itertools.product(cohere_cap_p, separate_p, dist_p, 
        radius_p, align_p, cohere_p, supercohere_p)

parameters_comb_list = [dict(zip(keys, comb)) for comb in combinaciones]


output_columns = ['bird', 'x', 'y', 'heading', 't', 'cluster', 'neighbors', 'cm_x', 'cm_y', 'behavior_type', 'retry']


def run_single(retry=0): 
    for params in parameters_comb_list: 
        for k, v in params.items():
            setattr(model.Parameters, k, v)

        flocks = Flock(name="Flocking")
        sim = Simulator(flocks)
        sim.setTerminationTime(DURATION)
        sim.setClassicDEVS()
        sim.simulate()

        dataframe = flocks.history
        dataframe['retry'] = retry
        tmpfile = tempfile.NamedTemporaryFile(mode='w', prefix='flocking_model', delete=False)
        dataframe.to_csv(tmpfile, header=False, index=False)


def run_multiple_retries():
    for i in progressbar.progressbar(range(RETRIES)):
        run_single(retry=i)

    filenames = [os.path.join("/tmp", f) for f in fnmatch.filter(os.listdir('/tmp'), 'flocking_model*')]

    outfilename = ('results/historial_flocks_g{0[GRID_SIZE]:d}'
            '_r{0[RADIUS]:d}_d{0[MAX_DIST]:0.1f}'
            '_ac{0[ANTICOHERE_CAP]:d}_septurn{0[MAX_SEPARATE_TURN]:0.2f}'
            '_alignturn{0[MAX_ALIGN_TURN]:0.2f}'
            '_cohturn{0[MAX_COHERE_TURN]:0.2f}'
            '_supercohere{0[SUPERCOHERE_CAP]:0.2f}'
            '.csv'.format(model.Parameters.__dict__))

    fin = fileinput.input(filenames)
    with open(outfilename, 'w') as fout:
        __import__('pdb').set_trace()
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
