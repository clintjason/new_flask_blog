from flask import Flask, render_template, url_for, flash, redirect
from forms import RegistrationForm, LoginForm
app = Flask(__name__)

app.config['SECRET_KEY'] = 'e2f6901qf5d4b6587c4ed6d8a'

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
    registration_form = RegistrationForm()
    if registration_form.validate_on_submit():
        flash('Account created for {}'.format(registration_form.username.data) + "!", 'success')
        return redirect(url_for("home"))
    return render_template('register.html', title='Register', form=registration_form)


@app.route("/login", methods=['GET','POST'])
def login():
    login_form = LoginForm()
    if login_form.validate_on_submit:
        if login_form.email.data == 'admin@blog.com' and login_form.password.data == 'admin':
               flash("You have been logged in!","success")
               return redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Username or Password Incorrect','danger')
    return render_template('login.html', title='Login', form=login_form)

if __name__ == '__main__':
    app.run(debug=True)

