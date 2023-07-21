/* Javascript for MindMapXBlock. */

// TODO: add notifications
function MindMapXBlock(runtime, element) {
  console.loog('Lms :D');
  $(element).find('.save-button').click(function () {
    const handlerUrl = runtime.handlerUrl(element, 'studio_submit');
    const data = {
      display_name: $(element).find('input[name=mindmap_display_name]').val(),
    };
    $.post(handlerUrl, JSON.stringify(data)).done(function (response) {
      window.location.reload(false);
    }).fail(function () {
      console.log('Error saving mindmap display name.')
    });
  });

  $(element).find('.cancel-button').click(function () {
    runtime.notify('cancel', {});
  });
}
