from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse
from app import app, db
from app.forms import LoginForm, PostForm, UserForm
from app.models import User, Post, Tag, post_tags
from sqlalchemy import func
from sqlalchemy.orm import load_only


@app.errorhandler(404)
def page_not_found(e):
    return redirect(url_for('index'))


@app.context_processor
def inject_tag():
    return dict(active_tag=request.args.get('tag', None))


@app.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    tag = request.args.get('tag', None)
    if tag:
        q = Post.query.filter(Post.tags.any(Tag.name == tag))
    else:
        q = Post.query
    posts = q.order_by(Post.timestamp.desc()).paginate(page, 50, False)
    next_url = url_for(
        'index', page=posts.next_num) if posts.has_next else None
    prev_url = url_for(
        'index', page=posts.prev_num) if posts.has_prev else None
    count = db.func.count('*').label('ct')
    tags = (db.session
            .query(Tag.name, count)
            .join(post_tags)
            .group_by(Tag.id)
            .order_by(count.desc())
            .limit(5)
            .all())
    return render_template('home.html', posts=posts.items, tags=tags, next_url=next_url, prev_url=prev_url)


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


@app.route('/about-me')
def about_me():
    user = User.query.filter_by(default=True).first_or_404()
    return render_template('about_me.html', user=user, title='About Me')


@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = UserForm()
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.email = form.email.data
        current_user.about = form.about.data
        image = request.files.get('image')
        if image:
            current_user.save_image(image)
        if form.password.data:
            current_user.set_password(form.password.data)
        db.session.commit()
        if current_user.default:
            return redirect(url_for('about_me'))
        else:
            return redirect(url_for('index'))
    elif request.method == 'GET':
        form.name.data = current_user.name
        form.email.data = current_user.email
        form.about.data = current_user.about
    return render_template('profile.html', form=form, title='Edit Profile')


@app.route('/post', methods=['GET', 'POST'])
@login_required
def post():
    form = PostForm()
    print(form.tags.data)
    if form.validate_on_submit():
        existing = Post.query.filter_by(title=form.title.data).first()
        if existing is not None:
            flash('Please choose a different title.')
            return redirect(url_for('post'))
        post = Post(
            title=form.title.data,
            body=form.body.data,
            author=current_user
        )
        images = request.files.getlist('images')
        if images:
            post.save_images(images)
        if form.tags.data:
            tags = form.tags.data.split(',')
            post.save_tags(tags)
        db.session.add(post)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('edit_post.html', form=form, title='Post')


@app.route('/post/<string:path>')
def view_post(path):
    title = path.replace('-', ' ')
    post = Post.query.filter(func.lower(Post.title) ==
                             func.lower(title)).first_or_404()
    return render_template('view_post.html', post=post)


@app.route('/post/<id>/edit', methods=['GET', 'POST'])
@login_required
def edit_post(id):
    post = Post.query.filter_by(id=id).first_or_404()
    form = PostForm()
    if form.validate_on_submit():
        images = request.files.getlist('images')
        if images:
            post.delete_images()
            post.save_images(images)
        if form.tags.data:
            tags = form.tags.data.split(',')
            post.save_tags(tags)
        post.title = form.title.data
        post.body = form.body.data
        db.session.commit()
        return redirect(url_for('view_post', path=post.path))
    elif request.method == 'GET':
        def map_name(tag):
            return tag.name
        form.title.data = post.title
        form.body.data = post.body
        tags = []
        for tag in post.tags.all():
            tags.append(tag.name)
        form.tags.data = ','.join(tags)
    return render_template('edit_post.html', form=form, post=post, title='Edit Post')


@app.route('/post/<id>/delete')
@login_required
def delete_post(id):
    post = Post.query.filter_by(id=id).first_or_404()
    post.delete_images()
    post.delete_tags()
    db.session.delete(post)
    db.session.commit()
    return redirect('index')
