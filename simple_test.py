#!/usr/bin/env python
import csv, os, time, hashlib, shutil, xlsxwriter, copy as myCopy, matplotlib.pyplot as plt, numpy as np
from matplotlib.ticker import MultipleLocator
from operator import itemgetter
from adjustText import adjust_text

a, b='/Users/rexlei/Work/users/20170312/2010-2011/data/pearsonCorr.csv', '/Users/rexlei/Work/users/20170312/2010-2012/data/pearsonCorr.csv'
c, d='/Users/rexlei/Work/users/20170312/2010-2013/data/pearsonCorr.csv', '/Users/rexlei/Work/users/20170312/2010-2014/data/pearsonCorr.csv'
e, saveDir='/Users/rexlei/Work/users/20170312/SINGLE/data/pearsonCorr.csv', '/Users/rexlei/Work/users/20170312/RPFig/'

def plotPearsonRP(xdata, ydata, trSets, xlabel, ylabel, title, figName):
	# fig = plt.figure()
	# ax = plt.axes()
	fig, ax = plt.subplots()
	x, y = np.array(xdata), np.array(ydata)

	# plt.plot(x, y, 'o', c='blue')
	ax.scatter(x,y)

	# texts = []
	# for i, txt in enumerate(trSets):
		# print i
		# texts.append(ax.text(x[i], y[i], txt))

	# adjust_text(texts, force_text=0.05, arrowprops=dict(arrowstyle="-|>", color='r', alpha=0.5))

	'''
	for i, txt in enumerate(trSets):
		# print '==================',i,'=================='
		toosmall = False
		xdiff,ydiff = 0,0
		if i > 0:
			xdiff, ydiff = x[i]-x[i-1], y[i]-y[i-1]
			if (abs(xdiff) <= 7) and (abs(ydiff) <= 0.1):
				toosmall = True

		if x[i] >= 115:
			if toosmall == True:
				if y[i] < y[i-1]:
					ax.annotate(txt, (x[i]-4,y[i]), horizontalalignment='center', verticalalignment='top')
				else:
					ax.annotate(txt, (x[i]-4,y[i]+0.05), horizontalalignment='center', verticalalignment='bottom')
			else:
				ax.annotate(txt, (x[i]-4,y[i]), horizontalalignment='center', verticalalignment='bottom')
		elif x[i] <= 5:
			if y[i]>=0.95:
				if toosmall == True:
					ax.annotate(txt, (x[i]+4,y[i]-0.05), horizontalalignment='center', verticalalignment='top')
				else:
					ax.annotate(txt, (x[i]+4,y[i]), horizontalalignment='center', verticalalignment='top')
			else:
				if toosmall == True:
					ax.annotate(txt, (x[i]+4,y[i]+0.05), horizontalalignment='center', verticalalignment='bottom')
				else:
					ax.annotate(txt, (x[i]+4,y[i]), horizontalalignment='center', verticalalignment='bottom')
		else:
			if toosmall == True:
				if y[i] < y[i-1]:
					ax.annotate(txt, (x[i],y[i]), horizontalalignment='center', verticalalignment='top')
				else:
					if (abs(x[i]>x[i-1])<=2) and (abs(y[i]>y[i-1])<=0.05):
						ax.annotate(txt, (x[i]+4,2*y[i]+0.05-y[i-1]), horizontalalignment='left', verticalalignment='bottom')
					# if abs(x[i]>x[i-1])<5:
					# 	if x[i]>x[i-1]:
					# 		if (x[i]>x[i-1])<2:
					# 			ax.annotate(txt, (x[i]+2,y[i]+0.1), horizontalalignment='center', verticalalignment='bottom')
					# 		else:
					# 			ax.annotate(txt, (x[i]+2,y[i]+0.05), horizontalalignment='center', verticalalignment='bottom')
					# 	else:
					# 		ax.annotate(txt, (x[i]-2,y[i]+0.05), horizontalalignment='center', verticalalignment='bottom')
					else:
						ax.annotate(txt, (x[i],y[i]+0.05), horizontalalignment='center', verticalalignment='bottom')
			else:
				ax.annotate(txt, (x[i],y[i]), horizontalalignment='center', verticalalignment='bottom')
	'''

	  #  	else:
			# if x[i] > 115:
			# 	if y[i] < -0.95:
			# 		ax.annotate(txt, (x[i]-5,y[i]), horizontalalignment='center', verticalalignment='bottom')
			# 	else:
			# 		ax.annotate(txt, (x[i]-5,y[i]), horizontalalignment='center', verticalalignment='top')
			# elif x[i] < 5:
			# 	if y[i]< -0.95:
			# 		ax.annotate(txt, (x[i]+5,y[i]), horizontalalignment='center', verticalalignment='bottom')
			# 	else:
			# 		ax.annotate(txt, (x[i]+5,y[i]), horizontalalignment='center', verticalalignment='top')
			# else:
			# 	ax.annotate(txt, (x[i],y[i]), horizontalalignment='center', verticalalignment='top')

	plt.xlabel(xlabel)
	plt.ylabel(ylabel)
	plt.title(title)

	plt.xlim(0, 120)
	plt.ylim(-1.0, 1.0)

	minorLocator, majorLocator = MultipleLocator(5), MultipleLocator(10)
	ax.xaxis.set_minor_locator(minorLocator)
	ax.xaxis.set_major_locator(majorLocator)

	minorLocator, majorLocator = MultipleLocator(0.1), MultipleLocator(0.1)
	ax.yaxis.set_minor_locator(minorLocator)
	ax.yaxis.set_major_locator(majorLocator)
	plt.xticks(rotation=90, fontsize='small')

	plt.grid(True)
	# plt.show()
	fig.savefig(figName)
	plt.close(fig)

def extractor(fname, trSet):
	retDict={}
	r=csv.reader(open(fname), delimiter=',')
	r.next()
	for row in r:
		predicted=row[2]+row[3]
		if predicted not in retDict:
			retDict[predicted] = [row[:6]+[trSet]]
		else:
			retDict[predicted].append(row[:6]+[trSet])

	return retDict

def fetchByKey(mydict, key):
	if key in mydict.keys():
		return mydict[key]
	else:
		return []

def predictingDict(data):
	retDict = {}
	for x in data:
		key = x[0]+x[1]
		if key not in retDict:
			retDict[key] = [x]
		else:
			retDict[key].append(x)

	return retDict

def yearExtractor(chars):
	for x in chars:
		if x.isdigit():
			return int(x)

def plotRDiff(data, xlabel, ylabel, title, figName):
	fig = plt.figure()
	y = np.array(data)
	x = np.arange(0, len(data), 1)

	plt.plot(x, y, 'o', c='blue')
	plt.xlabel(xlabel)
	plt.ylabel(ylabel)
	plt.title(title)

	plt.xlim(0, len(data)+1)
	plt.ylim(0.0, 1.0)

	ax = plt.axes()
	# minorLocator, majorLocator = MultipleLocator(5), MultipleLocator(10)
	# ax.xaxis.set_minor_locator(minorLocator)
	# ax.xaxis.set_major_locator(majorLocator)

	minorLocator, majorLocator = MultipleLocator(0.1), MultipleLocator(0.1)
	ax.yaxis.set_minor_locator(minorLocator)
	ax.yaxis.set_major_locator(majorLocator)
	plt.xticks(rotation=90, fontsize='small')

	plt.grid(True)
	plt.show()
	# fig.savefig(figName)
	plt.close(fig)

def pairsHist(x, figName):
	fig = plt.figure()
	bins = np.arange(0, 2.0, 0.1)
	plt.axis([0, 2.0, 0, 200])
	plt.title('Histogram of coefficient difference with Bin = ' + str(0.1), fontsize='large')
	plt.xlabel('Bins')
	plt.ylabel('Frequency')
	plt.grid(True)
	
	n, bins, patches = plt.hist(x, bins, normed=0, histtype='bar')

	# figName = saveDir + 'pairs_hist_' + 'interval_' + '.png'
	fig.savefig(figName)
	# plt.show()
	plt.close(fig)

a1011, a1012, a1013, a1014, a1015=extractor(a, '1011'), extractor(b, '1012'), extractor(c, '1013'), extractor(d, '1014'), extractor(e, '1015')

predictedArr = []
for key in a1011.keys()+a1012.keys()+a1013.keys()+a1014.keys()+a1015.keys():
	# print key
	if key not in predictedArr:
		predictedArr.append(key)

y2Arr,y3Arr,y4Arr=[],[],[]
cnt = 0
rdiffArr, myrecArr = [], []
for predicted in predictedArr:
	arr=fetchByKey(a1011,predicted)+fetchByKey(a1012,predicted)+fetchByKey(a1013,predicted)+fetchByKey(a1014,predicted)+fetchByKey(a1015,predicted)
	arr.sort(key=itemgetter(1,0), reverse=False)
	pdict = predictingDict(arr)
	for key, items in pdict.items():
		xdata, ydata, trSets = [],[],[]
		# predicted = items[0][2]+items[0][3]
		year = yearExtractor(predicted)
		myrec = [key, predicted, year]
		tr1011,tr1012,tr1013,tr1014,tr1015 = ['','',''],['','',''],['','',''],['','',''],['','','']
		for item in items:
			ydata.append(float(item[4]))
			xdata.append(int(item[5]))
			trSets.append(item[-1])
			# trSet = item[-1]
			# myrec+=[item[4], item[5], item[6]]
			if item[6]=='1011':
				tr1011=[item[4], item[5], item[6]]
			if item[6]=='1012':
				tr1012=[item[4], item[5], item[6]]
			if item[6]=='1013':
				tr1013=[item[4], item[5], item[6]]
			if item[6]=='1014':
				tr1014=[item[4], item[5], item[6]]
			if item[6]=='1015':
				tr1015=[item[4], item[5], item[6]]

		myrec+=tr1011+tr1012+tr1013+tr1014+tr1015
		folder = saveDir+predicted+'/'
		if not os.path.exists(folder):
			os.makedirs(folder)
		plotPearsonRP(xdata, ydata, trSets, 'Point#', 'Coefficient', key+' vs '+predicted, folder+predicted+'_'+key+'.png')
		cnt += 1
		# print cnt, ':', key, ' vs ', predicted

		maxr, minr=max(ydata), min(ydata)
		diff = maxr-minr
		d01=d02=d03=d04=0
		if diff < 0.1:
			d01 = 1
		elif diff <0.2:
			d02 = 1
		elif diff < 0.3:
			d03 = 1
		else:
			d04 = 1

		myrec+=[maxr, minr, format(float(maxr-minr), '.4f')]
		myrecArr.append(myCopy.deepcopy(myrec))
		print myrec

		rdiffArr.append([key, predicted, year, maxr, minr, maxr-minr, d01, d02, d03, d04])
		print cnt, ':', key+' vs '+predicted, ':', maxr, ':', minr, ':', maxr-minr
		if year==2:
			y2Arr.append(maxr-minr)
		if year==3:
			y3Arr.append(maxr-minr)
		if year==4:
			y4Arr.append(maxr-minr)

# plotRDiff(y2Arr, 'SN', 'r Diff', 'Year 2 Scatter', 'figName')
# plotRDiff(y3Arr, 'SN', 'r Diff', 'Year 3 Scatter', 'figName')
# plotRDiff(y4Arr, 'SN', 'r Diff', 'Year 4 Scatter', 'figName')
myrecArr.sort(key=itemgetter(2,1), reverse=False)
rdiffArr.sort(key=itemgetter(2,1), reverse=False)
w = csv.writer(open(saveDir+'diff.csv', 'w'))

w.writerow(['crs1','crs2','Year','max','min', 'diff', '[0.0,0.1)','[0.1,0.2)','[0.2,0.3)','[0.3,+oo)'])
header = ['crs1','crs2','Year','r','p', 'Tr1011','r','p', 'Tr1012','r','p', 'Tr1013','r','p', 'Tr1014','r','p', 'Tr1015']
w.writerows(rdiffArr+[[''],header]+myrecArr)

print len(y2Arr), len(y3Arr), len(y4Arr)
pairsHist(y2Arr, saveDir+'y2Arr.png')
pairsHist(y3Arr, saveDir+'y3Arr.png')
pairsHist(y4Arr, saveDir+'y4Arr.png')
# print y2Arr
# print y3Arr
# print y4Arr
