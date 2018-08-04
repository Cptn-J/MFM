### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ###
#
# Author        : Austin Brockner
# Creation Date : 07/30/17
# Last Updated  : 07/30/17
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

def main(redditAccess, subreddit, waitTime):
    while True:
        currentTime = datetime.now()
        print('Checking', subreddit, 'at', currentTime.strftime("%H:%M:%S"))
        
        # Calculate time difference for rhBot
        prevTime = currentTime - timedelta(minutes = waitTime)
        
        # Then execute brains of 'rhBot'. See rhBot.py for full information
        rhBot.runBot(redditAccess, subreddit, '08/03/18', prevTime.strftime('%H:%M:%S'), currentTime.strftime('%H:%M:%S'), None, None)

        print('rhBot has finished execution for:', subreddit)
        time.sleep(waitTime * 60)

def save_state():
    print('Saving current state...\nQuitting Plutus. Goodbye!')

if __name__ == '__main__':
    
    subreddit = ''
    waitTime = ''
    
    try:
        opts, args = getopt.getopt(sys.argv[1:],"hs:w:")
    except getopt.GetoptError:
        print('ERROR\nProper function is: runBotDuringDay.py -s <subreddit_name> -w <refresh_wait_time>')
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            print('Proper function is: runBotDuringDay.py -s <subreddit_name> -w <refresh_wait_time>')
            sys.exit()
        elif opt in ("-s", "--subreddit"):
            subreddit = arg
        elif opt in ("-w", "--waitTime"):
            waitTime = int(arg)
    
    print('To exit program type "quit" into command prompt!')

    # First login to reddit as "bot"
    redditAccess = rhBot.botLogin()
    subreddits = ['stocks', 'RobinHood', 'wallstreetbets']
    waitTime = 1 # In minutes

    # now threading1 runs regardless of user input
    subThread = Thread(target=main, args =[redditAccess, subreddit, waitTime])
    subThread.daemon = True
    subThread.start()

    while True:
        if input().lower() == 'quit':
            save_state()
            sys.exit()
        else:
            print('not disarmed')