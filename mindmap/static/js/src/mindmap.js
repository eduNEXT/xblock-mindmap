// TODO: add notifications
function MindMapXBlock(runtime, element, context) {
  const saveMindMapURL = runtime.handlerUrl(element, "save_assignment");
  const submitMindMapURL = runtime.handlerUrl(element, "submit_assignment");
  const getGradingDataURL = runtime.handlerUrl(element, "get_instructor_grading_data");
  const enterGradeURL = runtime.handlerUrl(element, "enter_grade");
  const removeGradeURL = runtime.handlerUrl(element, "remove_grade");

  /*
    Usually serializeArray gives us
    values of the form like this:
    doc https://api.jquery.com/serializearray/
    [
      {
        name: "field1",
        value: "value1"
      },
      {
        name: "field2",
        value: "value2"
      },
      ...
    ]
    This converts to an object with key value
    {
      field1: value1,
      field2: value2
    }
  */
  $.fn.serializeArrayToObject = function () {
    const objectSerialize = {};
    const arrayFields = this.serializeArray();
    arrayFields.forEach(function (item) {
      const { name, value } = item;

      if (objectSerialize[name] === undefined) {
        objectSerialize[name] = value || "";
      } else {
        if (!Array.isArray(objectSerialize[name])) {
          objectSerialize[name] = [objectSerialize[name]];
        }
        objectSerialize[name].push(value || "");
      }
    });

    return objectSerialize;
  };

  $(document).keydown(function (event) {
    // 'Esc' key was pressed
    if (event.key === "Escape") {
      $(element).find("#modal-submissions").removeClass("modal_opened");
    }
  });

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
      .find(".modal__close")
      .click(function () {
        $(element).find("#modal-submissions").removeClass("modal_opened");
      });

    $(element)
      .find(`#get_grade_submissions_button_${context.xblock_id}`)
      .click(function () {
        $.post(getGradingDataURL, JSON.stringify({}))
          .done(function (response) {
            const { assignments } = response;
            $(element).find("#modal-submissions").addClass("modal_opened");

            showDataTable();

            function showDataTable() {
              // TODO: add Submitted when submission issue is fixed
              const dataTableHeaderColumns = ["Username", "Uploaded", "Grade", "Actions"];
              const dataTableHeaderColumnsTranslated = dataTableHeaderColumns.map((currentColumn) => gettext(currentColumn));
              const dataTableHeaderColumnsHTML = dataTableHeaderColumnsTranslated.reduce(
                (prevColumn, currentColumn) => `${prevColumn}<th>${currentColumn}</th>`,
                ""
              );
              const dataTableHTML = `
                <table id="dataTable">
                  <thead>
                    <tr>
                      ${dataTableHeaderColumnsHTML}
                    </tr>
                  </thead>
                  <tbody>
                    <!-- Data rows will be added here using DataTables -->
                  </tbody>
                </table>
              `;

              $(element).find(".modal__data").html(dataTableHTML);
              $(element).find("#modal_title").html(gettext("Mindmap submissions"));

              const dataTable = $("#dataTable").DataTable({
                data: assignments,
                scrollY: "50vh",
                dom: "Bfrtip",
                bPaginate: false,
                destroy: true,
                columns: [
                  { data: "username" },
                  { data: "timestamp" },
                  // TODO: add this line { data: "submitted" },
                  { data: "score" },
                  {
                    data: null,
                    render: () => {
                      return `<button class="review_button button-link" type="button">${gettext("Review")}</button>`;
                    },
                  },
                ],
                language: {
                  info: gettext("Showing _START_ to _END_ of _TOTAL_ entries"),
                  search: gettext("Search"),
                }
              });

              handleRowDataTableClick(dataTable);
            }

            function handleRowDataTableClick(dataTable) {
              $(element)
                .find("#dataTable")
                .on("click", ".review_button", function (e) {
                  e.preventDefault();
                  const target = $(e.target);
                  const link = target;
                  const rowReview = link.closest("tr");
                  const submissionData = dataTable.row(rowReview).data();
                  const answerMindMap = submissionData.answer_body.mindmap_student_body;
                  const answerMindMapFormat = JSON.parse(answerMindMap);

                  const mindMapReviewContainer = `
                    <div class="review_mindmap_container">
                      <button class="button-link back-review">&larr;&nbsp; ${gettext('Back')}</button>
                      <div id="review-mindmap"></div>
                      <div class="grade-assessment">
                        <form id="grade-assessment-form">
                          <div class="grade-assessment_form-control">
                            <label for="grade">${gettext('Grade')}</label>
                            <input type="number" name="grade" class="inputs-styles" />
                          </div>
                          <div class="grade-assessment_form-control">
                            <label for="comment">${gettext('Comment')}</label>
                            <textarea rows="4" cols="50" name="comment" class="text-area-styles" placeholder="${gettext('optional')}"></textarea>
                          </div>
                          <div class="grade-assessment_form-buttons">
                            <button type="submit" class="grade-assessment__button-submit">${gettext('Submit')}</button>
                            <button type="submit" class="grade-assessment__button-submit">${gettext('Remove grade')}</button>
                          </div>
                        </form>
                      </div>
                    </div>`;

                  const modalTitle = gettext('Reviewing Mindmap for student:') + submissionData.username;
                  $(element).find(".modal__data").html(mindMapReviewContainer);
                  $(element).find("#modal_title").html(modalTitle);
                  const [mindMapReviewContent] = $(element).find("#review-mindmap");
                  const reviewMindMapOptions = {
                    container: mindMapReviewContent,
                    editable: false,
                    theme: "asphalt",
                  };

                  const currentMindMapReview = new jsMind(reviewMindMapOptions);
                  currentMindMapReview.show(answerMindMapFormat);

                  $(element)
                    .find(".back-review")
                    .click(function () {
                      showDataTable();
                    });

                  $("#grade-assessment-form").on("submit", function (e) {
                    e.preventDefault();
                    const formValues = $(this).serializeArrayToObject();
                    console.log("grade-assessment-form -> formValues", formValues);
                    console.log("submissionData ->", submissionData);
                  });
                });
            }
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

  function handleMindMap(_, _, mindMap, handlerUrl) {
    const mindMapData = mindMap.get_data("node_array");
    const jsonMindMapData = mindMapData;
    const data = { mind_map: jsonMindMapData };

    $.post(handlerUrl, JSON.stringify(data))
      .done(function () {
        window.location.reload(false);
      })
      .fail(function () {
        console.log("Error submitting mind map");
      });
  }

  // Allows us to add a script to the DOM
  function loadScript(script) {
    $("<script>").attr("type", "text/javascript").attr("src", script).appendTo(element);
  }

  if (typeof require === "function") {
    require(["jsMind"], function (jsMind) {
      showMindMap(jsMind, context);
    });
  } else {
    loadJSMind(function () {
      showMindMap(window.jsMind, context);
    });

    loadScript("https://cdn.datatables.net/1.11.5/js/jquery.dataTables.js");
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
