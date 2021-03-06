#!/usr/bin/env python

import csv, os, time, hashlib, shutil, xlsxwriter, copy as myCopy, matplotlib.pyplot as plt, numpy as np
from pylab import *
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.ticker import MultipleLocator
from scipy.stats import pearsonr, linregress, skew
from operator import itemgetter
from collections import Counter
import organizer
# from matplotlib import rcParams
# rcParams.update({'figure.autolayout': True})

class prepross(object):
	def __init__(self, degRegFiles):
		super(prepross, self).__init__()
		self.trainYrsList = [['2010', '2011'], ['2010', '2011', '2012'], ['2010', '2011', '2012', '2013'], ['2010', '2011', '2012', '2013', '2014']]
		# self.thresholdList = [1,5,10,15,20]
		self.thresholdList = [1]
		self.regFileList, self.degFileList, self.yearList, self.rawReg, self.rawDeg = degRegFiles

		# define the predictor course: ALL: use common predictors based on the picking criteria
		self.predictorCourses = ['ALL', 'SINGLE']
		# self.predictorCourses = ['ALL']
		self.f1courseList = ['CSC 110', 'MATH 100', 'MATH 133', 'MECH 141', 'PHYS 122', 'CHEM 150', 'ELEC 199', 'MATH 101', 'PHYS 125', 'CSC 160', 'CSC 115', 'CSC 111', 'ENGR 141']
		self.s2courseList = ['MATH 200', 'ELEC 200', 'ELEC 216', 'ELEC 220', 'MATH 201', 'CENG 241', 'ELEC 250', 'ELEC 260', 'MECH 295', 'CENG 255', 'STAT 254', 'CSC 230']

		self.factors = ['PR', 'P', 'R']

		# weights dictionary: key: the threshold; value: a dictionary with keys of train data length and value of weights
		self.wdict = {	1:{2:1.3, 3:1.1, 4:1.1, 5:1.1},
						5:{2:1.3, 3:1.1, 4:1.1, 5:1.2},
						10:{2:1.3, 3:1.1, 4:1.1, 5:1.2},
						15:{2:1.3, 3:1.1, 4:1.1, 5:1.2},
						20:{2:1.3, 3:1.1, 4:1.1, 5:1.2} }

		self.errMerge = False

	def statsPath(self):
		pathList, path = self.regFileList[0].split('/'), '/'
		for x in xrange(0,len(pathList[1:-2])):
			path = path+pathList[1:-1][x] + '/'

		# For MTIS
		self.matrixDir = path+'matrix/'

		self.allTechCrs = path+'techcourses/'+'technicalCourse.csv'
		self.availableTechCrsList, self.techList = [],[]

		self.timeDir = path+time.strftime('%Y%m%d')+'/'
		# No specific predictor
		if self.proPredictor == 'ALL':
			if len(self.trainYrs) > 1:
				self.trainYrsText = str(self.trainYrs[0])+'-'+str(self.trainYrs[-1])
			else:
				self.trainYrsText = str(self.trainYrs[0])

			self.currDir = self.timeDir+self.trainYrsText+'/'+self.factor+'/'
			self.dataDir = self.timeDir+self.trainYrsText+'/'+'data/'

			self.linear_plots_ori = self.timeDir+self.trainYrsText+'/LPlots_ori/'
			self.quadratic_plots_ori = self.timeDir+self.trainYrsText+'/QPlots_ori/'

			self.boxplots = self.timeDir+self.trainYrsText+'/boxPlots/'
		else:
			self.currDir = self.timeDir+self.proPredictor.replace(' ','')+'/'
			self.dataDir, self.rpDir4Single = self.currDir+'data/', self.currDir+'rp/'
			self.linear_plots_ori, self.quadratic_plots_ori = self.timeDir+self.proPredictor+'/LPlots_ori/', self.timeDir+self.proPredictor+'/QPlots_ori/'

			self.boxplots = self.timeDir+'boxPlots/'

			self.mergeSingleL, self.mergeSingleQ = self.currDir+'T1/L/mergeSingleL.csv', self.currDir+'T1/Q/mergeSingleQ.csv'

			self.meanPearson, self.meanPairs, self.f1s2CrsVnums, self.vnumMeans = self.dataDir+'meanPearsonCorr.csv', self.dataDir+'Train/MEANPAIRS_SAS.csv', self.dataDir+'Train/F1S2CRSVNUMS_SAS.csv', self.dataDir+'Train/VNUMSMEANS_SAS.csv'
			self.meanPlot, self.meanTest = self.timeDir+'MEAN/meanPlots/', self.timeDir+'MEAN/meanTest/'
			self.meanPredictedLCSV, self.meanPredictedQCSV, self.meanPrecisionL, self.meanPredictedELCSV, self.meanPredictedEQCSV, self.meanPrecisionQ = self.meanTest+'PMean_L.csv', self.meanTest+'PMean_Q.csv', self.meanTest+'PMean_PL.csv', self.meanTest+'PMean_EL.csv', self.meanTest+'PMean_EQ.csv', self.meanTest+'PMean_PQ.csv'
			for item in [self.meanPlot, self.meanTest, self.rpDir4Single]:
				if not os.path.exists(item):
					os.makedirs(item)

		[self.coefficient_ori, self.hist_ori, self.bars_ori, self.course_ori, self.pairsHistDir, self.splitsDir, self.maerp3DDir, self.yrvsyr, self.yr1l, self.yr2l, self.yr1q, self.yr2q] = [self.currDir+'coefficient_ori/', self.currDir+'hist_ori/', self.currDir+'bars_ori/', self.currDir+'course_ori/', self.currDir+'pairs_hist/', path+'splits/', self.currDir+'3d/', self.currDir+'yrVSyr/', self.currDir+'Yr1L/', self.currDir+'Yr2L/', self.currDir+'Yr1Q/', self.currDir+'Yr2Q/']

		pathBuilderList = [self.linear_plots_ori, self.quadratic_plots_ori, self.currDir, self.dataDir, self.dataDir+'Test/', self.dataDir+'Train/', self.currDir+'T1/L/', self.currDir+'T1/Q/', self.coefficient_ori, self.hist_ori, self.bars_ori, self.course_ori, self.pairsHistDir, self.splitsDir, self.matrixDir, self.maerp3DDir+'L/',self.maerp3DDir+'Q/', self.yrvsyr, self.boxplots]

		# filter the folders to create depending on the proPredictor and the year of predictor course
		if self.proPredictor == 'ALL':
			pathBuilderList += [self.currDir+'T3/L/', self.currDir+'T3/Q/', self.yr1l+'2/', self.yr1l+'3/', self.yr1l+'4/', self.yr1q+'2/', self.yr1q+'3/', self.yr1q+'4/', self.yr2l+'3/', self.yr2l+'4/', self.yr2q+'3/', self.yr2q+'4/']
		else:
			pathBuilderList += [self.yr1l+'2/', self.yr1l+'3/', self.yr1l+'4/', self.yr1q+'2/', self.yr1q+'3/', self.yr1q+'4/']
			pathBuilderList += [self.yr2l+'3/', self.yr2l+'4/', self.yr2q+'3/', self.yr2q+'4/']

		for item in pathBuilderList:
			if not os.path.exists(item):
				os.makedirs(item)

		self.pairsFrequency, self.pearsoncorr, self.skewness = self.dataDir+'pairsFrequency.csv', self.dataDir+'pearsonCorr.csv', self.dataDir+'skewness.csv'
		if self.proPredictor == 'ALL':
			self.degDataPath, self.regDataPath = self.splitsDir+'deg'+self.trainYrs[0]+'-'+self.trainYrs[-1]+'.csv', self.splitsDir+'reg'+self.trainYrs[0]+'-'+self.trainYrs[-1]+'.csv'
			self.top1pFactors, self.top3pFactors = self.dataDir + 'T1F_P_' + self.trainYrsText +'.csv', self.dataDir + 'T3F_P_' + self.trainYrsText +'.csv'
			self.top1rFactors, self.top3rFactors = self.dataDir + 'T1F_R_' + self.trainYrsText +'.csv', self.dataDir + 'T3F_R_' + self.trainYrsText +'.csv'
			self.top1FactorsFile, self.top3FactorsFile, self.weightPxyFile = '', '', ''

			self.linearTop1Top3Stats, self.quadraticTop1Top3Stats = self.currDir+'LT1T3Stats_'+self.trainYrsText+'.csv', self.currDir+'QT1T3Stats_'+self.trainYrsText+'.csv'
			self.linearQuadraticTop1Stats, self.linearQuadraticTop3Stats = self.currDir+'LQT1Stats_'+self.trainYrsText+'.csv', self.currDir+'LQT3Stats_'+self.trainYrsText+'.csv'
		else:
			self.degDataPath, self.regDataPath = self.rawDeg, self.rawReg
			self.top1FactorsFile = self.pearsoncorr
			self.linearQuadraticTop1Stats = self.currDir+'LQT1Stats_'+self.proPredictor+'.csv'

		# for test reg data
		# store test data's noDup filenames
		self.fTestRegFileNameList = []
		# store stats filenames for all of the test data
		self.fTestStatFileNameList = []
		# store test filenames
		self.testFileList = [self.regDataPath]

		if self.proPredictor == 'ALL':
			# use all of the data as one of the test datasets
			self.testFileList.append(self.rawReg)
			# create year combined test data
			combineYrsTestData = self.splitsDir+'reg'+self.yearList[len(self.trainYrs)]+'-'+self.yearList[-1]+'.csv'
			# self.comYrsTestHeader = ''
			for yr in self.yearList:
				if (yr not in self.trainYrs):
					index = self.yearList.index(yr)
					reg = self.regFileList[index]
					self.testFileList.append(reg)

			if len(self.trainYrs) != 5:
				self.testFileList.append(combineYrsTestData)

		# build test stats filenames and the predicting result and errors filenames
		self.linearPredictResultsListTop1, self.quadrPredictResultsListTop1 = [], []

		# this only works for use ALL predictors, not for a specific predictor
		if self.proPredictor == 'ALL':
			self.linearPredictResultsListTop3, self.quadrPredictResultsListTop3 = [], []
			self.linearPredictResultsListALL, self.quadrPredictResultsListALL = [], []

		for fname in self.testFileList:
			filename = fname.split('/')[-1].split('.')[0]
			# todo: optimize later
			if self.proPredictor == 'ALL':
				self.linearPredictResultsListTop1.append(self.currDir + 'T1/L/' + filename + '_' + self.factor + '_L.csv')
				self.quadrPredictResultsListTop1.append(self.currDir + 'T1/Q/' + filename + '_' + self.factor + '_Q.csv')
				self.linearPredictResultsListALL.append(self.currDir + 'T1/L/' + filename + self.factor + 'L.csv')
				self.quadrPredictResultsListALL.append(self.currDir + 'T1/Q/' + filename + self.factor + 'Q.csv')
				self.linearPredictResultsListTop3.append(self.currDir + 'T3/L/' + filename +'_L3.csv')
				self.quadrPredictResultsListTop3.append(self.currDir + 'T3/Q/' + filename +'_Q3.csv')
			else:
				self.linearPredictResultsListTop1.append(self.currDir + 'T1/L/' + filename + '_' + self.proPredictor + '_L.csv')
				self.quadrPredictResultsListTop1.append(self.currDir + 'T1/Q/' + filename + '_' + self.proPredictor + '_Q.csv')

			tmpList, prefix, testPath, yr = [], '', '',''
			if (fname == self.regDataPath) or (combineYrsTestData == fname):
				if self.proPredictor == 'ALL':
						testPath = self.dataDir +'Test/' + filename[3:12] + '/'
				else:
					testPath = self.dataDir +'Test/' + filename + '/'

				prefix = testPath + filename
				self.fTestRegFileNameList.append([prefix + '_TTech.csv', prefix + '_Test.csv'])
			else:
				if (fname == self.rawReg):
					testPath = self.dataDir +'Test/' + filename + '/'
					prefix = testPath + filename
				else:
					testPath = self.dataDir +'Test/' + filename[3:] + '/'
					prefix = testPath + filename[0:3] + 'test' + filename[3:]
				self.fTestRegFileNameList.append([prefix + '_TTech.csv', prefix + '_Test.csv'])

			if not os.path.exists(testPath):
				os.makedirs(testPath)

			for item in ['CRSPERSTU', 'STUREGISTERED', 'EMPTY', 'CRS_STU', 'CRS_STU_GRADE', 'STU_CRS', 'STU_CRS_GRADE']:
				tmpList.append(prefix + '_' + item +'.csv')

			self.fTestStatFileNameList.append(tmpList)
			# self.CRSPERSTU, self.STUREGISTERED, self.EMPTY, self.CRS_STU, self.CRS_STU_GRADE, self.STU_CRS

		# REPL, NODUP, CRSPERSTU, STUREGISTERED, EMPTY, EMPTY_STU, EMPTY_CRS, CRS_STU, IDMAPPER
		fileNameList = ['REPL.csv', 'NODUP.csv', 'TECH_NODUP.csv', 'CRSPERSTU.csv', 'STUREGISTERED.csv', 'EMPTY.csv', 'EMPTY_STU.csv', 'EMPTY_CRS.csv', 'CRS_STU.csv', 'CRS_STU_GRADE.csv', 'NODUP_REPL.csv', 'STU_CRS.csv', 'STU_CRS_GRADE.csv', 'CRS_MATRIX.csv', 'DISCARD.csv', 'uniCourseList.csv', 'uniTechCrsList.csv', 'TECH.csv', 'nan.csv', 'CRS_PAIRS.csv']
		for x in xrange(0,len(fileNameList)):
			fileNameList[x] = self.dataDir+'Train/'+fileNameList[x]

		[self.regREPL, self.regNODUP, self.techRegNODUP, self.CRSPERSTU, self.STUREGISTERED, self.EMPTY, self.EMPTY_STU, self.EMPTY_CRS, self.CRS_STU, self.CRS_STU_GRADE, self.regNODUPREPL, self.STU_CRS, self.STU_CRS_GRADE, self.crsMatrix, self.discardList, self.courselist, self.uniTechCrsList, self.techCrsCSV, self.nancsv, self.CRS_PAIRS] = fileNameList

		self.degREPL, self.IDMAPPER = self.dataDir+'REPL_SAS.csv', self.dataDir+'IDMAPPER_SAS.csv'

	def doBatch(self):
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
			# top1 prediction
			self.predictProcessTop1Factors(self.fTestStatFileNameList[x][3], self.linearPredictResultsListTop1[x], 1, predictors[0])
			self.predictProcessTop1Factors(self.fTestStatFileNameList[x][3], self.quadrPredictResultsListTop1[x], 2, predictors[0])

			# multiple predictors prediction
			self.predictProcessMultiFactors(self.fTestStatFileNameList[x][3], self.linearPredictResultsListALL[x], 1, self.pearsoncorr)
			self.predictProcessMultiFactors(self.fTestStatFileNameList[x][3], self.quadrPredictResultsListALL[x], 2, self.pearsoncorr)

			# top3 prediction
			self.predictProcessTop3Factors(self.fTestStatFileNameList[x][3], self.linearPredictResultsListTop3[x], 1, predictors[1])
			self.predictProcessTop3Factors(self.fTestStatFileNameList[x][3], self.quadrPredictResultsListTop3[x], 2, predictors[1])

	def predicting4Specific(self):
		# predition for meanPrediction
		self.f1s2YrTechYrCrsMeanPrediction(self.meanPairs, self.meanPearson)

		# predition for all test sets
		self.testSetsStats()
		for x in xrange(0,len(self.fTestStatFileNameList)):
			self.predictProcessMultiFactors(self.fTestStatFileNameList[x][3], self.linearPredictResultsListTop1[x], 1, self.top1FactorsFile)
			self.predictProcessMultiFactors(self.fTestStatFileNameList[x][3], self.quadrPredictResultsListTop1[x], 2, self.top1FactorsFile)

	def prepare(self):
		self.techCrs()
		self.formatRegSAS(self.regDataPath, self.regNODUP)
		self.formatRegSAS(self.techCrsCSV, self.techRegNODUP)
		self.simpleStats(self.techRegNODUP, self.CRSPERSTU, self.STUREGISTERED, self.CRS_STU, self.CRS_STU_GRADE, self.STU_CRS, self.STU_CRS_GRADE)
		self.createCrspairs(self.CRS_PAIRS, self.CRS_STU)
		self.pairs()
		self.pairsHists()

		self.uniqueCourseList()
		self.uniqueTechCrsList()

		self.techCrsHists()

		# compute correlation coefficients and draw correlation plots
		# if self.proPredictor == 'ALL':
		self.corrPlot(self.CRS_STU, self.pearsoncorr, self.skewness)
		organizer.courseOrganizer(self.skewness)
		# else:
		# 	self.corrPlotOneProPredictor(self.CRS_STU, self.pearsoncorr)

	def testSetsStats(self):
		# compute the stats data for the test datasets
		for testFile in self.testFileList:
			index = self.testFileList.index(testFile)
			# TTech: all tech records; noDupFile stores noDupTechCourses
			TTech, noDupFile = self.fTestRegFileNameList[index]
			self.techCoursePicker(testFile, TTech)
			self.formatRegSAS(TTech, noDupFile)

			statList = self.fTestStatFileNameList[index]
			self.simpleStats(noDupFile, statList[0], statList[1], statList[3], statList[4], statList[5], statList[6])

	def testWeights(self):
		# trying to find the good weights
		w1 = [1, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9, 2.0, 2.1, 2.2, 2.3, 2.4, 2.5]
		w2 = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
		self.formulaV1Integrate(w1,w2)

	def computeALL(self):
		self.predictionPrecisionALLList = []
		for yrList in self.trainYrsList:
			self.threshold, self.isPrepared = 1, False
			tripleFactorDict, MRMergeList, accRetList, maeRetList = {}, [], [], []
			for factor in self.factors:
				self.trainYrs, self.factor = yrList, factor
				self.statsPath()
				tripleFactorDict[factor] = {'L':self.linearPredictResultsListTop1, 'Q':self.quadrPredictResultsListTop1}

				self.predictionPrecisionALLList += myCopy.deepcopy(self.linearPredictResultsListTop1+self.quadrPredictResultsListTop1)

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
					self.predictorsDict = {'PR':[self.top1FactorsFile, self.top3FactorsFile],'P':[self.top1pFactors, self.top3pFactors],'R':[self.top1rFactors, self.top3rFactors]}

				self.predictorsScatterPlots()
				# self.predicting4ALL(self.wdict[self.threshold][len(self.trainYrs)], 1.0)
				self.predicting4ALL()
				self.mergePrecision4ALL(self.trainYrsText, self.linearPredictResultsListALL+self.quadrPredictResultsListALL, self.factor)

				# merge MAEs, Ranges
				MRFiles, accRets, maeRets = self.mergeMAEsRangesManager()
				MRMergeList+=MRFiles
				accRetList+=accRets
				maeRetList+=maeRets

				# plot yr vs yr scatter plots
				# self.gradePointsDistribution(self.predictorsDict[self.factor][0])

				# # todo: stats
				if self.errMerge:
					self.errTop1Top3StatsMerger(self.linearTop1Top3Stats, self.linearPredictResultsListTop1, self.linearPredictResultsListTop3)
					self.errTop1Top3StatsMerger(self.quadraticTop1Top3Stats, self.quadrPredictResultsListTop1, self.quadrPredictResultsListTop3)
					self.errLinearQuadraticStatsMerger(self.linearQuadraticTop1Stats, self.linearPredictResultsListTop1, self.quadrPredictResultsListTop1)
					self.errLinearQuadraticStatsMerger(self.linearQuadraticTop3Stats, self.linearPredictResultsListTop3, self.quadrPredictResultsListTop3)

			self.tripleFactorGrouper(tripleFactorDict, self.trainYrsText)
			self.mrMerger(MRMergeList, accRetList, maeRetList, self.trainYrsText)
		self.mergeACC_MAE_4PedALL(self.predictionPrecisionALLList)

	def mrMerger(self, fileList, accRetList, maeRetList, trainYrsText):
		mrXlsx = self.timeDir+trainYrsText+'_MRMerger.xlsx'
		workbook = xlsxwriter.Workbook(mrXlsx)
		myformat = workbook.add_format({'align':'center_across'})

		worksheet, rowcnt = workbook.add_worksheet('AccTable'), 0
		for row in [['Train', 'Test', 'Factor', 'Reg', 'Year', 'Max', 'Min']]+accRetList:
			worksheet.write_row(rowcnt,0,row,myformat)
			print row
			rowcnt+=1

		worksheet, rowcnt = workbook.add_worksheet('MAETable'), 0
		for row in [['Train', 'Test', 'Factor', 'Reg', 'Year', 'Max', 'Min']]+maeRetList:
			worksheet.write_row(rowcnt,0,row,myformat)
			print row
			rowcnt+=1

		for item in fileList:
			r = csv.reader(open(item), delimiter=',')
			sheetName = item.split('/')[-1].split('.')[0]
			worksheet, rowcnt = workbook.add_worksheet(sheetName), 0
			for row in r:
				worksheet.write_row(rowcnt,0,row,myformat)
				rowcnt+=1

	def tripleFactorGrouper(self, tripleFactorDict, trainYrsText):
		precisionXlsx = self.timeDir+trainYrsText+'_Triple_ACC.xlsx'
		MAEXlsx = self.timeDir+trainYrsText+'_Triple_MAE.xlsx'

		workbook = xlsxwriter.Workbook(precisionXlsx)
		MAEWorkbook = xlsxwriter.Workbook(MAEXlsx)
		myformat = workbook.add_format({'align':'center_across'})
		MAEmyformat = MAEWorkbook.add_format({'align':'center_across'})

		PLList, PQList = tripleFactorDict['P']['L'], tripleFactorDict['P']['Q']
		RLList, RQList = tripleFactorDict['R']['L'], tripleFactorDict['R']['Q']
		PRLList, PRQList = tripleFactorDict['PR']['L'], tripleFactorDict['PR']['Q']
		acc_In_All_Tests, MAE_In_All_Tests = [], []
		for fullname in PLList:
			test, factor, regression = fullname.split('/')[-1].split('.')[0].split('_')
			precisionHeader, pairArrs, MAEHeader, MAEPairArrs = '', [], '', []
			for filenamelist in [PLList, PQList, RLList, RQList, PRLList, PRQList]:
				testResultFile = self.getTestFactorRegFromFileName(test, filenamelist)
				if testResultFile != '':
					precisionHeader, resultList = self.readPrecision(testResultFile)
					MAEHeader, MAEResultList = self.readMAE(testResultFile)
					if len(resultList) > 0:
						pairArrs+=resultList
						acc_In_All_Tests+=resultList
					if len(MAEResultList) > 0:
						MAEPairArrs+=MAEResultList
						MAE_In_All_Tests+=MAEResultList

			self.writeWorkSheet(pairArrs, precisionHeader, workbook, test, myformat)
			self.writeWorkSheet(MAEPairArrs, MAEHeader, MAEWorkbook, test, MAEmyformat)

		self.writeWorkSheetMAE_ACC(acc_In_All_Tests, precisionHeader, 17, workbook, 'ACC', myformat, 'ACC')
		self.writeWorkSheetMAE_ACC(MAE_In_All_Tests, MAEHeader, 16, MAEWorkbook, 'MAE', MAEmyformat, 'MAE')

	def writeWorkSheetMAE_ACC(self, pairArrs, header, cmpIndex, workbook, sheetName, sheetFormat, category):
		s2List,t3List,f4List = self.groupRecsByYear(pairArrs, 7)

		worksheet, rowcnt = workbook.add_worksheet(sheetName), 0
		rowcnt, cmpList2, cmpFactorList2 = self.writeInOrderMAE_ACC(s2List, 6, 7, 2, 3, cmpIndex, worksheet, rowcnt, sheetFormat, header, category)
		rowcnt, cmpList3, cmpFactorList3 = self.writeInOrderMAE_ACC(t3List, 6, 7, 2, 3, cmpIndex, worksheet, rowcnt, sheetFormat, header, category)
		rowcnt, cmpList4, cmpFactorList4 = self.writeInOrderMAE_ACC(f4List, 6, 7, 2, 3, cmpIndex, worksheet, rowcnt, sheetFormat, header, category)

		worksheet, rowcnt = workbook.add_worksheet('LQ_CMP'), 0
		rowcnt = self.writeSheet(cmpList2+['']+cmpList3+['']+cmpList4, worksheet, sheetFormat, rowcnt)

		worksheet, rowcnt = workbook.add_worksheet('Factors_CMP'), 0
		rowcnt = self.writeSheet(cmpFactorList2+['']+cmpFactorList3+['']+cmpFactorList4, worksheet, sheetFormat, rowcnt)

	def writeSheet(self, cmpList, worksheet, sheetFormat, rowcnt):
		myrowcnt = rowcnt
		for row in cmpList+['']:
			worksheet.write_row(myrowcnt,0,row,sheetFormat)
			myrowcnt+=1

		return myrowcnt

	def writeInOrderMAE_ACC(self, pairArrs, pedCrsIndex, pedNumIndex, sortIndex1, sortIndex2, cmpIndex, worksheet, rowcnt, sheetFormat, header, category):
		predictedDict, myrowcnt, cmpLQList, cmpFactorList = {}, rowcnt, [], []
		for pair in pairArrs:
			# key: predicted course
			key = pair[pedCrsIndex]+pair[pedNumIndex]
			if key not in predictedDict:
				predictedDict[key] = [pair]
			else:
				predictedDict[key].append(pair)

		cmpStats, pcmpStat, rcmpStat, prcmpStat = [], ['P', 0, 0, 0], ['R,', 0, 0, 0], ['PR', 0, 0, 0]
		for key, items in predictedDict.items():
			items.sort(key=itemgetter(pedCrsIndex,pedNumIndex,sortIndex1), reverse=False)
			LDict, QDict = self.groupRecsByReg(items)
			for row in [header]+items+['']:
				worksheet.write_row(myrowcnt,0,row,sheetFormat)
				myrowcnt+=1

			cmpLFactorList = self.FactorCMP(key, LDict, cmpIndex, 'L')
			cmpQFactorList = self.FactorCMP(key, QDict, cmpIndex, 'Q')
			cmpFactorList+=cmpLFactorList+['']+cmpQFactorList+['']

			items.sort(key=itemgetter(pedCrsIndex,pedNumIndex,sortIndex2), reverse=False)
			pList,rList,prList = self.groupRecsByFactor(items, 3)
			for subitems in [pList,rList,prList]:
				for row in [header]+subitems+['']:
					worksheet.write_row(myrowcnt,0,row,sheetFormat)
					myrowcnt+=1

			pcmp, pcmpList = self.compareLQMAE_ACC('P', pList, cmpIndex, category)
			rcmp, rcmpList = self.compareLQMAE_ACC('R', rList, cmpIndex, category)
			prcmp, prcmpList = self.compareLQMAE_ACC('PR', prList, cmpIndex, category)

			cmpLQList+=[['PedCrs','PL','PQ','RL','RQ','PRL','PRQ'], [key]+pcmp+rcmp+prcmp]+['']+pcmpList+['']+rcmpList+['']+prcmpList+['']
			cmpStats+=[[key]+pcmp+rcmp+prcmp]
			self.factorCmpStat(pcmpStat, pcmp)
			self.factorCmpStat(rcmpStat, rcmp)
			self.factorCmpStat(prcmpStat, prcmp)

			for row in [['PedCrs','PL','PQ','RL','RQ','PRL','PRQ'], [key]+pcmp+rcmp+prcmp, '']:
				worksheet.write_row(myrowcnt,0,row,sheetFormat)
				myrowcnt+=1

		return [myrowcnt, cmpLQList+['', ['PedCrs','PL','PQ','RL','RQ','PRL','PRQ']]+cmpStats+['', ['Factor', 'Q>L', 'Q=L', 'Q<L']]+[pcmpStat, rcmpStat, prcmpStat, ''], cmpFactorList]

	def factorCmpStat(self, src, cmpArr):
		# L<Q
		if cmpArr[0] < cmpArr[1]:
			src[1]+=1
		# L>Q
		elif cmpArr[0] > cmpArr[1]:
			src[3]+=1
		# L=Q
		else:
			src[2]+=1

	def FactorCMP(self, pedCrs, arrDict, cmpIndex, regression):
		testList, PR_MAE_ACC_List, P_MAE_ACC_List, R_MAE_ACC_List, PDiffList, RDiffList = [pedCrs, regression], [pedCrs, 'PR'], [pedCrs, 'P'], [pedCrs, 'R'], [pedCrs, 'PDiff'], [pedCrs, 'RDiff']
		for key, items in arrDict.items():
			testList+=[key]
			pr, p, r = '', '', ''
			for x in items:
				if x[3]=='PR':
					pr=x
				if x[3]=='P':
					p=x
				if x[3]=='R':
					r=x

			if pr != '':
				PR_MAE_ACC_List+=[float(pr[cmpIndex])]
			else:
				PR_MAE_ACC_List+=['']

			if p!='':
				P_MAE_ACC_List+=[float(p[cmpIndex])]
				if pr != '':
					PDiffList+=[float(pr[cmpIndex])-float(p[cmpIndex])]
				else:
					PDiffList+=[float(p[cmpIndex])]
			else:
				P_MAE_ACC_List+=['']
				PDiffList+=['']

			if r!='':
				R_MAE_ACC_List+=[float(r[cmpIndex])]
				if pr != '':
					RDiffList+=[float(pr[cmpIndex])-float(r[cmpIndex])]
				else:
					RDiffList+=[float(r[cmpIndex])]
			else:
				R_MAE_ACC_List+=['']
				RDiffList+=['']

		return [testList, PR_MAE_ACC_List, P_MAE_ACC_List, R_MAE_ACC_List, PDiffList, RDiffList]

	def groupRecsByReg(self, arrs):
		LList, QList = [], []
		for item in arrs:
			if item[2] == 'L':
				LList.append(item)
			if item[2] == 'Q':
				QList.append(item)

		return [self.groupRecsByTest(LList), self.groupRecsByTest(QList)]

	def groupRecsByTest(self, arrs):
		testDict = {}
		for item in arrs:
			if item[1] not in testDict:
				testDict[item[1]] = [item]
			else:
				testDict[item[1]].append(item)

		return testDict

	def compareLQMAE_ACC(self, factor, arrs, cmpIndex, category):
		if len(arrs)%2!=0:
			return [[-1],[-1]]

		lcnt, qcnt = 0, 0
		testList, L_MAE_ACC_List, Q_MAE_ACC_List, diffList = [factor], ['L'], ['Q'], ['LQDiff']
		for x in xrange(0,len(arrs), 2):
			testList+=[arrs[x][1]]
			L_MAE_ACC_List+=[float(arrs[x][cmpIndex])]
			Q_MAE_ACC_List+=[float(arrs[x+1][cmpIndex])]
			diffList+=[float(arrs[x][cmpIndex])-float(arrs[x+1][cmpIndex])]

			if float(arrs[x][cmpIndex])>float(arrs[x+1][cmpIndex]):
				lcnt+=1
			elif float(arrs[x][cmpIndex])==float(arrs[x+1][cmpIndex]):
				qcnt+=1
				lcnt+=1
			else:
				qcnt+=1

		if category == 'MAE':
			return [[qcnt, lcnt], [testList, L_MAE_ACC_List, Q_MAE_ACC_List, diffList]]
		else:
			return [[lcnt, qcnt], [testList, L_MAE_ACC_List, Q_MAE_ACC_List, diffList]]

	def groupRecsByFactor(self, arrs, factorIndex):
		pList,rList,prList = [],[],[]
		for item in arrs:
			if item[factorIndex]=='P':
				pList.append(item)
			if item[factorIndex]=='R':
				rList.append(item)
			if item[factorIndex]=='PR':
				prList.append(item)

		pList.sort(key=itemgetter(1), reverse=False)
		rList.sort(key=itemgetter(1), reverse=False)
		prList.sort(key=itemgetter(1), reverse=False)

		return [pList,rList,prList]

	def writeWorkSheet(self, pairArrs, header, workbook, sheetName, sheetFormat):
		s2List,t3List,f4List = self.groupRecsByYear(pairArrs, 7)

		worksheet, rowcnt = workbook.add_worksheet(sheetName), 0

		# order by regression
		rowcnt = self.writeInOrder(s2List, 6, 7, 2, worksheet, 0, sheetFormat, header)
		rowcnt = self.writeInOrder(t3List, 6, 7, 2, worksheet, rowcnt, sheetFormat, header)
		rowcnt = self.writeInOrder(f4List, 6, 7, 2, worksheet, rowcnt, sheetFormat, header)
		# order by factor
		rowcnt = self.writeInOrder(s2List, 6, 7, 3, worksheet, rowcnt, sheetFormat, header)
		rowcnt = self.writeInOrder(t3List, 6, 7, 3, worksheet, rowcnt, sheetFormat, header)
		rowcnt = self.writeInOrder(f4List, 6, 7, 3, worksheet, rowcnt, sheetFormat, header)

		pairArrs.sort(key=itemgetter(6,7,3), reverse=False)
		for row in ['', '', header]+pairArrs:
			worksheet.write_row(rowcnt,0,row,sheetFormat)
			rowcnt+=1

	def writeInOrder(self, pairArrs, pedCrsIndex, pedNumIndex, sortIndex, worksheet, rowcnt, sheetFormat, header):
		predictedDict, myrowcnt = {}, rowcnt
		for pair in pairArrs:
			# key: predicted course
			key = pair[pedCrsIndex]+pair[pedNumIndex]
			if key not in predictedDict:
				predictedDict[key] = [pair]
			else:
				predictedDict[key].append(pair)

		for key, items in predictedDict.items():
			items.sort(key=itemgetter(pedCrsIndex,pedNumIndex,sortIndex), reverse=False)
			for row in [header]+items+['']:
				worksheet.write_row(myrowcnt,0,row,sheetFormat)
				myrowcnt+=1

		return myrowcnt

	def groupRecsByYear(self, arrs, pedIndex):
		s2List,t3List,f4List = [],[],[]
		for item in arrs:
			if item[pedIndex][0]=='2':
				s2List.append(item)
			if item[pedIndex][0]=='3':
				t3List.append(item)
			if item[pedIndex][0]=='4':
				f4List.append(item)

		return [s2List,t3List,f4List]

	def readMAE(self, filename):
		train = filename.split('/')[-5]
		test, factor, regression = filename.split('/')[-1].split('.')[0].split('_')
		r = csv.reader(open(filename), delimiter=',')
		r.next()
		ret = []
		MAEStart = False
		for row in r:
			if (len(row) == 0) and (MAEStart):
				MAEStart = False
				break

			if len(row) == 0:
				MAEStart = True

			if MAEStart:
				if len(row) > 0:
					print row
					ret.append(row[:20])

		header = ['TrainSet', 'TestSet', 'LQ', 'Factor'] + ret[0]
		maeList = []
		for x in ret[1:]:
			maeList.append([train, test, regression, factor]+x)

		return [header, maeList]

	def readPrecision(self, filename):
		r = csv.reader(open(filename), delimiter=',')
		header = r.next()
		ret = []
		for row in r:
			if len(row) == 0:
				break

			if len(row) > 0:
				ret.append(row)

		return [header, ret]

	def getTestFactorRegFromFileName(self, keyword, src):
		for x in src:
			test, factor, regression = x.split('/')[-1].split('.')[0].split('_')
			if keyword == test:
				return x

		return ''

	def computeSpecific(self):
		self.statsPath()
		self.prepare()
		self.f1s2YrTechYrCoursesMean(self.CRS_STU, self.STU_CRS)
		self.predictorsScatterPlots()
		self.predicting4Specific()
		# plot yr vs yr scatter plots
		# self.gradePointsDistribution(self.top1FactorsFile)
		self.mergePrecision4ALL('SINGLE_MEAN', self.linearPredictResultsListTop1+self.quadrPredictResultsListTop1+[self.meanPrecisionL, self.meanPrecisionQ], '')

		if self.errMerge:
			self.errLinearQuadraticStatsMerger(self.linearQuadraticTop1Stats, self.linearPredictResultsListTop1, self.quadrPredictResultsListTop1)

	def sortResultFiles(self, resultLists):
		trainDict = {}
		for fname in resultLists:
			key = fname.split('/')[-5]
			if key not in trainDict:
				trainDict[key] = [fname]
			else:
				trainDict[key].append(fname)

		return trainDict

	def mergeACC_MAE_4PedALL(self, resultLists):
		precisionXlsx = self.timeDir+'Ped_ACC.xlsx'
		workbook = xlsxwriter.Workbook(precisionXlsx)
		myformat = workbook.add_format({'align':'center_across'})

		allList, head, pindex = [], '', -1
		ALL_MAE_Recs, maeHead = [], ''
		for key, sublist in self.sortResultFiles(resultLists).items():
			dataset, recList, rowcnt = '', [], 0
			for fname in sublist:
				# read acc
				head, accRec = self.readPrecision(fname)
				recList += accRec
				# read MAEs
				maeHead, maeRec = self.readMAE(fname)
				ALL_MAE_Recs += maeRec

				print fname

			dataset = recList[0][0]
			print dataset

			recList.sort(key=itemgetter(7,6,0,1,3,5), reverse=False)
			allList += myCopy.deepcopy(recList)

			worksheet = workbook.add_worksheet(dataset)
			pindex = head.index('0~1.0')+1
			ret = self.pickCourses(recList, pindex, head)
			for row in ret:
				worksheet.write_row(rowcnt,0,row,myformat)
				rowcnt+=1

		# reset rowcnt
		rowcnt = 0
		worksheet = workbook.add_worksheet('ALLPed')
		allList.sort(key=itemgetter(7,0,3,5), reverse=False)
		ret = self.sortALLPed(allList, pindex, head)
		for row in ret:
			worksheet.write_row(rowcnt,0,row,myformat)
			rowcnt+=1

		# analyze courses' precision
		keys, crsDict = [],{}
		for row in allList:
			# predicted course
			key = row[6]+row[7]
			if key not in crsDict:
				keys.append(key)
				crsDict[key]=[row]
			else:
				crsDict[key].append(row)

		for key in keys:
			# reset rowcnt
			worksheet = workbook.add_worksheet(key)
			ret = self.analyzePrecision4OneCourse(crsDict[key], head)
			rowcnt = 0
			for row in ret:
				worksheet.write_row(rowcnt,0,row,myformat)
				rowcnt+=1

		# write Ped_MAE
		MAEXlsx = self.timeDir+'Ped_MAE.xlsx'
		MAE_workbook = xlsxwriter.Workbook(MAEXlsx)
		MAE_myformat = MAE_workbook.add_format({'align':'center_across'})

		worksheet = MAE_workbook.add_worksheet('ALLMAEs')
		ALL_MAE_Recs.sort(key=itemgetter(7,6,3,2,1), reverse=False)
		self.writeSheet([maeHead]+ALL_MAE_Recs, worksheet, MAE_myformat, 0)

		# write course sheet for MAE_workbook
		keys, MAEDict = self.format_ALL_MAEs(ALL_MAE_Recs)
		for key in keys:
			print 'Write ALL_MAEs for:\t', key
			predictedCrs_ALL_MAE_List = MAEDict[key]
			predictedCrs_ALL_MAE_List.sort(key=itemgetter(7,6,3,2,1), reverse=False)
			ret = self.format_Ped_MAEs(predictedCrs_ALL_MAE_List, maeHead)
			worksheet = MAE_workbook.add_worksheet(key)
			self.writeSheet(ret, worksheet, MAE_myformat, 0)

	def format_Ped_MAEs(self, predictedCrs_ALL_MAE_List, maeHead):
		ret = []
		pLList, rLList, prLList = [], [], []
		pQList, rQList, prQList = [], [], []
		for row in predictedCrs_ALL_MAE_List:
			if row[3] == 'P':
				if row[2] == 'L':
					pLList.append(row)
				elif row[2] == 'Q':
					pQList.append(row)
			elif row[3] == 'R':
				if row[2] == 'L':
					rLList.append(row)
				elif row[2] == 'Q':
					rQList.append(row)
			elif row[3] == 'PR':
				if row[2] == 'L':
					prLList.append(row)
				elif row[2] == 'Q':
					prQList.append(row)

		ret += self.Ped_MAEs_Spliter(pLList, maeHead)
		ret += self.Ped_MAEs_Spliter(pQList, maeHead)
		ret += self.Ped_MAEs_Spliter(rLList, maeHead)
		ret += self.Ped_MAEs_Spliter(rQList, maeHead)
		ret += self.Ped_MAEs_Spliter(prLList, maeHead)
		ret += self.Ped_MAEs_Spliter(prQList, maeHead)

		return ret

	def Ped_MAEs_Spliter(self, myList, maeHead):
		ret = []
		keyList, mydict = [], {}
		for row in myList:
			# key: test set
			key = row[1]
			if key not in mydict:
				mydict[key]=[row]
			else:
				mydict[key].append(row)

			if key not in keyList:
				keyList.append(key)

		tmp = [maeHead]
		for key in keyList:
			if len(mydict[key]) > 1:
				ret += [maeHead] + mydict[key] + ['']
			else:
				tmp += mydict[key]

		return (ret + tmp + ['',''])

	def format_ALL_MAEs(self, ALL_MAE_Recs):
		# sort by: yNum,ySubj,Factor,LQ,TestSet
		ALL_MAE_Recs.sort(key=itemgetter(7,6,3,2,1), reverse=False)
		# 2nd Year List, 3rd Year List, 4th Year List
		s2ListCrsList,t3ListCrsList,f4ListCrsList = [], [], []
		predictedCrsDict = {}
		for row in ALL_MAE_Recs:
			# key: predicted course
			key = row[6]+row[7]
			if key not in predictedCrsDict:
				predictedCrsDict[key]=[row]
			else:
				predictedCrsDict[key].append(row)

			if (row[7][0]=='2') and (key not in s2ListCrsList):
				s2ListCrsList.append(key)
			elif (row[7][0]=='3') and (key not in t3ListCrsList):
				t3ListCrsList.append(key)
			elif (row[7][0]=='4') and (key not in f4ListCrsList):
				f4ListCrsList.append(key)

		return [s2ListCrsList+t3ListCrsList+f4ListCrsList, predictedCrsDict]

	def analyzePrecision4OneCourse(self, crsList, head):
		pointIndex,rIndex,PxyIndex,insIndex,accIndex=head.index('point#'),head.index('r'),head.index('Pxy'),head.index('instance'),head.index('0~1.0')+1
		sameTrDict, sameTrKeys = {}, []
		for x in crsList:
			# training set
			sameTrKey = x[0]
			if sameTrKey not in sameTrDict:
				sameTrKeys.append(sameTrKey)
				sameTrDict[sameTrKey] = [x]
			else:
				sameTrDict[sameTrKey].append(x)

		ret1, ret2 = [], []
		for key in sameTrKeys:
			# records from the same training set; key: training set
			sameTrRecs, lList, qList = sameTrDict[key], [], []
			for x in sameTrRecs:
				if x[2] == 'L':
					lList.append(x)
				elif x[2] == 'Q':
					qList.append(x)

			# same Tr, same Test
			# sameTrRecs.sort(key=itemgetter(2,1), reverse=False)
			lList.sort(key=itemgetter(2,1), reverse=False), qList.sort(key=itemgetter(2,1), reverse=False)
			ret1 += self.sameTrSameT(key, lList, 'L', [pointIndex,rIndex,PxyIndex,insIndex,accIndex])+[['']]
			ret1 += self.sameTrSameT(key, qList, 'Q', [pointIndex,rIndex,PxyIndex,insIndex,accIndex])+[['']]

			# same Tr, diff Test
			# sameTrRecs.sort(key=itemgetter(3,2), reverse=False)
			lList.sort(key=itemgetter(3,2), reverse=False), qList.sort(key=itemgetter(3,2), reverse=False)
			ret2 += self.sameTrDiffT(key, lList, 'L', [pointIndex,rIndex,PxyIndex,insIndex,accIndex])+[['']]
			ret2 += self.sameTrDiffT(key, qList, 'Q', [pointIndex,rIndex,PxyIndex,insIndex,accIndex])+[['']]

		return myCopy.deepcopy([['STrST']]+ret1+[[''],[''],[''],[''],['STrDT']]+ret2)

	def sameTrDiffT(self, train, mylist, lq, indexList):
		PList,PRList,RList = [],[],[]
		headerPR,headerP,headerR = ['CRS', 'Tr', 'Type'],['CRS', 'Tr', 'Type'],['CRS', 'Tr', 'Type']
		for x in mylist:
			test = x[1].split('_')[0]
			if len(test) == 0:
				test = 'ALL'

			if x[3] == 'P':
				if test not in headerP:
					headerP.append(test)
				PList.append(x)
			elif x[3] == 'PR':
				if test not in headerPR:
					headerPR.append(test)
				PRList.append(x)
			elif x[3] == 'R':
				if test not in headerR:
					headerR.append(test)
				RList.append(x)

		ret1 = self.sameTrDiffTFormation(train, headerP, PList, 'P', lq, indexList)
		ret2 = self.sameTrDiffTFormation(train, headerPR, PRList, 'PR', lq, indexList)
		ret3 = self.sameTrDiffTFormation(train, headerR, RList, 'R', lq, indexList)

		return myCopy.deepcopy(ret2+ret1+ret3)

	def sameTrDiffTFormation(self, train, header, mylist, factor, lq, indexList):
		pointIndex, rIndex, PxyIndex, insIndex, accIndex = indexList
		crs = mylist[0][6]+mylist[0][7]
		Point, R, Pxy, ins, acc = [crs,train,factor+lq+'P'], [crs,train,factor+lq+'R'], [crs,train,factor+lq+'Pxy'], [crs,train,factor+lq+'ins'], [crs,train,factor+lq+'acc']

		pl,rl,pxyl,il,al=[],[],[],[],[]
		for x in xrange(0,len(header)-3):
			for y in [pl,rl,pxyl,il,al]:
				y.append(0)

		for x in mylist:
			test = x[1].split('_')[0]
			if len(test) == 0:
				test = 'ALL'

			index = header.index(test)-3
			pl[index], rl[index], pxyl[index], il[index], al[index] = x[pointIndex], x[rIndex], x[PxyIndex], x[insIndex], x[accIndex]

			# Point.append(x[pointIndex]),R.append(x[rIndex]),Pxy.append(x[PxyIndex]),ins.append(x[insIndex]),acc.append(x[accIndex])
		print '\nsameTrDiffTFormation:'
		print 'pl: ',pl,'\n','rl: ',rl,'\n','pxyl: ',pxyl,'\n','il: ',il,'\n','al: ',al,'\n',

		return myCopy.deepcopy([header, acc+al, Point+pl, R+rl, Pxy+pxyl, ins+il])

	def sameTrSameT(self, train, mylist, lq, indexList):
		pointIndex,rIndex,PxyIndex,insIndex,accIndex = indexList
		crs, yr = mylist[0][6]+mylist[0][7], mylist[0][7][0]

		PRQ_Point,PQ_Point,RQ_Point = [crs, train,'PR'+lq+'P'], [crs, train,'P'+lq+'P'], [crs, train,'R'+lq+'P']
		PRQ_R,PQ_R,RQ_R = [crs, train,'PR'+lq+'R'], [crs, train,'P'+lq+'R'], [crs, train,'R'+lq+'R']
		PRQ_Pxy,PQ_Pxy,RQ_Pxy = [crs, train,'PR'+lq+'Pxy'], [crs, train,'P'+lq+'Pxy'], [crs, train,'R'+lq+'Pxy']
		PRQ_ins,PQ_ins,RQ_ins = [crs, train,'PR'+lq+'ins'], [crs, train,'P'+lq+'ins'], [crs, train,'R'+lq+'ins']
		PRQ_acc,PQ_acc,RQ_acc = [crs, train,'PR'+lq+'acc'], [crs, train,'P'+lq+'acc'], [crs, train,'R'+lq+'acc']

		p_pl,p_rl,p_pxyl,p_il,p_al, pr_pl,pr_rl,pr_pxyl,pr_il,pr_al, r_pl,r_rl,r_pxyl,r_il,r_al = [],[],[],[],[],[],[],[],[],[],[],[],[],[],[]

		header = ['CRS', 'Tr', 'Type']
		for x in mylist:
			test = x[1].split('_')[0]
			if len(test) == 0:
				test = 'ALL'
			if test not in header:
				header.append(test)

		# inital lists
		for x in xrange(0,len(header)-3):
			for y in [p_pl,p_rl,p_pxyl,p_il,p_al,pr_pl,pr_rl,pr_pxyl,pr_il,pr_al,r_pl,r_rl,r_pxyl,r_il,r_al]:
				y.append(0)

		for x in mylist:
			test = x[1].split('_')[0]
			if len(test) == 0:
				test = 'ALL'

			index = header.index(test)-3
			if x[3] == 'P':
				# PQ_Point.append(x[pointIndex]),PQ_R.append(x[rIndex]),PQ_Pxy.append(x[PxyIndex]),PQ_ins.append(x[insIndex]),PQ_acc.append(x[accIndex])
				p_pl[index], p_rl[index], p_pxyl[index], p_il[index], p_al[index]=int(x[pointIndex]), float(x[rIndex]), float(x[PxyIndex]), int(x[insIndex]), float(x[accIndex])
			if x[3] == 'PR':
				# PRQ_Point.append(x[pointIndex]),PRQ_R.append(x[rIndex]),PRQ_Pxy.append(x[PxyIndex]),PRQ_ins.append(x[insIndex]),PRQ_acc.append(x[accIndex])
				pr_pl[index], pr_rl[index], pr_pxyl[index], pr_il[index], pr_al[index] =int(x[pointIndex]), float(x[rIndex]), float(x[PxyIndex]), int(x[insIndex]), float(x[accIndex])
			if x[3] == 'R':
				# RQ_Point.append(x[pointIndex]),RQ_R.append(x[rIndex]),RQ_Pxy.append(x[PxyIndex]),RQ_ins.append(x[insIndex]),RQ_acc.append(x[accIndex])
				r_pl[index], r_rl[index], r_pxyl[index], r_il[index], r_al[index]=int(x[pointIndex]), float(x[rIndex]), float(x[PxyIndex]), int(x[insIndex]), float(x[accIndex])

		print 'sameTrSameT: P --> \npoint: ',p_pl,'\nr: ',p_rl,'\npxy: ',p_pxyl,'\nins: ',p_il,'\nacc: ',p_al
		print 'sameTrSameT: PR --> \nppoint: ',pr_pl,'\nr: ',pr_rl,'\npxy: ',pr_pxyl,'\nins: ',pr_il,'\nacc: ',pr_al
		print 'sameTrSameT: R --> \npoint: ',r_pl,'\nr: ',r_rl,'\npxy: ',r_pxyl,'\nins: ',r_il,'\nacc: ',r_al

		self.plotSameTrSameT(train, lq, 'Accuracy', header[3:], ['P', 'Pxy', 'r'], [p_al, pr_al, r_al], crs, yr, 'acc')
		self.plotSameTrSameT(train, lq, 'Points', header[3:], ['P', 'Pxy', 'r'], [p_pl, pr_pl, r_pl], crs, yr, 'points')
		self.plotSameTrSameT(train, lq, 'Coefficients', header[3:], ['P', 'Pxy', 'r'], [p_rl, pr_rl, r_rl], crs, yr, 'coe')
		self.plotSameTrSameT(train, lq, 'Pxy', header[3:], ['P', 'Pxy', 'r'], [p_pxyl, pr_pxyl, r_pxyl], crs, yr, 'Pxy')
		self.plotSameTrSameT(train, lq, 'Test Instances', header[3:], ['P', 'Pxy', 'r'], [p_il, pr_il, r_il], crs, yr, 'ins')

		return myCopy.deepcopy([header, PRQ_acc+pr_al, PQ_acc+p_al, RQ_acc+r_al, header, PRQ_Point+pr_pl, PQ_Point+p_pl, RQ_Point+r_pl, header, PRQ_R+pr_rl, PQ_R+p_rl, RQ_R+r_rl, header, PRQ_Pxy+pr_pxyl, PQ_Pxy+p_pxyl, RQ_Pxy+r_pxyl, header, PRQ_ins+pr_il, PQ_ins+p_il, RQ_ins+r_il])

	def plotSameTrSameT(self, Tr, lq, fType, xticks, legend, mylist, ped, yr, subfolder):
		fig = plt.figure()
		xlist = xrange(1, len(mylist[0])+1)

		index, mycolor, shapes= 0, ['red', 'blue', 'cyan'], ['o', '*', '^']
		for x in mylist:
			plt.plot(xlist, x, shapes[index], c=mycolor[index], label=legend[index])
			index+=1

		ylist = []
		for x in mylist:
			ylist += x
		ymax, xmax = ceil(max(ylist)), len(mylist[0])+1
		plt.axis([0, xmax, 0, ymax])

		plt.xticks(xlist, xticks, rotation='10')
		plt.xlabel('Test Sets')
		plt.ylabel(fType)
		plt.title(ped+': Tr:'+Tr+', '+lq+', '+fType+' Comparison')
		plt.grid(True)

		ax = plt.subplot(111)
		# Shrink current axis's height by 10% on the bottom
		box = ax.get_position()
		ax.set_position([box.x0, box.y0+box.height*0.1, box.width, box.height*0.9])
		# Put a legend below current axis
		ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.13), fancybox=True, shadow=True, ncol=3, markerfirst=False, numpoints=3)

		# expand figure bottom space
		plt.gcf().subplots_adjust(bottom=0.19)

		figDir = self.timeDir+'CRS_Com_Figures/'+yr+'/'+ped+'/'+subfolder+'/'+lq+'/'
		if not os.path.exists(figDir):
			os.makedirs(figDir)

		filename = figDir+ped+'_'+Tr+'_'+lq+'_'+fType+'.png'

		# plt.show()
		fig.savefig(filename)
		plt.close(fig)

	def sortALLPed(self, mylist, pindex, head):
		keys, crsDict = [],{}
		TiedL, SmallerL, BiggerL = [],[],[]
		ret, diffList = [],[]
		for row in mylist:
			key = row[7]+row[6]
			if key not in crsDict:
				keys.append(key)
				crsDict[key]=[row]
			else:
				crsDict[key].append(row)

		for key in keys:
			crsList = crsDict[key]
			crsList.sort(key=itemgetter(2,1), reverse=False)
			ret += [head]+crsList+[['']]
			# Tied, Smaller, Bigger, crs, num = 0, 0, 0, crsList[0][5], crsList[0][6]

		return ret

	def pickCourses(self, mylist, pindex, head):
		keys, crsDict = [],{}
		TiedL, SmallerL, BiggerL = [],[],[]
		ret, diffList = [],[]
		for row in mylist:
			key = row[7]+row[6]
			if key not in crsDict:
				keys.append(key)
				crsDict[key]=[row]
			else:
				crsDict[key].append(row)

		d2 = ['subj', 'num', 'Tied', 'Smaller', 'Bigger', 'Total']
		for key in keys:
			crsList = crsDict[key]
			crsList.sort(key=itemgetter(7,6,0,1,3,5), reverse=False)
			Tied, Smaller, Bigger, crs, num = 0, 0, 0, crsList[0][6], crsList[0][7]
			for i in xrange(0,len(crsList)-1,2):
				diff = float(crsList[i][pindex])-float(crsList[i+1][pindex])
				if diff > 0:
					crsList[i+1]+=['-']
					Smaller += 1
				elif diff < 0:
					crsList[i+1]+=['+']
					Bigger += 1
				elif diff == 0:
					crsList[i+1]+=['#']
					Tied += 1

			tsum = Tied+Smaller+Bigger
			d1 = [crs, num, Tied, Smaller, Bigger, tsum, format(float(Tied*1.0/tsum), '.3f'), format(float(Smaller*1.0/tsum),'.3f'), format(float(Bigger*1.0/tsum), '.3f')]

			ret += [head]+myCopy.deepcopy(crsList)+[[''],d2,d1,['']]
			diffList += [d1]

		return ret+[d2]+diffList

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

	def removeDup(self, crses):
		result = ''
		for crs in crses:
			# the grade_point_value is not empty
			if len(crs[8]) > 0:
				# the variable result has already been assigned a course record
				if len(result) > 0:
					# the duplicate record has a smaller grade point value
					if int(result[8]) > int(crs[8]):
						result = crs
				else:
					result = crs

		return result

	def formatRegSAS(self, regfile, noDupRegFile):
		r, w = csv.reader(open(regfile), delimiter=','), csv.writer(open(noDupRegFile, 'w'))
		header = r.next()
		w.writerow(header)

		# user-courseList dictionary: VNUM as key, course as value; group the course data by their VNUM
		VCDict = {}
		for row in r:
			course = row[3].replace(' ','')+row[4].replace(' ','')
			# change MATH 110 ===> MATH 133; ENGR 110 ===> ENGR 111
			if course == 'MATH110':
				row[4] = '133'

			if course == 'ENGR110':
				row[4] = '111'

			# key: the v_number
			row[3], key=row[3].replace(' ',''), row[1].replace(' ','')
			if key not in VCDict:
				VCDict[key]=[row]
			else:
				VCDict[key].append(row)

		# iterate each student
		for vkey in VCDict:
			# VCDict[vkey]: one student's all possible courses including the records with same subj+num but different grades; vkey: student's vnumber
			# crs-same-crs-duplicate-record-List dictionary: subject_code+course_number as key, duplicate records as value; group one student's courses by course code(subj+num)
			CRSDict = {}
			for crs in VCDict[vkey]:
				ckey = crs[3]+crs[4]
				if ckey not in CRSDict:
					CRSDict[ckey] = [crs]
				else:
					CRSDict[ckey].append(crs)

			for ckey in CRSDict:
				result = self.removeDup(CRSDict[ckey])
				if len(result) > 0:
					w.writerow(result)
  
	def simpleStats(self, noDupRegFile, CRSPERSTU, STUREGISTERED, CRS_STU, CRS_STU_GRADE, STU_CRS, STU_CRS_GRADE):
		# CRSPERSTU: courses' frequency for each student
		# STUREGISTERED: students' frequency for each course
		# CRS_STU: course grade point matrix with row of course and column of student
		# CRS_STU_GRADE: course grade matrix with row of course and column of student
		# STU_CRS: course grade point matrix with row of student and column of course
		# STU_CRS_GRADE: course grade matrix with row of student and column of course
		r = csv.reader(open(noDupRegFile), delimiter=',')
		r.next()

		vnumDict, courseDict = {}, {}
		for row in r:
			# [vnum, subj, num, grade, point]
			course = [row[1], row[3], row[4], row[6], row[8]]
			# form vnumDict; key: vnum
			if row[1] not in vnumDict:
				vnumDict[row[1]]=[course]
			else:
				vnumDict[row[1]].append(course)
			# form courseDict; key: subj+' '+cnum
			key = row[3]+' '+row[4]
			if key not in courseDict:
				courseDict[key] = [course]
			else:
				courseDict[key].append(course)

		# create CRSPERSTU
		w = csv.writer(open(CRSPERSTU, 'w'))
		w.writerow(['VNUM', '#courses'])
		w.writerows([ [key, len(vnumDict[key])] for key in vnumDict ])

		# create STUREGISTERED
		w = csv.writer(open(STUREGISTERED, 'w'))
		# w.writerow(['Course', '#Students'])
		w.writerow(['subj', 'num', '#Stu', 'year'])
		w.writerows([ [key.split(' ')[0], key.split(' ')[1], len(courseDict[key]), key.split(' ')[1][0]] for key in courseDict ])

		# create CRS_STU, CRS_STU_GRADE
		w1, w2 = csv.writer(open(CRS_STU, 'w')), csv.writer(open(CRS_STU_GRADE, 'w'))
		vnumList = vnumDict.keys()
		w1.writerow(['subj', 'cnum']+vnumList)
		w2.writerow(['subj', 'cnum']+vnumList)
		for course in courseDict:
			CRS_STU_row, CRS_STU_GRADE_row, courses = course.split(' '), course.split(' '), courseDict[course]
			# insert blank value for every vnum
			[CRS_STU_row.append('') for vnum in vnumList]
			[CRS_STU_GRADE_row.append('') for vnum in vnumList]
			# row: [vnum, subj, num, grade, point]
			for row in courses:
				vnum, grade, point = row[0], row[3], row[4]
				index = vnumList.index(vnum)
				CRS_STU_row[index+2], CRS_STU_GRADE_row[index+2] = point, grade

			w1.writerow(CRS_STU_row)
			w2.writerow(CRS_STU_GRADE_row)

		# create STU_CRS, STU_CRS_GRADE
		w1, w2 = csv.writer(open(STU_CRS, 'w')), csv.writer(open(STU_CRS_GRADE, 'w'))
		crsList = [crs.replace(' ', '') for crs in courseDict.keys()]
		w1.writerow(['vnum']+crsList)
		w2.writerow(['vnum']+crsList)
		for vnum in vnumDict:
			STU_CRS_row, STU_CRS_GRADE_row, courses = [vnum], [vnum], vnumDict[vnum]
			[STU_CRS_row.append('') for crs in crsList]
			[STU_CRS_GRADE_row.append('') for crs in crsList]
			for course in courses:
				# course: [vnum, subj, num, grade, point]
				grade, point, crs = course[3], course[4], course[1]+course[2]
				index = crsList.index(crs)
				STU_CRS_row[index+1], STU_CRS_GRADE_row[index+1] = point, grade

			w1.writerow(STU_CRS_row)
			w2.writerow(STU_CRS_GRADE_row)

	def createCrspairs(self, CRS_PAIRS, CRS_STU):
		r, w = csv.reader(open(CRS_STU), delimiter=','), csv.writer(open(CRS_PAIRS, 'w'))
		r.next()
		f1list,s2list,t3list,f4list = [],[],[],[]
		for row in r:
			if row[1][0]=='1':
				f1list.append(row)
			elif row[1][0]=='2':
				s2list.append(row)
			elif row[1][0]=='3':
				t3list.append(row)
			elif row[1][0]=='4':
				f4list.append(row)

		results = [self.matchPair(f1list, s2list), self.matchPair(f1list, t3list), self.matchPair(f1list, f4list), self.matchPair(s2list, t3list), self.matchPair(s2list, f4list)]
		for result in results:
			if len(result) > 0:
				w.writerows(result)

	def matchPair(self, earlyList, laterList):
		result = []
		for itemL in laterList:
			for itemE in earlyList:
				L, E = [itemL[0], itemL[1]], [itemE[0], itemE[1]]
				for x in xrange(2,len(itemL)):
					if (len(itemL[x]) > 0) and (len(itemE[x]) > 0):
						L.append(int(itemL[x])), E.append(int(itemE[x]))

				if len(L) > 2:
					result += [E,L,[]]
					# self.createBoxPlots(E, L)

		return result

	def createBoxPlots(self, edata, ldata):
		# early course, late course
		ecourse, lcourse = edata[0]+' '+edata[1], ldata[0]+' '+ldata[1]
		figname = self.boxplots+lcourse+'/'+ecourse+ ' ' +lcourse+'.png'
		# already exists, return it and do not re-create it
		if os.path.exists(figname):
			return
		elif not os.path.exists(self.boxplots+lcourse):
			os.makedirs(self.boxplots+lcourse)

		fig = plt.figure()
		# fig = plt.figure(1, figsize=(4, 6))
		ax = plt.axes()
		plt.ylim(0.0, 9.0)
		bp = ax.boxplot([edata[2:], ldata[2:]])
		ax.set_xticklabels([ecourse, lcourse])

		minorLocator, majorLocator = MultipleLocator(0.1), MultipleLocator(0.5)
		ax.yaxis.set_minor_locator(minorLocator), ax.yaxis.set_major_locator(majorLocator)
		plt.grid(True)
		# plt.show()

		fig.savefig(figname, bbox_inches='tight')
		plt.close(fig)

	def techCoursePicker(self, regfile, techcourses):
		r, w = csv.reader(open(regfile), delimiter = ','), csv.writer(open(techcourses, 'w'))
		header = r.next()
		w.writerow(header)

		for row in r:
			course = row[3].replace(' ','')+row[4].replace(' ','')
			# change MATH 110 ===> MATH 133; ENGR 110 ===> ENGR 111
			if course == 'MATH110':
				row[4] = '133'

			if course == 'ENGR110':
				row[4] = '111'

			crs = row[3].replace(' ','')+row[4].replace(' ','')
			if crs in self.techList:
				w.writerow(row)

	def f1s2YrTechYrCoursesMean(self, CRS_STU, STU_CRS):
		# compute the 1st year tech courses vs 2nd/3rd/4th yr tech courses' average
		# plot the 1st yr vs mean graphs
		r1, r2 = csv.reader(open(CRS_STU), delimiter = ','), csv.reader(open(STU_CRS), delimiter = ',')
		vnumList, crsList = r1.next()[2:], r2.next()[1:]

		f1CrsList, s2CrsList, t3CrsList, f4CrsList = [], [], [], []
		# crsVnumDict: key:1st year course name (subj+cnum); value:vnums who took this 1st year tech course
		crsVnumDict = {}
		# form crsDict: key:subj+cnum; value:course record for all student graduated from 2010 to 2015
		w = csv.writer(open(self.f1s2CrsVnums, 'w'))

		crsDict = {}
		for row in r1:
			yr, key = row[1][0], row[0]+row[1]
			crsDict[key], vnums = row, []

			if yr == '1':
				f1CrsList.append(key)
				# for each 1st year technical course, to find all students who took this 1st year course
				for x in xrange(2,len(row)):
					if len(row[x]) > 0:
						vnums.append(vnumList[x-2])
			if yr == '2':
				s2CrsList.append(key)
				# for each 2nd year technical course, to find all students who took this 2nd year course
				for x in xrange(2,len(row)):
					if len(row[x]) > 0:
						vnums.append(vnumList[x-2])
			if yr == '3':
				t3CrsList.append(key)
			if yr == '4':
				f4CrsList.append(key)

			if len(vnums) > 0:
				# crs: the key, subj+cnum; vnums:all vnums who took course crs
				crsVnumDict[key] = vnums
				w.writerow([key]+vnums)

		# form vnumDict: key:vnum; value: one student's courses' record for all possible technical courses
		# calculate the average of 2nd/3rd/4th yr courses for each vnum
		w = csv.writer(open(self.vnumMeans, 'w'))
		w.writerow(['VNUM', 'MEAN1', 'MEAN2', 'MEAN3', 'MEAN4'])
		vnumMeanDict = {}
		for row in r2:
			# vnumDict[row[0]] = row
			f1Points, s2Points, t3Points, f4Points = [], [], [], []
			for x in xrange(1,len(row)):
				crs = crsList[x-1]
				if (crs in f1CrsList) and (len(row[x]) > 0):
					f1Points.append(int(row[x]))
				if (crs in s2CrsList) and (len(row[x]) > 0):
					s2Points.append(int(row[x]))
				if (crs in t3CrsList) and (len(row[x]) > 0):
					t3Points.append(int(row[x]))
				if (crs in f4CrsList) and (len(row[x]) > 0):
					f4Points.append(int(row[x]))

			vnumMeanDict[row[0]] = [format(np.mean(f1Points), '.2f'), format(np.mean(s2Points), '.2f'), format(np.mean(t3Points), '.2f'), format(np.mean(f4Points), '.2f')]
			w.writerow([row[0], format(np.mean(f1Points), '.2f'), format(np.mean(s2Points), '.2f'), format(np.mean(t3Points), '.2f'), format(np.mean(f4Points), '.2f')])

		# create Pearson coefficient csv; meanPairs csv
		w1, w2 = csv.writer(open(self.meanPairs, 'w')), csv.writer(open(self.meanPearson, 'w'))
		w2.writerow(['F1S2CRS', 'YR', 'R', '#points', 'slope', 'intercept', 'a', 'b', 'c'])
		for crs in crsVnumDict:
			vnums, course, yr = crsVnumDict[crs], crsDict[crs], crsDict[crs][1][0]
			crsPoints, vnums2Means, vnumt3Means, vnumf4Means = [], [], [], []
			for vnum in vnums:
				index = vnumList.index(vnum)
				crsPoints.append(float(course[index+2]))
				vnums2Means.append(float(vnumMeanDict[vnum][1]))
				vnumt3Means.append(float(vnumMeanDict[vnum][2]))
				vnumf4Means.append(float(vnumMeanDict[vnum][3]))

			if yr == '1':
				self.f1PointLaterMeanScatter(crs+' Grade Points', '2nd Year Courses Mean', crs+' vs Mean of 2nd Year Courses Grade Points', crsPoints, vnums2Means, self.meanPlot+crs+' 2nd.png')

			self.f1PointLaterMeanScatter(crs+' Grade Points', '3rd Year Courses Mean', crs+' vs Mean of 3rd Year Courses Grade Points', crsPoints, vnumt3Means, self.meanPlot+crs+' 3rd.png')
			self.f1PointLaterMeanScatter(crs+' Grade Points', '4th Year Courses Mean', crs+' vs Mean of 4th Year Courses Grade Points', crsPoints, vnumf4Means, self.meanPlot+crs+' 4th.png')

			# compute Pearson correlation coefficients
			if yr == '1':
				slope, intercept, r_value, p_value, std_err = linregress(crsPoints, vnums2Means)
				a,b,c = np.polyfit(crsPoints, vnums2Means, 2)
				w2.writerow([crs, '2', format(r_value, '.4f'), len(crsPoints), format(slope, '.4f'), format(intercept, '.4f'), format(a, '.4f'), format(b, '.4f'), format(c, '.4f')])

			slope, intercept, r_value, p_value, std_err = linregress(crsPoints, vnumt3Means)
			a,b,c = np.polyfit(crsPoints, vnumt3Means, 2)
			w2.writerow([crs, '3', format(r_value, '.4f'), len(crsPoints), format(slope, '.4f'), format(intercept, '.4f'), format(a, '.4f'), format(b, '.4f'), format(c, '.4f')])

			slope, intercept, r_value, p_value, std_err = linregress(crsPoints, vnumf4Means)
			a,b,c = np.polyfit(crsPoints, vnumf4Means, 2)
			w2.writerow([crs, '4', format(r_value, '.4f'), len(crsPoints), format(slope, '.4f'), format(intercept, '.4f'), format(a, '.4f'), format(b, '.4f'), format(c, '.4f')])

			# write a Mean Pairs
			if yr == '1':
				w1.writerows([[crs]+crsPoints, ['2']+vnums2Means, ['3']+vnumt3Means, ['4']+vnumf4Means])
			else:
				w1.writerows([[crs]+crsPoints, ['3']+vnumt3Means, ['4']+vnumf4Means])
			w1.writerow([])

			print '\nGrade Points:', crs, '\n', crsPoints, '\nvnums2Means:\n', vnums2Means, '\nvnumt3Means:\n', vnumt3Means, '\nvnumf4Means:\n', vnumf4Means

	def f1s2YrTechYrCrsMeanPrediction(self, meanPairs, predictorsFile):
		r1, r2 = csv.reader(open(meanPairs), delimiter = ','), csv.reader(open(predictorsFile), delimiter = ',')
		r2.next()
		# self.meanPredictedLCSV, self.meanPredictedQCSV, self.meanPredictedELCSV, self.meanPredictedEQCSV
		pointMeansDict, tmpList = {}, []
		for row in r1:
			if len(row) > 0:
				tmpList.append(row)
			else:
				if len(tmpList) > 0:
					key = tmpList[0][0]
					pointMeansDict[key] = tmpList
					tmpList = []

		if len(tmpList) > 0:
			key = tmpList[0][0]
			pointMeansDict[key] = tmpList
			tmpList = []

		print '\npointMeansDict:\n', pointMeansDict
		# form predictors dictionary
		predictorsDict = {}
		for rec in r2:
			crs, yr = rec[0], rec[1]
			if crs not in predictorsDict:
				predictorsDict[crs] = [rec]
			else:
				predictorsDict[crs].append(rec)

		print '\npredictorsDict:\n', predictorsDict, '\n'

		# todo: prediction process
		w1, w2 = csv.writer(open(self.meanPredictedLCSV, 'w')), csv.writer(open(self.meanPredictedQCSV, 'w'))

		s2LmeanPrecisionList, t3LmeanPrecisionList, f4LmeanPrecisionList = [], [], []
		s2QmeanPrecisionList, t3QmeanPrecisionList, f4QmeanPrecisionList = [], [], []

		for crs in pointMeansDict:
			crsPoints, mean2, mean3, mean4, predictor2, predictor3, predictor4 = [], [], [], [], [], [], []
			if len(pointMeansDict[crs]) == 4:
				crsPoints, mean2, mean3, mean4 = pointMeansDict[crs]
				predictor2, predictor3, predictor4 = predictorsDict[crs]
			elif len(pointMeansDict[crs]) == 3:
				crsPoints, mean3, mean4 = pointMeansDict[crs]
				predictor3, predictor4 = predictorsDict[crs]

			if len(pointMeansDict[crs]) == 4:
				[points, means, lMeanList, qMeanList, lErrList, qErrList] = self.computeLQErr(crsPoints, mean2, predictor2)
				w1.writerows([points, means, ['2']+lMeanList, lErrList])
				w2.writerows([points, means, ['2']+qMeanList, qErrList])
				# collect predictors and the mean error to compute the precision for linear and quadratic
				s2LmeanPrecisionList.append([points[0], '2nd']+predictor2[2:4]+lErrList[1:])
				s2QmeanPrecisionList.append([points[0], '2nd']+predictor2[2:4]+qErrList[1:])

			[points, means, lMeanList, qMeanList, lErrList, qErrList] = self.computeLQErr(crsPoints, mean3, predictor3)
			w1.writerows([points, means, ['3']+lMeanList, lErrList])
			w2.writerows([points, means, ['3']+qMeanList, qErrList])
			# collect predictors and the mean error to compute the precision for linear and quadratic
			t3LmeanPrecisionList.append([points[0], '3rd']+predictor3[2:4]+lErrList[1:])
			t3QmeanPrecisionList.append([points[0], '3rd']+predictor3[2:4]+qErrList[1:])

			[points, means, lMeanList, qMeanList, lErrList, qErrList] = self.computeLQErr(crsPoints, mean4, predictor4)
			w1.writerows([points, means, ['4']+lMeanList, lErrList])
			w2.writerows([points, means, ['4']+qMeanList, qErrList])
			# collect predictors and the mean error to compute the precision for linear and quadratic
			f4LmeanPrecisionList.append([points[0], '4th']+predictor4[2:4]+lErrList[1:])
			f4QmeanPrecisionList.append([points[0], '4th']+predictor4[2:4]+qErrList[1:])

		# self.meanPrecisionL, self.meanPrecisionQ
		w1, w2 = csv.writer(open(self.meanPrecisionL, 'w')), csv.writer(open(self.meanPrecisionQ, 'w'))
		# compute the precision
		header = ['CRS','YR','r','P','instance','0~0.5','%','0.5~1.0','%','0~1.0','%','1.0~1.5','%','gt1.5','%']
		precisionsL = self.computePrecisionForMeanPrediction(s2LmeanPrecisionList+t3LmeanPrecisionList+f4LmeanPrecisionList)
		precisionsQ = self.computePrecisionForMeanPrediction(s2QmeanPrecisionList+t3QmeanPrecisionList+f4QmeanPrecisionList)

		for key, values in self.sortMeanPredictionByIndex(precisionsL, 1).items():
			values.sort(key=itemgetter(10), reverse=True)
			w1.writerows([header]+values+[''])

		for key, values in self.sortMeanPredictionByIndex(precisionsL, 0).items():
			values.sort(key=itemgetter(10), reverse=True)
			w1.writerows([header]+values+[''])

		for key, values in self.sortMeanPredictionByIndex(precisionsQ, 1).items():
			values.sort(key=itemgetter(10), reverse=True)
			w2.writerows([header]+values+[''])

		for key, values in self.sortMeanPredictionByIndex(precisionsQ, 0).items():
			values.sort(key=itemgetter(10), reverse=True)
			w2.writerows([header]+values+[''])

		header = ['CRS','YR','r','P']
		for key, values in self.sortMeanPredictionByIndex(s2LmeanPrecisionList+t3LmeanPrecisionList+f4LmeanPrecisionList, 1).items():
			w1.writerows([header]+values+[''])

		for key, values in self.sortMeanPredictionByIndex(s2LmeanPrecisionList+t3LmeanPrecisionList+f4LmeanPrecisionList, 0).items():
			w1.writerows([header]+values+[''])

		for key, values in self.sortMeanPredictionByIndex(s2QmeanPrecisionList+t3QmeanPrecisionList+f4QmeanPrecisionList, 1).items():
			w2.writerows([header]+values+[''])

		for key, values in self.sortMeanPredictionByIndex(s2QmeanPrecisionList+t3QmeanPrecisionList+f4QmeanPrecisionList, 0).items():
			w2.writerows([header]+values+[''])

		# w1.writerows([header]+s2LmeanPrecisionList+['']+[header]+t3LmeanPrecisionList+['']+[header]+f4LmeanPrecisionList)
		# w2.writerows([header]+s2QmeanPrecisionList+['']+[header]+t3QmeanPrecisionList+['']+[header]+f4QmeanPrecisionList)

	def computePrecisionForMeanPrediction(self, errRecList):
		# error range: '0~0.5','0.5~1.0','1.0~1.5','gt1.5'
		# header = ['CRS','YR','r','P','instance','0~0.5','%','0.5~1.0','%','0~1.0','%','1.0~1.5','%','gt1.5','%']		
		# by defaut, the precisionList is ordered by YR
		precisionList = []
		for errRec in errRecList:
			# instance = len(errRec[4:])
			rec, errorList = errRec[:4]+[len(errRec[4:])], errRec[4:]

			le_05 = be_05_10 = be_10_15 = gt15 = 0
			for err in errorList:
				if abs(float(err)) <= 0.5:
					le_05 += 1
				elif abs(float(err)) <= 1.0:
					be_05_10 += 1
				elif abs(float(err)) <= 1.5:
					be_10_15 += 1
				else:
					gt15 += 1

			instance = le_05+be_05_10+be_10_15+gt15
			rec += [le_05, float(format(le_05*100.0/instance, '.4')), be_05_10, float(format(be_05_10*100.0/instance, '.4')), le_05+be_05_10, float(format((le_05+be_05_10)*100.0/instance, '.4')), be_10_15, float(format(be_10_15*100.0/instance, '.4')), gt15, float(format(gt15*100.0/instance, '.4'))]
			precisionList.append(rec)

		return precisionList

	def sortMeanPredictionByIndex(self, dataList, sortIndex):
		dataListDict = {}
		for rec in dataList:
			if rec[sortIndex] not in dataListDict:
				dataListDict[rec[sortIndex]] = [rec]
			else:
				dataListDict[rec[sortIndex]].append(rec)

		return dataListDict

	def computeLQErr(self, crsPoints, means, predictor):
		# Linear: k*x+b; Quadratic:a*x^2+b*x+c
		slope, intercept, a, b, c = [float(item) for item in predictor[4:]]
		lErrList, qErrList, lMeanList, qMeanList = ['LE'], ['QE'], [], []
		for x in xrange(1,len(crsPoints)):
			mean = float(means[x])
			# Linear
			lpmean = slope*float(crsPoints[x])+intercept
			lMeanList.append(format(lpmean, '.2f'))
			lErrList.append(format(mean-lpmean, '.2f'))
			# Quadratic
			qpmean = a*pow(float(crsPoints[x]), 2)+b*float(crsPoints[x])+c
			qMeanList.append(format(qpmean, '.2f'))
			qErrList.append(format(mean-qpmean, '.2f'))

		return [crsPoints, means, lMeanList, qMeanList, lErrList, qErrList]

	def f1PointLaterMeanScatter(self, xtitle, ytitle, title, xdata, ydata, figName):
		if os.path.exists(figName):
			return

		fig = plt.figure()
		x = np.array(xdata)
		y = np.array(ydata)

		z = np.polyfit(x, y, 1)
		p = np.poly1d(z)
		plt.plot(x, y, 'o', c='red')
		plt.plot(x, p(x), 'b--')

		plt.xlabel(xtitle)
		plt.ylabel(ytitle)
		plt.title(title)

		plt.ylim(0.0, 9.0)
		plt.xlim(0.0, 9.0)

		ax = plt.axes()
		minorLocator = MultipleLocator(0.1)
		majorLocator = MultipleLocator(0.5)
		ax.yaxis.set_minor_locator(minorLocator)
		ax.yaxis.set_major_locator(majorLocator)

		ax.xaxis.set_minor_locator(minorLocator)
		ax.xaxis.set_major_locator(majorLocator)

		plt.grid(True)
		# plt.show()
		fig.savefig(figName)
		plt.close(fig)

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

	def corrPlot(self, source, corr, skewness):
		reader = csv.reader(open(source), delimiter=',')
		header = reader.next()

		matrix = []
		for row in reader:
			matrix.append(row)

		wskew = csv.writer(open(skewness, 'w'))
		skewHeader = ['subCode1', 'Num1', 'subCode2', 'Num2', 'skew1', 'skew2', 'coefficient','#points','pValue','stderr','slope','intercept','a','b','c','R^2','xmin','xmax']
		wskew.writerow(skewHeader)

		w = csv.writer(open(corr, 'w'))
		w.writerow(['xsubCode','xnum','ysubCode','ynum','coefficient','#points','pValue','stderr','slope','intercept','a','b','c','R^2','xmin','xmax'])
		wnan = csv.writer(open(self.nancsv, 'w'))

		cnt, nocorrDict, nocommstuDict = 0, {}, {}
		nocorrlst = self.dataDir+'nocorr/no_corr_list.csv'
		nocommstulst = self.dataDir+'nocomstu/nocomstu_list.csv'
		wnocorrlst, wnocommstulst, nocomList, noCorrListTable, corrList = '', '', [], [], []

		rpSinglelist = []
		for x in xrange(0,len(matrix)):
			# course is a row with all marks
			course = matrix[x]
			# the first character of the course number, which indicates which year the course is designed, e.g.:1,2,3,4
			yr = course[1][0]
			noCorrList, nocommstuList = [], []
			for y in xrange(0,len(matrix)):
				newCourse = matrix[y]
				newYr = newCourse[1][0]
				if (int(yr) < int(newYr)) and (int(yr) < 3):
					cnt += 1
					xaxis, yaxis = course[0]+' '+course[1]+' Grades', newCourse[0]+' '+newCourse[1]+' Grades'

					xdata, ydata = [], []
					if source == self.crsMatrix:
						xdata, ydata= map(float, course[3:]), map(float, newCourse[3:])
					else:
						for index in xrange(2, len(course)):
							ix, iy = course[index], newCourse[index]
							if ix.isdigit() and iy.isdigit():
								xdata.append(float(ix)), ydata.append(float(iy))

						if len(xdata) == 0:
							cnt += 1
							nocommstuList.append(newCourse), nocomList.append([course[0]+' '+course[1], newCourse[0]+' '+newCourse[1]])
							if self.proPredictor == 'ALL':
								print 'cnt:',cnt,'no common students course pair, len:',len(ydata),course[0],course[1],'vs',newCourse[0],newCourse[1],'trainYrs:',self.trainYrsText
							else:
								print 'cnt:',cnt,'no common students course pair, len:',len(ydata),course[0],course[1],'vs',newCourse[0],newCourse[1]
							continue

					# if len(xdata) < self.threshold:
					# 	cnt += 1
					# 	print 'cnt:',cnt,'less than threshold course pair,', 'len:', len(ydata), course[0],course[1],'vs',newCourse[0],newCourse[1],'trainYrs:', self.trainYrsText, 'Thresh:', self.threshold
					# 	continue

					# before computing the pearson correlation coefficient, normalize the dataset
					xl = [i*1.0/sum(xdata) for i in xdata]
					yl = [i*1.0/sum(ydata) for i in ydata]

					(r, p) = pearsonr(xl, yl)
					p = float(format(p, '.4f'))
					if str(r) == 'nan':
						noCorrList.append(newCourse)
						cnt += 1
						if self.proPredictor == 'ALL':
							print 'cnt:',cnt,'no Pearson r course pair,', 'len:', len(ydata), course[0],course[1],'vs',newCourse[0],newCourse[1],'trainYrs:', self.trainYrsText
						else:
							print 'cnt:',cnt,'no Pearson r course pair,', 'len:', len(ydata), course[0],course[1],'vs',newCourse[0],newCourse[1]
						wnan.writerows([[course[0]+course[1],newCourse[0]+newCourse[1],'len:',len(ydata)]]+[[course[0]+course[1]]+xdata]+[[newCourse[0]+newCourse[1]]+ydata]+[])
						continue

					self.createBoxPlots([course[0], course[1]]+xdata, [newCourse[0], newCourse[1]]+ydata)
					# slope, intercept, r_value, p_value, std_err = linregress(xdata, ydata)
					# format the parameters precision
					slope, intercept, r_value, p_value, std_err = linregress(xl, yl)
					r, slope, intercept, r_value, p_value, std_err = [float(format(r, '.4f')), float(format(slope, '.4f')), float(format(intercept, '.4f')), float(format(r_value, '.4f')), float(format(p_value, '.4f')), float(format(std_err, '.4f'))]

					# r_value = float(format(r, '.4f'))
					slope, intercept = self.regressionPlot(xdata, ydata, r, 1, xaxis, yaxis, self.linear_plots_ori, len(ydata))
					a,b,c = self.regressionPlot(xdata, ydata, r, 2, xaxis, yaxis, self.quadratic_plots_ori, len(ydata))

					slope, intercept, a, b, c = [float(format(slope, '.4f')), float(format(intercept, '.4f')), float(format(a, '.4f')), float(format(b, '.4f')), float(format(c, '.4f'))]

					# if self.proPredictor == 'ALL':
					corrList.append([course[0],course[1],newCourse[0],newCourse[1],r,len(ydata),p_value,std_err,slope,intercept,a,b,c,float(format(r*r, '.4f')),min(xdata),max(xdata)])
					# else:
						# corrList.append([course[0], course[1], newCourse[0], newCourse[1], r, len(ydata), 0, p_value, std_err, slope, intercept, a, b, c, r*r, min(xdata), max(xdata)])

					rpSinglelist.append([course[0], course[1], newCourse[0], newCourse[1], r, len(ydata)])

					if self.proPredictor == 'ALL':
						print 'cnt:', cnt, course[0], course[1], 'vs', newCourse[0], newCourse[1], 'len:', len(ydata), 'r:', r, 'r_value:', r_value, 'p_value:', p_value, 'p:', p, 'slope:', slope, 'trainYrs:', self.trainYrsText
					else:
						print 'cnt:', cnt, course[0], course[1], 'vs', newCourse[0], newCourse[1], 'len:', len(ydata), 'r:', r, 'r_value:', r_value, 'p_value:', p_value, 'p:', p, 'slope:', slope

					# write skew to csv
					xskew, yskew  = float(format(skew(xdata, None, False), '.4f')), float(format(skew(ydata, None, False), '.4f'))
					wskew.writerow([course[0], course[1], newCourse[0], newCourse[1], xskew, yskew, r, len(ydata), p_value, std_err, slope, intercept, a, b, c, float(format(r*r, '.4f')), min(xdata), max(xdata)])

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
				wnocorrlst.writerows(noCorrList+[])
				
				# wnocorrlst.writerow([])
				lst.sort(key=itemgetter(4), reverse=True)
				wnocorrlst.writerows(lst+[])
				# wnocorrlst.writerow([])

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
				wnocommstulst.writerows(nocommstuList+[])
				# wnocommstulst.writerow([])

				wnocommstulst.writerow(['COURSE_1', 'COURSE_2'])
				wnocommstulst.writerow([course[0]+course[1], nocommstuList[1][0]+nocommstuList[1][1]])
				for indx in xrange(2,len(nocommstuList)):
					wnocommstulst.writerow(['', nocommstuList[indx][0]+nocommstuList[indx][1]])
				wnocommstulst.writerow([])

		# plot scatter graphs of r vs p for ALL and SINGLE
		if self.proPredictor == 'ALL':
			rlist, plist = [], []
			for rec in rpSinglelist:
				rlist.append(rec[4]), plist.append(rec[5])

			self.coefficientPointsPlot(rlist, plist, self.trainYrsText, self.currDir+self.factor+'_RvsP.png')
		else:
			rpSinglelist.sort(key=itemgetter(0,1), reverse=False)
			predictorDict = {}
			for rec in rpSinglelist:
				key = rec[0]+rec[1]
				if key not in predictorDict:
					predictorDict[key] = [rec]
				else:
					predictorDict[key].append(rec)

			for key in predictorDict:
				rlist, plist = [], []
				for rec in predictorDict[key]:
					rlist.append(rec[4]), plist.append(rec[5])

				self.coefficientPointsPlot(rlist, plist, key, self.rpDir4Single+key+'_RvsP.png')

		# sort r records
		flist = [x for x in corrList if x[1][0] == '1']
		slist = [x for x in corrList if x[1][0] == '2']
		flist.sort(key=itemgetter(3), reverse=False)
		slist.sort(key=itemgetter(3), reverse=False)
		w.writerows(flist+slist)

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
		nocorrlst, nocommstulst = self.dataDir+'nocorr/no_corr_list.csv', self.dataDir+'nocomstu/nocomstu_list.csv'
		wnocorrlst, wnocommstulst, nocomList, noCorrListTable, corrList = '', '', [], [], []

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
					nocommstuList.append(newCourse), nocomList.append([proPredictorCourse[0]+' '+proPredictorCourse[1], newCourse[0]+' '+newCourse[1]])
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
					wnan.writerows([[proPredictorCourse[0]+proPredictorCourse[1],newCourse[0]+newCourse[1],'len:',len(ydata)]]+[[proPredictorCourse[0]+proPredictorCourse[1]]+xdata]+[[newCourse[0]+newCourse[1]]+ydata]+[])
					continue

				self.createBoxPlots([proPredictorCourse[0], proPredictorCourse[1]]+xdata, [newCourse[0], newCourse[1]]+ydata)
				# slope, intercept, r_value, p_value, std_err = linregress(xdata, ydata)
				# format the parameters precision
				slope, intercept, r_value, p_value, std_err = linregress(xdata, ydata)
				r, slope, intercept, r_value, p_value, std_err = [float(format(r, '.4f')), float(format(slope, '.4f')), float(format(intercept, '.4f')), float(format(r_value, '.4f')), float(format(p_value, '.4f')), float(format(std_err, '.4f'))]

				# r_value = float(format(r, '.4f'))
				slope, intercept = self.regressionPlot(xdata, ydata, r, 1, xaxis, yaxis, self.linear_plots_ori, len(ydata))
				a,b,c = self.regressionPlot(xdata, ydata, r, 2, xaxis, yaxis, self.quadratic_plots_ori, len(ydata))

				slope, intercept, a, b, c = [float(format(slope, '.4f')), float(format(intercept, '.4f')), float(format(a, '.4f')), float(format(b, '.4f')), float(format(c, '.4f'))]

				# w.writerow([proPredictorCourse[0], proPredictorCourse[1], newCourse[0], newCourse[1], r, len(ydata), 0, p_value, std_err, slope, intercept, a, b, c, r*r, min(xdata), max(xdata)])
				corrList.append([proPredictorCourse[0], proPredictorCourse[1], newCourse[0], newCourse[1], r, len(ydata), 0, p_value, std_err, slope, intercept, a, b, c, float(format(r*r, '.4f')), min(xdata), max(xdata)])

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

		# sort r records
		flist = [x for x in corrList if x[1][0] == '1']
		slist = [x for x in corrList if x[1][0] == '2']
		flist.sort(key=itemgetter(3), reverse=False)
		slist.sort(key=itemgetter(3), reverse=False)
		w.writerows(flist+slist)

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

	def coefficientPointsPlot(self, rlist, plist, title, fname):
		if os.path.exists(fname):
			return

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
		plt.title('Pearson Coefficient vs Number of sample points \nusing '+title)

		plt.grid(True)

		# figName = self.currDir+fname+'_RvsP.png'
		fig.savefig(fname)
		plt.close(fig)

	def regressionPlot(self, xdata, ydata, r_value, power, xaxis, yaxis, plotDir, points):
		xarray, yarray = np.array(xdata), np.array(ydata)
		z = np.polyfit(xarray, yarray, power)
		p = np.poly1d(z)

		subj, num = xaxis.split(' ')[:2]
		subjNew, numNew = yaxis.split(' ')[:2]
		# create Predicting course folder
		folder = plotDir + subjNew + numNew
		figName = folder + '/' + subj + num + ' ' + subjNew + numNew + ' ' + str(r_value) + ' ' + str(points) + '.png'

		if os.path.exists(figName):
			return z
		elif not os.path.exists(folder):
			os.makedirs(folder)

		fig = plt.figure()

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
		creader, writer = csv.reader(open(self.courselist), delimiter = ','), csv.writer(open(self.uniTechCrsList, 'w'))
		header = creader.next()
		writer.writerow(header)
		for row in creader:
			crs = row[0].replace(' ','')+row[1]
			if crs in self.techList:
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
		# the technical course file does not have a header
		reader = csv.reader(open(self.allTechCrs), delimiter = ',')
		for row in reader:
			self.techList.append(row[0]+row[1])

		r = csv.reader(open(self.regDataPath), delimiter=',')
		techWrter = csv.writer(open(self.techCrsCSV, 'w'))

		hearders = r.next()
		techWrter.writerow(hearders)
		for row in r:
			course = row[3].replace(' ','')+row[4].replace(' ','')
			# change MATH 110 ===> MATH 133; ENGR 110 ===> ENGR 111
			if course == 'MATH110':
				row[4] = '133'

			if course == 'ENGR110':
				row[4] = '111'

			crs = row[3].replace(' ','')+row[4].replace(' ','')
			if crs in self.techList:
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
		# proPredictorSubj = proPredictorNum = ''
		# if not (self.proPredictor == 'ALL'):
		# 	proPredictorSubj, proPredictorNum = self.proPredictor.split(' ')

		reader = csv.reader(open(self.CRS_STU), delimiter = ',')
		reader.next()

		matrix, proPredictor = [],''
		for row in reader:
			matrix.append(row)
			# if (proPredictorSubj == row[0].replace(' ','')) and (proPredictorNum == row[1]):
			# 	proPredictor = row

		w = csv.writer(open(self.pairsFrequency, 'w'))
		w.writerow(['xcode', 'xnum', 'ycode', 'ynum', 'pairs'])

		# if self.proPredictor == 'ALL':
		for x in matrix:
			for y in matrix:
				if (int(x[1][0]) < int(y[1][0])) and (int(x[1][0]) < 3):
					cnt = 0
					for index in xrange(2,len(x)):
						if x[index].isdigit() and y[index].isdigit():
							cnt = cnt + 1
					# print x[0], ' ', x[1], ' vs ', y[0], ' ', y[1], ' cnt: ', cnt
					w.writerow([x[0], x[1], y[0], y[1], cnt])
		# else:
		# 	for x in matrix:
		# 		if int(x[1][0]) > int(proPredictorNum[0]):
		# 			cnt = 0
		# 			for index in xrange(2,len(x)):
		# 				if x[index].isdigit() and proPredictor[index].isdigit():
		# 					cnt = cnt + 1
		# 			w.writerow([proPredictor[0], proPredictor[1], x[0], x[1], cnt])

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

		self.weightPxyFile = self.dataDir + 'fv1_' + str(w1) + '_' + str(w2) +'.csv'
		writer = csv.writer(open(self.weightPxyFile, 'w'))
		# build the self.predictorFile
		self.top1FactorsFile = self.dataDir + 'T1F_' + str(w1) + '_' + str(w2) + '_' + self.trainYrsText +'.csv'
		factorWriter = csv.writer(open(self.top1FactorsFile, 'w'))
		self.top3FactorsFile = self.dataDir + 'T3F_' + str(w1) + '_' + str(w2) + '_' + self.trainYrsText +'.csv'
		factorTop3Writer = csv.writer(open(self.top3FactorsFile, 'w'))

		header.insert(6, str(w1) + '_' + str(w2))
		factorWriter.writerow(header)
		factorTop3Writer.writerow(header)

		ylist, rlist, plist, t1Lists = [], [], [], []
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
					# factorWriter.writerows(top1List)
					t1Lists += top1List
					factorTop3Writer.writerows(top3List)

					ylist, rlist, plist = [], [], []

		if (len(ylist) == len(rlist)) and (len(ylist) == len(plist)) and (len(ylist) > 0):
			writer.writerow(header)
			ylist, top1List, top3List = self.PxyPredictors(ylist, rlist, plist, w1, w2)
			writer.writerows(ylist)
			# factorWriter.writerows(top1List)
			t1Lists += top1List
			factorTop3Writer.writerows(top3List)

			ylist, rlist, plist = [], [], []

		# sort r records
		flist = [x for x in t1Lists if x[1][0] == '1']
		slist = [x for x in t1Lists if x[1][0] == '2']
		flist.sort(key=itemgetter(3), reverse=False)
		slist.sort(key=itemgetter(3), reverse=False)
		factorWriter.writerows(flist+slist)

	def PxyPredictors(self, ylist, rlist, plist, w1, w2):
		pxyArr, top1List, top3List = [], [], []
		for sublist in ylist:
			norm_r = abs(float(sublist[4]))/float(max(rlist))
			norm_p = float(sublist[5])/float(max(plist))
			pxy = w1*norm_r + w2*norm_p

			pxy = float(format(pxy, '.4f'))
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
				pxy = ''
				if r < 0:
					pxy = w1list[x]*r*(-1.0)/maxr + w2list[x]*p/maxp
				else:
					pxy = w1list[x]*r/maxr + w2list[x]*p/maxp

				sublist.append(format(pxy, '.4f'))

		return ylist

	def predictProcessTop3Factors(self, testReg, predictResults, power, predictorsFile):
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

	def precision4Ped(self, errRangeStdErrList, testSet, regression):
		precisionList = []
		for errRec in errRangeStdErrList:
			rec, errorList = [self.trainYrsText, testSet, regression, self.factor]+errRec[:6]+[errRec[18],errRec[14]], errRec[20:]
			le_05 = be_05_10 = be_10_15 = gt15 = 0
			for err in errorList:
				if abs(float(err)) <= 0.5:
					le_05 += 1
				elif abs(float(err)) <= 1.0:
					be_05_10 += 1
				elif abs(float(err)) <= 1.5:
					be_10_15 += 1
				else:
					gt15 += 1

			instance = le_05+be_05_10+be_10_15+gt15
			rec += [le_05, float(format(le_05*100.0/instance, '.4')), be_05_10, float(format(be_05_10*100.0/instance, '.4')), le_05+be_05_10, float(format((le_05+be_05_10)*100.0/instance, '.4')), be_10_15, float(format(be_10_15*100.0/instance, '.4')), gt15, float(format(gt15*100.0/instance, '.4'))]
			precisionList.append(rec)

		return precisionList

	def predictProcessTop1Factors(self, testReg, predictResults, power, predictorsFile):
		# this prediction process only works for Top1 ALL
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
						minList.append(x[15]), maxList.append(x[16]), testXs.append(testRegDict[testXKey])

				# have located the predictable course pairs stored in pairsList
				pairsList = self.gradePairs(testY, testXs, minList, maxList)
				if len(pairsList) > 0:
					predictingList.append(pairsList)

		writer = csv.writer(open(predictResults, 'w'))

		AERPList, errRangeStdErrList, pointsList, rList, aveAbsErrList, mapeList, realEstPairList, pairRangeList, ppedRec = [], [], [], [], [], [], [], [], []
		for pairsList in predictingList:
			for pairs in pairsList:
				[xgrades, ygrades] = pairs
				# locate predicting equation; key: predicting course
				key = ygrades[0] + ygrades[1]
				predictors = predictorDict[key]
				# linear: y = slope * x + intercept;	quadratic: y = ax^2+bx+c
				slope = intercept = coefficient = pointFreq = xSubj = xNum = ySubj = yNum = Pxy = 0
				for predictor in predictors:
					xcourse, predictorCourse = xgrades[0] + xgrades[1], predictor[0] + predictor[1]
					if xcourse == predictorCourse:
						# !!!caution: for the index
						# xSubj,xNum,ySubj,yNum, coefficient,pointFreq = predictor[0], predictor[1], predictor[2], predictor[3], predictor[4], predictor[5]
						# slope,intercept,a,b,c = predictor[9], predictor[10], predictor[11], predictor[12], predictor[13]
						xSubj,xNum,ySubj,yNum,coefficient,pointFreq,Pxy,slope,intercept,a,b,c = predictor[:7]+predictor[9:14]
						# slope,intercept,a,b,c = predictor[9:14]
						pointsList.append(float(pointFreq)), rList.append(float(coefficient))
						# compute errors: aesum: absolute err sum; aepsum: absolute err percent sum
						errorList, absErrPerList, aesum, aepsum, mseSum = [], [], 0, 0, 0
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

							# sum the mse
							mseSum += np.power(error, 2)

							errorList.append(error)
							aesum += abs(error)

							absErrPer = 0 
							if actualGrade == 0:
								absErrPer = abs(error)/1.0
							else:
								absErrPer = abs(error)/actualGrade

							aepsum += absErrPer
							absErrPerList.append(str(format(absErrPer*100, '.2f'))+'%')

						# compute mse
						mse = mseSum/(len(xgrades)-2)
						rmse = format(np.sqrt(mse), '.2f')

						mae = format(aesum/len(errorList), '.2f')
						aveAbsErrList.append(float(mae))

						mape = format(aepsum/len(errorList), '.2f')
						mapeList.append(float(mape))

						errArr = np.array(errorList)
						errorave, errStd = format(np.average(errArr), '.2f'), format(np.std(errArr), '.2f')

						gradesArr = np.array(predictGrades[2:])
						mean, std = format(np.average(gradesArr), '.2f'), format(np.std(gradesArr), '.2f')

						# compute the real grades' mean and std
						# print 'ygrades[2:]: ', ygrades[2:]
						realGrades = np.array([float(grade) for grade in ygrades[2:]])
						rMean, rStd = format(np.average(realGrades), '.2f'), format(np.std(realGrades), '.2f')

						tempList = [xSubj,xNum,ySubj,yNum,pointFreq,coefficient,mean,std,errStd,rMean,rStd,errorave,mae,mape,len(errorList),min(errorList),max(errorList), max(errorList)-min(errorList), Pxy, rmse]
						errRangeStdErrList.append(tempList+errorList)

						realEstPairList.append(ygrades), realEstPairList.append(predictGrades)

						actualGradesSorted, predictedGradesSorted = np.sort(ygrades[2:]), np.sort(predictGrades[2:])
						pairRangeList.append([xgrades[0], xgrades[1], ygrades[0], ygrades[1], actualGradesSorted[0], actualGradesSorted[-1], predictedGradesSorted[0], predictedGradesSorted[-1]])

						xgrades.insert(0, 'predictor'), ygrades.insert(0, 'real'), predictGrades.insert(0, 'predicting')

						errorList = ['', '', 'Err']+errorList
						absErrPerList = ['', '', 'AbsErrPer:%']+absErrPerList

						# appendix = ['point#', pointFreq, 'Coefficient:', coefficient, 'average error:', errorave]
						appendix = [ 'mean Err:', errorave, 'mea:', mae, 'mape:', mape]

						ppedRec += [myCopy.deepcopy(xgrades), myCopy.deepcopy(ygrades), myCopy.deepcopy(predictGrades), myCopy.deepcopy(errorList)]
						# if not self.errMerge:
							# writer.writerows([xgrades, ygrades, predictGrades, errorList])
							# writer.writerows([xgrades, ygrades, predictGrades, errorList, absErrPerList, appendix])
						# errw.writerow([errorave, coefficient, pointFreq])
						AERPList.append([errorave, coefficient, pointFreq])

						# print xgrades, '\n', ygrades, '\n', predictGrades, '\n', errorList, '\n', absErrPerList, '\n'

		# write precision
		header = ['TrainSet','TestSet','LQ','Factor','xSubj','xNum','ySubj','yNum','point#','r','Pxy','instance','0~0.5','%','0.5~1.0','%','0~1.0','%','1.0~1.5','%','gt1.5','%']
		testSet, factor, regression = predictResults.split('/')[-1].split('.')[0].split('_')
		precisionList = self.precision4Ped(errRangeStdErrList, testSet, regression)
		precisionList.sort(key=itemgetter(7,0,3,5), reverse=False)
		writer.writerows([header]+precisionList)

		# write predictor-predicted course lists
		# if not self.errMerge:
		# 	writer.writerows(['']+ppedRec)

		# pick the 1st year predictors and 2nd year predictors
		# sort errRangeStdErrList
		# [xsubj, xNum, ySubj, yNum, sample Point#, r, std, mean of err, mean absolute err, test instance#, minErr, maxErr, internal]
		header = ['xSubj','xNum','ySubj','yNum','point#','r','mean','std','errStd','rMean','rStd','ME','MAE','MAPE','instance','minErr','maxErr','interval','Pxy','RMSE']
		flist = [x for x in errRangeStdErrList if x[1][0] == '1']
		slist = [x for x in errRangeStdErrList if x[1][0] == '2']
		flist.sort(key=itemgetter(3), reverse=False)
		slist.sort(key=itemgetter(3), reverse=False)
		writer.writerows(['']+[header]+flist+slist+[''])

		# ['xSubj', 'xNum', 'ySubj', 'yNum', 'point#', 'r', 'mean', 'std', 'errStd', 'rMean', 'rStd','ME', 'MAE', 'MAPE', 'insOneCrs', 'minErr', 'maxErr', 'interval']
		# build the header-format table and sort by predictor, then predicted course
		header = ['xSubj','xNum','ySubj','yNum','point#','r','mean','rMean','std','rStd','mean diff','std diff','MAE','instance','minErr','maxErr','interval','Pxy','RMSE']
		# writer.writerow(header)
		tmp = [ item[:7]+[item[9], item[7], item[10], float(item[6])-float(item[9]), float(item[7])-float(item[10]), item[12]]+item[14:20] for item in errRangeStdErrList ]

		# pick the 1st year predictors and 2nd year predictors
		flist = [x for x in tmp if x[1][0] == '1']
		slist = [x for x in tmp if x[1][0] == '2']
		flist.sort(key=itemgetter(3), reverse=False)
		slist.sort(key=itemgetter(3), reverse=False)
		writer.writerows([header]+flist+[header]+slist+[''])

		header = ['xSubj', 'xNum', 'ySubj', 'yNum', 'rMin', 'rMax', 'pMin', 'pMax', 'rInterval', 'pInterval', 'abs diff']
		# writer.writerow(header)
		tmp = [pairRangeList[x]+[float(pairRangeList[x][5])-float(pairRangeList[x][4]), float(pairRangeList[x][7])-float(pairRangeList[x][6]), abs((float(pairRangeList[x][5])-float(pairRangeList[x][4]))-(float(pairRangeList[x][7])-float(pairRangeList[x][6])))] for x in xrange(0, len(pairRangeList))]
		# sort by predictor, then predicted course
		flist = [x for x in tmp if x[1][0] == '1']
		slist = [x for x in tmp if x[1][0] == '2']
		flist.sort(key=itemgetter(3), reverse=False)
		slist.sort(key=itemgetter(3), reverse=False)
		writer.writerows([header]+flist+[header]+slist)

		# add real vs estimated grade pairs
		writer.writerows(['']+realEstPairList)

		# format maeList to plot the graphs
		# ['xSubj', 'xNum', 'ySubj', 'yNum', 'point#', 'r', 'MAE']
		maeList = [ item[:6]+[item[12]] for item in errRangeStdErrList[1:] ]
		self.plotPredictionMAEFigures(testReg, power, maeList, '')

	def predictProcessMultiFactors(self, testReg, predictResults, power, predictorsFile):
		# build equation/predictor dict
		r1 = csv.reader(open(predictorsFile), delimiter=',')
		header1, predictorDict = r1.next(), {}
		for row in r1:
			# key: the predicting course; value of key: row of predictor & predicting course
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
		predictingList = []
		for key in predictorDict:
			if key in testRegDict:
				crsY, predictors = testRegDict[key], predictorDict[key]
				for x in predictors:
					crsXKey = x[0]+x[1]
					if crsXKey in testRegDict:
						crsX = testRegDict[crsXKey]
						if len(crsX) == len(crsY):
							xgrades, ygrades = [], []
							for index in xrange(2,len(crsY)):
								if (crsX[index].isdigit()) and (crsY[index].isdigit()):
									xgrades.append(crsX[index]), ygrades.append(crsY[index])
							if (len(xgrades) > 0) and (len(xgrades) == len(ygrades)):
								predictingList.append([crsX[:2]+xgrades, crsY[:2]+ygrades])

		AERPList, errRangeStdErrList, pointsList, rList, aveAbsErrList, mapeList, realEstPairList, pairRangeList = [], [], [], [], [], [], [], []
		# dict for predictor_predicting_records
		predictorPredictingRecDict, ppRecDict = {}, []
		for pairs in predictingList:
			xgrades, ygrades = pairs
			# locate predicting equation; key: predicting course
			key = ygrades[0] + ygrades[1]
			predictors = predictorDict[key]
			# linear: y = slope * x + intercept;	quadratic: y = ax^2+bx+c
			# slope = intercept = coefficient = pointFreq = xSubj = xNum = ySubj = yNum = Pxy = 0
			for predictor in predictors:
				xcourse, predictorCourse = xgrades[0]+xgrades[1], predictor[0]+predictor[1]
				if xcourse == predictorCourse:
					# !!!caution: for the index
					xSubj,xNum,ySubj,yNum,coefficient,pointFreq,slope,intercept,a,b,c = predictor[:6]+predictor[8:13]
					pointsList.append(float(pointFreq)), rList.append(float(coefficient))
					# compute errors: aesum: absolute err sum; aepsum: absolute err percent sum
					errorList, absErrPerList, aesum, aepsum, mseSum = [], [], 0, 0, 0
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

						# sum the mse
						mseSum += np.power(error, 2)

						errorList.append(error)
						aesum += abs(error)

						absErrPer = 0 
						if actualGrade == 0:
							absErrPer = abs(error)/1.0
						else:
							absErrPer = abs(error)/actualGrade

						aepsum += absErrPer
						absErrPerList.append(str(format(absErrPer*100, '.2f'))+'%')

					# compute mse
					mse = mseSum/(len(xgrades)-2)
					rmse = format(np.sqrt(mse), '.2f')

					mae = format(aesum/len(errorList), '.2f')
					aveAbsErrList.append(float(mae))

					mape = format(aepsum/len(errorList), '.2f')
					mapeList.append(float(mape))

					errArr = np.array(errorList)
					errorave, errStd = format(np.average(errArr), '.2f'), format(np.std(errArr), '.2f')

					gradesArr = np.array(predictGrades[2:])
					mean, std = format(np.average(gradesArr), '.2f'), format(np.std(gradesArr), '.2f')

					# compute the real grades' mean and std
					realGrades = np.array([float(grade) for grade in ygrades[2:]])
					rMean, rStd = format(np.average(realGrades), '.2f'), format(np.std(realGrades), '.2f')

					tempList = [xSubj,xNum,ySubj,yNum,pointFreq,coefficient,mean,std,errStd,rMean,rStd,errorave,mae,mape,len(errorList),min(errorList),max(errorList), max(errorList)-min(errorList), rmse]

					errRangeStdErrList.append(tempList+errorList)

					realEstPairList.append(ygrades), realEstPairList.append(predictGrades)

					actualGradesSorted, predictedGradesSorted = np.sort(ygrades[2:]), np.sort(predictGrades[2:])
					pairRangeList.append([xgrades[0], xgrades[1], ygrades[0], ygrades[1], actualGradesSorted[0], actualGradesSorted[-1], predictedGradesSorted[0], predictedGradesSorted[-1]])

					xgrades.insert(0, 'predictor'), ygrades.insert(0, 'real'), predictGrades.insert(0, 'predicting')

					errorList = ['', '', 'Err']+errorList
					absErrPerList = ['', '', 'AbsErrPer:%']+absErrPerList

					# appendix = ['point#', pointFreq, 'Coefficient:', coefficient, 'average error:', errorave]
					appendix = [ 'mean Err:', errorave, 'mea:', mae, 'mape:', mape]

					ppRecDict += [xgrades, ygrades, predictGrades, errorList]
					AERPList.append([errorave, coefficient, pointFreq])

					if (predictor[0]+predictor[1]) not in predictorPredictingRecDict:
						predictorPredictingRecDict[predictor[0]+predictor[1]] = [[xgrades, ygrades, predictGrades, errorList]]
					else:
						predictorPredictingRecDict[predictor[0]+predictor[1]].append([xgrades, ygrades, predictGrades, errorList])

		# =================================================================== #
		writer = csv.writer(open(predictResults, 'w'))
		# if not self.errMerge:
		# 	writer.writerows(ppRecDict)
		# =================================================================== #
		# sort predictorPredictingRecDict
		# writer.writerow([''])
		# for key in predictorPredictingRecDict:
			# for triple in predictorPredictingRecDict[key]:
				# writer.writerows(triple)
			# separate each predictor predicting records
			# writer.writerow([''])
		# =================================================================== #
		header = ['xSubj','xNum','ySubj','yNum','point#','r','instance','0~0.5','%','0.5~1.0','%','0~1.0','%','1.0~1.5','%','gt1.5','%']
		# insert Pxy
		topPrecisions, precisions = '', ''
		if (self.proPredictor == 'ALL') and (self.factor == 'PR'):
			# writer.writerows(self.insertPxy(self.predictionPrecision(errRangeStdErrList, header)))
			precisions = self.insertPxy(self.predictionPrecision(errRangeStdErrList, header))
			topPrecisions = self.pickTopPrecision(precisions)
		else:
			precisions = self.predictionPrecision(errRangeStdErrList, header)
			topPrecisions = self.pickTopPrecision(precisions)
			# writer.writerows(self.predictionPrecision(errRangeStdErrList, header))

		writer.writerows(topPrecisions+precisions)
		# =================================================================== #
		# [xsubj, xNum, ySubj, yNum, sample Point#, r, std, mean of err, mean absolute err, test instance#, minErr, maxErr, internal]
		header = ['xSubj','xNum','ySubj','yNum','point#','r','mean','std','errStd','rMean','rStd','ME','MAE','MAPE','instance','minErr','maxErr','interval','RMSE']
		# create errRangeStdErrList dict by predictors and predicting courses, respectively
		# insert Pxy
		if (self.proPredictor == 'ALL') and (self.factor == 'PR'):
			writer.writerows(self.insertPxy(self.sortPredictionResults(errRangeStdErrList, header)))
		else:
			writer.writerows(self.sortPredictionResults(errRangeStdErrList, header))
		# =================================================================== #
		# ['xSubj', 'xNum', 'ySubj', 'yNum', 'point#', 'r', 'mean', 'std', 'errStd', 'rMean', 'rStd','ME', 'MAE', 'MAPE', 'instance', 'minErr', 'maxErr', 'interval']
		# build the header-format table and sort by predictor, then predicted course
		header = ['xSubj','xNum','ySubj','yNum','point#','r','mean','rMean','std','rStd','mean diff','std diff','MAE','instance','minErr','maxErr','interval','RMSE']
		# writer.writerow(header)
		tmp = [ item[:7]+[item[9], item[7], item[10], float(item[6])-float(item[9]), float(item[7])-float(item[10]), item[12]]+item[14:19] for item in errRangeStdErrList ]
		# writer.writerows(self.sortPredictionResults(tmp, header))
		# =================================================================== #
		header = ['xSubj', 'xNum', 'ySubj', 'yNum', 'rMin', 'rMax', 'pMin', 'pMax', 'rInterval', 'pInterval', 'abs diff']
		# writer.writerow(header)
		tmp = [pairRangeList[x]+[float(pairRangeList[x][5])-float(pairRangeList[x][4]), float(pairRangeList[x][7])-float(pairRangeList[x][6]), abs((float(pairRangeList[x][5])-float(pairRangeList[x][4]))-(float(pairRangeList[x][7])-float(pairRangeList[x][6])))] for x in xrange(0, len(pairRangeList))]
		# writer.writerows(self.sortPredictionResults(tmp, header))
		# =================================================================== #
		# add real vs estimated grade pairs
		# writer.writerows(['']+realEstPairList)
		# =================================================================== #
		# format maeList to plot the graphs
		# ['xSubj', 'xNum', 'ySubj', 'yNum', 'point#', 'r', 'MAE']
		maeList = [ item[:6]+[item[12]] for item in errRangeStdErrList[1:] ]
		if self.proPredictor == 'ALL':
			self.plotPredictionMAEFigures(testReg, power, maeList, '')
		elif self.proPredictor == 'SINGLE':
			predictorsDict = {}
			for rec in maeList:
				predictor = rec[0]+' '+rec[1]
				# create predictorsDict
				if predictor not in predictorsDict:
					predictorsDict[predictor] = [rec]
				else:
					predictorsDict[predictor].append(rec)

			for predictor in predictorsDict:
				sub_maeList = predictorsDict[predictor]
				self.plotPredictionMAEFigures(testReg, power, sub_maeList, predictor)

	def pickTopPrecision(self, datasets):
		header = ''
		f1s2ListPredictor, f1t3ListPredictor, s2t3ListPredictor = [], [], []
		f1s2ListPredicted, f1t3ListPredicted, s2t3ListPredicted = [], [], []
		tempList, precisionIndex = [], ''
		for rec in datasets:
			if len(rec) > 0:
				if rec[0] == 'xSubj':
					header, precisionIndex = rec, rec.index('0~1.0')
				else:
					tempList.append(rec)
			else:
				self.pickTopPrecision4S2T3(precisionIndex+1, tempList, f1s2ListPredictor, f1t3ListPredictor, s2t3ListPredictor, f1s2ListPredicted, f1t3ListPredicted, s2t3ListPredicted)
				tempList = []

		if len(tempList) > 0:
			self.pickTopPrecision4S2T3(precisionIndex+1, tempList, f1s2ListPredictor, f1t3ListPredictor, s2t3ListPredictor, f1s2ListPredicted, f1t3ListPredicted, s2t3ListPredicted)

		for x in [f1s2ListPredictor, f1t3ListPredictor, s2t3ListPredictor, f1s2ListPredicted, f1t3ListPredicted, s2t3ListPredicted]:
			x.sort(key=itemgetter(precisionIndex+1), reverse=True)

		return [['f1s2P'], [''], header]+f1s2ListPredictor+[[''],['f1t3P'], [''], header]+f1t3ListPredictor+[[''],['s2t3P'], [''], header]+s2t3ListPredictor+[[''],['f1s2Ped'], [''], header]+f1s2ListPredicted+[[''],['f1t3Ped'], [''], header]+f1t3ListPredicted+[[''],['s2t3Ped'], [''], header]+s2t3ListPredicted+['']

	def pickTopPrecision4S2T3(self, precisionIndex, tempList, f1s2P, f1t3P, s2t3P, f1s2Ped, f1t3Ped, s2t3Ped):
		xyr, yyr = tempList[0][1][0], tempList[0][3][0]
		if yyr == '4':
			return

		maxPrecision = self.pickMaxPrecision(tempList, precisionIndex)

		freqx = Counter(item[0]+item[1] for item in tempList)
		freqy = Counter(item[2]+item[3] for item in tempList)

		# for predictor
		if len(freqx) == 1:
			# first year predictors
			if xyr == '1':
				# second year predicted courses
				if yyr == '2':
					ret = self.pickRecordsByCondiction(tempList, [precisionIndex, maxPrecision])
					f1s2P += ret
				# third year predicted courses
				else:
					ret = self.pickRecordsByCondiction(tempList, [precisionIndex, maxPrecision])
					f1t3P += ret
			# second year predictors
			else:
				ret = self.pickRecordsByCondiction(tempList, [precisionIndex, maxPrecision])
				s2t3P += ret
		# for predicted course
		elif len(freqy) == 1:
			# second year predicted courses: 1-2
			if yyr == '2':
				ret = self.pickRecordsByCondiction(tempList, [precisionIndex, maxPrecision])
				f1s2Ped += ret
			# third year predicted courses
			else:
				f1List, s2List = [], []
				for x in tempList:
					if x[1][0] == '1':
						f1List.append(x)
					else:
						s2List.append(x)
				# first year predictor: 1-3
				maxPrecision = self.pickMaxPrecision(f1List, precisionIndex)
				ret = self.pickRecordsByCondiction(f1List, [precisionIndex, maxPrecision])
				f1t3Ped += ret
				# second year predictor: 2-3
				maxPrecision = self.pickMaxPrecision(s2List, precisionIndex)
				ret = self.pickRecordsByCondiction(s2List, [precisionIndex, maxPrecision])
				s2t3Ped += ret

	def pickMaxPrecision(self, tempList, precisionIndex):
		precisionList = []
		[precisionList.append(float(x[precisionIndex])) for x in tempList]
		maxPrecision = max(precisionList)
		precisionList.sort(reverse=True)
		if maxPrecision == float(100):
			freq = Counter(item for item in precisionList)
			if len(freq) > 1:
				maxPrecision = precisionList[freq[maxPrecision]]

		return maxPrecision

	def pickRecordsByCondiction(self, datasets, condition):
		ret = []
		[precisionIndex, maxp] = condition
		for x in datasets:
			if float(x[precisionIndex]) >= float(maxp):
				ret.append(x)

		return ret

	def insertPxy(self, resultsData):
		r = csv.reader(open(self.weightPxyFile), delimiter=',')
		pxyPredictedCrsDict = {}
		for rec in r:
			if (len(rec) > 0) and (rec[0] != 'xsubCode'):
				key = rec[2]+rec[3]
				if key not in pxyPredictedCrsDict:
					pxyPredictedCrsDict[key] = [[rec[0], rec[1], rec[6]]]
				else:
					pxyPredictedCrsDict[key].append([rec[0], rec[1], rec[6]])

		ret = []
		for record in resultsData:
			rec = myCopy.deepcopy(record)
			if len(rec) > 0:
				if (rec[0] != 'xSubj'):
					key = rec[2]+rec[3]
					for predictor in pxyPredictedCrsDict[key]:
						if (rec[0]+rec[1]) == (predictor[0]+predictor[1]):
							rec.insert(6, predictor[2])
				elif (rec[0] == 'xSubj'):
					rec.insert(6, 'Pxy')

			ret.append(rec)

		return ret

	def sortPredictionResults(self, resultsData, header):
		predictorsDict, predictingDict = {}, {}
		for rec in resultsData:
			predictor, predicting = rec[0]+rec[1], rec[2]+rec[3]
			# create predictorsDict
			if predictor not in predictorsDict:
				predictorsDict[predictor] = [rec]
			else:
				predictorsDict[predictor].append(rec)

			# create predicting
			if predicting not in predictingDict:
				predictingDict[predicting] = [rec]
			else:
				predictingDict[predicting].append(rec)

		ret = []
		# write predictorsDict
		for key in predictorsDict:
			recs = predictorsDict[key]
			for key, items in self.partitionCoursesByYear(recs):
				# print items
				# sort by precision
				items.sort(key=itemgetter(12), reverse=True)
				# writer.writerows([header]+recs+[''])
				ret+=[header]+items+['']
		# write predictingDict
		for key in predictingDict:
			recs = predictingDict[key]
			recs.sort(key=itemgetter(12), reverse=True)
			# writer.writerows([header]+recs+[''])
			ret+=[header]+recs+['']

		return ret

	def predictionPrecision(self, errRecList, header):
		# error range: '0~0.5','0.5~1.0','1.0~1.5','gt1.5'
		precisionList = []
		for errRec in errRecList:
			rec, errorList = errRec[:6]+[errRec[14]], errRec[19:]
			le_05 = be_05_10 = be_10_15 = gt15 = 0
			for err in errorList:
				if abs(float(err)) <= 0.5:
					le_05 += 1
				elif abs(float(err)) <= 1.0:
					be_05_10 += 1
				elif abs(float(err)) <= 1.5:
					be_10_15 += 1
				else:
					gt15 += 1

			instance = le_05+be_05_10+be_10_15+gt15
			rec += [le_05, float(format(le_05*100.0/instance, '.4')), be_05_10, float(format(be_05_10*100.0/instance, '.4')), le_05+be_05_10, float(format((le_05+be_05_10)*100.0/instance, '.4')), be_10_15, float(format(be_10_15*100.0/instance, '.4')), gt15, float(format(gt15*100.0/instance, '.4'))]
			precisionList.append(rec)

		return self.sortPredictionResults(precisionList, header)

	def partitionCoursesByYear(self, dataList):
		yrCrsDict = {}
		for data in dataList:
			key = data[3][0]
			if key not in yrCrsDict:
				yrCrsDict[key]=[data]
			else:
				yrCrsDict[key].append(data)

		return yrCrsDict.items()

	def plotPredictionMAEFigures(self, testReg, power, maeList, predictor4Single):
		# ['xSubj', 'xNum', 'ySubj', 'yNum', 'point#', 'r', 'MAE']
		prefix, suffix = testReg.split('/')[-1].split('_')[0], ''
		if self.proPredictor == 'SINGLE':
			prefix = predictor4Single
		if power == 1:
			suffix, tSuffix = 'L', 'Linear'
		elif power == 2:
			suffix, tSuffix = 'Q', 'Quadratic'

		# sort by predictor, then predicted course
		# 1st yr predictors vs 2nd/3rd/4th predicted courses
		flist = [x for x in maeList if x[1][0] == '1']
		# 2nd yr predictors vs 3rd/4th predicted courses
		slist = [x for x in maeList if x[1][0] == '2']

		# f2List: 1vs2; f3List: 1vs3; f4List: 1vs4; s3List: 2vs3; s4List: 2vs4
		f2List,f3List,f4List, s3List,s4List = [],[],[],[],[]
		for rec in flist:
			yr = rec[3][0]
			if yr == '2':
				f2List.append(rec)
			elif yr == '3':
				f3List.append(rec)
			elif yr == '4':
				f4List.append(rec)

		for rec in slist:
			yr = rec[3][0]
			if yr == '3':
				s3List.append(rec)
			elif yr == '4':
				s4List.append(rec)

		# for the predictors in 1st/2nd year technical courses
		# combinations: 1st vs 2nd/3rd/4th/2nd&3rd/2nd&3rd&4th; 2nd vs 3rd/4th/3rd&4th; 1st&2nd vs 3rd/4th/3rd&4th
		# 3D: 1st vs 2nd
		if len(f2List) > 0:
			if self.proPredictor == 'ALL':
				if self.factor == 'PR':
					self.plotPrediction3D(f2List, prefix, suffix, '1 vs 2')
				else:
					self.plotPredictionMAEFigures4P_R(f2List, prefix, suffix, '1 vs 2', self.factor)
			else:
				# for 1st year technical predictor
				self.plotPrediction3D(f2List, prefix, suffix, '1 vs 2')
		# 3D: 1st vs 3rd
		if len(f3List) > 0:
			if self.proPredictor == 'ALL':
				if self.factor == 'PR':
					self.plotPrediction3D(f3List, prefix, suffix, '1 vs 3')
				else:
					self.plotPredictionMAEFigures4P_R(f3List, prefix, suffix, '1 vs 3', self.factor)
			else:
				# for 1st year technical predictor
				self.plotPrediction3D(f3List, prefix, suffix, '1 vs 3')
		# 3D: 1st vs 4th
		if len(f4List) > 0:
			if self.proPredictor == 'ALL':
				if self.factor == 'PR':
					self.plotPrediction3D(f4List, prefix, suffix, '1 vs 4')
				else:
					self.plotPredictionMAEFigures4P_R(f4List, prefix, suffix, '1 vs 4', self.factor)
			else:
				# for 1st year technical predictor
				self.plotPrediction3D(f4List, prefix, suffix, '1 vs 4')
		# 3D: 1st vs 2nd&3rd
		if len(f2List) > 0 and len(f3List) > 0:
			if self.proPredictor == 'ALL':
				if self.factor == 'PR':
					self.plotPrediction3D(f2List+f3List, prefix, suffix, '1 vs 2,3')
				else:
					self.plotPredictionMAEFigures4P_R(f2List+f3List, prefix, suffix, '1 vs 2,3', self.factor)
			else:
				# for 1st year technical predictor
				self.plotPrediction3D(f2List+f3List, prefix, suffix, '1 vs 2,3')
		# 3D: 1st vs 2nd&4th
		if len(f2List) > 0 and len(f4List) > 0:
			if self.proPredictor == 'ALL':
				if self.factor == 'PR':
					self.plotPrediction3D(f2List+f4List, prefix, suffix, '1 vs 2,4')
				else:
					self.plotPredictionMAEFigures4P_R(f2List+f4List, prefix, suffix, '1 vs 2,4', self.factor)
			else:
				# for 1st year technical predictor
				self.plotPrediction3D(f2List+f4List, prefix, suffix, '1 vs 2,4')
		# 3D: 1st vs 3rd&4th
		if len(f3List) > 0 and len(f4List) > 0:
			if self.proPredictor == 'ALL':
				if self.factor == 'PR':
					self.plotPrediction3D(f3List+f4List, prefix, suffix, '1 vs 3,4')
				else:
					self.plotPredictionMAEFigures4P_R(f3List+f4List, prefix, suffix, '1 vs 3,4', self.factor)
			else:
				# for 1st year technical predictor
				self.plotPrediction3D(f3List+f4List, prefix, suffix, '1 vs 3,4')
		# 3D: 1st vs 2nd&3rd&4th
		if len(f2List) > 0 and len(f3List) > 0 and len(f4List) > 0:
			if self.proPredictor == 'ALL':
				if self.factor == 'PR':
					self.plotPrediction3D(f2List+f3List+f4List, prefix, suffix, '1 vs 2,3,4')
				else:
					self.plotPredictionMAEFigures4P_R(f2List+f3List+f4List, prefix, suffix, '1 vs 2,3,4', self.factor)
			else:
				# for 1st year technical predictor
				self.plotPrediction3D(f2List+f3List+f4List, prefix, suffix, '1 vs 2,3,4')

		# 3D: 2nd vs 3nd
		if len(s3List) > 0:
			if self.proPredictor == 'ALL':
				if self.factor == 'PR':
					self.plotPrediction3D(s3List, prefix, suffix, '2 vs 3')
				else:
					self.plotPredictionMAEFigures4P_R(s3List, prefix, suffix, '2 vs 3', self.factor)
			else:
				# for 2nd year technical predictor
				self.plotPrediction3D(s3List, prefix, suffix, '2 vs 3')
		# 3D: 2nd vs 4th
		if len(s4List) > 0:
			if self.proPredictor == 'ALL':
				if self.factor == 'PR':
					self.plotPrediction3D(s4List, prefix, suffix, '2 vs 4')
				else:
					self.plotPredictionMAEFigures4P_R(s4List, prefix, suffix, '2 vs 4', self.factor)
			else:
				# for 2nd year technical predictor
				self.plotPrediction3D(s4List, prefix, suffix, '2 vs 4')
		# 3D: 2nd vs 3nd&4th
		if len(s3List) > 0 and len(s4List) > 0:
			if self.proPredictor == 'ALL':
				if self.factor == 'PR':
					self.plotPrediction3D(s3List+s4List, prefix, suffix, '2 vs 3,4')
				else:
					self.plotPredictionMAEFigures4P_R(s3List+s4List, prefix, suffix, '2 vs 3,4', self.factor)
			else:
				# for 2nd year technical predictor
				self.plotPrediction3D(s3List+s4List, prefix, suffix, '2 vs 3,4')

		# 3D: 1st&2nd vs 3rd
		if len(f3List) > 0 and len(s3List) > 0:
			if self.factor == 'PR':
				self.plotPrediction3D(f3List+s3List, prefix, suffix, '1,2 vs 3')
			else:
				self.plotPredictionMAEFigures4P_R(f3List+s3List, prefix, suffix, '1,2 vs 3', self.factor)
		# 3D: 1st&2nd vs 4th
		if len(f4List) > 0 and len(s4List) > 0:
			if self.factor == 'PR':
				self.plotPrediction3D(f4List+s4List, prefix, suffix, '1,2 vs 4')
			else:
				self.plotPredictionMAEFigures4P_R(f4List+s4List, prefix, suffix, '1,2 vs 4', self.factor)
		# 3D: 1st&2nd vs 3rd&4th
		if len(f3List) > 0 and len(f4List) > 0 and len(s3List) > 0 and len(s4List) > 0:
			if self.factor == 'PR':
				self.plotPrediction3D(f3List+f4List+s3List+s4List, prefix, suffix, '1,2 vs 3,4')
			else:
				self.plotPredictionMAEFigures4P_R(f3List+f4List+s3List+s4List, prefix, suffix, '1,2 vs 3,4', self.factor)

		# 3D: overall: 1st vs 2nd&3rd&4th && 2nd vs 3rd&4th
		if len(maeList) > 0 and self.proPredictor == 'ALL':
			if self.factor == 'PR':
				self.plotPrediction3D(maeList, prefix, suffix, 'Overall')
			else:
				self.plotPredictionMAEFigures4P_R(maeList, prefix, suffix, 'Overall', self.factor)

	def plotPrediction3D(self, dataList, prefix, suffix, combination):
		pointsList, rList, aveAbsErrList = [], [], []
		for rec in dataList:
			pointsList.append(int(rec[4])), rList.append(float(rec[5])), aveAbsErrList.append(float(rec[6]))
		if len(pointsList) > 0:
			if self.proPredictor == 'SINGLE':
				title = 'Points vs r vs MAE: '+suffix+'\nPredictor:'+prefix+'; '+combination
				figName = self.maerp3DDir+suffix+'/'+prefix+'_rpMAE_'+suffix+'_'+combination+'.png'
			elif self.proPredictor == 'ALL':
				figName = self.maerp3DDir+suffix+'/'+prefix[3:]+'_rpMAE_'+suffix+'_'+combination+'.png'
				title = 'Points vs r vs MAE: '+suffix+'; rw:'+str(self.rw)+', pw:'+str(self.pw)+'\n'+prefix[3:]+' vs '+self.trainYrsText+'; '+combination

			self.maerp3DPlots(pointsList, rList, aveAbsErrList, figName, title)

	def plotPredictionMAEFigures4P_R(self, dataList, prefix, suffix, combination, factor):
		prList, aveAbsErrList = [], []
		for rec in dataList:
			aveAbsErrList.append(float(rec[6]))
			if factor == 'P':
				prList.append(int(rec[4]))
			elif factor == 'R':
				prList.append(float(rec[5]))

		if len(prList) > 0:
			figName = self.maerp3DDir+suffix+'/'+prefix[3:]+'_'+factor+'_MAE_'+suffix+'_'+combination+'.png'
			ytitle = 'MAE from '+prefix[3:]
			if factor == 'R':
				xtitle = 'coefficients from training set '+self.trainYrs[0]+'-'+self.trainYrs[-1]
				title = 'coefficients vs MAE: '+suffix+':'+prefix[3:]+' vs '+self.trainYrsText+'\n'+combination+'; H:'+str(self.threshold)
				self.errScatter(xtitle, ytitle, title, prList, aveAbsErrList, figName, 'R')
			elif factor == 'P':
				xtitle = 'Sample Points from training set '+self.trainYrs[0]+'-'+self.trainYrs[-1]
				title = 'Sample Points vs MAE: '+suffix+'; H:'+str(self.threshold)+'\n'+prefix[3:]+' vs '+self.trainYrsText+'; '+combination
				self.errScatter(xtitle, ytitle, title, prList, aveAbsErrList, figName, 'P')

	def gradePairs(self, testY, testXs, minList, maxList):
		resultPairs, pairsList, xCrsNums = [], [], []
		for x in testXs:
			# build the xgrades, ygrades lists
			xgrades, ygrades = [x[0], x[1]],[testY[0], testY[1]]
			xindex = testXs.index(x)
			xmin, xmax = minList[xindex],maxList[xindex]
			for index in xrange(2,len(testY)):
				if (x[index].isdigit() and testY[index].isdigit()) and (float(x[index]) >= float(xmin)) and (float(x[index]) <= float(xmax)):
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

	def errScatter(self, xtitle, ytitle, title, xdata, ydata, figName, xflag):
		if os.path.exists(figName):
			return

		fig = plt.figure()
		x, y = np.array(xdata), np.array(ydata)

		z = np.polyfit(x, y, 1)
		p = np.poly1d(z)
		plt.plot(x, y, '^', c='red')
		# xp = np.linspace(0, 9, 100)
		if not (xflag == 'R'):
			plt.plot(x, p(x), 'b--')

		plt.xlabel(xtitle)
		plt.ylabel(ytitle)
		plt.title(title)

		# plt.ylim(0.0, max(ydata)+0.5)
		plt.ylim(0.0, 10.0)

		ax = plt.axes()
		minorLocator, majorLocator = MultipleLocator(0.1), MultipleLocator(0.5)
		ax.yaxis.set_minor_locator(minorLocator)
		ax.yaxis.set_major_locator(majorLocator)

		if xflag == 'R':
			plt.xlim(-1.0, 1.0)
			minorLocator, majorLocator = MultipleLocator(0.1), MultipleLocator(0.1)
			plt.xticks(rotation=20, fontsize='medium')
		if xflag == 'P':
			plt.xlim(0, 120)
			minorLocator, majorLocator = MultipleLocator(2), MultipleLocator(10)
			plt.xticks(rotation=90, fontsize='small')

		ax.xaxis.set_minor_locator(minorLocator)
		ax.xaxis.set_major_locator(majorLocator)

		plt.grid(True)
		fig.savefig(figName)
		plt.close(fig)

	def maerp3DPlots(self, point, r, MAE, figName, title):
		if os.path.exists(figName):
			return

		# plot 3D graph
		fig = plt.figure()
		ax = Axes3D(fig)

		# ax.scatter(point, r, MAE, c='r', marker='o')
		for index in xrange(0,len(point)):
			if MAE[index] >= 4.0:
				ax.scatter(point[index], r[index], MAE[index], c='blue', marker='v')
			elif MAE[index] >= 3.0:
				ax.scatter(point[index], r[index], MAE[index], c='red', marker='o')
			elif MAE[index] >= 2.0:
				ax.scatter(point[index], r[index], MAE[index], c='yellow', marker='^')
			elif MAE[index] >= 1.0:
				ax.scatter(point[index], r[index], MAE[index], c='green', marker='+')
			else:
				ax.scatter(point[index], r[index], MAE[index], c='purple', marker='x')

		# add legend
		# labels = ['>=4.0', '>=3.0', '>=2.0', '>=1.0', '>=0.0']
		labels = ['[4.0,inf)', '[3.0,4.0)', '[2.0,3.0)', '[1.0,2.0)', '[0.0,1.0)']
		markerColors = [['v', 'blue'], ['o','red'], ['^', 'yellow'], ['+', 'green'], ['x', 'purple']]
		points = [ax.scatter([], [], [], marker=s[0], c=s[1]) for s in markerColors]
		plt.legend(points, labels, scatterpoints=1, loc=0)

		# set lables
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
		plt.xticks(rotation=90, fontsize='9')

		ax.yaxis.set_minor_locator(MultipleLocator(0.1))
		ax.yaxis.set_major_locator(MultipleLocator(0.1))
		plt.yticks(rotation=90, fontsize='9')

		ax.zaxis.set_minor_locator(MultipleLocator(0.1))
		ax.zaxis.set_major_locator(MultipleLocator(0.5))
		for t in ax.zaxis.get_major_ticks():
			t.label.set_fontsize(9)

		ax.view_init(elev=26, azim=57)
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

	def gradePointsDistribution(self, top1FactorsFile):
		# COLLECT THE GRADES POINTS FOR EVERY PREDICTOR AND PREDICTING COURSE PAIRS, AND THEN PLOT THESE POINTS IN SCATTER SCHEME
		# AND THESE GRAPHS ARE STORED IN self.yrvsyr
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

	def yrVSyrScatter(self, xdata, ydata, title, xlabel, ylabel, fname):
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
				predictor.insert(6, float(format(pxy, '.4f')))
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

	def mergeMAEsRanges(self, srcList, destAccs, destMAEs, destRanges, regression):
		# srcList: self.linearPredictResultsListTop1 or self.quadrPredictResultsListTop1
		# destMAEs: merged MAEs for all test sets for the training set and the threshold
		# destRanges: merged Ranges for all test sets for the training set and the threshold
		accRet, maeRet = [], []
		precisionsW = csv.writer(open(destAccs, 'w'))
		MAEsW = csv.writer(open(destMAEs, 'w'))
		RangesW = csv.writer(open(destRanges, 'w'))
		for src in srcList:
			filename = src.split('/')[-1].split('_')[0]
			r = csv.reader(open(src), delimiter=',')
			precisionList, MAEsList, RangesList, spaceIndex = [], [], [], 0
			for row in r:
				if spaceIndex > 3:
					break
				# precisions
				if spaceIndex == 0:
					precisionList.append(row)
				# reach MAEs
				if spaceIndex == 2:
					MAEsList.append(row)
				# reach Ranges
				if spaceIndex == 3:
					RangesList.append(row)

				if len(row) == 0:
					spaceIndex += 1

			acronym = ''
			if len(filename) > 3:
				acronym = filename[3:]
			else:
				acronym = filename

			head = precisionList[0]
			s2list,t3list,f4list,s2extreme,t3extreme,f4extreme = self.splitByYear(precisionList[1:-1], [7,6,17], 7, 17)
			precisionsW.writerows([[acronym],head]+s2list+['',head]+t3list+['', head]+f4list+[''])
			accRet.append([self.trainYrsText, acronym, self.factor, regression, '2']+s2extreme)
			accRet.append([self.trainYrsText, acronym, self.factor, regression, '3']+t3extreme)
			accRet.append([self.trainYrsText, acronym, self.factor, regression, '4']+f4extreme)

			head = MAEsList[0]
			s2list,t3list,f4list,s2extreme,t3extreme,f4extreme = self.splitByYear(MAEsList[1:-1], [3,2,12], 3, 12)
			MAEsW.writerows([[acronym],head]+s2list+['',head]+t3list+['', head]+f4list+[''])
			maeRet.append([self.trainYrsText, acronym, self.factor, regression, '2']+s2extreme)
			maeRet.append([self.trainYrsText, acronym, self.factor, regression, '3']+t3extreme)
			maeRet.append([self.trainYrsText, acronym, self.factor, regression, '4']+f4extreme)

			RangesW.writerows([[acronym]]+RangesList)

		return [accRet, maeRet]

	def splitByYear(self, src, orderSeqs, yearIndex, Acc_MAE_index):
		s2list,t3list,f4list=[],[],[]
		s2,t3,f4=[],[],[]
		for row in src:
			y = row[yearIndex][0]
			if y=='2':
				s2list.append(row)
				s2.append(float(row[Acc_MAE_index]))
			if y=='3':
				t3list.append(row)
				t3.append(float(row[Acc_MAE_index]))
			if y=='4':
				f4list.append(row)
				f4.append(float(row[Acc_MAE_index]))

		s2list.sort(key=itemgetter(orderSeqs[0],orderSeqs[1],orderSeqs[2]), reverse=True)
		t3list.sort(key=itemgetter(orderSeqs[0],orderSeqs[1],orderSeqs[2]), reverse=True)
		f4list.sort(key=itemgetter(orderSeqs[0],orderSeqs[1],orderSeqs[2]), reverse=True)

		return [s2list,t3list,f4list, [max(s2), min(s2)], [max(t3), min(t3)], [max(f4), min(f4)]]

	def mergeMAEsRangesManager(self):
		# T1: Top 1; L: Linear; Q: Quadratic; M: MAEs; R: Grade Ranges; Acc: Precisions; str(len(self.trainYrs)): 2,3,4,5; self.factor: PR,P,R; str(self.threshold): 1,5,10
		filesRet, accRets, maeRets = [], [], []
		destAccs = self.currDir + 'T1/T1LAcc' + str(len(self.trainYrs)) + self.factor + str(self.threshold) + '.csv'
		destMAEs = self.currDir + 'T1/T1LM' + str(len(self.trainYrs)) + self.factor + str(self.threshold) + '.csv'
		destRanges = self.currDir + 'T1/T1LR' + str(len(self.trainYrs)) + self.factor + str(self.threshold) + '.csv'
		accRet, maeRet = self.mergeMAEsRanges(self.linearPredictResultsListTop1, destAccs, destMAEs, destRanges, 'L')
		accRets+=accRet
		maeRets+=maeRet
		filesRet.append(destAccs), filesRet.append(destMAEs), filesRet.append(destRanges)

		destAccs = self.currDir + 'T1/T1QAcc' + str(len(self.trainYrs)) + self.factor + str(self.threshold) + '.csv'
		destMAEs = self.currDir + 'T1/T1QM' + str(len(self.trainYrs)) + self.factor + str(self.threshold) + '.csv'
		destRanges = self.currDir + 'T1/T1QR' + str(len(self.trainYrs)) + self.factor + str(self.threshold) + '.csv'
		accRet, maeRet = self.mergeMAEsRanges(self.quadrPredictResultsListTop1, destAccs, destMAEs, destRanges, 'Q')
		accRets+=accRet
		maeRets+=maeRet
		filesRet.append(destAccs), filesRet.append(destMAEs), filesRet.append(destRanges)

		return [filesRet, accRets, maeRets]

	def mergePrecision4ALL(self, trainYrsText, precisionListALL, factor):
		precisionXlsx = self.timeDir+trainYrsText+'_'+factor+'_ACC.xlsx'
		workbook = xlsxwriter.Workbook(precisionXlsx)
		myformat = workbook.add_format({'align':'center_across'})
		for p in precisionListALL:
			filename = p.split('/')[-1].split('.')[0][3:]
			print filename
			worksheet = workbook.add_worksheet(filename)
			rowcnt = 0
			for row in csv.reader(open(p), delimiter=','):
				worksheet.write_row(rowcnt,0,row,myformat)
				rowcnt+=1

		ret, header = '', ''
		if trainYrsText == 'SINGLE_MEAN':
			ret, header = self.sortPredictorPrecisionsInDiffTestSet(precisionListALL[:2])
		else:
			ret, header = self.sortPredictorPrecisionsInDiffTestSet(precisionListALL)

		# precision index
		precisionIndex = header.index('0~1.0')+1

		f1s2P,f1t3P,s2t3P,f1s2Ped,f1t3Ped,s2t3Ped = [],[],[],[],[],[]
		keys = ret.keys()
		for key in keys:
			# f1s2P, f1t3P, s2t3P, f1s2Ped, f1t3Ped, s2t3Ped
			f1s2P += ret[key]['f1s2P']
			f1t3P += ret[key]['f1t3P']
			s2t3P += ret[key]['s2t3P']
			f1s2Ped += ret[key]['f1s2Ped']
			f1t3Ped += ret[key]['f1t3Ped']
			s2t3Ped += ret[key]['s2t3Ped']

		summaryList = []
		prefix = ['f1s2P', 'f1t3P', 's2t3P', 'f1s2Ped', 'f1t3Ped', 's2t3Ped']
		worksheet = workbook.add_worksheet('PPed')
		print 'PPed'
		rowcnt, sortIndex = 0, 0
		for mylist in [f1s2P,f1t3P,s2t3P,f1s2Ped,f1t3Ped,s2t3Ped]:
			header[0]=prefix[sortIndex]
			worksheet.write_row(rowcnt,0,header,myformat)
			rowcnt+=1

			Tied, Smaller, Bigger = 0, 0, 0
			if sortIndex <= 2:
				Tied, Smaller, Bigger = self.comparePrecisionInDiffDataset4EachCourse(mylist, 'P', precisionIndex)

				mylist.sort(key=itemgetter(2,1,0), reverse=True)
			else:
				Tied, Smaller, Bigger = self.comparePrecisionInDiffDataset4EachCourse(mylist, 'Ped', precisionIndex)

				mylist.sort(key=itemgetter(4,3,0), reverse=True)

			tsum = Tied+Smaller+Bigger
			summaryList.append([Tied, Smaller, Bigger, tsum, format(float(Tied*1.0/tsum), '.3f'), format(float(Smaller*1.0/tsum),'.3f'), format(float(Bigger*1.0/tsum), '.3f')])
			summaryList[sortIndex].insert(0, prefix[sortIndex])

			for row in mylist+[[''], ['Class', 'Tied', 'Smaller', 'Bigger', 'Total'], [prefix[sortIndex], Tied, Smaller, Bigger, tsum, format(float(Tied*1.0/tsum), '.3f'), format(float(Smaller*1.0/tsum),'.3f'), format(float(Bigger*1.0/tsum), '.3f')], ['']]:
				worksheet.write_row(rowcnt,0,row,myformat)
				rowcnt+=1

			# sortIndex = 0, 1, 2, sort for predictors; sortIndex = 3, 4, 5, sort for predicted courses
			sortIndex += 1

		summaryList.insert(3, ['Class', 'Tied', 'Smaller', 'Bigger', 'Total'])
		summaryList.insert(3, [''])
		summaryList.insert(0, ['Class', 'Tied', 'Smaller', 'Bigger', 'Total'])
		for x in summaryList:
			worksheet.write_row(rowcnt,0,x,myformat)
			rowcnt+=1
			print x

		print '\n'

	def comparePrecisionInDiffDataset4EachCourse(self, dataset, pped, precisionIndex):
		Tied, Smaller, Bigger = 0, 0, 0
		# pped: P: predictor; Ped: predicted courses
		crsIndex, numIndex = -1, -1
		if pped == 'P':
			crsIndex, numIndex = 1, 2
		elif pped == 'Ped':
			crsIndex, numIndex = 3, 4
		else:
			return

		crsDict = {}
		for rec in dataset:
			key = rec[crsIndex]+rec[numIndex]
			if key not in crsDict:
				crsDict[key] = [rec]
			else:
				crsDict[key].append(rec)

		for key, v in crsDict.items():
			v.sort(key=itemgetter(0), reverse=True)

			pair = []
			for x in xrange(0, len(v)-1):
				q=v[x][0][-1]
				# Q
				if q == 'Q':
					pair.append(v[x])
				# L
				else:
					pair.append(v[x])
					# pair found
					if v[x+1][0][-1] == 'Q':
						ret = self.precisionQLCmopare(pair, precisionIndex)
						if ret[1] == '+':
							Bigger += 1
						elif ret[1] == '-':
							Smaller += 1
						elif ret[1] == '#':
							Tied += 1
						# ===============================
						print ret[1]
						for rec in ret[0]:
							print rec
						print '\n'
						# ===============================
						pair = []

			pair.append(v[-1])
			ret = self.precisionQLCmopare(pair, precisionIndex)
			if ret[1] == '+':
				Bigger += 1
			elif ret[1] == '-':
				Smaller += 1
			elif ret[1] == '#':
				Tied += 1

			# ===============================
			print ret[1]
			for rec in ret[0]:
				print rec
			print '\n'
			# ===============================

		return [Tied, Smaller, Bigger]

	def precisionQLCmopare(self, pair, precisionIndex):
		setDict = {}
		for x in pair:
			# dataset in Q or L; key: L or Q
			key = x[0][-1]
			if key not in setDict:
				setDict[key] = [x]
			else:
				setDict[key].append(x)

		qMax, lMax = [], []
		for k in ['Q', 'L']:
			precisionList = []
			for x in setDict[k]:
				# remove duplicate precisions
				if float(x[precisionIndex]) not in precisionList:
					precisionList.append(float(x[precisionIndex]))

			# descendingly order
			precisionList.sort(reverse=True)
			if k == 'Q':
				[qMax.append(i) for i in precisionList]
			else:
				[lMax.append(i) for i in precisionList]

		# q precision, l precision
		qp, lp = '', ''
		if len(qMax) > 1:
			qp = qMax[1]
		else:
			qp = qMax[0]

		if len(lMax) > 1:
			lp = lMax[1]
		else:
			lp = lMax[0]

		if qp > lp:
			pair[-1] += ['+']
			return [pair, '+']
		elif qp < lp:
			pair[-1] += ['-']
			return [pair, '-']
		else:
			pair[-1] += ['#']
			return [pair, '#']

	def sortPredictorPrecisionsInDiffTestSet(self, precisionList):
		# f1s2P, f1t3P, s2t3P, f1s2Ped, f1t3Ped, s2t3Ped
		# datasetDict = {'2010': {'f1s2P': mylist, 'f1t3P': mylist, ......}}
		datasetDict, header = {}, ''
		for p in precisionList:
			filename = p.split('/')[-1].split('.')[0][3:]
			key, mydict = '', {}
			for row in csv.reader(open(p), delimiter=','):
				print row
				if (len(row) == 1) and (row[0] != ''):
					key = row[0]
				elif len(row) > 1:
					if (row[0] != 'xSubj'):
						row.insert(0, filename)
						if key not in mydict:
							mydict[key] = [row]
						else:
							mydict[key].append(row)
					else:
						row.insert(0, '')
						header = row
				elif len(row) == 0:
					print '========== ', key, ' =========='
					if key == 's2t3Ped':
						break

			datasetDict[filename] = mydict

		return [datasetDict, header]
