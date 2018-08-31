#!/usr/bin/env python
import rawData, sys, variables
import preprocessCurrentTrainingSet as preprocess
import predictCurrentTestingSet as predict

# import platform
# print platform.python_version()

# split the raw reg and deg datasets into single year data lists
prepare = rawData.splitRawData(sys.argv)
prepare.doBatch()
# obtain the reg, deg lists as well as the year list and the raw reg, deg datasets
# regFileList, degFileList, yearList, regcsv, degcsv = prepare.splitedRawData()

commVars = variables.commonVariables()

for trainingSet in commVars.getTrainingSets():
	print trainingSet
	preprocess.preprocessCurrentTrainingSet().preprocess(trainingSet)
	testingSets = commVars.getCurrentTrainingSetTestingSets(trainingSet)
	for testingSet in testingSets:
		
		test_CRS_STU = commVars.getCurrentTestingSetCourseStudentMatrixFileWithBlanks(trainingSet, testingSet)
		corrFile = commVars.getCurrentTrainingSetCorrelationFile(trainingSet)
		corrFilteredFile = commVars.getCurrentTrainingSetCorrelationFileFilteredByPValue(trainingSet)

		# For Linear
		corrLinearPredictionResult = commVars.getCurrentTestingSetLinearPredictionResultFile(trainingSet, testingSet)
		corrLinearFilteredPredictionResult = commVars.getCurrentTestingSetLinearPredictionFilteredResultFile(trainingSet, testingSet)
		predict.predictCurrentTestingSet().createPredictionResults(test_CRS_STU, corrLinearPredictionResult, 1, corrFile)
		predict.predictCurrentTestingSet().createPredictionResults(test_CRS_STU, corrLinearFilteredPredictionResult, 1, corrFilteredFile)

		# For Quadratic
		corrQuaPredictionResult = commVars.getCurrentTestingSetQuadraticPredictionResultFile(trainingSet, testingSet)
		corrQuaFilteredPredictionResult = commVars.getCurrentTestingSetQuadraticPredictionFilteredResultFile(trainingSet, testingSet)
		predict.predictCurrentTestingSet().createPredictionResults(test_CRS_STU, corrQuaPredictionResult, 2, corrFile)
		predict.predictCurrentTestingSet().createPredictionResults(test_CRS_STU, corrQuaFilteredPredictionResult, 2, corrFilteredFile)

# print the current top directory
# print variables.commonVariables().getCurrentTopDirectory()
# print variables.commonVariables().getCurrentTrainingSetTopDirectory(['2010', '2011'])
# print variables.commonVariables().getCurrentTrainingSetDataDirectory(['2010', '2011'])
# print variables.commonVariables().getCurrentTrainingSetLinearPlotsDirectory(['2010', '2011'])
# print variables.commonVariables().getCurrentTrainingSetQuadraticPlotsDirectory(['2010', '2011'])
# print variables.commonVariables().getCurrentTrainingSetBoxPlotsDirectory(['2010', '2011'])
# print variables.commonVariables().getCurrentUserDirectory()
# print variables.commonVariables().getAllTechCursesFromSchedules()
# print variables.commonVariables().getSplitDataDirectory()
# print variables.commonVariables().getCurrentTrainingSetAvailableTechCourses('/Users/rexlei/Work/srv/REG_withE199_20160628.csv')


