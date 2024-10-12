from flask import Flask , render_template , request , url_for , redirect
import requests

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route("/pincode" , methods = ['GET' , 'POST'])
def pincode():
    if request.method == 'POST':
        address = request.form.get("address")

        pincode = requests.get(f"https://api.postalpincode.in/postoffice/{address}")
        if pincode.json()[0]["Status"] == "Error":
            pincode = pincode.json()
            return render_template('result.html', pincode = pincode)
        pincode = pincode.json()[0]["PostOffice"]
        return render_template('result.html' , pincode = pincode)
    return render_template('pincode.html')

@app.route("/dog")
def dog():
    request = requests.get("https://dog.ceo/api/breeds/image/random");
    print(request.json())
    return render_template('dog.html')
Flask.run(app)