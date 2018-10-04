from flask import Flask
from flask_login import LoginManager
from flask_assets import Environment
from firebase_admin import credentials
from configs import production as config
from flask_restful import Api
from celery import Celery
import firebase_admin
from raven.contrib.flask import Sentry
from flask_gzip import Gzip
import twitter

apiTwitter = twitter.Api(consumer_key=config.twitter["consumerKey"],
                  consumer_secret=config.twitter["consumerSecret"],
                  access_token_key=config.twitter["accessKey"],
                  access_token_secret=config.twitter["accessSecret"],
                  tweet_mode="extended")

app = Flask(__name__)
app.secret_key = "askdhabiuhasdjahbjda"
gzip = Gzip(app)

sentry = Sentry(app, dsn='https://340895e4e4d9400e850bcab30058be3d:f18ab2bde06440e9950a762e5fe93fec@sentry.io/1282333')

endpoints = Api(app)

assets = Environment(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "sign_in"

cred = credentials.Certificate(config.firebase['serviceAccount'])
firebase_admin.initialize_app(cred, config.firebase)

app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'
app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379/0'

celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)

import methods
import routes
import api