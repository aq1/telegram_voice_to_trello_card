import requests


TRELLO_KEY = '0a2169778555b41e80b615399d83541f'
TRELLO_TOKEN = '776cea39c4013e6b8b94c47d7e7e56ac6122255587bad81ce8c6959d8859b8c7'
TRELLO_URL = 'https://api.trello.com/1/'


def call(method, name, resource_id='', nested='', data=None, params=None, **kwargs):
    url = TRELLO_URL + name
    if resource_id:
        url += '/' + resource_id
    if nested:
        url += '/' + nested

    print(url)
    data = data or {}
    params = params or {}

    params.update({
        'key': TRELLO_KEY,
        'token': TRELLO_TOKEN,
    })

    response = requests.request(method, url, data=data, params=params, **kwargs)
    if 200 <= response.status_code < 300:
        raise ValueError()

    try:
        return response.json()
    except (TypeError, KeyError):
        raise ValueError()
