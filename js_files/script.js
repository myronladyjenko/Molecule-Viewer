$(document).ready(function() {
    let element_cells = $("button");
    const prompt_form = $(".prompt-form"); 

    element_cells.each(function() {
        let cell = this;

        cell.addEventListener('click', function() {
            $.post("/form_handler.html",
	            /* pass a JavaScript dictionary */
	            {
                    url: "html_files/test.html",
	            },
                function(data) {
                    prompt_form.html(data);
                    $("#main-page").addClass("blur");
	            }
            );
        });
    });
});

window.onload = function() {
    $("#navigation-bar-placeholder").load("navigation_bar.html");
};
