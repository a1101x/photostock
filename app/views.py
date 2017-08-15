import io
import time
import datetime

from flask import Flask
from flask import current_app as app, g, jsonify, redirect, render_template, \
    request, url_for, send_file
from flask_classy import FlaskView, route
from flask_babel import gettext as _
from flask_mail import Mail, Message

from .forms import LoginForm, PaginatorForm, QuickSearchForm, \
    RecoverPasswordForm, RegisterForm, LightboxForm, ChangePasswordForm, \
    ChangeEmailForm, SettingsForm, NetelletAccForm, BankAccForm, \
    OrderCardForm, OrderAddressForm, ContactUsForm
from .models import Lightbox, User, Image
from .services import send_get, send_post, send_get_download, send_put, \
    send_delete
from .helpers import manage_lang, set_errors, redirect_back, Paginator, \
    get_plan, random_string
from .mixins import LightBoxMixin
from .decorators import login_required


def before_request():
    manage_lang()
    g.login_form = LoginForm()
    g.user = User()
    g.errors = []
    g.success_message = request.args.get('success', '')

    keyword = request.args.get('keyword', '')
    g.search_form = QuickSearchForm(keyword=keyword.lower(), type='tag')

    if request.path == '/':
        return redirect('/%s/' % g.current_lang)


class IndexView(FlaskView):

    route_base = '/<lang_code>/'

    @route("/", methods=["GET", "POST"])
    def index(self):
        gallery = {}
        search_form = QuickSearchForm()
        register_form = RegisterForm()
        login_form = LoginForm()

        status_code, response = send_get('image/most_popular_by_tag',
                                         {
                                             'tagImagesLimit': 10,
                                             'tagsLimit': 6
                                         })
        all_img = []

        for item in response.get('values', []):
            images = []
            for i, img in enumerate(item['images']):
                image = Image()
                image.__dict__.update(img)
                images.append({
                    'thumb_url': image.thumb_url,
                    'token': image.token
                })

                if i <= 1:
                    all_img.append({
                        'thumb_url': image.thumb_url,
                        'token': image.token,
                        'tags': image.tags
                    })

            gallery[item['tag']] = {'images': images}
            g.gallery = gallery
            g.all_img = all_img

        status_code, response = send_get('image/free_photo_of_the_week')
        free_image = response.get('image', [])
        g.free_image_user = free_image['userFullName']
        g.free_image_token = free_image['token']
        g.free_image_userid = free_image['userName']
        g.free_image_thumb = free_image['uploadId']

        status_code, response = send_get(
            'image/most_downloaded_photo_of_the_week')
        most_downloaded = response.get('image', [])
        if most_downloaded:
            g.most_downloaded_user = most_downloaded['userFullName']
            g.most_downloaded_token = most_downloaded['token']
            g.most_downloaded_userid = most_downloaded['userName']
            g.most_downloaded_thumb = most_downloaded['uploadId']

        if search_form.quick_search_btn.data and \
                search_form.validate_on_submit():
            keyword = request.form['keyword']
            return redirect(url_for('SearchView:search_results',
                                    lang_code=g.current_lang,
                                    keyword=keyword.lower()))

        if register_form.register_btn.data and \
                register_form.validate_on_submit():
            response = User().register(request.form, register_form)
            if response:
                return response

        return render_template("index.html", search_form=search_form,
                               register_form=register_form,
                               login_form=login_form)

    @route("/autocomplete/<keyword>")
    def autocomplete(self, keyword):
        q = {
            'searchTerm': keyword.lower(),
            'searchBy': 'TAG'
        }

        status_code, response = send_get('image/search_autocomplete', q)
        resp = []
        for item in response.get('values', []):
            if item['value'][0] not in resp:
                resp.append(item['value'][0])
        return jsonify(resp)

    @route("/quick-search/<keyword>")
    def quick_search(self, keyword):
        return url_for('SearchView:search_results', keyword=keyword.lower(),
                       lang_code=g.current_lang)


class UserView(FlaskView):

    route_base = '/<lang_code>/user/'

    @route("/login/", methods=["GET", "POST"])
    def login(self):
        login_form = LoginForm()

        if not g.user.is_anonymous:
            return redirect(url_for("IndexView:index",
                                    lang_code=g.current_lang))

        if login_form.validate_on_submit():
            user = User().login(request.form['email'],
                                request.form['password'])
            if user.errors:
                set_errors(login_form, user.errors)
            else:
                return redirect_back(url_for("IndexView:index",
                                             lang_code=g.current_lang))

        return render_template('login.html', login_form=login_form)

    @route("/logout/", methods=["GET", "POST"])
    def logout(self):
        user = User()
        user.logout()
        return redirect_back("UserView:login", lang_code=g.current_lang)

    @route("/register/", methods=["GET", "POST"])
    def registration(self):

        register_form = RegisterForm()
        login_form = LoginForm()

        if register_form.register_btn.data and \
                register_form.validate_on_submit():
            user = User().register(request.form['username'],
                                   request.form['email'],
                                   request.form['password'])
            if user.errors:
                set_errors(register_form, user.errors)
            else:
                return redirect_back(url_for("IndexView:index",
                                             lang_code=g.current_lang))

        if login_form.login_btn.data and login_form.validate_on_submit():
            user = User().login(request.form['email'],
                                request.form['password'])
            if user.errors:
                set_errors(login_form, user.errors)
            else:
                return redirect_back(url_for("IndexView:index",
                                             lang_code=g.current_lang))

        return render_template('register.html', register_form=register_form,
                               login_form=login_form)

    @route("/password/recover/", methods=["GET", "POST"])
    def recover(self):
        form = RecoverPasswordForm()
        if form.validate_on_submit():
            user = User().recover_passsword(request.form['email'])
            if not user.errors:
                return redirect(url_for("IndexView:index",
                                        lang_code=g.current_lang))
            else:
                set_errors(form, user.errors)

        return render_template('password_recover.html', form=form)


class SearchView(FlaskView, LightBoxMixin):

    route_base = '/<lang_code>/search'

    def __init__(self):
        super().__init__()

        self.userId = None
        self.searchTerm = None
        self.searchBy = 'TAG'
        self.maxResults = 15
        self.pageNum = 1
        self.imageToken = None

    def _get_images(self):
        img_list = []

        if self.userId and self.searchTerm:
            status_code, response = send_get('image/search_by_user_and_tag',
                                             self.__dict__)
        elif self.userId and not self.searchTerm:
            status_code, response = send_get('image/search_by_user',
                                             self.__dict__)
        elif self.imageToken:
            status_code, response = send_get('image/similar_by_tag',
                                             self.__dict__)
        else:
            status_code, response = send_get('image/search',
                                             self.__dict__)

        if status_code == 200:
            for item in response.get('values', []):
                image = Image()
                image.__dict__.update(item)
                img_list.append(image)

        return img_list

    def _get_amount(self):
        amount = 0

        if self.userId and self.searchTerm:
            status_code, resp_counter = send_get('image/count_by_user_and_tag',
                                                 self.__dict__)
        elif self.userId and not self.searchTerm:
            status_code, resp_counter = send_get('image/count_by_user/%s' %
                                                 self.userId)
        elif self.imageToken:
            status_code, resp_counter = send_get('image/similar_by_tag_count',
                                                 self.__dict__)
        else:
            status_code, resp_counter = send_get('image/search_count',
                                                 self.__dict__)

        if status_code == 200:
            amount = resp_counter['value']

        return amount

    @route("/", methods=["GET", "POST"])
    def search_results(self):
        g.img_list = []
        g.keyword = self.searchTerm = request.args.get('keyword')
        g.author = self.userId = request.args.get('author')
        g.similar = self.imageToken = request.args.get('similar')
        try:
            self.pageNum = int(request.args.get('page', 1))
        except ValueError:
            self.pageNum = 1
        self.maxResults = app.config['SEARCH_IMAGES_BY_PAGE']

        paginator_form = PaginatorForm(page=self.pageNum)
        lightbox_form = LightboxForm()

        if paginator_form.paginator_btn.data and \
                paginator_form.validate_on_submit():
            if request.form['page']:
                return redirect(url_for('SearchView:search_results',
                                        lang_code=g.current_lang,
                                        keyword=self.searchTerm.lower(),
                                        page=request.form['page'],
                                        author=self.userId,
                                        similar=self.imageToken))

        if g.search_form.quick_search_btn.data and \
                g.search_form.validate_on_submit():

            keyword =request.form.get('keyword', '')
            return redirect(url_for('SearchView:search_results',
                                    keyword=keyword.lower(),
                                    lang_code=g.current_lang,
                                    page=self.pageNum,
                                    author=self.userId))

        g.img_list = self._get_images()

        g.paginator = Paginator(self._get_amount(), self.pageNum)

        return render_template('search.html', lang_code=g.current_lang,
                               paginator_form=paginator_form,
                               lightbox_form=lightbox_form)

    @route("/download/<token>/", methods=["GET"])
    def download(self, token):
        status_code, response = send_get_download('image/{token}/download'.
                                                  format(token=token))
        hash_ = random_string()

        if status_code == 200:
            return send_file(io.BytesIO(response.read()),
                             mimetype='image/jpeg',
                             attachment_filename="{hash_}.jpg".
                             format(hash_=hash_),
                             as_attachment=True)

        return redirect(url_for('ImageDetailsView:get', token=token,
                                lang_code=g.current_lang))

    @route("/image-info/<token>/", methods=["GET", "POST"])
    def image_info(self, token):

        image = Image(token)

        resp = image.get_dict()
        resp['same_artist'] = image.same_artists
        resp['similar_images'] = image.similar_images
        resp['lightboxes'] = self.get_lightboxes()
        resp['download_verify'] = False
        resp['download_url'] = url_for("SearchView:download",
                                       lang_code=g.current_lang,
                                       token=token)

        status_code, response = send_get('image/%s/download/verify' % token)
        if status_code == 200:
            resp['download_verify'] = True

        return jsonify(resp)


class ImageDetailsView(FlaskView, LightBoxMixin):

    route_base = '/<lang_code>/image-details/'

    @route("/<token>/", methods=["GET"])
    def get(self, token):
        g.download_verify = False
        g.current_plan = True
        g.alreadyBought = False
        g.is_free = False
        g.lightboxes = self.get_lightboxes()
        g.image = Image(token)
        g.image.download_url = url_for("SearchView:download",
                                       lang_code=g.current_lang,
                                       token=token)

        if not g.user.is_anonymous:
            status_code, response = send_get('image/free_photo_of_the_week')
            if token == response['image']['token']:
                g.is_free = True

            status_code, response = send_get(
                'user/earnings/license',
                {
                    'maxResults': app.config['EARNINGS_IMAGES_BY_PAGE'],
                    'pageNum': 0
                })

            for item in response['values']:
                if token == item['imageToken']:
                    g.alreadyBought = True

            status_code, response = send_get('user/licenses',
                                             {'activeOnly': True},
                                             nocache=True)

            if status_code == 200:
                if not response['values']:
                    g.current_plan = False

        if not g.is_free:
            status_code, response = send_get('image/%s/download/verify' %
                                             token)
            if status_code == 200:
                g.download_verify = True

        lightbox_form = LightboxForm()
        g.profile = User().get_profile_by_id(g.image.userName)

        return render_template('image-details.html',
                               lightbox_form=lightbox_form)


class ProfileView(FlaskView):

    route_base = '/<lang_code>/profile/'

    @login_required
    def plans(self):
        status_code, response = send_get('user/licenses', {'activeOnly': True},
                                         nocache=True)

        if status_code == 200:
            g.plans = response['values']

        return render_template('profile_plans.html')

    @login_required
    @route("/", methods=["GET", "POST"])
    def index(self):
        g.user = User().get_profile()
        g.neteller_acc = ''
        g.bank_acc = ''

        status_code, response = send_get('user/preferences', nocache=True)
        if status_code == 200:
            settings_form = SettingsForm(
                email_preferences=response['userCommunication'],
                units=response['userImageSizeMeasurement'])
        else:
            settings_form = SettingsForm()

        neteller_acc = self._get_neteller_acc()
        if neteller_acc:
            g.neteller_acc = neteller_acc

        bank_acc = self._get_bank_acc()
        if bank_acc:
            g.bank_acc = bank_acc

        if settings_form.validate_on_submit():
            email_preferences = settings_form.email_preferences.data
            units = settings_form.units.data
            status_code, response = \
                send_post('user/preferences',
                          {
                              'userCommunication': email_preferences,
                              'userImageSizeMeasurement': units,
                              'emailLanguage': 'en'
                          })

            if status_code == 200:
                return redirect(url_for('ProfileView:index',
                                        lang_code=g.current_lang,
                                        status='account'))

        return render_template('profile_preferences.html',
                               settings_form=settings_form)

    @login_required
    def billing(self):
        return render_template('profile_billing.html')

    def get_date_from_timestamp(self, timestamp):
        return datetime.datetime.fromtimestamp(int(timestamp/1000)).\
            strftime('%d %b %Y')

    @login_required
    @route("/purchase-history/", methods=["GET"])
    def purchase_history(self):
        status_code, response = send_get('user/licenses',
                                         {'activeOnly': False}, nocache=True)
        g.licenses = []
        g.active_licenses = []
        desc = {
            'BASIC': _('Standart License'),
            'PROFESSIONAL': _('Professional license')
        }
        desc_duration = {
            'MONTH': _('30-day Subscription'),
            'YEAR': _('365-day Subscription')
        }

        if status_code == 200:
            for item in response['values']:
                line = {
                    'date': self.get_date_from_timestamp(
                        item.get('purchaseDate', None)),
                    'description': '{duration} {desc}'.format(
                        duration=desc_duration[item.get('duration', 'MONTH')],
                        desc=desc[item.get('type', 'BASIC')]),
                    'total': item.get('licensePrice', 0),
                    'receipt': item.get('receiptId'),
                    'type': item.get('type'),
                    'repurchase': url_for(
                        'OrderView:index',
                        lang_code=g.current_lang,
                        license_type=item['type'].lower(),
                        duration=item['duration'].lower(),
                        count=item['imagesCount']),
                    'expired': item.get('expired')
                }
                g.licenses.append(line)

        status_code, response = send_get('user/licenses', {'activeOnly': True},
                                         nocache=True)
        if status_code == 200:
            g.active_licenses = [i['type'] for i in response['values']]

        return render_template('profile_purchase_history.html')

    def _get_earnings(self, url, params):
        status_code, response = send_get(url, params, nocache=True)
        if status_code == 200:
            return response['values']
        return []

    def _get_amount(self, endpoint):
        status_code, response = send_get(endpoint, nocache=True)
        if status_code == 200:
            return response['value']
        return 0

    def _prepare_app_earnings(self, earnings):
        earnings_list = []
        for item in earnings:
            buyers_count = 0
            summ = 0
            if 'firstBuyer' in item:
                buyers_count += 1
                if item['firstBuyerPrice']:
                    summ += item['firstBuyerPrice']
            if 'secondBuyer' in item:
                buyers_count += 1
                if item['secondBuyerPrice']:
                    summ += item['secondBuyerPrice']
            if item['image']:
                earnings_list.append({
                    'buyers_count': buyers_count,
                    'price': summ,
                    'token': item['imageToken'],
                    'uploadId': item['image']['uploadId']
                })

        return earnings_list

    def _get_neteller_acc(self):
        status_code, response = send_get('user/receiptmethods',
                              {'receiptMethod': 'NETELLER'}, nocache=True)
        if status_code == 200 and response['values'] and response['values'][0]:
            return response['values'][0]

        return None

    def _get_bank_acc(self):
        status_code, response = send_get('user/receiptmethods',
                              {'receiptMethod': 'BANK_ACCOUNT'}, nocache=True)
        if status_code == 200 and response['values'] and response['values'][0]:
            return response['values'][0]
        return None

    def _get_user_profit(self):
        status_code, response = send_get('user/profit')
        if status_code == 200:
            return response
        return None

    @login_required
    @route("/earnings/", methods=["GET", "POST"])
    def earnings(self):
        page = int(request.args.get('page', 1))
        g.tab = request.args.get('tabs')
        g.earnings = []
        g.grand_total = 0
        g.still_to_cash = 0
        g.neteller_acc = ''
        amount = 0

        paginator_form = PaginatorForm(page=page)

        if paginator_form.paginator_btn.data and \
                paginator_form.validate_on_submit():
            if request.form['page']:
                return redirect(url_for('ProfileView:earnings',
                                        lang_code=g.current_lang,
                                        page=request.form['page'],
                                        tabs=g.tab))

        data = {
            'maxResults': app.config['EARNINGS_IMAGES_BY_PAGE'],
            'pageNum': page
        }

        if g.tab == 'app':
            earnings = self._get_earnings('user/sales', data)
            g.earnings = self._prepare_app_earnings(earnings)
            amount = self._get_amount('user/sales/count')
        elif g.tab == 'web':
            g.purchases = self._get_earnings('user/purchases', data)

            for item in g.purchases:
                status_code, response = send_get('image/%s' %
                                                 item['imageToken'])
                image = response
                status, resp = send_get('user/earnings/image/history',
                {
                    'userId': g.user.id,
                    'imageToken': item['imageToken'],
                    'maxResults': app.config['EARNINGS_IMAGES_BY_PAGE'],
                    'pageNum': page
                })

                image['earn'] = 0
                for value in resp['values']:
                    image['earn'] += value['earned']
                image['earn'] = round(image['earn'], 2)
                image['earned_total'] = round(image['earn'] * 0.75, 2)

                g.earnings.append(image)

            amount = self._get_amount('user/earnings/license/count')

        status_code, response = send_get('user/earnings/grandtotal',
                                         nocache=True)
        if status_code == 200:
            g.grand_total = response['value']

        g.profit = self._get_user_profit()
        g.profit['licenseValue'] = round(g.profit['licenseValue'], 2)
        if g.profit:
            g.still_to_cash = g.profit['value'] + g.profit['licenseValue']
        neteller_acc = self._get_neteller_acc()
        if neteller_acc:
            g.neteller_acc = neteller_acc

        g.paginator = Paginator(amount, page)
        g.grand_total = round(g.grand_total, 2)
        g.still_to_cash = round(g.still_to_cash, 2)
        return render_template('profile_earnings.html',
                               paginator_form=paginator_form)

    @login_required
    @route("/change-password/", methods=["GET", "POST"])
    def change_password(self):
        change_password_form = ChangePasswordForm()
        if change_password_form.validate_on_submit():
            User().change_password(request.form['new_password'],
                                          request.form['current_password'])
            return redirect(url_for("ProfileView:index",
                                    lang_code=g.current_lang,
                                    status='password'))
        return render_template('profile_change_password.html',
                               change_password_form=change_password_form)

    @login_required
    @route("/change-email/", methods=["GET", "POST"])
    def change_email(self):
        change_email_form = ChangeEmailForm()
        if change_email_form.validate_on_submit():
            user = User().change_email(request.form['email'])
            if user.errors:
                set_errors(change_email_form, user.errors)
            else:
                return redirect(url_for("ProfileView:index",
                                        lang_code=g.current_lang,
                                        status='email'))
        return render_template('profile_change_email.html',
                               change_email_form=change_email_form)

    @login_required
    @route("/change-neteller/", methods=["GET", "POST"])
    def change_neteller_account(self):

        receiptMethodId = random_string()

        neteller_acc = self._get_neteller_acc()
        if neteller_acc:
            neteller_form = NetelletAccForm(
                is_edit=True,
                email=neteller_acc['emailAddress'],
                name=neteller_acc['fullName'])
            receiptMethodId = neteller_acc['receiptMethodId']
        else:
            neteller_form = NetelletAccForm()

        if neteller_form.validate_on_submit():
            data = {
                'receiptMethod': 'NETELLER',
                'emailAddress': request.form['email'],
                'fullName': request.form['name'],
                'receiptMethodId': receiptMethodId,
                'receiptMethodName': _('Withdrawal from photostockStock')
            }

            if request.form['is_edit'] == 'True':
                status_code, response = send_put('user/receiptmethods', data)
            else:
                status_code, response = send_post('user/receiptmethods', data)

            return redirect(url_for('ProfileView:index',
                                    lang_code=g.current_lang,
                                    status='account'))

        return render_template('profile_change_neteller.html',
                               neteller_form=neteller_form)

    @login_required
    @route("/change-bank-account/", methods=["GET", "POST"])
    def change_bank_account(self):
        receiptMethodId = random_string()

        bank_acc = self._get_bank_acc()
        if bank_acc:
            bank_form = BankAccForm(is_edit=True,
                                    name=bank_acc['benificiary'],
                                    iban=bank_acc['iban'])
            receiptMethodId = bank_acc['receiptMethodId']
        else:
            bank_form = BankAccForm()

        if bank_form.validate_on_submit():
            data = {
                'receiptMethod': 'BANK_ACCOUNT',
                'iban': request.form['iban'],
                'benificiary': request.form['name'],
                'receiptMethodId': receiptMethodId,
                'receiptMethodName': _('Withdrawal from photostockStock')
            }

            if request.form['is_edit'] == 'True':
                status_code, response = send_put('user/receiptmethods', data)
            else:
                status_code, response = send_post('user/receiptmethods', data)

            return redirect(url_for('ProfileView:index',
                                    lang_code=g.current_lang,
                                    status='account'))

        return render_template('profile_change_bank_account.html',
                               bank_form=bank_form)

    @login_required
    @route("/image-info/<token>", methods=["GET", "POST"])
    def image_info(self, token):
        return jsonify({})

    @login_required
    @route("billing/change-card/", methods=["GET", "POST"])
    def billing_change_card(self):
        order_form = OrderCardForm()
        return render_template("profile_billing_change_card.html",
                               order_form=order_form)

    @login_required
    @route("/billing/change-address/", methods=["GET", "POST"])
    def billing_change_address(self):
        order_form = OrderAddressForm()
        return render_template("profile_billing_change_address.html",
                               order_form=order_form)

    @login_required
    @route("/withdraw/", methods=["POST"])
    def withdraw(self):
        response = None
        neteller_acc = self._get_neteller_acc()
        profit = self._get_user_profit()
        if profit:
            summ = request.get_json()
            summ = summ['total_earn']
            if summ:
                status_code, response = \
                    send_post('payments/withdraw_with_neteller',
                              {
                                  'currency': 'EUR',
                                  'email': neteller_acc['emailAddress'],
                                  'grossAmount': summ,
                                  'netAmount': summ
                              })

                if status_code == 200:
                    return jsonify({'success': True})

        return jsonify({'success': False, 'error': response})

    @login_required
    @route("/withdraw_bank/", methods=["POST"])
    def withdraw_bank(self):
        response = None
        current_date = time.strftime("%d/%m/%Y")
        bank_acc = self._get_bank_acc()
        profit = self._get_user_profit()
        g.bank_acc = bank_acc
        if profit:
            summ = request.get_json()
            summ = summ['total_earn']
            if summ:
                status_code, response = \
                    send_post('payments/withdraw_with_bank_transfer',
                              {
                                  'beneficiary': bank_acc['benificiary'],
                                  'beneficiary_date': current_date,
                                  'beneficiary_iban': bank_acc['benificiary'],
                                  'payer_iban': bank_acc['iban'],
                                  'reason': _('personal'),
                                  'value': summ
                              })

                if status_code == 200:
                    return jsonify({'success': True})
        return jsonify({'success': False, 'error': response})

    @login_required
    @route("/billing/payment_delete/", methods=["GET", "DELETE"])
    def payment_delete(self):
        status_code, response = send_get('user/payingmethods',
                                         {'paymentMethod': 'SPARKLING18'})

        if status_code == 200 and response['values'] and response['values'][0]:
            status_code, response = send_delete('user/payingmethods',
                                                {
                                                    'paymentMethodId':
                                                        response['values'][0]
                                                })

        return redirect(url_for('ProfileView:billing',
                                lang_code=g.current_lang))


class LightboxesView(FlaskView, LightBoxMixin):

    route_base = '/<lang_code>/lightboxes/'

    @login_required
    def get(self):
        lightboxes = self.get_lightboxes()
        for lightbox in lightboxes:
            status_code, response = \
                send_get('image/{token}'.
                         format(token=lightbox['thumbnailToken']))

            if status_code == 200:
                lightbox['thumb'] = response['uploadId']

        g.lightboxes = lightboxes
        return render_template('lightboxes.html')


class LightboxView(FlaskView):
    route_base = '/<lang_code>/lightbox/'

    @login_required
    @route("/<lightbox_id>/")
    def get(self, lightbox_id):
        g.lightbox = Lightbox(lightbox_id)
        g.thumbs = []
        for item in g.lightbox.imageTokens or []:
            status_code, response = send_get('image/{token}'.
                                             format(token=item))
            if status_code == 200:
                g.thumbs.append({
                    'url': response['uploadId'],
                    'title': response['title'],
                    'token': response['token']
                })

        return render_template('lightbox_item.html')


class PricingView(FlaskView):

    route_base = '/<lang_code>/pricing/'

    @route("/", methods=["GET", "POST"])
    def index(self):
        status_code, response = send_get('user/licenses', {'activeOnly': True},
                                         nocache=True)

        if status_code == 200:
            g.plans = [x['type'] for x in response['values'] if x]

        if request.method == 'POST':
            license_type = request.form['license_type']
            duration = request.form.get('duration', 'month')
            count = request.form.get('count', 0)
            return redirect(url_for('OrderView:index',
                                    lang_code=g.current_lang,
                                    license_type=license_type,
                                    duration=duration,
                                    count=count))

        return render_template('pricing.html')


class OrderView(FlaskView):

    route_base = '/<lang_code>/order/'

    @login_required
    @route("/", methods=["GET", "POST"])
    def index(self):
        duration, license, g.summ = get_plan(request.args)
        return render_template('order-summary.html')

    @login_required
    @route("/process/", methods=["POST"])
    def process(self):
        success_redirect = ('http://stage.photostock.org/%s/'
                            % g.current_lang)
        unsuccess_redirect = ('http://stage.photostock.org/%s/'
                              'payment_unsuccessful'
                              % g.current_lang)
        images = request.form.get('count', 5)
        duration, license, summ = get_plan(request.form)
        status_code, response = \
            send_post('payments/pay_plan_with_sparkling18_web',
                      {
                          'currency': 'EUR',
                          'paymentAmount': summ,
                          "paymentFailureRedirectUrl": unsuccess_redirect,
                          "paymentSuccessRedirectUrl": success_redirect,
                          'licenseDto': {
                              'duration': duration,
                              'imagesCount': images,
                              'type': license,
                              'userId': g.user.id,
                              'licensePrice': summ,
                              'couponCode': request.form['coupon'],
                              'vatNumber': request.form['vat'],
                              'autorenew': request.form['autorenew']
                          }
                      })

        if status_code == 200:
            return redirect(response['value'])

    @login_required
    @route("/get-link/", methods=["GET", "POST"])
    def get_link(self):
        status_code, response = \
            send_post('payments/pay_plan_with_sparkling18_web',
                      {
                          'currency': 'EUR',
                          'paymentAmount': 25,
                          'licenseDto': {
                              'duration': 'MONTH',
                              'imagesCount': 25,
                              'type': 'BASIC',
                              'userId': g.user.id,
                              'licensePrice': 25
                          }
                      })

        if status_code == 200:
            return jsonify({'status': True, 'value': response['value']})

        return jsonify({'status': False})


class DownloadHistoryView(FlaskView):

    route_base = '/<lang_code>/download-history/'

    def __init__(self):
        self.license_type = ''
        self.year = 0

    @login_required
    @route("/", methods=["GET", "POST"])
    def index(self):
        page = int(request.args.get('page', 1))
        license_types = {
            'professional': 'PROFESSIONAL',
            'basic': 'BASIC'
        }

        g.license_type = None
        try:
            self.year = int(request.args.get('year', None))
            g.license_type = request.args.get('license_type')
            self.license_type = license_types[g.license_type]
        except KeyError:
            self.license_type = ''
        except ValueError:
            self.year = 0
        except TypeError:
            self.year = 0

        g.img_list = []
        g.year = self.year
        amount = 0
        results_per_page = 12

        paginator_form = PaginatorForm(page=page)

        if paginator_form.paginator_btn.data and \
                paginator_form.validate_on_submit():
            if request.form['page']:
                return redirect(url_for('DownloadHistoryView:index',
                                        lang_code=g.current_lang,
                                        page=request.form['page'],
                                        license_type=g.license_type,
                                        year=g.year))

        status_code, response = send_get('image/downloads',
                                         {
                                             'userId': g.user.id,
                                             'maxResults': results_per_page,
                                             'pageNum': page,
                                             'year': self.year,
                                             'licenseType': self.license_type
                                         },
                                         nocache=True)

        if status_code == 200:
            for item in response.get('values', []):
                image = Image()
                image.__dict__.update(item)
                image.download_url = url_for("SearchView:download",
                                             lang_code=g.current_lang,
                                             token=image.imageToken)
                g.img_list.append(image)

        status_code, reponse = send_get('image/downloads/count',
                                        {
                                            'userId': g.user.id,
                                            'year': self.year,
                                            'licenseType': self.license_type
                                        },
                                        nocache=True)
        if status_code == 200:
            amount = reponse['value']

        status_code, reponse = send_get('image/downloads/years',
                                        {'userId': g.user.id})
        if status_code == 200:
            g.years = reponse['values']

        g.paginator = Paginator(amount, page, results_per_page)
        g.licenses = {
            'BASIC': _('Basic License'),
            'PROFESSIONAL': _('Professional License')
        }

        return render_template('download-history.html',
                               paginator_form=paginator_form)


class PrivacyPolicyView(FlaskView):

    route_base = '/<lang_code>/privacy_policy/'

    @route("/")
    def index(self):
        return render_template('privacy_policy.html', lang_code=g.current_lang)


class TermsOfUseView(FlaskView):

    route_base = '/<lang_code>/terms_of_use/'

    @route("/")
    def index(self):
        return render_template('terms_of_use.html', lang_code=g.current_lang)


class ContactUsView(FlaskView):

    route_base = '/<lang_code>/contact_us/'

    @route("/", methods=["GET", "POST"])
    def index(self):
        contact_us_form = ContactUsForm()
        if contact_us_form.validate_on_submit():
            app.config.update(dict(
                DEBUG=True,
                MAIL_SERVER='smtp.gmail.com',
                MAIL_PORT=587,
                MAIL_USE_TLS=True,
                MAIL_USE_SSL=False,
                MAIL_USERNAME='test@gmail.com',
                MAIL_PASSWORD='password',
            ))

            name = request.form['name']
            email = request.form['email']
            text = request.form['text']
            mail = Mail()
            mail.init_app(app)
            msg = Message(text, sender=email, recipients="support@photostock.org")
            return mail.send(msg)

        return render_template('contact_us.html',
                               contact_us_form=contact_us_form)


class HowItWorksView(FlaskView):

    route_base = '/<lang_code>/how_it_works/'

    @route("/")
    def index(self):
        return render_template('how_it_works.html', lang_code=g.current_lang)


class PaymentSuccessView(FlaskView):

    route_base = '/<lang_code>/payment_success/'

    @route("/")
    def index(self):
        return render_template('payment_success.html',
                               lang_code=g.current_lang)


class PaymentUnsuccessfulView(FlaskView):

    route_base = '/<lang_code>/payment_unsuccessful/'

    @route("/")
    def index(self):
        return render_template('unsuccessful_payment.html',
                               lang_code=g.current_lang)