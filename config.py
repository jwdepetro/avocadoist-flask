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

    # S3
    S3_BUCKET = os.environ.get('S3_BUCKET')
    S3_KEY = os.environ.get('S3_KEY')
    S3_SECRET = os.environ.get('S3_SECRET_ACCESS_KEY')
    S3_LOCATION = 'http://{}.s3.amazonaws.com/'.format(S3_BUCKET)
    ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif', 'tiff', 'bmp'])

    # Markdown Editor
    SIMPLEMDE_JS_IIFE = True
    SIMPLEMDE_USE_CDN = True


