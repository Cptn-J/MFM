### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ###
#
# Author        : Austin Brockner
# Creation Date : 05/31/18
# Last Updated  : 05/31/18
# Details       : Used to pull stock metrics from financial visualizations website finviz.com
#
### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ###

## First import libraries
# 'pandas' for data management
# 'BeautifulSoup' for HTML scrubbing
# 'requests' for HTTP access
# 'time' for pausing program
# 'pdb' for debugging
import pandas as pd
from bs4 import BeautifulSoup as bs
import requests
import time
import pdb

def getFundamentalData(tickerDF):
    
    badTickers = []
    for ticker in tickerDF.index:
        try:
            # First find finviz webpage for specific stock ticker
            url = ("http://finviz.com/quote.ashx?t=" + ticker.lower())
            page = requests.get(url).content
            # Then create a 'soup' for the webpage
            soup = bs(page, 'html.parser')
            # Then go through the webpage and pull out appropriate stock metric values
            for metric in tickerDF.columns:
                nameCell = soup.find('td', string = metric)
                cellValue = nameCell.next_sibling.text.strip()
                tickerDF.loc[ticker,metric] = cellValue
            # Pause for 1 second after pulling a webpage to not overload the site with requests
            print ('Pulled metrics for: ', ticker)
            time.sleep(0.1)
        except Exception as e:
            # If for any reason we come across an error we'll throw a response
            print (ticker, 'not screened properly.')
            print ('Please ensure the ticker exists and that Finviz webpage has not changed.')
            print ('Error was triggered looking for "', metric, '"')
            badTickers.append(ticker)
    
    with open('listOfBadTickers.txt', 'a') as theFile:
        for badTicker in badTickers:
            theFile.write("%s\n" % badTicker)
    
    return tickerDF