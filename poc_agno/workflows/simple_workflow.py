from logging import Logger
from pathlib import Path
from pprint import pprint
from typing import Optional

from agno.run.response import RunResponse
from agno.workflow.v2 import Workflow

from poc_agno.tools.another_file_reader import AnotherFileProcessor, FileError
from poc_agno.utils import get_builtin_logger


class SummarizerWorkflow(Workflow):
    def __init__(self, logger: Optional[Logger] = None):
        super().__init__()
        self.logger = logger if logger is not None else get_builtin_logger()

    description: str = "Sequential code accumulator workflow"

    _number_of_files = 0

    def run(self, source_file_path: str) -> RunResponse:
        self.logger.info(f"Starting file summarizing workflow")
        self.logger.info(f"Source: {source_file_path}")

        file_processor = AnotherFileProcessor(logger=self.logger, source_str=source_file_path)

        # Step 1: Read the file
        self.logger.debug("☞ Step 1: Reading source file...")

        for streamed_file in file_processor.stream_files():
            if isinstance(streamed_file, FileError):
                self.logger.error(f"<UNK> File error: {streamed_file}")
                continue

            self.logger.debug(f"✅ File read successfully: {streamed_file.path} ")
            org_file_content = streamed_file.content

            self.logger.info(org_file_content)

            self._number_of_files += 1

        return RunResponse(
            content={
                "workflow_summary": {
                    "work_flow_finished": True,
                    "number_of_files_summarized": self._number_of_files
                }
            }
        )

if __name__ == "__main__":
    # Create the workflow
    workflow = SummarizerWorkflow(logger=get_builtin_logger())
    PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
    print(PROJECT_ROOT)

    # Example file paths
    source = "SampleCode/sample-lib/src/main/java/org/jay/sample"

    source_path = str(Path(PROJECT_ROOT / source).absolute())
    print(source_path)
    # Run the workflow
    result = workflow.run(source_file_path=source_path)
    pprint(result)
