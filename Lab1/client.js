displayView = function(selectedView){
    // the code required to display a view
    const selection = document.getElementById(selectedView);
    const view = document.getElementById("view");

    view.innerHTML = selection.innerHTML;
};

viewDecider = function() {
    const token = localStorage.getItem("token");
    
    if (token) {
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

submitSignup = function() {
    const firstname = document.getElementById("firstName");
    const lastname = document.getElementById("lastName");
    const gender = document.getElementById("gender");
    const city = document.getElementById("city");
    const country = document.getElementById("country");
    const email = document.getElementById("email");
    const password = document.getElementById("passwordSignup");

    const user = {firstname:firstname.value, familyname:lastname.value, gender:gender.value, city:city.value, country:country.value, email:email.value, password:password.value};

    result = serverstub.signUp(user);
    

    if (result.success) {
        const loginResult = serverstub.signIn(email.value, password.value);
        if (loginResult.success) {
            localStorage.setItem("token", loginResult.data);
            viewDecider();
        }
        
    } else {
        document.getElementById("signupError").innerText = result.message;
    }
};

submitLogin = function(event) {
    event.preventDefault();
    const email = document.getElementById("loginEmail");
    const password = document.getElementById("loginPassword");

    const result = serverstub.signIn(email.value, password.value)

    if (result.success) {
        localStorage.setItem("token", result.data);
        viewDecider();
    } else {
        document.getElementById("loginError").innerText = result.message;
    }
}

submitSignout = function() {
    const token = localStorage.getItem("token");
    result = serverstub.signOut(token);
    
    if (result.success) {
        localStorage.removeItem("token");
        viewDecider();
    } else {
        document.getElementById("signoutError").value = result.message;
    }
}

submitPasswordChange = function(event) {
    event.preventDefault();
    const token = localStorage.getItem("token");
    
    const newPass = document.getElementById("newPassword").value;
    const oldPass = document.getElementById("oldPassword").value;

    result = serverstub.changePassword(token, oldPass, newPass);
    document.getElementById("changePasswordStatus").innerText = result.message;
    if (result.success) {
        document.getElementById("changePasswordPanel").reset();
    }
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
        result = serverstub.getUserMessagesByToken(token);
        wall = document.getElementById("messageWall");      
    }
    else {
        
        const email = document.getElementById("browseEmail").innerText;
        
        result = serverstub.getUserMessagesByEmail(token, email);
        wall = document.getElementById("browseMessageWall");
    }
    
    const messages = result.data;
    
    wall.innerHTML = "";
    
    messages.forEach(msg => {
        const div = document.createElement("div");
        div.innerHTML = "<b>" + msg.writer + ":</b> " + msg.content;
        wall.appendChild(div);
    })

    
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
        serverstub.postMessage(token, messageInput.value, email);
        messageInput.value = "";
        updateMessageBox(self)
    }
}

loadData = function(self) {
    const token = localStorage.getItem("token");
    let user;
    let destination;
    
    if (self) {
        const result = serverstub.getUserDataByToken(token);
        user = result.data;
        
        destination = "home";
    }
    else {
        const email = document.getElementById("searchUser").value
        
        const result = serverstub.getUserDataByEmail(token, email);
        user = result.data;

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

searchUser = function() {
    const userEmail = document.getElementById("searchUser").innerText;
    const otherUser = serverstub.getUserDataByEmail(userEmail);
    loadData(false)
    
}
