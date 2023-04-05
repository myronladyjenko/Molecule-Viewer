$(document).ready(function() {
    let clicked_button;

    $('.heading-periodic-table').click(function() {
        $('#lower-div').toggle();
    });

    const element_cells = $(".cell");
    const prompt_form = $(".prompt-form"); 

    prompt_form.submit(function(event) {
        event.preventDefault();
        const radVal = $("#radius").val();
        const radius = parseInt($("#radius").val());

        if (radVal.trim() === '' || radius > 100 || radius < 25) {
            $("#radius").css({"background-color": "#E93636", "color": "white"});
  
            setTimeout(() => {
                $("#radius").css({"background-color": "white", "color": "black"});
            }, 500);

            $("#pop-up-message").text("Please a correct radius (between 25 and 80)");
            $("#pop-up").dialog({
                buttons: {
                    close: function() {
                        $(this).dialog("close");
                    }
                }
            });            
        } else {
            $.post("/elements_manipulation.html", 
                {
                    value: 1,
                    number: parseInt($(clicked_button).find(".p-top").text()),
                    code: $(clicked_button).find(".span-center").text().trim(),
                    name: $(clicked_button).find(".p-bottom").text().trim(),
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
                    $(clicked_button).hover(function() {
                        $(this).css({"background-color": "red"});
                    }, function() {
                        $(this).css("background-color", "");
                    });

                    let dimensionY = $(".table-of-elements").offset().top;
                    $('html, body').animate({scrollTop: dimensionY}, 'slow');
                }
            );
        }
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
                        const top = (window.innerHeight / 2 - $(prompt_form).height() / 2) + window.scrollY;
                        const string = top.toString() + "px"; 
                        $(prompt_form).css("top", string);

                        $("#main-page").addClass("blur");
                        prompt_form.removeClass("hidden");
                    }
                );
            } else {
                $.post("/elements_manipulation.html", 
                    {
                        value: -1,
                        code: $(clicked_button).find(".span-center").text().trim(),
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
                    let html_oblect = {};

                    $(".span-center").each(function() {
                        if (($(this).text().trim()) === (name_cells[i].trim())) {
                            html_oblect = this;
                        }
                    });

                    $(".cell").each(function() {
                        if ($(this).find(html_oblect).length > 0) {
                            $(this).removeClass("element-gray-class");

                            $(this).hover(function() {
                                $(this).css("background-color", "red");
                            }, function() {
                                $(this).css("background-color", "");
                            });                            
                        }
                    });
                }

                $(".table-of-elements").html(new_str);
            }
        );
    }
    checkIfElementsLoaded();
});
