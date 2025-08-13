import json
import os
from collections import defaultdict
from pprint import pprint
from typing import Dict, List, Any

import tree_sitter_kotlin
from tree_sitter import Language, Parser, Query, Node

# Define the path to the tree-sitter language grammar.
# You need to have the `tree-sitter-kotlin` library compiled first.
# To do so, run the following commands in your terminal:
# 1. git clone https://github.com/tree-sitter/tree-sitter-kotlin
# 2. cd tree-sitter-kotlin
# 3. tree-sitter generate
# 4. python -m tree_sitter generate-language tree-sitter-kotlin
# 5. LANGUAGE = Language('build/my-languages.so', 'kotlin')
#
# For this example, we'll assume a pre-compiled library exists.
# A full, real-world implementation would handle this setup.
try:
    # Language.build_library(
    #     # Store the library in the `build` directory
    #     'build/my-languages.so',
    #     # List of the grammars to compile
    #     ['tree-sitter-kotlin']
    # )
    KOTLIN_LANGUAGE = Language(tree_sitter_kotlin.language())
except Exception as e:
    print(
        f"Failed to build tree-sitter-kotlin grammar. Please ensure `tree-sitter` and the grammar are installed. Error: {e}")
    KOTLIN_LANGUAGE = None


def get_parser():
    """Returns a configured tree-sitter parser for Kotlin."""
    parser = Parser()
    parser.language = KOTLIN_LANGUAGE
    return parser


def find_node_by_type(node: Node, node_type: str) -> List[Node]:
    """Recursively finds all nodes of a specific type in the AST."""
    nodes = []
    if node.type == node_type:
        nodes.append(node)
    for child in node.children:
        nodes.extend(find_node_by_type(child, node_type))
    return nodes


def extract_text(node: Node, source_bytes: bytes) -> str:
    """Extracts the text from an AST node."""
    return source_bytes[node.start_byte:node.end_byte].decode('utf-8')


def get_node_by_field_name(node: Node, field_name: str) -> Node | None:
    """Finds a child node by its field name."""
    for child in node.children:
        if child.type == field_name:
            return child
    return None


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

    # Find the package name
    package_name = ""

    query_string = """
        (package_header
          (identifier) @package_name)
    """

    query = KOTLIN_LANGUAGE.query("""
        (package_header
          (identifier) @package_name)
    """)
    print("*"*15)
    pprint(query)
    print("*"*15)

    pprint(tree.root_node.child(0))
    pprint(tree.root_node.child(0).children)

    package_node = get_node_by_field_name(tree.root_node, "package_header")
    if package_node:
        package_name_node = get_node_by_field_name(package_node, "package")
        if package_name_node:
            package_name = extract_text(package_name_node, source_bytes)

    # Find all class-like declarations
    all_declarations = find_node_by_type(tree.root_node, "class_declaration")
    all_declarations.extend(find_node_by_type(tree.root_node, "interface_declaration"))
    all_declarations.extend(find_node_by_type(tree.root_node, "object_declaration"))

    for node in all_declarations:
        declaration_info = {
            "path": file_path,
            "name": "",
            "package": package_name,
            "type": node.type.replace("_declaration", ""),
            "usage": [],
            "dependencies": [],
            "inheritance": [],
            "composition": [],
            "visibility": "public",  # Default to public
            "modifiers": []
        }

        # Extract name
        name_node = get_node_by_field_name(node, "name")
        if name_node:
            declaration_info["name"] = extract_text(name_node, source_bytes)

        # Extract modifiers and visibility
        modifier_list_node = get_node_by_field_name(node, "modifier_list")
        if modifier_list_node:
            for modifier_node in modifier_list_node.children:
                mod_text = extract_text(modifier_node, source_bytes)
                if mod_text in ["public", "private", "protected", "internal"]:
                    declaration_info["visibility"] = mod_text
                else:
                    declaration_info["modifiers"].append(mod_text)

        # Extract inheritance and dependencies (simpler version for demo)
        supertype_list_node = get_node_by_field_name(node, "supertype_list")
        if supertype_list_node:
            for supertype_node in supertype_list_node.children:
                supertype_text = extract_text(supertype_node, source_bytes).replace(":", "").strip()
                if supertype_text:
                    # Simple heuristic: assume anything after ':' is an inheritance or interface
                    declaration_info["inheritance"].append(supertype_text)

        # Find dependencies by looking at constructor parameters and properties
        for child in node.children:
            if child.type == "primary_constructor":
                for param in find_node_by_type(child, "function_parameter"):
                    type_node = get_node_by_field_name(param, "type")
                    if type_node:
                        dep_name = extract_text(type_node, source_bytes)
                        if dep_name not in declaration_info["dependencies"]:
                            declaration_info["dependencies"].append(dep_name)
            elif child.type == "property_declaration":
                type_node = get_node_by_field_name(child, "type")
                if type_node:
                    dep_name = extract_text(type_node, source_bytes)
                    if dep_name not in declaration_info["dependencies"]:
                        declaration_info["dependencies"].append(dep_name)

                # Simple check for composition (object created inside the class)
                initializer_node = get_node_by_field_name(child, "initializer")
                if initializer_node:
                    call_expression_node = get_node_by_field_name(initializer_node, "call_expression")
                    if call_expression_node and "class" in node.type:
                        declaration_info["composition"].append(dep_name)

        declarations.append(declaration_info)
    return declarations


def analyze_kotlin_codebase(root_path: str) -> Dict[str, Any]:
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
                    for declaration in declarations_in_file:
                        class_name = declaration["name"]
                        if class_name:
                            class_map[class_name] = declaration
                            analysis_results.append(declaration)
                except Exception as e:
                    print(f"Error processing file {file_path}: {e}")

    # Pass 2: Build cross-reference usage map
    for class_info in analysis_results:
        dependencies = class_info.get("dependencies", [])
        for dep_name in dependencies:
            # We check if the dependency is another class in our codebase
            if dep_name in class_map:
                usage_map[dep_name].append(class_info["name"])

    # Populate usage information in the final results
    for class_info in analysis_results:
        class_name = class_info["name"]
        if class_name:
            class_info["usage"] = usage_map.get(class_name, [])

    return {"analysis_report": analysis_results}


def run_tree_hugger() -> None:
    # In a real scenario, this would be a path to your Kotlin project.
    # We are creating a mock directory and files for this example.
    mock_dir = "mock_kotlin_project_advanced"
    os.makedirs(mock_dir, exist_ok=True)

    # Create sample files
    with open(os.path.join(mock_dir, "UserService.kt"), "w") as f:
        f.write("""
package com.example.app.services

import com.example.app.models.User
import com.example.app.repositories.UserRepository

interface UserService {
    fun getUserById(id: Int): User
}

class UserServiceImpl(private val userRepository: UserRepository) : UserService {
    override fun getUserById(id: Int): User {
        return userRepository.findById(id)
    }
}
""")
    with open(os.path.join(mock_dir, "UserRepository.kt"), "w") as f:
        f.write("""
package com.example.app.repositories

import com.example.app.models.User
import com.example.app.models.DatabaseConnection

class UserRepository(private val connection: DatabaseConnection) {
    fun findById(id: Int): User {
        // Implementation
        return User(id, "John Doe")
    }
}
""")
    with open(os.path.join(mock_dir, "User.kt"), "w") as f:
        f.write("""
package com.example.app.models

data class User(val id: Int, val name: String)
""")

    with open(os.path.join(mock_dir, "Database.kt"), "w") as f:
        f.write("""
package com.example.app.models

object DatabaseConnection {
    fun connect() {
        println("Connected to database.")
    }
}
""")

    # Run the analyzer on the mock directory
    report = analyze_kotlin_codebase(mock_dir)

    # Print a nicely formatted JSON output
    print(json.dumps(report, indent=2))


def build_kotlin_parser():
    kotlin_path = "/Users/asim/Documents/DEV/tree-sitter-kotlin"
    Language.build_library(
        'build/my-languages.so',
        [kotlin_path]
    )
    print("Kotlin language library built successfully!")


if __name__ == "__main__":
    run_tree_hugger()