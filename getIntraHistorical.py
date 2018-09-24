### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ###
#
# Author        : Austin Brockner
# Creation Date : 07/07/18
# Last Updated  : 07/07/18
# Details       : Used to compare a stocks value vs number of mentions over a time span
#
### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ###

## First import libraries
# 'pandas' for data management
# 'json' for JSON scrubbing
# 'datetime' for date management
# 'pdb' for debugging
# 'urlopen' to request stock data from AlphaVantage
import pandas as pd
import json
import datetime
import pdb
from urllib.request import Request, urlopen
from urllib.error import URLError

import time

def getPrice(ticker, stockTime, stockDate, inputKey):
    # Request data from AlphaVantage (an independent website with a user friendly API)
    # site   = specific html to AlphaVantage site for a specific function
    # symbol = desired ticker symbol
    # size   = interval size on intraday (1m, 5m, 15m, 30m, 60m) & 
    #          output size (compact[default] only 100 mins from current time or full [every min of day]
    # key    = required API key to use AlphaVantage
    site = "https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY"
    symbol = "&symbol=" + ticker.upper()
    size = "&interval=1min&outputsize=compact"
    keyPart1 = "&apikey="
    keyPart2 = inputKey
    fullUrl = site + symbol + size + keyPart1 + keyPart2
    
    try:
        # Utilze native urlopen and json library to open website of data and download json data into dictionary
        #with urllib.request.urlopen(fullUrl) as response:
        alphaRequest = Request(fullUrl)
        response = urlopen(alphaRequest)
        alphaDailyData = json.load(response)

        if 'Time Series (1min)' in alphaDailyData.keys():        
            # Date must be changed from the "StockHits" format to the "AlphaVantage" format to query dictionary
            alphaDate = datetime.datetime.strptime(stockDate, '%d-%m-%y').strftime('%Y-%m-%d')
            stockDates = list(alphaDailyData['Time Series (1min)'].keys())
            stockDates = [dayMonYr.split()[0] for dayMonYr in stockDates]
            stockDates = list(set(stockDates))
            searchTime = ' '.join([alphaDate, stockTime.strftime('%H:%M:%S')])
            
            if searchTime in alphaDailyData['Time Series (1min)'].keys():
                open = float(alphaDailyData['Time Series (1min)'][searchTime]['1. open'])
                #-*-*-*-*-#  High, Low, Close, and Volume are not currently needed #-*-*-*-*-#
                # high    = float(alphaDailyData['Time Series (1min)'][searchTime]['2. high'])
                # low     = float(alphaDailyData['Time Series (1min)'][searchTime]['3. low'])
                # close   = float(alphaDailyData['Time Series (1min)'][searchTime]['4. close'])
                # volume  = float(alphaDailyData['Time Series (1min)'][searchTime]['5. volume'])
            else:
                print('Data for', ticker, 'at', searchTime, 'does not exist on Alpha Vantage.')
                open = '-'
        
            return open
        else:
            print('Alpha Vantage did not load data.')
            raise

    except URLError as e:
        if hasattr(e, 'reason'):
            print('We failed to reach a server.')
            print('Reason: ', e.reason)
        elif hasattr(e, 'code'):
            print('The server couldn\'t fulfill the request.')
            print('Error code: ', e.code)
        

def roundTime(timeInDTFormat):
    if timeInDTFormat.second <= 29:
        roundedTime = timeInDTFormat.replace(second=0)
    else:
        roundedTime = timeInDTFormat.replace(minute=timeInDTFormat.minute+1, second = 0)
        
    if roundedTime.minute > 60:
        roundedTime = roundedTime.replace(hour=roundedTime.hour+1,minute=0)
        
    return roundedTime        
