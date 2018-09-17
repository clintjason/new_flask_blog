import os
from flask import url_for, current_app
import secrets
from PIL import Image
from flaskblog import mail
from flask_mail import Message


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)  # returns f_name and f_ext
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(current_app.root_path, 'static/profile_pics',picture_fn)
    # resize image before saving
    output_size = (125,125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)   # resize image
    i.save(picture_path)   #save resized image

    return picture_fn


def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request', sender='noreply@demo.com', recipients=[user.email])
    # the _external = True argument defines the absolute link for the token rather than relative
    msg.body = f'''To reset your password, visit the following link:
{url_for('users.reset_token', token=token, _external=True)}

If you did not make this request then, simply ignore this email and no changes will be made.
'''
    mail.send(msg)
