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