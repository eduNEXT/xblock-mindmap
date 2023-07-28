function MindMapXBlock(runtime, element, context) {

    const baseMind = {
        "meta": {
            "name": "Mind Map",
            "author": "eduNEXT",
            "version": "0.1"
        },
        "format": "node_array",
        "data": [
            { "id": "root", "isroot": true, "topic": "Root" },
        ]
    };

    const mind = context.mind_map || baseMind;

    const options = {
        container: 'jsmind_container',
        editable: true,
        theme: 'asphalt',
    };

    const jm = new jsMind(options);
    jm.show(mind);

    $(element).find('.save-button').click(function () {
        const mindMapData = jm.get_data('node_array');
        const jsonMindMapData = JSON.stringify(mindMapData);
        const handlerUrl = runtime.handlerUrl(element, 'upload_file');
        const data = { mind_map: jsonMindMapData };

        $.post(handlerUrl, JSON.stringify(data)).done(function (response) {
            window.location.reload(false);
        }).fail(function () {
            console.log("Error saving mind map");
        });
    });
}
