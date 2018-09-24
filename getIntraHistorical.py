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


##### DEBUG BULLSHIT #####  ##### DEBUG BULLSHIT #####  ##### DEBUG BULLSHIT #####      
# dataLogDF = pd.read_csv('D:/Projects/RH/RH_Working_Test/TEST2.csv')        
# dayMonYr = '16-07-18'
# marketOpen  = datetime.datetime.strptime(dayMonYr + ' 09:30:00', '%d-%m-%y %H:%M:%S')
# marketClose = datetime.datetime.strptime(dayMonYr + ' 16:00:00', '%d-%m-%y %H:%M:%S')
# MAX_RETRY_PER_SYMBOL = 3
# sleepTimer = 10

# for row in dataLogDF.itertuples(index = True, name = 'Pandas'):
    # commentTime = datetime.datetime.strptime(row.Date + ' ' + row.Time, '%d-%m-%y %H:%M:%S')
    # commentTime = roundTime(commentTime)
    
    # if commentTime > marketOpen and commentTime < marketClose:
        # try:
            # print('Attempting to get data information')
            # time.sleep(3)
            # stockPrice = getPrice(row.Stock, commentTime, dayMonYr)
            # print('Got data for', row.Stock, 'on first call')
        # except:
            # print("Couldn't get data on first call. Trying", str(MAX_RETRY_PER_SYMBOL), "more times!")
            # for retry_cnt in range(MAX_RETRY_PER_SYMBOL):
                # time.sleep(sleepTimer)
                # try:
                    # print('AlphaVantage denied requests. Waiting', str(sleepTimer), 'seconds')
                    # stockPrice = getPrice(row.Stock, commentTime, dayMonYr)
                    # sleepTimer = 10
                    # break
                # except:
                    # print("Failed to get data for", row.Stock, "within", retry_cnt+1, "tries.")
                    # sleepTimer += 10
                    # continue
            # else:
                # raise
            
        # dataLogDF.loc[row.Index, 'Price'] = stockPrice
        
# print('Finished with stocks')
##### DEBUG BULLSHIT #####  ##### DEBUG BULLSHIT #####  ##### DEBUG BULLSHIT #####  