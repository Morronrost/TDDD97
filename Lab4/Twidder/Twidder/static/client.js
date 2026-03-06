displayView = function(selectedView){
    // the code required to display a view
    const selection = document.getElementById(selectedView);
    const view = document.getElementById("view");

    view.innerHTML = selection.innerHTML;
};

viewDecider = function() {
    const token = localStorage.getItem("token");
    
    if (token) {
        initWebSocket(token);
        displayView("profileView")
        loadData(true)
        updateMessageBox();
        
    } else {
        displayView("welcomeView")
    };
}

window.onload = function(){
    //code that is executed as the page is loaded.
    //You shall put your own custom code here.
    //window.alert() is not allowed to be used in your implementation.
    //window.alert("Hello TDDD97!");

    viewDecider();
};


validatePasswordLength = function(pass) {

    if (pass.value.length <= 7 ) {
        pass.setCustomValidity("Password must be at least 8 characters long");
        return false;
    } else {
        pass.setCustomValidity("");
    }

    return true;
};

validateRepeatPassword = function(id1, id2) {
    
    const password = document.getElementById(id1);
    const repeat = document.getElementById(id2);
    
    
    if (password.value !== repeat.value) {
        repeat.setCustomValidity("Passwords do not match");
        return false;
    } else {
        repeat.setCustomValidity("");
    };
    return true;
};

submitSignup = function(event) {
    event.preventDefault();
    const firstname = document.getElementById("firstName");
    const lastname = document.getElementById("lastName");
    const gender = document.getElementById("gender");
    const city = document.getElementById("city");
    const country = document.getElementById("country");
    const email = document.getElementById("email");
    const password = document.getElementById("passwordSignup");

    const user = {firstname:firstname.value, familyname:lastname.value, gender:gender.value, city:city.value, country:country.value, email:email.value, password:password.value};
    sendRequest("POST", "/sign_up", user, function(status, result) {
        if (status == 201) {
            
            var signinData = {username:email.value, password:password.value} 
            sendRequest("POST", "/sign_in", signinData, function(status, result) {
                if (status == 200) {
                    localStorage.setItem("token", result.data);
                    viewDecider();
                }
            })
        }
        else if (status == 400) {
            if(result.message == "Invalid data field.") {
                getElementById("signupError").innerText = "One or more input fields is missing.";    
            }
            else {
                getElementById("signupError").innerText = "Invalid email";
            }
        }
        else if (status == 409) {
            getElementById("signupError").innerText = "User already exists"
        }
    })
};

submitLogin = function(event) {
    event.preventDefault();
    const email = document.getElementById("loginEmail");
    const password = document.getElementById("loginPassword");

    var signinData = {username:email.value, password:password.value} 
    sendRequest("POST", "/sign_in", signinData, function(status, result) {
        if (status == 200) {
            localStorage.setItem("token", result.data);
            initWebSocket(result.data);
            viewDecider();
        }
        else if (status == 400) {
            document.getElementById("loginError").innerText = "Missing input";
        }
        else if (status == 401) {
            document.getElementById("loginError").innerText = "Invalid username or password";

        }
    });
}

submitSignout = function() {
    const token = localStorage.getItem("token");
    sendRequest("DELETE", "/sign_out", null, function(status, result){
        if (status == 200) {
            localStorage.removeItem("token");
            viewDecider();
        }
        else if (status == 404){
            document.getElementById("signoutError").value = "Could not find user token";
        }
        else if (status == 401) {
            document.getElementById("signoutError").value = "Could not authorize user";          
        }
    }, token);
}

submitPasswordChange = function(event) {
    event.preventDefault();
    const token = localStorage.getItem("token");
    
    const newPass = document.getElementById("newPassword").value;
    const oldPass = document.getElementById("oldPassword").value;
    var data = {oldpassword:oldPass, newpassword:newPass};
    window.alert("new password: " + data.newpassword + "old password: " + data.oldpassword);


    sendRequest("PUT", "/change_password", data, function(status, result){
        if (status == 201) {
            document.getElementById("changePasswordPanel").reset();
            document.getElementById("changePasswordStatus").innerText = "Password has been changed";
        }
        else if (status == 400 && result.message == "Incorrect oldpassword") {
            document.getElementById("changePasswordStatus").innerText = "Current password is incorrect";
        }
        else if (status == 400) {
            document.getElementById("changePasswordStatus").innerText = "Missing input";
        }
        else if (status == 401) {
            document.getElementById("changePasswordStatus").innerText = "Authentication error";
        }
        else if (status == 404) {
            document.getElementById("changePasswordStatus").innerText = "User not found";
        }
    }, token);
}

switchTab = function(name) {
    const tabs = document.querySelectorAll(".tab");
    const panels = document.querySelectorAll(".panel");

    tabs.forEach(tab => tab.classList.remove("active"));
    panels.forEach(panel => panel.classList.remove("active"));
    
    document.getElementById(name + "Tab").classList.add("active");
    document.getElementById(name + "Panel").classList.add("active");
}

updateMessageBox = function(self) {
    const token = localStorage.getItem("token");
    let result;
    let wall;


    if (self) {
        sendRequest("GET", "/get_user_messages_by_token", null, function(status, result){
            if (status == 200) {
                wall = document.getElementById("messageWall");
                const messages = result.data;
    
                wall.innerHTML = "";
                
                messages.forEach(msg => {
                    const div = document.createElement("div");
                    div.innerHTML = "<b>" + msg.sender_email + ":</b> " + msg.content;
                    wall.appendChild(div);
                })
                setErrorBar("");
            }
            else if (status == 400) {
                setErrorBar("Empty message");
            }
            else if (status == 401) {
                setErrorBar("Authentication error");
            }
            else if (status == 404 && result.message == "Email not found"){
                setErrorBar("User not found");
            }
        }, token);
    }
    else {
        const email = document.getElementById("browseEmail").innerText;
        sendRequest("GET", "/get_user_messages_by_email/" + email, null, function(status, result){
            if (status == 200) {
                wall = document.getElementById("browseMessageWall");

                const messages = result.data;
                
                wall.innerHTML = "";
                
                messages.forEach(msg => {
                    const div = document.createElement("div");
                    div.innerHTML = "<b>" + msg.sender_email + ":</b> " + msg.content;
                    wall.appendChild(div);
                })
                setErrorBar("");
            }
            else if (status == 400) {
                setErrorBar("Empty message");
            }
            else if (status == 401) {
                setErrorBar("Authentication error");
            }
            else if (status == 404) {
                setErrorBar("User not found");
            }
        }, token);
    }
    
    

    
}

postMessage = function(self) {
    const token = localStorage.getItem("token");
    let email;
    let messageInput;
    if (self) {
        email = document.getElementById("homeEmail").innerText;
        messageInput = document.getElementById("messageInput");
    }
    else {
        email = document.getElementById("browseEmail").innerText;
        messageInput = document.getElementById("browseMessageInput");
        
    }
    if (messageInput.value != "") {
        var data = {email:email, message:messageInput.value}
        sendRequest("POST", "/post_message", data, function(status, result){
            if (status == 201) {
                messageInput.value = "";
                updateMessageBox(self)
                etErrorBar("");
            }
            else if (status == 400) {
                setErrorBar("Empty message");
            }
            else if (status == 401) {
                setErrorBar("Authentication error");
            }
            else if (status == 404) {
                setErrorBar("User not found");
            }
            else if (status == 500) {
                setErrorBar("Internal error");
            }
        }, token);
        
    }
}

loadData = function(self) {
    const token = localStorage.getItem("token");
    
    if (self) {
        sendRequest("GET", "/get_user_data_by_token", null, function(status, result){
            if (status == 200) {
                displayInfo(true, result.data)
            }
            else if (status == 401) {
                setErrorBar("Authentication error");
            }
            else if (status == 404) {
                setErrorBar("User not found");
            }
        }, token);
    }
    else {
        const email = document.getElementById("searchUser").value
        sendRequest("GET", "/get_user_data_by_email/" + email, null, function(status, result){
            if (status == 200) {
                displayInfo(false, result.data);
                setErrorBar("");
            }
            else if (status == 400) {
                setErrorBar("Invalid email");
            }
            else if (status == 401) {
                setErrorBar("Authentication error");
            }
            else if (status == 404) {
                setErrorBar("User not found");
            }
        }, token);
    }

    
    
}

setErrorBar = function(message) {
    document.getElementById("errorBarMessage").innerText = message;
}

displayInfo = function(self, user, error) {
    let destination;

    if (self) {
        destination = "home";
    }
    else {
        destination = "browse";
    }
    
    
    document.getElementById(destination + "Firstname").innerText = user.firstname;
    document.getElementById(destination + "Lastname").innerText = user.familyname;
    document.getElementById(destination + "Gender").innerText =  user.gender;
    document.getElementById(destination + "Email").innerText = user.email;
    document.getElementById(destination + "City").innerText = user.city;
    document.getElementById(destination + "Country").innerText = user.country;
    
    updateMessageBox(self); 

    
}

sendRequest = function(method, path, data, callback, token=null) {
    var request = new XMLHttpRequest();
    request.open(method, path, true);
    request.setRequestHeader("Content-Type", "application/json");

    if (token) {
        request.setRequestHeader("Authorization", token);
    }
    
    request.onload = function() {
        var result = JSON.parse(request.responseText);
        callback(request.status ,result);
        // if (request.status == 200 || request.status == 201) {
        //     var result = JSON.parse(request.responseText);
        //     callback(request.status ,result);
        // }
        // else {
        //     callback({ request.status });
        // }
    }
    request.send(JSON.stringify(data));
}

persistentSocket = null;

initWebSocket = function(token) {

    if (persistentSocket) return;

    const wsUrl = "ws://" + window.location.host + "/ws/" + token;

    persistentSocket = new WebSocket(wsUrl);

    persistentSocket.onmessage = function(event) {
        const msg = JSON.parse(event.data);
        
        if (msg.type === "logout") {
            localStorage.removeItem("token"); 
            persistentSocket.close();
            persistentSocket = null;
            viewDecider();
        }
    }

    persistentSocket.onclose = function() {
        persistentSocket = null;
    };

}
