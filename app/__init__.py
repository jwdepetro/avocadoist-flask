from flask import Flask, url_for
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_uploads import UploadSet, configure_uploads, IMAGES, patch_request_class
from flask_simplemde import SimpleMDE
from flask_misaka import Misaka
from werkzeug.utils import secure_filename
from config import Config
from io import BytesIO, StringIO
from PIL import Image
import os
import boto3
import uuid

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
moment = Moment(app)
login = LoginManager(app)
login.login_view = 'login'
photos = UploadSet('photos', IMAGES)
configure_uploads(app, photos)
patch_request_class(app)

app.config['SIMPLEMDE_JS_IIFE'] = True
app.config['SIMPLEMDE_USE_CDN'] = True
SimpleMDE(app)
Misaka(app)

s3 = boto3.client(
    "s3",
    aws_access_key_id=app.config['S3_KEY'],
    aws_secret_access_key=app.config['S3_SECRET']
)


@app.context_processor
def override_url_for():
    return dict(url_for=dated_url_for)


def dated_url_for(endpoint, **values):
    if endpoint == 'static':
        filename = values.get('filename', None)
        if filename:
            file_path = os.path.join(app.root_path,
                                     endpoint, filename)
            values['q'] = int(os.stat(file_path).st_mtime)
    return url_for(endpoint, **values)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower(
           ) in app.config["ALLOWED_EXTENSIONS"]


def upload_file(file):
    # try:
    if file and allowed_file(file.filename):
        bucket_name = app.config['S3_BUCKET']
        file.filename = secure_filename(file.filename)
        key_name = str(uuid.uuid4())

        img = Image.open(file)
        wpercent = (600 / float(img.size[0]))
        hsize = int((float(img.size[1]) * float(wpercent)))
        img = img.resize((600, hsize), Image.ANTIALIAS)
        buffer = BytesIO()
        img.save(buffer, 'PNG')
        buffer.seek(0)

        s3.upload_fileobj(
            buffer,
            bucket_name,
            key_name,
            ExtraArgs={
                'ACL': 'public-read',
                # 'ContentType': file.content_type
            }
        )
        return key_name
    return None
    # except Exception as e:
    # print(str(e))
    # return None


def delete_file(name):
    try:
        response = s3.delete_object(
            Bucket=app.config['S3_BUCKET'],
            Key=name
        )
        return 'DeleteMarker' in response and response['DeleteMarker'] == True
    except Exception as e:
        return False


from app import routes, models
