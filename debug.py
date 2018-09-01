#!/usr/bin/env python
import variables
import preprocessCurrentTrainingSet as preprocess
import predictCurrentTestingSet as predict
import aggregatePredictionResults as agrregator

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


xlinearOrigin = commVars.getMergedXCourseLinearOriginCorrPredictionResultsForAllTrainingSets()
xquaorigin = commVars.getMergedXCourseQuaOriginCorrPredictionResultsForAllTrainingSets()
xlinearfiltered = commVars.getMergedXCourseLinearFilteredCorrPredictionResultsForAllTrainingSets()
xquafiltered = commVars.getMergedXCourseQuaFilteredCorrPredictionResultsForAllTrainingSets()

ylinearorigin = commVars.getMergedYCourseLinearOriginCorrPredictionResultsForAllTrainingSets()
yquaorigin = commVars.getMergedYCourseQuaOriginCorrPredictionResultsForAllTrainingSets()
ylinearfiltered = commVars.getMergedYCourseLinearFilteredCorrPredictionResultsForAllTrainingSets()
yquafiltered = commVars.getMergedYCourseQuaFilteredCorrPredictionResultsForAllTrainingSets()

agrregator.aggregatePredictionResults().mergeMergedTestingSetsPredictionResults(xlinearOrigin, 0, 1, 3, 4, 'L', 'O')
agrregator.aggregatePredictionResults().mergeMergedTestingSetsPredictionResults(xquaorigin, 0, 1, 3, 4, 'Q', 'O')
agrregator.aggregatePredictionResults().mergeMergedTestingSetsPredictionResults(xlinearfiltered, 0, 1, 3, 4, 'L', 'F')
agrregator.aggregatePredictionResults().mergeMergedTestingSetsPredictionResults(xquafiltered, 0, 1, 3, 4, 'Q', 'F')

agrregator.aggregatePredictionResults().mergeMergedTestingSetsPredictionResults(ylinearorigin, 2, 3, 1, 2, 'L', 'O')
agrregator.aggregatePredictionResults().mergeMergedTestingSetsPredictionResults(yquaorigin, 2, 3, 1, 2, 'Q', 'O')
agrregator.aggregatePredictionResults().mergeMergedTestingSetsPredictionResults(ylinearfiltered, 2, 3, 1, 2, 'L', 'F')
agrregator.aggregatePredictionResults().mergeMergedTestingSetsPredictionResults(yquafiltered, 2, 3, 1, 2, 'Q', 'F')

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


