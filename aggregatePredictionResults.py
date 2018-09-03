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

		
		workbook = xlsxwriter.Workbook(mergedCrsAccFile)
		myformat = workbook.add_format({'align':'center_across'})
		worksheetALL, rowcntALL = workbook.add_worksheet('ALL'), 0

		# w = csv.writer(open(mergedCrsAccFile, 'w'))
		for key, value in crsAccDict.items():
			valueDict = self.groupCourses(value, crsSortIndex, numSortIndex)
			worksheetCrs, rowcntCrs = workbook.add_worksheet(key), 0
			for vkey, vvalue in valueDict.items():
				vvalue.sort(key=itemgetter(9), reverse=True)
				for row in [['TrainingSet']+header]+vvalue+['']:
					worksheetALL.write_row(rowcntALL,0,row,myformat)
					worksheetCrs.write_row(rowcntCrs,0,row,myformat)
					rowcntALL += 1
					rowcntCrs += 1
				# w.writerows([['TrainingSet']+header]+vvalue+[''])


	def groupCourses(self, values, crsSortIndex, numSortIndex):
		valueDict = {}
		for row in values:
			key = row[crsSortIndex]+row[numSortIndex]
			if key in valueDict:
				valueDict[key].append(row)
			else:
				valueDict[key] = [row]

		return valueDict


