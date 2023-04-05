$(document).ready(function() {
    $("#question-button").on('click', function() {
        $.post("/form_handler.html",
            {
                url: "html_files/help_form_upload.html",
            },
            function(data) {
                $(".help-guide").html(data);
                $("#main-page").addClass("blur");
                $(".help-guide").removeClass("hidden");
            }
        );
    });

    function popUp(message) {
        $("#pop-up-main-message").text(message);
        $("#pop-up-main").prop("title", "Error!");
        $("#pop-up-main").dialog({});  
    }

    function sumbitFromWhenExists() {
        $("#rotations").submit(function(event) {
            const clickedButton = this;
            event.preventDefault();

            let xIn = $("#roll").val();
            let yIn = $("#pitch").val();
            let zIn = $("#yaw").val();
            const x = parseInt(xIn);
            const y = parseInt(yIn);
            const z = parseInt(zIn);
            let check = true;

            if ((xIn === '' || yIn === '' || zIn === '')) {
                popUp("Please, make sure to fill out all fields");            
            } else {
                if (x === 0 && y === 0 && z === 0) {
                    check = false;
                }

                if (x === 0 && y === 0 && z !== 0) {
                    if (z >= 0 && z <= 360) {
                        check = false;
                    } else {
                        popUp("Please enter degrees between 0 and 360");
                        return;
                    }
                }

                if (x === 0 && y !== 0 && z === 0) {
                   if (y >= 0 && y <= 360) {
                        check = false;
                    } else {
                        popUp("Please enter degrees between 0 and 360");
                        return;
                    }
                }

                if (x !== 0 && y === 0 && z === 0) {
                   if (x >= 0 && x <= 360) {
                        check = false;
                    } else {
                        popUp("Please enter degrees between 0 and 360");
                        return;
                    }
                }
            }

            if (check === true) {
                popUp("Please, ensure that one field is not zero");    
            } else {
                $.post("/post_molecule.html", 
                    {
                        value: -1,
                        name: $($(clickedButton).closest("tr").prev("tr").find("td")[1]).text().trim(),
                        x_value: x,
                        y_value: y,
                        z_value: z
                    },
                    function(data) {
                        $(clickedButton).closest("tr").find(".mol-display-div").html(data);
                    }
                );                
            }
        });
    }

    $(".prompt-form").submit(function(event) {
        event.preventDefault();
        if ($("#mol_name").val().trim() === "") {
            $("#mol_name").css({"background-color": "#E93636", "color": "white"});
  
            setTimeout(() => {
                $("#mol_name").css({"background-color": "white", "color": "black"});
            }, 500);

            $("#pop-up-message").text("Please enter a molecule name.");
            $("#pop-up").dialog({
                buttons: {
                    close: function() {
                        $(this).dialog("close");
                    }
                }
            });
        } else if ($("#sdf_file")[0].files[0] === undefined) {
            $("#pop-up-message").text("Please choose a molecule.");
            $("#pop-up").dialog({
                buttons: {
                    close: function() {
                        $(this).dialog("close");
                    }
                }
            });
        } else {
            const file = $("#sdf_file")[0].files[0];

            const fileReader = new FileReader();
            fileReader.readAsText(file);
            fileReader.onload = function() {
                $.post("/molecule_manipulation.html", 
                    {
                        value: 1,
                        name: $("#mol_name").val(),
                        fileContents: fileReader.result
                    },
                    function(data) {
                        let lines = data.split("\n");
                        errorValue = lines[0];

                        new_str = "";
                        for (let i = 1; i < lines.length; i++) {
                            new_str += lines[i] + "\n";
                        }

                        $(".table-of-molecules").html(new_str);
                        $(".prompt-form").addClass("hidden");
                        $("#main-page").removeClass("blur");
                        $(".background-image").removeClass("blur");

                        addViewListeners($(".view-btn-icon"));
                        addDeleteListeners($(".delete-btn-icon"));
                        sumbitFromWhenExists();

                        if (errorValue === '1') {
                            $("#pop-up-main-message").text("This molecule already exists.");
                            $("#pop-up-main").prop("title", "Error!");
                            $("#pop-up-main").dialog({});
                        } else if (errorValue === '2') {
                            $("#pop-up-main-message").text("This file contains 0 atoms and bonds");
                            $("#pop-up-main").prop("title", "Notification");
                            $("#pop-up-main").dialog({});
                        } else {
                            $("#pop-up-main-message").text("File has been sucessfully uploaded.");
                            $("#pop-up-main").dialog({});
                        }
                    }
                );
            };
        }
    });

    $(".heading-molecule-upload").on('click', function() {
        $.post("/form_handler.html",
            {
                url: "html_files/upload_molecule_form.html",
            },
            function(data) {
                $(".prompt-form").html(data);
                const top = (window.innerHeight / 2 - $(".prompt-form").height() / 2) + window.scrollY;
                const string = top.toString() + "px"; 
                $(".prompt-form").css("top", string);

                $("#main-page").addClass("blur");
                $(".background-image").addClass("blur");
                $(".prompt-form").removeClass("hidden");
            }
        );
    });

    window.addEventListener('load', function() {
        if ($(".view-btn-icon").length > 0) {
            addViewListeners($(".view-btn-icon"));
            sumbitFromWhenExists();
        }

        if ($(".delete-btn-icon").length > 0) {
            addDeleteListeners($(".delete-btn-icon"));
        }
    });

    function addDeleteListeners(buttons) {
        $(buttons).each(function() {
            $(this).on('click', function() {
                $.post("/molecule_manipulation.html", 
                    {
                        value: -1,
                        name: $($(this).closest("tr").find("td")[1]).text().trim()
                    },
                    function(data) {
                        $(".table-of-molecules").html(data);
                        addDeleteListeners($(".delete-btn-icon"));
                        addViewListeners($(".view-btn-icon"));
                    }
                );                        
            });
        });
    }

    function addViewListeners(buttons) {
        $(buttons).each(function() {
            $(this).on('click', function() {
                clickedButton = this;
                if ($(this).closest("tr").next("tr").hasClass("hidden")) {
                    $.post("/post_molecule.html", 
                        {
                            value: 1,
                            name: $(this).closest("td").next("td").text().trim()
                        },
                        function(data) {
                            $(clickedButton).closest("tr").next("tr").find(".mol-display-div").html(data);
                        }
                    );
                    
                    $.post("/form_handler.html", 
                        {
                            url: "html_files/rotation_form.html",
                        },
                        function(data) {
                            $(clickedButton).closest("tr").next("tr").find("#rotations").html(data);
                        }
                    );  

                    $(this).closest("tr").next("tr").removeClass("hidden");
                } else {
                    $(this).closest("tr").next("tr").find(".mol-display-div").empty();
                    $(this).closest("tr").next("tr").addClass("hidden");
                }
            });
        });
    }

    function checkIfMoleculeLoaded() {
        $.post("/molecule_manipulation.html", 
            {
                value: 0
            },
            function(data) {
                $(".table-of-molecules").html(data);
            }
        );
    }
    checkIfMoleculeLoaded();
});