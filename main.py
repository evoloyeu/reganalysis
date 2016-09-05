import regrmdup, rawData, sys

prepare = rawData.splitRawData(sys.argv)
prepare.doBatch()
regrmdup.prepross(prepare.splitedRawData()).doBatch()
