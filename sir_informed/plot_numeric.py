from SIRSS_numeric import sir_num
import  matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import sys
import numpy as np
from scipy import interpolate
from scipy.interpolate import interp1d

data = pd.read_csv(sys.argv[1])
filtered_data = data.loc[(data.t > 0) & (data.t % 1 == 0)]
t,S,I,R=data.t,data.S,data.I,data.R

data_melteada = pd.melt(data, id_vars=['t', 'retry'], value_vars=['S', 'I', 'R'])
#__import__('ipdb').set_trace()


Sn,In,Rn=sir_num(4000*0.001,0.001,0,3,3,8,300)
#SIRn=sir_num(60*0.05,0.05,40*0.3,1,3,8,10000)
#sir_num(T,dt,EK,ga,b,lamb,pob):


tiempo_modelo=np.arange(0,4,0.001)
print(len(Sn),len(tiempo_modelo))




fig,ax=plt.subplots()
colors=["#FF0B04","#4374B3","#228800"]
sns.set_palette(sns.color_palette(colors))
sns.lineplot(data=data_melteada, x='t', y='value', hue='variable',ax=ax,color=['r','g','b'])
ax.set_xticklabels(range(-1,4,1))
# plt.plot(S,label='S')
# plt.plot(I,label='I')
# plt.plot(R,label='R')

plt.savefig('agent.png')

plt.plot(tiempo_modelo,299*Sn,label='Snumeric',color="#FF0B04",ls='--')
plt.plot(tiempo_modelo,299*In,label='Inumeric',color="#4374B3",ls='--')
plt.plot(tiempo_modelo,299*Rn,label='Rnumeric',color="#228800",ls='--')
plt.legend()
plt.title('gamma=,beta=,meandegree=')
plt.savefig('numeric.png')

plt.figure()
plt.plot(Sn)
plt.plot(In)
plt.plot(Rn)
plt.show()
