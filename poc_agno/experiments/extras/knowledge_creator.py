from logging import Logger
from pathlib import Path
from pprint import pprint
from textwrap import dedent

from agno.workflow.v2 import StepInput, StepOutput

from poc_agno.memory.chroma_code_context import store_result, knowledge_collection
from poc_agno.tools.another_file_reader import AnotherFileProcessor, FileError
from poc_agno.utils import get_builtin_logger


def knowledge_collector(logger: Logger, step_input: StepInput) -> StepOutput:
    source_file_path = step_input.message
    number_of_files = 0
    logger.info(f"Starting file summarizing workflow")
    logger.info(f"Source: {source_file_path}")

    file_processor = AnotherFileProcessor(logger=logger, source_str=source_file_path)

    # Step 1: Read the file
    logger.debug("☞ Reading source file...")

    for streamed_file in file_processor.stream_files():
        if isinstance(streamed_file, FileError):
            logger.error(f"<UNK> File error: {streamed_file}")
            continue

        logger.debug(f"✅ File read successfully: {streamed_file.path} ")

        org_file_content = f"\n=========================================\n"
        org_file_content += f"{streamed_file.rel_path}\n"
        org_file_content += f"=========================================\n"
        org_file_content += f"{streamed_file.content}"
        org_file_content += f"\n\n"

        logger.debug(org_file_content)

        store_result(data_content=org_file_content,
                     data_path=streamed_file.path,
                     collection=knowledge_collection,
                     metadata=[
                         {
                             "file_path": streamed_file.rel_path,
                             "doc_type": "code",
                         }
                     ]
                     )

        number_of_files += 1

    return StepOutput(
        content=dedent(f"""
            Total files processed: {number_of_files}
            Knowledge Base Created: True
            """)
    )


if __name__ == "__main__":
    PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
    print(f"Root : {PROJECT_ROOT}")

    # Example file paths
    source = "SampleCode/sample-lib/src/main/java/org/jay/sample"

    source_path = str(Path(PROJECT_ROOT / source).absolute())

    pprint(knowledge_collector(get_builtin_logger(), StepInput(message=source_path)))
