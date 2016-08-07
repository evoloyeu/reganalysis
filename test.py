import csv, sys, os, time, hashlib, shutil, numpy as np
from pylab import *
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator
from scipy.stats import pearsonr, linregress
from operator import itemgetter
from collections import Counter
from datetime import datetime
import random
import warnings

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
y = np.array([9, 9, 6, 9, 9, 6])
# # point
# x = np.array([9,12,2,7,8,42,17,42,42,28,42,32,42,40,7,42,5,22,15,25,16,4,10,2,2,2,28,35,42,18,30,42,35,20,30,42,11,13,19,11,6,39,21,29,6,40,10,10,10,42,40])
# r
x = np.array([9, 7, 6, 8, 9, 1])
z = ''
warnings.filterwarnings('error')
try:
	z = np.polyfit(y, x, 2)
except np.RankWarning:
	print np.RankWarning,'power:',2

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