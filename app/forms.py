from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, FileField, SelectMultipleField
from wtforms.fields.html5 import DateTimeLocalField
from wtforms.validators import DataRequired, Email, EqualTo
from app import photos
from app.models import Tag
from datetime import datetime


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class PostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    timestamp = DateTimeLocalField('Date', validators=[
                                   DataRequired()], format="%Y-%m-%dT%H:%M:%S", default=datetime.today)
    body = TextAreaField('Body', validators=[DataRequired()])
    images = FileField(validators=[FileAllowed(photos, u'Images only!')])
    meta_title = StringField('Meta Title', validators=[DataRequired()])
    meta_description = TextAreaField(
        'Meta Description', validators=[DataRequired()])
    tags = StringField('Tags')
    submit = SubmitField('Post')


class PostCommentForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    comment = TextAreaField('Comment', validators=[DataRequired()])
    submit = SubmitField('Comment')


class UserForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    about = TextAreaField('About')
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password')
    confirm_password = PasswordField('Confirm Password', validators=[
                                     EqualTo('password', message='Passwords do not match')])
    image = FileField(validators=[FileAllowed(photos, u'Images only!')])
    submit = SubmitField('Update')
