import csv, sys, os, time, hashlib, shutil, random
from pylab import *
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.ticker import MultipleLocator
from scipy.stats import pearsonr, linregress
import numpy as np
from operator import itemgetter
from collections import Counter
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

		path = '/'
		for x in xrange(0,len(pathList[1:-2])):
			path = path + pathList[1:-1][x] + '/'

		# self.currDir = path+'users/splits_'+time.strftime('%Y%m%d')+'/'
		self.currDir = path+'users/splits/'
		if not os.path.exists(self.currDir):
			os.makedirs(self.currDir)

		self.regFileList, self.degFileList = [],[]
		self.yearList = ['2010', '2011', '2012', '2013', '2014', '2015']
		for yr in self.yearList:
			self.regFileList.append(self.currDir+'reg'+yr+'.csv')
			self.degFileList.append(self.currDir+'deg'+yr+'.csv')

		self.IDDict = self.degIDListByYr()
		self.cDataNameList = self.combinedDataNameList()

	def doBatch(self):
		if not os.path.exists(self.cDataNameList[0]):
			for index in xrange(0, len(self.yearList)):
				self.groupRawData(self.rawDeg, self.degFileList[index], self.yearList[index])
				self.groupRawData(self.rawReg, self.regFileList[index], self.yearList[index])

			self.dataMerger()

	def groupRawData(self, src, dest, yr):
		reader = csv.reader(open(src), delimiter=',')
		rheader = reader.next()

		writer = csv.writer(open(dest, 'w'))
		writer.writerow(rheader)
		for row in reader:
			rowID, IDList = row[1], self.IDDict[yr]
			if rowID in IDList:
				writer.writerow(row)

	def degIDListByYr(self):
		degReader = csv.reader(open(self.rawDeg), delimiter=',')
		# degree data includes graduates from 2010 to 2015
		DegIDList10, DegIDList11, DegIDList12, DegIDList13, DegIDList14, DegIDList15 = [], [], [], [], [], []

		for deg in degReader:
			graduateYr = deg[9]
			if (graduateYr == '2010') and (not graduateYr in DegIDList10):
				if deg[1] not in DegIDList10:
					DegIDList10.append(deg[1])
			elif (graduateYr == '2011') and (not graduateYr in DegIDList11):
				if deg[1] not in DegIDList11:
					DegIDList11.append(deg[1])
			elif (graduateYr == '2012') and (not graduateYr in DegIDList12):
				if deg[1] not in DegIDList12:
					DegIDList12.append(deg[1])
			elif (graduateYr == '2013') and (not graduateYr in DegIDList13):
				if deg[1] not in DegIDList13:
					DegIDList13.append(deg[1])
			elif (graduateYr == '2014') and (not graduateYr in DegIDList14):
				if deg[1] not in DegIDList14:
					DegIDList14.append(deg[1])
			elif (graduateYr == '2015') and (not graduateYr in DegIDList15):
				if deg[1] not in DegIDList15:
					DegIDList15.append(deg[1])

		return {'2010':DegIDList10, '2011':DegIDList11, '2012':DegIDList12, '2013':DegIDList13, '2014':DegIDList14, '2015':DegIDList15}

	def splitedRawData(self):
		return [self.regFileList, self.degFileList, self.yearList, self.rawReg, self.rawDeg]

	def combinedDataNameList(self):
		nameList = []
		for yrList in self.trainYrsList:
			nameList.append(self.currDir+'degtrain'+yrList[0]+'-'+yrList[-1]+'.csv')
			nameList.append(self.currDir+'regtrain'+yrList[0]+'-'+yrList[-1]+'.csv')
			if len(yrList) != 5:
				nameList.append(self.currDir+'regtest'+self.yearList[len(yrList)]+'-'+self.yearList[-1]+'.csv')

		return nameList

	def dataMerger(self):
		for yrList in self.trainYrsList:
			self.rheader, self.dheader = '', ''
			degDataPath = self.currDir+'degtrain'+yrList[0]+'-'+yrList[-1]+'.csv'
			regDataPath = self.currDir+'regtrain'+yrList[0]+'-'+yrList[-1]+'.csv'
			for yr in yrList:
				index = self.yearList.index(yr)
				reg, deg = self.regFileList[index], self.degFileList[index]
				self.concatenateData(reg, regDataPath, 'reg')
				self.concatenateData(deg, degDataPath, 'deg')

			combineYrsTestData = self.currDir+'regtest'+self.yearList[len(yrList)]+'-'+self.yearList[-1]+'.csv'
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

class prepross(object):
	def __init__(self, degRegFiles):
		super(prepross, self).__init__()
		self.trainYrsList = [['2010', '2011'], ['2010', '2011', '2012'], ['2010', '2011', '2012', '2013'], ['2010', '2011', '2012', '2013', '2014']]
		self.thresholdList = [1,5,10,15,20]

		self.regFileList, self.degFileList, self.yearList, self.rawReg, self.rawDeg = degRegFiles
		rwList, pwList = [1.4,1.4,1.2,1.1], [1,1,1,1]
		self.coefficientList = ['Pearson']
		# define the predictor course: ALL: use common predictors based on the picking criteria
		self.predictorCourses = ['CSC 115', 'ALL']
		# self.predictorCourses = ['ALL']
		self.factors = ['PR', 'P', 'R']

		# weights dictionary: 
		# key: the threshold; value: a dictionary with keys of train data length and value of weights
		self.wdict = {
		1:{2:1.4, 3:1.4, 4:1.2, 5:1.1},
		5:{2:1.4, 3:1.0, 4:1.2, 5:1.2},
		10:{2:1.3, 3:1.2, 4:1.2, 5:1.2},
		15:{2:1.4, 3:1.2, 4:1.2, 5:1.2},
		20:{2:1.4, 3:1.2, 4:1.2, 5:1.2}
		}
		self.errMerge = False

	def statsPath(self):
		pathList, path = self.regFileList[0].split('/'), '/'
		for x in xrange(0,len(pathList[1:-2])):
			path = path+pathList[1:-1][x] + '/'

		# For MTIS
		self.matrixDir = path+'matrix/'

		# No specific predictor
		if self.proPredictor == 'ALL':
			if len(self.trainYrs) > 1:
				self.trainYrsText = str(self.trainYrs[0])+'-'+str(self.trainYrs[-1])
			else:
				self.trainYrsText = str(self.trainYrs[0])

			self.currDir = path+time.strftime('%Y%m%d')+'/'+self.coe+'/'+self.proPredictor+'/'+self.trainYrsText+'/'+str(self.threshold)+'/'+self.factor+'/'
			self.dataDir = path+time.strftime('%Y%m%d')+'/'+self.coe+'/'+self.proPredictor+'/'+self.trainYrsText+'/'+str(self.threshold)+'/'+'data/'
		else:
			# designated specific predictor
			self.currDir = path+time.strftime('%Y%m%d')+'/'+self.coe+'/'+self.proPredictor+'/'+str(self.threshold)+'/'
			self.dataDir = self.currDir+'data/'

		# data directory
		# self.dataDir = path+time.strftime('%Y%m%d')+'/'+self.coe+'/'+self.proPredictor+'/'+self.trainYrsText+'/'+str(self.threshold)+'/'+'data/'

		[self.linear_plots_ori, self.quadratic_plots_ori, self.coefficient_ori, self.hist_ori, self.bars_ori, self.course_ori, self.pairsHistDir, self.splitsDir, self.maerp3DDir, self.yrvsyr, self.yr1l, self.yr2l, self.yr1q, self.yr2q] = [self.dataDir+'LPlots_ori/', self.dataDir+'QPlots_ori/', self.currDir+'coefficient_ori/', self.currDir+'hist_ori/', self.currDir+'bars_ori/', self.currDir+'course_ori/', self.currDir+'pairs_hist/', path+'splits/', self.currDir+'3d/', self.currDir+'yrVSyr/', self.currDir+'Yr1L/', self.currDir+'Yr2L/', self.currDir+'Yr1Q/', self.currDir+'Yr2Q/']

		pathBuilderList = [self.currDir, self.dataDir, self.dataDir+'Test/', self.dataDir+'Train/', self.currDir+'T1/L/', self.currDir+'T3/L/', self.currDir+'T1/Q/', self.currDir+'T3/Q/', self.linear_plots_ori, self.quadratic_plots_ori, self.coefficient_ori, self.hist_ori, self.bars_ori, self.course_ori, self.pairsHistDir, self.splitsDir, self.matrixDir, self.maerp3DDir+'L/',self.maerp3DDir+'Q/', self.yrvsyr, self.yr1l+'2/', self.yr1l+'3/', self.yr1l+'4/', self.yr2l+'3/', self.yr2l+'4/', self.yr1q+'2/', self.yr1q+'3/', self.yr1q+'4/', self.yr2q+'3/', self.yr2q+'4/']
		for item in pathBuilderList:
			if not os.path.exists(item):
				os.makedirs(item)

		self.pairsFrequency, self.pearsoncorr = self.dataDir+'pairsFrequency.csv', self.dataDir+'pearsonCorr.csv'
		if self.proPredictor == 'ALL':
			self.degDataPath, self.regDataPath = self.splitsDir+'degtrain'+self.trainYrs[0]+'-'+self.trainYrs[-1]+'.csv', self.splitsDir+'regtrain'+self.trainYrs[0]+'-'+self.trainYrs[-1]+'.csv'
			self.top1pFactors, self.top3pFactors = self.dataDir + 'T1F_P_' + self.trainYrsText +'.csv', self.dataDir + 'T3F_P_' + self.trainYrsText +'.csv'
			self.top1rFactors, self.top3rFactors = self.dataDir + 'T1F_R_' + self.trainYrsText +'.csv', self.dataDir + 'T3F_R_' + self.trainYrsText +'.csv'
			self.top1FactorsFile, self.top3FactorsFile = '', ''

			self.linearTop1Top3Stats, self.quadraticTop1Top3Stats = self.currDir+'LT1T3Stats_'+self.trainYrsText+'.csv', self.currDir+'QT1T3Stats_'+self.trainYrsText+'.csv'
			self.linearQuadraticTop1Stats, self.linearQuadraticTop3Stats = self.currDir+'LQT1Stats_'+self.trainYrsText+'.csv', self.currDir+'LQT3Stats_'+self.trainYrsText+'.csv'
		else:
			self.degDataPath, self.regDataPath = self.rawDeg, self.rawReg
			self.top1FactorsFile = self.pearsoncorr
			self.linearQuadraticTop1Stats = self.currDir+'LQT1Stats_'+self.proPredictor+'.csv'

		self.allTechCrs = path+'techcourses/'+'technicalCourse.csv'
		self.availableTechCrsList = []

		# for test reg data
		# store test data's noDup filenames
		self.fTestRegFileNameList = []
		# store stats filenames for all of the test data
		self.fTestStatFileNameList = []
		# store test filenames
		self.testFileList = [self.regDataPath]

		if self.proPredictor == 'ALL':
			# create year combined test data
			combineYrsTestData = self.splitsDir+'regtest'+self.yearList[len(self.trainYrs)]+'-'+self.yearList[-1]+'.csv'
			# self.comYrsTestHeader = ''
			for yr in self.yearList:
				if (yr not in self.trainYrs):
					index = self.yearList.index(yr)
					reg = self.regFileList[index]
					self.testFileList.append(reg)

			if len(self.trainYrs) != 5:
				self.testFileList.append(combineYrsTestData)

		# build test stats filenames and the predicting result and errors filenames
		self.linearPredictResultsListTop1, self.linearPredictResultsAveErrTop1, self.quadrPredictResultsListTop1, self.quadrPredictResultsAveErrTop1 = [], [], [], []

		# this only works for use ALL predictors, not for a specific predictor
		if self.proPredictor == 'ALL':
			self.linearPredictResultsListTop3, self.linearPredictResultsAveErrTop3, self.quadrPredictResultsListTop3, self.quadrPredictResultsAveErrTop3 = [], [], [], []

		for fname in self.testFileList:
			filename = fname.split('/')[-1].split('.')[0]
			# todo: optimize later
			self.linearPredictResultsListTop1.append(self.currDir + 'T1/L/PGrades_' + filename + '_' + self.proPredictor + '_' + str(self.threshold) + '_LT1.csv')
			self.linearPredictResultsAveErrTop1.append(self.currDir + 'T1/L/PAveErr_' + filename + '_' + self.proPredictor + '_' + str(self.threshold) + '_LT1.csv')
			self.quadrPredictResultsListTop1.append(self.currDir + 'T1/Q/PGrades_' + filename + '_' + self.proPredictor + '_' + str(self.threshold) + '_QT1.csv')
			self.quadrPredictResultsAveErrTop1.append(self.currDir + 'T1/Q/PAveErr_' + filename + '_' + self.proPredictor + '_' + str(self.threshold) + '_QT1.csv')

			if self.proPredictor == 'ALL':
				self.linearPredictResultsListTop3.append(self.currDir + 'T3/L/PGrades_' + filename +'_LT3.csv')
				self.linearPredictResultsAveErrTop3.append(self.currDir + 'T3/L/PAveErr_' + filename +'_LT3.csv')
				self.quadrPredictResultsListTop3.append(self.currDir + 'T3/Q/PGrades_' + filename +'_QT3.csv')
				self.quadrPredictResultsAveErrTop3.append(self.currDir + 'T3/Q/PAveErr_' + filename +'_QT3.csv')

			tmpList, prefix, testPath, yr = [], '', '',''
			if (fname == self.regDataPath) or (combineYrsTestData == fname):
				if fname == self.regDataPath:
					if self.proPredictor == 'ALL':
						testPath = self.dataDir +'Test/' + filename[8:17] + '/'
					else:
						testPath = self.dataDir +'Test/' + filename + '/'
				else:
					testPath = self.dataDir +'Test/' + filename[7:16] + '/'

				prefix = testPath + filename
				self.fTestRegFileNameList.append(prefix + '_Test.csv')
			else:
				testPath = self.dataDir +'Test/' + filename[3:] + '/'
				prefix = testPath + filename[0:3] + 'test' + filename[3:]
				self.fTestRegFileNameList.append(prefix + '_Test.csv')

			if not os.path.exists(testPath):
				os.makedirs(testPath)

			for item in ['CRSPERSTU', 'STUREGISTERED', 'EMPTY', 'CRS_STU', 'CRS_STU_GRADE', 'STU_CRS', 'STU_CRS_GRADE']:
				tmpList.append(prefix + '_' + item +'.csv')

			self.fTestStatFileNameList.append(tmpList)
			# self.CRSPERSTU, self.STUREGISTERED, self.EMPTY, self.CRS_STU, self.CRS_STU_GRADE, self.STU_CRS

		# REPL, NODUP, CRSPERSTU, STUREGISTERED, EMPTY, EMPTY_STU, EMPTY_CRS, CRS_STU, IDMAPPER
		fileNameList = ['REPL_SAS.csv', 'NODUP_SAS.csv', 'TECH_NODUP_SAS.csv', 'CRSPERSTU_SAS.csv', 'STUREGISTERED_SAS.csv', 'EMPTY_SAS.csv', 'EMPTY_STU_SAS.csv', 'EMPTY_CRS_SAS.csv', 'CRS_STU_SAS.csv', 'CRS_STU_GRADE_SAS.csv', 'NODUP_REPL_SAS.csv', 'STU_CRS_SAS.csv', 'STU_CRS_GRADE_SAS.csv', 'CRS_MATRIX_SAS.csv', 'DISCARD_SAS.csv', 'uniCourseList.csv', 'uniTechCrsList.csv', 'TECH.csv', 'nan.csv']
		for x in xrange(0,len(fileNameList)):
			fileNameList[x] = self.dataDir+'Train/'+fileNameList[x]

		[self.regREPL, self.regNODUP, self.techRegNODUP, self.CRSPERSTU, self.STUREGISTERED, self.EMPTY, self.EMPTY_STU, self.EMPTY_CRS, self.CRS_STU, self.CRS_STU_GRADE, self.regNODUPREPL, self.STU_CRS, self.STU_CRS_GRADE, self.crsMatrix, self.discardList, self.courselist, self.uniTechCrsList, self.techCrsCSV, self.nancsv] = fileNameList

		self.degREPL, self.IDMAPPER = self.dataDir+'REPL_SAS.csv', self.dataDir+'IDMAPPER_SAS.csv'

	def doBatch(self):
		# build MTIS data
		# self.matrixBuilder()

		for coe in self.coefficientList:
			self.coe = coe
			for proPredictor in self.predictorCourses:
				self.proPredictor = proPredictor
				if proPredictor == 'ALL':
					self.computeALL()
				else:
					self.computeSpecific()

	def predicting4ALL(self):
		# predicting
		predictors = self.predictorsDict[self.factor]
		for x in xrange(0,len(self.fTestStatFileNameList)):
			self.predictProcessTop1Factors(self.fTestStatFileNameList[x][3], self.linearPredictResultsListTop1[x], self.linearPredictResultsAveErrTop1[x], 1, predictors[0])
			self.predictProcessTop1Factors(self.fTestStatFileNameList[x][3], self.quadrPredictResultsListTop1[x], self.quadrPredictResultsAveErrTop1[x], 2, predictors[0])
			self.predictProcessTop3Factors(self.fTestStatFileNameList[x][3], self.linearPredictResultsListTop3[x], self.linearPredictResultsAveErrTop3[x], 1, predictors[1])
			self.predictProcessTop3Factors(self.fTestStatFileNameList[x][3], self.quadrPredictResultsListTop3[x], self.quadrPredictResultsAveErrTop3[x], 2, predictors[1])

	def predicting4Specific(self):
		self.testSetsStats()
		for x in xrange(0,len(self.fTestStatFileNameList)):
			self.predictProcessTop1Factors(self.fTestStatFileNameList[x][3], self.linearPredictResultsListTop1[x], self.linearPredictResultsAveErrTop1[x], 1, self.top1FactorsFile)
			self.predictProcessTop1Factors(self.fTestStatFileNameList[x][3], self.quadrPredictResultsListTop1[x], self.quadrPredictResultsAveErrTop1[x], 2, self.top1FactorsFile)

	def prepare(self):
		self.techCrs()
		self.formatRegSAS(self.regDataPath, self.regNODUP)
		self.formatRegSAS(self.techCrsCSV, self.techRegNODUP)
		self.simpleStats(self.techRegNODUP, self.CRSPERSTU, self.STUREGISTERED, self.EMPTY, self.CRS_STU, self.CRS_STU_GRADE, self.STU_CRS, self.STU_CRS_GRADE)
		self.pairs()
		self.pairsHists()

		self.uniqueCourseList()
		self.uniqueTechCrsList()

		# self.cryptID()
		self.techCrsHists()

		# compute correlation coefficients and draw correlation plots
		if self.proPredictor == 'ALL':
			self.corrPlot(self.CRS_STU, self.pearsoncorr)
		else:
			self.corrPlotOneProPredictor(self.CRS_STU, self.pearsoncorr)

	def testSetsStats(self):
		# compute the stats data for the test datasets
		for testFile in self.testFileList:
			index = self.testFileList.index(testFile)
			noDupFile = self.fTestRegFileNameList[index]
			self.formatRegSAS(testFile, noDupFile)

			statList = self.fTestStatFileNameList[index]
			self.simpleStats(noDupFile, statList[0], statList[1], statList[2], statList[3], statList[4], statList[5], statList[6])

	def testWeights(self):
		# trying to find the good weights
		w1 = [1, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9, 2.0, 2.1, 2.2, 2.3, 2.4, 2.5]
		w2 = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
		self.formulaV1Integrate(w1,w2)

	def computeALL(self):
		for yrList in self.trainYrsList:
			for threshold in self.thresholdList:
				self.isPrepared = False
				for factor in self.factors:
					self.threshold, self.trainYrs, self.factor = threshold, yrList, factor
					self.statsPath()

					if not self.isPrepared:
						self.prepare()
						self.isPrepared = True

						self.testSetsStats()
						# create predictors
						self.testWeights()
						self.rw, self.pw = self.wdict[self.threshold][len(self.trainYrs)], 1.0
						# use factor Pxy
						self.formulaV1(self.rw,self.pw)
						# self.rw,self.pw = rw, pw
						# use factors of Points, coefficients
						self.createPRFactors()
						self.predictorsDict = {'PR': [self.top1FactorsFile, self.top3FactorsFile],'P': [self.top1pFactors, self.top3pFactors],'R': [self.top1rFactors, self.top3rFactors]}

					self.predictorsScatterPlots()
					# self.predicting4ALL(self.wdict[self.threshold][len(self.trainYrs)], 1.0)
					self.predicting4ALL()
					# plot yr vs yr scatter plots
					self.gradePointsDistribution(self.predictorsDict[self.factor][0])

					# # todo: stats
					if self.errMerge:
						self.errTop1Top3StatsMerger(self.linearTop1Top3Stats, self.linearPredictResultsListTop1, self.linearPredictResultsListTop3)
						self.errTop1Top3StatsMerger(self.quadraticTop1Top3Stats, self.quadrPredictResultsListTop1, self.quadrPredictResultsListTop3)
						self.errLinearQuadraticStatsMerger(self.linearQuadraticTop1Stats, self.linearPredictResultsListTop1, self.quadrPredictResultsListTop1)
						self.errLinearQuadraticStatsMerger(self.linearQuadraticTop3Stats, self.linearPredictResultsListTop3, self.quadrPredictResultsListTop3)

	def computeSpecific(self):
		for threshold in self.thresholdList:
			self.threshold = threshold
			self.statsPath()
			self.prepare()
			self.predictorsScatterPlots()
			self.predicting4Specific()
			# plot yr vs yr scatter plots
			self.gradePointsDistribution(self.top1FactorsFile)

			if self.errMerge:
				self.errLinearQuadraticStatsMerger(self.linearQuadraticTop1Stats, self.linearPredictResultsListTop1, self.quadrPredictResultsListTop1)

	def misc(self):
		self.coefficientHists(self.hist_ori, self.pearsoncorr)
		self.groupPlots(self.linear_plots_ori, self.pearsoncorr)
		self.plotsPickByCoefficient(1.0, self.pearsoncorr)
		self.plotsPickByCoefficient(-1.0, self.pearsoncorr)
		self.plotsPickByCoefficient(0.0, self.pearsoncorr)

	def discardFunction(self):
		pass
		# self.techCrs()
		# self.formatRegSAS(self.regDataPath, self.regNODUP)
		# self.formatRegSAS(self.techCrsCSV, self.techRegNODUP)

		# compute the stats data for the test datasets
		# for testFile in self.testFileList:
		# 	index = self.testFileList.index(testFile)
		# 	noDupFile = self.fTestRegFileNameList[index]
		# 	self.formatRegSAS(testFile, noDupFile)

		# 	statList = self.fTestStatFileNameList[index]
		# 	self.simpleStats(noDupFile, statList[0], statList[1], statList[2], statList[3], statList[4], statList[5])

		# self.simpleStats(self.techRegNODUP, self.CRSPERSTU, self.STUREGISTERED, self.EMPTY, self.CRS_STU, self.CRS_STU_GRADE, self.STU_CRS)
		# self.pairs()
		# self.pairsHists()

		# self.uniqueCourseList()
		# self.uniqueTechCrsList()

		# compute correlation coefficients and draw correlation plots
		# self.corrPlot(self.CRS_STU, self.linear_plots_ori, self.pearsoncorr)

		# self.coefficientHists(self.hist_ori, self.pearsoncorr)
		# self.groupPlots(self.linear_plots_ori, self.pearsoncorr)
		# self.plotsPickByCoefficient(1.0, self.pearsoncorr)
		# self.plotsPickByCoefficient(-1.0, self.pearsoncorr)
		# self.plotsPickByCoefficient(0.0, self.pearsoncorr)

	def groupPlots(self, fromDir, corr):
		todir = self.currDir+'groups/'
		intervals = np.linspace(-1.0, 1.0, 20, endpoint=False).tolist()
		for item in intervals:
			self.figureSelect(float(format(item, '.2f')), 0.1, self.linear_plots_ori, todir, corr)

	def figureSelect(self, threshold, interval, fromDir, toDir, corr):
		savePath = toDir + str(threshold) +'_'+ str(threshold + interval)
		saveZeroPath = toDir + str(0.0)

		if not os.path.exists(savePath):
			os.makedirs(savePath)

		if (not os.path.exists(saveZeroPath)) and (threshold == 0.0):
			os.makedirs(saveZeroPath)

		reader = csv.reader(open(corr), delimiter = ',')
		reader.next()
		for row in reader:
			name = row[0] + row[1] + ' ' + row[2] + row[3] + ' ' + row[4] + '.png'
			if threshold < 0:
				if (float(row[4]) > threshold) and (float(row[4]) <= (threshold + interval)) and (float(row[4]) != 0.0):
					shutil.copy2(fromDir + name, savePath + '/' + name)
			elif threshold > 0.0:
				if (float(row[4]) >= threshold) and (float(row[4]) < (threshold + interval)):
					shutil.copy2(fromDir + name, savePath + '/' + name)
			else:
				if (float(row[4]) > threshold) and (float(row[4]) < (threshold + interval)):
					shutil.copy2(fromDir + name, savePath + '/' + name)

	def plotsPickByCoefficient(self, coefficient, corr):
		toDir = self.currDir+'groups/' + str(coefficient)
		if not os.path.exists(toDir):
			os.makedirs(toDir)

		reader = csv.reader(open(corr), delimiter = ',')
		reader.next()
		for row in reader:
			if float(row[4]) == coefficient:
				fig = row[0] + row[1] + ' ' + row[2] + row[3] +  ' ' + row[4] + '.png'
				shutil.copy2(self.linear_plots_ori + fig, toDir + '/' + fig)

	def copyPlots(self, fromDir, toDir, corr):
		reader = csv.reader(open(corr), delimiter = ',')
		reader.next()

		for row in reader:
			folder = toDir + row[0]+row[1]
			if not os.path.exists(folder):
				os.makedirs(folder)
			fig = row[0] + row[1] + ' ' + row[2] + row[3] +  ' ' + row[4] +'.png'
			shutil.copy2(fromDir + fig, toDir + '/' + fig)

	def validations(self):
		for x in [0.60, 0.65, 0.70, 0.75, 0.80, 0.85, -0.45, -0.50, -0.55, -0.60, -0.65, -0.70, -0.75, -0.80, -0.85]:
			self.validation(self.pearsoncorr, 'ori', x)

	def cryptID(self):
		self.encodeVnumber()
		self.replaceVnum(self.degDataPath, self.degREPL)
		self.replaceVnum(self.regDataPath, self.regREPL)
		self.replaceVnum(self.regNODUP, self.regNODUPREPL)

	def coefficientHists(self, histDir, corr):
		for x in [0.05, 0.10, 0.15, 0.20]:
			self.coefficientHist(x, histDir, corr)

	def pickupFigures(self, plotsDir, coefficientsDir, coorDir):
		self.figureSelect(0.6, 0.2, plotsDir, coefficientsDir, coorDir)
		self.figureSelect(0.5, 0.05, plotsDir, coefficientsDir, coorDir)
		self.figureSelect(0.55, 0.05, plotsDir, coefficientsDir, coorDir)
		self.figureSelect(0.6, 0.05, plotsDir, coefficientsDir, coorDir)
		self.figureSelect(0.65, 0.05, plotsDir, coefficientsDir, coorDir)
		self.figureSelect(0.7, 0.05, plotsDir, coefficientsDir, coorDir)
		self.figureSelect(0.75, 0.05, plotsDir, coefficientsDir, coorDir)
		
	def techCrsHists(self):
		for x in xrange(1,11):			
			self.techCrsHist(x)

	def pairsHists(self):
		for x in xrange(1,11):
			self.pairsHist(x)

	def encodeVnumber(self):
		fDegree = self.degDataPath
		fDegreeIDMap = self.IDMAPPER

		fDegreeRder = csv.reader(open(fDegree), delimiter=',')
		fDegreeIDMapWrter = csv.writer(open(fDegreeIDMap, 'w'))

		# skip header
		fDegreeRder.next()
		fDegreeIDMapWrter.writerow(['V_NUMBER', 'SHA1'])
		for record in fDegreeRder:
			fDegreeIDMapWrter.writerow([record[1], hashlib.sha1(record[1]).hexdigest()])

	def replaceVnum(self, infile, outfile):
		fInfileRder = csv.reader(open(infile), delimiter=',')
		header = fInfileRder.next()

		fOutWrter = csv.writer(open(outfile, 'w'))
		fOutWrter.writerow(header)

		for row in fInfileRder:
			row[1]=hashlib.sha1(row[1]).hexdigest()
			fOutWrter.writerow(row)

	def removeDup(self, courseListPerPerson):
		dupList, dupCnt = [], 0
		for record in courseListPerPerson:
			index = courseListPerPerson.index(record)+1
			for crs in xrange(index,len(courseListPerPerson)):
				crsRecd = courseListPerPerson[crs]
				rec1, rec2 = record[3].replace(' ','') + record[4], crsRecd[3].replace(' ','') + crsRecd[4]
				if rec1 == rec2:
					if record[6] == crsRecd[6]:
						if record not in dupList:
							dupList.append(record)
					elif record[6] != '' and record[6] != 'DR':
						if crsRecd[6] == 'DR':
							if crsRecd not in dupList:
								dupList.append(crsRecd)
						elif len(crsRecd[6]) == 0:																	
							if record not in dupList:
								dupList.append(record)
						else:
							if record[8] > crsRecd[8]:
								if record not in dupList:
									dupList.append(record)
							else:
								if crsRecd not in dupList:
									dupList.append(crsRecd)
					elif len(record[6]) == 0:
						if record not in dupList:
							dupList.append(record)
					elif record[6] != 'DR':
						if crsRecd not in dupList:
							dupList.append(crsRecd)

		dupCnt = dupCnt + len(dupList)
		for record in dupList:
			if record in courseListPerPerson:
				courseListPerPerson.remove(record)

		return courseListPerPerson

	def formatRegSAS(self, regfile, noDupRegFile):
		fRegCSVRder = csv.reader(open(regfile), delimiter=',')
		fRegNodupWrter = csv.writer(open(noDupRegFile, 'w'))

		hearders = fRegCSVRder.next()
		# hearders.insert(2,'COURSE_CODE')
		fRegNodupWrter.writerow(hearders)

		newFlag, courseListPerPerson, vnum = False, [], ''
		cnt = userCnt = dupCnt = 0
		for row in fRegCSVRder:
			cnt = cnt + 1
			# to see if this course is the available technical course in the availabletechCrsList
			crs = row[3].replace(' ','')+row[4]
			if crs not in self.availableTechCrsList:
				continue
			# V_number: row[1]; Subject_code: row[3]; Course Number: row[4]; Grade_code: row[6]
			if len(courseListPerPerson) == 0:
				newFlag, vnum = False, row[1]
				userCnt = userCnt + 1
			elif row[1] != vnum:
				newFlag, vnum = True, row[1]
				userCnt = userCnt + 1

			if newFlag:
				newFlag = False
				# start to check the duplicate course records for this specific person
				if len(courseListPerPerson) > 0:
					for record in self.removeDup(courseListPerPerson):
						# record.insert(3,str(record[3])+str(record[4])); record[4] = str(record[4])
						# if len(record[8]) > 0:
						fRegNodupWrter.writerow(record)
				# after coping with duplicate records, clear the course list for new person's course records
				courseListPerPerson = []

			# collect course records for another person
			courseListPerPerson.append(row)

		if len(courseListPerPerson) > 0:
			for record in self.removeDup(courseListPerPerson):
				# record.insert(3,str(record[3])+str(record[4])); record[4] = str(record[4])
				# if len(record[8]) > 0:
				fRegNodupWrter.writerow(record)

	def simpleStats(self, noDupRegFile, CRSPERSTU, STUREGISTERED, EMPTY, CRS_STU, CRS_STU_GRADE, STU_CRS, STU_CRS_GRADE):
		fRegNodupRder = csv.reader(open(noDupRegFile), delimiter=',')
		# skip header
		header = fRegNodupRder.next()
		# count course frequency
		crsPerStu, crsFre, noGradeRecs, distinctCRSLst, distinctSTULst = {}, {}, [], [], []
		for record in fRegNodupRder:
			if record[1] not in distinctSTULst:
				distinctSTULst.append(record[1])
			course_code = record[3].replace(' ','')+record[4].replace(' ','')
			if course_code not in distinctCRSLst:
				distinctCRSLst.append(course_code)

			# record[1]:v_number; how many courses each students registered
			if record[1] in crsPerStu:
				crsPerStu[record[1]] = crsPerStu[record[1]] + 1
			else:
				crsPerStu[record[1]] = 1

			# course frequency; how many students each course was been registered
			if course_code in crsFre:
				crsFre[course_code] = crsFre[course_code] + 1
			else:
				crsFre[course_code] = 1

			if record[6] == '':
				noGradeRecs.append(record)
		
		# count how many courses registered for each student
		w = csv.writer(open(CRSPERSTU, 'w'))
		w.writerow(['V_NUMBER', '#Courses_registered'])
		w.writerows(crsPerStu.items())
		# count how many students for each course
		w = csv.writer(open(STUREGISTERED, 'w'))
		w.writerow(['Course', '#Students'])
		w.writerows(crsFre.items())
		# pickup the courses without grades
		w = csv.writer(open(EMPTY, 'w'))
		noGradeRecs.insert(0, header)
		w.writerows(noGradeRecs)
		"""
		# r = csv.reader(open(self.EMPTY), delimiter=',')
		# r.next()
		# uniStu, uniCrs = {}, {}
		# for record in r:
		# 	if record[1] not in uniStu:
		# 		uniStu[record[1]] = 1
		# 	else:
		# 		uniStu[record[1]] = uniStu[record[1]] + 1

		# 	course_code = record[3].replace(' ','') + record[4].replace(' ','')	
		# 	if course_code not in uniCrs:
		# 		uniCrs[course_code] = 1
		# 	else:
		# 		uniCrs[course_code] = uniCrs[course_code] + 1
		
		# # count the students who have courses without grades and how many no grade courses they have
		# w = csv.writer(open(self.EMPTY_STU, 'w'))
		# w.writerow(['V_NUMBER', '#_of_Courses_No_Grades'])
		# w.writerows(uniStu.items())
		# # count the #_of_students for the courses which were not assigned any grades
		# w = csv.writer(open(self.EMPTY_CRS, 'w'))
		# w.writerow(['Course', '#_of_Students_Reg_No_Grade'])
		# w.writerows(uniCrs.items())
		"""
		# create course list
		r = csv.reader(open(noDupRegFile), delimiter=',')
		# skip the header
		r.next()
		crsLst, crscodeLst, regLst, vnumLst = [], [], [], []

		# header: [subj_code, course_code, v_num1, v_num2, ......]
		header = ['SUBJECT_CODE', 'COURSE_NUMBER']
		for record in r:
			subj_code, course_code = record[3].replace(' ',''), record[4].replace(' ','')
			# reg: [v_num, subj_code, course_code, grade_point, grade_notation]
			regLst.append([record[1], subj_code, course_code, record[8], record[6]])
			crsCode = subj_code + course_code
			if crsCode not in crscodeLst:
				crscodeLst.append(crsCode)
				# cell: [subj_code, course_code, 'NA', ......]
				cell = [subj_code, course_code]
				for x in xrange(0,len(distinctSTULst)):
					# cell.append('NA')
					cell.append('')
				crsLst.append(cell)

			# header: [subj_code, course_code, v_num1, v_num2, ......]
			# vnumLst: [v_num1, v_num2, ......]
			if record[1] not in vnumLst:
				vnumLst.append(record[1])
				header.append(record[1])

		# create course matrix		
		w = csv.writer(open(CRS_STU, 'w'))
		w.writerow(header)
		wgrade = csv.writer(open(CRS_STU_GRADE, 'w'))
		wgrade.writerow(header)

		# matrix = [['' for x in range(len(distinctCRSLst))] for x in range(len(distinctSTULst))]
		for x in xrange(0,len(crscodeLst)):
			cell, crs_stu, crs_stu_grade = crsLst[x], [], []
			# copy cell into crs_stu, crs_stu_grade
			for item in crsLst[x]:
				crs_stu.append(item)
				crs_stu_grade.append(item)

			for y in xrange(0,len(regLst)):
				reg = regLst[y]
				# get the index of vnum in the vnumLst
				# vnumLst: [v_num1, v_num2, ......]
				indx = vnumLst.index(reg[0])
				# cell: [subj_code, course_code, 'NA', ......]
				# reg: [v_num, subj_code, course_code, grade_point, grade_notation]
				if (cell[0] == reg[1]) and (cell[1] == reg[2]):
					if reg[3] == '':
						# crs_stu[indx+2] = 'NG'
						# crs_stu_grade[indx+2] = 'NG'
						crs_stu[indx+2] = ''
						crs_stu_grade[indx+2] = ''
					else:
						crs_stu[indx+2] = reg[3]
						crs_stu_grade[indx+2] = reg[4]
			w.writerow(crs_stu)
			wgrade.writerow(crs_stu_grade)

		# create course matrix
		w = csv.writer(open(STU_CRS, 'w'))
		w1 = csv.writer(open(STU_CRS_GRADE, 'w'))
		# header: [v_num, crs1, crs2, ......]
		header = ['V_NUMBER']
		for crs in distinctCRSLst:
			header.append(crs)
		w.writerow(header)
		w1.writerow(header)

		# init rows
		rowLst, rowLst1 = [],[]
		for stu in distinctSTULst:
			# row: [v_num, 'NA', 'NA', ......]
			row = [stu]
			for y in xrange(0,len(distinctCRSLst)):
				# row.append('NA')
				row.append('')

			rowLst.append(row)
			rowLst1.append(row)

		# fill course grade point for each course		
		for row in rowLst:
			for reg in regLst:
				# row: [v_num, 'NA', 'NA', ......]
				# reg: [v_num, subj_code, course_code, grade_point, grade_notation]
				if row[0] == reg[0]:
					index = distinctCRSLst.index(reg[1]+reg[2])
					row[index+1] = reg[3]

			w.writerow(row)

		# fill course grade point for each course		
		for row in rowLst1:
			for reg in regLst:
				# row: [v_num, 'NA', 'NA', ......]
				# reg: [v_num, subj_code, course_code, grade_point, grade_notation]
				if row[0] == reg[0]:
					index = distinctCRSLst.index(reg[1]+reg[2])
					row[index+1] = reg[4]

			w1.writerow(row)

	def crsStuMatrix(self):
		# create course matrix and fill the blank grades
		reader = csv.reader(open(self.CRS_STU), delimiter=',')
		# skip the header
		header = reader.next()
		
		matrix, discardList = [], []
		# compute course average
		for row in reader:
			cnt, summation = 0, 0
			for item in row:
				if item.isdigit() and int(item) < 10:
					cnt = cnt + 1
					summation = summation + float(item)
			if cnt >= self.threshold:
				# insert course average grade
				row.insert(2,summation/cnt)
				matrix.append(row)
			else:
				discardList.append(row)
		
		# create course list whose frequency is less than self.threshold
		if len(discardList) > 0:
			w = csv.writer(open(self.discardList, 'w'))
			discardList.insert(0, header)
			w.writerows(discardList)
		# compute stu average grade
		tmp = zip(*matrix)
		a = list(tmp[0])
		a.insert(0,'STUAVE')
		tmp[0] = tuple(a)

		a = list(tmp[1])
		a.insert(0,'COURSE_NUMBER')
		tmp[1] = tuple(a)

		a = list(tmp[2])
		a.insert(0,'CRSAVE')
		tmp[2] = tuple(a)		
		
		for x in xrange(3,len(tmp)):
			summation, cnt = 0, 0
			for item in tmp[x]:
				if item.isdigit():
					cnt = cnt + 1
					summation = summation + float(item)
			a = list(tmp[x])
			a.insert(0, summation/cnt)
			tmp[x] = tuple(a)

		matrix = zip(*tmp)
		for x in xrange(0,len(matrix)):
			matrix[x] = list(matrix[x])
		
		# fill blank values
		stuave = matrix[0]
		for x in xrange(1,len(matrix)):
			row = matrix[x]
			for y in xrange(3,len(row)):
				if not row[y].isdigit():
					matrix[x][y] = (stuave[y]+row[2])/2

		header.insert(2, 'CRSAVE')
		matrix.insert(0,header)
		
		w = csv.writer(open(self.crsMatrix, 'w'))
		w.writerows(matrix)

	def corrPlot(self, source, corr):
		reader = csv.reader(open(source), delimiter=',')
		header = reader.next()

		matrix = []
		for row in reader:
			matrix.append(row)

		w = csv.writer(open(corr, 'w'))
		w.writerow(['xsubCode', 'xnum', 'ysubCode', 'ynum', 'coefficient', '#points', 'pValue', 'stderr', 'slope', 'intercept', 'a', 'b', 'c', 'R^2', 'xmin', 'xmax'])
		wnan = csv.writer(open(self.nancsv, 'w'))

		cnt, nocorrDict, nocommstuDict = 0, {}, {}
		nocorrlst = self.dataDir+'nocorr/no_corr_list.csv'
		nocommstulst = self.dataDir+'nocomstu/nocomstu_list.csv'
		wnocorrlst, wnocommstulst, nocomList, noCorrListTable = '', '', [], []

		rlist, plist = [],[]
		for x in xrange(0,len(matrix)):
			# course is a row with all marks
			course = matrix[x]
			# the first character of the course number, which indicates which year the course is designed, e.g.:1,2,3,4
			yr = course[1][0]
			noCorrList, nocommstuList = [], []
			for y in xrange(0,len(matrix)):
				newCourse = matrix[y]
				newYr = newCourse[1][0]
				if int(yr) < int(newYr) and int(yr) < 3:
					cnt += 1
					xaxis, yaxis = course[0]+' '+course[1]+' Grades', newCourse[0]+' '+newCourse[1]+' Grades'

					xdata, ydata = [], []
					if source == self.crsMatrix:
						xdata, ydata= map(float, course[3:]), map(float, newCourse[3:])
					else:
						for index in xrange(2, len(course)):
							ix, iy = course[index], newCourse[index]
							if ix.isdigit() and iy.isdigit():
								xdata.append(float(ix))
								ydata.append(float(iy))

						if len(xdata) == 0:
							cnt += 1
							nocommstuList.append(newCourse)
							nocomList.append([course[0]+' '+course[1], newCourse[0]+' '+newCourse[1]])
							print 'cnt:',cnt,'no common students course pair,', 'len:', len(ydata), course[0],course[1],'vs',newCourse[0],newCourse[1],'trainYrs:', self.trainYrsText, 'Thresh:', self.threshold
							continue

					if len(xdata) < self.threshold:
						cnt += 1
						print 'cnt:',cnt,'less than threshold course pair,', 'len:', len(ydata), course[0],course[1],'vs',newCourse[0],newCourse[1],'trainYrs:', self.trainYrsText, 'Thresh:', self.threshold
						continue

					(r, p) = pearsonr(xdata, ydata)
					if str(r) == 'nan':
						noCorrList.append(newCourse)
						cnt += 1
						print 'cnt:',cnt,'no Pearson r course pair,', 'len:', len(ydata), course[0],course[1],'vs',newCourse[0],newCourse[1],'trainYrs:', self.trainYrsText, 'Thresh:', self.threshold
						wnan.writerow([course[0]+course[1],newCourse[0]+newCourse[1],'len:',len(ydata)])
						wnan.writerow([course[0]+course[1]]+xdata)
						wnan.writerow([newCourse[0]+newCourse[1]]+ydata)
						wnan.writerow([])
						continue

					# slope, intercept, r_value, p_value, std_err = linregress(xdata, ydata)
					# format the parameters precision
					slope, intercept, r_value, p_value, std_err = linregress(xdata, ydata)
					r, slope, intercept, r_value, p_value, std_err = [float(format(r, '.4f')), float(format(slope, '.4f')), float(format(intercept, '.4f')), float(format(r_value, '.4f')), float(format(p_value, '.4f')), float(format(std_err, '.4f'))]

					# r_value = float(format(r, '.4f'))
					slope, intercept = self.regressionPlot(xdata, ydata, r_value, 1, xaxis, yaxis, self.linear_plots_ori, len(ydata))
					a,b,c = self.regressionPlot(xdata, ydata, r_value, 2, xaxis, yaxis, self.quadratic_plots_ori, len(ydata))

					slope, intercept, a, b, c = [float(format(slope, '.4f')), float(format(intercept, '.4f')), float(format(a, '.4f')), float(format(b, '.4f')), float(format(c, '.4f'))]

					w.writerow([course[0], course[1], newCourse[0], newCourse[1], r, len(ydata), p_value, std_err, slope, intercept, a, b, c, r*r, min(xdata), max(xdata)])
					rlist.append(r_value)
					plist.append(len(ydata))
					print 'cnt:', cnt, course[0], course[1], 'vs', newCourse[0], newCourse[1], 'len:', len(ydata), 'r:', r, 'r_value:', r_value, 'slope:', slope, 'trainYrs:', self.trainYrsText, 'Thresh:', self.threshold

			if len(noCorrList) > 0:
				if not os.path.exists(self.dataDir+'nocorr/'):
					os.makedirs(self.dataDir+'nocorr/')

				nocorrDict[course[0]+course[1]] = len(noCorrList)
				# count the grades of the two courses taken by the students
				lst = []
				for record in noCorrList:
					cnt1 = 0
					for indx in xrange(2,len(course)):
						if record[indx].isdigit() and course[indx].isdigit():
							cnt1 += 1
					lst.append([course[0], course[1], record[0], record[1], cnt1])

				noCorrList.insert(0, course)
				if wnocorrlst == '':
					wnocorrlst = csv.writer(open(nocorrlst, 'w'))
				wnocorrlst.writerows(noCorrList)
				
				wnocorrlst.writerow([])
				lst.sort(key=itemgetter(4), reverse=True)
				wnocorrlst.writerows(lst)
				wnocorrlst.writerow([])

				noCorrListTable.append(['Course_1', 'Course_2', '#Student'])
				[noCorrListTable.append([item[0]+' '+item[1], item[2]+' '+item[3], item[4]]) for item in lst]
				noCorrListTable.append([])

			if len(nocommstuList) > 0:
				if not os.path.exists(self.dataDir+'nocomstu/'):
					os.makedirs(self.dataDir+'nocomstu/')

				nocommstuDict[course[0] + course[1]] = len(nocommstuList)
				nocommstuList.insert(0, course)

				if wnocommstulst == '':
					wnocommstulst = csv.writer(open(nocommstulst, 'w'))
				wnocommstulst.writerows(nocommstuList)
				wnocommstulst.writerow([])

				wnocommstulst.writerow(['COURSE_1', 'COURSE_2'])
				wnocommstulst.writerow([course[0]+course[1], nocommstuList[1][0]+nocommstuList[1][1]])
				for indx in xrange(2,len(nocommstuList)):
					wnocommstulst.writerow(['', nocommstuList[indx][0]+nocommstuList[indx][1]])
				wnocommstulst.writerow([])

		self.coefficientPointsPlot(rlist, plist)

		if len(nocorrDict) > 0:
			nocorr = self.dataDir+'nocorr/no_corr_list_fre.csv'
			wnocorr = csv.writer(open(nocorr, 'w'))
			wnocorr.writerow(['Course', '#Course'])
			wnocorr.writerows(nocorrDict.items())

		if len(nocommstuDict) > 0:
			nocommstu = self.dataDir+'nocomstu/nocomstu_list_fre.csv'
			wnocom = csv.writer(open(nocommstu, 'w'))
			wnocom.writerow(['Course', '#Course'])
			wnocom.writerows(nocommstuDict.items())

		if len(noCorrListTable) > 0:
			wnocorrlst.writerows(noCorrListTable)

		if len(nocommstuList) > 0:
			wnocommstulst.writerow([])
			nocomList.sort(key=itemgetter(0), reverse=True)
			freq = Counter(item[0] for item in nocomList)
			nocomList = sorted(nocomList, key=lambda i: freq[i[0]], reverse=True)

			isHeader = True
			for indx in xrange(0, len(nocomList)):
				if isHeader:
					wnocommstulst.writerow(nocomList[indx])
					isHeader = False
				else:
					wnocommstulst.writerow(['', nocomList[indx][1]])

				if (indx < len(nocomList)-1) and (nocomList[indx][0] != nocomList[indx+1][0]):
					isHeader = True

	def corrPlotOneProPredictor(self, source, corr):
		reader = csv.reader(open(source), delimiter=',')
		# skip header
		header = reader.next()

		matrix, proPredictorCourse = [], ''
		proPredictorSubj, proPredictorNum = self.proPredictor.split(' ')
		for row in reader:
			matrix.append(row)
			if (proPredictorSubj == row[0]) and (proPredictorNum == row[1]):
				proPredictorCourse = row

		w = csv.writer(open(corr, 'w'))
		w.writerow(['xsubCode', 'xnum', 'ysubCode', 'ynum', 'coefficient', '#points', 'Pxy', 'pValue', 'stderr', 'slope', 'intercept', 'a', 'b', 'c', 'R^2', 'xmin', 'xmax'])
		wnan = csv.writer(open(self.nancsv, 'w'))

		cnt, nocorrDict, nocommstuDict = 0, {}, {}
		nocorrlst = self.dataDir+'nocorr/no_corr_list.csv'
		nocommstulst = self.dataDir+'nocomstu/nocomstu_list.csv'
		wnocorrlst, wnocommstulst, nocomList, noCorrListTable = '', '', [], []

		rlist, plist = [],[]
		for x in xrange(0,len(matrix)):
			# course is a row with all marks
			newCourse = matrix[x]
			# the first character of the course number, which indicates which year the course is designed, e.g.:1,2,3,4
			yr = newCourse[1][0]
			proPredictorYr = proPredictorNum[0]
			noCorrList, nocommstuList = [], []

			if int(yr) > int(proPredictorYr):
				cnt += 1
				xaxis, yaxis =  proPredictorCourse[0]+' '+proPredictorCourse[1]+' Grades', newCourse[0]+' '+newCourse[1]+' Grades'

				xdata, ydata = [], []
				for index in xrange(2, len(newCourse)):
					ix, iy = proPredictorCourse[index], newCourse[index]
					if ix.isdigit() and iy.isdigit():
						xdata.append(float(ix))
						ydata.append(float(iy))

				if len(xdata) == 0:
					cnt += 1
					nocommstuList.append(newCourse)
					nocomList.append([proPredictorCourse[0]+' '+proPredictorCourse[1], newCourse[0]+' '+newCourse[1]])
					print 'cnt:',cnt,'no common students course pair,', 'len:', len(ydata), proPredictorCourse[0],proPredictorCourse[1],'vs',newCourse[0],newCourse[1],'Predictor:', self.proPredictor, 'Thresh:', self.threshold
					continue

				if len(xdata) < self.threshold:
					cnt += 1
					print 'cnt:',cnt,'less than threshold course pair,', 'len:', len(ydata), proPredictorCourse[0],proPredictorCourse[1],'vs',newCourse[0],newCourse[1],'Predictor:', self.proPredictor, 'Thresh:', self.threshold
					continue

				(r, p) = pearsonr(xdata, ydata)
				if str(r) == 'nan':
					noCorrList.append(newCourse)
					cnt += 1
					print 'cnt:',cnt,'no Pearson r course pair,', 'len:', len(ydata), proPredictorCourse[0],proPredictorCourse[1],'vs',newCourse[0],newCourse[1],'Predictor:', self.proPredictor, 'Thresh:', self.threshold
					wnan.writerow([proPredictorCourse[0]+proPredictorCourse[1],newCourse[0]+newCourse[1],'len:',len(ydata)])
					wnan.writerow([proPredictorCourse[0]+proPredictorCourse[1]]+xdata)
					wnan.writerow([newCourse[0]+newCourse[1]]+ydata)
					wnan.writerow([])
					continue

				# slope, intercept, r_value, p_value, std_err = linregress(xdata, ydata)
				# format the parameters precision
				slope, intercept, r_value, p_value, std_err = linregress(xdata, ydata)
				r, slope, intercept, r_value, p_value, std_err = [float(format(r, '.4f')), float(format(slope, '.4f')), float(format(intercept, '.4f')), float(format(r_value, '.4f')), float(format(p_value, '.4f')), float(format(std_err, '.4f'))]

				# r_value = float(format(r, '.4f'))
				slope, intercept = self.regressionPlot(xdata, ydata, r_value, 1, xaxis, yaxis, self.linear_plots_ori, len(ydata))
				a,b,c = self.regressionPlot(xdata, ydata, r_value, 2, xaxis, yaxis, self.quadratic_plots_ori, len(ydata))

				slope, intercept, a, b, c = [float(format(slope, '.4f')), float(format(intercept, '.4f')), float(format(a, '.4f')), float(format(b, '.4f')), float(format(c, '.4f'))]

				w.writerow([proPredictorCourse[0], proPredictorCourse[1], newCourse[0], newCourse[1], r, len(ydata), 0, p_value, std_err, slope, intercept, a, b, c, r*r, min(xdata), max(xdata)])
				rlist.append(r_value)
				plist.append(len(ydata))
				print 'cnt:', cnt, proPredictorCourse[0], proPredictorCourse[1], 'vs', newCourse[0], newCourse[1], 'len:', len(ydata), 'r:', r, 'r_value:', r_value, 'slope:', slope, 'Predictor:', self.proPredictor, 'Thresh:', self.threshold

		if len(noCorrList) > 0:
			if not os.path.exists(self.dataDir+'nocorr/'):
				os.makedirs(self.dataDir+'nocorr/')

			nocorrDict[proPredictorCourse[0]+proPredictorCourse[1]] = len(noCorrList)
			# count the grades of the two courses taken by the students
			lst = []
			for record in noCorrList:
				cnt1 = 0
				for indx in xrange(2,len(proPredictorCourse)):
					if record[indx].isdigit() and proPredictorCourse[indx].isdigit():
						cnt1 += 1
				lst.append([proPredictorCourse[0], proPredictorCourse[1], record[0], record[1], cnt1])

			noCorrList.insert(0, proPredictorCourse)
			if wnocorrlst == '':
				wnocorrlst = csv.writer(open(nocorrlst, 'w'))
			wnocorrlst.writerows(noCorrList)
			
			wnocorrlst.writerow([])
			lst.sort(key=itemgetter(4), reverse=True)
			wnocorrlst.writerows(lst)
			wnocorrlst.writerow([])

			noCorrListTable.append(['Course_1', 'Course_2', '#Student'])
			[noCorrListTable.append([item[0]+' '+item[1], item[2]+' '+item[3], item[4]]) for item in lst]
			noCorrListTable.append([])

		if len(nocommstuList) > 0:
			if not os.path.exists(self.dataDir+'nocomstu/'):
				os.makedirs(self.dataDir+'nocomstu/')

			nocommstuDict[proPredictorCourse[0] + proPredictorCourse[1]] = len(nocommstuList)
			nocommstuList.insert(0, proPredictorCourse)

			if wnocommstulst == '':
				wnocommstulst = csv.writer(open(nocommstulst, 'w'))
			wnocommstulst.writerows(nocommstuList)
			wnocommstulst.writerow([])

			wnocommstulst.writerow(['COURSE_1', 'COURSE_2'])
			wnocommstulst.writerow([proPredictorCourse[0]+proPredictorCourse[1], nocommstuList[1][0]+nocommstuList[1][1]])
			for indx in xrange(2,len(nocommstuList)):
				wnocommstulst.writerow(['', nocommstuList[indx][0]+nocommstuList[indx][1]])
			wnocommstulst.writerow([])

		self.coefficientPointsPlot(rlist, plist)

		if len(nocorrDict) > 0:
			nocorr = self.dataDir+'nocorr/no_corr_list_fre.csv'
			wnocorr = csv.writer(open(nocorr, 'w'))
			wnocorr.writerow(['Course', '#Course'])
			wnocorr.writerows(nocorrDict.items())

		if len(nocommstuDict) > 0:
			nocommstu = self.dataDir+'nocomstu/nocomstu_list_fre.csv'
			wnocom = csv.writer(open(nocommstu, 'w'))
			wnocom.writerow(['Course', '#Course'])
			wnocom.writerows(nocommstuDict.items())

		if len(noCorrListTable) > 0:
			wnocorrlst.writerows(noCorrListTable)

		if len(nocommstuList) > 0:
			wnocommstulst.writerow([])
			nocomList.sort(key=itemgetter(0), reverse=True)
			freq = Counter(item[0] for item in nocomList)
			nocomList = sorted(nocomList, key=lambda i: freq[i[0]], reverse=True)

			isHeader = True
			for indx in xrange(0, len(nocomList)):
				if isHeader:
					wnocommstulst.writerow(nocomList[indx])
					isHeader = False
				else:
					wnocommstulst.writerow(['', nocomList[indx][1]])

				if (indx < len(nocomList)-1) and (nocomList[indx][0] != nocomList[indx+1][0]):
					isHeader = True

	def coefficientPointsPlot(self, rlist, plist):
		fig = plt.figure()
		xarray, yarray = np.array(plist), np.array(rlist)
		plt.plot(xarray, yarray, '.', c='r')

		plt.ylim(-1.0, 1.0)
		ticks = np.linspace(-1.0, 1.0, 20, endpoint=False).tolist()
		ticks.append(1.0)

		plt.xlim(0, 120)
		ticks = xrange(0, 120, 10)
		plt.xticks(ticks)

		plt.xlabel('Number of sample points')
		plt.ylabel('Pearson Coefficient')

		if self.proPredictor == 'ALL':
			plt.title('Pearson Coefficient vs Number of sample points \nfrom '+self.trainYrsText)
		else:
			plt.title('Pearson Coefficient vs Number of sample points \nusing predictor '+self.proPredictor)
		plt.grid(True)

		figName = self.currDir + 'RvsP.png'
		fig.savefig(figName)
		plt.close(fig)

	def regressionPlot(self, xdata, ydata, r_value, power, xaxis, yaxis, plotDir, points):
		fig = plt.figure()
		xarray, yarray = np.array(xdata), np.array(ydata)
		z = np.polyfit(xarray, yarray, power)
		p = np.poly1d(z)

		if power == 1:
			slope, intercept = z
			slope, intercept = [float(format(slope, '.4f')), float(format(intercept, '.4f'))]
			if r_value != 0.0:
				if intercept > 0:
					# plt.title(r'$r = $' + str(r_value) + r'$, y = $' + str(slope) + r'$x+$'+ str(intercept))
					plt.title(r'$r=%s,y=%sx+%s$'%(r_value, slope, intercept)+r'$;Points:%s$'%(points))
				elif intercept < 0:
					# plt.title(r'$r = $' + str(r_value) + r'$, y = $' + str(slope) + r'$x$' + str(intercept))
					plt.title(r'$r=%s,y=%sx%s$'%(r_value, slope, intercept)+r'$;Points:%s$'%(points))
				else:
					plt.title(r'$r=%s,y=%sx$'%(r_value, slope)+r'$;Points:%s$'%(points))
			else:
				# plt.title(r'$r = $' + str(r_value) + r'$, y = $' + str(intercept))
				plt.title(r'$r=%s,y=%s$'%(r_value, intercept)+r'$;Points:%s$'%(points))
		elif power == 2:
			a, b, c = z
			a, b, c = [float(format(a, '.4f')), float(format(b, '.4f')), float(format(c, '.4f'))]
			if a == 0:
				if b > 0:
					if c > 0:
						# plt.title(r'$r=$' + str(r_value) + r'$, y = $' + str(a) + r'$x^2$' + r'$+$' + str(b) + r'$x$' + r'$+$' + str(c))
						plt.title(r'$r=%s,y=%sx+%s$'%(r_value, b, c)+r'$;Points:%s$'%(points))
					elif c < 0:
						# plt.title(r'$r = $' + str(r_value) + r'$, y = $' + str(a) + r'$x^2$' + r'$+$' + str(b) + r'$x$' + str(c))
						plt.title(r'$r=%s,y=%sx%s$'%(r_value, b, c)+r'$;Points:%s$'%(points))
					else:
						# plt.title(r'$r = $' + str(r_value) + r'$, y = $' + str(a) + r'$x^2$' + r'$+$' + str(b))
						plt.title(r'$r=%s,y=%sx$'%(r_value, b)+r'$;Points:%s$'%(points))
				elif b < 0:
					if c > 0:
						# plt.title(r'$r=$' + str(r_value) + r'$, y = $' + str(a) + r'$x^2$' + r'$+$' + str(b) + r'$x$' + r'$+$' + str(c))
						plt.title(r'$r=%s,y=%sx+%s$'%(r_value, b, c)+r'$;Points:%s$'%(points))
					elif c < 0:
						# plt.title(r'$r = $' + str(r_value) + r'$, y = $' + str(a) + r'$x^2$' + r'$+$' + str(b) + r'$x$' + str(c))
						plt.title(r'$r=%s,y=%sx%s$'%(r_value, b, c)+r'$;Points:%s$'%(points))
					else:
						# plt.title(r'$r = $' + str(r_value) + r'$, y = $' + str(a) + r'$x^2$' + r'$+$' + str(b))
						plt.title(r'$r=%s,y=%sx$'%(r_value, b)+r'$;Points:%s$'%(points))
				else:
					if c > 0:
						# plt.title(r'$r=$' + str(r_value) + r'$, y = $' + str(a) + r'$x^2$' + r'$+$' + str(b) + r'$x$' + r'$+$' + str(c))
						plt.title(r'$r=%s,y=%s$'%(r_value, c)+r'$;Points:%s$'%(points))
					elif c < 0:
						# plt.title(r'$r = $' + str(r_value) + r'$, y = $' + str(a) + r'$x^2$' + r'$+$' + str(b) + r'$x$' + str(c))
						plt.title(r'$r=%s,y=%s$'%(r_value, c)+r'$;Points:%s$'%(points))
					# else:
						# plt.title(r'$r = $' + str(r_value) + r'$, y = $' + str(a) + r'$x^2$' + r'$+$' + str(b))
						# plt.title(r'$r=%s,x=%s$'%(r_value))
			else:
				if b > 0:
					if c > 0:
						# plt.title(r'$r=$' + str(r_value) + r'$, y = $' + str(a) + r'$x^2$' + r'$+$' + str(b) + r'$x$' + r'$+$' + str(c))
						plt.title(r'$r=%s,y=%sx^2+%sx+%s$'%(r_value, a, b, c)+r'$;Points:%s$'%(points))
					elif c < 0:
						# plt.title(r'$r = $' + str(r_value) + r'$, y = $' + str(a) + r'$x^2$' + r'$+$' + str(b) + r'$x$' + str(c))
						plt.title(r'$r=%s,y=%sx^2+%sx%s$'%(r_value, a, b, c)+r'$;Points:%s$'%(points))
					else:
						# plt.title(r'$r = $' + str(r_value) + r'$, y = $' + str(a) + r'$x^2$' + r'$+$' + str(b))
						plt.title(r'$r=%s,y=%sx^2+%sx$'%(r_value, a, b)+r'$;Points:%s$'%(points))
				elif b < 0:
					if c > 0:
						# plt.title(r'$r=$' + str(r_value) + r'$, y = $' + str(a) + r'$x^2$' + r'$+$' + str(b) + r'$x$' + r'$+$' + str(c))
						plt.title(r'$r=%s,y=%sx^2%sx+%s$'%(r_value, a, b, c)+r'$;Points:%s$'%(points))
					elif c < 0:
						# plt.title(r'$r = $' + str(r_value) + r'$, y = $' + str(a) + r'$x^2$' + r'$+$' + str(b) + r'$x$' + str(c))
						plt.title(r'$r=%s,y=%sx^2%sx%s$'%(r_value, a, b, c)+r'$;Points:%s$'%(points))
					else:
						# plt.title(r'$r = $' + str(r_value) + r'$, y = $' + str(a) + r'$x^2$' + r'$+$' + str(b))
						plt.title(r'$r=%s,y=%sx^2%sx$'%(r_value, a, b)+r'$;Points:%s$'%(points))
				else:
					if c > 0:
						# plt.title(r'$r=$' + str(r_value) + r'$, y = $' + str(a) + r'$x^2$' + r'$+$' + str(b) + r'$x$' + r'$+$' + str(c))
						plt.title(r'$r=%s,y=%sx^2+%s$'%(r_value, a, c)+r'$;Points:%s$'%(points))
					elif c < 0:
						# plt.title(r'$r = $' + str(r_value) + r'$, y = $' + str(a) + r'$x^2$' + r'$+$' + str(b) + r'$x$' + str(c))
						plt.title(r'$r=%s,y=%sx^2%s$'%(r_value, a, c)+r'$;Points:%s$'%(points))
					else:
						# plt.title(r'$r = $' + str(r_value) + r'$, y = $' + str(a) + r'$x^2$' + r'$+$' + str(b))
						plt.title(r'$r=%s,y=%sx^2$'%(r_value, a)+r'$;Points:%s$'%(points))

		xp = np.linspace(0, 9, 100)
		plt.plot(xarray, yarray, 'bo', xp, p(xp), '-')

		plt.xlabel(xaxis)
		plt.ylabel(yaxis)

		plt.ylim(0,9)
		plt.grid(True)

		subj, num = xaxis.split(' ')[:2]
		subjNew, numNew = yaxis.split(' ')[:2]

		# create Predicting course folder
		folder = plotDir + subjNew + numNew
		if not os.path.exists(folder):
			os.makedirs(folder)

		figName = folder + '/' + subj + num + ' ' + subjNew + numNew + ' ' + str(r_value) + ' ' + str(points) + '.png'
		fig.savefig(figName)
		plt.close(fig)

		return z

	def predictorsScatterPlots(self):
		self.quadratic_plots_ori
		self.linear_plots_ori

		top1Predictors = ''
		if self.proPredictor == 'ALL':
			top1Predictors = self.predictorsDict[self.factor][0]
		else:
			top1Predictors = self.top1FactorsFile

		r = csv.reader(open(top1Predictors), delimiter=',')
		r.next()
		for item in r:
			subj, num, subjNew, numNew, r, p = item[:6]
			fname = subj + num + ' ' + subjNew + numNew + ' ' + r + ' ' + p + '.png'
			figNameL = self.linear_plots_ori + subjNew + numNew + '/' + fname
			figNameQ = self.quadratic_plots_ori + subjNew + numNew + '/' + fname
			if num[0] == '1':
				if numNew[0] == '2':
					shutil.copy2(figNameL, self.yr1l + '2/' + fname)
					shutil.copy2(figNameQ, self.yr1q + '2/' + fname)
				if numNew[0] == '3':
					shutil.copy2(figNameL, self.yr1l + '3/' + fname)
					shutil.copy2(figNameQ, self.yr1q + '3/' + fname)
				if numNew[0] == '4':
					shutil.copy2(figNameL, self.yr1l + '4/' + fname)
					shutil.copy2(figNameQ, self.yr1q + '4/' + fname)
			elif num[0] == '2':
				if numNew[0] == '3':
					shutil.copy2(figNameL, self.yr2l + '3/' + fname)
					shutil.copy2(figNameQ, self.yr2q + '3/' + fname)
				if numNew[0] == '4':
					shutil.copy2(figNameL, self.yr2l + '4/' + fname)
					shutil.copy2(figNameQ, self.yr2q + '4/' + fname)

	def coefficientHist(self, interval, histDir, corr):
		if not os.path.exists(histDir):
			os.makedirs(histDir)

		reader = csv.reader(open(corr), delimiter = ',')
		reader.next()
		x = []
		for row in reader:
			x.append(float(row[4]))

		fig = plt.figure()
		bins = np.arange(-1.0, 1.5, interval)
		plt.title('Histogram of Coefficients with interval ' + str(interval), fontsize='large')
		plt.xlabel('Pearson Correlation Coefficient')
		# plt.xlabel('Bins')
		plt.ylabel('Frequency')
		plt.grid(True)
		
		# bins = [float(format(bins[i], '.2f')) for i in range(len(bins))]
		n, bins, patches = plt.hist(x, bins, normed=0, histtype='bar')

		figName = histDir + 'hist_' + 'interval_' + str(interval) + '.png'
		fig.savefig(figName)
		# plt.show()
		plt.close(fig)

	def courseBarPlots(self, barDir, corr):
		# figPath = self.currDir + 'bars_ave/'
		if not os.path.exists(barDir):
			os.makedirs(barDir)

		# create course list
		reader = csv.reader(open(corr), delimiter = ',')
		reader.next()
		crsList = []
		for row in reader:
			crs = row[0]+' '+row[1]
			if crs not in crsList:
				crsList.append(crs)
		
		for item in crsList:
			x = []
			xx = []
			y = []
			cnt = 0
			negative = 0
			reader = csv.reader(open(corr), delimiter = ',')
			reader.next()
			for row in reader:
				crs = row[0]+' '+row[1]
				if item == crs:
					x.append(row[2]+row[3])
					xx.append(int(cnt))
					cnt = cnt + 1
					y.append(float(row[4]))
					if float(row[4]) < 0:
						negative = 1
			if len(x) > 0:
				fig = plt.figure()
				plt.title(item)
				# plt.xlabel(xaxis)
				plt.ylabel('Pearson Coefficient')

				if negative == 1:
					plt.axis([-1, len(x), -0.3, 0.8])
				else:
					plt.axis([-1, len(x), 0, 0.8])

				sortedArr = self.sortCourse(x, y)

				rects = plt.bar(xx, sortedArr[1], align='center', color='grey')
				ind = 0
				for rect in rects:
					xloc = rect.get_x()
					yloc = 0
					if y[ind] < 0:
						yloc = (-1)*rect.get_height()-0.02
					else:
						yloc = rect.get_y() + rect.get_height()+0.02
					plt.text(xloc, yloc, str(format(y[ind], '.2f')), verticalalignment='center', fontsize='xx-small')
					ind = ind + 1

				plt.xticks(xx,sortedArr[0],rotation=80, fontsize='xx-small')
				# plt.grid(True)
				# plt.show()
				figName = barDir + item + '.png'
				fig.savefig(figName)
				plt.close(fig)

	def studentBarPlots(self, noDupRegFile):
		figPath = self.currDir + 'students/'
		if not os.path.exists(figPath):
			os.makedirs(figPath)

		reader = csv.reader(open(noDupRegFile), delimiter = ',')
		reader.next()
		students = []
		for row in reader:
			student = row[1]
			if student not in students:
				students.append(student)

		for student in students:
			x = []
			xx = []
			cnt = 0
			y = []			
			reader = csv.reader(open(noDupRegFile), delimiter = ',')
			reader.next()
			for row in reader:
				if row[1] == student:
					if len(row[8]) > 0:
						crs = row[3]+row[4]
						x.append(crs)
						xx.append(cnt)
						cnt = cnt + 1
						# grade point
						y.append(int(row[8]))
			if len(x) > 0:
				fig = plt.figure()
				plt.title(student)
				# plt.xlabel(xaxis)
				plt.ylabel('Grade Point Value')
				plt.axis([-1, len(x), 0, 10])
				
				sortedArr = self.sortCourse(x, y)
				
				rects = plt.bar(xx, sortedArr[1], align='center', color='grey')
				ind = 0
				for rect in rects:
					xloc = rect.get_x() + rect.get_width()/2
					yloc = 0
					yloc = rect.get_y() + rect.get_height() + rect.get_width()/3
					plt.text(xloc, yloc, str(y[ind]), verticalalignment='center', horizontalalignment='center', fontsize='xx-small')
					ind = ind + 1

				plt.xticks(xx,sortedArr[0],rotation=80, fontsize='xx-small')
				plt.grid(True)
				# plt.show()
				figName = figPath + student + '.png'
				fig.savefig(figName)
				plt.close(fig)

	def uniqueCourseList(self):
		reader = csv.reader(open(self.regNODUP), delimiter = ',')
		reader.next()
		freq = {}
		for row in reader:
			crs = row[3].replace(' ','')+row[4]
			if crs not in freq:
				freq[crs] = 1
			else:
				freq[crs] = freq[crs] + 1
		
		# print freq, '\n', len(freq)
		
		reader = csv.reader(open(self.regNODUP), delimiter = ',')
		reader.next()
		crsLst = []

		writer = csv.writer(open(self.courselist, 'w'))
		writer.writerow(['SUBJECT_CODE', 'COURSE_NUMBER', 'FREQUENCY', 'YEAR'])
		for row in reader:
			crs = row[3].replace(' ','')+row[4]
			if (crs not in crsLst):
				crsLst.append(crs)
				writer.writerow([row[3].replace(' ', ''), row[4], freq[crs], row[4][0]])

	def uniqueTechCrsList(self):
		creader = csv.reader(open(self.courselist), delimiter = ',')
		header = creader.next()

		treader = csv.reader(open(self.allTechCrs), delimiter = ',')
		techCrsList = []
		for row in treader:
			techCrsList.append(row[0]+row[1])

		writer = csv.writer(open(self.uniTechCrsList, 'w'))
		writer.writerow(header)
		for row in creader:
			crs = row[0].replace(' ','')+row[1]
			if crs in techCrsList:
				writer.writerow(row)
		
	def sortCourse(self, courses, values):
		for i in xrange(0,len(courses)):
			for j in xrange(i+1,len(courses)):
				ilastChar, jlastChar, icrn, jcrn = courses[i][-1], courses[j][-1], 0, 0
				if ilastChar.isdigit():
					icrn = int(courses[i][-3:])
				else:
					icrn = int(courses[i][-4:-1])

				if jlastChar.isdigit():
					jcrn = int(courses[j][-3:])
				else:
					jcrn = int(courses[j][-4:-1])

				if jcrn < icrn:
					itmp = courses[i]
					courses[i] = courses[j]
					courses[j] = itmp
					jtmp = values[i]
					values[i] = values[j]
					values[j] = jtmp

		return [courses, values]

	def corrMatrix(self, matrix, corrSeq):
		corrdir, corr, corrf = '', 1, 2
		if corrSeq == 12:
			corrdir = self.currDir+'12/'
		elif corrSeq == 23:
			corrdir, corr, corrf = self.currDir+'23/', 2, 3
		else:
			return

		if not os.path.exists(corrdir):
			os.makedirs(corrdir)
		for x in xrange(2,len(matrix)):
			if int(matrix[x][1][0]) == corr:
				name, lst = corrdir + matrix[x][0] + matrix[x][1] + '.csv', []
				lst.append(matrix[x])
				for y in xrange(2,len(matrix)):
					if int(matrix[y][1][0]) == corrf:
						lst.append(matrix[y])
				if len(lst) > 2:
					w = csv.writer(open(name, 'w'))
					w.writerows(lst)

	def techCrs(self):
		# reader = csv.reader(open(self.techCrsFile), delimiter = ',')
		reader = csv.reader(open(self.allTechCrs), delimiter = ',')
		# reader.next()
		techCrsList = []
		for row in reader:
			techCrsList.append(row[0]+row[1])

		r = csv.reader(open(self.regDataPath), delimiter=',')
		techWrter = csv.writer(open(self.techCrsCSV, 'w'))

		hearders = r.next()
		# hearders.insert(2,'COURSE_CODE')
		techWrter.writerow(hearders)
		for row in r:
			crs = row[3].replace(' ','')+row[4]
			if crs in techCrsList:
				techWrter.writerow(row)
				# save the available technical course list for future use
				if crs not in self.availableTechCrsList:
					self.availableTechCrsList.append(crs)

	def techCrsHist(self, interval):
		figPath = self.currDir+'crs_hist/'
		if not os.path.exists(figPath):
			os.makedirs(figPath)

		reader = csv.reader(open(self.uniTechCrsList), delimiter = ',')
		reader.next()
		x = []
		for row in reader:
			x.append(int(row[2]))

		fig = plt.figure()
		bins = np.arange(0, 50, interval)
		plt.axis([0, 45, 0, 30])
		# plt.title('Technical Course Histogram with Bin = ' + str(interval), fontsize='large')
		plt.title('Histogram of students with Bin = '+str(interval), fontsize='large')
		plt.xlabel('Number of students who registered the technical course')
		plt.ylabel('Frequency')
		plt.grid(True)
		
		# bins = [ int(bins[i]) for i in range(len(bins)) ]
		n, bins, patches = plt.hist(x, bins, normed=0, histtype='bar')

		figName = figPath+'registered_Fre_hist_'+'interval_'+str(interval)+'.png'
		fig.savefig(figName)
		# plt.show()
		plt.close(fig)

	def pairs(self):
		proPredictorSubj = proPredictorNum = ''
		if not (self.proPredictor == 'ALL'):
			proPredictorSubj, proPredictorNum = self.proPredictor.split(' ')

		reader = csv.reader(open(self.CRS_STU), delimiter = ',')
		reader.next()

		matrix, proPredictor = [],''
		for row in reader:
			matrix.append(row)
			if (proPredictorSubj == row[0].replace(' ','')) and (proPredictorNum == row[1]):
				proPredictor = row

		w = csv.writer(open(self.pairsFrequency, 'w'))
		w.writerow(['xcode', 'xnum', 'ycode', 'ynum', 'pairs'])

		if self.proPredictor == 'ALL':
			for x in matrix:
				for y in matrix:
					if int(x[1][0]) < int(y[1][0]) and int(x[1][0]) < 3:
						cnt = 0
						for index in xrange(2,len(x)):
							if x[index].isdigit() and y[index].isdigit():
								cnt = cnt + 1
						# print x[0], ' ', x[1], ' vs ', y[0], ' ', y[1], ' cnt: ', cnt
						w.writerow([x[0], x[1], y[0], y[1], cnt])
		else:
			for x in matrix:
				if int(x[1][0]) > int(proPredictorNum[0]):
					cnt = 0
					for index in xrange(2,len(x)):
						if x[index].isdigit() and proPredictor[index].isdigit():
							cnt = cnt + 1
					w.writerow([proPredictor[0], proPredictor[1], x[0], x[1], cnt])

	def pairsHist(self, interval):
		if not os.path.exists(self.pairsHistDir):
			os.makedirs(self.pairsHistDir)
		
		reader = csv.reader(open(self.pairsFrequency), delimiter = ',')
		reader.next()
		x = []
		for row in reader:
			x.append(int(row[4]))

		fig = plt.figure()
		bins = np.arange(0, 50, interval)
		plt.axis([0, 45, 0, 750])
		plt.title('Histogram of score pairs with Bin = ' + str(interval), fontsize='large')
		plt.xlabel('Number of Pairs')
		plt.ylabel('Frequency')
		plt.grid(True)
		
		n, bins, patches = plt.hist(x, bins, normed=0, histtype='bar')

		figName = self.pairsHistDir + 'pairs_hist_' + 'interval_' + str(interval) + '.png'
		fig.savefig(figName)
		# plt.show()
		plt.close(fig)		

	def validation(self, corr, flag, cutoff):
		r = csv.reader(open(self.CRS_STU_GRADE), delimiter=',')
		r.next()
		crsDict = {}
		for crs in r:
			key = crs[0].replace(' ','') + crs[1].replace(' ','')
			if not key in crsDict:
				crsDict[key] = crs[2:]

		# wfile = self.dataDir + str(self.threshold) + '_corr_' + flag + '_val' + str(cutoff) + '.csv'
		# w1file = self.dataDir + str(self.threshold) + '_corr_' + flag + '_val' + str(cutoff) + str(cutoff) + '.csv'
		wfile = self.dataDir + 'corr_' + flag + '_val' + str(cutoff) + '.csv'
		w1file = self.dataDir + 'corr_' + flag + '_val' + str(cutoff) + str(cutoff) + '.csv'
		w, w1 = csv.writer(open(wfile, 'w')), csv.writer(open(w1file, 'w'))

		r1 = csv.reader(open(corr), delimiter=',')
		r1.next()
		coeLst = []
		for pair in r1:
			if cutoff > 0:
				if float(format(float(pair[4]), '.2f')) >= cutoff:
					coeLst.append(pair)
			else:
				if float(format(float(pair[4]), '.2f')) <= cutoff:
					coeLst.append(pair)
		# sort coeLst according to the frequency of xcourse and the coefficient descending
		# group records according to the xcourse and the coefficient descending
		coeLst.sort(key=itemgetter(0,1,4), reverse=True)
		# compute the frequency for each xcourse
		freq = Counter(item[0]+item[1] for item in coeLst)
		# sort the records according to xcourse frequency descending
		coeLst = sorted(coeLst, key=lambda i: freq[i[0]+i[1]], reverse=True)

		gradeLevelFreLst = []
		for pair in coeLst:
			xkey, ykey = pair[0].replace(' ','') + pair[1].replace(' ',''), pair[2].replace(' ','') + pair[3].replace(' ','')
			xgrades, ygrades = crsDict[xkey], crsDict[ykey]
			total = 0
			for x in xrange(0,len(xgrades)):
				if (xgrades[x] != '' and ygrades[x] != ''):
					total = total + 1

			# [course_1, course_y, #_of_student, coefficient, #_of_courses]
			gradeLevelFreLst.append([xkey, ykey, total, pair[4], freq[xkey]])

		# sort gradeLevelFreLst by #_of_student and coefficient descendingly
		gradeLevelFreLst.sort(key=itemgetter(0,2,3), reverse=True)
		# freq = Counter(item[0] for item in gradeLevelFreLst)
		gradeLevelFreLst = sorted(gradeLevelFreLst, key=lambda i: freq[i[0]], reverse=True)
		header = ['Course_1', 'Course_2', '#students', 'Coefficient', '#Courses']
		w1.writerow(header)
		for index in xrange(0, len(gradeLevelFreLst)):
			w1.writerow(gradeLevelFreLst[index])
			if index < (len(gradeLevelFreLst)-1):
				if gradeLevelFreLst[index][0] != gradeLevelFreLst[index+1][0]:
					w1.writerow([])
					w1.writerow(header)

		w1.writerow([])
		w1.writerow(['Course', '#Course'])
		sorted_freq = sorted(freq.items(), key=itemgetter(1), reverse=True)
		for tps in sorted_freq:
			w1.writerow([tps[0], tps[1]])

		for pair in gradeLevelFreLst:
			xkey, ykey, total = pair[0], pair[1], 0
			xgrades, ygrades = crsDict[xkey], crsDict[ykey]
			levelA, levelB, levelC, levelD, levelF = [], [], [], [], []

			for x in xrange(0,len(xgrades)):
				if (xgrades[x] != '' and ygrades[x] != ''):
					total = total + 1
					if xgrades[x] in ['A', 'A-', 'A+']:
						levelA.append(ygrades[x])
					elif xgrades[x] in ['B', 'B-', 'B+']:
						levelB.append(ygrades[x])
					elif xgrades[x] in ['C', 'C+']:
						levelC.append(ygrades[x])
					elif xgrades[x] in ['D', 'SB', 'SB-', 'SD']:
						levelD.append(ygrades[x])
					elif xgrades[x] in ['E', 'F', 'N', 'SF']:
						levelF.append(ygrades[x])

			w.writerow(['Course_1', 'Course_2', '', '', '', '', '', '', '', '', '', '', '#Student', 'Coefficient', '#Courses'])
			w.writerow([xkey, ykey, 'A', 'B', 'C', 'D', 'F', '%A', '%B', '%C', '%D', '%F', total, pair[3], freq[xkey]])

			lsta, lstb, lstc = self.gradeDistributionCell(self.levelFrequency(levelA), 'A'), self.gradeDistributionCell(self.levelFrequency(levelB), 'B'), self.gradeDistributionCell(self.levelFrequency(levelC), 'C')
			lstd, lstf = self.gradeDistributionCell(self.levelFrequency(levelD), 'D'), self.gradeDistributionCell(self.levelFrequency(levelF), 'F')

			w.writerows([lsta, lstb, lstc, lstd, lstf])
			w.writerow([])
			# print [xkey, ykey, 'A', 'B', 'C', 'D', 'F', '%A', '%B', '%C', '%D', '%F', total, pair[2], pair[3], freq[xkey]], '\n', lsta, '\n', lstb, '\n', lstc, '\n', lstd, '\n', lstf

	def gradeDistributionCell(self, lst, gradeLevel):
		if sum(lst) != 0 and len(lst) == 5:
			return [gradeLevel, sum(lst), lst[0], lst[1], lst[2], lst[3], lst[4], format(lst[0]*1.0/sum(lst), '.2f'), format(lst[1]*1.0/sum(lst), '.2f'), format(lst[2]*1.0/sum(lst), '.2f'), format(lst[3]*1.0/sum(lst), '.2f'), format(lst[4]*1.0/sum(lst), '.2f')]
		else:
			return [gradeLevel, sum(lst), lst[0], lst[1], lst[2], lst[3], lst[4]]

	def levelFrequency(self, level):
		acnt = bcnt = ccnt = dcnt = fcnt = 0
		for x in level:
			if x in ['A', 'A-', 'A+']:
				acnt = acnt + 1
			elif x in ['B', 'B-', 'B+']:
				bcnt = bcnt + 1
			elif x in ['C', 'C+']:
				ccnt = ccnt + 1
			elif x in ['D', 'SB', 'SB-', 'SD']:
				dcnt = dcnt + 1
			elif x in ['E', 'F', 'N', 'SF']:
				fcnt = fcnt + 1

		return [acnt, bcnt, ccnt, dcnt, fcnt]

	def gradesGroup(self):
		return {'A':['A+','A','A-'], 'B':['B+','B','B-'], 'C':['C+','C'], 'D':['D','SB','SB-','SD'], 'Fail':['E','F','N','SF']}

	def gradePointMap(self):
		return {'A':8, 'A-':7, 'A+':9, 'B':5, 'B-':4, 'B+':6, 'C':2, 'C+':3, 'D':1, 'E':0, 'F':0, 'N':0, 'SB':1, 'SB-':1, 'SD':1, 'SF':0}

	def formulaV1(self, w1, w2):
		# build top1/top3 predictors using Pxy
		reader = csv.reader(open(self.pearsoncorr), delimiter=',')
		header = reader.next()
		rows = []
		for row in reader:
			# convert r str to r float
			row[4] = float(row[4])
			rows.append(row)

		rows.sort(key=itemgetter(2,3,4,5), reverse=True)

		fV1Reulsts = self.dataDir + 'fv1_' + str(w1) + '_' + str(w2) +'.csv'
		writer = csv.writer(open(fV1Reulsts, 'w'))
		# build the self.predictorFile
		self.top1FactorsFile = self.dataDir + 'T1F_' + str(w1) + '_' + str(w2) + '_' + self.trainYrsText +'.csv'
		factorWriter = csv.writer(open(self.top1FactorsFile, 'w'))
		self.top3FactorsFile = self.dataDir + 'T3F_' + str(w1) + '_' + str(w2) + '_' + self.trainYrsText +'.csv'
		factorTop3Writer = csv.writer(open(self.top3FactorsFile, 'w'))

		header.insert(6, str(w1) + '_' + str(w2))
		factorWriter.writerow(header)
		factorTop3Writer.writerow(header)

		ylist, rlist, plist = [], [], []
		for x in xrange(0,len(rows)):
			ylist.append(rows[x])
			rlist.append(abs(float(rows[x][4])))
			plist.append(float(rows[x][5]))

			if x < (len(rows)-1):
				if (rows[x][2]+rows[x][3]) != (rows[x+1][2]+rows[x+1][3]):
					writer.writerow(header)
					ylist, top1List, top3List = self.PxyPredictors(ylist, rlist, plist, w1, w2)
					writer.writerows(ylist)
					writer.writerow([])
					factorWriter.writerows(top1List)
					factorTop3Writer.writerows(top3List)

					ylist, rlist, plist = [], [], []

		if (len(ylist) == len(rlist)) and (len(ylist) == len(plist)) and (len(ylist) > 0):
			writer.writerow(header)
			ylist, top1List, top3List = self.PxyPredictors(ylist, rlist, plist, w1, w2)
			writer.writerows(ylist)
			factorWriter.writerows(top1List)
			factorTop3Writer.writerows(top3List)

			ylist, rlist, plist = [], [], []

	def PxyPredictors(self, ylist, rlist, plist, w1, w2):
		pxyArr, top1List, top3List = [], [], []
		for sublist in ylist:
			norm_r = abs(float(sublist[4]))/float(max(rlist))
			norm_p = float(sublist[5])/float(max(plist))
			pxy = w1*norm_r + w2*norm_p

			pxy = float(format(pxy, '.6f'))
			pxyArr.append(pxy)
			sublist.insert(6, pxy)

		top1List = self.top1Predictor(ylist, pxyArr)
		top3List = self.top3Predictors(ylist, pxyArr)

		return [ylist, top1List, top3List]

	def top3Predictors(self, ylist, pxyArr):
		# the return list
		top3List = []
		# locate and get the top 3 Pxy
		pxyIndexList = sorted(range(len(pxyArr)), key=lambda i: pxyArr[i])
		# top3Index = pxyIndexList[-3:]
		# top3Pxy = [ylist[top3Index[0]][6], ylist[top3Index[1]][6], ylist[top3Index[2]][6]]
		top3Pxy = []
		for index in pxyIndexList[-3:]:
			top3Pxy.append(ylist[index][6])

		# build the top3Ylist which have the top3 pxy, from ylist
		top3Ylist = []
		for sublist in ylist:
			for pxy in top3Pxy:
				if float(sublist[6]) == pxy:
					top3Ylist.append(sublist)
					break

		# there are just 3 or less items in the top3Ylist, so the answer found & just return it to callback; actually the less than condition does not exist
		if len(top3Ylist) <= 3:
			top3List = top3Ylist
		else:
			# there are more than 3 items which have the top 3 pxy values
			freq = Counter(item for item in top3Pxy)
			if len(freq) == 3:
				# the top 3 pxy are different, then for each of the top 3 pxy values, locate the bottom course number and the corresponding predictor and predicting course record; and then append them to the return list
				for pxy in top3Pxy:
					bottomNumRecList = self.bottomNumBuilder(top3Ylist, pxy, 1)
					for rec in bottomNumRecList:
						top3List.append(rec)
			elif len(freq) == 2:
				# there are two pxy values of the top 3 pxy values which have the same pxy value; then in this case, for the two pxy, find the bottom two couse numbers and the corresponding predictor and predicting records
				# for the other one pxy, find the bottom course number and the corresponding predictor and predicting record
				# after finishing the above two steps, add the the three records to the return list
				for key in freq.keys():
					# key: it is the pxy value here
					bottomNumRecList = self.bottomNumBuilder(top3Ylist, key, freq[key])
					for rec in bottomNumRecList:
						top3List.append(rec)
			elif len(freq) == 1:
				# the top 3 have the same value, then find the bottom 3 course number and the corresponding records, and add them to the return list
				# build course number list
				bottomNumRecList = self.bottomNumBuilder(top3Ylist, top3Pxy[0], 3)
				for rec in bottomNumRecList:
					top3List.append(rec)

		return top3List

	def bottomNumBuilder(self, ylist, pxy, bottomN):
		# bottomN: = 1,2,3
		xCrsNums, bottomNumRecList, dupPxyRecList = [], [], []
		for sublist in ylist:
			if pxy == float(sublist[6]):
				xCrsNums.append(int(sublist[1][:3]))
				dupPxyRecList.append(sublist)

		numIndexList = sorted(range(len(xCrsNums)), key=lambda i: xCrsNums[i])
		bottomNNumsList = []
		for index in numIndexList[:bottomN]:
			bottomNNumsList.append(xCrsNums[index])

		for sublist in dupPxyRecList:
			for bottomNNum in bottomNNumsList:
				if bottomNNum == int(sublist[1][:3]):
					bottomNumRecList.append(sublist)
					# break the inner for loop
					break

		return bottomNumRecList

	def top1Predictor(self, ylist, pxyArr):
		top1List = []
		# search the top one predictor course
		maxPxy = max(pxyArr)
		freq = Counter(item for item in pxyArr)
		# there is only one maximun pxy
		if freq[maxPxy] == 1:
			index = pxyArr.index(maxPxy)			
			top1List.append(ylist[index])
		else:
			# several maximum Pxy exist simultaneously
			bottomNumRecList = self.bottomNumBuilder(ylist, maxPxy, 1)
			for rec in bottomNumRecList:
				top1List.append(rec)

		return top1List

	def formulaV1Integrate(self, w1list, w2list):
		reader = csv.reader(open(self.pearsoncorr), delimiter=',')
		header = reader.next()
		rows = []
		for row in reader:
			row[4] = float(row[4])
			rows.append(row[0:6])

		rows.sort(key=itemgetter(2,3,4,5), reverse=True)

		fV1Reulsts = self.dataDir + 'fv1_w1_w2_'+self.trainYrsText+'_'+str(self.threshold)+'.csv'
		writer = csv.writer(open(fV1Reulsts, 'w'))

		header = header[0:6]
		for x in xrange(0, len(w1list)):
			header.append(str(w1list[x])+'_'+str(w2list[x]))

		cnt = 0
		ylist, rlist, plist = [], [], []
		for x in xrange(0,len(rows)):
			cnt += 1
			ylist.append(rows[x])

			r = float(rows[x][4])
			if r < 0:
				rlist.append(r*(-1.0))
			else:
				rlist.append(r)

			plist.append(float(rows[x][5]))
			# print 'cnt: ', cnt, '\t', rows[x]
			if x < (len(rows)-1):
				if (rows[x][2]+rows[x][3]) != (rows[x+1][2]+rows[x+1][3]):
					writer.writerow(header)
					writer.writerows(self.computePxyIntegrade(ylist, rlist, plist, w1list, w2list))
					writer.writerow([])
					ylist, rlist, plist = [], [], []
					# print '\n'

		if (len(ylist) == len(rlist)) and (len(ylist) == len(plist)) and (len(ylist) > 0):
			writer.writerow(header)
			writer.writerows(self.computePxyIntegrade(ylist, rlist, plist, w1list, w2list))
			ylist, rlist, plist = [], [], []
			# print '\n'

	def computePxyIntegrade(self, ylist, rlist, plist, w1list, w2list):
		for sublist in ylist:
			r, p, maxr, maxp = float(sublist[4]), float(sublist[5]), float(max(rlist)), float(max(plist))
			for x in xrange(0,len(w1list)):
				if r < 0:
					pxy = w1list[x]*r*(-1.0)/maxr + w2list[x]*p/maxp
				else:
					pxy = w1list[x]*r/maxr + w2list[x]*p/maxp

				sublist.append(format(pxy, '.4f'))

		return ylist

	def predictProcessTop3Factors(self, testReg, predictResults, aveErrResults, power, predictorsFile):
		# build equation/predictor dict; predictorDict = [key1:[rRec1, rRec2, rRec3, ...], key2:[], key3:[],...]
		r1 = csv.reader(open(predictorsFile), delimiter=',')
		header1, predictorDict, predictingList = r1.next(), {}, []
		rows = []
		for row in r1:
			rows.append(row)

		for x in xrange(0,len(rows)):
			predictingList.append(rows[x])
			if x < (len(rows)-1):
				if (rows[x][2]+rows[x][3]) != (rows[x+1][2]+rows[x+1][3]):
					# find one preciting course with its top3 predictor courses in the predictor csv file; then, save it in the predictorDict for later predicting
					key = rows[x][2]+rows[x][3]
					if key not in predictorDict:
						predictorDict[key] = predictingList
					else:
						existList = predictorDict[key]
						for item in predictingList:
							existList.append(item)
						predictorDict[key] = existList

					predictingList = []

		if len(predictingList) > 0:
			key = rows[-1][2]+rows[-1][3]
			if key not in predictorDict:
				predictorDict[key] = predictingList
			else:
				existList = predictorDict[key]
				for item in predictingList:
					existList.append(item)
				predictorDict[key] = existList

			predictingList = []

		# test data reg file: build test reg dict
		r2 = csv.reader(open(testReg), delimiter=',')
		header2, testRegDict = r2.next(), {}
		for row in r2:
			# key: course code(subject code and course number); value of key: course record
			key = row[0]+row[1]
			if key not in testRegDict:
				testRegDict[key] = row

		# build the prediction list for all possible predicting courses
		# keys: predicting course numbers; key: predicting course number
		keys, predictionList = predictorDict.keys(), []
		for key in keys:
			# the predictong course exist in the testRegDict
			if key in testRegDict:
				predictors, predicting, testPretors = predictorDict[key], testRegDict[key], []
				for predictor in predictors:
					crsNum = predictor[0]+predictor[1]
					# the predictor course also exists
					if crsNum in testRegDict:
						predictorCrs = testRegDict[crsNum]
						testPretors.append(predictorCrs)

				if len(testPretors) > 0:
					predictionList.append({'predicting': predicting, 'predictors': testPretors})

		# build the testing
		resultW = csv.writer(open(predictResults, 'w'))
		meanLists, cleanPredictingList = [], []
		for pdict in predictionList:
			predicting, predictors = pdict['predicting'], pdict['predictors']
			cleanPair = self.samplePointsFilter(predicting, predictors)

			if len(cleanPair) == 0:
				continue

			cleanPredicting, cleanPredictors = cleanPair[0], cleanPair[1]
			cleanPredictingList.append(cleanPredicting)
			# write predictor course records and the predicting record
			if not self.errMerge:
				resultW.writerows(cleanPredictors)
				resultW.writerow(cleanPredicting)

			[predictingGradesList, predictingErrList, predictingErrPerList, meanList, meanErrList, MeanErrPerList] = self.prediction(predictorDict, cleanPredicting, cleanPredictors, power)

			if not self.errMerge:
				resultW.writerows(predictingGradesList)
				resultW.writerows(predictingErrList)
				resultW.writerows(predictingErrPerList)
				resultW.writerows([meanList, meanErrList, MeanErrPerList])

				# add r, p, pxy
				rppxyList = [['xsub', 'xnum', 'ysub', 'ynum', 'r', 'point#', 'pxy']]
				for cleanPredictor in cleanPredictors:
					predictingKey = cleanPredicting[0]+cleanPredicting[1]
					for x in predictorDict[predictingKey]:
						if (x[0]+x[1])==(cleanPredictor[0]+cleanPredictor[1]):
							rppxyList.append([x[0], x[1], x[2], x[3], x[4], x[5], x[6]])
							break
				if len(rppxyList) > 0:
					resultW.writerows(rppxyList)
				resultW.writerow([])

			meanLists.append(meanList)

		[gradesList, statsList] = self.errStatsTop3(cleanPredictingList, meanLists)
		if not self.errMerge:
			resultW.writerows(gradesList)
		resultW.writerows(statsList)

	def prediction(self, predictorDict, cleanPredicting, cleanPredictors, power):
		# get the predicting equation according to the power
		key = cleanPredicting[0]+cleanPredicting[1]
		predictors = predictorDict[key]

		predictingGradesList, predictingErrList, predictingErrPerList = [], [], []		
		for cleanPredictor in cleanPredictors:
			currentPredictor = ''
			# find the coefficients of the predictor for prediction
			for predictor in predictors:
				if (predictor[0]+predictor[1]) == (cleanPredictor[0]+cleanPredictor[1]):
					currentPredictor = predictor
					break

			# calculate the predicting grades
			predictingGrades, predictingErrs, predictingErrPers = [cleanPredictor[0], cleanPredictor[1]], [cleanPredictor[0], cleanPredictor[1]], [cleanPredictor[0], cleanPredictor[1]]
			predictingGradesSum = predictingErrsSum = predictingErrPersSum = cnt = 0
			# for x in cleanPredictor[2:]:
			for index in xrange(2, len(cleanPredictor)):
				x = cleanPredictor[index]
				if x.isdigit():
					grade = ''
					# linear prediction
					if power == 1:
						slope, intercept = currentPredictor[9], currentPredictor[10]
						grade = float(slope)*float(x)+float(intercept)
					# quadratic prediction
					elif power == 2:
						a, b, c = currentPredictor[11], currentPredictor[12], currentPredictor[13]
						grade = float(a)*pow(float(x), 2)+float(b)*float(x)+float(c)

					grade = float(format(grade, '.1f'))
					predictingGrades.append(grade)
					err = float(cleanPredicting[index]) - grade
					predictingErrs.append(err)
					per = 0
					if float(cleanPredicting[index]) == 0:
						per = abs(err)/1.0*100
					else:
						per = abs(err)/float(cleanPredicting[index])*100
					predictingErrPers.append(str(per)+'%')

					cnt += 1
					predictingGradesSum += grade
					predictingErrsSum += abs(err)
					predictingErrPersSum += per
				else:
					predictingGrades.append('')
					predictingErrs.append('')
					predictingErrPers.append('')

			if len(predictingGrades) > 2:
				if cnt != 0:
					predictingGrades.append(format(predictingGradesSum/cnt, '.1f'))
					predictingErrs.append(format(predictingErrsSum/cnt, '.2f'))
					predictingErrPers.append(str(format(predictingErrPersSum/cnt, '.2f'))+'%')

				predictingGradesList.append(predictingGrades)
				predictingErrList.append(predictingErrs)
				predictingErrPerList.append(predictingErrPers)

		meanList, meanErrList, MeanErrPerList = [cleanPredicting[0], cleanPredicting[1]], [cleanPredicting[0], cleanPredicting[1]], [cleanPredicting[0], cleanPredicting[1]]
		meanSum = errSum = errPerSum = count = 0
		for index in xrange(2,len(cleanPredicting)):
			predictingGradeSum, cnt = 0, 0
			for predictingGrades in predictingGradesList:
				if predictingGrades[index] != '':
					predictingGradeSum += predictingGrades[index]
					cnt += 1

			mean = float(format(predictingGradeSum/cnt, '.2f'))
			meanList.append(mean)
			meanErr = float(cleanPredicting[index]) - mean
			meanErrList.append(meanErr)
			per = 0
			if float(cleanPredicting[index]) == 0:
				per = abs(meanErr)/1.0*100
			else:
				per = abs(meanErr)/float(cleanPredicting[index])*100
			MeanErrPerList.append(str(format(per, '.2f'))+'%')
			meanSum += mean
			errSum += abs(meanErr)
			errPerSum += per
			count += 1

		errArr = np.array(meanList[2:])
		std = format(np.std(errArr), '.2f')
		meanList.append(format(meanSum/count, '.2f'))
		meanList.append(std)
		meanErrList.append(format(errSum/count, '.2f'))
		MeanErrPerList.append(str(format(errPerSum/count, '.2f')+'%'))

		return [predictingGradesList, predictingErrList, predictingErrPerList, meanList, meanErrList, MeanErrPerList]

	def errStatsTop3(self, cleanPredictingList, meanLists):
		# mean, me, mae, mape
		statsList, gradesList = [['subj', 'num', 'mean', 'std', 'me', 'mae', 'mape', 'insOneCrs', 'minErr', 'maxErr', 'interval']], []
		for index in xrange(0,len(cleanPredictingList)):
			cleanPredicting, meanList = cleanPredictingList[index], meanLists[index]
			grades, means = cleanPredicting[2:], meanList[2:len(cleanPredicting)]
			grades = [float(i) for i in grades]
			# print 'grades:', grades, '\nmeans:', means

			gradesList.append(cleanPredicting)
			gradesList.append(meanList[:len(cleanPredicting)])
			gradesList.append([])

			gradesArr = np.array(grades)
			mean, std = np.average(gradesArr), np.std(gradesArr)
			errList, errAList, perList = [], [], []
			for x in xrange(0,len(grades)):
				err = grades[x] - means[x]
				errList.append(err)
				errAList.append(abs(err))

				per = 0
				if grades[x] == 0:
					per = abs(err)/1.0
				else:
					per = abs(err)/grades[x]
				perList.append(per)

			errArr, errAArr, perListArr = np.array(errList), np.array(errAList), np.array(perList)
			me, mae, mape, minerr, maxerr = np.average(errArr), np.average(errAList), np.average(perList), min(errList), max(errList), 
			interval, insOneCrs = maxerr-minerr, len(errList)

			stat = [cleanPredicting[0], cleanPredicting[1], format(mean, '.2f'), format(std, '.2f'), format(me, '.2f'), format(mae, '.2f'), format(mape, '.2f'), insOneCrs, minerr, maxerr, interval]
			statsList.append(stat)

		return [gradesList, statsList]

	def samplePointsFilter(self, predicting, predictors):
		if len(predicting) <= 2:
			return []

		gradeIndexList = []
		# reformed predicting course record, removing the cells in the record whose cooresponding cell in the predictor records do not have grades
		cleanPredicting = [predicting[0], predicting[1]]
		for index in xrange(2,len(predicting)):
			for x in xrange(0,len(predictors)):
				if (predictors[x][index].isdigit()) and (predicting[index].isdigit()):
					gradeIndexList.append(index)
					cleanPredicting.append(predicting[index])
					break

		cleanPredictors = []		
		for predictor in predictors:
			cleanPredictor = [predictor[0], predictor[1]]
			for index in gradeIndexList:
				cleanPredictor.append(predictor[index])
			if len(cleanPredictor) > 2:
				cleanPredictors.append(cleanPredictor)

		if len(cleanPredictors) > 0:
			return [cleanPredicting, cleanPredictors]
		else:
			return []

	def predictProcessTop1Factors(self, testReg, predictResults, aveErrResults, power, predictorsFile):
		# build equation/predictor dict
		r1 = csv.reader(open(predictorsFile), delimiter=',')
		header1, predictorDict = r1.next(), {}
		for row in r1:
			# key: the predicting course, value of key: row of predictor & predicting course
			key = row[2]+row[3]
			if key not in predictorDict:
				predictorDict[key] = [row]
			else:
				predictorDict[key].append(row)

		# test data reg file: build test reg dict
		r2 = csv.reader(open(testReg), delimiter=',')
		header2, testRegDict = r2.next(), {}
		for row in r2:
			# key: course code(subject code and course number); value of key: course record
			key = row[0]+row[1]
			if key not in testRegDict:
				testRegDict[key] = row

		# search predictable courses; keys: the predicting courses
		predictingList, keys = [],predictorDict.keys()
		for key in keys:
			if key in testRegDict:
				testY, testXs, predictors, minList, maxList = testRegDict[key],[],predictorDict[key],[],[]
				for x in predictors:
					testXKey = x[0]+x[1]
					if testXKey in testRegDict:
						minList.append(x[15])
						maxList.append(x[16])
						testXs.append(testRegDict[testXKey])

				# have located the predictable course pairs stored in pairsList
				pairsList = self.gradePairs(testY, testXs, minList, maxList)
				if len(pairsList) > 0:
					predictingList.append(pairsList)

		# predict
		writer = csv.writer(open(predictResults, 'w'))
		# errw = csv.writer(open(aveErrResults, 'w'))
		# errw.writerow(['aveErr', 'r', '#point'])
		# [errorave, coefficient, pointFreq]
		AERPList, errRangeStdErrList, pointsList, rList, aveAbsErrList, mapeList, realEstPairList, pairRangeList = [], [], [], [], [], [], [], []
		# [xsubj, xNum, ySubj, yNum, sample Point#, r, std, mean of err, mean absolute err, test instance#, minErr, maxErr, internal]
		header = ['xSubj', 'xNum', 'ySubj', 'yNum', 'point#', 'r', 'mean', 'std', 'errStd', 'rMean', 'rStd','ME', 'MAE', 'MAPE', 'insOneCrs', 'minErr', 'maxErr', 'interval']
		errRangeStdErrList.append(header)

		for pairsList in predictingList:
			for pairs in pairsList:
				[xgrades, ygrades] = pairs
				# locate predicting equation; key: predicting course
				key = ygrades[0] + ygrades[1]
				predictors = predictorDict[key]
				# linear: y = slope * x + intercept;	quadratic: y = ax^2+bx+c
				slope = intercept = coefficient = pointFreq = xSubj = xNum = ySubj = yNum = 0
				for predictor in predictors:
					xcourse, predictorCourse = xgrades[0] + xgrades[1], predictor[0] + predictor[1]
					if xcourse == predictorCourse:
						# !!!caution: for the index
						# xSubj,xNum,ySubj,yNum, coefficient,pointFreq = predictor[0], predictor[1], predictor[2], predictor[3], predictor[4], predictor[5]
						# slope,intercept,a,b,c = predictor[9], predictor[10], predictor[11], predictor[12], predictor[13]
						xSubj,xNum,ySubj,yNum, coefficient,pointFreq, slope,intercept,a,b,c = predictor[:6]+predictor[9:14]
						# slope,intercept,a,b,c = predictor[9:14]
						pointsList.append(float(pointFreq))
						rList.append(float(coefficient))
						# compute errors: aesum: absolute err sum; aepsum: absolute err percent sum
						errorList, absErrPerList, aesum, aepsum = [], [], 0, 0
						# compute predicting grade of testY using the equation located above
						predictGrades = [ygrades[0], ygrades[1]]
						for index in xrange(2, len(xgrades)):
							x, grade = xgrades[index], 0
							if power == 1:
								grade = float(slope)*float(x)+float(intercept)
							if power == 2:
								grade = float(a)*pow(float(x), 2)+float(b)*float(x)+float(c)

							grade = float(format(grade, '.1f'))
							predictGrades.append(grade)
							# fetch the actual grade from ygrades list
							actualGrade = float(ygrades[index])
							# calculate predicting err
							error = actualGrade-grade

							errorList.append(error)
							aesum += abs(error)

							absErrPer = 0 
							if actualGrade == 0:
								absErrPer = abs(error)/1.0
							else:
								absErrPer = abs(error)/actualGrade

							aepsum += absErrPer
							absErrPerList.append(str(format(absErrPer*100, '.2f'))+'%')

						mae = format(aesum/len(errorList), '.2f')
						aveAbsErrList.append(float(mae))

						mape = format(aepsum/len(errorList), '.2f')
						mapeList.append(float(mape))

						errArr = np.array(errorList)
						errorave = format(np.average(errArr), '.2f')
						errStd = format(np.std(errArr), '.2f')

						gradesArr = np.array(predictGrades[2:])
						mean = format(np.average(gradesArr), '.2f')
						std = format(np.std(gradesArr), '.2f')

						# compute the real grades' mean and std
						# print 'ygrades[2:]: ', ygrades[2:]
						realGrades = np.array([float(grade) for grade in ygrades[2:]])
						rMean = format(np.average(realGrades), '.2f')
						rStd = format(np.std(realGrades), '.2f')

						tempList = [xSubj,xNum,ySubj,yNum,pointFreq,coefficient,mean,std,errStd,rMean,rStd,errorave,mae,mape,len(errorList),min(errorList),max(errorList), max(errorList)-min(errorList)]
						errRangeStdErrList.append(tempList+errorList)

						realEstPairList.append(ygrades)
						realEstPairList.append(predictGrades)

						actualGradesSorted = np.sort(ygrades[2:])
						predictedGradesSorted = np.sort(predictGrades[2:])
						pairRangeList.append([xgrades[0], xgrades[1], ygrades[0], ygrades[1], actualGradesSorted[0], actualGradesSorted[-1], predictedGradesSorted[0], predictedGradesSorted[-1]])

						xgrades.insert(0, 'predictor')
						ygrades.insert(0, 'real')
						predictGrades.insert(0, 'predicting')				
						
						for x in xrange(0,2):
							errorList.insert(x, '')
							absErrPerList.insert(x, '')

						errorList.insert(2, 'Err:')
						absErrPerList.insert(2, 'AbsErrPer:%')

						# appendix = ['point#', pointFreq, 'Coefficient:', coefficient, 'average error:', errorave]
						appendix = [ 'mean Err:', errorave, 'mea:', mae, 'mape:', mape]

						if not self.errMerge:
							writer.writerows([xgrades, ygrades, predictGrades, errorList, absErrPerList, appendix, []])
						# errw.writerow([errorave, coefficient, pointFreq])
						AERPList.append([errorave, coefficient, pointFreq])

						# print xgrades, '\n', ygrades, '\n', predictGrades, '\n', errorList, '\n', absErrPerList, '\n'

		writer.writerows(errRangeStdErrList)
		writer.writerow([])
		# ['xSubj', 'xNum', 'ySubj', 'yNum', 'point#', 'r', 'mean', 'std', 'errStd', 'rMean', 'rStd','ME', 'MAE', 'MAPE', 'insOneCrs', 'minErr', 'maxErr', 'interval']
		# build the header-format table and sort by predictor, then predicted course
		header = ['xSubj', 'xNum', 'ySubj', 'yNum', 'point#', 'r', 'mean', 'rMean', 'std', 'rStd', 'mean diff', 'std diff', 'MAE']
		writer.writerow(header)
		tmp = [ item[:7]+[item[9], item[7], item[10], float(item[6])-float(item[9]), float(item[7])-float(item[10]), item[12]] for item in errRangeStdErrList[1:] ]

		# pick the 1st year predictors and 2nd year predictors
		flist = [x for x in tmp if x[1][0] == '1']
		slist = [x for x in tmp if x[1][0] == '2']
		flist.sort(key=itemgetter(3), reverse=False)
		slist.sort(key=itemgetter(3), reverse=False)
		writer.writerows(flist+[header]+slist)
		writer.writerow([])

		header = ['xSubj', 'xNum', 'ySubj', 'yNum', 'rMin', 'rMax', 'pMin', 'pMax', 'rInterval', 'pInterval', 'abs diff']
		writer.writerow(header)
		tmp = [pairRangeList[x]+[float(pairRangeList[x][5])-float(pairRangeList[x][4]), float(pairRangeList[x][7])-float(pairRangeList[x][6]), abs((float(pairRangeList[x][5])-float(pairRangeList[x][4]))-(float(pairRangeList[x][7])-float(pairRangeList[x][6])))] for x in xrange(0, len(pairRangeList))]
		# sort by predictor, then predicted course
		flist = [x for x in tmp if x[1][0] == '1']
		slist = [x for x in tmp if x[1][0] == '2']
		flist.sort(key=itemgetter(3), reverse=False)
		slist.sort(key=itemgetter(3), reverse=False)
		writer.writerows(flist+[header]+slist)

		writer.writerow([])
		writer.writerows(realEstPairList)

		prefix, suffix = testReg.split('/')[-1].split('_')[0], ''
		if power == 1:
			suffix, tSuffix = 'L', 'Linear'
		elif power == 2:
			suffix, tSuffix = 'Q', 'Quadratic'

		# 3D plots
		figName = self.maerp3DDir+suffix+'/'+prefix[3:]+'_rpMAE_'+suffix+'.png'
		title = ''
		if self.proPredictor == 'ALL':
			title = 'Sample points vs Pearson coefficient vs MAE \n'+tSuffix+':'+prefix[3:]+' vs '+self.trainYrsText+'; Threshold:'+str(self.threshold)+'; rw:'+str(self.rw)+', pw:'+str(self.pw)
		else:
			title = 'Sample points vs Pearson coefficient vs MAE \n'+tSuffix+': using predictor of '+self.proPredictor+'; Threshold:'+str(self.threshold)

		if self.proPredictor == 'ALL':
			if self.factor == 'PR':
				self.maerp3DPlots(pointsList, rList, aveAbsErrList, figName, title)
			elif self.factor == 'P':
				xtitle = 'coefficients from training set '+self.trainYrs[0]+'-'+self.trainYrs[-1]
				ytitle = 'mean absolute error from '+prefix[3:]
				title = 'coefficients vs mean absolute error (MAE) ('+suffix+')'
				figName = self.maerp3DDir+suffix+'/'+prefix[3:]+'_p_MAE_'+suffix+'.png'
				self.errScatter(xtitle, ytitle, title, pointsList, aveAbsErrList, figName, 'p', 'ma')
			elif self.factor == 'R':
				xtitle = 'coefficients from training set '+self.trainYrs[0]+'-'+self.trainYrs[-1]
				ytitle = 'mean of absolute error from '+prefix[3:]
				title = 'coefficients vs mean absolute error (MAE) ('+suffix+')'
				figName = self.maerp3DDir+suffix+'/'+prefix[3:]+'_r_MAE_'+suffix+'.png'
				self.errScatter(xtitle, ytitle, title, rList, aveAbsErrList, figName, 'r', 'ma')
		else:
			self.maerp3DPlots(pointsList, rList, aveAbsErrList, figName, title)

	def gradePairs(self, testY, testXs, minList, maxList):
		resultPairs, pairsList, xCrsNums = [], [], []
		for x in testXs:
			# build the xgrades, ygrades lists
			xgrades, ygrades = [x[0], x[1]],[testY[0], testY[1]]
			xindex = testXs.index(x)
			xmin, xmax = minList[xindex],maxList[xindex]
			for index in xrange(2,len(testY)):
				if (x[index].isdigit() and testY[index].isdigit()) and (float(x[index])>=float(xmin)) and (float(x[index])<=float(xmax)):
					xgrades.append(x[index])
					ygrades.append(testY[index])

			# to see if there are at least one pair between xgrades and ygrades
			if len(xgrades) > 2:
				pairsList.append([xgrades, ygrades])
				# save course number for later predictor pickup
				xCrsNums.append(int(x[1][0:3]))
				# print x[1][:3], 'gradePairs\t', 'trainYrsLen:', len(self.trainYrs)

		if len(pairsList) > 1:
			# randomIndex = randint(0,len(pairsList)-1)
			# return [pairsList[randomIndex]]
			# to pick up the course with min course number as the predictor
			mincrsnum = min(xCrsNums)
			freq = Counter(item for item in xCrsNums)
			# after testing, the below case does not exist
			# if freq[mincrsnum] > 1:
			# 	print '=========== ', mincrsnum, ' ===========\tgradePairs\t', 'trainYrsLen:', len(self.trainYrs)
			
			index = xCrsNums.index(mincrsnum)
			resultPairs.append(pairsList[index])
		else:
			resultPairs = pairsList

		return resultPairs

	def errScatter(self, xtitle, ytitle, title, xdata, ydata, figName, xflag, yflag):
		fig = plt.figure()
		x = np.array(xdata)
		y = np.array(ydata)

		z = np.polyfit(x, y, 1)
		p = np.poly1d(z)
		plt.plot(x, y, 'o', c='red')
		# xp = np.linspace(0, 9, 100)
		if not (xflag == 'r'):
			plt.plot(x, p(x), 'b--')

		plt.xlabel(xtitle)
		plt.ylabel(ytitle)
		plt.title(title)

		plt.ylim(0.0, max(ydata)+0.5)

		ax = plt.axes()
		minorLocator = MultipleLocator(0.1)
		majorLocator = MultipleLocator(0.5)
		ax.yaxis.set_minor_locator(minorLocator)
		ax.yaxis.set_major_locator(majorLocator)

		# if yflag == 'mae':
		# 	plt.ylim(0, 16)
		# 	ticks = xrange(0, 16, 2)
		# 	ticks = np.linspace(0.0, 16.0, 8, endpoint=False).tolist()
		# 	ticks.append(16)
		# 	plt.yticks(ticks)			
		# if yflag == 'mape':
		# 	plt.ylim(0, 5)
		# 	ticks = np.linspace(0.0, 5.0, 10, endpoint=False).tolist()
		# 	ticks.append(5.0)
		# 	plt.yticks(ticks)

		if xflag == 'r':
			plt.xlim(-1.0, 1.0)
			# ticks = np.linspace(-1.0, 1.0, 20, endpoint=False).tolist()
			# ticks.append(1.0)
			# plt.xticks(ticks, rotation=20, fontsize='medium')

			minorLocator = MultipleLocator(0.1)
			majorLocator = MultipleLocator(0.1)
			plt.xticks(rotation=20, fontsize='medium')
		if xflag == 'p':
			plt.xlim(0, 120)
			# ticks = xrange(0, max(xdata)+5, 5)
			# ticks = xrange(0, 120, 10)
			# plt.xticks(ticks)

			minorLocator = MultipleLocator(2)
			majorLocator = MultipleLocator(10)
			# ax.grid(which = 'minor')
			plt.xticks(rotation=90, fontsize='small')

		ax.xaxis.set_minor_locator(minorLocator)
		ax.xaxis.set_major_locator(majorLocator)
		# ax.grid(which = 'minor')

		plt.grid(True)
		# plt.show()
		fig.savefig(figName)
		plt.close(fig)

	def maerp3DPlots(self, point, r, MAE, figName, title):
		# plot 3D graph
		fig = plt.figure()
		ax = Axes3D(fig)

		ax.scatter(point, r, MAE, c='r', marker='o')
		ax.set_xlabel('Sample Points', fontsize='medium')
		ax.set_ylabel('Pearson r', fontsize='medium')
		ax.set_zlabel('MAE', fontsize='medium', rotation=90)
		plt.title(title)

		ax.set_xlim3d(0, 120)
		ax.set_ylim3d(-1.0, 1.0)
		# ax.set_zlim3d(0.0, max(MAE)+0.5)
		ax.set_zlim3d(0.0, 8.0)

		ax.xaxis.set_minor_locator(MultipleLocator(2))
		ax.xaxis.set_major_locator(MultipleLocator(10))
		plt.xticks(rotation=90, fontsize='small')

		ax.yaxis.set_minor_locator(MultipleLocator(0.1))
		ax.yaxis.set_major_locator(MultipleLocator(0.1))
		plt.yticks(rotation=90, fontsize='small')

		ax.zaxis.set_minor_locator(MultipleLocator(0.1))
		ax.zaxis.set_major_locator(MultipleLocator(0.5))

		ax.view_init(elev=27, azim=27)
		fig.savefig(figName)
		plt.close(fig)

	def errTop1Top3StatsMerger(self, dest, resultTop1, resultTop3):
		w = csv.writer(open(dest, 'w'))
		for x in xrange(0,len(resultTop3)):
			top1, top3 = resultTop1[x], resultTop3[x]
			yr = top1.split('/')[-1].split('.')[0].split('_')[2][3:]

			w.writerow([yr])

			r1, r2 = csv.reader(open(top1), delimiter=','), csv.reader(open(top3), delimiter=',')
			h1, h2 = r1.next(), r2.next()

			w.writerow(h2[:8]+['']+h1[2:4]+h1[6:12])

			row1List, row2List = [], []
			for row in r1:
				row1List.append(row)
			for row in r2:
				row2List.append(row)

			maxLen = 0
			if len(row1List) > len(row2List):
				maxLen = len(row1List)
			else:
				maxLen = len(row2List)

			for x in xrange(0,maxLen):
				row1, row2 = row1List[x], row2List[x]
				if (row1[2]+row1[3]) != (row2[0]+row2[1]):
					row = ''
					if len(row1List) > len(row2List):
						row2List.insert(x, ['' for i in xrange(0, 8)])
						row = ['' for i in xrange(0, 8)]+['']+row1[2:4]+row1[6:12]
					else:
						row1List.insert(x, ['' for i in xrange(0, 8)])
						row = row2[:8]+['']+['' for i in xrange(0, 8)]
					w.writerow(row)
				else:
					w.writerow(row2[:8]+['']+row1[2:4]+row1[6:12])

	def errLinearQuadraticStatsMerger(self, dest, linearResult, quadraticResult):
		w = csv.writer(open(dest, 'w'))
		for x in xrange(0,len(linearResult)):
			linear, quadratic = linearResult[x], quadraticResult[x]
			yr = linear.split('/')[-1].split('.')[0].split('_')[1][3:]
			w.writerow([yr, 'quadratic', 'linear'])
			r1, r2 = csv.reader(open(linear), delimiter=','), csv.reader(open(quadratic), delimiter=',')
			h1, h2 = r1.next(), r2.next()
			w.writerow(h2[:12]+['']+h1[:12])

			row1List, row2List = [], []
			for row in r1:
				row1List.append(row)
			for row in r2:
				row2List.append(row)

			for index in xrange(0,len(row1List)):
				row = row2List[index][:12]+['']+row1List[index][:12]
				w.writerow(row)
			w.writerow([])

	# FOR MTIS ASSIGNMENTS ONLY
	def matrixBuilder(self):
		self.threshold, randomOrderRegList = 1, []
		self.statsPath()		
		
		reader = csv.reader(open(self.allTechCrs), delimiter=',')
		crsDict = {}
		for row in reader:
			key, value = row[0]+row[1], row[2]
			crsDict[key] = value

		for regFile in self.regFileList:
			yr = regFile.split('/')[-1].split('.')[0][3:]
			path = self.matrixDir+yr+'/'
			if not os.path.exists(path):
				os.makedirs(path)

			fileNameList = []
			fileNameSuffix = ['REPL_SAS.csv', 'NODUP_SAS.csv', 'TECH_NODUP_SAS.csv', 'CRSPERSTU_SAS.csv', 'STUREGISTERED_SAS.csv', 'EMPTY_SAS.csv', 'EMPTY_STU_SAS.csv', 'EMPTY_CRS_SAS.csv', 'CRS_STU_SAS.csv', 'CRS_STU_GRADE_SAS.csv', 'NODUP_REPL_SAS.csv', 'STU_CRS_SAS.csv', 'STU_CRS_GRADE_SAS.csv', 'CRS_MATRIX_SAS.csv', 'DISCARD_SAS.csv', 'uniCourseList.csv', 'uniTechCrsList.csv', 'TECH.csv']
			for suffix in fileNameSuffix:
				fileNameList.append(path+yr+'_'+suffix)
			[self.regREPL, self.regNODUP, self.techRegNODUP, self.CRSPERSTU, self.STUREGISTERED, self.EMPTY, self.EMPTY_STU, self.EMPTY_CRS, self.CRS_STU, self.CRS_STU_GRADE, self.regNODUPREPL, self.STU_CRS, self.STU_CRS_GRADE, self.crsMatrix, self.discardList, self.courselist, self.uniTechCrsList, self.techCrsCSV] = fileNameList

			self.regDataPath = regFile
			self.techCrs()
			self.formatRegSAS(self.regDataPath, self.regNODUP)
			self.formatRegSAS(self.techCrsCSV, self.techRegNODUP)
			self.simpleStats(self.techRegNODUP, self.CRSPERSTU, self.STUREGISTERED, self.EMPTY, self.CRS_STU, self.CRS_STU_GRADE, self.STU_CRS, self.STU_CRS_GRADE)

			randomOrderReg = path+'randomOrderReg'+yr+'.csv'
			randomOrderRegList.append(randomOrderReg)
			self.randomize(self.STU_CRS_GRADE, randomOrderReg, crsDict)

	def randomize(self, src, dest, crsDict):
		reader = csv.reader(open(src), delimiter=',')
		header = reader.next()
		header = header[1:]

		newHeader = []
		for crs in header:
			newHeader.append(crsDict[crs])

		rowList = []
		for row in reader:
			rowList.append(row)

		indexList, toWriteList, writer = [],[],csv.writer(open(dest, 'w'))
		random.seed(datetime.now())		
		while True:
			rnum = random.randint(0,len(rowList)-1)
			if rnum not in indexList:
				indexList.append(rnum)				
				row = rowList[rnum]
				toWriteList.append(row[1:])
			if len(indexList) == len(rowList):
				break

		writer.writerow(newHeader)
		writer.writerows(toWriteList)

	# COLLECT THE GRADES POINTS FOR EVERY PREDICTOR AND PREDICTING COURSE PAIRS, AND THEN PLOT THESE POINTS IN SCATTER SCHEME
	# AND THESE GRAPHS ARE STORED IN self.yrvsyr
	def gradePointsDistribution(self, top1FactorsFile):
		# BUILDING COURSE GRADES DICTIONARY KEY:SUBJECT_CODE+COURSE_NUMBER; VALUE: COURSE GRADES OF ALL STUDENTS
		# DATASOURCE: self.CRS_STU
		courseGradeDict = {}
		r = csv.reader(open(self.CRS_STU), delimiter=',')
		r.next()
		for record in r:
			key = record[0]+record[1]
			courseGradeDict[key] = record

		# DATASOURCE: self.top1FactorsFile
		predictingPairs = []
		r = csv.reader(open(top1FactorsFile), delimiter=',')
		r.next()
		for pair in r:
			# SAVE THE PREDICTOR AND PREDICTING COURSE
			predictingPairs.append(pair[:4])
		
		# if not (self.proPredictor == 'ALL'):
		i1i2, i1i3, i1i4, i2i3, i2i4 = [[],[]],[[],[]],[[],[]],[[],[]],[[],[]]
		for pair in predictingPairs:
			predictorGrades = courseGradeDict[pair[0]+pair[1]][2:]
			predictedCourseGrades = courseGradeDict[pair[2]+pair[3]][2:]
			# THE FIRST DIGIT OF COURSE_NUMBER INDICATING THE YEAR WHEN THE COURSE ARE PROVIDED 
			# AND THE VALUE OF THIS VARIABLE IS IN THE LIST OF [1, 2] WHICH INDICATES THE 1ST YEAR AND SECOND YEAR, RESPECTIVELY
			predictorYr = pair[1][0]
			predictedCourseYr = pair[3][0]

			# THE PREDICTOR COURSE IS A 1ST YEAR COURSE, THEN PLOT 1ST VS 2ND/3RD/4TH, 1ST VS 2ND_3RD, 1ST VS 3RD_4TH AND 1ST VS 2ND_3RD_4TH SCATTER PLOTS
			# GET THE PREDICTOR'S GRADE LIST
			if int(predictorYr) == 1:
				for x in xrange(0, len(predictorGrades)):
					if predictorGrades[x].isdigit() and predictedCourseGrades[x].isdigit():
						# SAVE 1ST VS 2ND POINT PAIRS
						if int(predictedCourseYr) == 2:
							i1i2[0].append(int(predictorGrades[x]))
							i1i2[1].append(int(predictedCourseGrades[x]))
						# SAVE 1ST VS 3RD POINT PAIRS
						if int(predictedCourseYr) == 3:
							i1i3[0].append(int(predictorGrades[x]))
							i1i3[1].append(int(predictedCourseGrades[x]))
						# SAVE 1ST VS 4TH POINT PAIRS
						if int(predictedCourseYr) == 4:
							i1i4[0].append(int(predictorGrades[x]))
							i1i4[1].append(int(predictedCourseGrades[x]))
			# THE PREDICTOR COURSE IS A 2ND YEAR COURSE, THEN PLOT 2ND VS 3RD/4TH AND 2ND VS 3RD_4TH PLOTS
			elif int(predictorYr) == 2:
				for x in xrange(0, len(predictorGrades)):
					if predictorGrades[x].isdigit() and predictedCourseGrades[x].isdigit():
						# SAVE 2ND VS 3RD POINT PAIRS
						if int(predictedCourseYr) == 3:
							i2i3[0].append(int(predictorGrades[x]))
							i2i3[1].append(int(predictedCourseGrades[x]))
						# SAVE 2ND VS 4TH POINT PAIRS
						if int(predictedCourseYr) == 4:
							i2i4[0].append(int(predictorGrades[x]))
							i2i4[1].append(int(predictedCourseGrades[x]))

		# self.yrvsyr: THE DIRECTORY TO SAVE THESE SCATTER PLOTS
		# FOR THE CASE HAVING A PRO-PREDICTOR
		if not (self.proPredictor == 'ALL'):
			predictorYr = self.proPredictor.split(' ')[1][0]
			if int(predictorYr) == 1:
				# PLOT 1ST YEAR VS 2ND
				self.yrVSyrScatter(i1i2[0],i1i2[1],r'%s vs 2nd year courses'%(self.proPredictor), r'%s grades'%(self.proPredictor), '2nd year courses grades',self.yrvsyr+self.proPredictor+'_i1i2.png')
				# PLOT 1ST YEAR VS 3RD
				self.yrVSyrScatter(i1i3[0],i1i3[1],r'%s vs 3rd year courses'%(self.proPredictor), r'%s grades'%(self.proPredictor), '3rd year courses grades',self.yrvsyr+self.proPredictor+'_i1i3.png')
				# PLOT 1ST YEAR VS 4TH
				self.yrVSyrScatter(i1i4[0],i1i4[1],r'%s vs 4th year courses'%(self.proPredictor), r'%s grades'%(self.proPredictor), '4th year courses grades',self.yrvsyr+self.proPredictor+'_i1i4.png')
				# PLOT 1ST YEAR VS 2ND_3RD
				self.yrVSyrScatter(i1i2[0]+i1i3[0],i1i2[1]+i1i3[1],r'%s vs 2nd & 3rd year courses'%(self.proPredictor), r'%s grades'%(self.proPredictor), '2nd & 3rd year courses grades',self.yrvsyr+self.proPredictor+'_i1i2_3.png')
				# PLOT 1ST YEAR VS 3RD_4TH
				self.yrVSyrScatter(i1i3[0]+i1i4[0],i1i3[1]+i1i4[1],r'%s vs 3rd & 4th year courses'%(self.proPredictor), r'%s grades'%(self.proPredictor), '3rd & 4th year courses grades',self.yrvsyr+self.proPredictor+'_i1i3_4.png')
				# PLOT 1ST YEAR VS 2ND_3RD_4TH
				self.yrVSyrScatter(i1i2[0]+i1i3[0]+i1i4[0],i1i2[1]+i1i3[1]+i1i4[1],r'%s vs 2nd, 3rd & 4th year courses'%(self.proPredictor), r'%s grades'%(self.proPredictor), '2nd, 3rd & 4th year courses grades',self.yrvsyr+self.proPredictor+'_i1i2_3_4.png')
			elif int(predictorYr) == 2:
				# PLOT 2ND YEAR VS 3RD
				self.yrVSyrScatter(i2i3[0],i2i3[1],r'%s vs 3rd year courses'%(self.proPredictor), r'%s grades'%(self.proPredictor), '3rd year courses grades',self.yrvsyr+self.proPredictor+'_i2i3.png')
				# PLOT 2ND YEAR VS 4TH
				self.yrVSyrScatter(i2i4[0],i2i4[1],r'%s vs 4th year courses'%(self.proPredictor), r'%s grades'%(self.proPredictor), '4th year courses grades',self.yrvsyr+self.proPredictor+'_i2i4.png')
				# PLOT 2ND YEAR VS 3rd_4TH
				self.yrVSyrScatter(i2i3[0]+i2i4[0],i2i3[1]+i2i4[1],r'%s vs 3rd & 4th year courses'%(self.proPredictor), r'%s grades'%(self.proPredictor), '3rd & 4th year courses grades',self.yrvsyr+self.proPredictor+'_i2i3_4.png')

		if (self.proPredictor == 'ALL'):
			# THE CASE OF PICKING A PREDICTOR PREDICTION, THEN THE PREDICTORS ARE EITHER 1ST YEAR COURSE OR 2ND YEAR COURSE
			# THE 1ST YEAR PREDICTORS ARE IN ONE GROUP AND 2ND YEAR PREDICTORS ARE IN ANOTHER GROUP
			# ALSO, PLOT 1ST YEAR VS 2ND/3RD/4TH, 1ST VS 2ND_3RD, 1ST VS 3RD_4TH AND 1ST VS 2ND_3RD_4TH SCATTER PLOTS
			# FOR THE 2ND YR PREDICTORS, PLOT 2ND VS 3RD/4TH AND 2ND VS 3RD_4TH PLOTS
			# PLUS, COMBINE 1ST YEAR PREDICTORS AND 2ND YEAR PREDICTORS TOGETHER, THEN PLOT 1ST_2ND VS 3RD/4TH AND 1ST_2ND VS 3RD_4TH
			# PLOT 1ST YEAR VS 2ND
			self.yrVSyrScatter(i1i2[0],i1i2[1],'1st year courses vs 2nd year courses', '1st year courses grades', '2nd year courses grades',self.yrvsyr+'ALL_i1i2.png')
			# PLOT 1ST YEAR VS 3RD
			self.yrVSyrScatter(i1i3[0],i1i3[1],'1st year courses vs 3rd year courses', '1st year courses grades', '3rd year courses grades',self.yrvsyr+'ALL_i1i3.png')
			# PLOT 1ST YEAR VS 4TH
			self.yrVSyrScatter(i1i4[0],i1i4[1],'1st year courses vs 4th year courses', '1st year courses grades', '4th year courses grades',self.yrvsyr+'ALL_i1i4.png')
			# PLOT 1ST YEAR VS 2ND_3RD
			self.yrVSyrScatter(i1i2[0]+i1i3[0],i1i2[1]+i1i3[1],'1st year courses vs 2nd & 3rd year courses', '1st year courses grades', '2nd & 3rd year courses grades',self.yrvsyr+'ALL_i1i2_3.png')
			# PLOT 1ST YEAR VS 3RD_4TH
			self.yrVSyrScatter(i1i3[0]+i1i4[0],i1i3[1]+i1i4[1],'1st year courses vs 3rd & 4th year courses', '1st year courses grades', '3rd & 4th year courses grades',self.yrvsyr+'ALL_i1i3_4.png')
			# PLOT 1ST YEAR VS 2ND_3RD_4TH
			self.yrVSyrScatter(i1i2[0]+i1i3[0]+i1i4[0],i1i2[1]+i1i3[1]+i1i4[1],'1st year courses vs 2nd, 3rd & 4th year courses', '1st year courses grades', '2nd, 3rd & 4th year courses grades',self.yrvsyr+'ALL_i1i2_3_4.png')

			# PLOT 2ND YEAR VS 3RD
			self.yrVSyrScatter(i2i3[0],i2i3[1],'2nd year courses vs 3rd year courses', '2nd year courses grades', '3rd year courses grades',self.yrvsyr+'ALL_i2i3.png')
			# PLOT 2ND YEAR VS 4TH
			self.yrVSyrScatter(i2i4[0],i2i4[1],'2nd year courses vs 4th year courses', '2nd year courses grades', '4th year courses grades',self.yrvsyr+'ALL_i2i4.png')
			# PLOT 2ND YEAR VS 3rd_4TH
			self.yrVSyrScatter(i2i3[0]+i2i4[0],i2i3[1]+i2i4[1],'2nd year courses vs 3rd & 4th year courses', '2nd year courses grades', '3rd & 4th year courses grades',self.yrvsyr+'ALL_i2i3_4.png')

			# PLOT 1ST_2ND YEAR VS 3rd
			self.yrVSyrScatter(i1i3[0]+i2i3[0],i1i3[1]+i2i3[1],'1st & 2nd year courses vs 3rd year courses', '1st & 2nd year courses grades', '3rd year courses grades',self.yrvsyr+'ALL_i1_2i3.png')
			# PLOT 1ST_2ND YEAR VS 4TH
			self.yrVSyrScatter(i1i4[0]+i2i4[0],i1i4[1]+i2i4[1],'1st & 2nd year courses vs 4th year courses', '1st & 2nd year courses grades', '4th year courses grades',self.yrvsyr+'ALL_i1_2i4.png')
			# PLOT 1ST_2ND YEAR VS 3rd_4TH
			self.yrVSyrScatter(i1i3[0]+i1i4[0]+i2i3[0]+i2i4[0],i1i3[1]+i1i4[1]+i2i3[1]+i2i4[1],'1st & 2nd year courses vs 3rd & 4th year courses', '1st & 2nd year courses grades', '3rd & 4th year courses grades',self.yrvsyr+'ALL_i1_2i3_4.png')

	def yrVSyrScatter(self,xdata,ydata,title,xlabel,ylabel,fname):
		fig = plt.figure()
		x = np.array(xdata)
		y = np.array(ydata)

		plt.plot(x, y, 'o', c='blue')

		plt.xlabel(xlabel)
		plt.ylabel(ylabel)
		plt.title(title)

		plt.grid(True)
		# plt.show()
		fig.savefig(fname)
		plt.close(fig)

	def createPRFactors(self):
		reader = csv.reader(open(self.pearsoncorr), delimiter=',')
		header = reader.next()
		predictedDict, keys = {}, []
		for row in reader:
			key = row[2]+row[3]
			row[4], row[5] = float(row[4]), int(row[5])
			if key not in predictedDict:
				predictedDict[key] = [row]
			else:
				predictedDict[key].append(row)

			if key not in keys:
				keys.append(key)

		wTop1pF = csv.writer(open(self.top1pFactors, 'w'))
		wTop3pF = csv.writer(open(self.top3pFactors, 'w'))
		wTop1rF = csv.writer(open(self.top1rFactors, 'w'))
		wTop3rF = csv.writer(open(self.top3rFactors, 'w'))
		header.insert(6, 'Pxy')
		for w in [wTop1pF, wTop3pF, wTop1rF, wTop3rF]:
			w.writerow(header)

		for key in keys:
			# get all possible predictors for the predicted course (key=subj+num)
			predictors, pList, rList = predictedDict[key], [], []
			for predictor in predictors:
				pList.append(predictor[5])
				rList.append(abs(predictor[4]))
			for predictor in predictors:
				pxy = abs(predictor[4])*predictor[5]/(max(rList)*max(pList))
				predictor.insert(6, float(format(pxy, '.6')))
			# build top1 pFactors: self.top1pFactors
			top1pFactor = self.topFactors(predictors, 1, 5)
			wTop1pF.writerows(top1pFactor)
			# build top3 pFactors: self.top3pFactors
			top3pFactors = self.topFactors(predictors, 3, 5)
			wTop3pF.writerows(top3pFactors)
			# build top1 rFactors: self.top1rFactors
			top1rFactor = self.topFactors(predictors, 1, 4)
			wTop1rF.writerows(top1rFactor)
			# build top3 rFactors: self.top3rFactors
			top3rFactors = self.topFactors(predictors, 3, 4)
			wTop3rF.writerows(top3rFactors)

	def topFactors(self, predictors, topx, rpIndex):
		# find the top factors based on topx (topx=1, 3)
		# predictors: all possible predictors; rpIndex: rIndex=4, pIndex=5
		results = []
		predictors.sort(key=itemgetter(rpIndex), reverse=True)
		# topValues = [top1, top2, top3] or [top1]
		topValues, maxList, xnums = [], [], []
		# more predictors record than topx
		if len(predictors) >= topx:
			for x in xrange(0,topx):
				topValues.append(predictors[x][rpIndex])
		else:
			for predictor in predictors:
				topValues.append(predictor[rpIndex])

		for predictor in predictors:
			if predictor[rpIndex] in topValues:
				maxList.append(predictor)
				xnums.append(int(predictor[1][:3]))

		if topx == 1:
			if len(maxList) > 1:
				# there are more than one preditor with the maximum of points or coefficient, then select the one with smallest course number
				minNum = min(xnums)
				for item in maxList:
					if int(item[1][:3]) == minNum:
						results = [item]
			else:
				# there is only one preditor with the maximum of points or coefficient
				results = [predictors[0]]

		if topx == 3:
			# there are only 3 or less predictors, then use all of them as final predictors
			if len(predictors) <= topx:
				results = predictors
			else:
				# there are more than 3 predictos which have one of the topValues, then find the top3 as predictors
				freq = Counter(item for item in topValues)
				# top1==top2==top3, find the 3 courses with the top3 smallest course numbers
				if len(freq) == 1:
					# sort xnums ascendingly
					xnums.sort()
					for item in maxList:
						if int(item[1][:3]) in xnums[:3]:
							results.append(item)
				# there are two top values with the same values
				if len(freq) == 2:
					# top1 == top2, use top1 and top2 courses as predictors, then use the course with the smallest course number as predictor if there are more than one courses with top3rd
					if topValues[0] == topValues[1]:
						results = [maxList[0],maxList[1]]
						top3rdNums = xnums[2:]
						top3rdNums.sort()
						for item in maxList[2:]:
							if int(item[1][:3]) == top3rdNums[0]:
								results.append(item)
								break
					# top2 == top3, use top1 as predictor, use the two with the smallest course numbers as predictors
					else:
						results.append(maxList[0])
						top2nd3rdNums = xnums[1:]
						top2nd3rdNums.sort()
						for item in maxList[1:]:
							if int(item[1][:3]) in top2nd3rdNums[:2]:
								results.append(item)
				# top1 != top2 != top3
				if len(freq) == 3:
					results = [maxList[0],maxList[1],maxList[2]]

		return results

prepare = splitRawData(sys.argv)
prepare.doBatch()
prepross(prepare.splitedRawData()).doBatch()
