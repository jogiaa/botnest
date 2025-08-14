from io import StringIO

from ruamel.yaml import YAML


def load_yaml_instructions(filepath) -> str | None:
    """
    Loads a YAML file using ruamel.yaml to preserve its original structure,
    including comments and formatting, for direct use as agent instructions.
    """
    yaml_loader = YAML()
    try:
        with open(filepath, 'r', encoding='utf-8') as file:
            # .load() returns CommentedMap/CommentedSeq objects
            instructions = yaml_loader.load(file)
        print(f"YAML instructions from '{filepath}' loaded, preserving structure.")
        string_stream = StringIO()
        yaml_loader.dump(instructions, string_stream)
        return string_stream.getvalue()
    except Exception as e:
        print(f"Error loading YAML instructions from '{filepath}': {e}")
        return None


# --- How your agent might use these instructions ---
if __name__ == "__main__":

    # Load the instructions
    agent_instructions = load_yaml_instructions('../experiments/extras/documentation_instructions.yaml')

    if agent_instructions:
        print("\n--- Raw (structured) instructions object ---")
        # This will print the ruamel.yaml object, showing its special type
        print(type(agent_instructions))
        print(agent_instructions)

        print("\n--- Accessing specific instructions (like a dict, but with structure) ---")
        # print(f"Agent Name: {agent_instructions['agent_name']}")
        # print(f"Version: {agent_instructions['version']}")
        # print(f"First Language Supported: {agent_instructions['language_support'][0]}")
        #
        # print("\n--- Iterating through behavior steps and accessing comments ---")
        # ruamel.yaml allows you to access comments directly
        # For top-level comments or comments on sequences, you might access .ca (comment attribute)
        # For comments associated with keys in a map, they might be accessible via specific methods

        # Accessing comments is more advanced with ruamel.yaml, often done
        # when you want to *modify* and dump back.
        # For reading instructions, you're usually interested in the data values.

        # Example of accessing the 'description' for an action:
        # for behavior_step in agent_instructions['behavior']:
        #     action_name = behavior_step['action']
        #     description = behavior_step['description']
        #     print(f"Action: {action_name}")
        #     print(f"  Description:\n{description}")

        # print(f"\nStrict Compliance for add_docstrings: {agent_instructions['behavior'][1]['strict_compliance']}")
        # print(f"Output Format Instruction: {agent_instructions['output_format']}")
        # yaml_loader = YAML()
        # # If you wanted to *dump* it back, preserving comments:
        #
        # string_stream = StringIO()
        # yaml_loader.dump(agent_instructions, string_stream)
        # print("\n--- Instructions dumped back (preserving comments) ---")
        # print(string_stream.getvalue())
