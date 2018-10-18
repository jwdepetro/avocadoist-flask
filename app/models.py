import hashlib
import os
import time
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.datastructures import FileStorage
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
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    images = db.relationship('PostImage', backref='post', lazy='dynamic')

    def save_images(self, images):
        for image in images:
            name = hashlib.md5(
                ('post' + str(time.time())).encode('utf-8')).hexdigest()[:15] + '.png'
            photos.save(image, name=name)
            self.image_name = name
            i = PostImage(post=self, name=name)
            db.session.add(i)
            self.images.append(i)

    def delete_images(self):
        if self.images:
            for image in self.images:
                file_path = photos.path(image.name)
                os.remove(file_path)


class PostImage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))
    name = db.Column(db.String(120))

    def __repr__(self):
        return '<Image {}>'.format(self.name)

    def url(self):
        if self.name:
            return photos.url(self.name)
        else:
            return None


def __repr__(self):
    return '<Post {}>'.format(self.title)
