from typing import Dict, Callable

from flask import Flask, render_template
from flask_socketio import SocketIO, emit

from poc_agno import (DocumentationWorkflow, SingleFileDocumentationWorkflow, SummarizerWorkflow,
                      CombinedSummarizedDocumentationWorkflow, set_llm_model)

# Initialize the Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'local_secret'
socketio = SocketIO(app)


@app.route("/")
def hello_world():
    return render_template('app.html')


@socketio.on("document")
def document_code(json):
    source = json.get('src')
    destination = json.get('dst')
    model = json.get('model')
    mode = json.get('mode')
    start_documenting_code(source, destination, model, mode)


def start_documenting_code(
        source,
        destination,
        model,
        mode,
):
    set_llm_model(model)

    match mode:
        case "file_documenter":
            print("Mode is File Documenter. Running file documentation logic...")
            workflow = SingleFileDocumentationWorkflow(logger=SocketLogger())
        case "folder_documenter":
            print("Mode is Folder Documenter. Running folder documentation logic...")
            workflow = DocumentationWorkflow(logger=SocketLogger())
        case "summarizer":
            print("Mode is Summarizer. Running summarizer logic...")
            workflow = SummarizerWorkflow(logger=SocketLogger())
        case "summarizer_documenter":
            print("Mode is Summarizing Documenter. Running logic...")
            workflow = CombinedSummarizedDocumentationWorkflow(logger=SocketLogger())
        case _:
            workflow = CombinedSummarizedDocumentationWorkflow(logger=SocketLogger())

    try:
        result = workflow.run(
            source_file_path=source,
            destination_file_path=destination,
        )
        emit('result', {'result': "passed", 'content': result})
    except Exception as e:
        emit('result', {'result': "failed", 'content': f'Failed: {e}'})


class SocketLogger:
    def info(self, msg, *args, **kwargs) -> None:
        emit('progress', msg + "\n")

    def error(self, msg: str) -> None:
        emit('progress', msg + "\n")

    def warning(self, msg, *args, **kwargs) -> None:
        emit('progress', msg + "\n")

    def critical(self, msg, *args, **kwargs) -> None:
        emit('progress', msg + "\n")

    def debug(self, msg, *args, **kwargs) -> None:
        emit('progress', msg + "\n")


if __name__ == "__main__":
    socketio.run(app, debug=True)
