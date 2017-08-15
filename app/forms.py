import pycountry
from flask_wtf import Form
from wtforms import widgets, StringField, PasswordField, SubmitField, \
    SelectField, IntegerField, SelectMultipleField, RadioField, HiddenField, \
    TextField, TextAreaField
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired, Email, Length
from flask_babel import lazy_gettext as _


class LoginForm(Form):
    email = EmailField(_("Email Address"), validators=[DataRequired()])
    password = PasswordField(_("Password"), validators=[DataRequired()])
    login_btn = SubmitField(_("Sign In"))


class RegisterForm(Form):
    username = StringField(_("Username"), validators=[DataRequired()])
    email = EmailField(_("Email Address"), validators=[Email(),
                                                       DataRequired()])
    password = PasswordField(_("Password"), validators=[DataRequired(),
                                                        Length(6)])
    password_confirm = PasswordField(_('Confirm Password'))
    register_btn = SubmitField(_("Create Account"))


class RecoverPasswordForm(Form):
    email = StringField(_("Enter your email address below and we'll send you"
                          " a link to reset your password"),
                        validators=[DataRequired()])
    recover_btn = SubmitField(_("Send Reset Link"))


class QuickSearchForm(Form):
    TYPE_CHOICES = (("tag", "Tag"),
                    ("title", "Title"),
                    ("author", "Author"),)
    keyword = StringField(_("Find..."))
    type = SelectField("", choices=TYPE_CHOICES, default='tag')
    quick_search_btn = SubmitField(" ")


class PaginatorForm(Form):
    page = StringField()
    paginator_btn = SubmitField(" ")


class LightboxForm(Form):
    title = StringField()
    lightbox_btn = SubmitField("Save")


class OrderCardForm(Form):
    MONTHS = ((1, _('1 - January')),
              (2, _('2 - February')),
              (3, _('3 - March')),
              (4, _('4 - April')),
              (5, _('5 - May')),
              (6, _('6 - June')),
              (7, _('7 - July')),
              (8, _('8 - August')),
              (9, _('9 - September')),
              (10, _('10 - October')),
              (11, _('11 - November')),
              (12, _('12 - December')))
    card_no = IntegerField(_("Credit Card Number"),
                           validators=[DataRequired()])
    exp_date_month = SelectField(_("Expiration Date"), choices=MONTHS,
                                 validators=[DataRequired()])
    exp_date_year = SelectField('',
                                choices=[[i, i] for i in range(2016, 2026)])
    security_code = IntegerField(_("Security Code"),
                                 validators=[DataRequired()])
    order_card_btn = SubmitField(_('Save Changes'))


class OrderAddressForm(Form):
    COUNTRIES = ((item.alpha2, item.name) for item in pycountry.countries)
    first_name = StringField(_("First Name"), validators=[DataRequired()])
    last_name = StringField(_("Last Name"), validators=[DataRequired()])
    company = StringField(_("Company"))
    street = StringField(_("Street Address"), validators=[DataRequired()])
    city = StringField(_("City"), validators=[DataRequired()])
    state = StringField(_("State"))
    postal_code = StringField(_("Postal Code"), validators=[DataRequired()])
    country = SelectField(choices=COUNTRIES, validators=[DataRequired()])
    order_address_btn = SubmitField(_('Save Changes'))


class OrderForm(OrderCardForm, OrderAddressForm):
    order_btn = SubmitField(_('Process Order >'))


class ChangePasswordForm(Form):
    current_password = PasswordField(_("Current Password"))
    new_password = PasswordField(_("New Password"),
                                 validators=[Length(6), DataRequired()])
    new_password_confirm = PasswordField(_("Confirm New Password"),
                                         validators=[DataRequired()])
    change_password_btn = SubmitField(_("Save Changes"))


class ChangeEmailForm(Form):
    email = EmailField(_("New Email"), validators=[DataRequired()])
    email_confirm = EmailField(_("Confirm New Email"),
                               validators=[DataRequired()])
    change_email_btn = SubmitField(_("Save Changes"))


class MultiCheckboxField(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()


class SettingsForm(Form):
    EMAIL_PREFERENCES = (('TUTORIALS_AND_CONTENT',
                          _('Design inspiration, tutorial and \
                            professionally curated content')),
                         ('OFFERS_AND_DEALS',
                          _('Special offers and amazing deals')),
                         ('EDUCATION_AND_UPDATES',
                          _('Product education and updates')))
    UNITS = (('INCHES', 'Inches'),
             ('CENTIMETERS', 'Centimetres'))
    email_preferences = MultiCheckboxField('', choices=EMAIL_PREFERENCES)
    units = RadioField('', choices=UNITS, default='INCHES')


class NetelletAccForm(Form):
    name = StringField(_("Name on your account"), validators=[DataRequired()])
    email = EmailField(_("Email assosiated to the Netteler account"),
                       validators=[DataRequired()])
    neteller_acc_btn = SubmitField(_("Save Changes"))
    is_edit = HiddenField('', default=False)


class BankAccForm(Form):
    name = StringField(_("Name and surname on your account"),
                       validators=[DataRequired()])
    iban = StringField(_("IBAN"), validators=[DataRequired()])
    bank_acc_btn = SubmitField(_("Save Changes"))
    is_edit = HiddenField('', default=False)


class ContactUsForm(Form):
    name = StringField(_("Name"),
                       validators=[DataRequired()])
    email = StringField(_("E-mail"), validators=[DataRequired()])
    text = TextAreaField(_("Message"), validators=[DataRequired()])
    submit_btn = SubmitField(_("Submit"))