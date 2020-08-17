from requests import get
from os import environ
from box import Box

base_url = 'https://od-api.oxforddictionaries.com'

headers = {'app_id': environ['app_id'],
           'app_key': environ['app_key']}


def get_definition(word: str):
    response = get(
        '{}/api/v2/entries/en-gb/{}?strictMatch=true&fields=definitions'.format(base_url, word), headers=headers)
    json = response.json()
    json = Box(json)
    if 'error' in json:
        return False
    sense = json.results[0].lexicalEntries[0].entries[0].senses[0]
    return sense.definitions[0] if 'definitions' in sense else False


def get_root(word: str):
    response = get(
        '{}/api/v2/lemmas/en-gb/{}'.format(base_url, word), headers=headers)
    json = response.json()
    json = Box(json)
    if 'error' in json:
        return False
    return json.results[0].lexicalEntries[0].inflectionOf[0].text
