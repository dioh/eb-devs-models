import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

data = pd.read_csv('paraNumeric.csv')

aux = data.groupby('retry').max().reset_index()
# aux = aux[(aux.R > 10)]
data = data[data.retry.isin(aux.retry)]
data_melteada = pd.melt(data, id_vars=['t', 'retry', 'Quarantine Threshold', 'Quarantine Acceptance'], value_vars=['I', 'S', 'R'])
# data_melteada = pd.melt(data, id_vars=['t', 'retry', 'Quarantine Threshold'], value_vars=['I', 'S', 'R'])

data_melteada['value'] = data_melteada['value'] / float(300)
data_melteada = data_melteada.rename(columns={'variable': 'State', 't': 'Time', 'value': 'Proportion'})

__import__('ipdb').set_trace()
fig, ax =plt.subplots(figsize=(12, 14))
colors=["#FF0B04","#4374B3","#228800"]
sns.set_palette(sns.color_palette(colors))
sns.lineplot(data=data_melteada, x='Time', y='Proportion', hue='State', style='Quarantine Acceptance',  ax=ax,color=['r','g','b'], ci=None)

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

