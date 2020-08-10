from requests import get
from box import Box

base_url = 'http://www.anagramica.com'


def get_anagrams(letters: str, min_len = 4):
    response = get('{}/all/{}'.format(base_url, letters))
    json = response.json()
    json = Box(json)
    return [word for word in json.all if len(word) >= min_len]
