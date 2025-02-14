# Built in libraries:
from datetime import datetime
import time

# Third part libraries:
from bs4 import BeautifulSoup
from decouple import config
import requests


# Set private environment data:
#   ・ Telegram token
#   ・ Chat ID
TELEGRAM_TOKEN = config('TELEGRAM_TOKEN')
CHAT_ID = config('CHAT_ID')

EXCEPTIONS = ["American", "Pit", "Bull", "Terrier", "Chihuahua"]
NUMBER_OF_REQUESTS = 60
INTERVAL = 30


# CONSTANTS:
URL = "https://www.oregonhumane.org/adopt/?type=dogs"
DETAIL = "https://www.oregonhumane.org/adopt/details/"


class Dog:
    def __init__(self, name, breed, age, detail):
        self.name = name
        self.breed = breed
        self.age = age
        self.detail = detail

    def __str__(self):
        return (f"{self.name}\n"
                f"{self.breed}\n"
                f"{self.age}\n"
                f"{self.detail}\n")


# First, make sure that the URL returns 200 with try block.
# Otherwise, notify the bad request and exit the program.
def get_puppies(puppy_dict):
    """
    Gets puppies' data from OHS websie and create a new dictionary aside from `puppy_dict`
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

    # Initialize new puppy list.
    new_puppies = {}

    res = requests.get(URL)
    if res.status_code != 200:
        print(f"{res.status_code}: Bad request!")
        print("Exiting the program...")
        return

    soup = BeautifulSoup(res.content, 'html.parser')
    all_dogs = soup.find_all('div', {'data-ohssb-type': 'dog'})

    for dog in all_dogs:
        ident = dog.find('span', class_='id').text
        age = dog.find('span', class_='age').text
        # If the dog ID already exists in puppy_dict or the dog is older than 4 years,
        # then continue with the next dod.
        if ident in puppy_dict or int(age.split(' ', 1)[0]) > 4:
            continue

        breed = dog.find('span', class_='breed').text
        split_breed = breed.split(' ')
        ignore = False
        for b in split_breed:
            if b in EXCEPTIONS:
                ignore = True
                break
        if ignore:
            continue

        # If new ID found, then do the following:
        name = dog.find('span', class_='name').text
        detail = DETAIL + ident

        new_puppies[ident] = Dog(name, breed, age, detail)
        puppy_dict[ident] = Dog(name, breed, age, detail)

    current_time = datetime.now().strftime("%H:%M:%S")
    if new_puppies != {}:
        print(f"New doggy named {name} ({age} old) found!! {current_time}")
        send(new_puppies, current_time)
    else:
        print(f"No new puppies posted yet :( {current_time}")
        # print("Currently available number of dogs: {}".format(len(puppy_dict)))


def send(new_puppies, current_time):
    """Sends puppies' data to your telegram chat.

    Message format
    --------------
    ・ Name
       Age
       URL

    ・ ...
    """

    for (ident, puppy_info) in new_puppies.items():
        message = f"{puppy_info}" + f"{current_time}"

        send_text = 'https://api.telegram.org/bot' + TELEGRAM_TOKEN + \
            '/sendMessage?chat_id=' + CHAT_ID + '&parse_mode=Markdown&text=' + message

        # Note that it can also be requests.get(send_text),
        # but since I'm not needing to get any data from the
        # api, I prefer to use post.
        # If you are curious of the data, then you may want to
        # do something like:
        # res = requests.get(send_text)
        # data = res.json()
        requests.post(send_text)


# Make sure to loop main and request every 1 or 2 minutes.
# Increase count by 1 every loop and when the count is 60,
# exit the loop and quit the program.
if __name__ == '__main__':
    puppy_dict = {}
    res = requests.get(URL)
    Ok = True
    if res.status_code != 200:
        Ok = False
        print(f"{res.status_code}: Bad request!")

    if Ok:
        soup = BeautifulSoup(res.content, 'html.parser')
        all_dogs = soup.find_all('div', {'data-ohssb-type': 'dog'})

        # Initialize initial state.
        for dog in all_dogs:
            age = dog.find('span', class_='age').text
            if int(age.split(' ', 1)[0]) > 4:
                continue

            breed = dog.find('span', class_='breed').text
            split_breed = breed.split(' ')
            ignore = False
            for b in split_breed:
                if b in EXCEPTIONS:
                    ignore = True
                    break
            if ignore:
                continue

            ident = dog.find('span', class_='id').text
            name = dog.find('span', class_='name').text
            # breed = dog.find('span', class_='breed').text
            detail = DETAIL + ident

            puppy_dict[ident] = Dog(name, breed, age, detail)
        # Initial state initialization ends here.

        for k, v in puppy_dict.items():
            print(k)
            print(v)
            print()
        print("Current number of available dogs: {}\n".format(len(puppy_dict)))

        count = 0
        while count != NUMBER_OF_REQUESTS:
            time.sleep(INTERVAL)
            get_puppies(puppy_dict)
            count += 1
