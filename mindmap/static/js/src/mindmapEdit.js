/* Javascript for MindMapXBlock. */
function MindMapXBlock(runtime, element) {

  $(element).find('.save-button').click(function () {
    var handlerUrl = runtime.handlerUrl(element, 'studio_submit');
    var data = {
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
