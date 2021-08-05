# Import the model to be simulated
from model import Environment, Parameters
import model

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
from model import Environment, Parameters
import model


def run_single(duration, retry=0):
    environ = Environment(name='Env')
    sim = Simulator(environ)
    sim.setTerminationTime(duration)
    sim.setClassicDEVS()
    sim.simulate()
    dataframe = pd.DataFrame(environ.agents[-1].stats)
    dataframe['retry'] = retry
    dataframe['Fashion Rate'] = Parameters.FASHION_RATE
    output_columns = ['Time', 'Number of Cultures',  'retry', 'Fashion Rate']
    dataframe.columns = output_columns 
    return dataframe

def plot(data):
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
    filtered_data = data[(data.Time % 10 == 0)]
    plt.figure(figsize=(12,8))

    ax = sns.pointplot(x="Time", y="Number of Cultures", data=filtered_data,
            ci="sd", capsize=.2, dodge=True, hue='Fashion Rate')

    for ind, label in enumerate(ax.get_xticklabels()):
        if ind % 10 == 0:  # every 10th label is kept
            label.set_visible(True)
        else:
            label.set_visible(False)

    return ax



def run_multiple_retries(retries=1, duration=10000, fashions=[0 , 0.25, 0.5, 0.75, 1]):
    dfs = []
    for i, fashion_rate in tqdm.tqdm(list(itertools.product(range(retries), fashions))):
        Parameters.FASHION_RATE = fashion_rate
        dfs.append(run_single(retry=i, duration=duration))
    return pd.concat(dfs)

def save_retries_output(data):
    if not os.path.exists("results"):
        os.mkdir("results")

    data = pd.concat(dfs)
    data.columns = output_columns

    topology_name = os.path.basename(Parameters.TOPOLOGY_FILE)
    outfilename = "results/axelrod_%s_Q_%s_retries_%d.csv" % (topology_name, Parameters.CULTURE_LENGTH, RETRIES)
    data.to_csv(outfilename)

    ax = plot(data)

    topology_name = os.path.basename(Parameters.TOPOLOGY_FILE)
    outfilename = "results/axelrod_%s_Q_%s_retries_%d.csv" % (topology_name, Parameters.CULTURE_LENGTH, RETRIES)
    fig_filename = outfilename.replace('csv', 'png')
    ax.get_figure().savefig(fig_filename)
