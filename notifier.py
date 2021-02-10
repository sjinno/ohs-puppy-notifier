from bs4 import BeautifulSoup
from decouple import config
import time
import requests


# Set private environment data:
#   ・ Telegram token
#   ・ Chat ID
TELEGRAM_TOKEN = config('TELEGRAM_TOKEN')
CHAT_ID = config('CHAT_ID')


# CONSTANTS:
URL = "https://www.oregonhumane.org/adopt/?type=dogs"
DETAIL = "https://www.oregonhumane.org/adopt/details/"


# First, make sure that the URL returns 200 with try block.
# Otherwise, notify the bad request and exit the program.
def get_puppies(url, puppy_dict):
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
    new_puppies = {}

    res = requests.get(url)
    if res.status_code != 200:
        print(f"{res.status_code}: Bad request!")
        print("Exiting the program...")
        return

    soup = BeautifulSoup(res.content, 'html.parser')

    all_dogs = soup.find_all('div', {'data-ohssb-type': 'dog'})

    for dog in all_dogs:
        ident = dog.find('span', class_='id').text
        name = dog.find('span', class_='name').text
        breed = dog.find('span', class_='breed').text
        age = dog.find('span', class_='age').text
        detail = DETAIL + ident

        if ident in puppy_dict or int(age.split(' ', 1)[0]) > 4:
            continue

        new_puppies[ident] = {
            'name': name,
            'breed': breed,
            'age': age,
            'detail': detail
        }

        puppy_dict[ident] = {
            'name': name,
            'breed': breed,
            'age': age,
            'detail': detail
        }

    # print(puppy_dict)

    if new_puppies != {}:
        send(new_puppies)
    else:
        print("No new puppies posted yet. :(")


def send(new_puppies):
    """Sends puppies' data to your telegram chat.

    Message format
    --------------
    ・ Name
       Age
       URL

    ・ ...
    """
    for (ident, puppy_info) in new_puppies.items():
        message = f"{puppy_info['name']}\n{puppy_info['breed']}\n{puppy_info['age']}\n{puppy_info['detail']}"

        send_text = 'https://api.telegram.org/bot' + TELEGRAM_TOKEN + \
            '/sendMessage?chat_id=' + CHAT_ID + '&parse_mode=Markdown&text=' + message

        res = requests.get(send_text)
        res.json()


# def main():
#     pass


# Make sure to loop main and request every 1 or 2 minutes.
# Increase count by 1 every loop and when the count is 60,
# exit the loop and quit the program.
if __name__ == '__main__':
    # Initialize initial state.
    puppy_dict = {}
    res = requests.get(URL)
    Ok = True
    if res.status_code != 200:
        Ok = False
        print(f"{res.status_code}: Bad request!")

    if Ok:
        soup = BeautifulSoup(res.content, 'html.parser')
        all_dogs = soup.find_all('div', {'data-ohssb-type': 'dog'})

        for dog in all_dogs:
            ident = dog.find('span', class_='id').text
            name = dog.find('span', class_='name').text
            breed = dog.find('span', class_='breed').text
            age = dog.find('span', class_='age').text
            detail = DETAIL + ident

            if int(age.split(' ', 1)[0]) > 4:
                continue

            puppy_dict[ident] = {
                'name': name,
                'breed': breed,
                'age': age,
                'detail': detail
            }
        # Initial state initialization ends here.

        # dog_count = 0
        # for (ident, puppy_info) in puppy_dict.items():
        #     # print(
        #     #     f"{puppy_info['name']}\n{puppy_info['breed']}\n{puppy_info['age']}\n{puppy_info['detail']}")
        #     # print()
        #     # dog_count += 1
        #     message = f"{puppy_info['name']}\n{puppy_info['breed']}\n{puppy_info['age']}\n{puppy_info['detail']}"
        #     send_text = 'https://api.telegram.org/bot' + TELEGRAM_TOKEN + \
        #         '/sendMessage?chat_id=' + CHAT_ID + '&parse_mode=Markdown&text=' + message
        #     res = requests.get(send_text)
        #     res.json()
        # print(dog_count)

        count = 0
        while count != 30:
            get_puppies(URL, puppy_dict)
            count += 1
            time.sleep(30)
