import pickle
import hashlib
from functools import wraps
from json import JSONDecodeError

from werkzeug.contrib.cache import MemcachedCache
from flask_babel import gettext as _
from flask import g, request, redirect, url_for


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if g.user is None or g.user.is_anonymous:
            return redirect(url_for('UserView:login', lang_code=g.current_lang,
                                    next=request.url))
        return f(*args, **kwargs)
    return decorated_function


def normalize_response(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        response = f(*args, **kwargs)
        status_code = response.status_code
        try:
            response = response.json()
        except JSONDecodeError:
            response = {}

        message = response.get('message', '') or response.get('error', '')
        description = response.get('description', '') or \
                      response.get('error_description', '')
        if status_code > 200:
            print('Error: \n method: {method}\n args: {args}\n \
                  \r kwargs: {kwargs}\n status_code: {status_code}\n \
                  error: {error}'.
                  format(method=f.__name__, args=args, kwargs=kwargs,
                         status_code=status_code, error=response))
            if message.find('already added to the lightbox with') > 0:
                response = {
                    'type': 'lightbox_item',
                    'text': _('ALREADY_ADDED')
                }
            elif message.find('ERROR_USER_EMAIL_ALREADY_TAKEN') > 0:
                response = {
                    'type': 'email',
                    'text': _('Account with this email already exists')
                }
            elif message.find('ERROR_USER_NOT_FOUND') > 0:
                response = {
                    'type': 'email',
                    'text': _('User does not exist')
                }
            elif message.find('ERROR_USER_INVALID_OLD_PASSWORD') > 0:
                response = {
                    'type': 'current_password',
                    'text': _('Invalid password')
                }
            elif message == 'invalid_token':
                response = {
                    'type': 'email',
                    'text': _('User does not exist')
                }
            elif message == 'invalid_grant' and \
                    description != 'ERROR_USER_NOT_FOUND':
                response = {
                    'type': 'password',
                    'text': _('Invalid password')
                }
            elif message == 'invalid_grant' and \
                    description == 'ERROR_USER_NOT_FOUND':
                response = {
                    'type': 'email',
                    'text': _('User does not exist')
                }
            elif message == 'expired_token':
                g.user._update_token()
                decorated_function(args, kwargs)
            elif message.find('ERROR_INSUFFICIENT_BALANCE') > 0:
                g.errors.append('Above max transaction limit')
            elif message.find('ERROR_PAYMENT_NETELLER_'
                              'EXCEPTION_ABOVE_MAX_TRANSACTION_LIMIT') > 0:
                g.errors.append('Above max transaction limit')
            elif message.find('ERROR_NO_ACTIVE_USER_LICENSES') > 0:
                g.errors.append('You do not have active licenses.')
            else:
                response = {
                    'type': 'all',
                    'text': message
                }
                g.errors.append(message)
        return status_code, response
    return decorated_function


def cache_response(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        cache = MemcachedCache(['127.0.0.1:11211'])
        key = '{url}{data}'.format(url=args[0], data=pickle.dumps(args))
        hash_ = hashlib.md5(key.encode()).hexdigest()
        if not cache.has(hash_):
            status_code, cached_data = f(*args, **kwargs)
            if not kwargs.get('nocache', False) and status_code == 200:
                cache.set(hash_, (status_code, cached_data), timeout=5 * 60)
        else:
            status_code, cached_data = cache.get(hash_)
        return status_code, cached_data
    return decorated_function
