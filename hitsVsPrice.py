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
from urllib.request import urlopen
import matplotlib.pyplot as plt
import numpy as np
from sys import platform
from matplotlib.ticker import MaxNLocator

def hitsVsPrice(ticker, startDate = None, endDate = None, chartType = 'bar'):
    try:
        # Path to find all information (this should either be an input or default to this)
        # Check platform to determine how to properly declare file path and
        # add proper character to strftime to eliminate leading 0's
        if platform == 'win32':
            path = 'D:\\Projects\\RH\\RH_Working_Test\\'
        elif platform == 'darwin':
            path = '/Users/austinb/Desktop/Projects/RH_Working_070318/'
        else:
            print('This program has not been tested on this type of OS.')
            print('Exiting program.\n')
            exit()
        
        # Open Stock Hits file
        stockHitsDF = pd.read_csv(path + 'StockHits.csv')
        
        # If a start date isn't given for hitsVsPrice.py assume the start date is first date on Stock Hits Dataframe
        if (startDate == None):
            startDate = stockHitsDF.columns[1]
        # If a end date isn't given for hitsVsPrice.py assume the end date is last date on Stock Hits Dataframe
        if (endDate == None):
            endDate = stockHitsDF.columns[-1]
        
        # First identify our indexes for the row pertaining to the desired ticker, the column our startDate falls in, and
        # the column the endDate falls in.
        stockRow  = stockHitsDF.STOCK[stockHitsDF.STOCK == ticker].index.tolist()[0]
        startCol  = stockHitsDF.columns.get_loc(startDate)
        endCol    = stockHitsDF.columns.get_loc(endDate)
        # Then extract from the entire Dataframe only the information for the specific stock from specific dates
        dailyHits = stockHitsDF.loc[stockRow, startDate:endDate]
        
        # Request data from AlphaVantage (an independent website with a user friendly API)
        # site = specific html to AlphaVantage site for a specific function
        # symbol = desired ticker symbol
        # key = required API key to use AlphaVantage
        site = "https://www.alphavantage.co/query?function=TIME_SERIES_DAILY"
        symbol = "&symbol=" + ticker.upper()
        key = "&apikey=VYNTQ9X2CTZGVD5G"
        
        # Utilze native urlopen and json library to open website of data and downlaod json data into dictionary
        html = urlopen(site + symbol + key)
        alphaDailyData = json.load(html)
        
        # Creat blank lists for the 4 values we'll pull from AlphaVantage json output for stock
        openList  = []
        highList  = []
        lowList   = []
        closeList = []
        
        # Go through the json dictionary of historical stock data and pull out appropriate stock metric values        
        for date in dailyHits.index.tolist():
            # Date must be changed from the "StockHits.csv" format to the "AlphaVantage" format to query dictionary
            alphaDate = datetime.datetime.strptime(date, '%d-%m-%y').strftime('%Y-%m-%d')
            # Data is broken into dates so once we have date we can pull open, high, low, close from dict
            dayData = alphaDailyData['Time Series (Daily)'][alphaDate]
            openList.append(float(dayData['1. open']))
            highList.append(float(dayData['2. high']))
            lowList.append(float(dayData['3. low']))
            closeList.append(float(dayData['4. close']))
        
        # Combine all data into a dataframe. This is simply so it's easier to query. This could be removed if speed
        # and storage ever become a real issue
        plotDataDF = pd.DataFrame({'Date':dailyHits.index      ,
                                   'Mentions':dailyHits.values ,
                                   'Open':openList             ,
                                   'High':highList             ,
                                   'Low':lowList               ,
                                   'Close':closeList           })
                                   
        ### Plot data now
        # Create a figure and subplot
        fig, ax1 = plt.subplots()
        
        ax1.set_xlabel('Day (dd-mm-yy)')
        ax1.xaxis.set_ticks(plotDataDF.index.tolist())
        ax1.xaxis.set_ticklabels(plotDataDF.Date.tolist())
        ax1.yaxis.set_ticks(plotDataDF.Mentions.tolist())
        ax1.yaxis.set_ticklabels(plotDataDF.Mentions.tolist())
        ax1.set_ylabel('Number of Mentions', color = 'blue')
        
        ax2 = ax1.twinx()
        
        ax2.set_ylabel('Price ($)', color = 'green')
        
        for row in plotDataDF.itertuples():
            if row.Close > row.Open:
                stockColor = 'tab:green'
            else:
                stockColor = 'r'
            if chartType == 'bar':
                ax2.plot([row.Index, row.Index], [row.Low, row.High], color = stockColor, linewidth=1.5)
                ax2.plot([row.Index-0.2, row.Index], [row.Open, row.Open], color = stockColor, linewidth=1.5)
                ax2.plot([row.Index, row.Index+0.2], [row.Close, row.Close], color = stockColor, linewidth=1.5)
            elif chartType == 'candle':
                ax2.plot([row.Index, row.Index], [row.Low, row.High], color = (0,0,0), linewidth = 1.0)
                ax2.plot([row.Index, row.Index], [row.Close, row.Open], color = stockColor, linewidth=6.0)
            else:
                print('Chart Type input not recognized')
                print('Exiting...')
                exit()
            ax1.plot(row.Index, row.Mentions, 'b*')
        
        ax1.tick_params(axis = 'y', labelcolor = 'blue')
        ax2.tick_params(axis = 'y', labelcolor = 'green')
        
        fig.tight_layout()
        plt.setp(ax1.get_xticklabels(), rotation=45)
        plt.title(ticker)
        plt.show()
        

    except Exception as e:
        # If for any reason we come across an error we'll throw a response
        print (ticker, 'not screened properly.')
        
#hitsVsPrice('TRXC', '02-07-18', '10-07-18')
hitsVsPrice('TRXC')