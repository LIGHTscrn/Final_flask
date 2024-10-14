from flask import Flask ,flash, render_template , redirect , url_for , request, session
from flask_session import Session
from flask_login import UserMixin, LoginManager, login_required,login_user,logout_user,current_user
import sqlite3
from cs50 import SQL
import requests


app = Flask(__name__)

app.secret_key = "wuwu"

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

# app.config["TEMPLATES_AUTO_RELOAD"] = True

# db_user = SQL("sqlite:///users.db")

# app.config["SESSION_PERMANENT"] = False
# app.config["SESSION_TYPE"] = "filesystem"
# Session(app)
@login_manager.user_loader
def load_user(user_id):
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    user = c.fetchone()
    conn.close()
    if user:
        return User(id = user[0] , user = user[1] , password = user[2])
    return render_template("login.html", message="Invalid username or password")
class User(UserMixin):
    def __init__(self, id , username , password):
        self.id = id
        self.username = username
        self.password = password

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        conn = sqlite3.connect("users.db")
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
        user = c.fetchone()
        conn.close()
        print(user,"this is user")

        if user and user[2] == password:
            login_user(User(id=user[0] , username=user[1] , password=user[2]))
            flash("Logged in")
            return redirect(url_for("index"))
        else:
            return render_template("login.html", message="Invalid username or password")
        
    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        conn = sqlite3.connect("users.db")
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username = ?", (username,))
        user = c.fetchone()

        if user:
            return render_template("register.html", message="Username already exists")
        else:
            c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            conn.commit()
            return render_template("login.html", message="Registration Successful")
        conn.close()
    return render_template("register.html")



@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logged out")
    return redirect(url_for("index"))

@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route('/')
def index():
    image_link = "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTBxy4oqcKwCuv8h1xZlIdBFgbfKdQeseq9AQ&s"
    return render_template('index.html', image_link=image_link)

@app.route("/animal")
def animal():
    cat_response = requests.get("https://api.thecatapi.com/v1/images/search")
    cat_url = cat_response.json()[0]['url']
    dog_response = requests.get("https://api.thedogapi.com/v1/images/search")
    dog_url = dog_response.json()[0]['url']
    return render_template('animal.html', dog_url=dog_url, cat_url=cat_url)

if __name__ == '__main__':
    app.run(debug=True)