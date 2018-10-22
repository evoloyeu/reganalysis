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

		# =============================================Start: Prediction CourseX/Y-based=======================================================
		# CourseX-based prediction results files
		xpl = commVars.getCurrentTestingSetPredictionResultFile(trainingSet, testingSet, "X", "#", "L")
		xrl = commVars.getCurrentTestingSetPredictionResultFile(trainingSet, testingSet, "X", "R", "L")
		xPxyl = commVars.getCurrentTestingSetPredictionResultFile(trainingSet, testingSet, "X", "Pxy", "L")

		# CourseY-based prediction files
		ypl = commVars.getCurrentTestingSetPredictionResultFile(trainingSet, testingSet, "Y", "#", "L")
		yrl = commVars.getCurrentTestingSetPredictionResultFile(trainingSet, testingSet, "Y", "R", "L")
		yPxyl = commVars.getCurrentTestingSetPredictionResultFile(trainingSet, testingSet, "Y", "Pxy", "L")
		
		# predictor files for CourseX-based
		xp = courseXEnrolmentPredictorFile = commVars.getCurrentTrainingSetPredictorsFile(trainingSet, 'X', '#')
		xr = courseXCoefficientPredictorFile = commVars.getCurrentTrainingSetPredictorsFile(trainingSet, 'X', 'R')
		xPxy = courseXPxyPredictorFile = commVars.getCurrentTrainingSetPredictorsFile(trainingSet, 'X', 'Pxy')
		
		# predictor files for CourseY-based
		yp = courseYEnrolmentPredictorFile = commVars.getCurrentTrainingSetPredictorsFile(trainingSet, 'Y', '#')
		yr = courseYCoefficientPredictorFile = commVars.getCurrentTrainingSetPredictorsFile(trainingSet, 'Y', 'R')
		yPxy = courseYPxyPredictorFile = commVars.getCurrentTrainingSetPredictorsFile(trainingSet, 'Y', 'Pxy')

		# X: linear only
		predict.predictCurrentTestingSet().createPredictionResults(test_CRS_STU, xpl, 1, xp)
		predict.predictCurrentTestingSet().createPredictionResults(test_CRS_STU, xrl, 1, xr)
		predict.predictCurrentTestingSet().createPredictionResults(test_CRS_STU, xPxyl, 1, xPxy)

		# Y: linear only
		predict.predictCurrentTestingSet().createPredictionResults(test_CRS_STU, ypl, 1, yp)
		predict.predictCurrentTestingSet().createPredictionResults(test_CRS_STU, yrl, 1, yr)
		predict.predictCurrentTestingSet().createPredictionResults(test_CRS_STU, yPxyl, 1, yPxy)

		# =====================================================================================================================================

		xpq = commVars.getCurrentTestingSetPredictionResultFile(trainingSet, testingSet, "X", "#", "Q")
		xrq = commVars.getCurrentTestingSetPredictionResultFile(trainingSet, testingSet, "X", "R", "Q")
		xPxyq = commVars.getCurrentTestingSetPredictionResultFile(trainingSet, testingSet, "X", "Pxy", "Q")

		# CourseY-based prediction files
		ypq = commVars.getCurrentTestingSetPredictionResultFile(trainingSet, testingSet, "Y", "#", "Q")
		yrq = commVars.getCurrentTestingSetPredictionResultFile(trainingSet, testingSet, "Y", "R", "Q")
		yPxyq = commVars.getCurrentTestingSetPredictionResultFile(trainingSet, testingSet, "Y", "Pxy", "Q")

		# X: quadratic only
		predict.predictCurrentTestingSet().createPredictionResults(test_CRS_STU, xpq, 2, xp)
		predict.predictCurrentTestingSet().createPredictionResults(test_CRS_STU, xrq, 2, xr)
		predict.predictCurrentTestingSet().createPredictionResults(test_CRS_STU, xPxyq, 2, xPxy)

		# Y: quadratic only
		predict.predictCurrentTestingSet().createPredictionResults(test_CRS_STU, ypq, 2, yp)
		predict.predictCurrentTestingSet().createPredictionResults(test_CRS_STU, yrq, 2, yr)
		predict.predictCurrentTestingSet().createPredictionResults(test_CRS_STU, yPxyq, 2, yPxy)
		# =============================================End: Prediction CourseX/Y-based=========================================================

		# For Quadratic
		corrQuaPredictionResult = commVars.getCurrentTestingSetQuadraticPredictionResultFile(trainingSet, testingSet)
		corrQuaFilteredPredictionResult = commVars.getCurrentTestingSetQuadraticPredictionFilteredResultFile(trainingSet, testingSet)
		predict.predictCurrentTestingSet().createPredictionResults(test_CRS_STU, corrQuaPredictionResult, 2, corrFile)
		predict.predictCurrentTestingSet().createPredictionResults(test_CRS_STU, corrQuaFilteredPredictionResult, 2, corrFilteredFile)

	# merge prediction results to one xlsx file as per factor
	preprocess.preprocessCurrentTrainingSet().mergePredictionResults(trainingSet, '#', 'L')
	preprocess.preprocessCurrentTrainingSet().mergePredictionResults(trainingSet, 'R', 'L')
	preprocess.preprocessCurrentTrainingSet().mergePredictionResults(trainingSet, 'Pxy', 'L')

	preprocess.preprocessCurrentTrainingSet().mergePredictionResults(trainingSet, '#', 'Q')
	preprocess.preprocessCurrentTrainingSet().mergePredictionResults(trainingSet, 'R', 'Q')
	preprocess.preprocessCurrentTrainingSet().mergePredictionResults(trainingSet, 'Pxy', 'Q')


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


