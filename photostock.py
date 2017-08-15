import os

from flask import Flask

from settings import Production, Develop
from app.views import IndexView, UserView, SearchView, PricingView, \
    before_request, LightboxesView, ImageDetailsView, LightboxView, \
    OrderView, ProfileView, DownloadHistoryView, PrivacyPolicyView, \
    TermsOfUseView, ContactUsView, HowItWorksView, PaymentSuccessView, \
    PaymentUnsuccessfulView
from app.helpers import babel, get_section, date_format_friendly, \
    date_simple, thumb_url

app = Flask(__name__)

try:
    filename = os.path.join(app.root_path, '.production')
    f = open(filename)
    f.close()
    app.config.from_object(Production)
except:
    app.config.from_object(Develop)

app.before_request(before_request)

babel.init_app(app)

app.template_folder = "templates"

app.static_folder = "static"

# register template filters

app.jinja_env.filters['get_section'] = get_section

app.jinja_env.filters['data_format_friendly'] = date_format_friendly

app.jinja_env.filters['date_simple'] = date_simple

app.jinja_env.filters['thumb_url'] = thumb_url

# end register template filters

# register app components

IndexView.register(app)

UserView.register(app)

SearchView.register(app)

PricingView.register(app)

LightboxesView.register(app)

ImageDetailsView.register(app)

OrderView.register(app)

LightboxView.register(app)

ProfileView.register(app)

DownloadHistoryView.register(app)

PrivacyPolicyView.register(app)

TermsOfUseView.register(app)

ContactUsView.register(app)

HowItWorksView.register(app)

PaymentSuccessView.register(app)

PaymentUnsuccessfulView.register(app)

# end register app components

if __name__ == "__main__":
    if app.debug:
        use_debugger = True
    app.run()
