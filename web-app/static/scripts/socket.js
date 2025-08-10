import {io} from "https://cdn.socket.io/4.7.2/socket.io.esm.min.js";

export const socket = io();

export function initializeSockets(
    {
        onConnect = () => { },
        onProgress = (msg) => { },
        onResult = (msg) => { }
    }
) {
    socket.on("connect", () => {
        console.log("Connected to server via Socket.IO");
        onConnect();
    });

    socket.on("progress", (msg) => {
        console.log(`Got progress ${msg}`);
        onProgress(msg);
    });

    socket.on("result", (msg) => {
        console.log(`Finished result ${msg}`);
        onResult(msg);
    });
}

export function submitDocumentationRequest(data) {
    socket.emit("document", data);
}
