from requests import get
from box import Box

base_url = 'http://www.anagramica.com'


def get_anagrams(letters: str, min_len=4):
    response = get('{}/all/{}'.format(base_url, letters))
    json = response.json()
    json = Box(json)
    min_4 = [word for word in json.all if len(word) >= min_len]
    return min_4 if min_4 else json.all
