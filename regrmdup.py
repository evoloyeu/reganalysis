import csv, sys, os, time, hashlib, shutil
from pylab import *
import matplotlib.pyplot as plt
from scipy.stats import pearsonr, linregress
import numpy as np
from operator import itemgetter
from collections import Counter
from random import randint

class splitRawData(object):
	"""docstring for splitRawData"""
	def __init__(self, arg):
		super(splitRawData, self).__init__()
		self.rawDeg, self.rawReg = arg[1], arg[2]

		pathList = self.rawDeg.split('/')
		degFilename, regFileName = self.rawDeg.split('/')[-1], self.rawReg.split('/')[-1]

		path = '/'
		for x in xrange(0,len(pathList[1:-2])):
			path = path + pathList[1:-1][x] + '/'

		path = path + 'users/splits_' + time.strftime('%Y%m%d') +'/'
		if not os.path.exists(path):
			os.makedirs(path)

		self.regFileList, self.degFileList = [], []
		self.yearList = ['2010', '2011', '2012', '2013', '2014', '2015']
		for yr in self.yearList:
			self.regFileList.append(path+'reg'+yr+'.csv')
			self.degFileList.append(path+'deg'+yr+'.csv')

		self.IDDict = self.degIDListByYr()

	def doBatch(self):
		for index in xrange(0, len(self.yearList)):
			self.groupRawData(self.rawDeg, self.degFileList[index], self.yearList[index])
			self.groupRawData(self.rawReg, self.regFileList[index], self.yearList[index])

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
				DegIDList10.append(deg[1])
			elif (graduateYr == '2011') and (not graduateYr in DegIDList11):
				DegIDList11.append(deg[1])
			elif (graduateYr == '2012') and (not graduateYr in DegIDList12):
				DegIDList12.append(deg[1])
			elif (graduateYr == '2013') and (not graduateYr in DegIDList13):
				DegIDList13.append(deg[1])
			elif (graduateYr == '2014') and (not graduateYr in DegIDList14):
				DegIDList14.append(deg[1])
			elif (graduateYr == '2015') and (not graduateYr in DegIDList15):
				DegIDList15.append(deg[1])

		return {'2010':DegIDList10, '2011':DegIDList11, '2012':DegIDList12, '2013':DegIDList13, '2014':DegIDList14, '2015':DegIDList15}

	def splitedRawData(self):
		return [self.regFileList, self.degFileList, self.yearList]

class prepross(object):
	def __init__(self, degRegFiles):
		super(prepross, self).__init__()
		self.trainYrsList = [['2010', '2011'],
		['2010', '2011', '2012'],
		['2010', '2011', '2012', '2013'],
		['2010', '2011', '2012', '2013', '2014']
		]
		# self.trainYrs = ['2010', '2011']
		self.threshold = 1
		self.regFileList, self.degFileList, self.yearList = degRegFiles
		rwList = [1.4,1.4,1.2,1.1]
		pwList = [1,1,1,1]
		self.wdict = {2:1.4, 3:1.4, 4:1.2, 5:1.1}

	def statsPath(self):
		pathList = self.regFileList[0].split('/')
		# degFilename, regFileName = pathList[-1], self.regDataPath.split('/')[-1]
		path = '/'
		for x in xrange(0,len(pathList[1:-2])):
			path = path + pathList[1:-1][x] + '/'

		# self.currDir = path + 'raw/' + time.strftime('%Y%m%d') + '/'
		self.currDir = path + time.strftime('%Y%m%d') + '_' + str(len(self.trainYrs)) + '/'
		if not os.path.exists(self.currDir):
			os.makedirs(self.currDir)

		# creat training data
		self.rheader, self.dheader = '', ''
		self.degDataPath = path+'splits_'+time.strftime('%Y%m%d')+'/degtrain'+self.trainYrs[0]+'-'+self.trainYrs[-1]+'_'+str(len(self.trainYrs))+'.csv'
		self.regDataPath = path+'splits_'+time.strftime('%Y%m%d')+'/regtrain'+self.trainYrs[0]+'-'+self.trainYrs[-1]+'_'+str(len(self.trainYrs))+'.csv'
		regFileName, degFilename = self.regDataPath.split('/')[-1], self.degDataPath.split('/')[-1]
		for yr in self.trainYrs:
			index = self.yearList.index(yr)
			reg, deg = self.regFileList[index], self.degFileList[index]
			self.concatenateData(reg, self.regDataPath, 'reg')
			self.concatenateData(deg, self.degDataPath, 'deg')

		self.techCrsFile = path + 'techcourses/' + 'TechCrs' + str(self.threshold) + '.csv'
		self.allTechCrs = path + 'techcourses/' + 'technicalCourse.csv'
		self.availableTechCrsList = []

		self.dataDir = self.currDir + 'data/'
		if not os.path.exists(self.dataDir+'Test/'):
			os.makedirs(self.dataDir+'Test/')

		self.errPlotsDir = self.currDir + 'errPlotsDir/'
		if not os.path.exists(self.errPlotsDir):
			os.makedirs(self.errPlotsDir)

		# for test reg data
		# store test data's noDup filenames
		self.fTestRegFileNameList = []
		# store stats filenames for all of the test data
		self.fTestStatFileNameList = []
		# store test filenames
		self.testFileList = [self.regDataPath]
		# create year combined test data
		combineYrsTestData = path + 'splits_'+time.strftime('%Y%m%d')+'/regtest'+ self.yearList[len(self.trainYrs)]+'-'+self.yearList[-1]+'_'+str(len(self.trainYrs))+'.csv'
		self.comYrsTestHeader = ''
		for yr in self.yearList:
			if (yr not in self.trainYrs):
				index = self.yearList.index(yr)
				reg = self.regFileList[index]
				self.testFileList.append(reg)
				if len(self.trainYrs) != 5:
					self.concatenateData(reg, combineYrsTestData, 'testCom')

		if len(self.trainYrs) != 5:
			self.testFileList.append(combineYrsTestData)

		# build test stats filenames and the predicting result and errors filenames
		self.linearPredictResultsList, self.linearPredictResultsAveErr, self.quadrPredictResultsList, self.quadrPredictResultsAveErr = [], [], [], []
		for fname in self.testFileList:
			filename = fname.split('/')[-1].split('.')[0]
			self.linearPredictResultsList.append(self.dataDir + 'fv1_predicting_grades_' + filename +'_linear.csv')
			self.linearPredictResultsAveErr.append(self.dataDir + 'fv1_predicting_aveErr_' + filename +'_linear.csv')
			self.quadrPredictResultsList.append(self.dataDir + 'fv1_predicting_grades_' + filename +'_quadr.csv')
			self.quadrPredictResultsAveErr.append(self.dataDir + 'fv1_predicting_aveErr_' + filename +'_quadr.csv')

			tmpList, prefix = [], ''
			if (fname == self.regDataPath) or (combineYrsTestData == fname):
				prefix = self.dataDir +'Test/' + filename
				self.fTestRegFileNameList.append(self.dataDir +'Test/' + filename + '_Test.csv')
			else:
				prefix = self.dataDir +'Test/' + filename[0:3] + 'test' + filename[3:]
				self.fTestRegFileNameList.append(self.dataDir +'Test/' + filename[0:3] + 'test' + filename[3:] + '_Test.csv')

			for item in ['CRSPERSTU', 'STUREGISTERED', 'EMPTY', 'CRS_STU', 'CRS_STU_GRADE', 'STU_CRS']:
				tmpList.append(prefix + '_' + item +'.csv')

			self.fTestStatFileNameList.append(tmpList)
			# self.CRSPERSTU, self.STUREGISTERED, self.EMPTY, self.CRS_STU, self.CRS_STU_GRADE, self.STU_CRS

		# predictor file path
		self.predictorFile = ''

		# others
		self.pairsFrequency, self.pairsHistDir = self.dataDir + 'pairsFrequency.csv', self.currDir + 'pairs_hist/'

		# self.corrAVEResults, self.corrORIResults = self.dataDir + 'corr_ave.csv', self.dataDir + 'corr_ori.csv'
		self.corrORIResults = self.dataDir + 'corr_ori.csv'
		self.fV1Reulsts = self.dataDir + 'fv1_ori_result.csv'
		# self.valAVE, self.valORI = self.dataDir + 'corr_ave_val.csv', self.dataDir + 'corr_ori_val.csv'

		folders = [self.linear_plots_ori, self.quadratic_plots_ori, self.coefficient_ori, self.hist_ori, self.bars_ori, self.course_ori] = [self.currDir + 'linear_plots_ori/', self.currDir + 'quadratic_plots_ori/', self.currDir + 'coefficient_ori/', self.currDir + 'hist_ori/', self.currDir + 'bars_ori/', self.currDir + 'course_ori/']

		for folder in folders:
			if not os.path.exists(folder):
				os.makedirs(folder)

		# REPL, NODUP, CRSPERSTU, STUREGISTERED, EMPTY, EMPTY_STU, EMPTY_CRS, CRS_STU, IDMAPPER
		fileNameList = []
		for x in xrange(0,17):
			fileNameList.append(self.dataDir)

		fileNameSuffix = ['REPL_SAS.csv', 'NODUP_SAS.csv', 'TECH_NODUP_SAS.csv', 'CRSPERSTU_SAS.csv', 'STUREGISTERED_SAS.csv', 'EMPTY_SAS.csv', 'EMPTY_STU_SAS.csv', 'EMPTY_CRS_SAS.csv', 'CRS_STU_SAS.csv', 'CRS_STU_GRADE_SAS.csv', 'NODUP_REPL_SAS.csv', 'STU_CRS_SAS.csv', 'CRS_MATRIX_SAS.csv', 'DISCARD_SAS.csv', 'uniCourseList.csv', 'uniTechCrsList.csv', 'TECH.csv']

		for x in xrange(0, len(regFileName.split('_'))-1):
			for indx in xrange(0,len(fileNameList)):
				fileNameList[indx] += regFileName.split('_')[x] + '_'

		for x in xrange(0,len(fileNameList)):
			fileNameList[x] += fileNameSuffix[x]

		[self.regREPL, self.regNODUP, self.techRegNODUP, self.CRSPERSTU, self.STUREGISTERED, self.EMPTY, self.EMPTY_STU, self.EMPTY_CRS, self.CRS_STU, self.CRS_STU_GRADE, self.regNODUPREPL, self.STU_CRS, self.crsMatrix, self.discardList, self.courselist, self.uniTechCrsList, self.techCrsCSV] = fileNameList

		self.degREPL = self.IDMAPPER = self.dataDir
		for x in xrange(0, len(degFilename.split('_'))-1):
			self.degREPL, self.IDMAPPER = self.degREPL + degFilename.split('_')[x] + '_', self.IDMAPPER + degFilename.split('_')[x] + '_'

		self.degREPL, self.IDMAPPER = self.degREPL + 'REPL_SAS.csv', self.IDMAPPER + 'IDMAPPER_SAS.csv'

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

	def doBatch(self):
		for yrList in self.trainYrsList:
			self.trainYrs = yrList
			self.statsPath()
			self.prepare()
			self.testWeights()
			self.predicting(self.wdict[len(self.trainYrs)], 1.0)

	def predicting(self, rw, pw):
		self.testSetsStats()
		# create predictors
		self.formulaV1(rw,pw)
		# predicting
		for x in xrange(0,len(self.fTestStatFileNameList)):
			self.predictProcess(self.fTestStatFileNameList[x][3], self.linearPredictResultsList[x], self.linearPredictResultsAveErr[x], 1)
			self.predictProcess(self.fTestStatFileNameList[x][3], self.quadrPredictResultsList[x], self.quadrPredictResultsAveErr[x], 2)

	def prepare(self):
		self.techCrs()
		self.formatRegSAS(self.regDataPath, self.regNODUP)
		self.formatRegSAS(self.techCrsCSV, self.techRegNODUP)

		self.simpleStats(self.techRegNODUP, self.CRSPERSTU, self.STUREGISTERED, self.EMPTY, self.CRS_STU, self.CRS_STU_GRADE, self.STU_CRS)
		self.pairs()
		self.pairsHists()

		self.uniqueCourseList()
		self.uniqueTechCrsList()

		# self.cryptID()
		self.techCrsHists()

		# compute correlation coefficients and draw correlation plots
		self.corrPlot(self.CRS_STU, self.corrORIResults)

	def testSetsStats(self):
		# compute the stats data for the test datasets
		for testFile in self.testFileList:
			index = self.testFileList.index(testFile)
			noDupFile = self.fTestRegFileNameList[index]
			self.formatRegSAS(testFile, noDupFile)

			statList = self.fTestStatFileNameList[index]
			self.simpleStats(noDupFile, statList[0], statList[1], statList[2], statList[3], statList[4], statList[5])

	def testWeights(self):
		# trying to find the good weights
		w1 = [1, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9, 2.0, 2.1, 2.2, 2.3, 2.4, 2.5]
		w2 = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
		self.formulaV1Integrate(w1,w2)

	def misc(self):
		self.coefficientHists(self.hist_ori, self.corrORIResults)
		self.groupPlots(self.linear_plots_ori, self.corrORIResults)
		self.plotsPickByCoefficient(1.0, self.corrORIResults)
		self.plotsPickByCoefficient(-1.0, self.corrORIResults)
		self.plotsPickByCoefficient(0.0, self.corrORIResults)

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
		# self.corrPlot(self.CRS_STU, self.linear_plots_ori, self.corrORIResults)

		# self.coefficientHists(self.hist_ori, self.corrORIResults)
		# self.groupPlots(self.linear_plots_ori, self.corrORIResults)
		# self.plotsPickByCoefficient(1.0, self.corrORIResults)
		# self.plotsPickByCoefficient(-1.0, self.corrORIResults)
		# self.plotsPickByCoefficient(0.0, self.corrORIResults)

	def groupPlots(self, fromDir, corr):
		todir = self.currDir + 'groups/'
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
		toDir = self.currDir + 'groups/' + str(coefficient)
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
			self.validation(self.corrORIResults, 'ori', x)

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

	def simpleStats(self, noDupRegFile, CRSPERSTU, STUREGISTERED, EMPTY, CRS_STU, CRS_STU_GRADE, STU_CRS):
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
				if cell[0] == reg[1] and cell[1] == reg[2]:
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
		# header: [v_num, crs1, crs2, ......]
		header = ['V_NUMBER']
		for crs in distinctCRSLst:
			header.append(crs)
		w.writerow(header)

		# init rows
		rowLst = []
		for stu in distinctSTULst:
			# row: [v_num, 'NA', 'NA', ......]
			row = [stu]
			for y in xrange(0,len(distinctCRSLst)):
				# row.append('NA')
				row.append('')

			rowLst.append(row)

		# fill course grade point for each course		
		for row in rowLst:
			for reg in regLst:
				# row: [v_num, 'NA', 'NA', ......]
				# reg: [v_num, subj_code, course_code, grade_point, grade_notation]
				if row[0] == reg[0]:
					index = distinctCRSLst.index(reg[1] + reg[2])
					row[index+1] = reg[3]

			w.writerow(row)

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
		if source == self.crsMatrix:
			reader.next()

		header = reader.next()

		matrix = []
		for row in reader:
			cnt, items = 0, []
			if source == self.crsMatrix:
				items = row[3:]
			else:
				items = row[2:]

			for item in items:
				if item.isdigit() and float(item) < 10:
					cnt = cnt + 1
			if cnt >= self.threshold:
				matrix.append(row)

		w = csv.writer(open(corr, 'w'))
		w.writerow(['xsubCode', 'xnum', 'ysubCode', 'ynum', 'coefficient', '#points', 'pValue', 'stderr', 'slope', 'intercept', 'a', 'b', 'c'])

		cnt, nocorrDict, nocommstuDict = 0, {}, {}
		nocorrlst = self.dataDir + 'nocorr/' + 'no_corr_list.csv'
		nocommstulst = self.dataDir + 'nocomstu/' + 'nocomstu_list.csv'
		wnocorrlst, wnocommstulst, nocomList, noCorrListTable = '', '', [], []

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
					xaxis, yaxis = course[0] + ' ' + course[1] + ' Grades', newCourse[0] + ' ' + newCourse[1] + ' Grades'

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
							nocomList.append([course[0] + ' ' + course[1], newCourse[0] + ' ' + newCourse[1]])
							continue

					(r, p) = pearsonr(xdata, ydata)
					if str(r) == 'nan':
						noCorrList.append(newCourse)
						cnt += 1
						continue

					slope, intercept, r_value, p_value, std_err = linregress(xdata, ydata)
					# format the parameters precision
					slope, intercept, r_value, p_value, std_err = linregress(xdata, ydata)
					r, slope, intercept, r_value, p_value, std_err = [float(format(r, '.4f')), float(format(slope, '.4f')), float(format(intercept, '.4f')), float(format(r_value, '.4f')), float(format(p_value, '.4f')), float(format(std_err, '.4f'))]

					r_value = float(format(r, '.4f'))
					slope, intercept = self.regressionPlot(xdata, ydata, r_value, 1, xaxis, yaxis, self.linear_plots_ori)
					a,b,c = self.regressionPlot(xdata, ydata, r_value, 2, xaxis, yaxis, self.quadratic_plots_ori)

					slope, intercept, a, b, c = [float(format(slope, '.4f')), float(format(intercept, '.4f')), float(format(a, '.4f')), float(format(b, '.4f')), float(format(c, '.4f'))]

					w.writerow([course[0], course[1], newCourse[0], newCourse[1], r, len(ydata), p_value, std_err, slope, intercept, a, b, c])
					print 'cnt: ', cnt, '\t', course[0], course[1], ' vs ', newCourse[0], newCourse[1], '\t\tlen: ', len(ydata), '\tr: ', r, '\tr_value:', r_value, '\tslope: ', slope

			if len(noCorrList) > 0:
				if not os.path.exists(self.dataDir + 'nocorr/'):
					os.makedirs(self.dataDir + 'nocorr/')

				nocorrDict[course[0] + course[1]] = len(noCorrList)
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
				if not os.path.exists(self.dataDir + 'nocomstu/'):
					os.makedirs(self.dataDir + 'nocomstu/')

				nocommstuDict[course[0] + course[1]] = len(nocommstuList)
				nocommstuList.insert(0, course)

				if wnocommstulst == '':
					wnocommstulst = csv.writer(open(nocommstulst, 'w'))
				wnocommstulst.writerows(nocommstuList)
				wnocommstulst.writerow([])

				wnocommstulst.writerow(['COURSE_1', 'COURSE_2'])
				wnocommstulst.writerow([course[0] + course[1], nocommstuList[1][0] + nocommstuList[1][1]])
				for indx in xrange(2,len(nocommstuList)):
					wnocommstulst.writerow(['', nocommstuList[indx][0] + nocommstuList[indx][1]])
				wnocommstulst.writerow([])

		if len(nocorrDict) > 0:
			nocorr = self.dataDir + 'nocorr/' + 'no_corr_list_fre.csv'
			wnocorr = csv.writer(open(nocorr, 'w'))
			wnocorr.writerow(['Course', '#Course'])
			wnocorr.writerows(nocorrDict.items())

		if len(nocommstuDict) > 0:
			nocommstu = self.dataDir + 'nocomstu/' + 'nocomstu_list_fre.csv'
			wnocom = csv.writer(open(nocommstu, 'w'))
			wnocom.writerow(['Course', '#Course'])
			wnocom.writerows(nocommstuDict.items())

		wnocorrlst.writerows(noCorrListTable)

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

	def regressionPlot(self, xdata, ydata, r_value, power, xaxis, yaxis, plotDir):
		fig = plt.figure()
		xarray = np.array(xdata)
		yarray = np.array(ydata)
		z = np.polyfit(xarray, yarray, power)
		p = np.poly1d(z)

		if power == 1:
			slope, intercept = z
			slope, intercept = [float(format(slope, '.4f')), float(format(intercept, '.4f'))]
			if r_value != 0.0:
				if intercept > 0:
					# plt.title(r'$r = $' + str(r_value) + r'$, y = $' + str(slope) + r'$x+$'+ str(intercept))
					plt.title(r'$r=%s,y=%sx+%s$'%(r_value, slope, intercept))
				elif intercept < 0:
					# plt.title(r'$r = $' + str(r_value) + r'$, y = $' + str(slope) + r'$x$' + str(intercept))
					plt.title(r'$r=%s,y=%sx%s$'%(r_value, slope, intercept))
				else:
					plt.title(r'$r=%s,y=%sx$'%(r_value, slope))
			else:
				# plt.title(r'$r = $' + str(r_value) + r'$, y = $' + str(intercept))
				plt.title(r'$r=%s,y=%s$'%(r_value, intercept))
		elif power == 2:
			a, b, c = z
			a, b, c = [float(format(a, '.4f')), float(format(b, '.4f')), float(format(c, '.4f'))]
			if a == 0:
				if b > 0:
					if c > 0:
						# plt.title(r'$r=$' + str(r_value) + r'$, y = $' + str(a) + r'$x^2$' + r'$+$' + str(b) + r'$x$' + r'$+$' + str(c))
						plt.title(r'$r=%s,y=%sx+%s$'%(r_value, b, c))
					elif c < 0:
						# plt.title(r'$r = $' + str(r_value) + r'$, y = $' + str(a) + r'$x^2$' + r'$+$' + str(b) + r'$x$' + str(c))
						plt.title(r'$r=%s,y=%sx%s$'%(r_value, b, c))
					else:
						# plt.title(r'$r = $' + str(r_value) + r'$, y = $' + str(a) + r'$x^2$' + r'$+$' + str(b))
						plt.title(r'$r=%s,y=%sx$'%(r_value, b))
				elif b < 0:
					if c > 0:
						# plt.title(r'$r=$' + str(r_value) + r'$, y = $' + str(a) + r'$x^2$' + r'$+$' + str(b) + r'$x$' + r'$+$' + str(c))
						plt.title(r'$r=%s,y=%sx+%s$'%(r_value, b, c))
					elif c < 0:
						# plt.title(r'$r = $' + str(r_value) + r'$, y = $' + str(a) + r'$x^2$' + r'$+$' + str(b) + r'$x$' + str(c))
						plt.title(r'$r=%s,y=%sx%s$'%(r_value, b, c))
					else:
						# plt.title(r'$r = $' + str(r_value) + r'$, y = $' + str(a) + r'$x^2$' + r'$+$' + str(b))
						plt.title(r'$r=%s,y=%sx$'%(r_value, b))
				else:
					if c > 0:
						# plt.title(r'$r=$' + str(r_value) + r'$, y = $' + str(a) + r'$x^2$' + r'$+$' + str(b) + r'$x$' + r'$+$' + str(c))
						plt.title(r'$r=%s,y=%s$'%(r_value, c))
					elif c < 0:
						# plt.title(r'$r = $' + str(r_value) + r'$, y = $' + str(a) + r'$x^2$' + r'$+$' + str(b) + r'$x$' + str(c))
						plt.title(r'$r=%s,y=%s$'%(r_value, c))
					# else:
						# plt.title(r'$r = $' + str(r_value) + r'$, y = $' + str(a) + r'$x^2$' + r'$+$' + str(b))
						# plt.title(r'$r=%s,x=%s$'%(r_value))
			else:
				if b > 0:
					if c > 0:
						# plt.title(r'$r=$' + str(r_value) + r'$, y = $' + str(a) + r'$x^2$' + r'$+$' + str(b) + r'$x$' + r'$+$' + str(c))
						plt.title(r'$r=%s,y=%sx^2+%sx+%s$'%(r_value, a, b, c))
					elif c < 0:
						# plt.title(r'$r = $' + str(r_value) + r'$, y = $' + str(a) + r'$x^2$' + r'$+$' + str(b) + r'$x$' + str(c))
						plt.title(r'$r=%s,y=%sx^2+%sx%s$'%(r_value, a, b, c))
					else:
						# plt.title(r'$r = $' + str(r_value) + r'$, y = $' + str(a) + r'$x^2$' + r'$+$' + str(b))
						plt.title(r'$r=%s,y=%sx^2+%sx$'%(r_value, a, b))
				elif b < 0:
					if c > 0:
						# plt.title(r'$r=$' + str(r_value) + r'$, y = $' + str(a) + r'$x^2$' + r'$+$' + str(b) + r'$x$' + r'$+$' + str(c))
						plt.title(r'$r=%s,y=%sx^2%sx+%s$'%(r_value, a, b, c))
					elif c < 0:
						# plt.title(r'$r = $' + str(r_value) + r'$, y = $' + str(a) + r'$x^2$' + r'$+$' + str(b) + r'$x$' + str(c))
						plt.title(r'$r=%s,y=%sx^2%sx%s$'%(r_value, a, b, c))
					else:
						# plt.title(r'$r = $' + str(r_value) + r'$, y = $' + str(a) + r'$x^2$' + r'$+$' + str(b))
						plt.title(r'$r=%s,y=%sx^2%sx$'%(r_value, a, b))
				else:
					if c > 0:
						# plt.title(r'$r=$' + str(r_value) + r'$, y = $' + str(a) + r'$x^2$' + r'$+$' + str(b) + r'$x$' + r'$+$' + str(c))
						plt.title(r'$r=%s,y=%sx^2+%s$'%(r_value, a, c))
					elif c < 0:
						# plt.title(r'$r = $' + str(r_value) + r'$, y = $' + str(a) + r'$x^2$' + r'$+$' + str(b) + r'$x$' + str(c))
						plt.title(r'$r=%s,y=%sx^2%s$'%(r_value, a, c))
					else:
						# plt.title(r'$r = $' + str(r_value) + r'$, y = $' + str(a) + r'$x^2$' + r'$+$' + str(b))
						plt.title(r'$r=%s,y=%sx^2$'%(r_value, a))

		xp = np.linspace(0, 9, 100)
		plt.plot(xarray, yarray, '.', xp, p(xp), '-')

		plt.xlabel(xaxis)
		plt.ylabel(yaxis)

		plt.ylim(0,9)
		plt.grid(True)

		subj, num = xaxis.split(' ')[:2]
		subjNew, numNew = yaxis.split(' ')[:2]
		figName = plotDir + subj + num + ' ' + subjNew + numNew + ' ' + str(r_value) + '.png'
		fig.savefig(figName)
		plt.close(fig)

		return z

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
		figPath = self.currDir + 'crs_hist/'
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
		plt.title('Histogram of students with Bin = ' + str(interval), fontsize='large')
		plt.xlabel('Number of students who registered the technical course')
		plt.ylabel('Frequency')
		plt.grid(True)
		
		# bins = [ int(bins[i]) for i in range(len(bins)) ]
		n, bins, patches = plt.hist(x, bins, normed=0, histtype='bar')

		figName = figPath + 'registered_Fre_hist_' + 'interval_' + str(interval) + '.png'
		fig.savefig(figName)
		# plt.show()
		plt.close(fig)

	def pairs(self):
		reader = csv.reader(open(self.CRS_STU), delimiter = ',')
		reader.next()
		matrix = []
		for row in reader:
			matrix.append(row)

		w = csv.writer(open(self.pairsFrequency, 'w'))
		w.writerow(['xcode', 'xnum', 'ycode', 'ynum', 'pairs'])

		for x in matrix:
			for y in matrix:
				if int(x[1][0]) < int(y[1][0]) and int(x[1][0]) < 3:
					cnt = 0
					for index in xrange(2,len(x)):
						if x[index].isdigit() and y[index].isdigit():
							cnt = cnt + 1
					# print x[0], ' ', x[1], ' vs ', y[0], ' ', y[1], ' cnt: ', cnt
					w.writerow([x[0], x[1], y[0], y[1], cnt])

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
		reader = csv.reader(open(self.corrORIResults), delimiter=',')
		header = reader.next()
		rows = []
		for row in reader:
			row[4] = float(row[4])
			rows.append(row)

		rows.sort(key=itemgetter(2,3,4,5), reverse=True)

		fV1Reulsts = self.dataDir + 'fv1_' + str(w1) + '_' + str(w2) +'.csv'
		writer = csv.writer(open(fV1Reulsts, 'w'))
		# build the self.predictorFile
		self.predictorFile = self.dataDir + 'predictors_' + str(w1) + '_' + str(w2) +'.csv'
		eqw = csv.writer(open(self.predictorFile, 'w'))

		header.insert(6, str(w1) + '_' + str(w2))
		eqw.writerow(header)

		ylist, rlist, plist = [], [], []
		for x in xrange(0,len(rows)):
			ylist.append(rows[x])

			r = float(rows[x][4])
			if r < 0:
				rlist.append(r*(-1.0))
			else:
				rlist.append(r)

			plist.append(float(rows[x][5]))

			if x < (len(rows)-1):
				if (rows[x][2]+rows[x][3]) != (rows[x+1][2]+rows[x+1][3]):
					writer.writerow(header)
					ylist, predictorList = self.PxyPredictors(ylist, rlist, plist, w1, w2)
					writer.writerows(ylist)
					writer.writerow([])

					eqw.writerows(predictorList)

					ylist, rlist, plist = [], [], []

		if (len(ylist) == len(rlist)) and (len(ylist) == len(plist)) and (len(ylist) > 0):
			writer.writerow(header)
			ylist, predictorList = self.PxyPredictors(ylist, rlist, plist, w1, w2)
			writer.writerows(ylist)

			eqw.writerows(predictorList)

			ylist, rlist, plist = [], [], []

	def PxyPredictors(self, ylist, rlist, plist, w1, w2):
		pxyArr, predictorList = [], []
		for sublist in ylist:
			r = float(sublist[4])
			if r < 0:
				pxy = w1*float(sublist[4])*(-1.0)/float(max(rlist))+w2*float(sublist[5])/float(max(plist))
			else:
				pxy = w1*float(sublist[4])/float(max(rlist))+w2*float(sublist[5])/float(max(plist))

			pxy = format(pxy, '.4f')
			pxyArr.append(pxy)
			sublist.insert(6, pxy)

		# search the predictor course
		maxPxy = max(pxyArr)
		freq = Counter(item for item in pxyArr)
		# there is only one maximun pxy
		if freq[maxPxy] == 1:
			index = pxyArr.index(maxPxy)			
			predictorList.append(ylist[index])
		else:
			xCrsNums, maxPxyList = [], []
			for sublist in ylist:
				if sublist[6] == maxPxy:
					maxPxyList.append(sublist)
					xCrsNums.append(sublist[1][0:-1])

			mincrsnum = min(xCrsNums)
			index = xCrsNums.index(mincrsnum)
			predictorList.append(maxPxyList[index])

		return [ylist, predictorList]

	def formulaV1Integrate(self, w1list, w2list):
		reader = csv.reader(open(self.corrORIResults), delimiter=',')
		header = reader.next()
		rows = []
		for row in reader:
			row[4] = float(row[4])
			rows.append(row[0:6])

		rows.sort(key=itemgetter(2,3,4,5), reverse=True)

		fV1Reulsts = self.dataDir + 'fv1_w1_w2.csv'
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

	def predictProcess(self, testReg, predictResults, aveErrResults, power):
		# build equation/predictor dict
		r1 = csv.reader(open(self.predictorFile), delimiter=',')
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
		predictingList, keys = [], predictorDict.keys()
		for key in keys:
			if key in testRegDict:
				testY, testXs, predictors = testRegDict[key], [], predictorDict[key]
				for x in predictors:
					testXKey = x[0]+x[1]
					if testXKey in testRegDict:
						testXs.append(testRegDict[testXKey])

				# have located the predictable course pairs stored in pairsList
				pairsList = self.gradePairs(testY, testXs)
				if len(pairsList) > 0:
					predictingList.append(pairsList)

		# predict
		writer = csv.writer(open(predictResults, 'w'))
		errw = csv.writer(open(aveErrResults, 'w'))
		errw.writerow(['aveErr', 'r', '#point'])
		# [errorave, coefficient, pointFreq]
		AERPList, errRangeStdErrList, pointsList, rList, aveAbsErrList = [], [], [], [], []
		# [xsubj, xNum, ySubj, yNum, sample Point#, r, std, mean of err, mean absolute err, test instance#, minErr, maxErr, internal]
		header = ['xSubj', 'xNum', 'ySubj', 'yNum', 'point#', 'r', 'std', 'ME', 'MAE', 'MAPE', 'insOneCrs', 'minErr', 'maxErr', 'interval']
		errRangeStdErrList.append(header)

		for pairsList in predictingList:
			for pairs in pairsList:
				[xgrades, ygrades] = pairs
				# locate predicting equation; key: predicting course
				key = ygrades[0] + ygrades[1]
				predictors = predictorDict[key]
				# linear: y = slope * x + intercept
				# quadratic: y = ax^2+bx+c
				slope = intercept = coefficient = pointFreq = xSubj = xNum = ySubj = yNum = 0
				for predictor in predictors:
					xcourse, predictorCourse = xgrades[0] + xgrades[1], predictor[0] + predictor[1]
					if xcourse == predictorCourse:
						# !!!caution: for the index
						xSubj,xNum,ySubj,yNum, coefficient,pointFreq = predictor[0], predictor[1], predictor[2], predictor[3], predictor[4], predictor[5]
						slope,intercept,a,b,c = predictor[9], predictor[10], predictor[11], predictor[12], predictor[13]
						pointsList.append(int(pointFreq))
						rList.append(float(coefficient))
						# compute errors: aesum: absolute err sum; aepsum: absolute err percent sum
						errorList, absErrPerList, aesum, aepsum = [], [], 0, 0
						# compute predicting grade of testY using the equation located above
						predictGrades = [ygrades[0], ygrades[1]]
						for index in xrange(2, len(xgrades)):
							x, grade = xgrades[index], 0
							if power == 1:
								grade = float(slope) * float(x) + float(intercept)
							if power == 2:
								grade = float(a)*pow(float(x), 2)+float(b)*float(x)+float(c)

							grade = float(format(grade, '.1f'))
							predictGrades.append(grade)
							# fetch the actual grade from ygrades list
							actualGrade = float(ygrades[index])
							# calculate predicting err
							error = actualGrade - grade

							errorList.append(error)
							aesum += abs(error)

							absErrPer = 0 
							if actualGrade == 0:
								absErrPer = abs(error)/1
							else:
								absErrPer = abs(error)/actualGrade

							aepsum += absErrPer
							absErrPerList.append(str(format(absErrPer*100, '.2f'))+'%')

						mae = format(aesum/len(errorList), '.2f')
						aveAbsErrList.append(float(mae))

						mape = format(aepsum/len(errorList), '.2f')

						errArr = np.array(errorList)
						errorave = format(np.average(errArr), '.2f')
						std = format(np.std(errArr), '.2f')

						tempList = [xSubj,xNum,ySubj,yNum,pointFreq,coefficient,std,errorave,mae,mape,len(errorList),min(errorList),max(errorList), max(errorList)-min(errorList)]
						for error in errorList:
							tempList.append(error)
						
						errRangeStdErrList.append(tempList)

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

						writer.writerows([xgrades, ygrades, predictGrades, errorList, absErrPerList, appendix, []])
						errw.writerow([errorave, coefficient, pointFreq])
						AERPList.append([errorave, coefficient, pointFreq])

						# print xgrades, '\n', ygrades, '\n', predictGrades, '\n', errorList, '\n', absErrPerList, '\n'

		writer.writerows(errRangeStdErrList)

		prefix = testReg.split('/')[-1].split('_')[0]
		suffix = ''
		if power == 1:
			suffix = 'linear'
		elif power == 2:
			suffix = 'quadratic'		
		# points vs aveAbsErr
		xtitle = 'sample points from training set '+self.trainYrs[0]+'-'+self.trainYrs[-1]
		ytitle = 'average of absolute error from ' + prefix[3:]
		title = 'points vs average of absolute errors ('+suffix+')'
		figName = self.errPlotsDir+prefix[3:]+'_point_aveAbsErr_'+suffix+'.png'
		self.errScatter(xtitle, ytitle, title, pointsList, aveAbsErrList, figName, 'p')

		# r vs aveAbsErr
		xtitle = 'coefficients from training set '+self.trainYrs[0]+'-'+self.trainYrs[-1]
		ytitle = 'average of absolute error from '+prefix[3:]
		title = 'coefficients vs average of absolute errors ('+suffix+')'
		figName = self.errPlotsDir+prefix[3:]+'_r_aveAbsErr_'+suffix+'.png'
		self.errScatter(xtitle, ytitle, title, rList, aveAbsErrList, figName, 'r')

	def gradePairs(self, testY, testXs):
		resultPairs, pairsList, xCrsNums = [], [], []
		for x in testXs:
			# build the xgrades, ygrades lists
			xgrades = [x[0], x[1]]
			ygrades = [testY[0], testY[1]]
			for index in xrange(2,len(testY)):
				if x[index].isdigit() and testY[index].isdigit():
					xgrades.append(x[index])
					ygrades.append(testY[index])

			# to see if there are at least one pair between xgrades and ygrades
			if len(xgrades) > 2:
				pairsList.append([xgrades, ygrades])
				# save course number for later predictor pickup
				xCrsNums.append(x[1][0:-1])

		if len(pairsList) > 1:
			# randomIndex = randint(0,len(pairsList)-1)
			# return [pairsList[randomIndex]]
			# to pick up the course with min course number as the predictor
			mincrsnum = min(xCrsNums)
			index = xCrsNums.index(mincrsnum)
			resultPairs.append(pairsList[index])
		else:
			resultPairs = pairsList

		return resultPairs

	def errScatter(self, xtitle, ytitle, title, xdata, ydata, figName, flag):
		x = np.array(xdata)
		y = np.array(ydata)

		fig = plt.figure()
		plt.plot(x, y, '.', c='red')
		plt.xlabel(xtitle)
		plt.ylabel(ytitle)
		plt.title(title)

		# plt.ylim(min(ydata), max(ydata)+0.5)
		plt.ylim(0, 15)
		if flag == 'r':
			plt.xlim(-1.0, 1.0)
			ticks = np.linspace(-1.0, 1.0, 20, endpoint=False).tolist()
			ticks.append(1.0)
			plt.xticks(ticks, rotation=20, fontsize='medium')			
		if flag == 'p':
			# plt.xlim(min(xdata), max(xdata)+5)
			plt.xlim(0, 120)
			# ticks = xrange(0, max(xdata)+5, 5)
			ticks = xrange(0, 120, 10)
			plt.xticks(ticks)

		plt.grid(True)
		# plt.show()
		fig.savefig(figName)
		plt.close(fig)

prepare = splitRawData(sys.argv)
prepare.doBatch()
prepross(prepare.splitedRawData()).doBatch()
