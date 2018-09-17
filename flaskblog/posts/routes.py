from flaskblog.models import Post
from flask_login import current_user, login_required
from flask import redirect, url_for, render_template, abort, flash, request, Blueprint
from flaskblog.posts.forms import PostForm
from flaskblog import db

posts = Blueprint('posts', __name__)

@posts.route("/post/new", methods=['GET','POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title=form.title.data, content=form.content.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Your post has been created','success')
        return redirect(url_for('main.home'))
    return render_template('create_post.html', title='New Post', form=form,legend='New Post')

@posts.route("/post/<int:post_id>", methods=['GET','POST'])
@login_required
def post(post_id):
    #post = Post.query.get(post_id)
    post = Post.query.get_or_404(post_id)   # get post id else return a 404 error i,e post not found error
    return render_template('post.html', title='post.title', post=post)

@posts.route("/post/<int:post_id>/update", methods=['GET','POST'])
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
        return redirect(url_for('posts.post',post_id=post.id))
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content
    return render_template('create_post.html', title='Update Post', form=form, legend='Update Post')

@posts.route("/post/<int:post_id>/delete", methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    # make sure only user who created the post can modify it
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('Your post has been deleted', 'success')
    return redirect(url_for('main.home'))
