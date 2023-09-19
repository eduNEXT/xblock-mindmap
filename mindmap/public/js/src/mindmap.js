// TODO: add notifications
function MindMapXBlock(runtime, element, context) {
  const saveMindMapURL = runtime.handlerUrl(element, "save_assignment");
  const submitMindMapURL = runtime.handlerUrl(element, "submit_assignment");
  const getGradingDataURL = runtime.handlerUrl(element, "get_instructor_grading_data");
  const enterGradeURL = runtime.handlerUrl(element, "enter_grade");
  const removeGradeURL = runtime.handlerUrl(element, "remove_grade");
  const maxPointsAllowed = context.max_points;

  let gettext;
  if ("MindMapI18N" in window || "gettext" in window) {
    gettext = window.MindMapI18N?.gettext || window.gettext;
  }

  if (typeof gettext == "undefined") {
    // No translations -- used by test environment
    gettext = (string) => string;
  }

  $(".card, .icon-collapsible").on("click", function () {
    $(".icon-collapsible").toggleClass("active");
    $(".collapse-container").slideToggle(200);
  });

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

            function showDataTable(newAssignments) {
              // TODO: add Submitted when submission issue is fixed
              const dataTableHeaderColumns = [
                gettext("Username"),
                gettext("Uploaded"),
                gettext("Submission Status"),
                gettext("Grade"),
                gettext("Actions"),
              ];
              const dataTableHeaderColumnsTranslated = dataTableHeaderColumns.map((currentColumn) =>
                gettext(currentColumn)
              );
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

              const modalTitleSubmissions = gettext("Mindmap submissions");
              const reviewButtonText = gettext("Review");
              const dataTableSearchText = gettext("Search");
              const dataTableEntriesText = gettext("Showing _START_ to _END_ of _TOTAL_ entries");
              const dataTableEmptyText = gettext("No data available in table");
              const dataTableInfoEmptyText = gettext("Showing 0 to 0 of 0 entries");
              const dataTableZeroRecordsText = gettext("No matching records found");
              const dataTableInfoFilteredText = gettext("(filtered from _MAX_ total entries)");
              $(element).find(".modal__data").html(dataTableHTML);
              $(element).find("#modal_title").html(modalTitleSubmissions);

              const dataTable = $("#dataTable").DataTable({
                data: newAssignments || assignments,
                scrollY: "50vh",
                dom: "Bfrtip",
                bPaginate: false,
                destroy: true,
                columns: [
                  { data: "username" },
                  { data: "timestamp" },
                  { data: "submission_status" },
                  { data: "score" },
                  {
                    data: null,
                    render: () => {
                      return `<button class="review_button button-link" type="button">${reviewButtonText}</button>`;
                    },
                  },
                ],
                language: {
                  info: dataTableEntriesText,
                  search: dataTableSearchText,
                  emptyTable: dataTableEmptyText,
                  infoEmpty: dataTableInfoEmptyText,
                  zeroRecords: dataTableZeroRecordsText,
                  infoFiltered: dataTableInfoFilteredText,
                },
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
                  const submitGradeButtonText = gettext("Submit");
                  const removeGradeButtonText = gettext("Remove grade");
                  const loadingButtonText = gettext("Loading...");
                  const reviewGoBackButtonText = gettext("Back");
                  const gradeLabelText = gettext("Grade");

                  const mindMapReviewContainer = `
                    <div class="review_mindmap_container">
                      <button class="button-link back-review">&larr;&nbsp; ${reviewGoBackButtonText}</button>
                      <div id="review-mindmap"></div>
                      <div class="grade-assessment">
                        <form id="grade-assessment-form">
                          <div class="grade-assessment_form-control">
                            <label for="grade">${gradeLabelText}</label>
                            <input type="number" name="grade" required class="inputs-styles" id="grade_value" />
                            <span class="error-message" id="error-grade"></span>
                          </div>
                          <div class="grade-assessment_form-buttons">
                            <button type="submit" class="grade-assessment__button-submit" data-type="add_grade">${submitGradeButtonText}</button>
                            <button type="submit" class="grade-assessment__button-submit" data-type="remove_grade">${removeGradeButtonText}</button>
                          </div>
                        </form>
                      </div>
                    </div>`;

                  const modalTitle = gettext("Reviewing Mindmap for student: ") + submissionData.username;
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
                      $.post(getGradingDataURL, JSON.stringify({}))
                        .done(function (response) {
                          const { assignments } = response;
                          showDataTable(assignments);
                        })
                        .fail(function () {
                          console.log("Error listing Mindmap submissions");
                        });
                    });

                  $(".grade-assessment__button-submit").on("click", function () {
                    // Get the custom data-type attribute of the clicked button
                    const typeAction = $(this).attr("data-type");
                    $("#grade-assessment-form").attr("data-type", typeAction);
                    if (typeAction === "remove_grade") {
                      $("#grade_value").removeAttr("required");
                      $("#grade_value").attr("type", "text");
                    } else {
                      $("#grade_value").attr("required");
                      $("#grade_value").attr("type", "number");
                    }
                  });

                  $("#grade-assessment-form").on("submit", function (e) {
                    e.preventDefault();
                    const typeAction = $(this).attr("data-type");
                    const grade = $("#grade_value").val();
                    const { submission_id, student_id, module_id } = submissionData;
                    const invalidGradeMessage = gettext("Invalid grade must be a number");
                    const maxGradeMessage = gettext("Please enter a lower grade, maximum grade allowed is:");
                    const gradeParsed = parseInt(grade, 10);

                    if (gradeParsed > maxPointsAllowed) {
                      $("#error-grade").html(`${maxGradeMessage} ${maxPointsAllowed}`);
                      return;
                    }

                    const onlyNumberRegex = /^[0-9]*$/g;

                    if (!onlyNumberRegex.test(grade)) {
                      $("#error-grade").html(invalidGradeMessage);
                      return;
                    }

                    $("#error-grade").html("");

                    let data;
                    let apiUrl;

                    if (typeAction === "add_grade") {
                      apiUrl = enterGradeURL;
                      data = {
                        grade: grade,
                        submission_id: submission_id,
                        module_id: module_id,
                      };
                    }

                    if (typeAction === "remove_grade") {
                      apiUrl = removeGradeURL;
                      data = {
                        student_id: student_id,
                        module_id: module_id,
                      };
                    }

                    $(".grade-assessment__button-submit").attr("disabled", "disabled");
                    $(".grade-assessment__button-submit").html(
                      `<i class="fa fa-spinner fa-spin"></i>${loadingButtonText}`
                    );
                    $.post(apiUrl, JSON.stringify(data))
                      .done(function (response) {
                        console.log(response);
                      })
                      .fail(function (error) {
                        console.log(error);
                      })
                      .always(function () {
                        $(".grade-assessment__button-submit").removeAttr("disabled");
                        const submitGradeButton = $('.grade-assessment__button-submit[data-type="add_grade"]');
                        const removeGradeButton = $('.grade-assessment__button-submit[data-type="remove_grade"]');
                        submitGradeButton.html(submitGradeButtonText);
                        removeGradeButton.html(removeGradeButtonText);
                      });
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
        const module_id = $(element).find(`#module-id-input_${context.xblock_id}`).val();
        const data = {
          grade: grade,
          submission_id: submission_id,
          module_id: module_id,
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
        const module_id = $(element).find(`#module-id-input_${context.xblock_id}`).val();
        const data = {
          student_id: student_id,
          module_id: module_id,
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
