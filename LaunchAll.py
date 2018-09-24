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
# Launch these to collect data from the past, ignoring intraday prices
# os.system("start /B start cmd.exe @cmd /k python runBotDuringDay.py -s RobinHood -f DataLogRH.csv -v -b 08/11/18")
# os.system("start /B start cmd.exe @cmd /k python runBotDuringDay.py -s stocks -f DataLogS.csv -v -b 08/11/18")
# os.system("start /B start cmd.exe @cmd /k python runBotDuringDay.py -s wallstreetbets -f DataLogWSB.csv -v -b 08/11/18")

# Launch these to wait for market to open and to collect intraday
os.system("start /B start cmd.exe @cmd /k python runBotDuringDay.py -s RobinHood -w 1 -f DataLogRH.csv -i -m -v")
os.system("start /B start cmd.exe @cmd /k python runBotDuringDay.py -s stocks -w 1 -f DataLogS.csv -i -m -v")
os.system("start /B start cmd.exe @cmd /k python runBotDuringDay.py -s wallstreetbets -w 1 -f DataLogWSB.csv -i -m -v")