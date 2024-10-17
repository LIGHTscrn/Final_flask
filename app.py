from flask import Flask ,flash, jsonify, render_template , redirect , url_for , request, session
from flask_login import UserMixin, LoginManager, login_required,login_user,logout_user, current_user
from flask_session import Session
import sqlite3
import requests
from datetime import timedelta
import speech_recognition as sr
from faceswap import face_swap

app = Flask(__name__)

app.secret_key = "wuwu"

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config["SESSION_PERMANENT"] = False
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(hours=1)
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

@login_manager.user_loader
def load_user(user_id):
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    user = c.fetchone()
    conn.close()
    if user:
        return User(id = user[0] , username = user[1] , password = user[2])
    return None
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

            session.permanent = False

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
            conn.close()  # Don't forget to close the connection in this case
            return render_template("register.html", message="Username already exists")
        else:
            # Insert new user into the database
            c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            conn.commit()
            conn.close()

            # Flash a success message and redirect to login page
            flash("Registration successful! Please log in.")
            return redirect(url_for("login"))  # Redirect to the login page

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
@login_required
def animal():
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("""
              CREATE TABLE IF NOT EXISTS animal_counts (
              id INTEGER PRIMARY KEY,
              cat INTEGER DEFAULT 0,
              dog INTEGER DEFAULT 0, 
              FOREIGN KEY (id) REFERENCES users(id)
              )
                """)
    cat_counts = c.execute("SELECT cat FROM animal_counts WHERE id = ?", (current_user.id,)).fetchone()
    dog_counts = c.execute("SELECT dog FROM animal_counts WHERE id = ?", (current_user.id,)).fetchone()
    conn.close()
    cat_counts = cat_counts[0] if cat_counts is not None else 0
    dog_counts = dog_counts[0] if dog_counts is not None else 0
    person_type = "You are a person"
    if cat_counts > dog_counts:
        difference = cat_counts - dog_counts

        if difference >= 1 and difference <= 3:
            person_type = "You like cats"

        elif difference >=4 and difference <= 6:
            person_type = "You really like cats"

        elif difference > 6:
            person_type = "You love cats"

    elif cat_counts < dog_counts:
        difference = dog_counts - cat_counts

        if difference >= 1 and difference <= 3:
            person_type = "You like dogs"

        elif difference >=4 and difference <= 6:
            person_type = "You really like dogs"

        elif difference > 6:
            person_type = "You love dogs"

    cat_response = requests.get("https://api.thecatapi.com/v1/images/search")
    cat_url = cat_response.json()[0]['url']
    dog_response = requests.get("https://api.thedogapi.com/v1/images/search")
    dog_url = dog_response.json()[0]['url']
    return render_template('animal.html', dog_url=dog_url, cat_url=cat_url, person_type=person_type)

@app.route("/cat_button", methods=["POST"])
def cat_button():
    if not current_user.is_authenticated:
        return redirect(url_for("login"))

    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("""
       INSERT INTO animal_counts (id, cat) VALUES (? , 1) 
       ON CONFLICT(id) DO UPDATE SET cat = cat + 1
       """, (current_user.id,))
    conn.commit()
    conn.close()
 
    flash("You clicked the cat button")
    return redirect(url_for("animal"))       
        

@app.route("/dog_button", methods=["POST"])
def dog_button():
    if not current_user.is_authenticated:
        return redirect(url_for("login"))
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("""
       INSERT INTO animal_counts (id, dog) VALUES (? , 1) 
       ON CONFLICT(id) DO UPDATE SET dog = dog + 1
       """, (current_user.id,))
    conn.commit()
    conn.close()
 
    flash("You clicked the cat button")
    return redirect(url_for("animal")) 

@app.route("/faceswap", methods=["GET","POST"])
@login_required
def faceswap():

    swapped_image_path = None

    if request.method == "POST":
        image1 = request.files["image1"]
        image2 = request.files["image2"]

        image1_path = f"static/images/temp_{current_user.id}_1.jpeg"
        image2_path = f"static/images/temp_{current_user.id}_2.jpeg"
        image1.save(image1_path)
        image2.save(image2_path)

        swapped_image = face_swap(image1_path, image2_path)
        if swapped_image == None:
            text = "No face detected in one of the images"
            return render_template("faceswap.html", text=text)
        swapped_image_path = f"static/images/swapped_{current_user.id}.jpeg"
        swapped_image.save(swapped_image_path)

        return render_template("faceswap.html", swapped_image =swapped_image_path)
    return render_template("faceswap.html", swapped_image =swapped_image_path)
    
def voice_search():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        audio = recognizer.listen(source)
        try:
            query = recognizer.recognize_google(audio)
            return query
        except sr.UnknownValueError:
            return "Sorry, I did not get that"
        except sr.RequestError:
            return "Could not request results from Google Speech Recognition service."

@app.route("/voice_search")
def voice_search_route():
    query = voice_search()
    return jsonify(result=query)

if __name__ == '__main__':
    app.run(debug=False)