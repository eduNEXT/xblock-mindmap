/* Javascript for MindMapXBlock. */

// TODO: add notifications
function MindMapXBlock(runtime, element, context) {
  var currentMindMap = null;

  $(element)
    .find(".save-button")
    .click(function () {
      const handlerUrl = runtime.handlerUrl(element, "studio_submit");
      const data = {
        display_name: $(element).find("input[name=mindmap_display_name]").val(),
        has_score: Number($(element).find("select[name=mindmap_has_score]").val()),
        weight: Number($(element).find("input[name=mindmap_weight]").val()),
        points: Number($(element).find("input[name=mindmap_points]").val()),
        is_static: Number($(element).find("select[name=mindmap_is_static]").val()),
        mind_map: currentMindMap.get_data("node_array"),
      };
      $.post(handlerUrl, JSON.stringify(data))
        .done(function () {
          window.location.reload(false);
        })
        .fail(function () {
          console.log("Error saving mindmap display name.");
        });
    });

  $(element)
    .find(".cancel-button")
    .click(function () {
      runtime.notify("cancel", {});
    });

  function showMindMap(jsMind, context) {
    const mind = context.mind_map;

    mind.meta.author = context.author;

    const options = {
      container: "jsmind_container",
      editable: context.editable,
      theme: "asphalt",
    };

    currentMindMap = new jsMind(options);
    currentMindMap.show(mind);
  }

  if (typeof require === "function") {
    require(["jsMind"], function (jsMind) {
      window.jsMind = jsMind;

      if (window.isJsMindDraggablePluginLoaded) {
        showMindMap(jsMind, context);
      } else {
        loadJsMindDraggablePlugin(function () {
          showMindMap(jsMind, context);
        });
      }
    });
  } else {
    loadJSMind(function () {
      showMindMap(window.jsMind, context);
    }, context.editable);
  }
}

function loadJSMind(callback, isEditable = false) {
  if (window.jsMind) {
    callback();
  } else {
    // Load jsMind dynamically using $.getScript
    $.getScript("https://unpkg.com/jsmind@0.6.4/es6/jsmind.js")
      .done(function () {
        // Assign jsMind to the window object after it's loaded
        window.jsMind = jsMind;
        // Load jsMind.draggable-node dynamically using $.getScript
        if (!window.isJsMindDraggablePluginLoaded && isEditable) {
          loadJsMindDraggablePlugin(callback);
        } else {
          callback();
        }
      })
      .fail(function () {
        console.error("Error loading jsMind.");
      });
  }
}

function loadJsMindDraggablePlugin(callback) {
  $.getScript("https://unpkg.com/jsmind@0.6.4/es6/jsmind.draggable-node.js")
    .done(function () {
      if (window.jsMind) {
        // Both jsMind and jsMind.draggable are now loaded and available
        window.isJsMindDraggablePluginLoaded = true;
        callback();
      } else {
        console.error("Error loading jsMind or jsMind.draggable.");
      }
    })
    .fail(function () {
      console.error("Error loading jsMind.draggable-node.");
    });
}
