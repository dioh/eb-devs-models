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

df = pd.read_csv('output.csv')

print('''@startuml''')

for mname in df.ModelName.array.unique():
    print ('concise "%s" as %s' % (mname, mname))

print('''
concise "Parent Model" as PMS
concise "Grand Parent Model" as GPMS
''')
# for mname in df.MS.array.unique():
#     print ('concise "%s" as %s' % (mname, mname))
# for mname in df.PMS.array.unique():
#     print ('concise "%s" as %s' % (mname, mname))
# for mname in df.GPMS.array.unique():
#     print ('concise "%s" as %s' % (mname, mname))
print('')

dicc = {}

for index, row in df.iterrows():
    vv = dicc.get(row['T'], [])
    txt = '%s is %s\nPMS is %s\nGPMS is %s' % (row['ModelName'], row['MS'], row['PMS'],str(row['GPMS']))
    vv.append(txt)
    dicc[row['T']] = vv   

for k, v in dicc.items():
    print('@%d\n%s' % (k, "\n".join(sorted(v))))
    print('')


print("@enduml")

