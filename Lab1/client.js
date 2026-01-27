displayView = function(selectedView){
    // the code required to display a view
    const selection = document.getElementById(selectedView);
    const view = document.getElementById("view");

    view.innerHTML = selection.innerHTML;
};

window.onload = function(){
    //code that is executed as the page is loaded.
    //You shall put your own custom code here.
    //window.alert() is not allowed to be used in your implementation.
    //window.alert("Hello TDDD97!");

    const loggedIn = false;

    if (loggedIn) {
        displayView("profileView")
    } else {
        displayView("welcomeView")
    };
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

validateRepeatPassword = function() {
    
    const password = document.getElementById("passwordSignup");
    const repeat = document.getElementById("repeatPS");
    
    
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
    
    window.alert(result.message);

    if (result.success) {
        displayView(profileView);
    }

};

