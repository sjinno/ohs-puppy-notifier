from bs4 import BeautifulSoup

import environ
import requests
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext
import time


# Set private environment data:
#   - Telegram token

# Constants:
URL = "https://www.oregonhumane.org/adopt/?type=dogs"
DOG_DETAIL_URL = "https://www.oregonhumane.org/adopt/details/"


# First, make sure that the URL returns 200 with try block.
# Otherwise, notify the bad request and exit the program.


def get_puppies(url, puppy_dict):
    """Gets puppies' data from OHS websie and create a new dictionary aside from `puppy_dict`
       so that we don't sned redundant puppies to telegram.

    Parameters
    ----------
    url : str
        The URL of OHS

    puppy_dict : dict
        A dictionary of puppies to update.

    Returns
    -------
    dict
        A dictionary of puppies' data: { puppy: [name, age, url], etc. }
    """
    new_puppies = {}
    return new_puppies


def send():
    """Sends puppies' data to your telegram chat.

    Message format
    --------------
    ・ Name
       Age
       URL

    ・ ...
    """
    pass


def main():
    print("Hello, world!")


# Make sure to loop main and request every 1 or 2 minutes.
# Increase count by 1 every loop and when the count is 60,
# exit the loop and quit the program.
if __name__ == '__main__':
    main()
