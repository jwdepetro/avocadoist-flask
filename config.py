import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    # App
    SECRET_KEY = os.environ.get('SECRET_KEY') or \
                 'no-secret-key-exists'

    UPLOADED_PHOTOS_DEST = os.environ.get('UPLOADED_PHOTOS_DEST') or \
                           os.getcwd() + '/storage/images'

    # SQL
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
                              'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
