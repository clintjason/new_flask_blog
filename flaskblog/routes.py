import os
import secrets
from PIL import Image
from flaskblog import app, db, bcrypt
from flask import render_template, url_for, flash, redirect, request, abort
from flaskblog.forms import RegistrationForm, LoginForm, UpdateAccountForm, PostForm
from flaskblog.models import User, Post
from flask_login import login_user, current_user, logout_user, login_required

@app.route("/home")
@app.route("/")
def home():
    # The page argument is optional and its default value is one
    #type int is to throw a value error if an int is not passed
    page = request.args.get('page', 1, type=int) 
    posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page,per_page=5)
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

@app.route("/post/new", methods=['GET','POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title=form.title.data, content=form.content.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Your post has been created','success')
        return redirect(url_for('home'))
    return render_template('create_post.html', title='New Post', form=form,legend='New Post')

@app.route("/post/<int:post_id>", methods=['GET','POST'])
@login_required
def post(post_id):
    #post = Post.query.get(post_id)
    post = Post.query.get_or_404(post_id)   # get post id else return a 404 error i,e post not found error
    return render_template('post.html', title='post.title', post=post)

@app.route("/post/<int:post_id>/update", methods=['GET','POST'])
@login_required
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    # make sure only user who created the post can modify it
    if post.author != current_user:
        abort(403)  # create an exception. 403 meaning access forbidden
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()
        flash('Your post has been updated', 'success')
        return redirect(url_for('post',post_id=post.id))
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content
    return render_template('create_post.html', title='Update Post', form=form, legend='Update Post')

@app.route("/post/<int:post_id>/delete", methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    # make sure only user who created the post can modify it
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('Your post has been deleted', 'success')
    return redirect(url_for('home'))


@app.route("/user/<string:username>")
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