from flask_assets import Bundle
from webassets.filter import get_filter
from app import assets

################
### Landing  ###
################

landing_js = Bundle(
        'js/jquery.min.js',
        'scripts/config-staging.js',
        'scripts/landing.js', 
    output='bundles/js/landing.js'
)

logged_js = Bundle(
        'js/jquery.min.js',
        'scripts/logged.js', 
    output='bundles/js/logged.js'
)

assets.register('logged_js', logged_js)
assets.register('landing_js', landing_js)