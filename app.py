
from flask import Flask, render_template, request, url_for, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user
import json
import random

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db.sqlite"
app.config["SECRET_KEY"] = "abc"
db = SQLAlchemy()
 
login_manager = LoginManager()
login_manager.init_app(app)

class Users(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(250), unique=True, nullable=False)
    password = db.Column(db.String(250), nullable=False)
    sets = db.Column(db.Text(), default='[]')
 
class Sets(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250))
    belongsTo = db.Column(db.Integer)
    set = db.Column(db.Text(), default={})
    public = db.Column(db.Boolean(), default=True)

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
    if current_user.is_authenticated:
        return render_template("home.html", json=json, Sets=Sets)
    else:
        return redirect(url_for("login"));

@app.route("/error/<int:id>")
def error():
    if id == 1:
        msg = "Sorry, there was an error. Please check that this account doesn't already exist."
    elif id == 2:
        msg = "Sorry, there was an error. Please check that your password and/or username is correct."
    render_template('error.html', msg=msg)
    
@app.route("/new", methods=["GET", "POST"])
def newset():
    if current_user.is_authenticated:
        if request.method =="GET":
            return render_template("createset.html")
        elif request.method == "POST":
            i = 0
            qna = []
            

            while True:
                i = i + 1;
                if request.form.get(f"q{i}") == None or request.form.get(f"a{i}") == None:
                    break;
                qna.append([request.form.get(f"q{i}"), request.form.get(f"a{i}"), 0]) # last #: 0: not learned/wrong, 1: learning, 2: learned
            newset = Sets(name=request.form.get("title"), belongsTo=current_user.id, set=json.dumps(qna), public=True)
            db.session.add(newset)
            db.session.commit()

            userSets = json.loads(current_user.sets)
            userSets.append(newset.id)
            current_user.sets = json.dumps(userSets)

            db.session.commit()

            return redirect(url_for("set", id=newset.id))
    else: 
        return redirect(url_for("login"))

def getQuestionToStudy(set:Sets): # WORK ON ALGORITHM LATER TO PRIORITZE 0 OVER 1 AND TO INCLUDE 2 IF NO OTHER
    while True:
        question = random.choice(json.loads(set.set))
        if question[2] == 0 or question[2] == 1: 
            return question;
    


@app.route("/sets/<int:id>")
def set(id):
    if not current_user.is_authenticated:
        return redirect(url_for("login"))

    try:
        set = Sets.query.get(id)
        return render_template("set.html", set=set)
    except:
        return redirect(url_for("error", msg="Sorry, there was an error. This set cannot be found."))

@app.route("/sets/<int:id>/write")
def write(id):

    if not current_user.is_authenticated:
        return redirect(url_for("login"))

    
    try:
        set = Sets.query.get(id)
        
        if request.method == "GET":
            q = getQuestionToStudy(set)
            return render_template("write.html", question=q, set=set);
        elif request.method == "POST":
            pass
    except:
        return redirect(url_for("error", msg="Sorry, there was an error in retrieving the set. Check that this set actually exists and there is content inside of it."))
       

if __name__ == "__main__":
    app.run()