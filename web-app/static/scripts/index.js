import {App} from "./app.js";
import {Model} from "./model.js";
import {Store} from "./store.js";
import {initializeSockets, submitDocumentationRequest} from "./socket.js";

// wait for the window to load DOM to initialize the app
window.addEventListener("load", () => {
    initializeSockets({
        onConnect: () => {
            // Optional: indicate connection success in UI
            console.log("Custom onConnect handler triggered");
        },
        onProgress: (message) => {
            App.notifyDocumentationProgress(message);
        },
        onResult: (result) => {
            App.notifyDocumentationComplete(result);
        },
    });

    // Initialize App
    App.init({
        availableModels: Model.$.availableModels,
        documenterModes: Model.$.documenterModes,
        modeConfig: Model.$.modeConfig,
        onModelChanged: (modelId) => {
            Store.updateState({model: modelId});
        },
        onDocumenterModeChanged: (modeId) => {
            Store.updateState({mode: modeId});
        },
        onPathUpdated: (inputSource, inputDestination) => {
            Store.updateState({source: inputSource, destination: inputDestination});
        },
        onFormSubmitted: () => {
            if (Store.isValid()) {
                App.notifyDocumentationRequested();
                const currentState = Store.state;
                submitDocumentationRequest({
                    src: `${currentState.source}`,
                    dst: `${currentState.destination}`,
                    model: `${currentState.model}`,
                    mode: `${currentState.mode}`,
                });
            } else {
                App.notifyDocumentationRequestFailed();
            }
        },
    });
});
