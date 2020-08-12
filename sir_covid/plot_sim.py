import matplotlib.pyplot as plt
import numpy as np
import sys
import csv


if __name__ == '__main__':
	f = plt.figure()

	with open(sys.argv[1]) as csv_file:
		simulation = csv.reader(csv_file, delimiter=',')
		headers = next(simulation, None)
		time = map(lambda x: float(x[0]), simulation)
	with open(sys.argv[1]) as csv_file:
		simulation = csv.reader(csv_file, delimiter=',')
		headers = next(simulation, None)
		s = map(lambda x: int(x[1]), simulation)
	with open(sys.argv[1]) as csv_file:
		simulation = csv.reader(csv_file, delimiter=',')
		headers = next(simulation, None)
		i = map(lambda x: int(x[2]), simulation)
	with open(sys.argv[1]) as csv_file:
		simulation = csv.reader(csv_file, delimiter=',')
		headers = next(simulation, None)
		r = map(lambda x: int(x[3]), simulation)
	with open(sys.argv[1]) as csv_file:
		simulation = csv.reader(csv_file, delimiter=',')
		headers = next(simulation, None)
		v = map(lambda x: int(x[5]), simulation)


	print time
	print s	

	plt.plot(time, s , marker='o', label='S')
	plt.plot(time, i , marker='o', label='I')
	plt.plot(time, v , marker='o', label='V')
	plt.plot(time, r , marker='o', label='R')

	# plt.plot([0],[0.5],marker='s')

	# labels = map(lambda x: "%.0f%%" % x, time)
	# f.set_xticks(x)
	# f.set_xticklabels(labels,rotation=45)	

	plt.xlim(0,5)

	plt.xlabel('Certifying ratio (over correct tests cases)')
	plt.ylabel('Added lines of code ratio (over orbs slice)')



	# plt.yticks(list(plt.yticks()[0]) + [0.66],map(lambda x: np.around(x,2),list(plt.yticks()[0])) +  ['holis'])

	# plt.yticks([0.5],['holis'])
	plt.legend()

	plt.show()

	# f.savefig("closure-vs-dominators.pdf", bbox_inches='tight')

	