import requests
from bs4 import BeautifulSoup

from constants import EMPTY_LETTER


def get_meaning(word: str) -> (str, str):
    dict_link = 'http://endic.naver.com/search.nhn?query={}'.format(word)
    soup = BeautifulSoup(requests.get(dict_link).content, "lxml")
    try:
        meaning = soup.find('dl', {'class': 'list_e2'}).find('dd').find('span', {'class': 'fnt_k05'}).get_text()
    except AttributeError:
        meaning = ''
    meaning = meaning if meaning else EMPTY_LETTER

    return dict_link, meaning
