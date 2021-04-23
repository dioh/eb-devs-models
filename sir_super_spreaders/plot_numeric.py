from SIRSS_numeric import sir_num
import  matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import sys
import numpy as np
from scipy import interpolate
from scipy.interpolate import interp1d

SMALL_SIZE = 14
MEDIUM_SIZE = 18
BIGGER_SIZE = 24

plt.rc('font', size=SMALL_SIZE)          # controls default text sizes
plt.rc('axes', titlesize=SMALL_SIZE)     # fontsize of the axes title
plt.rc('axes', labelsize=MEDIUM_SIZE)    # fontsize of the x and y labels
plt.rc('xtick', labelsize=SMALL_SIZE)    # fontsize of the tick labels
plt.rc('ytick', labelsize=SMALL_SIZE)    # fontsize of the tick labels
plt.rc('legend', fontsize=SMALL_SIZE)    # legend fontsize
plt.rc('figure', titlesize=BIGGER_SIZE)

data = pd.read_csv(sys.argv[1])
aux = data.groupby('retry').max().reset_index()
aux = aux[(aux.R > 50)]
data = data[data.retry.isin(aux.retry)]
data_melteada = pd.melt(data, id_vars=['t', 'retry', 'Quarantine Threshold'], value_vars=['I', 'S', 'R'])

data_melteada['value'] = data_melteada['value'] / float(299)
data_melteada = data_melteada.rename(columns={'variable': 'State', 't': 'Time', 'value': 'Proportion'})

Sn,In,Rn=sir_num(4000*0.001,0.001,0,3,3,5,299)
tiempo_modelo=np.arange(0,4,0.001)

fig, ax =plt.subplots(figsize=(12,8))
colors=["#FF0B04","#4374B3","#228800"]
sns.set_palette(sns.color_palette(colors))
sns.lineplot(data=data_melteada, x='Time', y='Proportion', hue='State',  ax=ax,color=['r','g','b'])

plt.setp(ax,yticks=np.arange(0, 1.01, 0.10))
plt.legend(bbox_to_anchor=( 0., 1.02,1.,.102),loc=3,ncol=2, mode="expand",borderaxespad=0.,title='SIR with Quarantine') #, borderaxespad=0.)
#ax.set_xticklabels(range(-1,4,1))
plt.plot(tiempo_modelo,Sn,label='Snumeric',color="#4374B3",ls='--')
plt.plot(tiempo_modelo,In,label='Inumeric',color="#FF0B04",ls='--')
plt.plot(tiempo_modelo,Rn,label='Rnumeric',color="#228800",ls='--')
plt.legend()
plt.title('SIR - Agent simulation vs Numeric Integration')
plt.tight_layout()
plt.savefig('numeric.png')
plt.show()
