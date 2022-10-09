from crypt import methods
from enum import unique
from flask import Flask, render_template, url_for, redirect, request, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from os.path import dirname, join, realpath
import re

# from macpath import realpath

app = Flask (__name__)


# Konfigurime per Sesions
app.secret_key= "123flask_sqlalchemy2345"


# Konfigurime per Database
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///albums.db'
db = SQLAlchemy(app)


# Konfigurime per Brcrypt
bcrypt = Bcrypt(app)


# Konfigurime per Upload
UPLOAD_FOLDER = join(dirname(realpath(__file__)), 'static/photos')
ALLOWED_EXTENSIONS = ['png', 'jpg', 'jpeg', 'gif']
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

#Krijimi i modeleve
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password = password
    
    def __repr__(self):
        return "<User %s>" % self.email

class Album(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title =db.Column(db.String(50), unique=True, nullable=False)
    user_id = db.Column(db.Integer, nullable=False)
    
    def __init__(self, title, user_id):
        self.title = title
        self.user_id = user_id
        
    def __repr__(self):
        return "<Album %s>" % self.title

class Photo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title =db.Column(db.String(50), nullable=False)
    album_id = db.Column(db.Integer, nullable=False)
    
    def __init__(self, title, album_id):
        self.title = title
        self.album_id = album_id
        
    def __repr__(self):
        return "<Photo %s>" % self.title

@app.route ("/")
def home():
    return render_template("homepage.html")

@app.route ("/login", methods = ["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form['email']
        password = request.form['password']
        if not_empty([email, password ]):
            if is_email(email):
                user = User.query.filter_by(email=email).first()
                if user:
                    if bcrypt.check_password_hash(user.password, password):
                        session['is_logged_in'] = True
                        session['username'] = user.username
                        session['user_id'] = user.id                        
                        session['email'] = email
                        return redirect(url_for('dashboard'))
                    else:
                        flash("Password is incorrect")
                else:
                    flash("User doesn't exist!")
                               
            else:
                flash("Email is not valid!")
        else:
            flash("All fields are required")
        return redirect (url_for('login'))
    else:
        if session['is_logged_in'] == True:
            return redirect(url_for('dashboard'))
        return render_template("auth/login.html")

@app.route ("/register", methods = ["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        if not_empty([username, email, password, confirm_password]):
            if is_email(email):

                if password_match(password, confirm_password):
                    password_hash = bcrypt.generate_password_hash(password)
                    user = User(username, email, password_hash)
                    db.session.add(user)
                    db.session.commit()
                    # create session 3 items (we will need these in dashboard/albums/photos)
                    session['is_logged_in'] = True
                    session['username'] = username
                    session['email'] = email
                    return redirect(url_for('dashboard'))
                
                else:
                    flash("Password doesn't match!")
            else:
                flash("Email is not valid!")
        else:
            flash("All fields are required")
    else:
        if session['is_logged_in']==True:
            return redirect (url_for('dashboard'))
        return render_template("auth/register.html")

@app.route ("/dashboard")
def dashboard():
    if session['is_logged_in'] == False:
        return render_template("not_allowed.html")
    return render_template("admin/dashboard.html")

@app.route("/albums", methods = ["GET", "POST"])
def album():
    if session['is_logged_in'] == True:
        albums = Album.query.all()
        if request.method == "POST":
            title = request.form['title']
            album = Album(title, session.get('user_id'))
            db.session.add(album)
            db.session.commit()
            flash("Album was created successfully!")
            return redirect(url_for('album'))
        return render_template("admin/albums.html", albums=albums)
    else:
        return redirect(url_for("home"))

@app.route("/album/<int:album_id>/delete")
def delete_album(album_id):
    album=Album.query.get_or_404(album_id)
    db.session.delete(album)
    db.session.commit()
    flash("Album was deleted successfully!")
    return redirect (url_for('album'))



@app.route("/loggout", methods = ["GET", "POST"])
def loggout():
    session['username'] = ""
    session['email'] = ""
    session['is_logged_in'] = False
    return redirect(url_for('home'))

@app.route("/photos/<int:album_id>", methods = ["GET", "POST"])
def photos(album_id):
    if session['is_logged_in'] == True:
        album = Album.query.get_or_404(album_id)
        photos = Photo.query.filter_by(album_id=album.id).all()
        if request.method == "POST":
            # upload photos
            pass
        return render_template("admin/photos.html", photos=photos, album=album)
    else:
        return redirect(url_for("home"))

def not_empty(form_fields):
    for field in form_fields:
        if len(field) == 0:
            return False
        else:
            return True

def is_email(email): 
    return re.search("[\w\.\_\-]+\.[a-z]{2,5}",email) !=None

def password_match(password, confirm_password):
    return password == confirm_password

if __name__ == '__main__':
    app.run (debug=True)
