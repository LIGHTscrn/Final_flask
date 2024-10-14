from flask import Flask , render_template , redirect , url_for , request
import requests

app = Flask(__name__)

@app.route('/')
def index():
    image_link = "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTBxy4oqcKwCuv8h1xZlIdBFgbfKdQeseq9AQ&s"
    return render_template('index.html', image_link=image_link)

@app.route("/dog")

if __name__ == '__main__':
    app.run(debug=True)