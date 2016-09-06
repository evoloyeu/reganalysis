import regrmdup, rawData, os, sys, csv, random, shutil
from datetime import datetime

class myMTIS(object):
	"""docstring for myMTIS"""
	def __init__(self, arg):
		super(myMTIS, self).__init__()
		prepare = rawData.splitRawData(arg)
		prepare.doBatch()
		self.myReg = regrmdup.prepross(prepare.splitedRawData())
		self.myReg.proPredictor, self.myReg.trainYrs, self.myReg.coe, self.myReg.factor = ['ALL', ['2010', '2011'], 'Pearson', 'PR']
		
	# FOR MTIS ASSIGNMENTS ONLY
	def matrixBuilder(self):
		self.myReg.threshold, randomOrderRegList = 1, []
		self.myReg.statsPath()
		
		reader = csv.reader(open(self.myReg.allTechCrs), delimiter=',')
		crsDict = {}
		for row in reader:
			key, value = row[0]+row[1], row[2]
			crsDict[key] = value

		auxDirs = []
		for regFile in self.myReg.regFileList:
			yr = regFile.split('/')[-1].split('.')[0][3:]
			path = self.myReg.matrixDir+yr+'/'
			auxDirs.append(path)
			if not os.path.exists(path):
				os.makedirs(path)

			fileNameList = []
			fileNameSuffix = ['REPL_SAS.csv', 'NODUP_SAS.csv', 'TECH_NODUP_SAS.csv', 'CRSPERSTU_SAS.csv', 'STUREGISTERED_SAS.csv', 'EMPTY_SAS.csv', 'EMPTY_STU_SAS.csv', 'EMPTY_CRS_SAS.csv', 'CRS_STU_SAS.csv', 'CRS_STU_GRADE_SAS.csv', 'NODUP_REPL_SAS.csv', 'STU_CRS_SAS.csv', 'STU_CRS_GRADE_SAS.csv', 'CRS_MATRIX_SAS.csv', 'DISCARD_SAS.csv', 'uniCourseList.csv', 'uniTechCrsList.csv', 'TECH.csv']
			for suffix in fileNameSuffix:
				fileNameList.append(path+yr+'_'+suffix)

			[self.myReg.regREPL, self.myReg.regNODUP, self.myReg.techRegNODUP, self.myReg.CRSPERSTU, self.myReg.STUREGISTERED, self.myReg.EMPTY, self.myReg.EMPTY_STU, self.myReg.EMPTY_CRS, self.myReg.CRS_STU, self.myReg.CRS_STU_GRADE, self.myReg.regNODUPREPL, self.myReg.STU_CRS, self.myReg.STU_CRS_GRADE, self.myReg.crsMatrix, self.myReg.discardList, self.myReg.courselist, self.myReg.uniTechCrsList, self.myReg.techCrsCSV] = fileNameList

			self.myReg.regDataPath = regFile
			self.myReg.techCrs()
			self.myReg.formatRegSAS(self.myReg.regDataPath, self.myReg.regNODUP)
			self.myReg.formatRegSAS(self.myReg.techCrsCSV, self.myReg.techRegNODUP)
			self.myReg.simpleStats(self.myReg.techRegNODUP, self.myReg.CRSPERSTU, self.myReg.STUREGISTERED, self.myReg.EMPTY, self.myReg.CRS_STU, self.myReg.CRS_STU_GRADE, self.myReg.STU_CRS, self.myReg.STU_CRS_GRADE)

			randomOrderReg = self.myReg.matrixDir+'random'+yr+'.csv'
			randomOrderRegList.append(randomOrderReg)
			self.randomize(self.myReg.STU_CRS_GRADE, randomOrderReg, crsDict)

		# remove auxiliary data
		for path in auxDirs:
			shutil.rmtree(path)

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

