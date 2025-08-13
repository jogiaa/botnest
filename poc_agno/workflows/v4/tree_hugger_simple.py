import os
from collections import defaultdict
from typing import Dict, List, Any

import tree_sitter_kotlin
from tree_sitter import Language, Parser, Node, Query, QueryCursor

try:
    KOTLIN_LANGUAGE = Language(tree_sitter_kotlin.language())
except Exception as e:
    print(
        f"Failed to build tree-sitter-kotlin grammar. Please ensure `tree-sitter` and the grammar are installed. Error: {e}")
    KOTLIN_LANGUAGE = None


def get_parser() -> Parser:
    """Returns a configured tree-sitter parser for Kotlin."""
    parser = Parser()
    parser.language = KOTLIN_LANGUAGE
    return parser


def analyze_kotlin_file(file_path: str, source_bytes: bytes) -> List[Dict[str, Any]]:
    """
    Parses a single Kotlin file and extracts high-level information
    about its declarations using tree-sitter.
    """
    if not KOTLIN_LANGUAGE:
        return []

    parser = get_parser()
    tree = parser.parse(source_bytes)
    declarations = []
    root_node = tree.root_node
    # First, let's debug the actual structure
    # print("-" * 15)
    # print(str(source_bytes))
    # print("-" * 15)
    print("=== DEBUGGING TREE STRUCTURE ===")
    debug_tree_structure_detailed(root_node, str(source_bytes))
    print("=== END DEBUG ===\n")

    find_package_name(root_node)

    return declarations


def find_package_name(root_node: Node) -> str:

    query_patterns = [
        # Pattern 1: Direct qualified_identifier from package_header
        """
        (package_header
          (qualified_identifier) @package_name)
        """,

        # Pattern 2: More specific - capture the qualified_identifier text
        # """
        # (source_file
        #   (package_header
        #     (qualified_identifier) @package_name))
        # """,

        # Pattern 3: Alternative structure matching
        # """
        # (package_header
        #   (package)
        #   (qualified_identifier) @package_name)
        # """,

        # Pattern 4: Capture any qualified_identifier in package context
        # """
        # (package_header
        #   (_)
        #   (qualified_identifier) @package_name)
        # """,
        # """
        # (qualified_identifier) @name
        # """
    ]

    for i, pattern in enumerate(query_patterns):
        try:
            print("*" * 15)
            print(f"Trying query pattern {i + 1}: {pattern.strip()}")
            query = Query(KOTLIN_LANGUAGE, pattern)
            cursor = QueryCursor(query)

            # Use the correct method to get captures
            # Try different methods that might be available
            matches = cursor.matches(root_node)

            for match in matches:
                # print(type(match))
                # pprint(match)
                captures_dict = match[1]
                if "package_name" in captures_dict:
                    nodes = captures_dict["package_name"]
                    if nodes and len(nodes) > 0:
                        # Return the first match
                        return nodes[0].text.decode("utf-8")
                # print(type(node))
                # for key, value in node.items():
                #     print(f"{key} = {value}")
                #     print(type(value))
                #     for item in value:
                #         print(type(item))
                #         print(item)
                #         return item.text.decode("utf-8")

            # print("-^-" * 30)
            # captures = cursor.captures(root_node)
            # for capture in captures:
            #     print(type(capture))
            #     pprint(capture)
            # print("-*-" * 30)
            # for capture in match.captures:
            #     capture_name = query.capture_names[capture[1]]
            #     node = capture[0]
            #     text = node.text.decode("utf-8") if node.text else ""
            #
            #     print(f"Found qualified_identifier: '{text}'")
            #
            #     # Check if this qualified_identifier is in a package_header
            #     parent = node.parent
            #     if parent and parent.type == "package_header":
            #         print(f"  -> This is in a package_header, using as package name")
            #         return text.strip()
            #     else:
            #         print(f"  -> This is not in package_header (parent: {parent.type if parent else 'None'})")


        except Exception as e:
            print(f"  Query failed---->: {e}")
            continue

    return None


def analyze_kotlin_codebase(root_path: str):
    """
    Main function to analyze a Kotlin codebase using a two-pass approach.
    """
    analysis_results = []
    class_map = {}
    usage_map = defaultdict(list)

    # Pass 1: Collect all declarations and their dependencies
    for dirpath, _, filenames in os.walk(root_path):
        for filename in filenames:
            print(f"Analyzing {filename}")
            if filename.endswith('.kt'):
                file_path = os.path.join(dirpath, filename)
                try:
                    with open(file_path, 'rb') as f:
                        source_bytes = f.read()

                    declarations_in_file = analyze_kotlin_file(file_path, source_bytes)
                except Exception as e:
                    print(f"Error processing file {file_path}: {e}")


def debug_tree_structure_detailed(root_node, kotlin_code: str) -> None:
    """
    Detailed debugging to show tree structure with line/column info.
    """
    lines = kotlin_code.split('\n')

    def print_node_detailed(node: Node, depth: int = 0) -> None:
        indent = "  " * depth
        text = node.text.decode("utf-8") if node.text else ""

        # Show position info
        start_row, start_col = node.start_point
        end_row, end_col = node.end_point

        # Get the actual text from source for better readability
        if start_row < len(lines):
            line_text = lines[start_row].strip()
            print(
                f"{indent}{node.type} [{start_row}:{start_col}-{end_row}:{end_col}] '{text[:50]}{'...' if len(text) > 50 else ''}' | Line: '{line_text}'")
        else:
            print(
                f"{indent}{node.type} [{start_row}:{start_col}-{end_row}:{end_col}] '{text[:50]}{'...' if len(text) > 50 else ''}'")

        # Only show first few levels to avoid spam
        if depth < 4:
            for child in node.children:
                print_node_detailed(child, depth + 1)

    print_node_detailed(root_node)


def run_():
    analyze_kotlin_codebase("mock_kotlin_project_advanced")


if __name__ == "__main__":
    run_()
