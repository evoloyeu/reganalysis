#!/usr/bin/env python

import csv, os, time, hashlib, shutil, xlsxwriter, copy as myCopy, matplotlib.pyplot as plt, numpy as np
from pylab import *
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.ticker import MultipleLocator
from scipy.stats import pearsonr, linregress, skew
from operator import itemgetter
from collections import Counter
import organizer, predictionCollector

class predictCurrentTestingSet(object):
	"""docstring for predictCurrentTestingSet"""
	def __init__(self):
		super(predictCurrentTestingSet, self).__init__()

	def getPredictorDictionary(self, predictorFile):
		r1 = csv.reader(open(predictorFile), delimiter=',')
		r1.next()
		predictorDict = {}
		for row in r1:
			# key: the predicted course: course name + course number 
			# value: rows of the predictor file except the header
			key = row[2]+row[3]
			if key not in predictorDict:
				predictorDict[key] = [row]
			else:
				predictorDict[key].append(row)

		return predictorDict

	def getTestingSetCourseDictionary(self, testReg):
		# test data reg file: build test reg dict
		r2 = csv.reader(open(testReg), delimiter=',')
		header2, testRegDict = r2.next(), {}
		for row in r2:
			# key: course code(subject code and course number), predicting course
			# value: course record, one row of the CRS_STU
			key = row[0]+row[1]
			testRegDict[key] = row

		return testRegDict

	def createPredictableCoursePairs(self, predictorFile, testReg):
		predictorDict = self.getPredictorDictionary(predictorFile)
		testRegDict = self.getTestingSetCourseDictionary(testReg)

		retPredictableCourseList = []

		# search predictable courses; keys: the predicting courses
		predictingList, keys = [], predictorDict.keys()
		for key in keys: # key: the courseY, predicted course
			if key in testRegDict:
				testY, testXs, predictors = testRegDict[key], [], predictorDict[key]
				# find all predicting courses and store them in testXs
				for x in predictors:
					testXKey = x[0]+x[1]
					if testXKey in testRegDict:
						testXs.append(testRegDict[testXKey])

				retPredictableCourseList.append([testY, testXs, predictors])

		return retPredictableCourseList

	def createPredictableCourseGradesPairs(self, predictorFile, testReg):
		predictableCourseList = self.createPredictableCoursePairs(predictorFile, testReg)

		coursePairs = []
		for item in predictableCourseList:
			testY, testXs, predictors = item
			# no predicting course exists for predicted course
			if len(testXs) == 0:
				continue

			for x in testXs:
				xgrades, ygrades = [x[0], x[1]],[testY[0], testY[1]]
				for index in xrange(2,len(testY)):
					if (x[index].isdigit() and testY[index].isdigit()):
						xgrades.append(x[index])
						ygrades.append(testY[index])

				if len(xgrades) > 2 and len(xgrades) == len(ygrades):
					coursePairs.append([xgrades, ygrades])

		return coursePairs

	def getPredictingPredictedCorrRow(self, courseX, courseY, predictorFile):
		predictorDict = self.getPredictorDictionary(predictorFile)

		return [item for item in predictorDict[courseY] if (item[0]+item[1]) == courseX][0]

	def getFormulaFactors(self, courseX, courseY, predictorFile):
		predictorRow = self.getPredictingPredictedCorrRow(courseX, courseY, predictorFile)
		slope,intercept,a,b,c = predictorRow[8:13]

		return [slope,intercept,a,b,c]

	def computePredictionPrecision(self, ygrades, predictedYGrades):
		if len(ygrades) != len(predictedYGrades) or len(ygrades) == 2 or len(predictedYGrades) == 2:
			return []

		le_05 = be_05_10 = be_10_15 = gt15 = 0
		diffsum = 0.0
		for index in xrange(2,len(ygrades)):
			diff = abs(float(ygrades[index]) - float(predictedYGrades[index]))
			# for compute MAE
			diffsum += diff
			if abs(float(diff)) <= 0.5:
					le_05 += 1
			elif abs(float(diff)) <= 1.0:
					be_05_10 += 1
			elif abs(float(diff)) <= 1.5:
					be_10_15 += 1
			else:
					gt15 += 1

		instance = le_05+be_05_10+be_10_15+gt15
		mae = float(format(diffsum*1.0/instance, '.2'))		
		# [le_05, float(format(le_05*100.0/instance, '.4')), be_05_10, float(format(be_05_10*100.0/instance, '.4')), le_05+be_05_10, float(format((le_05+be_05_10)*100.0/instance, '.4')), be_10_15, float(format(be_10_15*100.0/instance, '.4')), gt15, float(format(gt15*100.0/instance, '.4'))]

		# Total Instance, 0-1.0 Instances, precision
		return [instance, le_05+be_05_10, float(format((le_05+be_05_10)*100.0/instance, '.2')), mae]

	def createPredictionResults(self, testReg, predictResults, predictGradeResults, power, predictorFile):
		precisionHeader = ['CrsXCode', 'CrsXNum', 'CrsYCode', 'CrsYNum', 'r', '#points', 'Enrolment', '0~1.0', '%', 'MAE']
		writer = csv.writer(open(predictResults, 'w'))
		writer.writerow(precisionHeader)
		
		gw = csv.writer(open(predictGradeResults, 'w'))

		coursePairs = self.createPredictableCourseGradesPairs(predictorFile, testReg)
		for pair in coursePairs:
			xgrades, ygrades = pair
			courseX = xgrades[0]+xgrades[1]
			courseY = ygrades[0]+ygrades[1]
			# predicted courseY grades
			predictedYGrades = [ygrades[0], ygrades[1]]

			slope,intercept,a,b,c = self.getFormulaFactors(courseX, courseY, predictorFile)
			for index in xrange(2,len(ygrades)): # skipe the course name and course number
				# create prediction formula
				if power == 1:
					grade = float(slope)*float(xgrades[index])+float(intercept)
					# grade = float(format(grade, '.2'))
					predictedYGrades.append(grade)
				if power == 2:
					grade = float(a)*pow(float(xgrades[index]), 2)+float(b)*float(xgrades[index])+float(c)
					# grade = float(format(grade, '.2'))
					predictedYGrades.append(grade)

			acc = self.computePredictionPrecision(ygrades, predictedYGrades)
			if len(acc) == 0:
				continue

			# form the precision row for this prediction course pair
			corrRow = self.getPredictingPredictedCorrRow(courseX, courseY, predictorFile)
			precisionRow = corrRow[:6]+acc
			writer.writerow(precisionRow)

			gw.writerows([ygrades, predictedYGrades, precisionRow, ['']])
