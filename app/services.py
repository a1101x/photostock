import time
import json
import hmac
from urllib.parse import urlencode
from hashlib import sha1

import requests
from flask import session, current_app as app

from .decorators import normalize_response, cache_response


def generate_api_key(segment, data=None, is_auth=False):
    if data:
        q_string = '/{segment}?{params}'.format(segment=segment,
                                                params=urlencode(data))
    else:
        q_string = '/{segment}'.format(segment=segment)
    client_secret = app.config['CLIENT_SECRET'] if not is_auth else \
        app.config['CLIENT_SECRET_AUTH']
    hashed = hmac.new(app.config['API_KEY'].encode(),
                      '{api_secret}{timestamp}{url}'.format(
                          api_secret=client_secret,
                          timestamp=int(time.time()), url=q_string).encode(),
                      sha1)
    return hashed.hexdigest()


def send_get_download(segment, data=None):
    timestamp = int(time.time())
    if data:
        data = {x: y for x, y in data.items() if y}
    headers = {
        'apikey': generate_api_key(segment, data),
        'timestamp': timestamp,
        'Accept': 'image/jpeg'
    }
    if session.get('user'):
        headers['Authorization'] = 'Bearer %s' % \
            session['user']['access_token']
    with requests.Session() as s:
        response = s.get('{api_url}{segment}'.format(
            api_url=app.config['API_URL'], segment=segment),
            headers=headers, params=data, stream=True)
    return response.status_code, response.raw if response.status_code == 200 \
        else response


@cache_response
@normalize_response
def send_get(segment, data=None, stream=False, nocache=False):
    timestamp = int(time.time())
    if data:
        data = {x: y for x, y in data.items() if y is not None}
    url = '{api_url}{segment}'.format(api_url=app.config['API_URL'],
                                      segment=segment)
    headers = {
        'apikey': generate_api_key(segment, data),
        'timestamp': timestamp,
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }
    if session.get('user'):
        headers['Authorization'] = 'Bearer %s' % \
                                   session['user']['access_token']
    with requests.Session() as s:
        response = s.get(url, headers=headers, params=data, stream=stream)
    return response


@normalize_response
def send_put(segment, data=None):
    timestamp = int(time.time())
    if data:
        data = {x: y for x, y in data.items() if y}
    url = '{api_url}{segment}'.format(api_url=app.config['API_URL'],
                                      segment=segment)
    headers = {
        'apikey': generate_api_key(segment),
        'timestamp': timestamp,
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }
    if session.get('user'):
        headers['Authorization'] = 'Bearer %s' % \
                                   session['user']['access_token']
    with requests.Session() as s:
        response = s.put(url, headers=headers, data=json.dumps(data))
    return response


@normalize_response
def send_delete(segment, data=None):
    timestamp = int(time.time())
    if data:
        data = {x: y for x, y in data.items() if y}
    url = '{api_url}{segment}'.format(api_url=app.config['API_URL'],
                                      segment=segment)
    headers = {
        'apikey': generate_api_key(segment),
        'timestamp': timestamp,
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }
    if session.get('user'):
        headers['Authorization'] = 'Bearer %s' % \
                                   session['user']['access_token']
    with requests.Session() as s:
        response = s.delete(url, headers=headers, data=json.dumps(data))
    return response


@normalize_response
def send_post(segment, data=None):
    timestamp = int(time.time())
    if data:
        data = {x: y for x, y in data.items() if y}
    url = '{api_url}{segment}'.format(api_url=app.config['API_URL'],
                                      segment=segment)
    headers = {
        'apikey': generate_api_key(segment),
        'timestamp': timestamp,
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }
    if session.get('user'):
        headers['Authorization'] = 'Bearer %s' % \
                                   session['user']['access_token']
    with requests.Session() as s:
        response = s.post(url, headers=headers, data=json.dumps(data))
    return response


@normalize_response
def send_post_oauth(segment, params=None):
    timestamp = int(time.time())
    if params:
        params = {x: y for x, y in params.items() if y}
    url = '{api_url}{segment}'.format(api_url=app.config['API_URL'],
                                      segment=segment)
    headers = {
        'apikey': generate_api_key(segment, is_auth=True),
        'timestamp': timestamp,
        'Accept': 'application/json',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    with requests.Session() as s:
        response = s.post(url, headers=headers, params=params)
    return response
