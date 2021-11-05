import pandas as pd
import sys
if sys.version_info[0] < 3: 
    from StringIO import StringIO
else:
    from io import StringIO
csv = StringIO('''T,MName,MS,PMS,GPMS
1,False,False,False
2,True,False,False
3,False,True,False
4,True,False,True
5,False,True,False
6,True,False,True
''')

df = pd.read_csv('datos.csv')

print('''@startuml''')


print('''
robust "Grand Parent Model" as GPMS
robust "Parent Model" as PMS
''')
for mname in df.ModelName.array.unique():
    print ('robust "%s" as %s' % (mname, mname))
print('')

dicc = {}

for index, row in df.iterrows():
    vv = dicc.get(row['T'], [])
    txt = '%s is %s\nPMS is %s\nGPMS is %s' % (row['ModelName'], row['MS'], row['PMS'],str(row['GPMS']))
    vv.append(txt)
    dicc[row['T']] = vv   

ndic = dict(sorted(dicc.items(), key=lambda item: item[1]))


for k in sorted(dicc.keys()):
    print('@%.2f\n%s' % (k, "\n".join(sorted(dicc[k]))))
    print('')


print("@enduml")

