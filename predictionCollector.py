#!/usr/bin/env python

import csv, os, xlsxwriter, sys
from operator import itemgetter
import organizer

sheetDict = {
	'2010-2011':['2012', '2013', '2014', '2015', '2012-2015'],
	'2010-2012':['2013', '2014', '2015', '2013-2015'],
	'2010-2013':['2014', '2015', '2014-2015'],
	'2010-2014':['2015']
}

h1 = ['xSubj', 'xNum', 'ySubj', 'yNum', '#', 'r', 'Pxy', 'instance',	'0~0.5', '%', '0.5~1.0', '%', '0~1.0', '%', '1.0~1.5', '%', 'gt1.5', '%']
h2 = ['xSubj', 'xNum', 'ySubj', 'yNum', '#', 'r', 'instance',	'0~0.5', '%', '0.5~1.0', '%', '0~1.0', '%', '1.0~1.5', '%', 'gt1.5', '%']
accHeader = []

def rawResultCollector(trainYrsText, factor, resultList):
	resultPath = '/'.join(resultList[0].split('/')[:-1])+'/'
	# path for the current computation
	path = '/'.join(resultList[0].split('/')[:-5])+'/'
	print 'Path: ', path
	xlsx = path+trainYrsText+'_'+factor+'_picked.xlsx'
	workbook = xlsxwriter.Workbook(xlsx)
	myformat = workbook.add_format({'align':'center_across'})

	print 'trainYrsText: ', trainYrsText,  '\tfactor:', factor
	
	# fetch predictors from both CourseX and CourseY
	pickListsX, pickListsY = organizer.pickedCoursePairList()

	# build file list
	# originResultFileList = []
	for item in sheetDict[trainYrsText]:
		print 'sheetDict: ', resultPath+'reg'+item+factor+'L.csv'
		# originResultFileList.append(resultPath+'reg'+item+factor+'L.csv')
		file = resultPath+'reg'+item+factor+'L.csv'
		# fetch acc data from the file
		accList = readAccFromResultFile(file)
		# search acc data from accList
		xAccList, yAccList = searchAllAccByPredictors(pickListsX, pickListsY, accList, factor)
		# create sheets
		xsheetName = item+factor+'X'
		ysheetName = item+factor+'Y'
		createSheet(workbook, xsheetName, myformat, xAccList)
		createSheet(workbook, ysheetName, myformat, yAccList)

	print '======================================= ', factor, ' ======================================='
	print '======================================= rawResultCollector Done ======================================='

def createSheet(workbook, sheetname, myformat, data):
	worksheet = workbook.add_worksheet(sheetname)
	rowcnt = 0
	for row in data:
		worksheet.write_row(rowcnt,0,row,myformat)
		rowcnt+=1

def searchAllAccByPredictors(pickListsX, pickListsY, accList, factor):
	xPredictors = []
	yPredictors = []
	if factor == 'PR':
		accHeader = h1
		xPredictors = pickListsX[2]
		yPredictors = pickListsY[2]
	if factor == 'R':
		accHeader = h2
		xPredictors = pickListsX[1]
		yPredictors = pickListsY[1]
	if factor == 'P':
		accHeader = h2
		xPredictors = pickListsX[0]
		yPredictors = pickListsY[0]

	xAccList = searchAccByPredictors(accList, xPredictors)
	yAccList = searchAccByPredictors(accList, yPredictors)

	xAccList  = [[factor], accHeader]+xAccList
	yAccList  = [['YPoint'], accHeader]+yAccList

	return [xAccList, yAccList]

def searchAccByPredictors(accList, pickedPredictors):
	retAcc = []
	for predictorRow in pickedPredictors:
		crsx, numx = predictorRow[0].split(' ')
		crsy, numy = predictorRow[1].split(' ')
		for accRow in accList:
			if crsx in accRow and numx in accRow and crsy in accRow and numy in accRow:
				if accRow not in retAcc:
					retAcc.append(accRow)

	return retAcc

def readAccFromResultFile(file):
	retAccList = []
	lastTag = 0
	startBlank = 0
	# file = '/Users/rexlei/Google Drive/20180426/2010-2011/PR/T1/L/reg2015PRL.csv'
	r = csv.reader(open(file), delimiter=',')
	for row in r:
		# remove the '' elements in the row
		row = filter(lambda x: x != '', row)
		# find the last 
		if (len(row) == 1) and ('s2t3Ped' in row):
			lastTag += 1

		if (lastTag == 1) and (len(row) == 0):
			startBlank += 1
		if (startBlank >= 2) and (len(row) > 0):
			# skip the header row
			if 'gt1.5' in row:
				continue
			if 'RMSE' in row:
				break

			retAccList.append(row)
			print type(row), 'Len: ', len(row), ' -- ', row

	return retAccList
