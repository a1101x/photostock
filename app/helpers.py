import math
import random
import string
from _datetime import datetime
from urllib.parse import urlparse, urljoin, parse_qs

from flask import g, redirect, request, session, url_for, current_app as app
from flask_babel import Babel


babel = Babel()


@babel.localeselector
def get_locale():
    if request.view_args and 'lang_code' in request.view_args:
        req_lang = request.view_args['lang_code']
        lang_code = req_lang if req_lang in app.config['LANGUAGES'].keys() \
            else session.get('current_lang', 'en')
        return lang_code


def manage_lang():
    if request.view_args and 'lang_code' in request.view_args:
        g.current_lang = request.view_args['lang_code']
        session['current_lang'] = g.current_lang
        request.view_args.pop('lang_code')
    elif 'current_lang' in session:
        g.current_lang = session['current_lang']
    else:
        g.current_lang = 'en'
        session['current_lang'] = 'en'


def _is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and \
        ref_url.netloc == test_url.netloc


def _get_redirect_target():
    query_string = request.referrer.split('?')[-1]
    next_ = parse_qs(query_string).get('next', [''])[0]

    for target in next_, request.values.get('next'), request.referrer:
        if not target:
            continue
        if _is_safe_url(target):
            return target


def redirect_back(endpoint, **values):
    target = _get_redirect_target()
    if not target:
        target = url_for(endpoint, **values)
    return redirect(target)


def set_errors(form, error):
    if error.get('type') and error['type'] in [i for i in form._fields]:
        form[error['type']].errors.append(error['text'])


def get_section(string, delim, section):
    if string:
        return string.split(delim)[section]


def thumb_url(string):
    return '{url}{img}.jpg'.format(url=app.config['THUMBS_URL'],
                                   img=string)


def date_format_friendly(timestamp):
    if not timestamp:
        return 0
    time = datetime.fromtimestamp(timestamp / 1000.0)

    def suffix(date):
        return 'th' if 11 <= date <= 13 else {1: 'st', 2: 'nd', 3: 'rd'}.\
            get(date % 10, 'th')

    def custom_strftime(format, time):
        return time.strftime(format).replace('{S}', str(time.day) +
                                             suffix(time.day))

    return custom_strftime('{S} %b  %Y', time)


def date_simple(timestamp):
    if not timestamp:
        return 0
    t = datetime.fromtimestamp(timestamp / 1000.0)
    return t.strftime('%m/%d/%y')


def get_plan(form):
    duration = form.get('duration', 'month')
    license = form.get('license_type', 'basic')
    try:
        images = int(form.get('count', 5))
        license = app.config['LICENSES'][license]
        print (license[duration])
        return license[duration][images]
    except KeyError:
        return ('MONTH', 'BASIC', 25)
    except ValueError:
        return ('MONTH', 'BASIC', 25)


def random_string(size=16, chars=string.ascii_uppercase +
                  string.ascii_lowercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


class Paginator:
    def __init__(self, amount, page, count=None):
        self.page = page
        self.amount = amount
        self.count = count or app.config['SEARCH_IMAGES_BY_PAGE']

    @property
    def page_next(self):
        return self.page + 1 if self.page < self.pages_amount else None

    @property
    def page_prev(self):
        return self.page - 1 if self.page > 1 else None

    @property
    def pages_amount(self):
        return math.ceil(self.amount / self.count)
