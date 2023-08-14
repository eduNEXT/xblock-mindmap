// TODO: add notifications
function MindMapXBlock(runtime, element, context) {

    function showMindMap(jsMind, context) {
        const mind = context.mind_map

        mind.meta.author = context.author;

        container_selector = `jsmind_container_${context.xblock_id}`
        container = $(element).find(`#${container_selector}`)
        if (container.length == 0) {
          return
        }

        const options = {
            container: container_selector,
            editable: context.editable,
            theme: "asphalt",
        };

        const currentMindMap = new jsMind(options);
        currentMindMap.show(mind);

        $(element).find(`#save_button_${context.xblock_id}`).click(function () {
            saveMindMap(runtime, element, currentMindMap, "student");
        });

    };

    function saveMindMap(runtime, element, mindMap, path_prefix) {
        const mindMapData = mindMap.get_data("node_array");
        const jsonMindMapData = mindMapData;
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
        $.getScript("https://unpkg.com/jsmind@0.6.4/es6/jsmind.js")
            .done(function () {
                // Assign jsMind to the window object after it's loaded
                window.jsMind = jsMind;

                // Load jsMind.draggable-node dynamically using $.getScript
                $.getScript("https://unpkg.com/jsmind@0.6.4/es6/jsmind.draggable-node.js")
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
