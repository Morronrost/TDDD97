from flask import Flask, request, jsonify
import database_helper

app = Flask(__name__)

with app.app_context():
    database_helper.init_db()

@app.route("/")
def root():
    return app.send_static_file("client.html")

@app.route("/sign_up", methods=["POST"])
def sign_up():
    data = request.get_json()
    required = ["email", "password", "firstname", "familyname", "gender", "city", "country"]
    
    if not all(data.get(field) for field in required):
        return jsonify(success=False, message="Invalid data field.", data=None), 200
    
    if " " in data.get("email"):
        
        return jsonify(success=False, message="Invalid email.", data=None), 200
    elif data.get("email").count("@") != 1:
        return jsonify(success=False, message="Invalid email.", data=None), 200
    else: 
        local, domain = data.get("email").split("@")
        if not local:
            return jsonify(success=False, message="Invalid email.", data=None), 200
        if not domain:
            return jsonify(success=False, message="Invalid email.", data=None), 200
        if "." in local:
            return jsonify(success=False, message="Invalid email.", data=None), 200
        if not "." in domain:
            return jsonify(success=False, message="Invalid email.", data=None), 200
        if domain.startswith(".") or domain.endswith("."):
            return jsonify(success=False, message="Invalid email.", data=None), 200

    success = database_helper.sign_up(data.get("email"), data.get("password"), data.get("firstname"), data.get("familyname"), data.get("gender"), data.get("city"), data.get("country"))

    if not success:
        return jsonify(success=False, message="User already exists.", data=None), 200

    return jsonify(success=True, message="User created.", data=None), 200



@app.route("/sign_in", methods=["POST"])
def sign_in():
    data = request.get_json()

    if not data:
        return jsonify(success=False, message="Missing JSON body", data=None)

    success, token = database_helper.sign_in(data.get("username"), data.get("password"))

    if not success:
        return jsonify(success=False, message="Invalid username or password"), 200
    
    return jsonify(success=True, message="Successfully logged in", data=token), 200

@app.route("/sign_out", methods=["DELETE"])
def sign_out():
    token = request.headers.get("Authorization")

    if not database_helper.get_user_data_by_token(token)[0] or not token:
        return jsonify(success=False, message="Incorrect token", data=None), 200 

    success = database_helper.sign_out(token)

    return jsonify(success=True, message="Successfully logged out", data=None), 200

@app.route("/change_password", methods=["PUT"])
def change_password():
    data = request.get_json()
    token = request.headers.get("Authorization")

    if not token:
        return jsonify(success=False, message="Incorrect token", data=None), 200
    if data.get("oldpassword") == None:
        return jsonify(success=False, message="Incorrect oldpassword", data=None), 200
    if data.get("newpassword") == None:
        return jsonify(success=False, message="Invalid newpassword", data=None), 200



    success, error = database_helper.change_password(token, data.get("oldpassword"), data.get("newpassword"))

    if not success:
        if error == "token":
            return jsonify(success=False, message="Incorrect token", data=None), 200
        elif error == "password":
            return jsonify(success=False, message="Incorrect oldpassword", data=None), 200

    return jsonify(success=True, message="Password has been changed successfully", data=None), 200



@app.route("/get_user_data_by_token", methods=["GET"])
def get_user_data_by_token():
    token = request.headers.get("Authorization")

    if not token:
        return jsonify(success=False, message="Incorrect token", data=None), 200

    success, user = database_helper.get_user_data_by_token(token)
    
    
    if not success:
        return jsonify(success=False, message="Incorrect token", data=None), 200
    
    user = dict(user)
    return jsonify(success=True, message="Data retrieved", data=user), 200

@app.route("/get_user_data_by_email/<email>", methods=["GET"])
def get_user_data_by_email(email):
    token = request.headers.get("Authorization")

    if not database_helper.get_user_data_by_token(token)[0] or not token:
        return jsonify(success=False, message="Incorrect token", data=None), 200
        

    if not email:
        return jsonify(success=False, message="email not found", data=None), 200

    success, user = database_helper.get_user_data_by_email(token, email)

    if not success or not user:
        return jsonify(success=False, message="Incorrect email or token", data=None), 200
    
    user = dict(user)
    print(user["email"])

    return jsonify(success=True, message="Data retrieved", data=user), 200

@app.route("/post_message", methods=["POST"])
def post_message():
    token = request.headers.get("Authorization")
    data = request.get_json()
    
    if not database_helper.get_user_data_by_token(token)[0] or not token:
        return jsonify(success=False, message="Incorrect token", data=None), 200

    if not database_helper.get_user_data_by_email(token, data["email"])[0] or not data["email"]:
        return jsonify(success=False, message="Email not found", data=None), 200
    
    if not data["message"]:
        return jsonify(success=False, message="No message", data=None), 200

    success = database_helper.post_message(token, data["message"], data["email"])

    if not success:
        return jsonify(success=False, message="Error occured", data=None), 200
    return jsonify(success=True, message="Message posted", data=None), 200

@app.route("/get_user_messages_by_email/<email>", methods=["GET"])
def get_user_messages_by_email(email):
    token = request.headers.get("Authorization")

    if not database_helper.get_user_data_by_token(token)[0] or not token:
        return jsonify(success=False, message="Incorrect token", data=None), 200

    success, messages = database_helper.get_user_messages_by_email(email)

    if not success:
        return jsonify(success=False, message="Incorrect email", data=None), 200

    if not messages:
        return jsonify(success=False, message="No messages retreived", data=None), 200

    return jsonify(success=True, message="Messages retreived", data=messages), 200

@app.route("/get_user_messages_by_token", methods=["GET"])
def get_user_messages_by_token():
    token = request.headers.get("Authorization")

    success, user = database_helper.get_user_data_by_token(token)

    if not success or not token:
        return jsonify(success=False, message="Incorrect token", data=None), 200
    
    success, messages = database_helper.get_user_messages_by_email(user["email"])

    print(messages)
    if not success:
        return jsonify(success=False, message="Incorrect email", data=None), 200

    if not messages:
        return jsonify(success=False, message="No messages retreived", data=None), 200

    return jsonify(success=True, message="Messages retreived", data=messages), 200




    

