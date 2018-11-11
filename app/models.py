import hashlib
import os
import time
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.datastructures import FileStorage
from app import app, db, login, photos, upload_file, delete_file


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    default = db.Column(db.Boolean, default=False)
    name = db.Column(db.String(64))
    about = db.Column(db.String(10000000))
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    image_name = db.Column(db.String(120))
    posts = db.relationship('Post', backref='author', lazy='dynamic')

    def __repr__(self):
        return '<User {}>'.format(self.email)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def image_url(self):
        if self.image_name:
            return '{}{}'.format(app.config['S3_LOCATION'], self.image_name)
        else:
            return None

    def save_image(self, image):
        if self.image_name:
            self.delete_image()
        name = upload_file(image)
        self.image_name = name

    def delete_image(self):
        if self.image_name:
            if delete_file(self.image_name):
                self.image_name = None


post_tags = db.Table(
    'post_tag',
    db.Column('post_id', db.Integer, db.ForeignKey('post.id')),
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'))
)


class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))

    def __repr__(self):
        return '<Tag {}>'.format(self.name)


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(10000000))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    images = db.relationship('PostImage', backref='post', lazy='dynamic')
    tags = db.relationship('Tag', secondary=post_tags, lazy='dynamic')

    def __repr__(self):
        return '<Post {}>'.format(self.title)

    def save_images(self, images):
        for file in images:
            name = upload_file(file)
            i = PostImage(post=self, name=name)
            db.session.add(i)
            self.images.append(i)

    def delete_images(self):
        if self.images:
            for image in self.images:
                if delete_file(image.name):
                    db.session.delete(image)
                    db.session.commit()

    def save_tags(self, tag_names):
        self.delete_tags()
        for name in tag_names:
            tag = Tag.query.filter_by(name=name).first()
            if not tag:
                tag = Tag(name=name)
                db.session.add(tag)
            self.tags.append(tag)

    def delete_tags(self):
        for tag in self.tags:
            self.tags.remove(tag)


class PostImage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))
    name = db.Column(db.String(120))

    def __repr__(self):
        return '<PostImage {}>'.format(self.name)

    def url(self):
        if self.name:
            return '{}{}'.format(app.config['S3_LOCATION'], self.name)
        else:
            return None
