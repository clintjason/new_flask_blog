import os
import secrets
from PIL import Image
from flaskblog import app, db, bcrypt
from flask import render_template, url_for, flash, redirect, request
from flaskblog.forms import RegistrationForm, LoginForm, UpdateAccountForm
from flaskblog.models import User, Post
from flask_login import login_user, current_user, logout_user, login_required

posts = [
    {
        'author': 'Corey Asbury',
        'title' : 'Blog Post 1',
        'content': 'First post content',
        'date_posted' : 'April 20, 2018'
    },
    {
        'author': 'Michael Koulinaous',
        'title' : 'Blog Post 2',
        'content': 'Second post content',
        'date_posted' : 'April 21, 2018'
    }
]
@app.route("/home")
@app.route("/")
def home():
    return render_template('home.html', posts=posts)

@app.route("/about")
def about():
    return render_template("about.html",title='About')

@app.route("/register", methods=['GET','POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    registration_form = RegistrationForm()
    if registration_form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(
                registration_form.password.data).decode('utf-8')
        user = User(username=registration_form.username.data, password= hashed_password,
                email= registration_form.email.data)
        db.session.add(user)
        db.session.commit()
        flash('Your Account has been created! You can now Log in', 'success')
        return redirect(url_for("login"))
    return render_template('register.html', title='Register', form=registration_form)


@app.route("/login", methods=['GET','POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    login_form = LoginForm()
    if login_form.validate_on_submit():
        user = User.query.filter_by(email=login_form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, login_form.password.data):
            login_user(user, remember=login_form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Email or Password Incorrect','danger')
    return render_template('login.html', title='Login', form=login_form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))

def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)  # returns f_name and f_ext
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics',picture_fn)
    # resize image before saving
    output_size = (125,125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)   # resize image
    i.save(picture_path)   #save resized image

    return picture_fn

@app.route('/account', methods=['GET','POST'])
@login_required
def account():
    account_form = UpdateAccountForm()
    if account_form.validate_on_submit():
        if account_form.picture.data:
            picture_file = save_picture(account_form.picture.data)
            current_user.image_file = picture_file
        current_user.username = account_form.username.data
        current_user.email = account_form.email.data
        db.session.commit()
        flash('Your account has been updated', 'success')
        return redirect(url_for('account'))
    
    elif request.method == 'GET':
        account_form.username.data = current_user.username
        account_form.email.data = current_user.email
        
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('account.html', title='Account', 
            image_file= image_file, form=account_form)