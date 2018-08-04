### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ###
#
# Author        : Austin Brockner
# Creation Date : 08/03/18
# Last Updated  : 08/03/18
# Details       : Used to get real-time stock price from a google search.
#
### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ###

from bs4 import BeautifulSoup as bs
import requests

def getIntraData(ticker, results):
    try:
        # First find finviz webpage for specific stock ticker
        url = ("https://www.google.com/search?q=%24" + ticker.upper() + "+stock+price")
        page = requests.get(url).content
        # Then create a 'soup' for the webpage
        soup = bs(page, 'lxml')
        # Go to the 6th entry of span from the soup and collect our stock price (this is not robust at all)
        price = soup.find_all("span")[5].contents[0].string
        stockFloat = float(price.replace(',',''))
        results[ticker] = stockFloat
    except:
        # If for any reason we come across an error we'll throw a response
        print('Unknown error with:', ticker.upper())
        results[ticker] = {}
    return True