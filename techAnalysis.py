### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ###
#
# Author        : Austin Brockner
# Creation Date : 07/6/18
# Last Updated  : 07/6/18
# Details       : Uses a combination of financial metrics to screen stocks and flag
#				  stocks that could be potentially 'good' candidates for a swing trade
#
### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ###

# Import necessary libraries
import datetime
import re
import pandas as pd
import string
import operator
from sys import platform

import pdb
import traceback, sys

def screenStocks():
    try:
        # # # # # # # # # # # # # # # Data Loading Begin # # # # # # # # # # # # # # # 
        # Intro steps to load data, screener metrics, establish variables, etc.
        # Inform user function has begun
        print("\nSearching for the Hottest Stocks this side of the Mississippi!\n")
        
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

        # Load Stock WatchList to have a dataframe of stocks we will screen
        stockListDF = pd.read_csv(path + 'WatchList.csv')
        stockListOrigLength = len(stockListDF.index.tolist())

        # Load the screener metrics (this should be a function input eventually)
        screenerDF = pd.read_csv(path + 'screenerV2.csv')
    
        # Setup up operations table. This is so we can interpret the comparative from the stock
        # screener csv literally
        ops = { "<": operator.lt, ">": operator.gt }
    
        # Setup up dictionary to convert large strings from WatchList, which uses
        # abbreviations such as 'K' or 'M' for thousand or million because of FinViz.
        numAbv = {'K': 1000, 'M': 1000000, 'B': 1000000000, '%': 0.01}
        
        # Create lists that are used in screening summary report
        drops = {'numDrops': [], 'reason': []}
        # # # # # # # # # # # # # # # Data Loading Ends # # # # # # # # # # # # # # # 
        
        # # # # # # # # # # # # # # # Stock Screening Begin # # # # # # # # # # # # # # # 
        # Iterate through the stocks removing any stock that does not meet criteria
        # The iteration will have the screening metric as the hierarchy so that rows
        # that fail any criteria won't be needlessly screened for other criteria
        for metricRow in screenerDF.itertuples():
            # Establish an empty list for the stock rows that will be removed
            dropIdx = []
            # This is lazy but basically lets us exclude screening metrics from the
            # screener csv easily    
            if metricRow.Metric[0] == '#':
                continue
                
            # Go through each stock(row) and compare metrics to screener metric
            for stockRow in stockListDF.index.tolist():
                screenerValue = metricRow.Value
                stockValue = stockListDF.loc[stockRow][metricRow.Metric]
                
                # Any metric that has a '-' means that FinViz doesn't have a value
                # for said metric, meaning that it normally doesn't exist. These are 
                # given a pass currently, but this should change in the future because
                # the lack of a fundamental metric is not a good sign.
                if stockValue == '-':
                    continue
                
                # Check to see if the stock metric is a number. This is necessary
                # because FinViz uses abbreviations like 54M to mean 54,000,000.
                # This is also done to convert percentages to numbers. If the metric
                # is a number we'll convert it to a float.
                if not is_number(stockValue):
                    alpha = stockValue[-1]
                    numKey = numAbv.get(alpha, 'default')
                    stockValue = float(stockValue.strip(alpha)) * numKey
                else:
                    stockValue = float(stockValue)
            
                # Currently the Stock Screener csv has a column to dictate if a value
                # is a percentage, this is done for ease of reading the screener metrics.
                if metricRow.Percentage:
                    screenerValue = screenerValue * 0.01
                
                # Compare Stock metric value to screener value
                passScreen = ops[metricRow.Comparison](stockValue,screenerValue)
            
                # Remove Stock from dataframe if it doesn't meet criteria
                if not passScreen:
                    dropIdx.append(stockRow)
                
            # Now remove all rows of stocks that didn't meet criteria
            stockListDF = stockListDF.drop(dropIdx)
            # Append data about dropped rows for screening summary
            drops['numDrops'].append(len(dropIdx))
            if metricRow.Metric == 'Market Cap' and metricRow.Comparison == '>':
                drops['reason'].append(metricRow.Metric + ' Min')
            elif metricRow.Metric == 'Market Cap' and metricRow.Comparison == '<':
                drops['reason'].append(metricRow.Metric + ' Max')
            else:
                drops['reason'].append(metricRow.Metric)
        # # # # # # # # # # # # # # # Stock Screening Ends # # # # # # # # # # # # # # #             

        # # # # # # # # # # # # # # # Screening Summary Begin # # # # # # # # # # # # #
        # Iterate through the drops dictionary and for any screening criteria
        # that caused a row(stock) to be dropped, print out how many rows(stocks) were eliminated
        # by the metric. This can be used to tweak screening data, especially if a majority
        # of stocks are being removed due to one metric
        for x in drops['numDrops']:
            if x > 0:
                percentDropped = x/stockListOrigLength * 100
                print('Removed', x, 'rows ('
                      + str(int(percentDropped)) + '%)', 'due to',
                      drops['reason'][drops['numDrops'].index(x)], 'restriction.')
                if int(percentDropped) >= 30:
                    print('    Consider Adjusting', drops['reason'][drops['numDrops'].index(x)], 'restriction!')
        print('\nTotal rows removed:', sum(drops['numDrops']))
        percentDropped = sum(drops['numDrops'])/stockListOrigLength * 100
        print('Percentage of rows removed:', str(percentDropped) + '%')
        # # # # # # # # # # # # # # # Screening Summary Begin # # # # # # # # # # # # #

        # # # # # # # # # # # # # # # Data Update Begin # # # # # # # # # # # # #        
        # Add any stocks that meet all screener criteria to the list of "HotStocks"
        if not stockListDF.empty:
            stockHitsDF.to_csv(path + 'HotStocks.csv', header = True, index = False)
            print("HotStocks updated with screened stocks. Hot Damn!\n")
        else:
            print("No Hot Stocks today. Bummer!\n") 
        # # # # # # # # # # # # # # # Data Update Ends # # # # # # # # # # # # #        
        
    except:
        print("Exception in user code:")
        print("-"*60)
        traceback.print_exc(file=sys.stdout)
        print("-"*60)
        
def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False