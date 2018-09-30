import hashlib
import os
import time
from datetime import datetime

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from app import db, login, photos


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    posts = db.relationship('Post', backref='author', lazy='dynamic')

    def __repr__(self):
        return '<User {}>'.format(self.email)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(360))
    image_name = db.Column(db.String(120))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def image_url(self):
        if self.image_name:
            return photos.url(self.image_name)
        else:
            return None

    def save_image(self, image):
        name = hashlib.md5(('admin' + str(time.time())).encode('utf-8')).hexdigest()[:15] + '.png'
        photos.save(image, name=name)
        self.image_name = name

    def delete_image(self):
        if self.image_name:
            file_path = photos.path(self.image_name)
            os.remove(file_path)


def __repr__(self):
    return '<Post {}>'.format(self.title)
