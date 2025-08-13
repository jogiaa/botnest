import os
from collections import defaultdict
from dataclasses import dataclass, field
from pprint import pprint
from typing import Dict, List, Any

import tree_sitter_kotlin
from tree_sitter import Language, Parser, Node, Query, QueryCursor


@dataclass
class KotlinAnalysis:
    """Data class to hold all extracted information."""
    package_name: str = ""
    imports: List[str] = field(default_factory=list)
    classes: List[Dict] = field(default_factory=list)
    functions: List[Dict] = field(default_factory=list)
    interfaces: List[Dict] = field(default_factory=list)
    objects: List[Dict] = field(default_factory=list)


@dataclass
class KotlinAnalysis2:
    """Data class to hold all extracted information."""
    filename: str = ""
    package_name: str = ""
    imports: List[str] = field(default_factory=list)
    name: str = ""
    type: str = ""  # class or interface or data class or enum or object
    visibility: str = ""  # private | internal | public
    functions: List[Dict] = field(
        default_factory=list)  # only filled where applicable. But it would contain something like [ {'name':'aFunctionName' , 'modifier':'private|public|internal' , 'params':[{'firstParam':'Int','secondParam':'User'}],'return':'Unit|Int|or whatever'} ,
    uses: List[str] = field(default_factory=list)  # User
    used_by: List[str] = field(default_factory=list)  # other classes using this


# comprehensive_query = """
#     ; Package declaration
#     (package_header (qualified_identifier) @package)
#
#     ; Import statements
#     (import (qualified_identifier) @import)
#
#     ; Class declarations with modifiers and constructors
#     (class_declaration
#       (modifiers)? @class_modifiers
#       (identifier) @class_name
#       (primary_constructor
#         (class_parameters
#           (class_parameter
#             (modifiers)? @param_modifiers
#             (identifier) @param_name
#             (user_type (type_identifier) @param_type)?
#           )*
#         )
#       )? @class_constructor
#       (class_body)? @class_body
#     ) @class_declaration
#
#     ; Interface declarations
#     (interface_declaration
#       (modifiers)? @interface_modifiers
#       (identifier) @interface_name
#     ) @interface_declaration
#
#     ; Object declarations
#     (object_declaration
#       (modifiers)? @object_modifiers
#       (identifier) @object_name
#     ) @object_declaration
#
#     ; Function declarations
#     (function_declaration
#       (modifiers)? @function_modifiers
#       (identifier) @function_name
#       (function_value_parameters
#         (function_parameter
#           (identifier) @function_param_name
#           (user_type (type_identifier) @function_param_type)?
#         )*
#       )? @function_params
#       (user_type (type_identifier) @function_return_type)?
#     ) @function_declaration
#
#     ; Property declarations
#     (property_declaration
#       (modifiers)? @property_modifiers
#       (identifier) @property_name
#       (user_type (type_identifier) @property_type)?
#     ) @property_declaration
#     """
#
comprehensive_query = """
    ; Package declaration
    (package_header (qualified_identifier) @package)

    ; Import statements
    (import (qualified_identifier) @import)

    ; Class declarations with modifiers and constructors
    (class_declaration
        (modifiers)? @class_modifiers
        (identifier) @class_name
        (primary_constructor
            (class_parameters
                (class_parameter
                    (modifiers)? @param_modifiers
                    (identifier) @param_name
                    (type (qualified_identifier) @param_type)?
                )*
            )
        )? @class.constructor
        (class_body
            (class_member_declaration
                (function_declaration
                    (modifiers)? @function_modifiers
                    (identifier) @function_name
                ) @class.member_function
            )?
        )?
    )@class_declaration
    """

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
    parser = get_parser()
    tree = parser.parse(source_bytes)
    declarations = []
    root_node = tree.root_node
    print("=== DEBUGGING TREE STRUCTURE ===")
    print_tree(source_bytes=source_bytes)
    print("=== END DEBUG ===\n")

    complete_analysis = analyze_it(root_node)

    pprint(complete_analysis)

    return declarations


def analyze_it(root_node: Node) -> KotlinAnalysis:
    analysis = KotlinAnalysis2()
    try:
        query = Query(KOTLIN_LANGUAGE, comprehensive_query)
        cursor = QueryCursor(query)
        matches = cursor.matches(root_node)

        for index, match in enumerate(matches):
            pprint(f"{index}: {match}")
            captures_dict = match[1]
            if "import" in captures_dict:
                analysis.imports.append(extract_imports(captures_dict, index))
            if "package" in captures_dict:
                analysis.package_name = extract_package_name(captures_dict, index)
            if "class_declaration" in captures_dict:
                class_name = _get_node_text(captures_dict["class_name"][0])
                class_modifiers = "public" if "class_modifiers" not in captures_dict \
                    else _get_node_text(captures_dict["class_modifiers"][0])

                print(f"{index}: Name: {class_name} class_modifiers: {class_modifiers}")
                print(f"param_modifiers :: {_get_node_text(captures_dict['class.constructor'][0])}")
                analysis.type = "class"
                analysis.name = class_name
                analysis.visibility = class_modifiers if class_modifiers != "" else "public"

    except Exception as err:
        print("*" * 4 + "ERROR" + "*" * 4)
        print(err)
        print("*" * 4 + "ERROR" + "*" * 4)

    return analysis


def extract_imports(captures_dict, index):
    if "import" in captures_dict:
        import_name = _get_node_text(captures_dict["import"][0])
        print(f"{index}: Import: {import_name}")
        return import_name
    else:
        return ""


def _get_node_text(node) -> str:
    """Get text content of a node."""
    return node.text.decode('utf-8') if node else ""


def extract_package_name(captures_dict, index) -> str:
    if "package" in captures_dict:
        package_name = _get_node_text(captures_dict["package"][0])
        print(f"{index}: Package: {package_name}")
        return package_name
    else:
        return ""


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
# Debug helpers
def print_tree(source_bytes: bytes, node=None, indent=0, max_lines=2000):
    """Recursively print node types and text (useful to find exact node names in your grammar)."""
    if node is None:
        tree = get_parser().parse(source_bytes)
        node = tree.root_node

    prefix = "  " * indent
    text = node_text(source_bytes, node).strip().splitlines()
    sample = text[0][:80] + ("..." if len(text[0]) > 80 else "") if text else ""
    print(f"{prefix}{node.type} [{node.start_point}..{node.end_point}] -- {sample}")
    for child in node.children:
        print_tree(source_bytes, child, indent + 1)

def node_text(source_bytes: bytes, node) -> str:
    return source_bytes[node.start_byte:node.end_byte].decode("utf-8")

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
                f"{indent}{node.type} [{start_row}:{start_col}-{end_row}:{end_col}] '{text} | Line: '{line_text}'")
        else:
            print(
                f"{indent}{node.type} [{start_row}:{start_col}-{end_row}:{end_col}] '{text}'")

        # Only show first few levels to avoid spam
        if depth < 4:
            for child in node.children:
                print_node_detailed(child, depth + 1)

    print_node_detailed(root_node)


def run_():
    analyze_kotlin_codebase("mock_kotlin_project_advanced")


if __name__ == "__main__":
    run_()
