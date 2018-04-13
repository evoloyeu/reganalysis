#!/usr/bin/env python

import csv, os, xlsxwriter, sys
from operator import itemgetter

# subCode1	Num1	subCode2	Num2	skew1	skew2	coefficient	#points	pValue	stderr	slope	intercept	a	b	c	R^2	xmin	xmax
# 0			1		2			3		4		5		6			7		8		9		10		11			12	13	14	15	16		17
cutoff = 0.05
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

	r = csv.reader(open(src), delimiter=',')
	# skip header
	reservedList = []
	course1List = {}
	course2List = {}
	header = r.next()
	for row in r:
		p_value = row[8]
		if float(p_value) <= cutoff:
			reservedList.append(row)
			course1 = row[0]+row[1]
			course2 = row[2]+row[3]
			if course1List.has_key(course1):
				course1List[course1].append(row)
			else:
				course1List[course1] = [row]

			if course2List.has_key(course2):
				course2List[course2].append(row)
			else:
				course2List[course2] = [row]

	xlsx = path+'/'+filenameWithoutExtension+'.xlsx'
	workbook = xlsxwriter.Workbook(xlsx)
	myformat = workbook.add_format({'align':'center_across'})

	worksheet = workbook.add_worksheet('Above 0.05')
	rowcnt = 0
	for row in [header]+reservedList:
		worksheet.write_row(rowcnt,0,row,myformat)
		# print row
		rowcnt+=1

	worksheet = workbook.add_worksheet('Sorted')
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

	# print course1List

	worksheet = workbook.add_worksheet('Course1 Lists')
	rowcnt = 0
	for key, v in course1List.items():
		for row in [header]+v+['']:
			worksheet.write_row(rowcnt,0,row,myformat)
			rowcnt+=1

	worksheet = workbook.add_worksheet('Course2 Lists')
	rowcnt = 0
	for key, v in course2List.items():
		for row in [header]+v+['']:
			worksheet.write_row(rowcnt,0,row,myformat)
			rowcnt+=1

	worksheet = workbook.add_worksheet('Course1 Count')
	worksheet.write_row(0,0,['count','subCode1','Num1','subCode2','Num2','coefficient','#points','pValue','stderr'],myformat)
	rowcnt = 1
	for k,v in course1List.items():
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

	worksheet = workbook.add_worksheet('Course2 Count')
	worksheet.write_row(0,0,['count','subCode1','Num1','subCode2','Num2','coefficient','#points','pValue','stderr'],myformat)
	rowcnt = 1
	for k,v in course2List.items():
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


# courseOrganizer(sys.argv[1])
