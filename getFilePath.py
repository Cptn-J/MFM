### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ###
#
# Author        : Austin Brockner
# Creation Date : 07/14/17
# Last Updated  : 07/14/17
# Details       : Returns the file path for any program that calls this function.
#
### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ###
#
# [IN] : None
#
# [OUT]: Full file path
#
### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ###

# Import necessary libraries
import os

def getPath():
    return os.path.dirname(os.path.realpath(__file__))