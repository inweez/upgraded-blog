from flask import Flask, render_template, request
import requests
import smtplib
from wtforms import StringField, SubmitField
from flask_wtf import FlaskForm
from wtforms.validators import DataRequired, URL
# from flask_ckeditor import CKEditor, CKEditorField
from flask_bootstrap import Bootstrap
from datetime import date
from flask_sqlalchemy import SQLAlchemy
import os

your_email = os.environ.get('YOUR_EMAIL')
my_email = os.environ.get('MY_EMAIL')
password = os.environ.get('MY_EMAIL_PASSWORD')
#secret_key = os.environ.get('BLOG_SECRET_KEY')
post = requests.get(url='https://api.npoint.io/721413adb75035cec088').json()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('BLOG_SECRET_KEY')
db = SQLAlchemy(app)
Bootstrap(app)


class BlogPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True, nullable=False)
    subtitle = db.Column(db.String(250), nullable=False)
    date = db.Column(db.String(250), nullable=False)
    body = db.Column(db.Text, nullable=False)
    author = db.Column(db.String(250), nullable=False)
    img_url = db.Column(db.String(250), nullable=False)


class CreatePostForm(FlaskForm):
    title = StringField("Blog Post Title", validators=[DataRequired()])
    subtitle = StringField("Subtitle", validators=[DataRequired()])
    author = StringField("Your Name", validators=[DataRequired()])
    img_url = StringField("Blog Image URL", validators=[DataRequired(), URL()])
    body = StringField("Blog Content", validators=[DataRequired()])
    #submit = SubmitField("Submit Post")


@app.route('/')
def get_all_posts():
    return render_template("index.html", post=post)

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/post/<int:index>")
def show_post(index):
    requested_post = None
    for blog in post:
        if blog['id'] == index:
            requested_post = blog
    return render_template("post.html", post=requested_post)


@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        data = request.form
        send_email(data['name'], data['email'], data['phone'], data['message'])
        return render_template("contact.html", msg_sent=True)
    return render_template("contact.html", msg_sent=False)


def send_email(name, email, phone, message):
    email_msg = f'Subject:New Message\n\nName: {name}\nEmail: {email}\nPhone: {phone} \nMessage: {message}'
    with smtplib.SMTP("smtp.gmail.com") as connection:
        connection.starttls()
        connection.login(user=my_email, password=password)
        connection.sendmail(from_addr=my_email, to_addrs=your_email, msg=email_msg)


@app.route("/new-post", methods=['GET', 'POST'])
def new_post():
    form = CreatePostForm()
    if form.validate_on_submit():
        new_post = BlogPost(
            title=form.title.data,
            subtitle=form.subtitle.data,
            body=form.body.data,
            img_url=form.img_url.data,
            author=form.author.data,
            date=date.today().strftime("%B %d, %Y")
        )
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for("get_all_posts"))
    return render_template("make-post.html", form=form)

@app.route("/delete/<int:index>")
def delete_post(index):
    # post_to_delete = BlogPost.query.get(index)
    requested_post = None
    for blog in post:
        if blog['id'] == index:
            requested_post = blog

    db.session.delete(requested_post)
    db.session.commit()
    return redirect(url_for('get_all_posts'))


# @app.route("/edit-post/<int:index>", methods=["GET", "POST"])
# def edit_post(index):
#     post = BlogPost.query.get(index)
#     edit_form = CreatePostForm(
#         title=post.title,
#         subtitle=post.subtitle,
#         img_url=post.img_url,
#         author=post.author,
#         body=post.body
#     )
#     return render_template("make-post.html", form=edit_form, is_edit=True)


if __name__ == '__main__':
    app.run(debug=True)
