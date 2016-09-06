import regrmdup, rawData, sys, MTIS

skip = True
if not skip:
	# build MTIS data
	MTIS.myMTIS(sys.argv).matrixBuilder()
else:
	# compute thesis data
	prepare = rawData.splitRawData(sys.argv)
	prepare.doBatch()
	regrmdup.prepross(prepare.splitedRawData()).doBatch()
