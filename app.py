'''
app.py contains all of the server application
this is where you'll find all of the get/post request handlers
the socket event handlers are inside of socket_routes.py
'''

from flask import Flask, render_template, request, abort, url_for, session
from flask_socketio import SocketIO
import db
import secrets
import ssl
from datetime import timedelta

# import logging

# this turns off Flask Logging, uncomment this to turn off Logging
# log = logging.getLogger('werkzeug')
# log.setLevel(logging.ERROR)

app = Flask(__name__)

# SSL certificate and key files 
CERT_PATH = "./certs/localhost+2.pem" 
KEY_PATH = "./certs/localhost+2-key.pem"
context = ssl.SSLContext()
context.load_cert_chain(CERT_PATH, KEY_PATH)

# secret key used to sign the session cookie
app.config['SECRET_KEY'] = secrets.token_hex()
socketio = SocketIO(app)

# session timeout
@app.before_request
def before_request():
    session.permanent = True
    # Change to shorter minutes value to test
    app.permanent_session_lifetime = timedelta(minutes=10)

# don't remove this!!
import socket_routes

# index page
@app.route("/")
def index():
    # remove session data if exists
    if "username" in session:
        # clear session data
        session.pop("username", default=None)

    return render_template("index.jinja")

# login page
@app.route("/login")
def login():
    # remove session data if exists
    if "username" in session:
        # clear session data
        session.pop("username", default=None)

    return render_template("login.jinja")

# handles a post request when the user clicks the log in button
@app.route("/login/user", methods=["POST"])
def login_user():
    if not request.is_json:
        abort(404)
    
    # remove session data if exists
    if "username" in session:
        # clear session data
        session.pop("username", default=None)

    username = request.json.get("username")
    password = request.json.get("password")

    user =  db.get_user(username)
    if user is None:
        return "Error: User does not exist!"
    
    # calculate password hash and compare
    in_password = db.hash_password(password, user.salt)

    if user.password != in_password:
        return "Error: Password does not match!"
    
    # save to session object
    session["username"] = username

    return url_for('home')

# handles a get request to the signup page
@app.route("/signup")
def signup():
    # remove session data if exists
    if "username" in session:
        # clear session data
        session.pop("username", default=None)

    return render_template("signup.jinja")

# handles a post request when the user clicks the signup button
@app.route("/signup/user", methods=["POST"])
def signup_user():
    if not request.is_json:
        abort(404)
    
    # remove session data if exists
    if "username" in session:
        # clear session data
        session.pop("username", default=None)
    
    username = request.json.get("username")
    password = request.json.get("password")

    if db.get_user(username) is None:
        db.insert_user(username, password)
        # save to session object
        session["username"] = username
        return url_for('home')
    
    return "Error: User already exists!"

# handler when a "404" error happens
@app.errorhandler(404)
def page_not_found(_):
    return render_template('404.jinja'), 404

# home page, where the messaging app is
@app.route("/home")
def home():
    if "username" in session:
        username = session["username"]
        if username is None:
            abort(404)
        friList = db.get_allfri(username)
        frirequestList = db.get_allrev(username)

        friList = friList if friList is not None else ['hi']
        return render_template("home.jinja", all_fris=friList, friend_requests=frirequestList)
    else:
        return render_template("login.jinja")

# handles when the user clicks the log out button
@app.route("/logout")
def logout():
    # clear session data
    session.pop("username", default=None)
    return render_template("logout.jinja")


if __name__ == '__main__':
    # socketio.run(app,debug=True)
    socketio.run(app, ssl_context=context,debug=True)
