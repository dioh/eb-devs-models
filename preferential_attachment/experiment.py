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
import collections
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

import numpy as np
import scipy as sc
from scipy import interpolate
from scipy import optimize
import pandas as pd


def create_nodes_degrees_df(environ, retry):
    nodes = []
    degrees = []
    for n, d in environ.G.degree():
        nodes.append(n)
        degrees.append(d)
    degree_sequence = sorted(degrees, reverse=True)  # degree sequence
    degreeCount = collections.Counter(degree_sequence)
    deg, cnt = zip(*degreeCount.items())

    df = pd.DataFrame({'degree':deg, 'frequency':cnt, 'retry':retry})

    return df


def func(x,b, c):
    return x*b +c

def eval_func(x, b, c):
    return np.exp(x*b + c)

def func_powerlaw(x,  m, c):
        return  x**m * c

def fit_power(df):

    cnt = df.groupby('degree').mean().frequency.values
    deg = np.unique(df.degree.values)

    popt, pcov = sc.optimize.curve_fit(func_powerlaw, deg, cnt, maxfev=5000)
    yajuste2 = func_powerlaw(np.array(deg), *popt)

    plt.figure(figsize=(12,8))
    yajuste2 = func_powerlaw(np.linspace(min(deg), max(deg), 50), *popt)
    sns.pointplot(x=np.linspace(min(deg), max(deg), 50), y=yajuste2)
    sns.barplot(data=df, x='degree', y='frequency', color='gray')

    print(popt)

    plt.xlabel('Degree')
    plt.ylabel('Frequency')
    
    plt.savefig('prueba.png')



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

DURATION = 100000
RETRIES = 10


dfs = []
degrees_dfs = []


def run_single(retry=0):
    environ = Environment(name='Env')
    sim = Simulator(environ)
    sim.setTerminationTime(DURATION)
    sim.setClassicDEVS()
    sim.setDSDEVS(True)

    sim.setSchedulerMinimalList() 

    sim.simulate()
    dataframe = pd.DataFrame(environ.agents[-1].stats)
    dataframe['connect_to'] = Parameters.CONNECT_TO
    dataframe['retry'] = retry
    degrees_dfs.append(dataframe)

    topology_name = os.path.basename(Parameters.TOPOLOGY_FILE)

    outfilename = "results/pa_model_dynamic_graph_%s.gml" % (topology_name)
    nx.write_gml(environ.G, outfilename)
    fig_filename = outfilename.replace('gml', 'png')

    dfs.append(create_nodes_degrees_df(environ, retry))


def run_multiple_retries():
    Parameters.TOPOLOGY_FILE = 'topology/graph_n10.adj'

    for connect_to in [1]: #, 2, 3]:
        Parameters.CONNECT_TO = connect_to
        for i in tqdm.tqdm(range(RETRIES)):
            run_single(retry=i)

    df = pd.concat(dfs)
    fit_power(df)

    degrees_df = pd.concat(degrees_dfs)
    degrees_df.columns = ['t', 'avg_deg', 'sd_deg', 'num_nodes', 'connect_to', 'retry']

    plt.figure(figsize=(12,8))
    sns.relplot(x='t', y='avg_deg', kind='line', hue='connect_to', data=degrees_df)

    plt.savefig('pruebadegs.png')



run_multiple_retries()

#    ======================================================================

# 5. (optional) Extract data from the simulated model
# print("Simulation terminated with traffic light in state %s" % (trafficSystem.trafficLight.state.get()))
