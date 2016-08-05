import csv, sys, os, time, hashlib, shutil, numpy as np
from pylab import *
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator
from scipy.stats import pearsonr, linregress
from operator import itemgetter
from collections import Counter
from datetime import datetime
import random

# f1 = '/Users/rexlei/Important/SPPreliminary/20160408/srv/EE_DEG_10GE_INY_E199.csv'
# f2 = '/Users/rexlei/360cloud/academia/research/SPPPreliminary/20160408/DEG_1015_EE_20160628ALL.csv'
# f3 = '/Users/rexlei/360cloud/academia/research/SPPPreliminary/20160408/DEG_1015_EE_20160628NOTN.csv'
# f4 = '/Users/rexlei/360cloud/academia/research/SPPPreliminary/20160408/DEG_oE199_20160628.csv'
# f5 = '/Users/rexlei/360cloud/academia/research/SPPPreliminary/20160408/DEG_oE199_20160628ALL.csv'

# def uniqueV(f):
# 	r = csv.reader(open(f), delimiter=',')
# 	r.next()
# 	vlist = []
# 	for row in r:
# 		v = row[1]
# 		if v not in vlist:
# 			vlist.append(v)

# 	print 'vlist len: ', len(vlist), '\t', f
# 	print vlist
# 	print '==============================='

# uniqueV(f1)
# uniqueV(f2)
# uniqueV(f3)
# uniqueV(f4)
# uniqueV(f5)

# std
y = np.array([1.79,2.04,1.4,1.65,0,1.54,2.8,1.55,2.14,1.53,1.83,1.46,2.08,2.03,2.7,1.85,0.2,2.19,2.97,1.8,1.88,1.15,1.05,0.83,0,1.22,1.22,2.07,2.23,1.77,1.1,1.64,1.96,2.08,1.3,1.85,1.68,0.72,1.25,1.43,0,1.39,2.04,2.13,0.24,2.3,2.51,0,1.7,1.88,1.38])
# # point
# x = np.array([9,12,2,7,8,42,17,42,42,28,42,32,42,40,7,42,5,22,15,25,16,4,10,2,2,2,28,35,42,18,30,42,35,20,30,42,11,13,19,11,6,39,21,29,6,40,10,10,10,42,40])
# r
x = np.array([0.7109,0.648,1,0.7433,0.7819,0.6942,0.6407,0.5915,0.6715,0.5785,0.5434,0.7036,0.7506,0.4252,-0.8346,0.6346,0.9068,0.701,0.7777,0.5698,0.6794,0.9869,0.7367,1,1,1,0.4545,0.4991,0.6063,0.797,0.4774,0.5253,0.421,0.7114,0.4743,0.5331,0.6831,0.9081,0.4992,0.7016,0.8771,0.6553,0.7257,0.6994,0.8363,0.4948,0.6607,0.6909,0.8037,0.5401,0.573])

z = np.polyfit(x, y, 1)
p = np.poly1d(z)
print type(z), ':\t', z

xp = np.linspace(-1.0, 1.0, 100)
_ = plt.plot(x, y, '.', x, p(x), '-', c='red')
# _ = plt.plot(x, y, '.', c='r')
plt.xlabel('STD')
plt.ylabel('Point#')
plt.title('2012: ERR STD vs POINT#, quadratic regression')

# plt.ylim(0,max(y)+1.0)
# plt.xlim(0,max(x))

ax = plt.axes()
minorLocator = MultipleLocator(0.1)
majorLocator = MultipleLocator(0.5)
ax.yaxis.set_minor_locator(minorLocator)
ax.yaxis.set_major_locator(majorLocator)
ax.grid(which = 'minor')

# ticks = xrange(-1.0, 1.0, 0.2)
ticks = np.linspace(-1.0, 1.0, 20, endpoint=False).tolist()
ticks.append(1.0)
plt.xticks(ticks, rotation=30, fontsize='medium')

plt.grid(True)
plt.show()

# exist = []
# while True:
# 	random.seed(datetime.now())
# 	# for x in xrange(0,10):
# 	rnum = random.randint(0,9)
# 	if rnum not in exist:
# 		exist.append(rnum)

# 	print rnum
# 	print '---------------'
# 	if len(exist) >= 10:
# 		print exist
# 		break