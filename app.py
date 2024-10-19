from flask import Flask ,flash, jsonify, render_template , redirect , url_for , request, session
from flask_login import UserMixin, LoginManager, login_required,login_user,logout_user, current_user
from flask_session import Session
import sqlite3
import requests
from datetime import timedelta
from helpers import face_swap
from helper import lookup

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
    with get_db_connection() as c:
        user = c.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    if user:
        print(user)
        return User(id = user["id"] , username = user["username"] , password = user["password"])
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

        conn = get_db_connection()
        if not conn:
            return render_template("login.html", message = "dataase connection error")
        
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
        user =  c.fetchone() 
        conn.close()

        if user and user["password"] == password:
            login_user(User(id=user["id"] , username=user["username"] , password=user["password"]))
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

        conn = get_db_connection()
        if not conn:
            return render_template("register.html", message = "dataase connection error")
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

def get_db_connection():
    c = sqlite3.connect("users.db")
    c.row_factory = sqlite3.Row
    return c


@app.route('/')
def index():
    return render_template('index.html')

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

@app.route("/finance_buy", methods=["GET", "POST"])
@login_required
def finance_buy():
    if request.method == "POST":
        symbol = request.form.get("symbol")
        number = request.form.get("number")

        try:
            number = float(number)
        except ValueError:
            return render_template("finance_buy.html", message="Please enter a valid")

        if not symbol:
            return render_template("finance_buy.html", message="Please enter a symbol")
        
        stock = lookup(symbol)
        if stock is None:
            return render_template("finance_buy.html", message="Invalid symbol")
        
        stock_name = stock["name"]
        stock_price = float(stock["price"])

        conn = sqlite3.connect("users.db")
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("""
                  SELECT cash FROM users WHERE id = ? 
                  """, (current_user.id,))
        user_cash = c.fetchone()["cash"]

        total_price_of_stocks = stock_price * number

        if user_cash < total_price_of_stocks:
            return render_template("finance_buy.html", message="Not enough cash")
        
        c.execute("""
                     CREATE TABLE IF NOT EXISTS history (
                        id INTEGER NOT NULL,
                        username TEXT NOT NULL,
                        stock TEXT NOT NULL,
                        shares INTEGER NOT NULL,
                        price REAL NOT NULL
                        )
                    """)
        conn.commit()
        
        c.execute("""
                   INSERT INTO history (id , username, stock , shares , price) VALUES (? , ? , ? , ? , ?)
                  """, (current_user.id , current_user.username , stock_name , number , total_price_of_stocks))
        conn.commit()
        user_cash -= total_price_of_stocks
        c.execute("""UPDATE users SET cash = ? WHERE id = ?""", (user_cash, current_user.id))
        conn.commit()

        c.execute("""
                     CREATE TABLE IF NOT EXISTS stocks (
                        id INTEGER NOT NULL,
                        username TEXT NOT NULL,
                        stock TEXT NOT NULL,
                        shares INTEGER NOT NULL
                        )
                    """)
        conn.commit()

        c.execute(""" UPDATE stocks SET shares = shares + ? WHERE username = ? AND stock = ? """, (number, current_user.username, stock_name))
        
        if(c.rowcount == 0):
            c.execute(""" INSERT INTO stocks (id , username, stock , shares) VALUES (? , ? , ? , ?) """, (current_user.id , current_user.username , stock_name , number))
        conn.commit()    

        conn.close()
                     
        return render_template("finance_buy.html", message = "Stock bought successfully")
    return render_template("finance_buy.html")

@app.route("/finance_lookup", methods=["GET", "POST"])
@login_required
def finance_lookup():
    if request.method == "POST":
        symbol = request.form.get("symbol")
        stock = lookup(symbol)
        stock_name = stock["name"]
        stock_price = float(stock["price"])
        return render_template("finance_lookup.html",name = stock_name, price = stock_price)
    return render_template("finance_lookup.html")

@app.route("/finance_profile", methods=["GET", "POST"])
@login_required
def finance_profile():
    conn = sqlite3.connect("users.db")
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("""
                SELECT * FROM stocks WHERE id = ?
                """, (current_user.id,))
    stocks = c.fetchall()
    stocks = [dict(row) for row in stocks]

    c.execute("""
                SELECT cash FROM users WHERE id = ?
                """, (current_user.id,))
    user_cash = float(c.fetchone()["cash"])
    processed_stocks = []
    for stock in stocks:
        stock_name = stock["stock"]
        stock_price = float(lookup(stock_name)["price"])
        total = float(stock["shares"]) * stock_price
        processed_stocks.append({"stock": stock_name, "shares": stock["shares"], "price": stock_price , "total": total})
        

    conn.close()

    total = user_cash + sum([stock["total"] for stock in processed_stocks])
    return render_template("finance_profile.html",processed_stocks=processed_stocks, user_cash = user_cash, total = total)

@app.route("/finance_sell", methods=["GET", "POST"])
@login_required
def sell():
    conn = sqlite3.connect("users.db")
    conn.row_factory = sqlite3.Row
    db = conn.cursor()
    db.execute(
        "SELECT * FROM stocks WHERE id = ?", (current_user.id,)
    )
    stocks = db.fetchall()
    stocks = [dict(row) for row in stocks]
    print(stocks)

    if request.method == "POST":

        number = float(request.form.get("shares"))
        if not number or number < 0:
            return render_template("finance_sell.html", stocks = stocks, message="Invalid number")

        symbol = request.form.get("symbol")
        if not symbol:
            return render_template("finance_sell.html", stocks=stocks, message="Invalid symbol")

        share = lookup(symbol)
        symbol = share["name"]
        price = float(share["price"])
        current_numberofShares = 0
        if share is None:
            return render_template("finance_sell.html", stocks = stocks, message="Invalid symbol")
        for stock in stocks:
            if stock["stock"] == symbol:
                current_numberofShares = stock["shares"]
                if stock["shares"] < number:
                    return render_template("finance_sell.html", stocks = stocks, message="Not enough shares")
                
        total = number * price

        db.execute(
            "SELECT cash FROM users WHERE id = ?", (current_user.id,)
        )
        user_cash = db.fetchall()
        user_cash =[dict(row) for row in user_cash]
        user_cash = float(user_cash[0]["cash"])
        final_price = user_cash + total
        remaining_shares = current_numberofShares - number
        if remaining_shares < 0:
            return render_template("finance_sell.html", stocks = stocks, message="Not enough shares")
        new_total = remaining_shares * price

        db.execute(
            "UPDATE users SET cash = ? WHERE id = ?", (final_price, current_user.id)
        )
        db.execute(
            "INSERT INTO history (id , username , stock , shares, price) VALUES (? ,? ,? ,?,?)",
            (current_user.id,current_user.username,symbol,remaining_shares,new_total)
        )
        
        db.execute("""
                   UPDATE stocks SET shares = ? WHERE id = ? AND stock = ?
                   """,
                     (remaining_shares, current_user.id, symbol)
                     )
        conn.commit()
        conn.close()
        return render_template("finance_sell.html", stocks = stocks, message="Stock sold successfully")
    return render_template("finance_sell.html", stocks = stocks)

@app.route("/finance_history")
@login_required
def finance_history():
    conn = sqlite3.connect("users.db")
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("""
                SELECT * FROM history WHERE id = ?
                """, (current_user.id,))
    history = c.fetchall()
    conn.close()

    history = [dict(row) for row in history]
    return render_template("finance_history.html", history = history)

if __name__ == '__main__':
    app.run(debug=True)