import os
import dataclasses
import json
import re
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

import tree_sitter_kotlin
from tree_sitter import Language, Parser, Node, Query, QueryCursor

# Define a more comprehensive query for Kotlin, extending it to capture annotations,
# generics, and function overloading details.
# This query now includes captures for annotation lists and generic type parameters.
COMPREHENSIVE_QUERY = """
;; Package declaration
(package_header (qualified_identifier) @package_name)

;; Import declarations
(import (qualified_name) @import_name)

;; --- Top-Level Declarations ---
(declaration) @top_level_declaration

(class_declaration
  (modifier_list
    (visibility_modifier)? @declaration.visibility
    (annotation)* @declaration.annotation
  )?
  name: (identifier) @declaration.name
  type_parameters: (type_parameter_list (type_parameter (type_identifier) @declaration.type.parameter (type_constraint)?)*)?
  primary_constructor: (primary_constructor
    (class_parameter_list
      (class_parameter (modifier_list (visibility_modifier)? (val_or_var_modifier)?) (identifier) @constructor_param_name (type) @constructor_param_type)*
    )?
  )?
  delegation_specifier_list: (delegation_specifier_list
    (delegation_specifier (constructor_invocation (unqualified_name) @declaration.extends))?
    (delegation_specifier (unqualified_name) @declaration.implements)
  )*
) @top_level_declaration.class

(interface_declaration
  (modifier_list
    (visibility_modifier)? @declaration.visibility
    (annotation)* @declaration.annotation
  )?
  name: (identifier) @declaration.name
  type_parameters: (type_parameter_list (type_parameter (type_identifier) @declaration.type.parameter (type_constraint)?)*)?
  delegation_specifier_list: (delegation_specifier_list
    (delegation_specifier (unqualified_name) @declaration.implements)
  )?
) @top_level_declaration.interface

(enum_class_declaration
  (modifier_list
    (visibility_modifier)? @declaration.visibility
    (annotation)* @declaration.annotation
  )?
  name: (identifier) @declaration.name
) @top_level_declaration.enum_class

(object_declaration
  (modifier_list
    (data_modifier)? @declaration.is_data
    (visibility_modifier)? @declaration.visibility
    (annotation)* @declaration.annotation
  )?
  name: (identifier) @declaration.name
  delegation_specifier_list: (delegation_specifier_list
    (delegation_specifier (constructor_invocation (unqualified_name) @declaration.extends))?
    (delegation_specifier (unqualified_name) @declaration.implements)
  )*
) @top_level_declaration.object

(sealed_class_declaration
  (modifier_list (visibility_modifier)? @declaration.visibility)?
  name: (identifier) @declaration.name
  type_parameters: (type_parameter_list (type_parameter (type_identifier) @declaration.type.parameter (type_constraint)?)*)?
) @top_level_declaration.sealed_class

(sealed_interface_declaration
  (modifier_list (visibility_modifier)? @declaration.visibility)?
  name: (identifier) @declaration.name
  type_parameters: (type_parameter_list (type_parameter (type_identifier) @declaration.type.parameter (type_constraint)?)*)?
) @top_level_declaration.sealed_interface

(data_class_declaration
  (modifier_list
    (visibility_modifier)? @declaration.visibility
    (annotation)* @declaration.annotation
  )?
  name: (identifier) @declaration.name
  type_parameters: (type_parameter_list (type_parameter (type_identifier) @declaration.type.parameter (type_constraint)?)*)?
  primary_constructor: (primary_constructor
    (class_parameter_list
      (class_parameter (modifier_list (visibility_modifier)? (val_or_var_modifier)?) (identifier) @constructor_param_name (type) @constructor_param_type)*
    )?
  )?
  delegation_specifier_list: (delegation_specifier_list
    (delegation_specifier (constructor_invocation (unqualified_name) @declaration.extends))?
    (delegation_specifier (unqualified_name) @declaration.implements)
  )*
) @top_level_declaration.data_class

;; --- Member Declarations ---
(property_declaration
  (modifier_list
    (visibility_modifier)? @member.visibility
    (annotation)* @member.annotation
  )?
  name: (identifier) @member.name
  type: (type) @member.type
) @member_declaration.property

(function_declaration
  (modifier_list
    (visibility_modifier)? @function.visibility
    (override_modifier)? @function.override
    (annotation)* @function.annotation
  )?
  type_parameters: (type_parameter_list (type_parameter (type_identifier) @function.type.parameter (type_constraint)?)*)?
  name: (identifier) @function.name
  parameters: (function_parameter_list
    (function_parameter (identifier) @function.param.name type: (type) @function.param.type)*
  )?
  return_type: (type) @function.return_type
) @member_declaration.function

;; --- Type Usage Captures ---
;; This section is refined to capture more complex types, including generics.
(unqualified_name) @type_usage.name
(user_type (type_identifier) @type_usage.name (type_arguments (type)*)?)
(constructor_invocation (unqualified_name) @type_usage.name)
(type_identifier) @type_usage.name
"""


@dataclass
class KotlinAnalysis:
    """Data class to hold all extracted information."""
    filename: str = ""
    package_name: str = ""
    imports: List[str] = field(default_factory=list)
    name: str = ""
    type: str = ""  # class| interface|data class|enum| object | sealed class etc
    visibility: str = ""  # private | internal | public | protected
    annotations: List[str] = field(default_factory=list)
    generic_type_parameters: List[str] = field(default_factory=list)
    extends: str = ""  # parent class
    implements: List[str] = field(default_factory=list)  # list of interfaces being implemented
    constructor_param_type: List[str] = field(default_factory=list)
    members: List[Dict] = field(default_factory=list)
    functions: List[Dict] = field(
        default_factory=list)  # now includes signature to handle overloading
    uses: List[str] = field(default_factory=list)  # User
    used_by: List[str] = field(default_factory=list)  # for multi-file analysis (left empty for now)

    def to_json(self):
        """Helper to print the dataclass nicely."""
        return json.dumps(self, default=dataclasses.asdict, indent=4)


class KotlinASTAnalyzer:
    """
    A class to analyze Kotlin source code using Tree-sitter.

    This class encapsulates the parser, language, and all analysis logic.
    """

    def __init__(self):
        """Initializes the parser for Kotlin language."""
        self.KOTLIN_LANGUAGE = Language(tree_sitter_kotlin.language())
        self.parser = Parser()
        self.parser.language = self.KOTLIN_LANGUAGE
        # self.query = QueryCursor(Query(self.KOTLIN_LANGUAGE, COMPREHENSIVE_QUERY))

    def _get_text(self, node: Node, source_code_bytes: bytes) -> str:
        """Extracts the text from a node."""
        return source_code_bytes[node.start_byte:node.end_byte].decode('utf8')

    def _find_parent_declaration(self, node: Node, source_code_bytes: bytes):
        """Finds the top-level declaration (class, interface, etc.) for a given node."""
        while node:
            if node.type in [
                'class_declaration', 'interface_declaration',
                'object_declaration', 'enum_class_declaration',
                'data_class_declaration', 'sealed_class_declaration',
                'sealed_interface_declaration'
            ]:
                # Get the name node. Handle cases where the name might be the second or third child.
                name_node = next((c for c in node.children if c.is_named), None)
                name = self._get_text(name_node, source_code_bytes) if name_node else "Unknown"
                return name, node.type
            node = node.parent
        return None, None

    def analyze_code(self, source_code: str, file_path: str, base_project_path: str) -> List[KotlinAnalysis]:
        """
        Analyzes Kotlin source code to extract structured information.

        This method uses a multi-pass approach to build a complete picture
        of the code from Tree-sitter captures.
        """
        source_bytes = source_code.encode('utf8')
        tree = self.parser.parse(source_bytes)
        root_node = tree.root_node
        captures = self.query.captures(root_node)

        declarations_map: Dict[str, KotlinAnalysis] = {}
        package_name = ""
        imports = []

        # Pass 1: Find package and imports
        for node, name in captures:
            if name == 'package_name':
                package_name = self._get_text(node, source_bytes)
            elif name == 'import_name':
                imports.append(self._get_text(node, source_bytes))

        # Pass 2: Process top-level declarations and their details
        for node, name in captures:
            if name.startswith('top_level_declaration'):
                declaration_node = node

                # Get the name of the declaration
                name_node = next((c for c in declaration_node.children if
                                  c.is_named and c.type in ['class_name', 'interface_name', 'enum_class_name',
                                                            'object_name']), None)
                decl_name = self._get_text(name_node, source_bytes) if name_node else "Unknown"

                if decl_name not in declarations_map:
                    full_filename = os.path.join(base_project_path, file_path)
                    analysis = KotlinAnalysis(
                        filename=full_filename,
                        package_name=package_name,
                        imports=imports,
                        name=decl_name,
                        visibility="public",
                        type=name.split('.')[-1].replace('_', ' ')
                    )
                    declarations_map[decl_name] = analysis

                current_analysis = declarations_map[decl_name]

                # Iterate through children to find more details
                for child in declaration_node.children:
                    if child.type == 'modifiers':
                        for modifier_node in child.children:
                            if modifier_node.type == 'visibility_modifier':
                                current_analysis.visibility = self._get_text(modifier_node, source_bytes)
                            elif modifier_node.type == 'data_modifier':
                                current_analysis.type = "data " + current_analysis.type
                            elif modifier_node.type == 'annotation_list':
                                for annot_node in modifier_node.children:
                                    current_analysis.annotations.append(self._get_text(annot_node, source_bytes))
                    elif child.type == 'type_parameters':
                        for type_param_node in child.children:
                            if type_param_node.type == 'type_parameter':
                                current_analysis.generic_type_parameters.append(
                                    self._get_text(type_param_node, source_bytes))
                    elif child.type == 'constructor_invocation':
                        current_analysis.extends = self._get_text(child.children[0], source_bytes)
                    elif child.type == 'delegation_specifier_list':
                        for delegation in child.children:
                            if delegation.type == 'delegation_specifier':
                                current_analysis.implements.append(self._get_text(delegation.children[0], source_bytes))
                    elif child.type == 'class_parameter_list':
                        for param_node in child.children:
                            if param_node.type == 'class_parameter':
                                param_type = self._get_text(param_node.children[-1], source_bytes)
                                current_analysis.constructor_param_type.append(param_type)

        # Pass 3: Process member and function declarations
        for node, name in captures:
            if name.startswith('member_declaration'):
                parent_name, _ = self._find_parent_declaration(node, source_bytes)
                if parent_name and parent_name in declarations_map:
                    current_analysis = declarations_map[parent_name]

                    if name == 'member_declaration.function':
                        func_name_node = next((c for c in node.children if c.type == 'function_name'), None)
                        func_name = self._get_text(func_name_node, source_bytes) if func_name_node else ""

                        visibility = "public"
                        annotations = []
                        generic_params = []
                        for child in node.children:
                            if child.type == 'modifiers':
                                for mod_child in child.children:
                                    if mod_child.type == 'visibility_modifier':
                                        visibility = self._get_text(mod_child, source_bytes)
                                    elif mod_child.type == 'annotation_list':
                                        for annot_node in mod_child.children:
                                            annotations.append(self._get_text(annot_node, source_bytes))
                            elif child.type == 'type_parameters':
                                for type_param_node in child.children:
                                    if type_param_node.type == 'type_parameter':
                                        generic_params.append(self._get_text(type_param_node, source_bytes))

                        return_type_node = next((c for c in node.children if c.type == 'type'), None)
                        return_type = self._get_text(return_type_node, source_bytes) if return_type_node else "Unit"

                        param_types = []
                        param_list_node = next((c for c in node.children if c.type == 'function_parameter_list'), None)
                        if param_list_node:
                            for param_node in param_list_node.children:
                                if param_node.type == 'function_parameter':
                                    param_type_node = param_node.children[-1]
                                    param_types.append(self._get_text(param_type_node, source_bytes))

                        current_analysis.functions.append({
                            'name': func_name,
                            'signature': f"{func_name}({', '.join(param_types)})",  # Unique identifier for overloading
                            'visibility': visibility,
                            'return_type': return_type,
                            'param_types': param_types,
                            'annotations': annotations,
                            'generic_type_parameters': generic_params,
                        })

                    elif name == 'member_declaration.property':
                        prop_name_node = next((c for c in node.children if c.type == 'simple_identifier'), None)
                        prop_name = self._get_text(prop_name_node, source_bytes) if prop_name_node else ""

                        visibility = "public"
                        annotations = []
                        for child in node.children:
                            if child.type == 'modifiers':
                                for mod_child in child.children:
                                    if mod_child.type == 'visibility_modifier':
                                        visibility = self._get_text(mod_child, source_bytes)
                                    elif mod_child.type == 'annotation_list':
                                        for annot_node in mod_child.children:
                                            annotations.append(self._get_text(annot_node, source_bytes))

                        prop_type_node = next((c for c in node.children if c.type == 'type'), None)
                        prop_type = self._get_text(prop_type_node, source_bytes) if prop_type_node else "Any"

                        current_analysis.members.append({
                            'name': prop_name,
                            'visibility': visibility,
                            'type': prop_type,
                            'annotations': annotations,
                        })

        # Pass 4: Collect type usages, including from generic types
        all_type_usages = set()
        for node, name in captures:
            if name == 'type_usage.name':
                full_type_text = self._get_text(node, source_bytes)
                # Split complex types like List<String> into List and String
                matches = re.findall(r'(\w+)', full_type_text)
                all_type_usages.update(matches)

        for decl_name, analysis in declarations_map.items():
            used_types = set()
            for usage in all_type_usages:
                # Avoid adding the declaration itself and its internal members
                is_internal = any(
                    usage == m['name'] for m in analysis.members
                ) or any(
                    usage == f['name'] for f in analysis.functions
                )
                if usage != decl_name and usage not in analysis.implements and usage != analysis.extends and usage not in analysis.constructor_param_type and not is_internal:
                    used_types.add(usage)
            analysis.uses = sorted(list(used_types))

        return list(declarations_map.values())

    def print_ast_tree(self, source_code: str):
        """
        Parses source code and prints the full AST tree in a hierarchical, readable format.
        """
        source_bytes = source_code.encode('utf8')
        tree = self.parser.parse(source_bytes)
        root_node = tree.root_node

        print("--- AST Tree ---")
        self._print_node(root_node, source_bytes, 0)
        print("--- End of AST Tree ---")

    def _print_node(self, node: Node, source_bytes: bytes, indent: int):
        """Recursive helper function to print the AST nodes with indentation."""
        indentation = "  " * indent
        node_text = self._get_text(node, source_bytes)
        print(f"{indentation}{node.type} [pos: {node.start_point} to {node.end_point}] "
              f"text: '{node_text.strip()}'")

        for child in node.children:
            self._print_node(child, source_bytes, indent + 1)


if __name__ == '__main__':
    # Initialize the analyzer
    analyzer = KotlinASTAnalyzer()

    # --- Sample 1: Class with Inheritance and Implementation, Generics, and Annotations ---
    print("--- Sample 1: Advanced Class Example with Generics & Annotations ---")
    file_path_1 = "src/main/kotlin/org/jay/sample/computing/ProcessorDelay.kt"
    source_code_1 = """
@file:JvmName("ProcessingUtils")
package org.jay.sample.computing

import kotlin.random.Random
import org.jay.sample.computing.categories.Processor

@Deprecated("This class is deprecated")
class ProcessorDelay<T : Any, V>(private val delayFactor: Int, @Inject private val formFactor : FormFactor) : Processor(delayFactor), IProcessorDelay<T> {

    @Volatile
    private var actuater : Random.Default

    @Override
    override fun startProcessing(category: ProcessorCategory): Int {
        return when (category) {
            Alpha -> {
                when(formFactor){
                    SimpleForm -> calculateDelay()
                    ComplexForm -> calculateDelay(extraInfo = 5)
                }
            }
            Beta -> {
                delayFactor
            }
            is Gamma -> {
                calculateDelay(extraInfo = category.extraCapacity)
            }
        }
    }

    fun processData(data: T): V? = null
    fun processData(data: T, key: String): V = TODO()

    private fun calculateDelay(extraInfo: Int = 1): Int {
        return extraInfo * delayFactor * actuater.nextInt()
    }

    private fun prepare(){

    }
}
"""
    analyzer.print_ast_tree(source_code_1)
#     results_1 = analyzer.analyze_code(source_code_1, file_path_1, "baseProject")
#     for res in results_1:
#         print(res.to_json())
#
    # --- Sample 2: Interface with Generics ---
    print("\n\n--- Sample 2: Interface with Generics and Annotations ---")
    file_path_2 = "src/main/kotlin/org/jay/sample/computing/IProcessorDelay.kt"
    source_code_2 = """
package org.jay.sample.computing

@Service
interface IProcessorDelay<T> {
    fun startProcessing(category: ProcessorCategory) : Int
    fun processData(data: T): Any?
}
"""
#     results_2 = analyzer.analyze_code(source_code_2, file_path_2, "baseProject")
#     for res in results_2:
#         print(res.to_json())
#
#     # --- Sample 3: Sealed Class Hierarchy ---
#     print("\n\n--- Sample 3: Sealed Class Hierarchy ---")
#     file_path_3 = "src/main/kotlin/org/jay/sample/computing/ProcessorCategory.kt"
#     source_code_3 = """
# package org.jay.sample.computing
#
# sealed class ProcessorCategory
#
# data object Alpha : ProcessorCategory()
#
# object Beta : ProcessorCategory()
#
# data class Gamma(val extraCapacity: Int) : ProcessorCategory()
# """
#     results_3 = analyzer.analyze_code(source_code_3, file_path_3, "baseProject")
#     for res in results_3:
#         print(res.to_json())
