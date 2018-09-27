from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_user, logout_user
from werkzeug.urls import url_parse

from app import app, db
from app.forms import LoginForm, PostForm
from app.models import User, Post


@app.route('/')
@app.route('/index')
def index():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.timestamp.desc()).paginate(page, 50, False)
    return render_template('home.html', posts=posts.items)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', form=form, title='Login')


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/post', methods=['GET', 'POST'])
def post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(
            title=form.title.data,
            body=form.body.data
        )
        db.session.add(post)
        db.session.commit()
        flash('Posted!')
        return redirect(url_for('index'))
    return render_template('post.html', form=form, title='Post')
