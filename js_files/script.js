$(document).ready(function() {
    let clicked_button;

    window.onload = function() {
        $("#navigation-bar-placeholder").load("navigation_bar.html");
    };

    const element_cells = $(".cell");
    const prompt_form = $(".prompt-form"); 

    prompt_form.submit(function(event) {
        event.preventDefault();

        $.post("/elements_addition.html", 
            {
                number: parseInt($(clicked_button).find(".p-top").text()),
                code: $(clicked_button).find(".span-center").text(),
                name: $(clicked_button).find(".p-bottom").text(),
                radius: parseInt($("#radius").val()),
                color1: $("#col1").val(),
                color2: $("#col2").val(),
                color3: $("#col3").val(),
            },
            function(data) {
                $(".table-of-elements").html(data);
                $(prompt_form).addClass("hidden");
                $("#main-page").removeClass("blur");
                $(clicked_button).removeClass("element-gray-class");
                $(".heading-elements-in-database").removeClass("hidden");
                $(".table-of-elements").removeClass("hidden");
            }
        );
    });

    element_cells.each(function() {
        let cell = this;
        $(this).addClass("element-gray-class");

        cell.addEventListener('click', function(event) {
            clicked_button = cell;

            $.post("/form_handler.html",
	            /* pass a JavaScript dictionary */
	            {
                    url: "html_files/add_elements_form.html",
	            },
                function(data) {
                    prompt_form.html(data);
                    $("#main-page").addClass("blur");
                    prompt_form.removeClass("hidden");
	            }
            );
        });
    });
});
