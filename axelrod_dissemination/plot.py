import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns


SMALL_SIZE = 22
MEDIUM_SIZE = 24
BIGGER_SIZE = 28

plt.rc('font', size=SMALL_SIZE)          # controls default text sizes
plt.rc('axes', titlesize=SMALL_SIZE)     # fontsize of the axes title
plt.rc('axes', labelsize=MEDIUM_SIZE)    # fontsize of the x and y labels
plt.rc('xtick', labelsize=SMALL_SIZE)    # fontsize of the tick labels
plt.rc('ytick', labelsize=SMALL_SIZE)    # fontsize of the tick labels
plt.rc('legend', fontsize=SMALL_SIZE)    # legend fontsize
plt.rc('figure', titlesize=BIGGER_SIZE)  

outfilename = 'results/axelrod_lattice.adj_Q_5_retries_10.csv'
data = pd.read_csv(outfilename, header=0)
filtered_data = data[(data.Time % 10 == 0) & (data.Time > 0)]
plt.figure(figsize=(12,8))

ax = sns.pointplot(x="Time", y="Number of Cultures", data=filtered_data,
		ci="sd", capsize=.2, dodge=True, hue='Fashion Rate')
plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3,
		           ncol=6, mode="expand", borderaxespad=0., title='Fashion Rate')

# ax.xaxis.set_major_locator(plt.MaxNLocator(10))
# ax.xaxis.set_major_locator(plt.MultipleLocator(100))
# ax.xaxis.set_minor_locator(plt.MultipleLocator(10))
for ind, label in enumerate(ax.get_xticklabels()):
	if ind % 10 == 0:  # every 10th label is kept
		label.set_visible(True)
	else:
		label.set_visible(False)
# ax.set_xticklabels(ax.get_xticklabels(), rotation=45)
fig_filename = outfilename.replace('csv', 'png')
ax.get_figure().savefig(fig_filename)


