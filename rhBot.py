### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ###
#
# Author        : Austin Brockner
# Creation Date : 11/07/17
# Last Updated  : 08/03/18
# Details       : Bot used to browse reddit and collect data on stocks based
#				  on user comments. There are large assumptions made, as is the 
#                 case with paper trading, but they will be explained as they 
#				  come up.
#
### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ###
#
# [IN]: redditLogin     - custom                   - A Login instance from the reddit PRAW API.
#       subredditName   - 'subreddit_name'         - Name of the subreddit that will be searched
#       searchDate      - 'dd/mm/yy'               - The creation date of submissions/comments to be searched
#                                                    OPTIONAL. Defaults to current day.
#       searchTimeStart - 'HH:MM:SS'               - The earliest time a submission/comment can be created to be searched
#                                                    OPTIONAL. Defaults to 00:00:01
#       searchTimeEnd   - 'HH:MM:SS'               - The latest time a submission/comment can be created to be searched
#                                                    OPTIONAL. Defaults to 23:23:59
#       path            - '.../dir/outputCsv'      - Full file path to where the output csv files are located.
#                                                    OPTIONAL. Defaults to code execution file path
#       postLim         - int                      - Limit of subreddit submissions to look through. Max is 300(?).
#                                                    OPTIONAL. Defaults to newest 100 submissions
#
#
### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ###
#
# rhBot currently accesses a subreddit on Reddit and does the following:
# 	1. Accesses all submissions/comments that happened on searchDate. The submission text is only collected 
#       when the submission is originally made, otherwise the submission is just searched for comments.
#       To be collected: searchTimeStart < submission text/comments < searchTimeEnd 
#   2. Pool all comments
#   3. Sort through comments 1-by-1 and collect all ticker symbols
#   4. Dump raw data from comment with ticker symbol into DataLog.csv 
#      a. Action,Stock,Price,Author,Comment,Sub,Time,Date
#   5. Count the number of times a stock is mentioned and update StockHits.csv (REMOVED TO BECOME SEPARATE FUNCTION)
#      a. Stock, day_1-month-year, day_2-month-year, ... day_N-month-year
#   6. Access WatchList.csv and either update metrics for existing ticker mentioned (REMOVED TO BECOME SEPARATE FUNCTION)
#      today or add a new ticker. Metrics are below
#      a. STOCK, Price, Market Cap, Avg Volume, Rel Volume, EPS (ttm),
#         P/E, P/S, RSI (14), SMA20, SMA50, SMA200, Shs Outstand,
#         Short Float, Insider Own, Volatility, Change, Earnings, 
#         Sales, Insider Trans, Dividend, Last Update
#
### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ###

# IF USING WINDOWS 10 CONSOLE AND ENCODING ERROR HAPPENS TYPE THIS INTO CONSOLE:
# chcp 65001

# Import necessary libraries
import praw
import config
import datetime
import re
import pdb
import pandas
import string
import os
from sys import platform
from collections import OrderedDict
from threading import Thread

# Import custom libraries
import getFilePath
from getIntraRealtime import getIntraData
import stockChecker as sc

# Method for bot to login into reddit. 
def botLogin():
    reddit = praw.Reddit(client_id     = config.clientId     ,
                         client_secret = config.clientSecret ,
                         user_agent    = "/u/USER MEME Portfolio maker v1.0" )
    return reddit

def runBot(redditLogin, subredditName, searchDate = None, searchTimeStart = None, searchTimeEnd = None, filePath = None, postLim = 100):
    """
    # --*-- # # --*-- # # --*-- # Introduction # --*-- # # --*-- # # --*-- #
    First Validate any optional inputs. Check searchDate, searchTimeStart, and searchTimeEnd input 
    with the validateDateText and validateTimeText functions. If any of them are None (or improperly 
    formatted which returns None from validate functions), then use todays date and the entire day as
    the search span.
    Then check filePath, if it is None or not found to exist, use the directory python is being called in.
    Finally check postLim, mainly just to make sure it's not less than 1 and that it is an integer. Reddit
    has a hard limit on the maximum number of posts that can be pulled and if postLim is higher than that
    it will just default to Reddit's hard limit.
    """
    searchDate = validateDateText(searchDate)
    if searchDate is None:
        searchDate = datetime.datetime.today()
        
    # Create date format for "StockHits.csv".
    #*UPDATE*#  This should changed so that everything uses same date format
    dayMonYr = searchDate.strftime('%d-%m-%y')
    
    searchTimeStart = validateTimeText(searchTimeStart, dayMonYr)
    if searchTimeStart is None:
        searchTimeStart = datetime.datetime.strptime(dayMonYr + ' 00:00:01', '%d-%m-%y %H:%M:%S')
    
    searchTimeEnd = validateTimeText(searchTimeEnd, dayMonYr)    
    if searchTimeEnd is None or searchTimeEnd < searchTimeStart:
        searchTimeEnd = datetime.datetime.strptime(dayMonYr + ' 23:59:59', '%d-%m-%y %H:%M:%S')

    if filePath is None:
        filePath = getFilePath.getPath()
    elif os.path.exists(filePath) is False:
        filePath = getFilePath.getPath()
    
    postLim = isInteger(postLim)
    if postLim is None:
        postLim = 100
    elif postLim < 1:
        postLim = 100

    # Create empty dictionary we'll populate with stock data
    stockData = OrderedDict()
    stockData['Action']    = []
    stockData['Stock']     = []
    stockData['Price']     = []
    stockData['Author']    = []
    stockData['Comment']   = []
    stockData['Sub']       = []
    stockData['Time']      = []
    stockData['Date']      = []
    
    # Somehow when sorted by 'new', a 7 day old post shot to the top and ruined the code.
    # The code would stop searching for post because it breaks when a current post has a date 
    # before the search date. Count is so we hit at least 3 old post before moving on.
    oldDateCount = 0
    
    # boolean used to determine if we find any post at all that meet our criteria
    foundPost = False
    
    # Start looking through subreddit, scrape comments (and titles, slash post body text) that have ticker names
    subreddit = redditLogin.subreddit(subredditName)
    
    # Set dailyId default 0, so that if we don't find the daily submission dailyId we'll exit the program	
    dailyId = 0
    
    # Look through postLim amount of 'new' posts on the designated subreddit
    for submission in subreddit.new(limit = postLim):
        # Go through the last 100 hot submissions, and collect data from any that were posted on 'searchDate'
        submissionDate = datetime.datetime.utcfromtimestamp(submission.created_utc)
        #print(submissionDate.strftime("%d/%m/%y"))
        if submissionDate.day > searchDate.day:
            continue
        elif searchDate.day == submissionDate.day:
            if dailyId == 0:
                #print("\nCollecting data for DataLog...")
                foundPost = True
            dailyId = submission.id
            oldDateCount = 0
        else:
            oldDateCount += 1
            continue
            
        if oldDateCount > 3:
            #print('\nThere are no more post on r/' + subredditName, 'for', searchDate.strftime("%d/%m/%y"))
            #print('\n-' + 25 * '-*-' + '\n')
            oldDateCount = 0
            break
        
        #Check when submission is created
        submissionTime = datetime.datetime.fromtimestamp(submission.created_utc)
        
        # Only capture text from submission when it is created
        if submissionTime > searchTimeStart and submissionTime < searchTimeEnd:
            # First gather data from combing through comment list and put into the 'DataLog'
            commentTitleBody = submission.title + ' ' + submission.selftext
            
            # Parse comment looking for ticker symbol flag, "$", but making sure to exclude doller amounts
            tickers = re.findall(r'[$][^0.000-9.999]\w+',commentTitleBody)
            if tickers != []:
                foundStock = True
                #print("Found some meme stock based on the '$' symbol!")
                for ticker in tickers:
                    tickerSymbol = ticker.split('$')[-1]
                    #print("Buying shares of $" + tickerSymbol)
                    stockData['Action'].append('None')
                    stockData['Stock'].append(tickerSymbol.upper())
                    stockData['Price'].append('-')
                    if submission.author is None:
                        stockData['Author'].append('N/A')
                    else:
                        stockData['Author'].append(submission.author.name)
                    stockData['Comment'].append(commentTitleBody.replace(";", "."))
                    stockData['Sub'].append(subredditName)
                    stockData['Time'].append(submissionTime.strftime('%H:%M:%S'))
                    stockData['Date'].append(dayMonYr)
            else:
                # Can't find tickers the easy way with a "$" indication, so have to do it the hard way
                # First remove any punctuation such as commas or periods
                shortWords = [''.join(c for c in s if c not in string.punctuation) for s in commentTitleBody.split()]
                # Then, remove anything that is not all uppercase to denote a stock i.e. CRSP, NTLA, AAPL
                shortWords = [' '.join(word for word in sWord.split() if word.isupper()) for sWord in shortWords]
                # Lastly remove any empty quotes in the list
                shortWords = list(filter(None, shortWords))
                
                if shortWords == []:
                    #print ("Nothing to search for in sentence.")
                    continue
                    
                # Now send the list of possible ticker symbols to be checked against known market symbols
                tickers = findTickerSymbols(shortWords)
                if tickers != []:
                    foundStock = True
                    #print("Found some meme stock based on brute force approach!")
                    for ticker in tickers:
                        #print("Buying shares of $" + ticker)
                        stockData['Action'].append('None')
                        stockData['Stock'].append(ticker.upper())
                        stockData['Price'].append('-')
                        if submission.author is None:
                            stockData['Author'].append('N/A')
                        else:
                            stockData['Author'].append(submission.author.name)
                        stockData['Comment'].append(commentTitleBody.replace(";", "."))
                        stockData['Sub'].append(subredditName)
                        stockData['Time'].append(submissionTime.strftime('%H:%M:%S'))
                        stockData['Date'].append(dayMonYr)
         
        # Now check for comments made in the current submission between searchTimeStart and searchTimeEnd
        # Access submission to parse comments
        submission = redditLogin.submission(dailyId)
        # Expand comment forest so that all comments are shown (otherwise they're hidden behind 
        # the 'show more comments' button)
        # The comments are sorted by "best" I believe.
        submission.comments.replace_more(limit=0)
        
        # Go through comments looking for ticker symbols
        # foundStock boolean is for information output to terminal
        foundStock = True
        # Iterate through every comment in the comment tree from the daily stock discussion
        for comment in submission.comments.list():
            #Check when comment is made 
            commentTime = datetime.datetime.fromtimestamp(comment.created_utc)
            
            if commentTime > searchTimeStart and commentTime < searchTimeEnd:
                if foundStock:
                    #print("Reading comments...")
                    foundStock = False
                
                # Parse comment looking for ticker symbol flag, "$", but making sure to exclude doller amounts
                tickers = re.findall(r'[$][^0.000-9.999]\w+',comment.body)
                if tickers != []:
                    foundStock = True
                    #print("Found some meme stock based on the '$' symbol!")
                    for ticker in tickers:
                        tickerSymbol = ticker.split('$')[-1]
                        #print("Buying shares of $" + tickerSymbol)
                        stockData['Action'].append('None')
                        stockData['Stock'].append(tickerSymbol.upper())
                        stockData['Price'].append('-')
                        if comment.author is None:
                            stockData['Author'].append('N/A')
                        else:
                            stockData['Author'].append(comment.author.name)
                        stockData['Comment'].append(comment.body.replace(";", "."))
                        stockData['Sub'].append(subredditName)
                        stockData['Time'].append(commentTime.strftime('%H:%M:%S'))
                        stockData['Date'].append(dayMonYr)
                else:
                    # Can't find tickers the easy way with a "$" indication, so have to do it the hard way
                    # First remove any punctuation such as commas or periods
                    shortWords = [''.join(c for c in s if c not in string.punctuation) for s in comment.body.split()]
                    # Then, remove anything that is not all uppercase to denote a stock i.e. CRSP, NTLA, AAPL
                    shortWords = [' '.join(word for word in sWord.split() if word.isupper()) for sWord in shortWords]
                    # Lastly remove any empty quotes in the list
                    shortWords = list(filter(None, shortWords))
                    
                    if shortWords == []:
                        #print ("Nothing to search for in sentence.")
                        continue
                        
                    # Now send the list of possible ticker symbols to be checked against known market symbols
                    tickers = findTickerSymbols(shortWords)
                    if tickers != []:
                        foundStock = True
                        #print("Found some meme stock based on brute force approach!")
                        for ticker in tickers:
                            #print("Buying shares of $" + ticker)
                            stockData['Action'].append('None')
                            stockData['Stock'].append(ticker.upper())
                            stockData['Price'].append('-')
                            if comment.author is None:
                                stockData['Author'].append('N/A')
                            else:
                                stockData['Author'].append(comment.author.name)
                            stockData['Comment'].append(comment.body.replace(";", "."))
                            stockData['Sub'].append(subredditName)
                            stockData['Time'].append(commentTime.strftime('%H:%M:%S'))
                            stockData['Date'].append(dayMonYr)
            else:
                #Comment was not made during current searchTime frame
                continue
                        
    # Exit program if no daily thread from searchDate was found
    if dailyId == 0:
        print('No post were found on r/' + subredditName, 'for', searchDate.strftime("%d/%m/%y"), 'within a search limit of', postLim)
        print('\n-' + 25 * '-*-')
        return
    
    # Create dataframe from stockData dicttionary
    dataLogDF = pandas.DataFrame(stockData, columns = stockData.keys())
    
    # Create list of unique stock entries
    stockList = list(set(stockData['Stock']))
    
    # Read in list of known bad "tickers"
    badTickers = []
    with open(os.path.join(filePath,'listOfBadTickers.txt')) as f:
        badTickers = f.read().splitlines()
        
    # Remove any ticker that is on the known bad ticker list
    goodStocks = [ticker for ticker in stockList if ticker not in badTickers]
    
    # Now remove any ticker from the dataframe that is a known bad ticker
    dataLogDF = dataLogDF[dataLogDF.Stock.isin(goodStocks)].reset_index(drop=True)
    
    # Create empty results dict for all threads of "getIntraData" to use
    results = {stock:0 for stock in goodStocks}
    # Creat empty threads list
    threads = []
    
    for ii in range(len(goodStocks)):
        process = Thread(target = getIntraData, args =[goodStocks[ii], results])
        process.start()
        threads.append(process)

    for process in threads:
        process.join()
    
    for stock in goodStocks:
        idx = dataLogDF[dataLogDF['Stock'] == stock].index
        if len(idx) == 1:
            dataLogDF.at[idx, 'Price'] = results[stock]
        else:
            for index in idx:
                dataLogDF.at[index, 'Price'] = results[stock]
    
    dataLogDF.to_csv(os.path.join(filePath, 'DataLog.csv'), mode = 'a', header = False, index = False)
    print("Datalog updated with Daily Stock Discussion Information.")

def findTickerSymbols(wordList):
    tickerList = []
    for word in wordList:
        # In no particular order, check ticker symbols for 3 markets RH uses to trade
        # First double check that we ticker isn't repeated in the sentence
        if word in tickerList or word == 'I':
            continue
        # Next check the NASDAQ
        bTicker = sc.checkStock(word,"stock_lookup/NASDAQ.csv")
        if bTicker:
            tickerList.append(word)
            bTicker = False
            continue
        # Then check the New York Stock Exchange
        bTicker = sc.checkStock(word,"stock_lookup/NYSE.csv")
        if bTicker:
            tickerList.append(word)
            bTicker = False
            continue
        # Finally check the AMEX
        bTicker = sc.checkStock(word,"stock_lookup/AMEX.csv")
        if bTicker:
            tickerList.append(word)
            bTicker = False
            continue
    return tickerList
    
def validateTimeText(timeText, dateText):
    try:
        dtFormat = datetime.datetime.strptime(' '.join([dateText,timeText]), '%d-%m-%y %H:%M:%S')
        return dtFormat
    except:
        return None
        
def validateDateText(dateText):
    try:
        dtFormat = datetime.datetime.strptime(dateText, "%m/%d/%y")
        return dtFormat
    except:
        return None
        
def isInteger(s):
    try:
        pLimInt = int(s)
        return pLimInt
    except:
        return None
