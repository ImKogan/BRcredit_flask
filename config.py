'''
config.py
'''

import os
import json
with open('config.json') as config:
    options = json.load(config)
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    ''' configure project parameters from congig.json - options dict'''
    SECRET_KEY = options["SECRET_KEY"]
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.googlemail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', '587'))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in \
        ['true', 'on', '1']
    MAIL_USERNAME = options["MAIL_USERNAME"]
    MAIL_PASSWORD = options["MAIL_PASSWORD"]
    BRCREDIT_MAIL_SUBJECT_PREFIX = '[BRcredit]'
    BRCREDIT_MAIL_SENDER = 'BRcredit Admin '+'<'+options["BRCREDIT_ADMIN"]+'>'
    BRCREDIT_ADMIN = options["BRCREDIT_ADMIN"]
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    HOST = options["HOST"]

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    ''' development configuration'''
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'data-dev.sqlite')


class TestingConfig(Config):
    ''' testing configuration'''
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or \
        'sqlite://'


class ProductionConfig(Config):
    ''' production configuration'''
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'data.sqlite')


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,

    'default': DevelopmentConfig
}
