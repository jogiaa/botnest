from pathlib import Path
from pprint import pprint
from typing import List, Dict, Any

from agno.agent import Agent
from agno.tools.file import FileTools

from poc_agno.llm_model_config import llm_model


class FileReaderAgent:
    """
    An Agno agent that can read all files in a given path using Agno's file tools.
    """

    def __init__(self, base_path: str = None, show_tool_calls: bool = True):
        """
        Initialize the FileReaderAgent.

        Args:
            base_path: Base directory path for file operations
            show_tool_calls: Whether to show tool calls in output
        """
        self.base_path = Path(base_path) if base_path else Path.cwd()

        # Create FileTools with the specified base directory
        file_tools = FileTools(
            base_dir=self.base_path,
            read_files=True,
            list_files=True,
            save_files=False  # We don't need to save files for reading
        )

        # Create the agent with file tools
        self.agent = Agent(
            model=llm_model,
            tools=[file_tools],
            show_tool_calls=show_tool_calls,
            instructions="""
            You are a file reading assistant. Your job is to help users read files from the specified directory.
            When asked to read all files in a path:
            1. First, list all files in the directory
            2. Then read each file's contents
            3. Provide a summary of what was found

            Be helpful and organize the information clearly for the user.
            """
        )

    def read_all_files(self, path: str = None) -> Dict[str, Any]:
        """
        Read all files in the specified path.

        Args:
            path: Optional path to read files from. If None, uses base_path.

        Returns:
            Dictionary containing file contents and metadata
        """
        target_path = Path(path) if path else self.base_path

        prompt = f"""
        Please read all files in the directory: {target_path}

        Follow these steps:
        1. List all files in the directory recursively
        2. Read the contents of each file
        3. Provide a summary of the files and their contents

        If there are any errors reading specific files, note them but continue with the others.
        """

        response = self.agent.run(prompt)
        return response

    def read_specific_files(self, file_patterns: List[str], path: str = None) -> Dict[str, Any]:
        """
        Read specific files matching given patterns.

        Args:
            file_patterns: List of file patterns/names to read
            path: Optional path to read files from

        Returns:
            Dictionary containing file contents and metadata
        """
        target_path = Path(path) if path else self.base_path

        patterns_str = ", ".join(file_patterns)
        prompt = f"""
        In the directory {target_path}, please:
        1. List all files
        2. Read only the files that match these patterns: {patterns_str}
        3. Provide the contents of the matching files

        File patterns can include wildcards or specific filenames.
        """

        response = self.agent.run(prompt)
        return response

    def get_file_summary(self, path: str = None) -> Dict[str, Any]:
        """
        Get a summary of all files in the specified path without reading contents.

        Args:
            path: Optional path to analyze

        Returns:
            Summary information about files
        """
        target_path = Path(path) if path else self.base_path

        prompt = f"""
        Please provide a summary of all files in the directory: {target_path}

        Just list the files with basic information like:
        - File names
        - File types/extensions
        - Count of different file types

        Do not read the file contents, just provide the directory listing and summary.
        """

        response = self.agent.run(prompt)
        return response


# Example usage and helper functions
def create_file_reader_agent(path: str) -> FileReaderAgent:
    """
    Convenience function to create a FileReaderAgent for a specific path.

    Args:
        path: Directory path to read files from

    Returns:
        Configured FileReaderAgent instance
    """
    return FileReaderAgent(base_path=path)


def main():
    """
    Example usage of the FileReaderAgent
    """
    # Example 1: Create agent for current directory
    print("=== Example 1: Reading files from current directory ===")
    agent = FileReaderAgent()

    # Get file summary first
    print("Getting file summary...")
    summary = agent.get_file_summary()
    print(f"Summary response: {summary}")

    # Read all files
    print("\nReading all files...")
    all_files = agent.read_all_files()
    print(f"All files response: {all_files}")

    # Example 2: Create agent for specific directory
    print("\n=== Example 2: Reading files from specific directory ===")
    specific_path = "/Users/asim/Documents/DEV/botnest/SampleCode"  # Change this to your desired path

    try:
        agent2 = FileReaderAgent(base_path=specific_path)

        # Read only Python files
        python_files = agent2.read_specific_files(["*.kt"])
        pprint(f"Python files response: {python_files}")

    except Exception as e:
        print(f"Could not access {specific_path}: {e}")
        print("Using current directory instead...")

        # Fallback to current directory
        agent2 = FileReaderAgent()
        files = agent2.read_specific_files(["*.*"])
        print(f"Text/Markdown/Python files response: {files}")


if __name__ == "__main__":
    main()
