$(document).ready(function () {

    // all custom jQuery will go here
    $("#firstbutton").click(function () {
        $.ajax({
            url: "http://192.168.33.10:30077", success: function (result) {
                $("#firstbutton").toggleClass("btn-primary:focus");
                }
        });
    });
    $("#secondbutton").click(function () {
        $.ajax({
            url: "http://192.168.33.10:30078", success: function (result) {
                $("#secondbutton").toggleClass("btn-primary:focus");
            }
        });
    });    
});