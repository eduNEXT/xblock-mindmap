function MindMapXBlock(runtime, element) {
    var mind = {
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

    var options = {
        container: 'jsmind_container',
        editable: true,
        theme: 'asphalt',
    };

    var jm = new jsMind(options);
    jm.show(mind);

    function saveMindMap() {
        const jsonData = jm.get_data('node_array');
        const data = JSON.stringify(jsonData);
        console.log(data);
    }

    const saveButton = document.getElementById('save');
    saveButton.addEventListener('click', saveMindMap);
}
