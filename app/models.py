import time

from flask import current_app as app, g, session

from .helpers import date_format_friendly, thumb_url
from .services import send_delete, send_get, send_post, send_post_oauth, \
    send_put


class User:

    access_token = ''

    id = ''
    country = ''
    equipment = []
    fullName = ''
    imageCount = 0
    registeredOnUtc = 0
    styles = []
    email = ''

    refresh_token = ''
    expires_in = ''
    token_exp = 0

    errors = {}

    @property
    def registered(self):
        return date_format_friendly(self.registeredOnUtc)

    @property
    def is_anonymous(self):
        if self.access_token:
            return False
        return True

    def __init__(self):
        if session.get('user'):
            self.__dict__.update(session['user'])
            if self.token_exp <= int(time.time()):
                self._update_token()

    def _set_token_exp(self):
        self.token_exp = int(time.time()) + (int(self.expires_in) - 10 * 60)

    def _clean_session(self):
        if 'user' in session:
            session.pop('user')

    def _update_session(self):
        self._clean_session()
        session['user'] = self.__dict__
        return self

    def _update_token(self):
        data = {
            'grant_type': 'refresh_token',
            'refresh_token': self.refresh_token,
            'client_id': app.config['CLIENT_ID'],
            'client_secret': app.config['CLIENT_SECRET_AUTH']
        }
        status_code, response = send_post_oauth('oauth/token', data)

        if response.get('access_token'):
            self.__dict__.update(response)
            self._set_token_exp()
            self._update_session()
        else:
            self._clean_session()

    def get_profile(self):
        status_code, response = send_get('user', nocache=True)
        if status_code == 200:
            self.__dict__.update(response)
            self._update_session()
        return self

    def get_profile_by_id(self, id):
        status_code, response = send_get('users/%s' % id, nocache=True)
        if status_code == 200:
            self.__dict__.update(response)
        return self

    def login(self, email, password):
        data = {
            'username': email,
            'password': password,
            'grant_type': 'password',
            'client_id': app.config['CLIENT_ID'],
            'client_secret': app.config['CLIENT_SECRET_AUTH']
        }

        status_code, response = send_post_oauth('oauth/token', data)
        if status_code == 200:
            self.__dict__.update(response)
            self._set_token_exp()
            self._update_session()
            self.get_profile()
        else:
            self.errors = response
        return self

    def logout(self):
        self._clean_session()
        g.pop('user')

    def register(self, username, email, password):
        data = {
            'fullName': username,
            'email': email,
            'password': password,
            'passwordConfirmation': password
        }

        status_code, response = send_post('users/register', data)
        if status_code == 200:
            self.login(email, password)
        else:
            self.errors = response

        return self

    def recover_passsword(self, email):
        status_code, response = send_post('users/recover/password/agency',
                                          {'value': email})
        if status_code > 200:
            self.errors = response

        return self

    def change_password(self, password, old_password):
        status_code, response = send_put('user/password',
                                         {
                                             'newPassword': password,
                                             'oldPassword': old_password
                                         })
        if status_code > 200:
            self.errors = response

    def change_email(self, email):
        status_code, response = send_put('user', {'email': email})
        if status_code > 200:
            self.errors = response

        return self


class Lightbox:

    lightBoxId = 0
    title = ''
    imageTokens = []
    thumbnailToken = []
    size = 0

    def __init__(self, lightbox_id=None):
        if lightbox_id:
            self.lightBoxId = lightbox_id
            status_code, response = send_get('image/lightbox',
                                             {'lightBoxId': self.lightBoxId},
                                             nocache=True)
            if status_code == 200:
                self.__dict__.update(response)

    def list_lightboxes(self):
        resp = []
        status_code, response = send_get('image/lightboxes', nocache=True)
        if status_code == 200:
            resp = response['values']
        return resp

    def create(self, title):
        status_code, response = send_post('image/lightbox', {'value': title})
        if status_code == 200:
            self.__dict__.update(response)
        return self

    def update(self, data):
        data.update({'lightBoxId': self.lightBoxId})
        status_code, response = send_put('image/lightbox', data)
        if status_code == 200:
            self.__dict__.update(response)
        return self

    def delete(self):
        status_code, response = send_delete('image/lightbox',
                                            {'value': self.lightBoxId})
        return True if status_code == 200 else False

    def append_item(self, token):
        status_code, response = send_post('image/lightbox_image',
                                          {
                                              'lightBoxId': self.lightBoxId,
                                              'imageToken': token
                                          })
        if status_code == 200:
            self.__dict__.update(response)
            return True
        else:
            if response['text'] == 'ALREADY_ADDED':
                return True
        return False

    def remove_item(self, token):
        status_code, response = send_delete('image/lightbox_image',
                                            {
                                                'lightBoxId': self.lightBoxId,
                                                'imageToken': token
                                            })
        return True if status_code == 200 else False


class Image:

    imageHeight = ''
    userName = ''
    createdOnUtc = ''
    title = ''
    buyers = []
    tags = []
    imageWidth = 0
    publicShared = ''
    charityDisplayName = ''
    uploadId = ''
    dpi = 0
    status = 'APPROVED'
    charityId = ''
    imageUploaded = True
    uploadedOnUtc = 0
    boughtByUser = False
    sold = True
    special = False
    price = 0
    token = ''
    userFullName = ''
    downloadCount = 0

    @property
    def thumb_url(self):
        return thumb_url(self.uploadId)

    @property
    def thumb_width(self):
        return int(self.imageWidth / app.config['THUMB_RATIO'])

    @property
    def thumb_height(self):
        return int(self.imageHeight / app.config['THUMB_RATIO'])

    @property
    def published(self):
        return date_format_friendly(self.uploadedOnUtc)

    @property
    def same_artists(self):
        same_artist_list = []
        status_code, response = send_get('image/search_by_user/',
                                         {
                                             'userId': self.userName,
                                             'maxResults': 9, 'pageNum': 0
                                         })
        if status_code == 200:
            for same_artist in response['values']:
                image = Image()
                image.__dict__.update(same_artist)
                same_artist_list.append(image.get_dict())
        return same_artist_list

    @property
    def similar_images(self):
        similar_image_list = []
        status_code, response = send_get('image/similar_by_tag/',
                                         {
                                             'imageToken': self.token,
                                             'maxResults': 9, 'pageNum': 0
                                         })
        if status_code == 200:
            for similar_image in response['values']:
                image = Image()
                image.__dict__.update(similar_image)
                similar_image_list.append(image.get_dict())
        return similar_image_list

    def __init__(self, token=None):
        if token:
            status_code, response = send_get('image/{token}'.
                                             format(token=token))
            if status_code == 200:
                self.__dict__.update(response)

    def get_dict(self):
        self.__dict__.update({
            'thumb_url': self.thumb_url,
            'thumb_width': self.thumb_width,
            'thumb_height': self.thumb_height,
            'published': self.published})
        return self.__dict__
