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

myPointPickListX = []
myCoefficientPickListX = []
myPxyPickListX = []

myPointPickListY = []
myCoefficientPickListY = []
myPxyPickListY = []

wList = [1.0,1.1,1.2,1.3,1.4,1.5,1.6,1.7,1.8,1.9,2.0,2.1,2.2,2.3,2.4,2.5]

# sort the courses 
def courseOrganizer(src):
	print '\n\n\n*******************************************\n'+src+'\n'
	path = src.split('/')
	trainText = path[-3]
	filenameWithoutExtension = path[-1].split('.')[0]
	path = '/'.join(path[0:-1])
	print path, '\n'
	print filenameWithoutExtension, '\n'

	# if not (filenameWithoutExtension == 'skewness'):
	# 	return
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
		row[4] = float(row[4])
		row[5] = int(row[5])
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
	xlsx = path+'/'+trainText+'_'+filenameWithoutExtension+'.xlsx'
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
	CourseCountSheet(course1KeysList, course1List, [2, 3, 0, 1], workbook, worksheet, 'CourseX Count', myformat, ['CourseX', 'CourseY', 'Count'])
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
	CourseCountSheet(course2KeysList, course2List, [0, 1, 2, 3], workbook, worksheet, 'CourseY Count', myformat, ['CourseY', 'CourseX', 'Count'])
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
	CourseMaximumFactorSheet(workbook, ["CourseX Pick", "X_R_PICK", "X_#_PICK", "X_XY_PICK"], myformat, course1KeysList, course1List, [2,3], header, 0)
	CourseMaximumFactorSheet(workbook, ["CourseY Pick", "Y_R_PICK", "Y_#_PICK", "Y_XY_PICK"], myformat, course2KeysList, course2List, [0,1], header, 1)
	# ==========================================================================================================================
	# create Course2 Count sheet
	# ==========================================================================================================================

	print '============================================================Organizer DONE=============================================================='

def CourseMaximumFactorSheet(workbook, sheetNames, myformat, courseKeys, courseDict, sortIndex, header, flag):
	courseKeys.sort(key=itemgetter(1), reverse=False)	
	pointPickList = []
	coefficientPickList = []
	pxyPickList = []
	pxyList = []
	for key in courseKeys:
		v =courseDict[key[0]+key[1]]
		
		# v.sort(key=itemgetter(6), reverse=True)
		# deal with negative r-s
		rList = [abs(float(row[4])) for row in v]
		maxR = max(rList)
		maxCoefficientRowRaw = [row for row in v if abs(float(row[4]))==maxR]
		# courseX
		maxCoefficientRows = []
		# if flag == 0:
		# 	for row in maxCoefficientRowRaw:
		# 		maxCoefficientRows.append([row[0]+' '+row[1], row[2]+' '+row[3]]+row[4:])
		# # courseY
		# if flag == 1:
			# find the smallest course number of courseX
		maxCoefficientRowRaw.sort(key=itemgetter(sortIndex[1]), reverse=False)
		maxCoefficientRows = [[maxCoefficientRowRaw[0][0]+' '+maxCoefficientRowRaw[0][1], maxCoefficientRowRaw[0][2]+' '+maxCoefficientRowRaw[0][3]]+maxCoefficientRowRaw[0][4:]]

		# deal with max point
		v.sort(key=itemgetter(5), reverse=True)
		maxP = v[0][5]
		maxPointRowRaw = [row for row in v if row[5]==maxP]
		maxPointRows = []
		# if flag == 0:
		# 	for row in maxPointRowRaw:
		# 		maxPointRows.append([row[0]+' '+row[1], row[2]+' '+row[3]]+row[4:])
		# if flag == 1:
		maxPointRowRaw.sort(key=itemgetter(sortIndex[1]), reverse=False)
		maxPointRows = [[maxPointRowRaw[0][0]+' '+maxPointRowRaw[0][1], maxPointRowRaw[0][2]+' '+maxPointRowRaw[0][3]]+maxPointRowRaw[0][4:]]
		
		coefficientPickList+=maxCoefficientRows
		pointPickList+=maxPointRows

		# build Pxy matrix
		v.sort(key=itemgetter(sortIndex[0], sortIndex[1]), reverse=False)
		pxyReturnList = ComputePxy(key, v, sortIndex, flag)
		pxyList += pxyReturnList+['']
		# pxyPickList
		temp = XYPick(pxyReturnList)
		if len(temp) == 1:
			pxyPickList += temp
		if len(temp) > 1:
			pxyPickList += temp[0]
			pxyList += temp[1]+['']

	# create xlsx sheets
	# Course Pick
	rowcnt = 0
	pxyHeader = ['CourseX', 'CourseY',1.0,1.1,1.2,1.3,1.4,1.5,1.6,1.7,1.8,1.9,2.0,2.1,2.2,2.3,2.4,2.5]
	newHeader = ['CourseX', 'CourseY']+header[4:]
	worksheet = workbook.add_worksheet(sheetNames[0])
	for row in ['PPICK', newHeader]+pointPickList+['','RPICK', newHeader]+coefficientPickList+['','PXYPICK', pxyHeader]+pxyList:
		worksheet.write_row(rowcnt,0,row,myformat)
		rowcnt+=1

	# _R_PICK
	worksheet = workbook.add_worksheet(sheetNames[1])
	rowcnt = 0
	for row in [newHeader]+coefficientPickList:
		worksheet.write_row(rowcnt,0,row,myformat)
		rowcnt+=1
	# _P_PICK
	worksheet = workbook.add_worksheet(sheetNames[2])
	rowcnt = 0
	for row in [newHeader]+pointPickList:
		worksheet.write_row(rowcnt,0,row,myformat)
		rowcnt+=1
	# _XY_PICK

	pxyPickList = reversePxyForCourseY(pxyPickList, flag)
	pxyPickList = integratePxyPickedRow(pxyPickList, flag, courseDict)
	worksheet = workbook.add_worksheet(sheetNames[3])
	rowcnt = 0
	for row in [newHeader]+pxyPickList:
		worksheet.write_row(rowcnt,0,row,myformat)
		rowcnt+=1

	copyPickLists(flag, pointPickList, coefficientPickList, pxyPickList)

def integratePxyPickedRow(pxyPickedList, flag, rowListDict):
	retList = []
	# CourseX
	if flag == 0:
		for item in pxyPickedList:
			coursex = ''.join(item[0].split(' '))
			coursey = ''.join(item[1].split(' '))
			if rowListDict.has_key(coursex):
				temp = [row for row in rowListDict[coursex] if ((row[0]+row[1]) == coursex) and ((row[2]+row[3]) == coursey)][0]
				retList.append(item+temp[4:])
	# CourseY
	if flag == 1:
		for item in pxyPickedList:
			coursex = ''.join(item[0].split(' '))
			coursey = ''.join(item[1].split(' '))
			if rowListDict.has_key(coursey):
				temp = [row for row in rowListDict[coursey] if ((row[0]+row[1]) == coursex) and ((row[2]+row[3]) == coursey)][0]
				retList.append(item+temp[4:])

	return retList

def reversePxyForCourseY(pxyPickList, flag):
	if flag == 0:
		return pxyPickList
	if flag == 1:
		return [list(reversed(i)) for i in pxyPickList]

def ComputePxy(keycourse, courseList, sortIndex, flag):
	if len(courseList) == 1:
		# courseX
		if flag == 0:
			return [[courseList[0][0]+' '+courseList[0][1], courseList[0][2]+' '+courseList[0][3]]+courseList[4:8]]
		if flag == 1:
			return [[courseList[0][2]+' '+courseList[0][3], courseList[0][0]+' '+courseList[0][1]]+courseList[4:8]]

	# normalization
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

def XYPick(pxyReturnList):
	if len(pxyReturnList) == 1:
		return [[pxyReturnList[0][0], pxyReturnList[0][1]]]

	# accumulate sum in row
	sumList = []
	for i in xrange(0,len(pxyReturnList)):
		sumList.append(0)

	xyArrayList = []
	for i in xrange(0,len(wList)):
		colPxys = []
		for j in xrange(0,len(pxyReturnList)):
			colPxys.append(float(pxyReturnList[j][i+2]))

		maxPxy = max(colPxys)
		temp = []
		for k in xrange(0, len(colPxys)):
			if colPxys[k] == maxPxy:
				temp.append(1)
				sumList[k] += 1
			else:
				temp.append(0)

		xyArrayList.append(temp)

	maxSum = max(sumList)
	ret = []
	for i in xrange(0,len(sumList)):
		if maxSum == sumList[i]:
			ret.append([pxyReturnList[i][0], pxyReturnList[i][1]])

	# find the max
	for item in xyArrayList:
		print item

	# form max row
	rows = []
	for i in xrange(0,len(pxyReturnList)):
		temp = [pxyReturnList[i][0], pxyReturnList[i][1]]
		for j in xrange(0,len(xyArrayList)):
			temp.append(xyArrayList[j][i])
		rows.append(temp)

	return [ret, rows]

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
		v.sort(key=itemgetter(4,5), reverse=True)
		for row in [header]+v+['']:
			worksheet.write_row(rowcnt,0,row,myformat)
			rowcnt+=1

def CourseCountSheet(courseKeys, courseDict, sortKeyIndex, workbook, worksheet, sheetName, myformat, header):
	courseKeys.sort(key=itemgetter(1), reverse=False)
	worksheet = workbook.add_worksheet(sheetName)
	worksheet.write_row(0,8,CourseCountInYear(courseKeys),myformat)
	rowcnt = 1
	for row in courseKeys:
		worksheet.write_row(rowcnt,8,row,myformat)
		rowcnt+=1

	rowcnt = 0
	worksheet.write_row(rowcnt,0,['count','CourseX','CourseY','r','#','p-value','stderr'],myformat)
	rowcnt+=1
	singleLineList = []
	for key in courseKeys:
		v =courseDict[key[0]+key[1]]
		v.sort(key=itemgetter(sortKeyIndex[0],sortKeyIndex[1]), reverse=False)
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

		singleLineList.append([v[0][sortKeyIndex[2]] + ' ' + v[0][sortKeyIndex[3]], formSingleLineCourses(c1List), count])

	rowcnt = 2
	for item in [header]+singleLineList:
		print item
		worksheet.write_row(rowcnt,11,item,myformat)
		rowcnt += 1

def formSingleLineCourses(courseList):
	previous = ''
	retstr = ''
	for item in courseList:
		prefix, num = item[0].split(' ')
		if prefix == previous:
			retstr += '/'+num
		else:
			retstr += ', '+item[0]
			previous = prefix

	return retstr[2:]

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

def copyPickLists(flag, pointPickList, coefficientPickList, pxyPickList):
	# by courseX
	if flag == 0:
		del myPointPickListX[:]
		del myCoefficientPickListX[:]
		del myPxyPickListX[:]

		for item in pointPickList:
			myPointPickListX.append(item)
		for item in coefficientPickList:
			myCoefficientPickListX.append(item)
		for item in pxyPickList:
			myPxyPickListX.append(item)

	# by courseY
	if flag == 1:
		del myPointPickListY[:]
		del myCoefficientPickListY[:]
		del myPxyPickListY[:]

		for item in pointPickList:
			myPointPickListY.append(item)
		for item in coefficientPickList:
			myCoefficientPickListY.append(item)
		for item in pxyPickList:
			myPxyPickListY.append(item)

def pickedCoursePairList():
	return [[myPointPickListX, myCoefficientPickListX, myPxyPickListX], [myPointPickListY, myCoefficientPickListY, myPxyPickListY]]

# courseOrganizer(sys.argv[1])
