from flaskblog import app, db, bcrypt
from flask import render_template, url_for, flash, redirect, request
from flaskblog.forms import RegistrationForm, LoginForm
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

@app.route('/account', methods=['GET','POST'])
@login_required
def account():
    return render_template('account.html', title='Account')