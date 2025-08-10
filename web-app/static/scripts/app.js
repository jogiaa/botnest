// create App namespace
export const App = {
    $: {
        form: document.getElementById("operation-form"),

        // user input elements
        modelDropdown: document.getElementById("model_selection"),
        documentorModeDropdown: document.getElementById("documenter_mode_selection"),

        sourceFolderInput: document.getElementById("source_folder_input"),
        sourceLabel: document.getElementById("source-label"),
        sourceHelpText: document.getElementById("source-help-text"),

        destinationFolderInput: document.getElementById("destination_folder"),
        destinationLabel: document.getElementById("destination-label"),

        submitButton: document.getElementById("submit-button"),

        // result and progress
        progressContainer: document.getElementById("progress-container"),
        progressLog: document.getElementById("progress-log"),

        resultContainer: document.getElementById("result-container"),
        resultText: document.getElementById("result-text"),
    },

    init(
        {
            availableModels,
            documenterModes,
            modeConfig,
            onModelChanged = (model) => { },
            onDocumenterModeChanged = (mode) => { },
            onPathUpdated = (source, destination) => { },
            onFormSubmitted = () => { },
        }
    ) {
        // initialize dropdown
        App.populateDropDown(App.$.modelDropdown, availableModels);
        App.populateDropDown(App.$.documentorModeDropdown, documenterModes);

        // Set initial UI on page load
        App.updateForm(modeConfig[App.$.documentorModeDropdown.value]);

        // Set initial user selection
        onModelChanged(App.$.modelDropdown.value);
        onDocumenterModeChanged(App.$.documentorModeDropdown.value);

        // add actions
        App.registerEventListeners(
            modeConfig,
            onModelChanged,
            onDocumenterModeChanged,
            onPathUpdated,
            onFormSubmitted
        );
    },

    registerEventListeners(
        modeConfig,
        onModelChanged = (model) => {
        },
        onDocumenterModeChanged = (mode) => {
        },
        onPathUpdated = (source, destination) => {
        },
        onFormSubmitted = () => {
        }
    ) {
        App.$.modelDropdown.addEventListener("change", (event) => {
            const model = event.target.value;
            onModelChanged(model);
        });

        App.$.documentorModeDropdown.addEventListener("change", (event) => {
            const mode = event.target.value;

            // update UI
            App.updateForm(modeConfig[mode]);

            // reset inputs
            App.$.sourceFolderInput.value = "";
            App.$.destinationFolderInput.value = "";

            // inform selection update
            onDocumenterModeChanged(mode);
        });

        App.$.sourceFolderInput.addEventListener("input", (event) => {
            const sourcePath = event.target.value.trim();
            if (sourcePath) {
                const destinationPath = sourcePath + "_documented";
                App.$.destinationFolderInput.value = destinationPath;
                onPathUpdated(sourcePath, destinationPath);
            } else {
                App.$.destinationFolderInput.value = "";
                onPathUpdated("", "");
            }
        });

        App.$.form.addEventListener("submit", (event) => {
            event.preventDefault(); // Prevent the default form submission
            onFormSubmitted();
        });
    },

    populateDropDown(dropdown, options) {
        dropdown.innerHTML = "";
        options.forEach((choice) => {
            const option = document.createElement("option");
            option.value = choice.id;
            option.textContent = choice.displayName;
            dropdown.appendChild(option);
        });
    },

    updateForm(config) {
        App.$.sourceLabel.textContent = config.sourceLabel;
        App.$.sourceHelpText.textContent = config.sourceHelpText;
        App.$.sourceFolderInput.placeholder = config.sourcePlaceholder;
        App.$.destinationLabel.textContent = config.destinationLabel;
    },

    notifyDocumentationRequestFailed(
        message = "Please select a source folder first."
    ) {
        alert(message);
    },

    notifyDocumentationRequested(message = "Processing ...") {
        App.$.submitButton.disabled = true;
        App.$.submitButton.textContent = message;

        // Reset result area
        App.$.resultText.textContent = "";
        App.$.resultText.className = ""; // optional: clear previous color classes
        App.$.resultContainer.classList.add("hidden");

        // Reset progress area
        App.$.progressContainer.classList.remove("hidden");
        App.$.progressLog.textContent = "";
        App.$.progressLog.parentElement.scrollTop = 0;
    },

    notifyDocumentationProgress(message) {
        const progressLog = App.$.progressLog;
        progressLog.textContent += message;
        progressLog.parentElement.scrollTop =
            progressLog.parentElement.scrollHeight;
    },

    notifyDocumentationComplete(message) {
        const result = message.result;
        const resultText = App.$.resultText;
        resultText.innerHTML = `Status: ${result}<br>Message: ${message.content}`;
        if (result === 'Passed') {
            resultText.className = 'text-md font-medium text-green-600';
        } else {
            resultText.className = 'text-md font-medium text-red-600';
        }
        App.$.resultContainer.classList.remove('hidden');

        // Re-enable the button
        App.$.submitButton.disabled = false;
        App.$.submitButton.textContent = 'Begin Operation';
    },
};
