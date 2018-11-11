from app import app
from io import BytesIO, StringIO
from PIL import Image
from werkzeug.utils import secure_filename
from flask_uploads import IMAGES
import os
import boto3
import uuid

s3 = boto3.client(
    "s3",
    aws_access_key_id=app.config['S3_KEY'],
    aws_secret_access_key=app.config['S3_SECRET']
)


def image_url(name):
    if name:
        return '{}{}'.format(app.config['S3_LOCATION'], name)
    return None


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in IMAGES


def create_image(file):
    try:
        if file and allowed_file(file.filename):
            bucket_name = app.config['S3_BUCKET']
            file.filename = secure_filename(file.filename)
            key_name = str(uuid.uuid4())

            # Resize the image
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
                    'ContentType': file.content_type
                }
            )
            return key_name
        return None
    except Exception as e:
        return None


def delete_image(name):
    try:
        response = s3.delete_object(
            Bucket=app.config['S3_BUCKET'],
            Key=name
        )
        return 'DeleteMarker' in response and response['DeleteMarker'] == True
    except Exception as e:
        return False
