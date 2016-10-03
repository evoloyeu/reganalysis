#!/usr/bin/env python

import csv, sys, os, time, hashlib, shutil, numpy as np
from pylab import *
import matplotlib
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.ticker import MultipleLocator
from scipy.stats import pearsonr, linregress
from operator import itemgetter
from collections import Counter
from datetime import datetime
import random
import warnings

# test import error
# import matplotlib
# print matplotlib.__file__

# import mpl_toolkits.mplot3d
# print mpl_toolkits.mplot3d.__file__

# test import error

# sort course pairs
# testList = [
# ['CSC','115','MATH','200'],
# ['CSC','115','ELEC','200'],
# ['CSC','115','MATH','201'],
# ['CSC','125','ELEC','216'],
# ['CSC','135','ELEC','220'],
# ['CSC','145','ELEC','300'],
# ['CSC','155','CSC','349A'],
# ['CSC','115','ELEC','370'],
# ['CSC','115','ELEC','380'],
# ['CSC','115','ELEC','426'],
# ['CSC','115','ELEC','434'],
# ['CSC','115','ELEC','435'],
# ['CSC','115','SENG','440'],
# ['CSC','215','MATH','200'],
# ['CSC','215','ELEC','200'],
# ['CSC','215','MATH','201'],
# ['CSC','215','ELEC','216'],
# ['CSC','215','ELEC','220'],
# ['CSC','215','ELEC','300'],
# ['CSC','215','CSC','349A'],
# ['CSC','215','ELEC','370'],
# ['CSC','215','ELEC','380'],
# ['CSC','215','ELEC','426'],
# ['CSC','215','ELEC','434'],
# ['CSC','215','ELEC','435'],
# ['CSC','215','SENG','440']
# ]

# flist = [x for x in testList if x[1][0] == '1']
# slist = [x for x in testList if x[1][0] == '2']

# testList = [
# ['MATH','100','CENG','241','0.1735',22],
# ['MATH','133','CENG','241','0.3015',28],
# ['MECH','141','CENG','241','0.439',41],
# ['PHYS','122','CENG','241','0.5273',31],
# ['CSC','160','CENG','241','0.3186',36],
# ['CHEM','150','CENG','241','0.5659',28],
# ['ELEC','199','CENG','241','0.3819',42],
# ['MATH','101','CENG','241','0.0275',29],
# ['PHYS','125','CENG','241','0.4991',35],
# ['CSC','115','CENG','241','0.6163',6],
# ['CSC','110','CENG','241','0.3354',31]
# ]

# testList.sort(key=itemgetter(3,1), reverse=False)
# flist = [x for x in testList if x[1][0] == '1']
# flist.sort(key=itemgetter(5), reverse=True)
# freq = Counter(item[5] for item in flist)

# for x in flist:
# 	print x

# print '\n', freq, '\n', freq[flist[0][5]]

# plot 3D graph
# point = [9,12,2,8,7,40,17,42,42,28,42,33,42,39,7,41,5,23,15,26,15,4,11,2,2,28,41,43,17,30,41,42,20,31,43,12,14,20,12,40,36,28,6,40,11,10,43,40]
# r = [0.7109,0.648,1,0.6845,0.8971,0.7037,0.6407,0.5327,0.6801,0.5785,0.4766,0.6774,0.6998,0.5599,-0.8346,0.6062,0.9068,0.7105,0.7777,0.5719,0.6524,0.9869,0.7085,1,1,0.4545,0.439,0.6011,0.8621,0.4774,0.5948,0.4435,0.6199,0.4758,0.533,0.6063,0.877,0.4437,0.685,0.6347,0.5158,0.6982,0.8363,0.4797,0.5798,0.8037,0.5527,0.5749]
# MAE = [1.27,2.03,1.4,1.2,0.8,1.17,2.95,1.19,1.72,0.96,1.69,1.41,1.59,1.48,2.2,1.6,0.7,1.84,0.64,1.82,1.28,0.75,0.82,3.5,1,1.4,1.65,1.41,1.72,0.88,1.31,1.76,1.68,1.38,1.24,0.6,0.66,1.35,1.27,1.05,1.5,1.58,1.58,1.96,1.68,1.61,1.73,1.33]

# fig = plt.figure()
# # ax = fig.add_subplot(111, projection='3d')
# ax = Axes3D(fig)

# for index in xrange(0,len(point)):
# 	if MAE[index] >= 4.0:
# 		ax.scatter(point[index], r[index], MAE[index], c='blue', marker='v')
# 	elif MAE[index] >= 3.0:
# 		ax.scatter(point[index], r[index], MAE[index], c='red', marker='o')
# 	elif MAE[index] >= 2.0:
# 		ax.scatter(point[index], r[index], MAE[index], c='yellow', marker='^')
# 	elif MAE[index] >= 1.0:
# 		ax.scatter(point[index], r[index], MAE[index], c='green', marker='+')
# 	else:
# 		ax.scatter(point[index], r[index], MAE[index], c='purple', marker='x')


# labels = ['>=4.0', '>=3.0', '>=2.0', '>=1.0', '>=0.0']
# labels = ['[4.0,inf)', '[3.0,4.0)', '[2.0,3.0)', '[1.0,2.0)', '[0.0,1.0)']
# markerColors = [['v', 'blue'], ['o','red'], ['^', 'yellow'], ['+', 'green'], ['x', 'purple']]
# points = [ax.scatter([], [], [], marker=s[0], c=s[1]) for s in markerColors]
# plt.legend(points, labels, scatterpoints=1, loc=0)

# ax.set_xlabel('Sample Points', fontsize='medium')
# ax.set_ylabel('Pearson r', fontsize='medium')
# ax.set_zlabel('MAE', fontsize='medium', rotation=90)
# plt.title('Points vs r vs MAE')

# ax.set_xlim3d(0, 120)
# ax.set_ylim3d(-1.0, 1.0)
# # ax.set_zlim3d(0.0, max(MAE)+0.5)
# ax.set_zlim3d(0.0, 8.0)

# ax.zaxis.set_minor_locator(MultipleLocator(0.1))
# ax.zaxis.set_major_locator(MultipleLocator(0.5))

# ax.xaxis.set_minor_locator(MultipleLocator(2))
# ax.xaxis.set_major_locator(MultipleLocator(10))
# plt.xticks(fontsize='9')

# ax.yaxis.set_minor_locator(MultipleLocator(0.1))
# ax.yaxis.set_major_locator(MultipleLocator(0.1))
# plt.yticks(rotation=90, fontsize='9')
# # ax.set_yticks3d(rotation=90, fontsize='small')
# for t in ax.zaxis.get_major_ticks():
# 	t.label.set_fontsize(9)

# ax.view_init(elev=26, azim=57)
# plt.grid(True)
# plt.show()


# test: build data for MITS
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
# y = np.array([9, 9, 6, 9, 9, 6])
# # # point
# # x = np.array([9,12,2,7,8,42,17,42,42,28,42,32,42,40,7,42,5,22,15,25,16,4,10,2,2,2,28,35,42,18,30,42,35,20,30,42,11,13,19,11,6,39,21,29,6,40,10,10,10,42,40])
# # r
# x = np.array([9, 7, 6, 8, 9, 1])
# z = ''
# warnings.filterwarnings('error')
# try:
# 	z = np.polyfit(y, x, 2)
# except np.RankWarning:
# 	print np.RankWarning,'power:',2

# p = np.poly1d(z)
# print type(z), ':\t', z

# xp = np.linspace(-1.0, 1.0, 100)
# _ = plt.plot(x, y, '.', x, p(x), '-', c='red')
# # _ = plt.plot(x, y, '.', c='r')
# plt.xlabel('STD')
# plt.ylabel('Point#')
# plt.title('2012: ERR STD vs POINT#, quadratic regression')

# # plt.ylim(0,max(y)+1.0)
# # plt.xlim(0,max(x))

# ax = plt.axes()
# minorLocator = MultipleLocator(0.1)
# majorLocator = MultipleLocator(0.5)
# ax.yaxis.set_minor_locator(minorLocator)
# ax.yaxis.set_major_locator(majorLocator)
# ax.grid(which = 'minor')

# # ticks = xrange(-1.0, 1.0, 0.2)
# ticks = np.linspace(-1.0, 1.0, 20, endpoint=False).tolist()
# ticks.append(1.0)
# plt.xticks(ticks, rotation=30, fontsize='medium')

# plt.grid(True)
# plt.show()

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
