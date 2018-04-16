#!/usr/bin/env python

import csv, os, random
from datetime import datetime

class splitRawData(object):
	"""docstring for splitRawData"""
	def __init__(self, arg):
		super(splitRawData, self).__init__()
		self.trainYrsList = [['2010', '2011'], ['2010', '2011', '2012'], ['2010', '2011', '2012', '2013'], ['2010', '2011', '2012', '2013', '2014']]
		# ['degtrain2010-2011.csv', 'degtrain2010-2012.csv', ]
		self.rawDeg, self.rawReg = arg[1], arg[2]

		pathList = self.rawDeg.split('/')
		degFilename, regFileName = self.rawDeg.split('/')[-1], self.rawReg.split('/')[-1]
		self.vnumDict = {}

		path = '/'
		for x in xrange(0,len(pathList[1:-2])):
			path = path + pathList[1:-1][x] + '/'

		self.currDir = path+'users/splits/'
		if not os.path.exists(self.currDir):
			os.makedirs(self.currDir)

		self.regFileList, self.degFileList, self.degcsv, self.regcsv = [],[],self.currDir+'deg.csv',self.currDir+'reg.csv'
		self.yearList = ['2010', '2011', '2012', '2013', '2014', '2015']
		for yr in self.yearList:
			self.regFileList.append(self.currDir+'reg'+yr+'.csv')
			self.degFileList.append(self.currDir+'deg'+yr+'.csv')

		if not os.path.exists(self.degcsv):
			# split VNumber and create the Degree data by year
			self.IDListGroup = self.degIDListByYrDegreeDataBuilder()
		# fetch combination data filename
		# self.cDataNameList = self.combinedDataNameList()

	def doBatch(self):
		if not os.path.exists(self.regFileList[0]):
			self.createRegFiles()
			self.dataMerger()

	def createRegFiles(self):
		r = csv.reader(open(self.rawReg), delimiter=',')
		header = r.next()

		DegIDList10, DegIDList11, DegIDList12, DegIDList13, DegIDList14, DegIDList15 = self.IDListGroup
		regList10, regList11, regList12, regList13, regList14, regList15 = [], [], [], [], [], []
		for row in r:
			crs = row[3].replace(' ','')+row[4].replace(' ','')
			if (crs) == 'MATH110':
				row[4] = '133'
			if (crs) == 'ENGR110':
				row[4] = '111'
			if (crs) == 'ENGR141':
				row[3] = 'MECH'

			if (row[1] in DegIDList10):
				regList10.append(row)
			elif (row[1] in DegIDList11):
				regList11.append(row)
			elif (row[1] in DegIDList12):
				regList12.append(row)
			elif (row[1] in DegIDList13):
				regList13.append(row)
			elif (row[1] in DegIDList14):
				regList14.append(row)
			elif (row[1] in DegIDList15):
				regList15.append(row)

		for row in (regList10+regList11+regList12+regList13+regList14+regList15):
			row[1]=self.vnumDict[row[1]]

		# write reg data
		w = csv.writer(open(self.regcsv, 'w'))
		w.writerow(header)
		w.writerows(regList10+regList11+regList12+regList13+regList14+regList15)
		# write degree data by year from 2010 to 2015
		index = 0
		for crsList in [regList10, regList11, regList12, regList13, regList14, regList15]:
			filename = self.regFileList[index]
			w = csv.writer(open(filename, 'w'))
			w.writerow(header)
			w.writerows(crsList)
			index += 1

	def encryptVNUM(self, vnumList):
		vnumDict, nums = {}, []
		random.seed(datetime.now())
		for vnum in vnumList:
			while True:
				num = random.randint(100,len(vnumList)+100)
				if num not in nums:
					nums.append(num)
					vnumDict[vnum] = 'ID_'+str(num)
					break

		return vnumDict

	def degIDListByYrDegreeDataBuilder(self):
		degReader = csv.reader(open(self.rawDeg), delimiter=',')
		header = degReader.next()
		# degree data includes graduates from 2010 to 2015
		DegIDList10, DegIDList11, DegIDList12, DegIDList13, DegIDList14, DegIDList15 = [], [], [], [], [], []
		DegList10, DegList11, DegList12, DegList13, DegList14, DegList15 = [], [], [], [], [], []

		for deg in degReader:
			if deg[1] in ['V00202855', 'V00241653', 'V00682567']:
				continue
			# graduateYr,OFFICIAL_SNAPSHOT_IND = deg[9],deg[12]
			if (deg[9] == '2010') and (not deg[9] in DegIDList10) and (deg[12]=='Y'):
				DegList10.append(deg)
				if deg[1] not in DegIDList10:
					DegIDList10.append(deg[1])
			elif (deg[9] == '2011') and (not deg[9] in DegIDList11) and (deg[12]=='Y'):
				DegList11.append(deg)
				if deg[1] not in DegIDList11:
					DegIDList11.append(deg[1])
			elif (deg[9] == '2012') and (not deg[9] in DegIDList12) and (deg[12]=='Y'):
				DegList12.append(deg)
				if deg[1] not in DegIDList12:
					DegIDList12.append(deg[1])
			elif (deg[9] == '2013') and (not deg[9] in DegIDList13) and (deg[12]=='Y'):
				DegList13.append(deg)
				if deg[1] not in DegIDList13:
					DegIDList13.append(deg[1])
			elif (deg[9] == '2014') and (not deg[9] in DegIDList14) and (deg[12]=='Y'):
				DegList14.append(deg)
				if deg[1] not in DegIDList14:
					DegIDList14.append(deg[1])
			elif (deg[9] == '2015') and (not deg[9] in DegIDList15) and (deg[12]=='Y'):
				DegList15.append(deg)
				if deg[1] not in DegIDList15:
					DegIDList15.append(deg[1])

		# map vnum to a random integer
		self.vnumDict = self.encryptVNUM(DegIDList10+DegIDList11+DegIDList12+DegIDList13+DegIDList14+DegIDList15)
		for row in (DegList10+DegList11+DegList12+DegList13+DegList14+DegList15):
			row[1]=self.vnumDict[row[1]]

		# write degree data
		w = csv.writer(open(self.degcsv, 'w'))
		w.writerow(header)
		w.writerows(DegList10+DegList11+DegList12+DegList13+DegList14+DegList15)
		# write degree data by year from 2010 to 2015
		index = 0
		for degList in [DegList10, DegList11, DegList12, DegList13, DegList14, DegList15]:
			filename = self.degFileList[index]
			w = csv.writer(open(filename, 'w'))
			w.writerow(header)
			w.writerows(degList)
			index += 1

		# return {'2010':DegIDList10, '2011':DegIDList11, '2012':DegIDList12, '2013':DegIDList13, '2014':DegIDList14, '2015':DegIDList15}
		return [DegIDList10, DegIDList11, DegIDList12, DegIDList13, DegIDList14, DegIDList15]

	def splitedRawData(self):
		return [self.regFileList, self.degFileList, self.yearList, self.regcsv, self.degcsv]

	def combinedDataNameList(self):
		nameList = []
		for yrList in self.trainYrsList:
			nameList.append(self.currDir+'deg'+yrList[0]+'-'+yrList[-1]+'.csv')
			nameList.append(self.currDir+'reg'+yrList[0]+'-'+yrList[-1]+'.csv')
			if len(yrList) != 5:
				nameList.append(self.currDir+'reg'+self.yearList[len(yrList)]+'-'+self.yearList[-1]+'.csv')

		return nameList

	def dataMerger(self):
		for yrList in self.trainYrsList:
			self.rheader, self.dheader = '', ''
			degDataPath = self.currDir+'deg'+yrList[0]+'-'+yrList[-1]+'.csv'
			regDataPath = self.currDir+'reg'+yrList[0]+'-'+yrList[-1]+'.csv'
			for yr in yrList:
				index = self.yearList.index(yr)
				reg, deg = self.regFileList[index], self.degFileList[index]
				self.concatenateData(reg, regDataPath, 'reg')
				self.concatenateData(deg, degDataPath, 'deg')

			combineYrsTestData = self.currDir+'reg'+self.yearList[len(yrList)]+'-'+self.yearList[-1]+'.csv'
			self.comYrsTestHeader = ''
			for yr in self.yearList:
				if (yr not in yrList):
					index = self.yearList.index(yr)
					reg = self.regFileList[index]
					if len(yrList) != 5:
						self.concatenateData(reg, combineYrsTestData, 'testCom')

	def concatenateData(self, src, dest, datatype):
		writer = csv.writer(open(dest, 'a'))
		reader = csv.reader(open(src), delimiter=',')
		header = reader.next()

		if datatype == 'reg':
			if len(self.rheader) == 0:
				self.rheader = header
				writer.writerow(header)

		if datatype == 'deg':
			if len(self.dheader) == 0:
				self.dheader = header
				writer.writerow(header)

		if datatype == 'testCom':
			if len(self.comYrsTestHeader) == 0:
				self.comYrsTestHeader = header
				writer.writerow(header)

		for row in reader:
			writer.writerow(row)
