import pandas as pd
df = pd.read_csv('paraNumeric.csv')
final = df[df.t.ge(3.999)]
final['hubo_epidemia'] = final.R > 50
print(final.groupby(['Quarantine Threshold', 'Quarantine Acceptance']).hubo_epidemia.value_counts())


