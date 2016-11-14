#!/usr/bin/env python

import regrmdup, rawData, sys, MTIS, Validate

validate, mtis, split = True, False, False

if validate:
	Validate.myValidate(sys.argv).doBatch()
elif mtis:
	# build MTIS data
	MTIS.myMTIS(sys.argv).matrixBuilder()
elif split:
	prepare = rawData.splitRawData(sys.argv)
	prepare.doBatch()
else:
	# compute thesis data
	prepare = rawData.splitRawData(sys.argv)
	prepare.doBatch()
	regrmdup.prepross(prepare.splitedRawData()).doBatch()
