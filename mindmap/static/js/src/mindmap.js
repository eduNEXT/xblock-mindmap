function MindMapXBlock(runtime, element) {
    console.log("This is the MindMapXBlock");
    (function () {
        var mind = {
            "meta": {
                "name": "jsMind remote",
                "author": "eduNEXT",
                "version": "0.1"
            },
            "format": "node_array",
            "data": [
                { "id": "root", "isroot": true, "topic": "Root" },
            ]
        };

        var options = {
            container: 'jsmind_container',
            editable: true,
            theme: 'asphalt',
        };

        var jm = new jsMind(options);
        jm.show(mind);
    })();
}
