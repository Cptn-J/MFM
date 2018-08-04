### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ###
#
# Author        : Austin Brockner
# Creation Date : 11/8/17
# Details       : Used to search a specific trading database for a ticker. 
#
### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ###

import pandas as pd

def checkStock(ticker,tickerFile):
	dataFile = pd.read_csv(tickerFile)
	symbolCol = dataFile.Symbol
	
	if symbolCol.str.contains(ticker).any():
		return True
		print (ticker + "exists in" + tickerFile)
	else:
		return False