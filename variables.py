#!/usr/bin/env python
import time, sys, csv, os

class commonVariables(object):
	"""docstring for commonVariables"""
	def __init__(self):
		super(commonVariables, self).__init__()


	# Global variables
	def getCurrentUserDirectory(self):
		if sys.version_info[0] < 3:
			from os.path import expanduser
			return expanduser("~")+'/'
		else:
			from pathlib import Path
			return str(Path.home())+'/'

	def getSplitDataDirectory(self):
		path = self.getCurrentUserDirectory()+'Work/users/splits/'
		if not os.path.exists(path):
			os.makedirs(path)
		return path

	def getAllTechCursesFromSchedules(self):
		file = self.getCurrentUserDirectory()+'Work/users/techcourses/technicalCourse.csv'
		# the technical course file does not have a header
		techList = []
		reader = csv.reader(open(file), delimiter = ',')
		[techList.append(row[0]+row[1]) for row in reader]

		return techList

	def getCurrentTopDirectory(self):
		path = self.getCurrentUserDirectory()+'Google Drive/'+time.strftime('%Y%m%d')+'_debug/'
		if not os.path.exists(path):
			os.makedirs(path)
		return path		

	def getTrainingSets(self):
		splitPath = self.getSplitDataDirectory()
		return [splitPath+'reg2010-2011.csv', splitPath+'reg2010-2012.csv', splitPath+'reg2010-2013.csv', splitPath+'reg2010-2014.csv']


	def getMergedXCourseLinearOriginCorrPredictionResultsForAllTrainingSets(self):
		return self.getCurrentTopDirectory()+'mergedXCourseLinearOriginCorrPredictionAcc4AllTrainingSets.xlsx'

	def getMergedXCourseQuaOriginCorrPredictionResultsForAllTrainingSets(self):
		return self.getCurrentTopDirectory()+'mergedXCourseQuaOriginCorrPredictionAcc4AllTrainingSets.xlsx'

	def getMergedXCourseLinearFilteredCorrPredictionResultsForAllTrainingSets(self):
		return self.getCurrentTopDirectory()+'mergedXCourseLinearFilteredCorrPredictionAcc4AllTrainingSets.xlsx'

	def getMergedXCourseQuaFilteredCorrPredictionResultsForAllTrainingSets(self):
		return self.getCurrentTopDirectory()+'mergedXCourseQuaFilteredCorrPredictionAcc4AllTrainingSets.xlsx'

	def getMergedYCourseLinearOriginCorrPredictionResultsForAllTrainingSets(self):
		return self.getCurrentTopDirectory()+'mergedYCourseLinearOriginCorrPredictionAcc4AllTrainingSets.xlsx'

	def getMergedYCourseQuaOriginCorrPredictionResultsForAllTrainingSets(self):
		return self.getCurrentTopDirectory()+'mergedYCourseQuaOriginCorrPredictionAcc4AllTrainingSets.xlsx'

	def getMergedYCourseLinearFilteredCorrPredictionResultsForAllTrainingSets(self):
		return self.getCurrentTopDirectory()+'mergedYCourseLinearFilteredCorrPredictionAcc4AllTrainingSets.xlsx'

	def getMergedYCourseQuaFilteredCorrPredictionResultsForAllTrainingSets(self):
		return self.getCurrentTopDirectory()+'mergedYCourseQuaFilteredCorrPredictionAcc4AllTrainingSets.xlsx'
	
	# Variables for specific training dataset
	def getCurrentTrainingSetTestingSets(self, trainingSet):
		splitPath = self.getSplitDataDirectory()
		trainingSetTimeSlotString = self.getCurrentTrainingSetTimeSlotString(trainingSet)
		if trainingSetTimeSlotString == '2010-2011':
			return [splitPath+'reg2012.csv', splitPath+'reg2013.csv', splitPath+'reg2014.csv', splitPath+'reg2015.csv', splitPath+'reg2012-2015.csv']
		if trainingSetTimeSlotString == '2010-2012':
			return [splitPath+'reg2013.csv', splitPath+'reg2014.csv', splitPath+'reg2015.csv', splitPath+'reg2013-2015.csv']
		if trainingSetTimeSlotString == '2010-2013':
			return [splitPath+'reg2014.csv', splitPath+'reg2015.csv', splitPath+'reg2014-2015.csv']
		if trainingSetTimeSlotString == '2010-2014':
			return [splitPath+'reg2015.csv']

	def getCurrentTestingSetTimeSlotString(self, testingSet):
		return testingSet.split('/')[-1].split('.')[0][3:]

	def getCurrentTestingDirectory(self, trainingSet, testingSet):
		path = self.getCurrentTrainingSetTestDirectory(trainingSet)+self.getCurrentTestingSetTimeSlotString(testingSet)+'/'
		if not os.path.exists(path):
			os.makedirs(path)
		return path

	# prediction results files for courseX or courseY
	def getCurrentTestingSetPredictionResultFile(self, trainingSet, testingSet, courseXY, factor, linearQuadra):
		return self.getCurrentTestingDirectory(trainingSet, testingSet)+self.getCurrentTestingSetTimeSlotString(testingSet)+'_'+courseXY+'_'+factor+'_'+linearQuadra+'_Prediction.csv'

	def getCurrentTrainingSetMergedPredictionResultsFile(self, trainingSet, factor, LinearQuadra):
		return self.getCurrentTrainingSetDataDirectory(trainingSet)+self.getCurrentTrainingSetTimeSlotString(trainingSet)+'_'+factor+'_'+LinearQuadra+'_Picked.xlsx'

	def getCurrentTestingSetLinearPredictionResultFile(self, trainingSet, testingSet):
		return self.getCurrentTestingDirectory(trainingSet, testingSet)+self.getCurrentTestingSetTimeSlotString(testingSet)+'corrPredictionResults_Linear.csv'

	def getCurrentTestingSetLinearPredictionFilteredResultFile(self, trainingSet, testingSet):
		return self.getCurrentTestingDirectory(trainingSet, testingSet)+self.getCurrentTestingSetTimeSlotString(testingSet)+'corrFilteredPredictionResults_Linear.csv'

	def getCurrentTestingSetQuadraticPredictionResultFile(self, trainingSet, testingSet):
		return self.getCurrentTestingDirectory(trainingSet, testingSet)+self.getCurrentTestingSetTimeSlotString(testingSet)+'corrPredictionResults_Qua.csv'

	def getCurrentTestingSetQuadraticPredictionFilteredResultFile(self, trainingSet, testingSet):
		return self.getCurrentTestingDirectory(trainingSet, testingSet)+self.getCurrentTestingSetTimeSlotString(testingSet)+'corrFilteredPredictionResults_Qua.csv'

	def getCurrentTestingSetUniqueCourseFile(self, trainingSet, testingSet):
		return self.getCurrentTestingDirectory(trainingSet, testingSet)+self.getCurrentTestingSetTimeSlotString(testingSet)+'NODUP.csv'

	def getCurrentTestingSetTechCourseFile(self, trainingSet, testingSet):
		return self.getCurrentTestingDirectory(trainingSet, testingSet)+self.getCurrentTestingSetTimeSlotString(testingSet)+'Tech.csv'

	def getCurrentTestingSetUniqueTechCourseFile(self, trainingSet, testingSet):
		return self.getCurrentTestingDirectory(trainingSet, testingSet)+self.getCurrentTestingSetTimeSlotString(testingSet)+'Tech_NODUP.csv'

	def getCurrentTestingSetStudentEnrolmentFrequencyFile(self, trainingSet, testingSet):
		return self.getCurrentTestingDirectory(trainingSet, testingSet)+self.getCurrentTestingSetTimeSlotString(testingSet)+'Student_EnrolmentFrequency.csv'

	def getCurrentTestingSetCourseEnrolmentFrequencyFile(self, trainingSet, testingSet):
		return self.getCurrentTestingDirectory(trainingSet, testingSet)+self.getCurrentTestingSetTimeSlotString(testingSet)+'Course_EnrolmentFrequency.csv'

	def getCurrentTestingSetCourseStudentMatrixFileWithBlanks(self, trainingSet, testingSet):
		return self.getCurrentTestingDirectory(trainingSet, testingSet)+self.getCurrentTestingSetTimeSlotString(testingSet)+'CRS_STU.csv'

	def getCurrentTestingSetCourseStudentMatrixWithLetterGrades(self, trainingSet, testingSet):
		return self.getCurrentTestingDirectory(trainingSet, testingSet)+self.getCurrentTestingSetTimeSlotString(testingSet)+'CRS_Letter_Grade_Matrix.csv'

	def getCurrentTestingSetStudentCourseMatrixFileWithBlanks(self, trainingSet, testingSet):
		return self.getCurrentTestingDirectory(trainingSet, testingSet)+self.getCurrentTestingSetTimeSlotString(testingSet)+'STU_CRS.csv'
	
	def getCurrentTestingSetStudentCourseMatrixWithoutBlanks(self, trainingSet, testingSet):
		return self.getCurrentTestingDirectory(trainingSet, testingSet)+self.getCurrentTestingSetTimeSlotString(testingSet)+'STU_CRS_Grade.csv'

	def getCurrentTestingSetHeader(self, testingSet):
		return csv.reader(open(testingSet), delimiter=',').next()



	def getCurrentTrainingSetTimeSlotString(self, trainingSet):
		return trainingSet.split('/')[-1].split('.')[0][3:]

	def getCurrentTrainingSetTopDirectory(self, trainingSet):
		path = self.getCurrentTopDirectory()+self.getCurrentTrainingSetTimeSlotString(trainingSet)+'/'
		if not os.path.exists(path):
			os.makedirs(path)
		return path

	def getCurrentTrainingSetDataDirectory(self, trainingSet):
		path = self.getCurrentTrainingSetTopDirectory(trainingSet)+"data/"
		if not os.path.exists(path):
			os.makedirs(path)
		return path

	def getCurrentTrainingSetLinearPlotsDirectory(self, trainingSet):
		path = self.getCurrentTrainingSetTopDirectory(trainingSet)+"LPlots_ori/"
		if not os.path.exists(path):
			os.makedirs(path)
		return path

	def getCurrentTrainingSetQuadraticPlotsDirectory(self, trainingSet):
		path = self.getCurrentTrainingSetTopDirectory(trainingSet)+"QPlots_ori/"
		if not os.path.exists(path):
			os.makedirs(path)
		return path

	def getCurrentTrainingSetBoxPlotsDirectory(self, trainingSet):
		path = self.getCurrentTrainingSetTopDirectory(trainingSet)+"boxPlots/"
		if not os.path.exists(path):
			os.makedirs(path)
		return path

	def getCurrentTrainingSetTrainDirectory(self, trainingSet):
		path = self.getCurrentTrainingSetDataDirectory(trainingSet)+'Train/'
		if not os.path.exists(path):
			os.makedirs(path)
		return path

	def getCurrentTrainingSetTestDirectory(self, trainingSet):
		path = self.getCurrentTrainingSetDataDirectory(trainingSet)+'Test/'
		if not os.path.exists(path):
			os.makedirs(path)
		return path

	def getCurrentTrainingSetNoCommonStudentCourseDirectory(self, trainingSet):
		path = self.getCurrentTrainingSetTrainDirectory(trainingSet)+'nocomstu/'
		if not os.path.exists(path):
			os.makedirs(path)
		return path

	def getCurrentTrainingSetNoCorrelationCourseDirectory(self, trainingSet):
		path = self.getCurrentTrainingSetTrainDirectory(trainingSet)+'nocorr/'
		if not os.path.exists(path):
			os.makedirs(path)
		return path

	def getCurrentTraingSetMergedTestingSet(self, trainingSet):
		splitPath = self.getSplitDataDirectory()
		trainingSetTimeSlotString = self.getCurrentTrainingSetTimeSlotString(trainingSet)
		if trainingSetTimeSlotString == '2010-2011':
			return splitPath+'reg2012-2015.csv'
		if trainingSetTimeSlotString == '2010-2012':
			return splitPath+'reg2013-2015.csv'
		if trainingSetTimeSlotString == '2010-2013':
			return splitPath+'reg2014-2015.csv'
		if trainingSetTimeSlotString == '2010-2014':
			return splitPath+'reg2015.csv'

	def getCurrentTrainingSetAvailableTechCourses(self, trainingSet):
		availableTechCrsList = []
		techList = self.getAllTechCursesFromSchedules()

		r = csv.reader(open(trainingSet), delimiter=',')
		for row in r:
			course = row[3].replace(' ','')+row[4].replace(' ','')
			# change MATH 110 ===> MATH 133; ENGR 110 ===> ENGR 111
			if course == 'MATH110':
				course = 'MATH133'

			if course == 'ENGR110':
				course = 'ENGR111'

			if course in techList and course not in availableTechCrsList:
				# save the available technical course list for future use
				availableTechCrsList.append(course)

		return availableTechCrsList

	def getCurrentTrainingSetHeader(self, trainingSet):
		return csv.reader(open(trainingSet), delimiter=',').next()

	def getCurrentTrainingSetNonDuplicateGradesFile(self, trainingSet):
		return self.getCurrentTrainingSetTrainDirectory(trainingSet)+'NODUP.csv'

	def getCurrentTrainingSetTechCourseFile(self, trainingSet):
		return self.getCurrentTrainingSetTrainDirectory(trainingSet)+'Tech.csv'

	def getCurrentTrainingSetNonDuplicateTechGradesFile(self, trainingSet):
		return self.getCurrentTrainingSetTrainDirectory(trainingSet)+'TECH_NODUP.csv'

	def getCurrentTrainingSetEncryptedGradesFile(self, trainingSet):
		return self.getCurrentTrainingSetTrainDirectory(trainingSet)+'Encrypted.csv'

	def getCurrentTrainingSetUniqueEncryptedGradesFile(self, trainingSet):
		return self.getCurrentTrainingSetTrainDirectory(trainingSet)+'Encrypted_Unique.csv'

	def getCurrentTrainingSetCourseEnrolmentFrequencyFile(self, trainingSet):
		return self.getCurrentTrainingSetTrainDirectory(trainingSet)+'Course_EnrolmentFrequency.csv'

	def getCurrentTrainingSetStudentEnrolmentFrequencyFile(self, trainingSet):
		return self.getCurrentTrainingSetTrainDirectory(trainingSet)+'Student_EnrolmentFrequency.csv'

	def getCurrentTrainingSetEmptyGradesFile(self, trainingSet):
		return self.getCurrentTrainingSetTrainDirectory(trainingSet)+'Empty.csv'

	def getCurrentTrainingSetEmptyCourseFile(self, trainingSet):
		return self.getCurrentTrainingSetTrainDirectory(trainingSet)+'Empty_Course.csv'

	def getCurrentTrainingSetEmptyStudentFile(self, trainingSet):
		return self.getCurrentTrainingSetTrainDirectory(trainingSet)+'Empty_Student.csv'

	def getCurrentTrainingSetCourseStudentMatrixFileWithBlanks(self, trainingSet):
		return self.getCurrentTrainingSetTrainDirectory(trainingSet)+'CRS_STU.csv'

	def getCurrentTrainingSetCourseStudentMatrixWithoutBlanks(self, trainingSet):
		return self.getCurrentTrainingSetTrainDirectory(trainingSet)+'CRS_Matrix.csv'

	def getCurrentTrainingSetCourseStudentMatrixWithLetterGrades(self, trainingSet):
		return self.getCurrentTrainingSetTrainDirectory(trainingSet)+'CRS_Letter_Grade_Matrix.csv'

	def getCurrentTrainingSetStudentCourseMatrixFileWithBlanks(self, trainingSet):
		return self.getCurrentTrainingSetTrainDirectory(trainingSet)+'STU_CRS.csv'

	def getCurrentTrainingSetStudentCourseMatrixWithoutBlanks(self, trainingSet):
		return self.getCurrentTrainingSetTrainDirectory(trainingSet)+'STU_CRS_Grade.csv'

	def getCurrentTrainingSetStudentCourseMatrixWithLetterGrades(self, trainingSet):
		return self.getCurrentTrainingSetTrainDirectory(trainingSet)+'STU_Letter_Grade_Matrix.csv'

	def getCurrentTrainingSetDiscardCourseFile(self, trainingSet):
		return self.getCurrentTrainingSetTrainDirectory(trainingSet)+'Discard.csv'

	def getCurrentTrainingSetUniqueCourseFile(self, trainingSet):
		return self.getCurrentTrainingSetTrainDirectory(trainingSet)+'UniqueCourseList.csv'

	def getCurrentTrainingSetUniqueTechCourseFile(self, trainingSet):
		return self.getCurrentTrainingSetTrainDirectory(trainingSet)+'UniqueTechCourseList.csv'

	def getCurrentTrainingSetNoCoefficientCourseFile(self, trainingSet):
		return self.getCurrentTrainingSetTrainDirectory(trainingSet)+'NoCoefficientCourseList.csv'

	def getCurrentTrainingSetCoursePairsFile(self, trainingSet):
		return self.getCurrentTrainingSetTrainDirectory(trainingSet)+'CRS_Pairs.csv'

	def getCurrentTrainingSetCorrelationFile(self, trainingSet):
		return self.getCurrentTrainingSetDataDirectory(trainingSet)+'PearsonCorr.csv'

	def getCurrentTrainingSetCorrelationFileFilteredByPValue(self, trainingSet):
		return self.getCurrentTrainingSetDataDirectory(trainingSet)+'PearsonCorrFiltered.csv'

	# courseXY: CourseX or CourseY
	# factor: P: enrolemtn, r: coefficient, pxy: combination of p and r
	def getCurrentTrainingSetPredictorsFile(self, trainingSet, courseXY, factor):
		return self.getCurrentTrainingSetDataDirectory(trainingSet)+ self.getCurrentTestingSetTimeSlotString(trainingSet)+'_Predictors_'+courseXY+'_'+factor+'.csv'

	def getCurrentTrainingSetSkewnessFile(self, trainingSet):
		return self.getCurrentTrainingSetDataDirectory(trainingSet)+'skewness.csv'

	def getCurrentTrainingSetNoCommonStudentCourseFile(self, trainingSet):
		return self.getCurrentTrainingSetNoCommonStudentCourseDirectory(trainingSet)+'nocomstu_list.csv'

	def getCurrentTrainingSetNoCommonStudentCourseFrequencyFile(self, trainingSet):
		return self.getCurrentTrainingSetNoCommonStudentCourseDirectory(trainingSet)+'nocomstu_list_fre.csv'

	def getCurrentTrainingSetNoCorrelationCourseFile(self, trainingSet):
		return self.getCurrentTrainingSetNoCorrelationCourseDirectory(trainingSet)+'no_corr_list.csv'

	def getCurrentTrainingSetNoCorrelationCourseFrequencyFile(self, trainingSet):
		return self.getCurrentTrainingSetNoCorrelationCourseDirectory(trainingSet)+'no_corr_list_fre.csv'

# fileNameList = ['REPL.csv', 'NODUP.csv', 'TECH_NODUP.csv', 'CRSPERSTU.csv', 'STUREGISTERED.csv', 'EMPTY.csv', 'EMPTY_STU.csv', 'EMPTY_CRS.csv', 'CRS_STU.csv', 'CRS_STU_GRADE.csv', 'NODUP_REPL.csv', 'STU_CRS.csv', 'STU_CRS_GRADE.csv', 'CRS_MATRIX.csv', 'DISCARD.csv', 'uniCourseList.csv', 'uniTechCrsList.csv', 'TECH.csv', 'nan.csv', 'CRS_PAIRS.csv']


