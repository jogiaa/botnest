from agno.run.response import RunResponse
from agno.tools.file import FileTools
from agno.utils.log import logger
from agno.workflow import Workflow

from poc_agno.agents.code_documenter import code_doc_agent, DocumentedResult


class SingleFileDocumentationWorkflow(Workflow):
    description: str = "Sequential file processing workflow: read → capitalize → save"

    def run(self, source_file_path: str, destination_file_path: str) -> RunResponse:
        """
        Execute the three-agent workflow:
        1. File Reader → reads the source file
        2. Add documentation to the code
        3. File Saver → saves to destination path
        """
        logger.info(f"Starting file processing workflow")
        logger.info(f"Source: {source_file_path}")
        logger.info(f"Destination: {destination_file_path}")
        file_tools = FileTools()
        # Step 1: Read the file
        logger.info("Step 1: Reading source file...")
        org_file_content = file_tools.read_file(source_file_path)

        if org_file_content.__contains__("Error"):
            return RunResponse(
                content=f"Failed to read file from {source_file_path}"
            )

        logger.info(f"✅ File read successfully. content: {org_file_content}")

        # Step 2: Capitalize the content
        logger.info("Step 2: Adding comments...")

        comment_response = code_doc_agent.run(org_file_content)

        if not comment_response.content or not isinstance(comment_response.content, DocumentedResult):
            return RunResponse(
                content="Failed to add comment file content"
            )

        comment_result = comment_response.content

        if not comment_result.modified_code:
            return RunResponse(
                content="Failed to add comment file content"
            )

        logger.info(f"✅ Comments added.")

        # Step 3: Save the capitalized content
        logger.info("Step 3: Saving to destination file...")

        save_response = file_tools.save_file(
            file_name=destination_file_path,
            contents=comment_result.modified_code)

        if not save_response or save_response.__contains__("Error"):
            return RunResponse(
                content="Failed to save file"
            )

        logger.info(f"✅ File saved successfully to {save_response}")

        # Return a summary of the entire workflow
        return RunResponse(
            content={
                "workflow_summary": {
                    "all_good": True
                }
            }
        )


if __name__ == "__main__":
    # Create the workflow
    workflow = SingleFileDocumentationWorkflow()

    # Example file paths
    source_path = "test.py"
    destination_path = "output_test.py"

    # Run the workflow
    result = workflow.run(source_file_path=source_path, destination_file_path=destination_path)
    print(result.content)
