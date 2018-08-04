### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ###
#
# Author        : Austin Brockner
# Creation Date : 08/04/17
# Last Updated  : 08/04/17
# Details       : Calls "runBotDuringDay" for each subreddit in a separate command prompt
#
### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ###
#
# [IN] : None
# [OUT]: None
#
### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ###
import os

'''
The new instances of Command Prompt are launched in the same directory this function is called from,
so there is no need to pass a full file path.
'''
os.system("start /B start cmd.exe @cmd /k python runBotDuringDay.py -s RobinHood -w 5")
os.system("start /B start cmd.exe @cmd /k python runBotDuringDay.py -s stocks -w 5")
os.system("start /B start cmd.exe @cmd /k python runBotDuringDay.py -s wallstreetbets -w 5")