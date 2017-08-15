class Default:
    SECRET_KEY = 'c47111eb8f0f30da1b70ed0(fbbc0%Hl36b^5b62caaad'
    BABEL_DEFAULT_LOCALE = 'en'
    BABEL_DEFAULT_TIMEZONE = 'UTC'
    LANGUAGES = {'en': 'en_US'}
    API_KEY = 'devApiKey'
    API_URL = 'https://devapi.photostock.org/'
    CLIENT_ID = 'appClientId'
    CLIENT_SECRET = 'devApiSecret'
    CLIENT_SECRET_AUTH = 'appClientSecret'
    STATIC_URL = 'https://devstatic.photostock.org/'
    THUMBS_URL = '%simages/thumbs/' % STATIC_URL
    MIDDLE_URL = '%simages/mid/' % STATIC_URL
    FULL_URL = '%simages/full/' % STATIC_URL
    CHARITY_URL = '%simages/charity/' % STATIC_URL
    SEARCH_IMAGES_BY_PAGE = 15
    EARNINGS_IMAGES_BY_PAGE = 10
    THUMB_RATIO = 5.33
    MIDDLE_RATIO = 1.77
    LICENSES = {'basic': {'month': {5: ('MONTH', 'BASIC', 25),
                                    25: ('MONTH', 'BASIC', 100)}},
                'professional': {'month': {50: ('MONTH', 'PROFESSIONAL', 100),
                                           100: ('MONTH', 'PROFESSIONAL',
                                                 150)},
                                 'year': {50: ('YEAR', 'PROFESSIONAL', 900),
                                          100: ('YEAR', 'PROFESSIONAL',
                                                1200)}}}
    DURATION = {'month': 'MONTH', 'year': 'YEAR'}


class Production(Default):
    DEBUG = False
    TESTING = False


class Develop(Default):
    DEBUG = False
    TESTING = False
