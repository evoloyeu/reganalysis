import csv, sys, os, time, hashlib, shutil
from pylab import *
import matplotlib.pyplot as plt
from scipy.stats import pearsonr, linregress
import numpy as np
from operator import itemgetter
from collections import Counter

class prepross(object):
	def __init__(self, arg):
		super(prepross, self).__init__()
		self.arg = arg
		self.degDataPath = arg[1]
		self.regDataPath = arg[2]

	def doBatch(self):
		self.flows()		

	def flows(self):
		for x in xrange(1,2):
			self.threshold = x
			self.statsPath()			
			self.flow()
			self.cryptID()
			self.techCrsHists()

	def flow(self):
		self.techCrs()
		self.formatRegSAS(self.regDataPath, self.regNODUP)
		self.formatRegSAS(self.techCrsCSV, self.techRegNODUP)
		
		self.simpleStats(self.techRegNODUP)
		self.pairs()
		self.pairsHists()

		self.uniqueCourseList()

		self.crsStuMatrix()
		# compute correlation coefficients and draw correlation plots
		self.corrPlot(self.CRS_STU, self.plots_ori, self.corrORIResults)
		# self.validation(self.corrORIResults, 'ori', 0.60)
		# self.validation(self.corrORIResults, 'ori', 0.65)
		# self.validation(self.corrORIResults, 'ori', 0.70)

		# self.corrPlot(self.crsMatrix, self.plots_ave, self.corrAVEResults)
		# self.validation(self.corrAVEResults, 'ave', 0.60)
		# self.validation(self.corrAVEResults, 'ave', 0.65)
		# self.validation(self.corrAVEResults, 'ave', 0.70)
		# self.validation(self.corrAVEResults, 'ave', 0.75)
		
		self.groupPlots(self.plots_ori, self.course_ori, self.corrORIResults)
		# self.groupPlots(self.plots_ave, self.course_ave, self.corrAVEResults)

		self.courseBarPlots(self.bars_ori, self.corrORIResults)
		# self.courseBarPlots(self.bars_ave, self.corrAVEResults)
		self.studentBarPlots(self.techRegNODUP)

		self.pickupFigures(self.plots_ori, self.coefficient_ori, self.corrORIResults)
		# self.pickupFigures(self.plots_ave, self.coefficient_ave, self.corrAVEResults)

		self.coefficientHists(self.hist_ori, self.corrORIResults)
		# self.coefficientHists(self.hist_ave, self.corrAVEResults)

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

	def statsPath(self):
		pathList = self.degDataPath.split('/')
		degFilename = pathList[-1]
		regFileName = self.regDataPath.split('/')[-1]

		path = '/'
		for x in xrange(0,len(pathList[1:-1])):
			path = path + pathList[1:-1][x] + '/'


		self.techCrsFile = path + 'techcourses/' + 'TechCrs' + str(self.threshold) + '.csv'
		self.allTechCrs = path + 'techcourses/' + 'allTechCrs.csv'

		self.currDir = path + 'raw/' + time.strftime('%Y%m%d') + '/threshold_' + str(self.threshold) + '/'
		if not os.path.exists(self.currDir):
			os.makedirs(self.currDir)
		
		self.dataDir = self.currDir + 'data/'
		if not os.path.exists(self.dataDir):
			os.makedirs(self.dataDir)

		self.pairsFrequency = self.dataDir + str(self.threshold) + '_pairsFrequency.csv'
		self.pairsHistDir = self.currDir + 'pairs_hist/'

		self.corrAVEResults = self.dataDir + str(self.threshold) + '_corr_ave.csv'
		self.corrORIResults = self.dataDir + str(self.threshold) + '_corr_ori.csv'
		self.valAVE = self.dataDir + str(self.threshold) + '_corr_ave_val.csv'
		self.valORI = self.dataDir + str(self.threshold) + '_corr_ori_val.csv'

		self.valAVE60 = self.dataDir + str(self.threshold) + '_corr_ave_val60.csv'
		self.valAVE65 = self.dataDir + str(self.threshold) + '_corr_ave_val65.csv'
		self.valAVE70 = self.dataDir + str(self.threshold) + '_corr_ave_val70.csv'
		self.valAVE75 = self.dataDir + str(self.threshold) + '_corr_ave_val75.csv'

		self.valORI60 = self.dataDir + str(self.threshold) + '_corr_ori_val60.csv'
		self.valORI65 = self.dataDir + str(self.threshold) + '_corr_ori_val65.csv'
		self.valORI70 = self.dataDir + str(self.threshold) + '_corr_ori_val70.csv'

		self.valAVE6060 = self.dataDir + str(self.threshold) + '_corr_ave_val60_60.csv'
		self.valAVE6565 = self.dataDir + str(self.threshold) + '_corr_ave_val65_65.csv'
		self.valAVE7070 = self.dataDir + str(self.threshold) + '_corr_ave_val70_70.csv'
		self.valAVE7075 = self.dataDir + str(self.threshold) + '_corr_ave_val75_75.csv'

		self.valORI6060 = self.dataDir + str(self.threshold) + '_corr_ori_val60_60.csv'
		self.valORI6565 = self.dataDir + str(self.threshold) + '_corr_ori_val65_65.csv'
		self.valORI7070 = self.dataDir + str(self.threshold) + '_corr_ori_val70_70.csv'

		self.plots_ave = self.currDir + 'plots_ave/'
		self.plots_ori = self.currDir + 'plots_ori/'
		self.coefficient_ave = self.currDir + 'coefficient_ave/'
		self.coefficient_ori = self.currDir + 'coefficient_ori/'
		self.hist_ave = self.currDir + 'hist_ave/'
		self.hist_ori = self.currDir + 'hist_ori/'
		self.bars_ave = self.currDir + 'bars_ave/'
		self.bars_ori = self.currDir + 'bars_ori/'
		self.course_ave = self.currDir + 'course_ave/'
		self.course_ori = self.currDir + 'course_ori/'

		# REPL, NODUP, CRSPERSTU, STUREGISTERED, EMPTY, EMPTY_STU, EMPTY_CRS, CRS_STU, IDMAPPER
		self.regREPL = self.dataDir + str(self.threshold) + '_'
		self.regNODUP = self.dataDir + str(self.threshold) + '_'
		self.techRegNODUP = self.dataDir + str(self.threshold) + '_'
		self.CRSPERSTU = self.dataDir + str(self.threshold) + '_'
		self.STUREGISTERED = self.dataDir + str(self.threshold) + '_'
		self.EMPTY = self.dataDir + str(self.threshold) + '_'
		self.EMPTY_STU = self.dataDir + str(self.threshold) + '_'
		self.EMPTY_CRS = self.dataDir + str(self.threshold) + '_'
		self.CRS_STU = self.dataDir + str(self.threshold) + '_'
		self.CRS_STU_GRADE = self.dataDir + str(self.threshold) + '_'
		self.regNODUPREPL = self.dataDir + str(self.threshold) + '_'
		self.STU_CRS = self.dataDir + str(self.threshold) + '_'
		self.crsMatrix = self.dataDir + str(self.threshold) + '_'
		self.discardList = self.dataDir + str(self.threshold) + '_'
		self.courselist = self.dataDir + str(self.threshold) + '_'
		self.techCrsCSV = self.dataDir + str(self.threshold) + '_'		

		for x in xrange(0, len(regFileName.split('_'))-1):
			self.regREPL = self.regREPL + regFileName.split('_')[x] + '_'
			self.regNODUP = self.regNODUP + regFileName.split('_')[x] + '_'
			self.CRSPERSTU = self.CRSPERSTU + regFileName.split('_')[x] + '_'
			self.STUREGISTERED = self.STUREGISTERED + regFileName.split('_')[x] + '_'
			self.EMPTY = self.EMPTY + regFileName.split('_')[x] + '_'
			self.EMPTY_STU = self.EMPTY_STU + regFileName.split('_')[x] + '_'
			self.EMPTY_CRS = self.EMPTY_CRS + regFileName.split('_')[x] + '_'
			self.CRS_STU = self.CRS_STU + regFileName.split('_')[x] + '_'
			self.regNODUPREPL = self.regNODUPREPL + regFileName.split('_')[x] + '_'
			self.STU_CRS = self.STU_CRS + regFileName.split('_')[x] + '_'
			self.CRS_STU_GRADE = self.CRS_STU_GRADE + regFileName.split('_')[x] + '_'
			self.crsMatrix = self.crsMatrix + regFileName.split('_')[x] + '_'
			self.discardList = self.discardList + regFileName.split('_')[x] + '_'
			self.courselist = self.courselist + regFileName.split('_')[x] + '_'
			self.techCrsCSV = self.techCrsCSV + regFileName.split('_')[x] + '_'
			self.techRegNODUP = self.techRegNODUP + regFileName.split('_')[x] + '_'

		self.regREPL = self.regREPL + 'REPL_SAS.csv'
		self.regNODUP = self.regNODUP + 'NODUP_SAS.csv'
		self.techRegNODUP = self.techRegNODUP + 'TECH_NODUP_SAS.csv'
		self.CRSPERSTU = self.CRSPERSTU + 'CRSPERSTU_SAS.csv'
		self.STUREGISTERED = self.STUREGISTERED + 'STUREGISTERED_SAS.csv'
		self.EMPTY = self.EMPTY + 'EMPTY_SAS.csv'
		self.EMPTY_STU = self.EMPTY_STU + 'EMPTY_STU_SAS.csv'
		self.EMPTY_CRS = self.EMPTY_CRS + 'EMPTY_CRS_SAS.csv'
		self.CRS_STU = self.CRS_STU + 'CRS_STU_SAS.csv'
		self.CRS_STU_GRADE = self.CRS_STU_GRADE + 'CRS_STU_GRADE_SAS.csv'
		self.regNODUPREPL = self.regNODUPREPL + 'NODUP_REPL_SAS.csv'
		self.STU_CRS = self.STU_CRS + 'STU_CRS_SAS.csv'		
		self.crsMatrix = self.crsMatrix + 'CRS_MATRIX_SAS.csv'
		self.discardList = self.discardList + 'DISCARD_SAS.csv'
		self.courselist = self.courselist + 'uniCourseList.csv'
		self.techCrsCSV = self.techCrsCSV + 'TECH.csv'

		self.degREPL = self.dataDir + str(self.threshold) + '_'
		self.IDMAPPER = self.dataDir + str(self.threshold) + '_'
		for x in xrange(0, len(degFilename.split('_'))-1):
			self.degREPL = self.degREPL + degFilename.split('_')[x] + '_'
			self.IDMAPPER = self.IDMAPPER + degFilename.split('_')[x] + '_'

		self.degREPL = self.degREPL + 'REPL_SAS.csv'
		self.IDMAPPER = self.IDMAPPER + 'IDMAPPER_SAS.csv'

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
		dupList = []
		dupCnt = 0
		for record in courseListPerPerson:
			index = courseListPerPerson.index(record)+1
			for crs in xrange(index,len(courseListPerPerson)):
				crsRecd = courseListPerPerson[crs]
				rec1 = record[3].replace(' ','') + record[4]
				rec2 = crsRecd[3].replace(' ','') + crsRecd[4]
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

		newFlag = False
		courseListPerPerson = []
		vnum = ''

		cnt = 0
		userCnt = 0
		dupCnt = 0
		for row in fRegCSVRder:
			cnt = cnt + 1
			# V_number: row[1]
			# Subject_code: row[3]
			# Course Number: row[4]
			# Grade_code: row[6]	
			if len(courseListPerPerson) == 0:
				newFlag = False
				vnum = row[1]
				userCnt = userCnt + 1
			elif row[1] != vnum:
				newFlag = True
				vnum = row[1]
				userCnt = userCnt + 1

			if newFlag:
				newFlag = False
				# start to check the duplicate course records for this specific person
				if len(courseListPerPerson) > 0:
					for record in self.removeDup(courseListPerPerson):
						# record.insert(3,str(record[3])+str(record[4]))
						# record[4] = str(record[4])
						# if len(record[8]) > 0:
						fRegNodupWrter.writerow(record)
				# after coping with duplicate records, clear the course list for new person's course records
				courseListPerPerson = []

			# raw_input("\n")
			# collect course records for another person	
			courseListPerPerson.append(row)

		if len(courseListPerPerson) > 0:
			for record in self.removeDup(courseListPerPerson):
				# record.insert(3,str(record[3])+str(record[4]))
				# record[4] = str(record[4])
				# if len(record[8]) > 0:
				fRegNodupWrter.writerow(record)

	def simpleStats(self, noDupRegFile):
		fRegNodupRder = csv.reader(open(noDupRegFile), delimiter=',')
		# skip header
		header = fRegNodupRder.next()
		# count course frequency
		crsPerStu, crsFre = {}, {}
		noGradeRecs, distinctCRSLst, distinctSTULst = [], [], []
		for record in fRegNodupRder:
			if record[1] not in distinctSTULst:
				distinctSTULst.append(record[1])
			course_code = record[3].replace(' ','')+record[4].replace(' ','')
			if course_code not in distinctCRSLst:
				distinctCRSLst.append(course_code)
			# record[1]:v_number
			# how many courses each students registered
			if record[1] in crsPerStu:
				crsPerStu[record[1]] = crsPerStu[record[1]] + 1
			else:
				crsPerStu[record[1]] = 1

			# course frequency
			# how many students each course was been registered
			if course_code in crsFre:
				crsFre[course_code] = crsFre[course_code] + 1
			else:
				crsFre[course_code] = 1

			if record[6] == '':
				noGradeRecs.append(record)
		
		# count how many courses registered for each student
		w = csv.writer(open(self.CRSPERSTU, 'w'))
		w.writerow(['V_NUMBER', '#_of_Courses_registered'])
		w.writerows(crsPerStu.items())
		# count how many students for each course
		w = csv.writer(open(self.STUREGISTERED, 'w'))
		w.writerow(['Course', '#_of_Students'])
		w.writerows(crsFre.items())
		# pickup the courses without grades
		w = csv.writer(open(self.EMPTY, 'w'))
		noGradeRecs.insert(0, header)
		w.writerows(noGradeRecs)
		
		r = csv.reader(open(self.EMPTY), delimiter=',')
		r.next()
		uniStu, uniCrs = {}, {}
		for record in r:
			if record[1] not in uniStu:
				uniStu[record[1]] = 1
			else:
				uniStu[record[1]] = uniStu[record[1]] + 1

			course_code = record[3].replace(' ','') + record[4].replace(' ','')	
			if course_code not in uniCrs:
				uniCrs[course_code] = 1
			else:
				uniCrs[course_code] = uniCrs[course_code] + 1
		
		# count the students who have courses without grades and how many no grade courses they have
		w = csv.writer(open(self.EMPTY_STU, 'w'))
		w.writerow(['V_NUMBER', '#_of_Courses_No_Grades'])
		w.writerows(uniStu.items())
		# count the #_of_students for the courses which were not assigned any grades
		w = csv.writer(open(self.EMPTY_CRS, 'w'))
		w.writerow(['Course', '#_of_Students_Reg_No_Grade'])
		w.writerows(uniCrs.items())
		
		# create course list
		r = csv.reader(open(noDupRegFile), delimiter=',')
		# skip the header
		r.next()
		crsLst, crscodeLst, regLst, vnumLst = [], [], [], []

		# header: [subj_code, course_code, v_num1, v_num2, ......]
		header = ['SUBJECT_CODE', 'COURSE_NUMBER']
		for record in r:
			subj_code = record[3].replace(' ','')
			course_code = record[4].replace(' ','')
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
		w = csv.writer(open(self.CRS_STU, 'w'))		
		w.writerow(header)
		wgrade = csv.writer(open(self.CRS_STU_GRADE, 'w'))
		wgrade.writerow(header)

		# matrix = [['' for x in range(len(distinctCRSLst))] for x in range(len(distinctSTULst))]
		for x in xrange(0,len(crscodeLst)):
			cell = crsLst[x]

			crs_stu, crs_stu_grade = [], []
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
			print '=============print cell, crs_stu, crs_stu_grade   begin============='
			print cell
			print crs_stu
			print crs_stu_grade
			print '=============print cell, crs_stu, crs_stu_grade   end============='

		# create course matrix
		w = csv.writer(open(self.STU_CRS, 'w'))
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
			cnt = 0
			summation = 0
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
			summation = 0
			cnt = 0
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

	def corrPlot(self, source, plotDir, corr):
		if not os.path.exists(plotDir):
			os.makedirs(plotDir)

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
		w.writerow(['xsubCode', 'xnum', 'ysubCode', 'ynum', 'coefficient', 'pValue', 'stderr', 'slope', 'intercept'])

		cnt = 0
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
					xaxis, yaxis = course[0] + ' ' + course[1], newCourse[0] + ' ' + newCourse[1]

					xdata, ydata = [], []
					if source == self.crsMatrix:
						xdata, ydata= map(float, course[3:]), map(float, newCourse[3:])
					else:
						for index in xrange(2, len(course)):
							ix, iy = course[index], newCourse[index]
							if ix.isdigit() and iy.isdigit():
								xdata.append(float(ix))
								ydata.append(float(iy))

						print '===============', 'x:', len(xdata), ' y: ', len(ydata),'================'
						if len(xdata) < self.threshold:
							print '@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@ discard begin @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@ self.threshold: ', self.threshold
							print course[0], ' ', course[1], ' vs ', newCourse[0], ' ', newCourse[1], '\tlen: ', len(xdata), '\tcnt: ', cnt
							print '@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@ discard end @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@ self.threshold:', self.threshold
							# nocommstuList.append(course)
							nocommstuList.append(newCourse)
							continue

					(r, p) = pearsonr(xdata, ydata)
					if str(r) == 'nan':
						print '^^^^^^^^^^^^^^^^^^^^^^^^^^^^^CANNOT Compute Pearson Correlation^^^^^^^^^^^^^^^^^^^^^^^^^^^'
						print '^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ cnt: ', cnt, ' end^^^^^^^^^^^^^^^^^^^^^^^^^^^^^'
						# noCorrList.append(course)
						noCorrList.append(newCourse)
						continue

					fig = plt.figure()
					plt.title('Grades Scatter (Pearson Correlation)')
					plt.xlabel(xaxis)
					plt.ylabel(yaxis)
					for j in xrange(0,len(xdata)):
						plt.scatter(xdata[j], ydata[j], c = 'blue')

					slope, intercept, r_value, p_value, std_err = linregress(xdata, ydata)
					# format the parameters precision
					r, slope, intercept, r_value, p_value, std_err = [float(format(r, '.2f')), float(format(slope, '.2f')), float(format(intercept, '.2f')), float(format(r_value, '.2f')), float(format(p_value, '.2f')), float(format(std_err, '.2f'))]
					
					w.writerow([course[0], course[1], newCourse[0], newCourse[1], r, p_value, std_err, slope, intercept])

					xdata.insert(0, 0.0)
					xdata.insert(-1, 9.0)
					yp = [x*slope+intercept for x in xdata]
					plt.plot(xdata, yp, c='green', label = 'r = ' + str(r_value) + ', y = ' + str(slope) + 'x' + '+' +str(intercept))

					plt.axis([0, 9, 0, 9])
					plt.grid(True)
					plt.legend(loc='best')

					figName = plotDir + course[0] + course[1] + ' ' + newCourse[0] + newCourse[1] + '.png'
					fig.savefig(figName)
					plt.close(fig)
					print 'cnt: ', cnt, '\t', course[0], course[1], ' vs ', newCourse[0], newCourse[1], '\t\tlen: ', len(xdata), '\tr: ', r, '\tr_value:', r_value, '\tslope: ', slope, '\tself.threshold: ', self.threshold

			if len(noCorrList) > 0:
				if not os.path.exists(self.dataDir + 'nocorr/'):
					os.makedirs(self.dataDir + 'nocorr/')

				nocorr = self.dataDir + 'nocorr/' + str(self.threshold) + '_no_corr_' + course[0] + '' + course[1] + '.csv'
				wnocorr = csv.writer(open(nocorr, 'w'))
				# wnocorr.writerow(header)
				noCorrList.insert(0, course)
				wnocorr.writerows(noCorrList)

			if len(nocommstuList) > 0:
				if not os.path.exists(self.dataDir + 'nocomstu/'):
					os.makedirs(self.dataDir + 'nocomstu/')

				nocommstu = self.dataDir + 'nocomstu/' + str(self.threshold) + '_nocomstu_' + course[0] + '' + course[1] + '.csv'
				wnocom = csv.writer(open(nocommstu, 'w'))
				# wnocom.writerow(header)
				nocommstuList.insert(0, course)
				wnocom.writerows(nocommstuList)
			
	def figureSelect(self, threshold, interval, fromDir, toDir, corr):		
		savePath = toDir + str(threshold) +'_'+ str(threshold + interval)

		if not os.path.exists(savePath):
			os.makedirs(savePath)

		reader = csv.reader(open(corr), delimiter = ',')
		reader.next()
		for row in reader:
			if float(row[4]) > threshold and float(row[4]) < threshold + interval:
				name = row[0] + row[1] + ' ' + row[2] + row[3] + '.png'
				shutil.copy2(fromDir + name, savePath + '/' + name)

	def coefficientHist(self, interval, histDir, corr):
		if not os.path.exists(histDir):
			os.makedirs(histDir)

		reader = csv.reader(open(corr), delimiter = ',')
		reader.next()
		x = []
		for row in reader:
			x.append(float(row[4]))

		fig = plt.figure()
		bins = np.arange(-1.0, 1.0, interval)
		plt.title('Histogram of Coefficients with interval ' + str(interval), fontsize='large')
		plt.xlabel('Pearson Correlation Coefficient')
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
		
		print freq, '\n', len(freq)
		
		reader = csv.reader(open(self.regNODUP), delimiter = ',')
		reader.next()
		crsLst = []

		writer = csv.writer(open(self.courselist, 'w'))
		writer.writerow(['SUBJECT_CODE', 'COURSE_NUMBER', 'FREQUENCY'])
		for row in reader:
			crs = row[3].replace(' ','')+row[4]
			if (crs not in crsLst):
				crsLst.append(crs)
				writer.writerow([row[3].replace(' ', ''), row[4], freq[crs]])
		
	def sortCourse(self, courses, values):
		for i in xrange(0,len(courses)):
			for j in xrange(i+1,len(courses)):
				ilastChar = courses[i][-1]
				jlastChar = courses[j][-1]
				icrn = 0
				jcrn = 0
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

		# print courses
		return [courses, values]

	def groupPlots(self, fromDir, toDir, corr):
		reader = csv.reader(open(corr), delimiter = ',')
		reader.next()
		# figPath = self.currDir + 'plots_ave/'
		for row in reader:
			folder = toDir + row[0]+row[1]
			if not os.path.exists(folder):
				os.makedirs(folder)
			fig = row[0] + row[1] + ' ' + row[2] + row[3] + '.png'
			shutil.copy2(fromDir + fig, toDir + '/' + fig)

	def corrMatrix(self, matrix, corrSeq):
		corrdir = ''
		corr = 1
		corrf = 2
		if corrSeq == 12:
			corrdir = self.currDir+'12/'
		elif corrSeq == 23:
			corrdir = self.currDir+'23/'
			corr = 2
			corrf = 3
		else:
			return

		if not os.path.exists(corrdir):
			os.makedirs(corrdir)
		for x in xrange(2,len(matrix)):
			if int(matrix[x][1][0]) == corr:
				name = corrdir + matrix[x][0] + matrix[x][1] + '.csv'
				lst = []
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
		reader.next()
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

	def techCrsHist(self, interval):
		figPath = self.currDir + 'crs_hist/'
		if not os.path.exists(figPath):
			os.makedirs(figPath)

		reader = csv.reader(open(self.allTechCrs), delimiter = ',')
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
					print x[0], ' ', x[1], ' vs ', y[0], ' ', y[1], ' cnt: ', cnt
					# if cnt > 1:
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

		w, w1 = '', ''
		if cutoff == 0.60:
			if flag == 'ave':
				w = csv.writer(open(self.valAVE60, 'w'))
				w1 = csv.writer(open(self.valAVE6060, 'w'))
			if flag == 'ori':
				w = csv.writer(open(self.valORI60, 'w'))
				w1 = csv.writer(open(self.valORI6060, 'w'))
		elif cutoff == 0.65:
			if flag == 'ave':
				w = csv.writer(open(self.valAVE65, 'w'))
				w1 = csv.writer(open(self.valAVE6565, 'w'))
			if flag == 'ori':
				w = csv.writer(open(self.valORI65, 'w'))
				w1 = csv.writer(open(self.valORI6565, 'w'))
		elif cutoff == 0.70:
			if flag == 'ave':
				w = csv.writer(open(self.valAVE70, 'w'))
				w1 = csv.writer(open(self.valAVE7070, 'w'))
			if flag == 'ori':
				w = csv.writer(open(self.valORI70, 'w'))
				w1 = csv.writer(open(self.valORI7070, 'w'))
		elif cutoff == 0.75:
			if flag == 'ave':
				w = csv.writer(open(self.valAVE75, 'w'))
				w1 = csv.writer(open(self.valAVE7075, 'w'))

		r1 = csv.reader(open(corr), delimiter=',')
		r1.next()
		coeLst = []
		for pair in r1:
			if float(format(float(pair[4]), '.2f')) >= cutoff:
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
				# if (xgrades[x] != 'NA' and xgrades[x] != 'NG') and (ygrades[x] != 'NA' and ygrades[x] != 'NG'):
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
					w1.writerow(header)

		w1.writerow(['Course', '#Course'])
		sorted_freq = sorted(freq.items(), key=itemgetter(1), reverse=True)
		for tps in sorted_freq:
			w1.writerow([tps[0], tps[1]])

		for pair in gradeLevelFreLst:
			xkey, ykey = pair[0], pair[1]
			xgrades, ygrades = crsDict[xkey], crsDict[ykey]
			total = 0
			levelA, levelB, levelC, levelD, levelF = [], [], [], [], []
			for x in xrange(0,len(xgrades)):
				# if (xgrades[x] != 'NA' and xgrades[x] != 'NG') and (ygrades[x] != 'NA' and ygrades[x] != 'NG'):
				if (xgrades[x] != '' and ygrades[x] != ''):
					total = total + 1
					if xgrades[x] == 'A' or xgrades[x] == 'A-' or xgrades[x] == 'A+':
						levelA.append(ygrades[x])
					if xgrades[x] == 'B' or xgrades[x] == 'B-' or xgrades[x] == 'B+':
						levelB.append(ygrades[x])
					if xgrades[x] == 'C' or xgrades[x] == 'C+':
						levelC.append(ygrades[x])
					if xgrades[x] == 'D' or xgrades[x] == 'SB' or xgrades[x] == 'SB-' or xgrades[x] == 'SD':
						levelD.append(ygrades[x])
					if xgrades[x] == 'E' or xgrades[x] == 'F' or xgrades[x] == 'N' or xgrades[x] == 'SF':
						levelF.append(ygrades[x])

			w.writerow(['Course_1', 'Course_2', '', '', '', '', '', '', '', '', '', '', '#Student', 'Coefficient', '#Courses'])
			w.writerow([xkey, ykey, 'A', 'B', 'C', 'D', 'F', '%A', '%B', '%C', '%D', '%F', total, pair[3], freq[xkey]])

			lsta = self.gradeDistributionCell(self.levelFrequency(levelA), 'A_1')
			lstb = self.gradeDistributionCell(self.levelFrequency(levelB), 'B_1')
			lstc = self.gradeDistributionCell(self.levelFrequency(levelC), 'C_1')
			lstd = self.gradeDistributionCell(self.levelFrequency(levelD), 'D_1')
			lstf = self.gradeDistributionCell(self.levelFrequency(levelF), 'F_1')

			w.writerows([lsta, lstb, lstc, lstd, lstf])

			print [xkey, ykey, 'A', 'B', 'C', 'D', 'F', '%A', '%B', '%C', '%D', '%F', total, pair[2], pair[3], freq[xkey]]
			print lsta, '\n', lstb, '\n', lstc, '\n', lstd, '\n', lstf

	def gradeDistributionCell(self, lst, gradeLevel):
		if sum(lst) != 0 and len(lst) == 5:
			return [gradeLevel, sum(lst), lst[0], lst[1], lst[2], lst[3], lst[4], format(lst[0]*1.0/sum(lst), '.2f'), format(lst[1]*1.0/sum(lst), '.2f'), format(lst[2]*1.0/sum(lst), '.2f'), format(lst[3]*1.0/sum(lst), '.2f'), format(lst[4]*1.0/sum(lst), '.2f')]
		else:
			return [gradeLevel, sum(lst), lst[0], lst[1], lst[2], lst[3], lst[4]]

	def levelFrequency(self, level):
		acnt = bcnt = ccnt = dcnt = fcnt = 0
		for x in level:
			if x == 'A' or x == 'A-' or x == 'A+':
				acnt = acnt + 1
			if x == 'B' or x == 'B-' or x == 'B+':
				bcnt = bcnt + 1
			if x == 'C' or x == 'C+':
				ccnt = ccnt + 1
			if x == 'D' or x == 'SB' or x == 'SB-' or x == 'SD':
				dcnt = dcnt + 1
			if x == 'E' or x == 'F' or x == 'N' or x == 'SF':
				fcnt = fcnt + 1

		return [acnt, bcnt, ccnt, dcnt, fcnt]

	def gradesGroup(self):
		return {'A':['A+','A','A-'], 'B':['B+','B','B-'], 'C':['C+','C'], 'D':['D','SB','SB-','SD'], 'Fail':['E','F','N','SF']}

	def gradePointMap(self):
		return {'A':8, 'A-':7, 'A+':9, 'B':5, 'B-':4, 'B+':6, 'C':2, 'C+':3, 'D':1, 'E':0, 'F':0, 'N':0, 'SB':1, 'SB-':1, 'SD':1, 'SF':0}


prepross(sys.argv).doBatch()
