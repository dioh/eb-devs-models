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
import itertools
import pandas as pd
import tqdm
import itertools

# Import the model to be simulated
from model import Cell, Parameters


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
#    being reached.)
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
import numpy as np
import random


# from pypdevs.minimal import Simulator
from pypdevs.simulator import Simulator

def run_single():
    environ = Cell(name="Mitto Fi Fu")
    sim = Simulator(environ)
    sim.setTerminationTime(DURATION)
    sim.setClassicDEVS()
    # sim.setVerbose(None)
    # sim.setSchedulerDiscreteTime()
    sim.setSchedulerMinimalList()

    sim.simulate()
    pd.concat({ k: pd.DataFrame.from_dict(v, 'index') for k, v in environ.agent_states_dict.items()}, axis=0).\
        to_csv("xperiment_prob_fission_%.2f.csv" % model.Parameters.PROB_FISSION)


RETRIES = 1
FF_CICLES = 12

def run_multiple():
    # parameters_comb_list = [{"PROB_FISSION": 0.5}, {"PROB_FISSION": 0.8}]
    parameters_comb_list = [
            {"PROB_FISSION": 0.2, "RATE_INACTIVE_FF_WAKE":300, "RATE_FF":300},
            {"PROB_FISSION": 0.5, "RATE_INACTIVE_FF_WAKE":300,"RATE_FF": 300},
            {"PROB_FISSION": 0.8, "RATE_INACTIVE_FF_WAKE":300, "RATE_FF":300},
            # {"PROB_FISSION": 0, "RATE_INACTIVE_FF_WAKE":300,"RATE_FF": 300},
            # {"PROB_FISSION": 1, "RATE_INACTIVE_FF_WAKE":300,"RATE_FF": 300}
            ]

    run_combinations = list(itertools.product(parameters_comb_list, range(1, 1+ RETRIES)))
    for params, retry in tqdm.tqdm(run_combinations):
        for k, v in params.items():
            setattr(model.Parameters, k, v)
        DURATION = FF_CICLES * Parameters.RATE_FF
        setattr(model.Parameters, "DURATION", DURATION)
        setattr(model.Parameters, "RETRY", retry)
        environ = Cell(name="Mitto Fi Fu")
        sim = Simulator(environ)
        sim.setTerminationTime(Parameters.DURATION)
        sim.setClassicDEVS()
        # sim.setVerbose(None)
        # sim.setSchedulerDiscreteTime()
        sim.setSchedulerMinimalList()
        sim.simulate()
        environ.conn.commit()
        environ.conn.close()

run_multiple()

# Extract from the sqlite file the aggregated data: 
conn = model.init_sqlite3("mito_experiment.sqlite")
cursor = conn.cursor()
cursor.execute("""
select mitostate.currenttime,
 mitostate.fissionprob,
 mitostate.state,
 mitostate.retry,
 sum(mitostate.mass)/300 as perc,
  ms2.mass_group,
  mitostate.duration
from (select id, currenttime, duration, retry, fissionprob, rerun,
     (case when mass between 0 and 1 then 'small'
    when mass between 1 and 2 then 'medium'
    when mass between 2 and 3 then 'large' end) as mass_group from mitostate) as ms2 
inner join mitostate on mitostate.id=ms2.id and
mitostate.currenttime = ms2.currenttime and
mitostate.duration = ms2.duration and
mitostate.retry = ms2.retry and
mitostate.fissionprob = ms2.fissionprob and
mitostate.rerun = ms2.rerun
where 
mitostate.id = ms2.id and 
state != 'Inactive' and
mitostate.rerun = 0
group by mitostate.fissionprob,
 mitostate.retry,
 mitostate.currenttime,
 mitostate.duration,
ms2.mass_group;
""")

import csv
rows = cursor.fetchall()
filename = "experiment_cicles_%d_retries_%d_duration.csv"  % (FF_CICLES, RETRIES,)
csvWriter = csv.writer(open(filename, "w"))
csvWriter.writerows(rows)

event_count = """select currenttime, fissionprob, retry, duration,
requestedstate, count(1) from mitostate where requestedstate != 'None' and
state != 'Inactive' GROUP BY currenttime, fissionprob, duration, retry, requestedstate;"""
cursor.execute(event_count)

rows = cursor.fetchall()
filename = "experiment_events_%d_retries_%d_duration.csv"  % (FF_CICLES, RETRIES,)
csvWriter = csv.writer(open(filename, "w"))
csvWriter.writerows(rows)



#    ======================================================================

# 5. (optional) Extract data from the simulated model
# print("Simulation terminated with traffic light in state %s" % (trafficSystem.trafficLight.state.get()))
