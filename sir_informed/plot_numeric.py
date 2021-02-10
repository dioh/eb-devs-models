from SIRSS_numeric import sir_num
import  matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import sys

data = pd.read_csv(sys.argv[1])
filtered_data = data.loc[(data.t > 0) & (data.t % 1 == 0)]
t,S,I,R=data.t,data.S,data.I,data.R

data_melteada = pd.melt(data, id_vars=['t', 'retry'], value_vars=['S', 'I', 'R'])
__import__('ipdb').set_trace()


Sn,In,Rn=sir_num(10000*0.01,0.01,0,1,3,8,10000)


fig=plt.figure()
sns.pointplot(data=data_melteada, x='t', y='value', hue='variable')
# plt.plot(S,label='S')
# plt.plot(I,label='I')
# plt.plot(R,label='R')

plt.plot(299*Sn,label='Snumeric')
plt.plot(299*In,label='Inumeric')
plt.plot(299*Rn,label='Rnumeric')
plt.savefig('tuvieja.png')
