### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ###
#
# Author        : Austin Brockner
# Creation Date : 07/14/17
# Last Updated  : 07/14/17
# Details       : Master program that calls supporting functions to collect data from subreddit
#
### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ###
#
# [IN] : None
# [OUT]: None
#
### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ###

# Import necessary libraries
import rhBot

# subreddit = 'stocks'
subreddit = 'RobinHood'
# subreddit = 'wallstreetbets'

# First login to reddit as "bot"
redditAccess = rhBot.botLogin()

if subreddit is 'stocks':
    datalogFile = 'DataLogS.csv'    
elif subreddit is 'RobinHood':
    datalogFile = 'DataLogRH.csv'
else:
    datalogFile = 'DataLogWSB.csv'

# Then execute brains of 'rhBot'. See rhBot.py for full information
#def runBot(redditLogin, subredditName, datalogFile, searchDate, searchTimeStart, searchTimeEnd, filePath, postLim, intraday)
# rhBot.runBot(redditAccess, subreddit,  datalogFile, '08/07/18', None, None ,None, 1000, False)
rhBot.runBot(redditAccess, subreddit,  'TEST.csv', '08/13/18', '07:30:00', '14:00:00', None, 1000, False)

print('Program has finished execution.')
input('Press Any Key to exit')