#!/usr/bin/env python

import csv, os

class myValidate(object):
	"""docstring for myValidate"""
	def __init__(self, arg):
		super(myValidate, self).__init__()
		self.rawDeg, self.rawReg = arg[1], arg[2]

		pathList = self.rawDeg.split('/')
		path = '/'
		for x in xrange(0,len(pathList[1:-2])):
			path = path + pathList[1:-1][x] + '/'

		self.allTechCrs = path+'users/techcourses/technicalCourse.csv'
		self.techList = []

	def doBatch(self):
		self.techCourseList()
		DegIDList = self.validateID()
		self.list1st2ndYrCourses()
		self.validateELEC199(DegIDList)

	def techCourseList(self):
		r = csv.reader(open(self.allTechCrs), delimiter=',')

		for row in r:
			course = row[0].replace(' ','')+row[1].replace(' ','')
			self.techList.append(course)

	def list1st2ndYrCourses(self):
		r = csv.reader(open(self.rawReg), delimiter=',')
		r.next()

		f1courseList,s2courseList,t3courseList,f4courseList = [], [], [], []
		for row in r:
			crs = row[3].replace(' ','')+row[4].replace(' ','')
			if (crs) == 'MATH110':
				row[4] = '133'
			if (crs) == 'ENGR110':
				row[4] = '111'
			if (crs) == 'ENGR141':
				row[3] = 'MECH'

			course = row[3].replace(' ','')+row[4].replace(' ','')

			if course not in f1courseList and row[4][0]=='1' and (course in self.techList):
				f1courseList.append(course)
				# print '1st Yr Tech Course:', course
			elif course not in s2courseList and row[4][0]=='2' and (course in self.techList):
				s2courseList.append(course)
				# print '2nd Yr Tech Course:', course
			elif course not in t3courseList and row[4][0]=='3' and (course in self.techList):
				t3courseList.append(course)
			elif course not in f4courseList and row[4][0]=='4' and (course in self.techList):
				f4courseList.append(course)

			# if course == 'MATH133' or course == 'MATH110':
			# 	print course
		f1courseList.sort(reverse=False)
		s2courseList.sort(reverse=False)
		t3courseList.sort(reverse=False)
		f4courseList.sort(reverse=False)
		print '\nlen(f1courseList):', len(f1courseList), '\n', f1courseList
		print '\nlen(s2courseList):', len(s2courseList), '\n', s2courseList
		print '\nlen(t3courseList):', len(t3courseList), '\n', t3courseList
		print '\nlen(f4courseList):', len(f4courseList), '\n', f4courseList

	def validateID(self):
		print 'validateID:'
		r = csv.reader(open(self.rawDeg), delimiter=',')
		r.next()

		# degree data includes graduates from 2010 to 2015
		DegIDList10, DegIDList11, DegIDList12, DegIDList13, DegIDList14, DegIDList15, DegIDList = [], [], [], [], [], [], []
		# DegList10, DegList11, DegList12, DegList13, DegList14, DegList15 = [], [], [], [], [], []

		for deg in r:
			if deg[1] not in DegIDList:
				DegIDList.append(deg[1])

			if deg[1] in ['V00202855', 'V00241653', 'V00682567']:
				continue

			# graduateYr,OFFICIAL_SNAPSHOT_IND = deg[9],deg[12]
			if (deg[9] == '2010') and (deg[12]=='Y'):
				# DegList10.append(deg)
				if deg[1] not in DegIDList10:
					DegIDList10.append(deg[1])
			elif (deg[9] == '2011') and (deg[12]=='Y'):
				# DegList11.append(deg)
				if deg[1] not in DegIDList11:
					DegIDList11.append(deg[1])
			elif (deg[9] == '2012') and (deg[12]=='Y'):
				# DegList12.append(deg)
				if deg[1] not in DegIDList12:
					DegIDList12.append(deg[1])
			elif (deg[9] == '2013') and (deg[12]=='Y'):
				# DegList13.append(deg)
				if deg[1] not in DegIDList13:
					DegIDList13.append(deg[1])
			elif (deg[9] == '2014') and (deg[12]=='Y'):
				# DegList14.append(deg)
				if deg[1] not in DegIDList14:
					DegIDList14.append(deg[1])
			elif (deg[9] == '2015') and (deg[12]=='Y'):
				# DegList15.append(deg)
				if deg[1] not in DegIDList15:
					DegIDList15.append(deg[1])

		if len(DegIDList) == (len(DegIDList10)+len(DegIDList11)+len(DegIDList12)+len(DegIDList13)+len(DegIDList14)+len(DegIDList15)):
			print 'len(DegIDList):', len(DegIDList)
		else:
			print 'len(DegIDList):', len(DegIDList), '\tlen(Y):', len(DegIDList10)+len(DegIDList11)+len(DegIDList12)+len(DegIDList13)+len(DegIDList14)+len(DegIDList15)

		print '10:', len(DegIDList10),'\n11:', len(DegIDList11), '\n12:', len(DegIDList12), '\n13:', len(DegIDList13), '\n14:', len(DegIDList14), '\n15:', len(DegIDList15), '\nTotal:', len(DegIDList10)+len(DegIDList11)+len(DegIDList12)+len(DegIDList13)+len(DegIDList14)+len(DegIDList15), '\n'

		print 'rest IDs:'
		cnt = 1
		for x in DegIDList:
			if x not in DegIDList10+DegIDList11+DegIDList12+DegIDList13+DegIDList14+DegIDList15:
				print cnt, ': ', x
				cnt += 1

		return DegIDList10+DegIDList11+DegIDList12+DegIDList13+DegIDList14+DegIDList15

	def validateELEC199(self, ids):
		idDict = {}
		r = csv.reader(open(self.rawReg), delimiter=',')
		r.next()
		for row in r:
			if (row[3]+row[4]) == 'ELEC199':
				if row[1] in ids:
					if row[1] not in idDict:
						idDict[row[1]] = [ [row[1], row[3], row[4], row[8]] ]
					else:
						idDict[row[1]].append([row[1], row[3], row[4], row[8]])

		print '\nNo ELEC 199 IDs:'
		for idx in ids:
			if idx not in idDict.keys():
				print idx

		print 'IDs whose ELEC 199 with Null grade:'
		for idx, elec199List in idDict.items():
			nullGrade = 0
			for elec199 in elec199List:
				if len(elec199[3]) > 0:
					nullGrade = 1

			if nullGrade == 0:
				print idx, elec199List

		print 'len(ids):', len(ids), '\t', 'len(idDict):', len(idDict)
