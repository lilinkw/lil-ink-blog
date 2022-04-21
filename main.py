import flask
from flask import Flask, render_template, redirect, url_for, flash
from flask_bootstrap import Bootstrap
from flask_ckeditor import CKEditor
from datetime import date
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from forms import CreatePostForm, RegisterForm, LoginForm, CommentForm
from flask_gravatar import Gravatar
from functools import wraps
import os


app = Flask(__name__)
# get secret key from .env on Heroku
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
ckeditor = CKEditor(app)
Bootstrap(app)

# CONNECT TO DB
# os.environ.get('DATABASE_URL') to connect to DB on heroku else use sqlite instead
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///blog.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Connect to Gravata
gravatar = Gravatar(app,
                    size=100,
                    rating='g',
                    default='retro',
                    force_default=False,
                    force_lower=False,
                    use_ssl=False,
                    base_url=None)

# Configure flask_login
login_manager = LoginManager()
login_manager.init_app(app)


# Must have
@login_manager.user_loader
def load_user(user_id):
    user = User.query.filter_by(id=user_id).first()
    if user:
        return user
    return None


# CONFIGURE TABLES

# users_table
class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(100))

    # This will act like a List of BlogPost objects attached to each User.
    # The "author" refers to the author property in the BlogPost class.
    posts = relationship("BlogPost", back_populates="author")
    # The 'author' refers to author property in Comment class
    comments = relationship("Comment", back_populates='author')

    def __init__(self, email, name, password):
        self.email = email
        self.name = name
        self.password = password


# blog_posts table
class BlogPost(db.Model):
    __tablename__ = "blog_posts"
    id = db.Column(db.Integer, primary_key=True)

    # Create Foreign Key, "users.id" the users refers to the table name of User.
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    # Create reference to the User object, the "posts" refers to the posts protperty in the User class.
    author = relationship("User", back_populates="posts")
    # The 'parent_post' refers to post property in Comment class
    comments = relationship("Comment", back_populates='parent_post')

    title = db.Column(db.String(250), unique=True, nullable=False)
    subtitle = db.Column(db.String(250), nullable=False)
    date = db.Column(db.String(250), nullable=False)
    body = db.Column(db.Text, nullable=False)
    img_url = db.Column(db.String(250), nullable=False)


# comments table
class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(250), nullable=False)

    # Create Foreign Key, "users.id" the users refers to the table name of User.
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    # Create reference to the User object, the "posts" refers to the posts protperty in the User class.
    author = relationship("User", back_populates="comments")

    # Link to comments in BlogPost
    post_id = db.Column(db.Integer, db.ForeignKey("blog_posts.id"))
    parent_post = relationship('BlogPost', back_populates='comments')

    def __init__(self, text, author_id, post_id):
        self.text = text
        self.author_id = author_id
        self.post_id = post_id


# Create database
db.create_all()


@app.route('/')
def get_all_posts():
    posts = BlogPost.query.all()
    return render_template("index.html", all_posts=posts)


# Register new user
@app.route('/register', methods=['GET', 'POST'])
def register():
    # Create a new form
    register_form = RegisterForm()
    # If Submit valid
    if register_form.validate_on_submit():
        # Get data from the form
        email = register_form.email.data

        # Query user from the DB
        # Check if Email already existed
        if User.query.filter_by(email=email).first():
            flash('This email has already been registered, try another')
            # Redirect to register
            return redirect(url_for('register'))

        # Create a new user
        new_user = User(
            email=email,
            name=register_form.name.data,
            # Hash password by werkzeug module
            # Default method= "pbkdf2:sha256"
            password=generate_password_hash(
                password=register_form.password.data,
                salt_length=8,
            )
        )
        # add new_user to the database
        db.session.add(new_user)
        db.session.commit()

        # Log in user
        login_user(user=new_user)
        # Return to home route
        return redirect(url_for('get_all_posts'))
    return render_template("register.html", form=register_form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    # Create a new login form
    login_form = LoginForm()

    if login_form.validate_on_submit():
        # Get data form the form
        email = login_form.email.data

        # Query user with the inputted email
        # Check if email is existed
        user = User.query.filter_by(email=email).first()
        if user is None:
            flash('This email does not existed, please try another')
            # Redirect to log in
            return redirect(url_for('login'))
        # Check if the pass word is correct
        if check_password_hash(pwhash=user.password, password=login_form.password.data):
            # Log in if correct
            login_user(user=user)
            flash('Logged in successfully')
            # Redirect to home route
            return redirect(url_for('get_all_posts'))
        else:
            flash('Password is Incorrect, try again')
            # Redirect to log in route
            return redirect(url_for('login'))
    return render_template("login.html", form=login_form)


# Decorator for admin only action
def admin_only(func):
    @wraps(func)
    def wrapper_func(*args, **kwargs):
        if current_user is None or current_user.id != 1:
            return flask.abort(403)
        return func(*args, **kwargs)
    return wrapper_func


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('get_all_posts'))


@app.route("/post/<int:post_id>", methods=['GET', 'POST'])
def show_post(post_id):
    requested_post = BlogPost.query.get(post_id)
    # Create a comment form
    comment_form = CommentForm()
    if comment_form.validate_on_submit():
        if not current_user.is_authenticated:
            flash("You need to login or register to comment.")
            return redirect(url_for("login"))

        # Create a new comment
        new_comment = Comment(
            text=comment_form.comment.data,
            author_id=current_user.id,
            post_id=requested_post.id,
        )
        # Add to DB
        db.session.add(new_comment)
        db.session.commit()
        # Redirect to show_post
        return redirect(url_for('show_post', post_id=post_id))
    return render_template("post.html", post=requested_post, form=comment_form)


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")


@app.route("/new-post", methods=['GET', 'POST'])
@admin_only
def add_new_post():
    form = CreatePostForm()
    if form.validate_on_submit():
        new_post = BlogPost(
            title=form.title.data,
            subtitle=form.subtitle.data,
            body=form.body.data,
            img_url=form.img_url.data,
            author=current_user,
            date=date.today().strftime("%B %d, %Y")
        )
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for("get_all_posts"))
    return render_template("make-post.html", form=form)


@app.route("/edit-post/<int:post_id>")
@admin_only
def edit_post(post_id):
    post = BlogPost.query.get(post_id)
    edit_form = CreatePostForm(
        title=post.title,
        subtitle=post.subtitle,
        img_url=post.img_url,
        author=post.author,
        body=post.body
    )
    if edit_form.validate_on_submit():
        post.title = edit_form.title.data
        post.subtitle = edit_form.subtitle.data
        post.img_url = edit_form.img_url.data
        post.author = edit_form.author.data
        post.body = edit_form.body.data
        db.session.commit()
        return redirect(url_for("show_post", post_id=post.id))

    return render_template("make-post.html", form=edit_form)


@app.route("/delete/<int:post_id>")
@admin_only
def delete_post(post_id):
    post_to_delete = BlogPost.query.get(post_id)
    db.session.delete(post_to_delete)
    db.session.commit()
    return redirect(url_for('get_all_posts'))


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
