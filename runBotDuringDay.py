### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ###
#
# Author        : Austin Brockner
# Creation Date : 07/30/17
# Last Updated  : 08/12/17
# Details       : Runs rhBot every [TIME LIMIT] to collect data throughout the day.
#
### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ###
#
# [IN] : None
# [OUT]: None
#
### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ###

from threading import Thread
import time
import sys, getopt
import os
from datetime import datetime, timedelta
import rhBot
import pdb

def main(redditAccess, subreddit, waitTime, datalogFile, intraday, timeout, timeoutStart, searchDate, backlog):
    if not backlog:
        while True:
            currentTime = datetime.now()
            print('Checking', subreddit, 'at', currentTime.strftime("%H:%M:%S"))
            
            # Calculate time difference for rhBot
            prevTime = currentTime - timedelta(minutes = waitTime)
            
            # Then execute brains of 'rhBot'. See rhBot.py for full information
            rhBot.runBot(redditAccess, subreddit, datalogFile, None, prevTime.strftime('%H:%M:%S'), currentTime.strftime('%H:%M:%S'), None, 100, intraday)
                   
            print('rhBot has finished execution for:', subreddit)
            time.sleep(waitTime * 60)
            
            if time.time() > timeoutStart + timeout:
                print('Time is up!')
                os._exit(1)
    else:
        # Then execute brains of 'rhBot'. See rhBot.py for full information
        rhBot.runBot(redditAccess, subreddit, datalogFile, searchDate, None, None, None, 1000, False)
        os._exit(1)

def save_state():
    print('Saving current state...\nQuitting Plutus. Goodbye!')

if __name__ == '__main__':
    
    subreddit     = ''
    waitTime      = ''
    datalogFile   = ''
    intraday      = False
    waitForMarket = False
    verbose       = False
    backlog       = False
    searchDate    = datetime.today().strftime("%m/%d/%y")    
    timeout       = 23400 # seconds
    
    try:
        opts, args = getopt.getopt(sys.argv[1:],"s:w:f:imb:vh", ['subreddit=', 'waitTime=', 'datalogFile=', 'intraday', 'market', 'backlog=', 'verbose', 'help'])
    except getopt.GetoptError:
        print('\nERROR: Input arguments invalid. Acceptable inputs are as follows:\n'
              '  -s or --subreddit   ->  Name of subreddit that will be searched.\n'
              '  -w or --waitTime    ->  Time (in minutes) between each successive search in subreddit.\n'
              '  -f or --datalogFile ->  Name of CSV file where data from search will be dumped.\n'
              '  -i or --intraday    ->  [Toggle] Use if you want to check Google for current stock prices when a comment is found.\n'
              '  -m or --market      ->  [Toggle] Use if you want to wait until the market opens (9:30 AM EST) to start searching a subreddit.\n'
              '                          NOTE: It is advised to always use -i and -m together to get accurate intraday prices.\n'
              '  -b or --backlog     ->  A past date to be searched.\n'
              '                          NOTE: -i, and therefore -m, cannot be used if data from the past is being searched.\n'
              '  -v or --verbose     ->  [Toggle] Use if you want more output from the functions being called.'
            )
        sys.exit(2)

    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print('\nAcceptable inputs are as follows:\n'
                  '  -s or --subreddit   ->  Name of subreddit that will be searched.\n'
                  '  -w or --waitTime    ->  Time (in minutes) between each successive search in subreddit.\n'
                  '  -f or --datalogFile ->  Name of CSV file where data from search will be dumped.\n'
                  '  -i or --intraday    ->  [Toggle] Use if you want to check Google for current stock prices when a comment is found.\n'
                  '  -m or --market      ->  [Toggle] Use if you want to wait until the market opens (9:30 AM EST) to start searching a subreddit.\n'
                  '                          NOTE: It is advised to always use -i and -m together to get accurate intraday prices.\n'
                  '  -b or --backlog     ->  A past date to be searched.\n'
                  '                          NOTE: -i, and therefore -m, cannot be used if data from the past is being searched.\n'
                  '  -v or --verbose     ->  [Toggle] Use if you want more output from the functions being called.'
                )
            sys.exit()
        elif opt in ("-s", "--subreddit"):
            subreddit = arg
        elif opt in ("-w", "--waitTime"):
            waitTime = int(arg)
        elif opt in ("-f", "--datalogFile"):
            datalogFile = arg
        elif opt in ("-i", "--intraday"):
            intraday = True
        elif opt in ("-m", "--market"):
            waitForMarket = True
        elif opt in ("-b", "--backlog"):
            backlog       = True
            waitForMarket = False
            searchDate    = arg
        elif opt in ("-v", "--verbose"):
            verbose = True            
    
    if verbose:
        print('\nRunning rhBot with the following options:\n'
              '  subreddit            -', subreddit    , '\n'
              '  wait_time(min)       -', waitTime     , '\n'
              '  datalog_file         -', datalogFile  , '\n'
              '  get_intraday         -', intraday     , '\n' 
              '  wait_for_market_open -', waitForMarket, '\n'
              '  collection_time(hr)  -', timeout/3600 , '\n'
              '  backlog_scrape       -', backlog      , '\n'
              '  backlog_search_date  -', searchDate   , '\n'
              )
    print('To exit program type "quit" into command prompt!')
    
    if waitForMarket is True:
        marketOpen = 570 # number of minutes at 9:30 AM
        currentTime = datetime.fromtimestamp(time.time())
        print("It's", currentTime.strftime("%H:%M:%S")," and we're waiting for the market to open.")
        while ((currentTime.hour*60 + currentTime.minute) < marketOpen):
            time.sleep(1)
            currentTime = datetime.fromtimestamp(time.time())
        print("It's", currentTime.strftime("%H:%M:%S"),"and the market is open!")
    
    # First login to reddit as "bot"
    redditAccess = rhBot.botLogin()
    
    timeoutStart = time.time()
    # now threading1 runs regardless of user input
    subThread = Thread(target=main, args =[redditAccess, subreddit, waitTime, datalogFile, intraday, timeout, timeoutStart, searchDate, backlog])
    subThread.daemon = True
    subThread.start()

    while True:
        if input().lower() == 'quit':
            save_state()
            sys.exit()
        else:
            print('not disarmed')
        time.sleep(1)