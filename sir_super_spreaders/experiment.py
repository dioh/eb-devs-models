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
from matplotlib import pyplot as plt
# Import the model to be simulated
from model import Environment, Parameters
import numpy as np


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
import networkx as nx
import seaborn as sns
# from SIRSS_numeric import sir_num

SMALL_SIZE = 16
MEDIUM_SIZE = 20
BIGGER_SIZE = 24

plt.rc('font', size=SMALL_SIZE)          # controls default text sizes
plt.rc('axes', titlesize=SMALL_SIZE)     # fontsize of the axes title
plt.rc('axes', labelsize=MEDIUM_SIZE)    # fontsize of the x and y labels
plt.rc('xtick', labelsize=SMALL_SIZE)    # fontsize of the tick labels
plt.rc('ytick', labelsize=SMALL_SIZE)    # fontsize of the tick labels
plt.rc('legend', fontsize=SMALL_SIZE)    # legend fontsize
plt.rc('figure', titlesize=BIGGER_SIZE)

DURATION = 4
RETRIES = 30
output_columns = ['t','I','S','R','retry']

dfs = []
def run_single(retry=0):
    global dfs
    environ = Environment(name="SIR over CM")
    sim = Simulator(environ)
    initial_states = [(ag.state.name, ag.state.state, 0) for ag in environ.agents] 
    sim.setTerminationTime(DURATION)
    sim.setClassicDEVS()
    sim.setDSDEVS(True)
    topology_name = os.path.basename(Parameters.TOPOLOGY_FILE)
    # sim.setVerbose(None)
    sim.simulate()
    dataframe = pd.DataFrame(environ.log_agent.stats)
    dataframe.columns = ['t','I', 'S', 'R']
    dataframe['retry'] = retry
    dataframe['Quarantine Threshold'] = Parameters.QUARANTINE_THRESHOLD
    dataframe['Quarantine Acceptance'] = Parameters.QUARANTINE_ACCEPTATION
    tmpfile = tempfile.NamedTemporaryFile(mode='w', prefix='sir_model', delete=False)
    dataframe.to_csv(tmpfile, header=False, index=False)
    outfilename = "results/pa_model_dynamic_graph_%s.gml" % (topology_name)
    nx.write_gml(environ.G, outfilename)
    dfs.append(dataframe)

def run_multiple_retries():
    Parameters.TOPOLOGY_FILE = 'grafos_ejemplo/grafo_vacio'

    topology_name = os.path.basename(Parameters.TOPOLOGY_FILE)
    for i in range(RETRIES):
        run_single(retry=i)

for i in [1]: #, 0.10, 0.40]:
    Parameters.QUARANTINE_THRESHOLD = i  
    Parameters.QUARANTINE_ACCEPTATION = i
    run_multiple_retries()

data = pd.concat(dfs)
data.to_csv('paraNumeric.csv')

aux = data.groupby('retry').max().reset_index()
aux = aux[(aux.R > 50)]
data = data[data.retry.isin(aux.retry)]
data_melteada = pd.melt(data, id_vars=['t', 'retry', 'Quarantine Threshold', 'Quarantine Acceptance'], value_vars=['I', 'S', 'R'])

data_melteada['value'] = data_melteada['value'] / float(300)
data_melteada = data_melteada.rename(columns={'variable': 'State', 't': 'Time', 'value': 'Proportion'})

fig, ax =plt.subplots(figsize=(12, 14))
colors=["#FF0B04","#4374B3","#228800"]
sns.set_palette(sns.color_palette(colors))
sns.lineplot(data=data_melteada, x='Time', y='Proportion', hue='State', style='Quarantine Acceptance',  ax=ax,color=['r','g','b'])#, ci=None)

plt.setp(ax,yticks=np.arange(0, 1.01, 0.10))
#plt.legend()
plt.legend(bbox_to_anchor=( 0., 1.02,1.,.102),loc=3,ncol=2, mode="expand",borderaxespad=0.,title='SIR with Quarantine') #, borderaxespad=0.)
plt.tight_layout()
plt.savefig('agent_new_2.png', bbox_inches='tight')

#BETA_PROB = 10 RHO_PROB = 0.9
#T,dt,EK,g,b,lamb,pob
    
#    ======================================================================

# 5. (optional) Extract data from the simulated model
# print("Simulation terminated with traffic light in state %s" % (trafficSystem.trafficLight.state.get()))
