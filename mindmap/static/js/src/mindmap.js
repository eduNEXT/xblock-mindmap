// TODO: add notifications
function MindMapXBlock(runtime, element, context) {
  const saveMindMapURL = runtime.handlerUrl(element, "save_assignment");
  const submitMindMapURL = runtime.handlerUrl(element, "submit_assignment");
  const getGradingDataURL = runtime.handlerUrl(element, "get_instructor_grading_data");
  const enterGradeURL = runtime.handlerUrl(element, "enter_grade");
  const removeGradeURL = runtime.handlerUrl(element, "remove_grade");

  function showMindMap(jsMind, context) {
    const mind = context.mind_map;

    mind.meta.author = context.author;

    container_selector = `jsmind_container_${context.xblock_id}`;
    container = $(element).find(`#${container_selector}`);
    if (container.length == 0) {
      return;
    }

    const options = {
      container: container_selector,
      editable: context.editable,
      theme: "asphalt",
    };

    const currentMindMap = new jsMind(options);
    currentMindMap.show(mind);

    $(element)
      .find(`#save_button_${context.xblock_id}`)
      .click(function () {
        handleMindMap(runtime, element, currentMindMap, saveMindMapURL);
      });

    $(element)
      .find(`#submit_button_${context.xblock_id}`)
      .click(function () {
        handleMindMap(runtime, element, currentMindMap, submitMindMapURL);
      });

    $(element)
      .find(`#get_submissions_button_${context.xblock_id}`)
      .click(function () {
        $.post(getGradingDataURL, JSON.stringify({}))
          .done(function (response) {
            console.log(response.assignments);
          })
          .fail(function () {
            console.log("Error submitting mind map");
          });
      });

    $(element)
      .find(`#enter-grade-button_${context.xblock_id}`)
      .click(function () {
        const grade = $(element).find(`#grade-input_${context.xblock_id}`).val();
        const submission_id = $(element).find(`#submission-id-input_${context.xblock_id}`).val();
        const data = {
          grade: grade,
          submission_id: submission_id,
        };
        console.log(data);
        $.post(enterGradeURL, JSON.stringify(data))
          .done(function (response) {
            console.log(response);
          })
          .fail(function (error) {
            console.log(error);
          });
      });

    $(element)
      .find(`#remove-grade-button_${context.xblock_id}`)
      .click(function () {
        const student_id = $(element).find(`#student-id-input_${context.xblock_id}`).val();
        const data = {
          student_id: student_id,
        };
        console.log(data);
        $.post(removeGradeURL, JSON.stringify(data))
          .done(function (response) {
            console.log(response);
          })
          .fail(function (error) {
            console.log(error);
          });
      });
  }

  function handleMindMap(runtime, element, mindMap, handlerUrl) {
    const mindMapData = mindMap.get_data("node_array");
    const jsonMindMapData = mindMapData;
    const data = { mind_map: jsonMindMapData };

    $.post(handlerUrl, JSON.stringify(data))
      .done(function (response) {
        window.location.reload(false);
      })
      .fail(function () {
        console.log("Error submitting mind map");
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
