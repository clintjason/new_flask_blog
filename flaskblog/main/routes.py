from flask import Blueprint, render_template, request
from flaskblog.models import Post

main = Blueprint('main', __name__)

@main.route("/home")
@main.route("/")
def home():
    # The page argument is optional and its default value is one
    #type int is to throw a value error if an int is not passed
    page = request.args.get('page', 1, type=int) 
    posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page,per_page=5)
    return render_template('home.html', posts=posts)

@main.route("/about")
def about():
    return render_template("about.html",title='About')