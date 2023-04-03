$(document).ready(function() {
    let clicked_button;

    window.onload = function() {
        $("#navigation-bar-placeholder").load("navigation_bar.html");
    };

    $('.heading-periodic-table').click(function() {
        $('#lower-div').toggle();
    });

    const element_cells = $(".cell");
    const prompt_form = $(".prompt-form"); 

    prompt_form.submit(function(event) {
        event.preventDefault();

        $.post("/elements_manipulation.html", 
            {
                value: 1,
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
            }
        );
    });

    $("#question-button").on('click', function() {
        $.post("/form_handler.html",
            {
                url: "html_files/help_form.html",
            },
            function(data) {
                $(".help-guide").html(data);
                $("#main-page").addClass("blur");
                $(".help-guide").removeClass("hidden");
            }
        );
    });

    element_cells.each(function() {
        let cell = this;
        $(this).addClass("element-gray-class");

        cell.addEventListener('click', function() {
            clicked_button = cell;

            if ($(cell).hasClass("element-gray-class")) {
                $.post("/form_handler.html",
                    {
                        url: "html_files/add_elements_form.html",
                    },
                    function(data) {
                        prompt_form.html(data);
                        $("#main-page").addClass("blur");
                        prompt_form.removeClass("hidden");
                    }
                );
            } else {
                $.post("/elements_manipulation.html", 
                    {
                        value: -1,
                        code: $(clicked_button).find(".span-center").text(),
                    },
                    function(data) {
                        $(".table-of-elements").html(data);
                        $(clicked_button).addClass("element-gray-class");
                    }
                );
            }
        });
    });

    function checkIfElementsLoaded() {
        $.post("/elements_manipulation.html", 
            {
                value: 0
            },
            function(data) {
                let lines = data.split("\n");
                let name_cells = (lines[0]).trim().split(/ +/);

                new_str = "";
                for (let i = 1; i < lines.length; i++) {
                    new_str += lines[i] + "\n";
                }

                for (let i = 0; i < name_cells.length; i++) {
                    console.log(name_cells[i]);
                    let html_oblect = {};

                    $(".span-center").each(function() {
                        if (($(this).text().trim()) === (name_cells[i].trim())) {
                            html_oblect = this;
                        }
                    });

                    $(".cell").each(function() {
                        if ($(this).find(html_oblect).length > 0) {
                            $(this).removeClass("element-gray-class");
                        }
                    });
                }

                $(".table-of-elements").html(new_str);
            }
        );
    }
    checkIfElementsLoaded();
});
