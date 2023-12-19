from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, URL
from flask_ckeditor import CKEditor, CKEditorField
import datetime

CKEDITOR_SERVE_LOCAL = True

db = SQLAlchemy()
app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
ckeditor = CKEditor(app)
Bootstrap(app)

# CONNECT TO DB
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///posts.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)


# CONFIGURE TABLE
class BlogPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True, nullable=False)
    subtitle = db.Column(db.String(250), nullable=False)
    date = db.Column(db.String(250), nullable=False)
    body = db.Column(db.Text, nullable=False)
    author = db.Column(db.String(250), nullable=False)
    img_url = db.Column(db.String(250), nullable=False)


# WTForm
class CreatePostForm(FlaskForm):
    title = StringField("Blog Post Title", validators=[DataRequired()])
    subtitle = StringField("Subtitle", validators=[DataRequired()])
    author = StringField("Your Name", validators=[DataRequired()])
    img_url = StringField("Blog Image URL", validators=[DataRequired(), URL()])
    body = CKEditorField('Body')
    submit = SubmitField("Submit Post")


@app.route('/')
def get_all_posts():
    posts = db.session.execute(db.select(BlogPost)).scalars()
    return render_template("index.html", all_posts=posts)


@app.route('/delete/<int:post_id>')
def delete_post(post_id):
    post = db.get_or_404(BlogPost, post_id)

    db.session.delete(post)
    db.session.commit()
    return redirect(url_for('get_all_posts'))


@app.route('/new-post', methods=['GET', 'POST'])
def add_post():
    today = datetime.date.today().strftime('%B %d, %Y')
    form = CreatePostForm()
    h1 = 'New Post'
    if request.method == 'POST':
        if form.validate_on_submit():
            post = BlogPost(
                title=form.title.data,
                subtitle=form.subtitle.data,
                date=today,
                body=form.body.data,
                author=form.author.data,
                img_url=form.img_url.data
            )
            db.session.add(post)
            db.session.commit()
            return redirect(url_for('get_all_posts'))
    return render_template('make-post.html', form=form, h1=h1)


@app.route("/post/<int:index>")
def show_post(index):
    post = db.get_or_404(BlogPost, index)
    return render_template("post.html", post=post)


@app.route('/edit-post/<int:post_id>', methods=['GET', 'POST'])
def edit_post(post_id):
    post = db.get_or_404(BlogPost, post_id)
    form = CreatePostForm(
        body=post.body,
        author=post.author,
        title=post.title,
        img_url=post.img_url,
        subtitle=post.subtitle
    )
    h1 = 'Edit Post'
    if request.method == 'POST':
        if form.validate_on_submit():
            post.title = form.title.data
            post.body = form.body.data
            post.author = form.author.data
            post.img_url = form.img_url.data
            post.subtitle = form.subtitle.data
            db.session.add(post)
            db.session.commit()
            return redirect(url_for('show_post', index=post_id))
    return render_template('make-post.html', form=form, h1=h1)


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")


with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
