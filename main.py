import regrmdup, rawData, sys, MTIS, Validate

mtis = False
validate = True

if validate:
	Validate.myValidate(sys.argv).doBatch()

elif mtis:
	# build MTIS data
	MTIS.myMTIS(sys.argv).matrixBuilder()
else:
	# compute thesis data
	prepare = rawData.splitRawData(sys.argv)
	prepare.doBatch()
	regrmdup.prepross(prepare.splitedRawData()).doBatch()
