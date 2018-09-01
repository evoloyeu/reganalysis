#!/usr/bin/env python
import variables
import xlsxwriter, csv
from operator import itemgetter

commVars = variables.commonVariables()

class aggregatePredictionResults(object):
	"""docstring for aggregatePredictionResults"""
	def __init__(self):
		super(aggregatePredictionResults, self).__init__()

	def mergeMergedTestingSetsPredictionResults(self, mergedCrsAccFile, crsKeyIndex, numKeyIndex, crsSortIndex, numSortIndex, linearQua, OriginFiltered):
		crsAccDict = {}
		header = ''
		for trainingSet in commVars.getTrainingSets():
			trainingSetTimeSlotStr = commVars.getCurrentTrainingSetTimeSlotString(trainingSet)
			mergedTestingSet = commVars.getCurrentTraingSetMergedTestingSet(trainingSet)

			mergedTestingSetAcc = ''
			if linearQua == 'L':
				if OriginFiltered == 'O':
					mergedTestingSetAcc = commVars.getCurrentTestingSetLinearPredictionResultFile(trainingSet, mergedTestingSet)
				else:
					mergedTestingSetAcc = commVars.getCurrentTestingSetLinearPredictionFilteredResultFile(trainingSet, mergedTestingSet)
			else:
				if OriginFiltered == 'O':
					mergedTestingSetAcc = commVars.getCurrentTestingSetQuadraticPredictionResultFile(trainingSet, mergedTestingSet)
				else:
					mergedTestingSetAcc = commVars.getCurrentTestingSetQuadraticPredictionFilteredResultFile(trainingSet, mergedTestingSet)

			r = csv.reader(open(mergedTestingSetAcc), delimiter=',')
			header = r.next()
			for row in r:
				key = row[crsKeyIndex]+row[numKeyIndex]
				if key in crsAccDict:
					crsAccDict[key].append([trainingSetTimeSlotStr] + row)
				else:
					crsAccDict[key] = [[trainingSetTimeSlotStr] + row]

		w = csv.writer(open(mergedCrsAccFile, 'w'))
		for key, value in crsAccDict.items():
			valueDict = self.groupCourses(value, crsSortIndex, numSortIndex)
			for vkey, vvalue in valueDict.items():
				vvalue.sort(key=itemgetter(9), reverse=True)
				w.writerows([['TrainingSet']+header]+vvalue+[''])


	def groupCourses(self, values, crsSortIndex, numSortIndex):
		valueDict = {}
		for row in values:
			key = row[crsSortIndex]+row[numSortIndex]
			if key in valueDict:
				valueDict[key].append(row)
			else:
				valueDict[key] = [row]

		return valueDict


