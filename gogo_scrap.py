import requests as req
from bs4 import BeautifulSoup
import re

BASE_URL = 'https://gogoanime.so/'  # Change this if this link to gogoanime goes down

def _validifyName_(name):
    """

    Inner method used to clean anime search query

    :param name: Anime search query
    :return: Replaces special characters with '-' to comply with Gogoanime's URL specifications
    """

    # Replace all special characters and get a normalized name where only - is between words, and words in in lowercase
    newName = re.sub(r' +|:+|#+|%+|\?+|\^+|\$+|\(+|\)+|_+|&+|\*+ |\[+ |]+|\\+|{+|}+|\|+|/+|<+|>+|\.+|\'+', "-",
                     name.lower())
    newName = re.sub(r'-+', "-", newName)

    return newName

def search(anime, base_url=BASE_URL):
    """
    Uses Gogoanime's (limited) search functionality to find the exact anime or anime the user wants to get info about.
    This is required because the other functions in this bot require the user to input the exact title used in Gogoanime.

    :param anime: Search query
    :param base_url: Base Gogoanime URL. Useful if the current default URL gets taken down
    :return: List of search results
    """

    anime = _validifyName_(anime)
    searchUrl = base_url + '/search.html?keyword=' + anime

    page_response = req.get(searchUrl)
    page = BeautifulSoup(page_response.content, "html.parser")

    items = page.find('ul', class_='items').findAll('li')
    res = []

    for item in items:
        info = {}
        info['name'] = item.find('p', class_='name').find('a').text
        info['link'] = base_url + item.find('p', class_='name').find('a').get('href')
        info['released'] = item.find('p', class_='released').text.strip()
        info['gogoTitle'] = info['link'][info['link'].find('category') + 9:]
        res.append(info)

    return res


def get_links(name,episodes, source=None) -> 'list[str]':
    if source is not None:
        source_ep = f"https://gogoanime.pe/{name}-episode-"
        episode_links = [
            f"{source_ep}{i}"
            for i in range(1, episodes + 1)
        ]
        episode_links.insert(0, source)
    else:
        source_ep = f"https://gogoanime.pe/{name}-episode-"
        episode_links = [
            f"{source_ep}{i}"
            for i in range(1,episodes + 1)
        ]
    return episode_links

def get_download_links(episode_link) -> 'list[str]':
    with req.get(episode_link) as res:
        soup = BeautifulSoup(res.content, "html.parser")
        exist = soup.find("h1", {"class": "entry-title"})
        if exist is None:
            # Episode link == 200
            episode_link = soup.find("li", {"class": "dowloads"})
            return episode_link.a.get("href")
        else:
            # Episode link == 404
            episode_link = f"{episode_link}-"
            with req.get(episode_link) as res:
                soup = BeautifulSoup(res.content, "html.parser")
                exist = soup.find("h1", {"class": "entry-title"})
                if exist is None:
                    episode_link = soup.find("li", {"class": "dowloads"})
                    return episode_link.a.get("href")
                else:
                    return None
