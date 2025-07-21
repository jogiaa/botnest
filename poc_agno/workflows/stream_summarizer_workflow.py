from dataclasses import dataclass, asdict
from string import Template
from typing import Iterator

from agno.run.response import RunResponse
from agno.utils.log import logger
from agno.workflow import Workflow

from poc_agno.agents.code_summary_agent import code_summary_agent
from poc_agno.memory.chroma_code_context import store_result
from poc_agno.tools.another_file_reader import AnotherFileProcessor, FileError


@dataclass
class SummarizerStatus:
    status: str
    source: str
    message: str = ""
    file_processed: str = ""
    file_summary: str = ""
    contextual_summary: str = ""
    files_processed_so_far: int = 0


STATUS_EVENT_STARTED = "STARTED"
STATUS_EVENT_IN_PROGRESS = "IN_PROGRESS"
STATUS_EVENT_COMPLETED = "COMPLETED"
STATUS_EVENT_ERROR = "ERROR"


class StreamSummarizerWorkflow(Workflow):
    description: str = "Sequential file summarizing workflow: read → summarize → updateChroma"

    contextual_summary = ""
    number_of_files = 0

    prompt_template = Template("""
        Current summary so far: $current_summary \n\n
        Update the summary to include the following file: $file_path \n\n 
        With content
        ```
        $content_code
        ```
    """)

    def run(self, source_file_path: str) -> Iterator[RunResponse]:

        STATUS_CATEGORY_FAILED = "FAILED"
        STATUS_CATEGORY_SKIPPED = "SKIPPED"
        STATUS_CATEGORY_FILE_PROCESSED = "FILE_PROCESSED"

        logger.info(f"Starting file summarizing workflow")
        logger.info(f"Source: {source_file_path}")

        yield RunResponse(
            run_id=self.run_id,
            content=asdict(SummarizerStatus(
                status=STATUS_EVENT_STARTED,
                source=source_file_path,
            ))
        )

        file_processor = AnotherFileProcessor(source_str=source_file_path)

        # Step 1: Read the file
        logger.info("Step 1: Reading source file...")

        yield RunResponse(
            run_id=self.run_id,
            content=asdict(
                SummarizerStatus(
                    status=STATUS_EVENT_IN_PROGRESS,
                    source=source_file_path,
                    message="☞ Step 1: Reading source file(s)..."
                )
            )
        )

        for streamed_file in file_processor.stream_files():
            if isinstance(streamed_file, FileError):
                logger.info(f"<UNK> File error: {streamed_file}")
                yield RunResponse(
                    run_id=self.run_id,
                    content=asdict(
                        SummarizerStatus(
                            status=STATUS_EVENT_ERROR,
                            source=source_file_path,
                            file_processed=streamed_file.path,
                            message=f"❌File error: {streamed_file}"
                        )
                    )
                )
                continue

            logger.info(f"File read successfully: {streamed_file.path} ")

            yield RunResponse(
                run_id=self.run_id,
                content=asdict(
                    SummarizerStatus(
                        status=STATUS_EVENT_IN_PROGRESS,
                        source=source_file_path,
                        file_processed=streamed_file.path,
                        message=f"✅ File read successfully: {streamed_file.path} "
                    )
                )
            )

            org_file_content = streamed_file.content

            # Step 2: Summarizing the content
            logger.info("Step 2: Summarizing file...")

            yield RunResponse(
                run_id=self.run_id,
                content=asdict(
                    SummarizerStatus(
                        status=STATUS_EVENT_IN_PROGRESS,
                        source=source_file_path,
                        file_processed=streamed_file.path,
                        message="☞ Step 2: Summarizing file..."
                    )
                )
            )

            prompt = self.prompt_template.substitute(
                current_summary=self.contextual_summary,
                file_path=streamed_file.path,
                content_code=org_file_content
            )

            # pprint("❤️ " + prompt)

            response = code_summary_agent.run(prompt)

            # pprint(f"☠️☠️☠️The response we got is ${response}")

            logger.info(f"Code summarized.")

            self.contextual_summary = self.contextual_summary + response.content
            # logger.info(response.content)

            store_result(
                data_content=response.content,
                data_path=streamed_file.path
            )
            self.number_of_files += 1

            yield RunResponse(
                run_id=self.run_id,
                content=asdict(
                    SummarizerStatus(
                        status=STATUS_EVENT_IN_PROGRESS,
                        source=source_file_path,
                        file_processed=streamed_file.path,
                        message=f"✅ Code summarized.",
                        files_processed_so_far=self.number_of_files
                    )
                )
            )

        # Return a summary of the entire workflow
        # pprint(self.contextual_summary)

        yield RunResponse(
            run_id=self.run_id,
            content={
                "status": STATUS_EVENT_COMPLETED,
                "message": f"✅ Summary completed. Total files processed: {self.number_of_files}",
                "workflow_summary": {
                    "work_flow_finished": True,
                    "number_of_files_summarized": self.number_of_files
                }
            }
        )


if __name__ == "__main__":
    # Create the workflow
    workflow = StreamSummarizerWorkflow()

    # Example file paths
    source = "koin/examples/coffee-maker"

    # Run the workflow
    # result = workflow.run(source_file_path=source)

    for result in workflow.run(source_file_path=source):
        print(f"Status: {result.content['status']}")
        if result.content['status'] == STATUS_EVENT_IN_PROGRESS:
            file_path = result.content.get("file_path")
            message = result.content.get("message", "Unknown")

            print(f"Progress: {file_path or message}")

        elif result.content['status'] == STATUS_EVENT_ERROR:
            print(f"Failed to read  {result.content['file_path']}\n\n  {result.content['message']}\n")
        elif result.content['status'] == STATUS_EVENT_COMPLETED:
            print(f"Total files: {result.content['workflow_summary']['number_of_files_summarized']}")
