#!/usr/bin/env python

import csv, os, time, hashlib, shutil, xlsxwriter, copy as myCopy, matplotlib.pyplot as plt, numpy as np
from pylab import *
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.ticker import MultipleLocator
from scipy.stats import pearsonr, linregress, skew
from operator import itemgetter
from collections import Counter
import organizer, predictionCollector

import variables
comVars = variables.commonVariables()

class preprocessCurrentTrainingSet(object):
	"""docstring for filterCourseDataSets"""
	def __init__(self):
		super(preprocessCurrentTrainingSet, self).__init__()

	def preprocess(self, trainingSet):
		noDupRegFile = comVars.getCurrentTrainingSetNonDuplicateGradesFile(trainingSet)
		techCourseFile = comVars.getCurrentTrainingSetTechCourseFile(trainingSet)
		uniqueTechCourseFile = comVars.getCurrentTrainingSetNonDuplicateTechGradesFile(trainingSet)

		techsFile = comVars.getCurrentTrainingSetTechCourseFile(trainingSet)
		hearders = comVars.getCurrentTrainingSetHeader(trainingSet)
		self.createTechCourse(trainingSet, techsFile, hearders)
		self.createUniqueRegSAS(trainingSet, noDupRegFile)
		self.createUniqueRegSAS(techCourseFile, uniqueTechCourseFile)

		CRSPERSTU = comVars.getCurrentTrainingSetStudentEnrolmentFrequencyFile(trainingSet)
		STUREGISTERED = comVars.getCurrentTrainingSetCourseEnrolmentFrequencyFile(trainingSet)
		CRS_STU = comVars.getCurrentTrainingSetCourseStudentMatrixFileWithBlanks(trainingSet)
		CRS_STU_GRADE = comVars.getCurrentTrainingSetCourseStudentMatrixWithLetterGrades(trainingSet)
		STU_CRS = comVars.getCurrentTrainingSetStudentCourseMatrixFileWithBlanks(trainingSet)
		STU_CRS_GRADE = comVars.getCurrentTrainingSetStudentCourseMatrixWithoutBlanks(trainingSet)
		self.createSimpleStats(uniqueTechCourseFile, CRSPERSTU, STUREGISTERED, CRS_STU, CRS_STU_GRADE, STU_CRS, STU_CRS_GRADE)

		CRS_PAIRS = comVars.getCurrentTrainingSetCoursePairsFile(trainingSet)
		self.createCrspairs(CRS_PAIRS, CRS_STU)

		uniqueCourseFile = comVars.getCurrentTrainingSetUniqueCourseFile(trainingSet)
		uniqueTechCourseListFile = comVars.getCurrentTrainingSetUniqueTechCourseFile(trainingSet)
		self.createUniqueCourseList(noDupRegFile, uniqueCourseFile)
		self.createUniqueTechCrsList(trainingSet, uniqueCourseFile, uniqueTechCourseListFile)

		pearsonCorrFile = comVars.getCurrentTrainingSetCorrelationFile(trainingSet)
		skewnessFile = comVars.getCurrentTrainingSetSkewnessFile(trainingSet)
		self.createCorrelationFileAndPlots(trainingSet, CRS_STU, pearsonCorrFile, skewnessFile)

		filteredCorrFile = comVars.getCurrentTrainingSetCorrelationFileFilteredByPValue(trainingSet)
		self.createFilteredCorrelationFile(0.05, pearsonCorrFile, filteredCorrFile)

		# create predictor xlsx
		organizer.courseOrganizer(filteredCorrFile)

		# create predictor files
		self.createPredictorFiles(trainingSet)

		# compute simple stats for testing sets
		self.createCurrentTestingSetsSimpleStats(trainingSet)


	def createPredictorFiles(self, trainingSet):
		courseXCoefficientPredictorFile = comVars.getCurrentTrainingSetPredictorsFile(trainingSet, 'X', 'R')
		courseXEnrolmentPredictorFile = comVars.getCurrentTrainingSetPredictorsFile(trainingSet, 'X', '#')
		courseXPxyPredictorFile = comVars.getCurrentTrainingSetPredictorsFile(trainingSet, 'X', 'Pxy')

		courseYCoefficientPredictorFile = comVars.getCurrentTrainingSetPredictorsFile(trainingSet, 'Y', 'R')
		courseYEnrolmentPredictorFile = comVars.getCurrentTrainingSetPredictorsFile(trainingSet, 'Y', '#')
		courseYPxyPredictorFile = comVars.getCurrentTrainingSetPredictorsFile(trainingSet, 'Y', 'Pxy')

		# fetch predictors from both CourseX and CourseY
		pickListsX, pickListsY = organizer.pickedCoursePairList()
		enrolmentPredictorsX, coefficientPredictorsX, pxyPredictorsX = pickListsX
		enrolmentPredictorsY, coefficientPredictorsY, pxyPredictorsY = pickListsY
		print '****************************** Start: Predictors *******************************************'
		print 'enrolmentPredictorsX:', len(enrolmentPredictorsX)
		print '****************************** End: Predictors *********************************************'

		self.writePredictorsToFile(courseXCoefficientPredictorFile, [self.getCorrelationFileHeader()]+[row[0].split(' ')+row[1].split(' ')+row[2:] for row in coefficientPredictorsX])
		self.writePredictorsToFile(courseXEnrolmentPredictorFile, [self.getCorrelationFileHeader()]+[row[0].split(' ')+row[1].split(' ')+row[2:] for row in enrolmentPredictorsX])
		self.writePredictorsToFile(courseXPxyPredictorFile, [self.getCorrelationFileHeader()]+[row[0].split(' ')+row[1].split(' ')+row[2:] for row in pxyPredictorsX])

		self.writePredictorsToFile(courseYCoefficientPredictorFile, [self.getCorrelationFileHeader()]+[row[0].split(' ')+row[1].split(' ')+row[2:] for row in coefficientPredictorsY])
		self.writePredictorsToFile(courseYEnrolmentPredictorFile, [self.getCorrelationFileHeader()]+[row[0].split(' ')+row[1].split(' ')+row[2:] for row in enrolmentPredictorsY])
		self.writePredictorsToFile(courseYPxyPredictorFile, [self.getCorrelationFileHeader()]+[row[0].split(' ')+row[1].split(' ')+row[2:] for row in pxyPredictorsY])


	def writePredictorsToFile(self, file, rows):
		with open(file, 'w') as csvfile:
		    spamwriter = csv.writer(csvfile)
		    spamwriter.writerows(rows)

	def getCorrelationFileHeader(self):
		return ['xsubCode','xnum','ysubCode','ynum','coefficient','#points','pValue','stderr','slope','intercept','a','b','c','R^2','xmin','xmax']

	def createUniqueRegSAS(self, trainingSet, noDupRegFile):
		r, w = csv.reader(open(trainingSet), delimiter=','), csv.writer(open(noDupRegFile, 'w'))
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

	def createTechCourse(self, regData, techsFile, hearders):
		allTechData = comVars.getAllTechCursesFromSchedules()
		techWrter = csv.writer(open(techsFile, 'w'))
		techWrter.writerow(hearders)

		r = csv.reader(open(regData), delimiter=',')
		for row in r:
			course = row[3].replace(' ','')+row[4].replace(' ','')
			# change MATH 110 ===> MATH 133; ENGR 110 ===> ENGR 111
			if course == 'MATH110':
				row[4] = '133'

			if course == 'ENGR110':
				row[4] = '111'

			crs = row[3].replace(' ','')+row[4].replace(' ','')
			if crs in allTechData:
				techWrter.writerow(row)

	def createSimpleStats(self, noDupRegFile, CRSPERSTU, STUREGISTERED, CRS_STU, CRS_STU_GRADE, STU_CRS, STU_CRS_GRADE):
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

	def createUniqueCourseList(self, regNODUP, uniCourselist):
		reader = csv.reader(open(regNODUP), delimiter = ',')
		reader.next()
		freq = {}
		for row in reader:
			crs = row[3].replace(' ','')+row[4]
			if crs not in freq:
				freq[crs] = 1
			else:
				freq[crs] = freq[crs] + 1

		reader = csv.reader(open(regNODUP), delimiter = ',')
		reader.next()
		crsLst = []

		writer = csv.writer(open(uniCourselist, 'w'))
		writer.writerow(['SUBJECT_CODE', 'COURSE_NUMBER', 'FREQUENCY', 'YEAR'])
		for row in reader:
			crs = row[3].replace(' ','')+row[4]
			if (crs not in crsLst):
				crsLst.append(crs)
				writer.writerow([row[3].replace(' ', ''), row[4], freq[crs], row[4][0]])

	def createUniqueTechCrsList(self, trainingSet, uniCourselist, uniTechCrsList):
		techData = comVars.getCurrentTrainingSetAvailableTechCourses(trainingSet)
		creader, writer = csv.reader(open(uniCourselist), delimiter = ','), csv.writer(open(uniTechCrsList, 'w'))
		header = creader.next()
		writer.writerow(header)
		for row in creader:
			crs = row[0].replace(' ','')+row[1]
			if crs in techData:
				writer.writerow(row)

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

	def createCorrelationFileAndPlots(self, trainingSet, source, corr, skewness):
		reader = csv.reader(open(source), delimiter=',')
		header = reader.next()

		matrix = []
		for row in reader:
			matrix.append(row)

		wskew = csv.writer(open(skewness, 'w'))
		skewHeader = ['X1', 'X1', 'Y1', 'Y1', 'r','#','pValue','stderr','slope','intercept','a','b','c','R^2','xmin','xmax', 'skew1', 'skew2']
		wskew.writerow(skewHeader)

		w = csv.writer(open(corr, 'w'))
		w.writerow(['xsubCode','xnum','ysubCode','ynum','coefficient','#points','pValue','stderr','slope','intercept','a','b','c','R^2','xmin','xmax'])
		wnan = csv.writer(open(comVars.getCurrentTrainingSetNoCoefficientCourseFile(trainingSet), 'w'))

		cnt, nocorrDict, nocommstuDict = 0, {}, {}
		nocorrlst = comVars.getCurrentTrainingSetNoCorrelationCourseFile(trainingSet) # self.dataDir+'nocorr/no_corr_list.csv'
		nocommstulst = comVars.getCurrentTrainingSetNoCommonStudentCourseFile(trainingSet) # self.dataDir+'nocomstu/nocomstu_list.csv'
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
					# if source == self.crsMatrix:
					# 	xdata, ydata= map(float, course[3:]), map(float, newCourse[3:])
					# else:
					for index in xrange(2, len(course)):
						ix, iy = course[index], newCourse[index]
						if ix.isdigit() and iy.isdigit():
							xdata.append(float(ix)), ydata.append(float(iy))

					if len(xdata) == 0:
						cnt += 1
						nocommstuList.append(newCourse), nocomList.append([course[0]+' '+course[1], newCourse[0]+' '+newCourse[1]])
						# if self.proPredictor == 'ALL':
						print 'cnt:',cnt,'no common students course pair, len:',len(ydata),course[0],course[1],'vs',newCourse[0],newCourse[1],'trainYrs:',comVars.getCurrentTrainingSetTimeSlotString(trainingSet)
						 # else:
							#  print 'cnt:',cnt,'no common students course pair, len:',len(ydata),course[0],course[1],'vs',newCourse[0],newCourse[1]
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
						# if self.proPredictor == 'ALL':
						print 'cnt:',cnt,'no Pearson r course pair,', 'len:', len(ydata), course[0],course[1],'vs',newCourse[0],newCourse[1],'trainYrs:', comVars.getCurrentTrainingSetTimeSlotString(trainingSet)
						# else:
						# 	print 'cnt:',cnt,'no Pearson r course pair,', 'len:', len(ydata), course[0],course[1],'vs',newCourse[0],newCourse[1]
						wnan.writerows([[course[0]+course[1],newCourse[0]+newCourse[1],'len:',len(ydata)]]+[[course[0]+course[1]]+xdata]+[[newCourse[0]+newCourse[1]]+ydata]+[])
						continue

					# self.createBoxPlots([course[0], course[1]]+xdata, [newCourse[0], newCourse[1]]+ydata)
					# slope, intercept, r_value, p_value, std_err = linregress(xdata, ydata)
					# format the parameters precision
					slope, intercept, r_value, p_value, std_err = linregress(xl, yl)
					r, slope, intercept, r_value, p_value, std_err = [float(format(r, '.4f')), float(format(slope, '.4f')), float(format(intercept, '.4f')), float(format(r_value, '.4f')), float(format(p_value, '.4f')), float(format(std_err, '.4f'))]

					# r_value = float(format(r, '.4f'))
					slope, intercept = self.regressionPlot(xdata, ydata, r, 1, xaxis, yaxis, comVars.getCurrentTrainingSetLinearPlotsDirectory(trainingSet), len(ydata))
					a,b,c = self.regressionPlot(xdata, ydata, r, 2, xaxis, yaxis, comVars.getCurrentTrainingSetQuadraticPlotsDirectory(trainingSet), len(ydata))

					slope, intercept, a, b, c = [float(format(slope, '.4f')), float(format(intercept, '.4f')), float(format(a, '.4f')), float(format(b, '.4f')), float(format(c, '.4f'))]

					# if self.proPredictor == 'ALL':
					corrList.append([course[0],course[1],newCourse[0],newCourse[1],r,len(ydata),p_value,std_err,slope,intercept,a,b,c,float(format(r*r, '.4f')),min(xdata),max(xdata)])
					# else:
						# corrList.append([course[0], course[1], newCourse[0], newCourse[1], r, len(ydata), 0, p_value, std_err, slope, intercept, a, b, c, r*r, min(xdata), max(xdata)])

					rpSinglelist.append([course[0], course[1], newCourse[0], newCourse[1], r, len(ydata)])

					# if self.proPredictor == 'ALL':
					print 'cnt:', cnt, course[0], course[1], 'vs', newCourse[0], newCourse[1], 'len:', len(ydata), 'r:', r, 'r_value:', r_value, 'p_value:', p_value, 'p:', p, 'slope:', slope, 'trainYrs:', comVars.getCurrentTrainingSetTimeSlotString(trainingSet)
					# else:
					# 	print 'cnt:', cnt, course[0], course[1], 'vs', newCourse[0], newCourse[1], 'len:', len(ydata), 'r:', r, 'r_value:', r_value, 'p_value:', p_value, 'p:', p, 'slope:', slope

					# write skew to csv
					xskew, yskew  = float(format(skew(xdata, None, False), '.4f')), float(format(skew(ydata, None, False), '.4f'))
					wskew.writerow([course[0], course[1], newCourse[0], newCourse[1], r, len(ydata), p_value, std_err, slope, intercept, a, b, c, float(format(r*r, '.4f')), min(xdata), max(xdata), xskew, yskew])

			if len(noCorrList) > 0:
				# if not os.path.exists(self.dataDir+'nocorr/'):
				# 	os.makedirs(self.dataDir+'nocorr/')

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
				# if not os.path.exists(self.dataDir+'nocomstu/'):
				# 	os.makedirs(self.dataDir+'nocomstu/')

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
		# if self.proPredictor == 'ALL':
			# rlist, plist = [], []
			# for rec in rpSinglelist:
			# 	rlist.append(rec[4]), plist.append(rec[5])

			# self.coefficientPointsPlot(rlist, plist, comVars.getCurrentTrainingSetTimeSlotString(trainingSet), self.currDir+self.factor+'_RvsP.png')
		# else:
		# 	rpSinglelist.sort(key=itemgetter(0,1), reverse=False)
		# 	predictorDict = {}
		# 	for rec in rpSinglelist:
		# 		key = rec[0]+rec[1]
		# 		if key not in predictorDict:
		# 			predictorDict[key] = [rec]
		# 		else:
		# 			predictorDict[key].append(rec)

		# 	for key in predictorDict:
		# 		rlist, plist = [], []
		# 		for rec in predictorDict[key]:
		# 			rlist.append(rec[4]), plist.append(rec[5])

		# 		self.coefficientPointsPlot(rlist, plist, key, self.rpDir4Single+key+'_RvsP.png')

		# sort r records
		flist = [x for x in corrList if x[1][0] == '1']
		slist = [x for x in corrList if x[1][0] == '2']
		flist.sort(key=itemgetter(3), reverse=False)
		slist.sort(key=itemgetter(3), reverse=False)
		w.writerows(flist+slist)

		if len(nocorrDict) > 0:
			nocorr = comVars.getCurrentTrainingSetNoCorrelationCourseFrequencyFile(trainingSet) # self.dataDir+'nocorr/no_corr_list_fre.csv'
			wnocorr = csv.writer(open(nocorr, 'w'))
			wnocorr.writerow(['Course', '#Course'])
			wnocorr.writerows(nocorrDict.items())

		if len(nocommstuDict) > 0:
			nocommstu = comVars.getCurrentTrainingSetNoCommonStudentCourseFrequencyFile(trainingSet) # self.dataDir+'nocomstu/nocomstu_list_fre.csv'
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

	def createFilteredCorrelationFile(self, cutoff, originCorrFile, filteredCorrFile):
		reader = csv.reader(open(originCorrFile), delimiter = ',')
		header = reader.next()

		writer = csv.writer(open(filteredCorrFile, 'w'))
		writer.writerow(header)
		writer.writerows([row for row in reader if row[6] != 'nan' and float(row[6]) <= cutoff])

	# Testing Sets
	def createCurrentTestingSetsSimpleStats(self, trainingSet):
		testingSets = comVars.getCurrentTrainingSetTestingSets(trainingSet)
		for testingSet in testingSets:
			techsFile = comVars.getCurrentTestingSetTechCourseFile(trainingSet, testingSet)
			hearders = comVars.getCurrentTestingSetHeader(testingSet)
			uniqueTechCourseFile = comVars.getCurrentTestingSetUniqueTechCourseFile(trainingSet, testingSet)

			self.createTechCourse(testingSet, techsFile, hearders)
			self.createUniqueRegSAS(techsFile, uniqueTechCourseFile)

			CRSPERSTU = comVars.getCurrentTestingSetStudentEnrolmentFrequencyFile(trainingSet, testingSet)
			STUREGISTERED = comVars.getCurrentTestingSetCourseEnrolmentFrequencyFile(trainingSet, testingSet)
			CRS_STU = comVars.getCurrentTestingSetCourseStudentMatrixFileWithBlanks(trainingSet, testingSet)
			CRS_STU_GRADE = comVars.getCurrentTestingSetCourseStudentMatrixWithLetterGrades(trainingSet, testingSet)
			STU_CRS = comVars.getCurrentTestingSetStudentCourseMatrixFileWithBlanks(trainingSet, testingSet)
			STU_CRS_GRADE = comVars.getCurrentTestingSetStudentCourseMatrixWithoutBlanks(trainingSet, testingSet)
			self.createSimpleStats(uniqueTechCourseFile, CRSPERSTU, STUREGISTERED, CRS_STU, CRS_STU_GRADE, STU_CRS, STU_CRS_GRADE)

	def mergePredictionResults(self, trainingSet, factor, LinearQuadra):		
		xlsx = comVars.getCurrentTrainingSetMergedPredictionResultsFile(trainingSet, factor, LinearQuadra)
		workbook = xlsxwriter.Workbook(xlsx)
		myformat = workbook.add_format({'align':'center_across'})

		testingSets = comVars.getCurrentTrainingSetTestingSets(trainingSet)
		for courseXY in ['X', 'Y']:
			for testingSet in testingSets:
				testingTimeSlotString = comVars.getCurrentTestingSetTimeSlotString(testingSet)
				resultFile = comVars.getCurrentTestingSetPredictionResultFile(trainingSet, testingSet, courseXY, factor, LinearQuadra)
				r = csv.reader(open(resultFile), delimiter=',')
				cnt = 0
				worksheet = workbook.add_worksheet(testingTimeSlotString+factor+courseXY)
				for row in r:
					worksheet.write_row(cnt,0,row,myformat)
					cnt += 1
