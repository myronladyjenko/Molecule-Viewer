$(document).ready(function() {
    window.onload = function() {
        $("#navigation-bar-placeholder").load("navigation_bar.html");
    };

    window.addEventListener('scroll', () => {
        const top = (window.innerHeight / 2 - $(".prompt-form").height() / 2) + window.scrollY;
        const string = top.toString() + "px"; 
        $(".prompt-form").css("top", string);
    });
});