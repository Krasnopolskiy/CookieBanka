from logging import error
from re import template
from flask import render_template_string, render_template, redirect, flash, session
from flask.helpers import url_for
from flask_login import login_user, logout_user, login_required, current_user
from app import app, db
from . import misc, models, forms


@app.route('/')
def index():
    return render_template('index.html', pagename='Index')


@app.route('/users')
@login_required
def users():
    users = models.User.query.all()
    return render_template('users.html', pagename='Users', users=users)


@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    form = forms.CookieForm()
    if form.validate_on_submit():
        cookie = models.Cookie(name=form.name.data, value=form.value.data, user_id=current_user.id)
        db.session.add(cookie)
        db.session.commit()
        flash('Cookie was created')
        return redirect(url_for('dashboard'))
    if form.errors:
        [flash(*form.errors[error]) for error in form.errors]
        return redirect(url_for('dashboard'))
    cookies = models.Cookie.query.filter_by(user_id=current_user.id)[::-1]
    return render_template('dashboard.html', form=form, pagename='Dashboard', cookies=cookies)


@app.route('/cookie/<cookie_id>')
@login_required
def cookie(cookie_id):
    if not cookie_id.isdigit():
        flash('Incorrect cookie id')
        return redirect(url_for('dashboard'))
    cookie_id = int(cookie_id)
    cookie = models.Cookie.query.filter_by(id=cookie_id).first()
    if not cookie:
        flash('Cookie does not exist')
        return redirect(url_for('dashboard'))
    if cookie.user_id != current_user.id:
        flash('You do not have access')
        return redirect(url_for('dashboard'))
    template = misc.load_template_string('cookie')
    template = template.format(name=cookie.name, value=cookie.value, dashboard=url_for('dashboard'), delete=url_for('delete', cookie_id=cookie.id))
    return render_template_string(template)


@app.route('/delete/<cookie_id>')
@login_required
def delete(cookie_id):
    if not cookie_id.isdigit():
        flash('Incorrect cookie id')
        return redirect(url_for('dashboard'))
    cookie_id = int(cookie_id)
    cookie = models.Cookie.query.filter_by(id=cookie_id).first()
    if not cookie:
        flash('Cookie does not exist')
        return redirect(url_for('dashboard'))
    if cookie.user_id != current_user.id:
        flash('You do not have access')
        return redirect(url_for('dashboard'))
    db.session.delete(cookie)
    db.session.commit()
    flash('Cookie was deleted')
    return redirect(url_for('dashboard'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = forms.LoginForm()
    if form.validate_on_submit():
        user = models.User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user)
        return redirect(url_for('index'))
    return render_template('login.html', form=form, pagename='Sign in')


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = forms.RegistrationForm()
    if form.validate_on_submit():
        user = models.User(username=form.username.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('User is registered')
        return redirect(url_for('login'))
    if form.errors:
        [flash(*form.errors[error]) for error in form.errors]
        return redirect(url_for('register'))
    return render_template('register.html', form=form, pagename='Register')


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))