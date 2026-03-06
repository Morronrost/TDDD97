from flask import Flask, request, jsonify
from flask_sock import Sock
import json
import database_helper

app = Flask(__name__)

sock = Sock(app)

with app.app_context():
    database_helper.init_db()

active_sockets = {}

@sock.route("/ws/<token>")
def websocket_connection(ws, token):
    success, user = database_helper.get_user_data_by_token(token)

    if not success:
        ws.close()
        return

    active_sockets[user["email"]] = ws
    ws.receive()

    if active_sockets.get(user["email"]) == ws:
        del active_sockets[user["email"]]



@app.route("/")
def root():
    return app.send_static_file("client.html")

@app.route("/sign_up", methods=["POST"])
def sign_up():
    data = request.get_json()
    required = ["email", "password", "firstname", "familyname", "gender", "city", "country"]
    
    if not all(data.get(field) for field in required):
        return jsonify(message="Invalid data field.", data=None), 400
    
    if " " in data.get("email"):
        
        return jsonify(message="Invalid email.", data=None), 400
    elif data.get("email").count("@") != 1:
        return jsonify(message="Invalid email.", data=None), 400
    else: 
        local, domain = data.get("email").split("@")
        if not local:
            return jsonify(message="Invalid email.", data=None), 400
        if not domain:
            return jsonify(message="Invalid email.", data=None), 400
        if "." in local:
            return jsonify(message="Invalid email.", data=None), 400
        if not "." in domain:
            return jsonify(message="Invalid email.", data=None), 400
        if domain.startswith(".") or domain.endswith("."):
            return jsonify(message="Invalid email.", data=None), 400

    success = database_helper.sign_up(data.get("email"), data.get("password"), data.get("firstname"), data.get("familyname"), data.get("gender"), data.get("city"), data.get("country"))

    if not success:
        return jsonify(message="User already exists.", data=None), 409

    return jsonify(message="User created.", data=None), 201



@app.route("/sign_in", methods=["POST"])
def sign_in():
    data = request.get_json()

    if not data:
        return jsonify(message="Missing JSON body", data=None), 400

    success, token = database_helper.sign_in(data.get("username"), data.get("password"))

    if success:
        success_user, user = database_helper.get_user_data_by_token(token)
        email = user["email"]
        if email in active_sockets:
            try:
                active_sockets[email].send(
                    json.dumps({"type": "logout"})
                )
                active_sockets[email].close()
            except:
                pass

    if not success:
        return jsonify(message="Invalid username or password"), 401
    
    return jsonify(message="Successfully logged in", data=token), 200

@app.route("/sign_out", methods=["DELETE"])
def sign_out():
    token = request.headers.get("Authorization")

    if not database_helper.get_user_data_by_token(token)[0]:
        return jsonify(message="Incorrect token", data=None), 404 
    elif not token:
        return jsonify(message="Incorrect token", data=None), 401

    success = database_helper.sign_out(token)

    return jsonify(message="Successfully logged out", data=None), 200

@app.route("/change_password", methods=["PUT"])
def change_password():
    data = request.get_json()
    token = request.headers.get("Authorization")

    if not token:
        return jsonify(message="Incorrect token", data=None), 401
    if data.get("oldpassword") == None:
        return jsonify(message="Missing oldpassword", data=None), 400
    if data.get("newpassword") == None:
        return jsonify(message="Missing newpassword", data=None), 400



    success, error = database_helper.change_password(token, data.get("oldpassword"), data.get("newpassword"))

    if not success:
        if error == "token":
            return jsonify(message="Incorrect token", data=None), 404
        elif error == "password":
            return jsonify(message="Incorrect oldpassword", data=None), 400

    return jsonify(message="Password has been changed successfully", data=None), 201



@app.route("/get_user_data_by_token", methods=["GET"])
def get_user_data_by_token():
    token = request.headers.get("Authorization")

    if not token:
        return jsonify(message="Incorrect token", data=None), 401

    success, user = database_helper.get_user_data_by_token(token)
    
    
    if not success:
        return jsonify(message="Token not found", data=None), 404
    
    user = dict(user)
    return jsonify(message="Data retrieved", data=user), 200

@app.route("/get_user_data_by_email/<email>", methods=["GET"])
def get_user_data_by_email(email):
    token = request.headers.get("Authorization")

    if not database_helper.get_user_data_by_token(token)[0] or not token:
        return jsonify(message="Incorrect token", data=None), 401
        

    if not email:
        return jsonify(message="Incorrect email", data=None), 400

    success, user = database_helper.get_user_data_by_email(email)

    if not success or not user:
        return jsonify(message="Email not found", data=None), 404
    
    user = dict(user)
    print(user["email"])

    return jsonify(message="Data retrieved", data=user), 200

@app.route("/post_message", methods=["POST"])
def post_message():
    token = request.headers.get("Authorization")
    data = request.get_json()
    
    if not database_helper.get_user_data_by_token(token)[0] or not token:
        return jsonify(message="Incorrect token", data=None), 401

    if not database_helper.get_user_data_by_email(data["email"])[0] or not data["email"]:
        return jsonify(message="Email not found", data=None), 404
    
    if not data["message"]:
        return jsonify(message="No message", data=None), 400

    success = database_helper.post_message(token, data["message"], data["email"])

    if not success:
        return jsonify(message="Error occured", data=None), 500
    return jsonify(message="Message posted", data=None), 201

@app.route("/get_user_messages_by_email/<email>", methods=["GET"])
def get_user_messages_by_email(email):
    token = request.headers.get("Authorization")

    if not database_helper.get_user_data_by_token(token)[0] or not token:
        return jsonify(message="Incorrect token", data=None), 401

    success, messages = database_helper.get_user_messages_by_email(email)

    if not success:
        return jsonify(message="Email not found", data=None), 404

    if not messages:
        return jsonify(message="Messages not found", data=None), 404

    return jsonify(message="Messages retreived", data=messages), 200

@app.route("/get_user_messages_by_token", methods=["GET"])
def get_user_messages_by_token():
    token = request.headers.get("Authorization")

    if not token:
        return jsonify(message="Incorrect token", data=None), 401

    success, user = database_helper.get_user_data_by_token(token)

    if not success:
        return jsonify(message="Token not found", data=None), 404
    
    success, messages = database_helper.get_user_messages_by_email(user["email"])

    if not success:
        return jsonify(message="Email not found", data=None), 404

    if not messages:
        return jsonify(message="No messages retreived", data=None), 404

    return jsonify(message="Messages retreived", data=messages), 200




    

