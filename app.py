
from flask import Flask, render_template, request, url_for, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user
import json
 
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db.sqlite"
app.config["SECRET_KEY"] = "abc"
db = SQLAlchemy()
 
login_manager = LoginManager()
login_manager.init_app(app)

class set():
    def __init__(self, qs: list, ans: list, needsimp: list):
        self.questions = qs
        self.answers= ans
        self.needsimprovement = needsimp

class sets(): # SET NAMES CANNOT HAVE ANY SPACES, MAKE SURE TO REMOVE ALL SPACES BEFORE CREATING NEW SET
    def loadFromJSON(username: str):
        try:
            return json.loads(Users.query.filter_by(
                username=username).sets)
        except:
            return "error"

    def write(sets: dict, username: str):
        try:
            Users.query.filter_by(
                username=username).sets = json.loads(sets)
            db.session.commit()
            return "success"
        except:
            return "error"

class Users(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(250), unique=True, nullable=False)
    password = db.Column(db.String(250), nullable=False)
    sets = db.Column(db.Text(), default='{}')
 
 
db.init_app(app)
 
 
with app.app_context():
    db.create_all()
 
 
@login_manager.user_loader
def loader_user(user_id):
    return Users.query.get(user_id)
 
 
@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "POST":
        try: 
            user = Users(username=request.form.get("username"),
                        password=request.form.get("password"))
            db.session.add(user)
            db.session.commit()
            return redirect(url_for("login"))
        except:
            return render_template("error.html", msg="Sorry, there was an error. Please check that this account doesn't already exist")
    return render_template("sign_up.html")
 
 
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        try:
            user = Users.query.filter_by(
                username=request.form.get("username")).first()
            if user.password == request.form.get("password"):
                login_user(user)
                return redirect(url_for("home"))
        except:
            return render_template('error.html', msg="Sorry, there was an error. Please check that your password and/or username is correct.")
    return render_template("login.html")
 
 
@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("home"))
 
 
@app.route("/")
def home():
    return render_template("home.html", json=json)

@app.route("/error/<int:id>")
def error():
    if id == 1:
        msg = "Sorry, there was an error. Please check that this account doesn't already exist."
    elif id == 2:
        msg = "Sorry, there was an error. Please check that your password and/or username is correct."
    render_template('error.html', msg=msg)
    
@app.route("/new")
def newset():    
    return render_template("createset.html")
 
if __name__ == "__main__":
    app.run()
