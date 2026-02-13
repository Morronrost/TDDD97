from flask import Flask

app = Flask(__name__)

@app.route("/sign_in", methods=["GET", "POST"])
def sign_in():
    return "<p>Hello, World!</p>"