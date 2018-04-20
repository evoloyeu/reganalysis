#!/usr/bin/env python

import csv, os, xlsxwriter, sys
from operator import itemgetter

# subCode1	Num1	subCode2	Num2	coefficient	#points	pValue	stderr	slope	intercept	a	b	c	R^2	xmin	xmax	skew1	skew2
# 	0		1		2			3		4			5		6		7		8		9			10	11	12	13	14		15		16		17
cutoff = 0.05
crsx1index = 0
numx1index = 1
crsx2index = 2
numx2index = 3
rindex = 4
pindex = 5
pvindex = 6
stderrindex = 7

# sort the courses 
def courseOrganizer(src):
	print '\n\n\n*******************************************\n'+src+'\n'
	path = src.split('/')
	filenameWithoutExtension = path[-1].split('.')[0]
	path = '/'.join(path[0:-1])
	print path, '\n'
	print filenameWithoutExtension, '\n'

	if not (filenameWithoutExtension == 'skewness'):
		return
	# ==========================================================================================================================
	# create Course2 Count sheet
	# ==========================================================================================================================
	r = csv.reader(open(src), delimiter=',')
	# skip header
	reservedList = []
	course1List = {}
	course1KeysList = []
	course2List = {}
	course2KeysList = []
	header = r.next()
	for row in r:
		p_value = row[6]
		r = row[4]
		if (float(p_value) <= cutoff) and (abs(float(r)) != 1.0):
			reservedList.append(row)
			course1 = row[0]+row[1]
			course2 = row[2]+row[3]
			if course1List.has_key(course1):
				course1List[course1].append(row)
			else:
				course1List[course1] = [row]
				course1KeysList.append([row[0],row[1]])

			if course2List.has_key(course2):
				course2List[course2].append(row)
			else:
				course2List[course2] = [row]
				course2KeysList.append([row[2],row[3]])

	# ==========================================================================================================================
	# create Course2 Count sheet
	# ==========================================================================================================================
	xlsx = path+'/'+filenameWithoutExtension+'.xlsx'
	workbook = xlsxwriter.Workbook(xlsx)
	myformat = workbook.add_format({'align':'center_across'})

	worksheet = workbook.add_worksheet('Above 0.05')
	rowcnt = 0
	for row in [header]+reservedList:
		worksheet.write_row(rowcnt,0,row,myformat)
		# print row
		rowcnt+=1
	# ==========================================================================================================================
	# create Course2 Count sheet
	# ==========================================================================================================================
	worksheet = workbook.add_worksheet('Sorted')
	rowcnt = CourseSortedSheet(worksheet, myformat, 0, header, reservedList, [3,2,5])
	rowcnt = CourseSortedSheet(worksheet, myformat, rowcnt, header, reservedList, [1,0,5])
	"""
	rowcnt = 0
	reservedList.sort(key=itemgetter(3,2,7), reverse=False)	
	for row in [header]+reservedList+['']:
		worksheet.write_row(rowcnt,0,row,myformat)
		# print row
		rowcnt+=1

	reservedList.sort(key=itemgetter(1,0,7), reverse=False)
	for row in [header]+reservedList+['']:
		worksheet.write_row(rowcnt,0,row,myformat)
		# print row
		rowcnt+=1
	"""
	# ==========================================================================================================================
	# create Course2 Count sheet
	# ==========================================================================================================================
	CourseListSheet(workbook, worksheet, 'CourseX Lists', myformat, course1List, header)
	"""
	worksheet = workbook.add_worksheet('Course1 Lists')
	rowcnt = 0
	for key, v in course1List.items():
		for row in [header]+v+['']:
			worksheet.write_row(rowcnt,0,row,myformat)
			rowcnt+=1
	"""
	# ==========================================================================================================================
	# create Course2 Count sheet
	# ==========================================================================================================================
	CourseListSheet(workbook, worksheet, 'CourseY Lists', myformat, course2List, header)
	"""
	worksheet = workbook.add_worksheet('Course2 Lists')
	rowcnt = 0
	for key, v in course2List.items():
		for row in [header]+v+['']:
			worksheet.write_row(rowcnt,0,row,myformat)
			rowcnt+=1
	"""
	# ==========================================================================================================================
	# create Course1 Count sheet
	# ==========================================================================================================================
	CourseCountSheet(course1KeysList, course1List, [2, 3, 0, 1], workbook, worksheet, 'CourseX Count', myformat)
	"""
	course1KeysList.sort(key=itemgetter(1), reverse=False)
	worksheet = workbook.add_worksheet('Course1 Count')
	worksheet.write_row(0,11,courseCountInYear(course1KeysList),myformat)
	rowcnt = 1
	for row in course1KeysList:
		worksheet.write_row(rowcnt,11,row,myformat)
		rowcnt+=1

	rowcnt = 0
	# for k,v in course1List.items():
	for key in course1KeysList:
		v =course1List[key[0]+key[1]]
		v.sort(key=itemgetter(2,3), reverse=False)
		worksheet.write_row(rowcnt,0,['count','subCode1','Num1','subCode2','Num2','coefficient','#points','pValue','stderr'],myformat)
		rowcnt+=1
		count = len(v)
		c2List = []
		for row in v:
			c2List.append([row[2],row[3],row[6],row[7],row[8],row[9]])
		c1 = [count, v[0][0], v[0][1]] + c2List[0]
		worksheet.write_row(rowcnt,0,c1,myformat)
		rowcnt+=1
		for row in c2List[1:]:
			worksheet.write_row(rowcnt,0,['','','']+row,myformat)
			rowcnt+=1
	"""
	# ==========================================================================================================================
	# create Course2 Count sheet
	# ==========================================================================================================================
	CourseCountSheet(course2KeysList, course2List, [0, 1, 2, 3], workbook, worksheet, 'CourseY Count', myformat)
	"""
	course2KeysList.sort(key=itemgetter(1), reverse=False)
	worksheet = workbook.add_worksheet('Course2 Count')
	worksheet.write_row(0,11,courseCountInYear(course2KeysList),myformat)
	rowcnt = 1
	for row in course2KeysList:
		worksheet.write_row(rowcnt,11,row,myformat)
		rowcnt+=1

	rowcnt = 0
	# for k,v in course2List.items():
	for key in course2KeysList:
		v =course2List[key[0]+key[1]]
		v.sort(key=itemgetter(0,1), reverse=False)
		worksheet.write_row(rowcnt,0,['count','subCode1','Num1','subCode2','Num2','coefficient','#points','pValue','stderr'],myformat)
		rowcnt+=1
		count = len(v)
		c1List = []
		for row in v:
			c1List.append([row[0],row[1],row[6],row[7],row[8],row[9]])
		c1 = [count, v[0][2], v[0][3]] + c1List[0]
		worksheet.write_row(rowcnt,0,c1,myformat)
		rowcnt+=1
		for row in c1List[1:]:
			worksheet.write_row(rowcnt,0,['','','']+row,myformat)
			rowcnt+=1
	"""
	# ==========================================================================================================================
	# create Course2 Count sheet
	# ==========================================================================================================================
	CourseMaximumFactorSheet(workbook, worksheet, "CourseX Pick", myformat, course1KeysList, course1List, [2,3], header)
	CourseMaximumFactorSheet(workbook, worksheet, "CourseY Pick", myformat, course2KeysList, course2List, [0,1], header)
	# ==========================================================================================================================
	# create Course2 Count sheet
	# ==========================================================================================================================
	
	# ==========================================================================================================================
	# create Course2 Count sheet
	# ==========================================================================================================================

	# ==========================================================================================================================
	# create Course2 Count sheet
	# ==========================================================================================================================

	print '============================================================Organizer DONE=============================================================='

def CourseMaximumFactorSheet(workbook, worksheet, sheetName, myformat, courseKeys, courseDict, sortIndex, header):
	courseKeys.sort(key=itemgetter(1), reverse=False)
	worksheet = workbook.add_worksheet(sheetName)
	pointPickList = []
	coefficientPickList = []
	pxyPickList = []
	for key in courseKeys:
		v =courseDict[key[0]+key[1]]
		
		# v.sort(key=itemgetter(6), reverse=True)
		# deal with negative r-s
		rList = [abs(float(row[4])) for row in v]
		maxR = max(rList)
		maxCoefficientRowRaw = [row for row in v if abs(float(row[4]))==maxR]
		maxCoefficientRow = [[maxCoefficientRowRaw[0][0]+' '+maxCoefficientRowRaw[0][1], maxCoefficientRowRaw[0][2]+' '+maxCoefficientRowRaw[0][3]]+maxCoefficientRowRaw[0][4:]]

		v.sort(key=itemgetter(5), reverse=True)
		# concate crsx, numx into CourseX; crsY, numY into CourseY
		maxPointRow = [v[0][0]+' '+v[0][1], v[0][2]+' '+v[0][3]]+v[0][4:]
		
		coefficientPickList+=(maxCoefficientRow)
		pointPickList.append(maxPointRow)

		# build Pxy matrix
		v.sort(key=itemgetter(sortIndex[0], sortIndex[1]), reverse=False)
		pxyPickList += ComputePxy(key, v, sortIndex)+['']

	# create xlsx sheets
	rowcnt = 0
	pxyHeader = ['CourseX', 'CourseY',1.0,1.1,1.2,1.3,1.4,1.5,1.6,1.7,1.8,1.9,2.0,2.1,2.2,2.3,2.4,2.5]
	newHeader = ['CourseX', 'CourseY']+header[4:]
	for row in ['PPICK', newHeader]+pointPickList+['','RPICK', newHeader]+coefficientPickList+['','PXYPICK', pxyHeader]+pxyPickList:
		worksheet.write_row(rowcnt,0,row,myformat)
		rowcnt+=1

def ComputePxy(keycourse, courseList, sortIndex):
	if len(courseList) == 1:
		return courseList
	# function incompleted
	rList = [abs(float(row[4])) for row in courseList]
	pList = [float(row[5]) for row in courseList]
	maxR = max(rList)
	minR = min(rList)
	maxP = max(pList)
	minP = min(pList)

	normedRList = [(x-minR)/(maxR-minR) for x in rList]
	if (maxP-minP) == 0:
		normedPList = [x/x for x in pList]
	else:
		normedPList = [(x-minP)/(maxP-minP) for x in pList]

	incrementR = [1.0,1.1,1.2,1.3,1.4,1.5,1.6,1.7,1.8,1.9,2.0,2.1,2.2,2.3,2.4,2.5]
	incrementP = [1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0]

	# build the pxy matrix
	pxyList = []
	for i in xrange(0,len(rList)):
		temp = [keycourse[0]+' '+keycourse[1],courseList[i][sortIndex[0]]+' '+courseList[i][sortIndex[1]]]
		for j in xrange(0,len(incrementR)):
			temp.append(normedPList[i]*incrementP[j]+normedRList[i]*incrementR[j])
		pxyList.append(temp)

	return pxyList

def CourseSortedSheet(worksheet, myformat, rowcnt, header, reservedList, sortIndex):
	reservedList.sort(key=itemgetter(sortIndex[0], sortIndex[1], sortIndex[2]), reverse=False)
	for row in [header]+reservedList+['']:
		worksheet.write_row(rowcnt,0,row,myformat)
		# print row
		rowcnt+=1
	return rowcnt

def CourseListSheet(workbook, worksheet, courseListSheetName, myformat, courseList, header):
	worksheet = workbook.add_worksheet(courseListSheetName)
	rowcnt = 0
	for key, v in courseList.items():
		for row in [header]+v+['']:
			worksheet.write_row(rowcnt,0,row,myformat)
			rowcnt+=1

def CourseCountSheet(courseKeys, courseDict, sortKeyIndex, workbook, worksheet, sheetName, myformat):
	courseKeys.sort(key=itemgetter(1), reverse=False)
	worksheet = workbook.add_worksheet(sheetName)
	worksheet.write_row(0,11,CourseCountInYear(courseKeys),myformat)
	rowcnt = 1
	for row in courseKeys:
		worksheet.write_row(rowcnt,11,row,myformat)
		rowcnt+=1

	rowcnt = 0
	# for k,v in course2List.items():
	for key in courseKeys:
		v =courseDict[key[0]+key[1]]
		v.sort(key=itemgetter(sortKeyIndex[0],sortKeyIndex[1]), reverse=False)
		worksheet.write_row(rowcnt,0,['count','CourseX','CourseY','r','#','p-value','stderr'],myformat)
		rowcnt+=1
		count = len(v)
		c1List = []
		for row in v:
			c1List.append([row[sortKeyIndex[0]]+' '+row[sortKeyIndex[1]],row[4],row[5],row[6],row[7]])
		c1 = [count, v[0][sortKeyIndex[2]] + ' ' + v[0][sortKeyIndex[3]]] + c1List[0]
		worksheet.write_row(rowcnt,0,c1,myformat)
		rowcnt+=1
		for row in c1List[1:]:
			worksheet.write_row(rowcnt,0,['','']+row,myformat)
			rowcnt+=1

def CourseCountInYear(courseList):
	y1,y2,y3,y4 = 0, 0, 0, 0
	for row in courseList:
		if row[1][0] == '1':
			y1+=1
		if row[1][0] == '2':
			y2+=1
		if row[1][0] == '3':
			y3+=1
		if row[1][0] == '4':
			y4+=1

	return ['y1', y1, 'y2', y2, 'y3', y3, 'y4', y4, 'sum', y1+y2+y3+y4]

# courseOrganizer(sys.argv[1])
