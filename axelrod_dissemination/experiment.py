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
from multiprocessing import Pool
import multiprocessing
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

DURATION =2
RETRIES = 11


def run_single(retry=0):
    environ = Environment(name='Env')
    sim = Simulator(environ)
    sim.setTerminationTime(DURATION)
    sim.setClassicDEVS()
    sim.setVerbose(None)
    sim.simulate()
    dataframe = pd.DataFrame(environ.agents[-1].stats)
    dataframe['retry'] = retry
    dataframe['Fashion Rate'] = Parameters.FASHION_RATE
    tmpfile = tempfile.NamedTemporaryFile(mode='w', prefix='/tmp/axelrod_model', delete=False)
    dataframe.to_csv(tmpfile, header=False, index=False)

    topology_name = os.path.basename(Parameters.TOPOLOGY_FILE)
    outfilename = "results/axelrod_%s_F_%s_Q_%s_retry_%d_fashion_%.2f.gml" % (topology_name, Parameters.CULTURE_LENGTH,Parameters.TRAITS, retry, Parameters.FASHION_RATE)

    str_cultures = {str(id):str(cult) for id, cult in environ.cultures.items()}
    nx.set_node_attributes(environ.G, str_cultures, "culture")
    nx.write_gml(environ.G, outfilename)
    return dataframe

    # states = [(ag.state.id, ag.state.infected, ag.state.infected_time, ag.state.infected_end_time) for ag in environ.agents[:-1] if ag.state.infected_time > -1]
    # outfilenamestates = "results/sir_model_%s_emergence_%s_rt.csv" % (topology_name, Parameters.EMERGENT_MODEL)
    # pd.DataFrame(states).to_csv(outfilenamestates)

FASHIONS = [0, 0.25, 0.5, 0.75, 1]

def lambda_prop(parameters): 
    Parameters.FASHION_RATE = parameters[1]
    return run_single(parameters[0])

def run_multiple_retries():
    Parameters.TOPOLOGY_FILE = 'topology/lattice.adj'

    Parameters.CULTURE_LENGTH = 5
    Parameters.TRAITS = 5

    usable_cpu_count = multiprocessing.cpu_count() - 2
    parameters = itertools.product(range(RETRIES), FASHIONS)

    for i in tqdm.tqdm(range(RETRIES)):
        run_single(retry=i)

    pool =  Pool(usable_cpu_count) 
    # pool_prop_res = []
    # for r in tqdm.tqdm(pool.imap_unordered(lambda_prop, parameters), total=len(list(parameters))):
    #     pool_prop_res.append(r)
    pool_prop_res = pool.map(lambda_prop, parameters)
    # pool_prop_res = []
    # for i, fashion_rate in tqdm.tqdm(itertools.product(range(RETRIES), FASHIONS)):
    #     Parameters.FASHION_RATE = fashion_rate
    #     pool_prop_res.append(run_single(retry=i))

    topology_name = os.path.basename(Parameters.TOPOLOGY_FILE)
    outfilename = "results/axelrod_%s_F_%s_Q_%s_retries_%d.csv" % (topology_name, Parameters.CULTURE_LENGTH,Parameters.TRAITS, RETRIES)

    if not os.path.exists("results"):
        os.mkdir("results")

    output_columns = ['Time', 'Number of Cultures',  'retry', 'Fashion Rate']
    data = pd.concat(pool_prop_res)
    data.columns = output_columns
    data.to_csv(outfilename, header=True, index=False)

    filtered_data = data[(data.Time % 10 == 0)]
    plt.figure(figsize=(12,8))

    ax = sns.pointplot(x="Time", y="Number of Cultures", data=filtered_data,
            ci="sd", capsize=.2, dodge=True, hue='Fashion Rate')

    for ind, label in enumerate(ax.get_xticklabels()):
        if ind % 5 == 0:  # every 10th label is kept
            label.set_visible(True)
        else:
            label.set_visible(False)
    # ax.set_xticklabels(ax.get_xticklabels(), rotation=45)
    fig_filename = outfilename.replace('csv', 'png')
    ax.get_figure().savefig(fig_filename)

run_multiple_retries()

#    ======================================================================

# 5. (optional) Extract data from the simulated model
# print("Simulation terminated with traffic light in state %s" % (trafficSystem.trafficLight.state.get()))
