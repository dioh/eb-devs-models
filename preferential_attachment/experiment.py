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

def fit_power(df, parameters):
    cnt = df.groupby('degree').mean().frequency.values
    deg = np.unique(df.degree.values)

    missing = np.setdiff1d(range(min(deg), max(deg)), deg)
    new_df = pd.DataFrame({'degree': missing, 'frequency': 0})

    df = df.append(new_df)

    popt, pcov = sc.optimize.curve_fit(func_powerlaw, deg, cnt, maxfev=5000)
    yajuste2 = func_powerlaw(np.array(deg), *popt)

    mean_freq = df.frequency.mean()
    degree_for_mean_freq = df.iloc[(df['frequency']-mean_freq).abs().argsort()[:1]].degree.to_list()[0]


    plt.figure(figsize=(12,8))
    yajuste2 = func_powerlaw(np.linspace(min(deg), max(deg), 50), *popt)
    sns.pointplot(x=np.linspace(min(deg), max(deg), 50), y=yajuste2)
    ax = sns.barplot(data=df, x='degree', y='frequency', color='gray')
    plt.axvline(degree_for_mean_freq, color='red')

    for ind, label in enumerate(ax.get_xticklabels()):
        if ind % 5 == 0:  # every 10th label is kept
            label.set_visible(True)
        else:
            label.set_visible(False)

    plt.xlabel('Degree')
    plt.ylabel('Frequency')
    
    plt.savefig('prueba_%s.png' % str(parameters))



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

DURATION = 10000
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

all_degree_dfs = []

def run_multiple_retries():
    Parameters.TOPOLOGY_FILE = 'topology/graph_n10.adj'
    global degrees_dfs
    global dfs

    for connect_to in [1, 2, 3]:
        Parameters.CONNECT_TO = connect_to
        for i in tqdm.tqdm(range(RETRIES)):
            run_single(retry=i)
        df = pd.concat(dfs)
        fit_power(df, connect_to)
        dfs = []

        degrees_df = pd.concat(degrees_dfs)
        degrees_df.columns = ['Time', 'Average Degree', 'sd_deg', 'num_nodes', 'Connect To', 'retry']
        all_degree_dfs.append(degrees_df)

        plt.figure(figsize=(12,8))
        sns.relplot(x='Time', y='Average Degree',  data=degrees_df[degrees_df['Time'] % 10 == 0], kind='line')

        plt.savefig('pruebadegs_%s.png' % connect_to)
        degrees_dfs = []



run_multiple_retries()
degrees_df = pd.concat(all_degree_dfs)
degrees_df.columns = ['Time', 'Average Degree', 'sd_deg', 'num_nodes', 'Connect To', 'retry']
degrees_df['Connect To'] = degrees_df['Connect To'].astype('category')

plt.figure(figsize=(12,8))
sns.relplot(x='Time', y='Average Degree',
       data=degrees_df[(degrees_df['Time'] % 10 == 0)], kind='line', hue='Connect To')
plt.tight_layout()

plt.savefig('pruebadegs_all.png')

#    ======================================================================

# 5. (optional) Extract data from the simulated model
# print("Simulation terminated with traffic light in state %s" % (trafficSystem.trafficLight.state.get()))
