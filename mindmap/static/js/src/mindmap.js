function MindMapXBlock(runtime, element) {
    const mind = {
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

    const options = {
        container: 'jsmind_container',
        editable: true,
        theme: 'asphalt',
    };

    const jm = new jsMind(options);
    jm.show(mind);
}
