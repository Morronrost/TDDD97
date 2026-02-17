from flask import Flask, request
import database_helper

app = Flask(__name__)

with app.app_context():
    database_helper.init_db()

@app.route("/sign_up", methods=["POST"])
def sign_up():
    data = request.get_json()
    required = ["email", "password", "firstname", "familyname", "gender", "city", "country"]
    
    if not all(data.get(field) for field in required):
        return jsonify(success=False, message="Invalid data field.", data=None), 400

    success = database_helper.sign_up(data.get("email"), data.get("password"), data.get("firstname"), data.get("familyname"), data.get("gender"), data.get("city"), data.get("country"))

    if not success:
        return jsonify(success=False, message="User already exists.", data=None), 400

    return jsonify(success=True, message="User created.", data=None), 201



@app.route("/sign_in", methods=["POST"])
def sign_in():
    data = request.get_json()

    if not data:
        return jsonify(success=False, message="Missing JSON body", data=None)

    success, token = database_helper.sign_in(data.get("email"), data.get("password"))

    if not success:
        return jsonify(success=False, message="Invalid username or password"), 400
    
    return jsonify(success=True, message="Successfully logged in", data=token), 200