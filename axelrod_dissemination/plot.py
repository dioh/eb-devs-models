import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import sys


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

outfilename = sys.argv[1]
data = pd.read_csv(outfilename, header=0)
data.Time = data.Time - 1
# filtered_data = data[((data.Time % 10 == 0) | (data.Time == 0)) & (data.Time >= 0)] #& (data.Time < 5000)]
filtered_data = data#[((data.Time % 100 == 0) | (data.Time < 100)) & (data.Time >= 0)] #& (data.Time < 5000)]
plt.figure(figsize=(12,8))


ax = sns.pointplot(x="Time", y="Number of Cultures", data=filtered_data,ci=None,
		 capsize=.02,  hue='Fashion Rate', plot_kws=dict(alpha=0.3), hue_order=[ 1.0, 0.75, 0.5, 0.25, 0.0])

plt.setp(ax.collections, alpha=.3) #for the markers
plt.setp(ax.lines, alpha=.3)       #for the lines

plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3,
		           ncol=6, mode="expand", borderaxespad=0., title='Fashion Rate')

ax.set(xscale="log",yscale='log') #, xlim=(9, None))

# ax.set_yticks([1, 2, 3, 10, 100])
# ax.yaxis.set_ticklabels([1, 2, 3, 10, 100])
ax.set_xticks([1, 10, 100, 1000, 10000])
ax.xaxis.set_ticklabels([1, 10, 100, 1000, 10000])
ax.set_yticks([1,2,3,4, 10, 36, 100])
ax.yaxis.set_ticklabels([1,2,3,4, 10, 36, 100])
plt.grid(axis='y')

# ax.xaxis.set_major_locator(plt.MaxNLocator(10))
# ax.xaxis.set_major_locator(plt.MultipleLocator(100))
# ax.xaxis.set_minor_locator(plt.MultipleLocator(10))
# for ind, label in enumerate(ax.get_xticklabels()):
# 	if ind % 100 == 0:  # every 10th label is kept
# 		label.set_visible(True)
# 	else:
# 		label.set_visible(False)
# ax.set_xticklabels(ax.get_xticklabels(), rotation=45)
fig_filename = outfilename.replace('csv', '_nolog.png')
ax.get_figure().savefig(fig_filename)


