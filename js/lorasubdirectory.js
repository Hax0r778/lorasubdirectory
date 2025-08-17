// js/TextOrFile.js

import { app } from "../../scripts/app.js";

app.registerExtension({
    name: "lorasubdirectory",
    async nodeCreated(node) {
        if (node.comfyClass !== "LoraSubdirectory" && node.comfyClass !== "LoraModelOnlySubdirectory") return;

	const other_widgets = [];

        // Locate the primary dropdown widget
        const lora_directory = node.widgets.find(w => w.name === "lora_directory");
		
	// a change to the directory is what will shift the name dropdown
        const origCallback = lora_directory.callback;

        // Override its callback to add/remove inputs on change
        lora_directory.callback = (value) => {
            origCallback?.call(node, value);

	    if (node.widgets.findIndex(w => w.name == value) == -1) {
		if (other_widgets.findIndex(w => w.name == value) !== -1) {
		    // insert in position 1 without deletion to ensure the order is right
		    node.widgets.splice(1, 0, other_widgets.find(w => w.name == value));
		}
	    }
	   
	    // remove any inactive widgets from the node list (and store in the other_widget list for later)
	    var other = node.widgets.filter(w => w.name !== "lora_directory" && w.name !== "strength_model" && w.name !== "strength_clip" && w.name !== value);
	    other.forEach(function(entry) {
		const index = node.widgets.findIndex(w => w.name == entry.name);
		if (index !== -1) {
		    other_widgets.push(node.widgets.splice(index, 1)[0]);
		}
	    });

            // Force a redraw so the UI updates immediately
            node.setDirtyCanvas(true, true);
        };

        // Initialize once on node creation
        lora_directory.callback(lora_directory.value);
    }
});
