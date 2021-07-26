import pandas as pd
import sys
if sys.version_info[0] < 3: 
    from StringIO import StringIO
else:
    from io import StringIO
csv = StringIO('''T,MS,PMS,GPMS
1,False,False,False
2,True,False,False
3,False,True,False
4,True,False,True
5,False,True,False
6,True,False,True
''')

df = pd.read_csv('multi_model_out.csv')


print('''@startuml
robust "Model" as MS
robust "Parent Model" as PMS
robust "Grand Parent Model" as GPMS
''')


for index, row in df.iterrows():
    print('@%d\nMS is %d\nPMS is %d\nGPMS is %d' % (row['T'], 
        row['MS'], row['PMS'], row['GPMS']))
    print('')

print("@enduml")

