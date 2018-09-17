from flask_login import login_user, current_user, logout_user, login_required
from flask_mail import Message
from flask import render_template, url_for, flash, redirect, request, abort, Blueprint
from flaskblog.users.forms import (RegistrationForm, LoginForm, UpdateAccountForm,
                            RequestResetForm, ResetPasswordForm)
from flaskblog import db, bcrypt
from flaskblog.models import User, Post
from flaskblog.users.utils import save_picture, send_reset_email

users = Blueprint('users', __name__)


@users.route("/register", methods=['GET','POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    registration_form = RegistrationForm()
    if registration_form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(
                registration_form.password.data).decode('utf-8')
        user = User(username=registration_form.username.data, password= hashed_password,
                email= registration_form.email.data)
        db.session.add(user)
        db.session.commit()
        flash('Your Account has been created! You can now Log in', 'success')
        return redirect(url_for("users.login"))
    return render_template('register.html', title='Register', form=registration_form)


@users.route("/login", methods=['GET','POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    login_form = LoginForm()
    if login_form.validate_on_submit():
        user = User.query.filter_by(email=login_form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, login_form.password.data):
            login_user(user, remember=login_form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.home'))
        else:
            flash('Login Unsuccessful. Email or Password Incorrect','danger')
    return render_template('login.html', title='Login', form=login_form)

@users.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.home'))

@users.route('/account', methods=['GET','POST'])
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
        return redirect(url_for('users.account'))
    
    elif request.method == 'GET':
        account_form.username.data = current_user.username
        account_form.email.data = current_user.email
        
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('account.html', title='Account', 
            image_file= image_file, form=account_form)


@users.route("/user/<string:username>")
def user_posts(username):
    # The page argument is optional and its default value is one
    #type int is to throw a value error if an int is not passed
    page = request.args.get('page', 1, type=int)
    # Get user by username of return a not found error
    user = User.query.filter_by(username=username).first_or_404() 
    posts = Post.query.filter_by(author=user)\
            .order_by(Post.date_posted.desc())\
            .paginate(page=page,per_page=5)
    return render_template('user_posts.html', posts=posts, user=user)



@users.route('/reset_password',methods=['GET','POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('An email has been sent with instructions to reset the password', 'info')
        return redirect(url_for('users.login'))
    return render_template('reset_request.html', form=form, title='Reset Password')


@users.route('/reset_password/<token>',methods=['GET','POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('Token Expired or Invalid','warning')
        return redirect(url_for('users.reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(
                form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash('Your Password has been updated! You can now Log in', 'success')
        return redirect(url_for("users.login"))
    return render_template('reset_token.html', form=form, title='Reset Password')