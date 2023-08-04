// TODO: add notifications
function MindMapXBlock(runtime, element, context) {

    function showMindMap(jsMind, context) {
        const baseMind = {
            meta: {
                name: "Mind Map",
                version: "0.1",
            },
            format: "node_array",
            data: [{ id: "root", isroot: true, topic: "Root" }],
        };

        const mind = context.mind_map || baseMind;
        mind.meta.author = context.author;

        const options = {
            container: "jsmind_container",
            editable: context.editable,
            theme: "asphalt",
        };

        const currentMindMap = new jsMind(options);
        currentMindMap.show(mind);

        $(element).find(".save-button-student").click(function () {
            saveMindMap(runtime, element, currentMindMap, "student");
        });

        $(element).find(".save-button-instructor").click(function () {
            saveMindMap(runtime, element, currentMindMap, "instructor");
        });
    };

    function saveMindMap(runtime, element, mindMap, path_prefix) {
        const mindMapData = mindMap.get_data("node_array");
        const jsonMindMapData = JSON.stringify(mindMapData);
        const handlerUrl = runtime.handlerUrl(element, "upload_file");
        const data = { mind_map: jsonMindMapData, path_prefix: path_prefix };

        $.post(handlerUrl, JSON.stringify(data))
            .done(function (response) {
                window.location.reload(false);
            })
            .fail(function () {
                console.log("Error saving mind map");
            });
    }

    if (typeof require === "function") {
        require(["jsMind"], function (jsMind) {
            showMindMap(jsMind, context);
        });
    } else {
        loadJSMind(function () {
            showMindMap(window.jsMind, context);
        });
    }
}


function loadJSMind(callback) {
    if (window.jsMind) {
        callback();
    } else {
        // Load jsMind dynamically using $.getScript
        $.getScript("https://unpkg.com/jsmind@latest/es6/jsmind.js")
            .done(function () {
                // Assign jsMind to the window object after it's loaded
                window.jsMind = jsMind;

                // Load jsMind.draggable-node dynamically using $.getScript
                $.getScript("https://unpkg.com/jsmind@latest/es6/jsmind.draggable-node.js")
                    .done(function () {
                        if (window.jsMind) {
                            // Both jsMind and jsMind.draggable are now loaded and available
                            callback();
                        } else {
                            console.error("Error loading jsMind or jsMind.draggable.");
                        }
                    })
                    .fail(function () {
                        console.error("Error loading jsMind.draggable-node.");
                    });
            })
            .fail(function () {
                console.error("Error loading jsMind.");
            });
    }
}
