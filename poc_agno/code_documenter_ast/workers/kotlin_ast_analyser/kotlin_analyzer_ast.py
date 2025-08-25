import traceback
from pprint import pprint
from typing import List, Optional

import tree_sitter_kotlin
from tree_sitter import Language, Parser, Node, Query, QueryCursor

from poc_agno.code_documenter_ast.workers.kotlin_ast_analyser.model import KotlinAnalysisData, FunctionData, \
    VariableData


class KotlinASTAnalyzer:
    """
    A Kotlin Abstract Syntax Tree (AST) analyzer using tree-sitter.
    
    This class provides comprehensive analysis of Kotlin source code by parsing
    the AST and extracting structural information including classes, functions,
    properties, annotations, and inheritance relationships.
    
    The analyzer uses tree-sitter queries with named captures to extract specific
    code elements. All capture names are defined as constants to ensure consistency
    and maintainability across queries and result processing.
    
    Each query has comprehensive documentation explaining what it extracts, with
    examples and use cases. Use the `get_all_queries_documentation()` method to
    access detailed documentation for all queries.
    
    Attributes:
        language (Language): The tree-sitter language object for Kotlin
        parser (Parser): The tree-sitter parser instance
        
        # Query capture key constants - Define all capture names used in queries
        KEY_PACKAGE, KEY_IMPORT, KEY_CLASS_ANNOTATION, etc.
        
        # Tree-sitter query methods - Return query strings with capture key constants
        _get_package_query(): Returns package declaration query
        _get_import_query(): Returns import statements query
        _get_high_level_class_query(): Returns class declaration query
        _get_extends_implements_query(): Returns inheritance query
        _get_function_query(): Returns function declaration query
        _get_members_query(): Returns property declaration query
        _get_ctor_params_query(): Returns constructor parameters query
        _get_object_query(): Returns object declaration query
    """

    # Query capture key constants - Used in tree-sitter queries and result processing
    # These constants define the capture names used in tree-sitter queries
    # and are referenced throughout the code to avoid magic strings
    KEY_PACKAGE = "package"                    # Package declaration capture
    KEY_IMPORT = "import"                      # Import statement capture
    KEY_CLASS_ANNOTATION = "class.annotation"  # Class-level annotation capture
    KEY_CLASS_VISIBILITY = "class.visibility"  # Class visibility modifier capture
    KEY_CLASS_MODIFIER = "class.modifier"      # Class modifier (data, sealed, etc.) capture
    KEY_TYPE_NAME = "type.name"                # Class/interface name capture
    KEY_CLASS_BODY = "class.body"              # Class body content capture
    KEY_CLASS_PARENT = "class.parent"                    # Superclass inheritance capture
    KEY_CLASS_INTERFACE = "class.interface"              # Interface implementation capture
    KEY_FUNCTION_ANNOTATION = "function.annotation"  # Function annotation capture
    KEY_FUNCTION_VISIBILITY = "function.visibility"  # Function visibility capture
    KEY_FUNCTION_NAME = "function.name"        # Function name capture

    KEY_FUNCTION_PARAMS = "function.params"    # Function parameters capture
    KEY_FUNCTION_PARAM_NAME = "function.param.name"
    KEY_FUNCTION_PARAM_TYPE = "function.param.type"
    KEY_FUNCTION_PARAM_ANNOTATION = "function.param..annotation"
    KEY_FUNCTION_PARAM_DEFAULT_VALUE = "function.param.default.value"

    KEY_FUNCTION_RETURN_TYPE = "function.return_type"  # Function return type capture
    KEY_PROPERTY_ANNOTATION = "property.annotation"    # Property annotation capture
    KEY_PROPERTY_VISIBILITY = "property.visibility"    # Property visibility capture
    KEY_PROPERTY_NAME = "property.name"        # Property name capture
    KEY_PROPERTY_TYPE = "property.type"        # Property type capture
    KEY_PROPERTY_DEFAULT = "property.default"  # Property default value capture
    KEY_CTOR_PARAM_ANNOTATION = "ctor.param.annotation"    # Constructor param annotation capture
    KEY_CTOR_PARAM_VISIBILITY = "ctor.param.visibility"    # Constructor param visibility capture
    KEY_CTOR_PARAM_NAME = "ctor.param.name"    # Constructor parameter name capture
    KEY_CTOR_PARAM_TYPE = "ctor.param.type"    # Constructor parameter type capture
    KEY_CTOR_PARAM_DEFAULT = "ctor.param.default"  # Constructor parameter default capture
    KEY_DECLARATION = "declaration"
    KEY_USER_TYPE_NAME = "user.type.name"

    KOTLIN_BUILTIN_TYPES = {
        "Int", "Long", "Short", "Byte", "Float", "Double", "Char", "Boolean", "Unit",
        "String", "Any", "Nothing", "Array", "List", "MutableList", "Set", "Map",
        "MutableSet", "MutableMap"
    }

    def _get_package_query(self) -> str:
        """
        Get the package declaration query.
        
        This query extracts package declarations from Kotlin source code.
        
        **Query Pattern:**
        ```kotlin
        package org.example.myapp
        ```
        
        **Captures:**
        - ``{self.KEY_PACKAGE}``: The full package identifier (e.g., "org.example.myapp")
        
        **Example Output:**
        - Input: ``package com.company.project``
        - Captured: ``{self.KEY_PACKAGE} = "com.company.project"``
        
        **Use Case:** Identifying the namespace/package of the Kotlin file.
        """
        return f"""
        ;; Package declaration query - Captures package name from package_header
        (package_header (qualified_identifier) @{self.KEY_PACKAGE})
        """

    def _get_import_query(self) -> str:
        """
        Get the import statements query.
        
        This query extracts all import statements from Kotlin source code.
        
        **Query Pattern:**
        ```kotlin
        import kotlin.collections.List
        import org.example.User
        import javax.inject.Inject
        ```
        
        **Captures:**
        - ``{self.KEY_IMPORT}``: Each import statement identifier
        
        **Example Output:**
        - Input: Multiple import statements
        - Captured: 
          - ``{self.KEY_IMPORT} = "kotlin.collections.List"``
          - ``{self.KEY_IMPORT} = "org.example.User"``
          - ``{self.KEY_IMPORT} = "javax.inject.Inject"``
        
        **Use Case:** Building dependency graphs and understanding external dependencies.
        """
        return f"""
        ;; Import statements query - Captures all import declarations
        (import (qualified_identifier) @{self.KEY_IMPORT})
        """

    def _get_high_level_class_query(self) -> str:
        """
        Get the high-level class/interface declaration query.
        
        This query extracts comprehensive information about class and interface declarations.
        
        **Query Pattern:**
        ```kotlin
        @Deprecated("Use NewClass instead")
        public data class User(
            val name: String,
            val age: Int
        ) { ... }
        
        @Service
        internal interface UserService { ... }
        ```
        
        **Captures:**
        - ``{self.KEY_CLASS_ANNOTATION}``: Class-level annotations (e.g., "@Deprecated", "@Service")
        - ``{self.KEY_CLASS_VISIBILITY}``: Visibility modifier ("public", "private", "internal")
        - ``{self.KEY_CLASS_MODIFIER}``: Class modifiers ("data", "sealed", "abstract", "enum")
        - ``{self.KEY_TYPE_NAME}``: Class/interface name (e.g., "User", "UserService")
        - ``{self.KEY_CLASS_BODY}``: Class body content for further analysis
        
        **Example Output:**
        - Input: ``@Deprecated public data class User { ... }``
        - Captured:
          - ``{self.KEY_CLASS_ANNOTATION} = ["@Deprecated"]``
          - ``{self.KEY_CLASS_VISIBILITY} = "public"``
          - ``{self.KEY_CLASS_MODIFIER} = "data"``
          - ``{self.KEY_TYPE_NAME} = "User"``
          - ``{self.KEY_CLASS_BODY} = class body node``
        
        **Use Case:** Understanding class structure, modifiers, and metadata for documentation generation.
        """
        return f"""
        ;; Class/interface declaration query - Captures class structure and metadata
        [
            (class_declaration
                (modifiers
                    (annotation)? @{self.KEY_CLASS_ANNOTATION}*    ;; Class annotations (e.g., @Deprecated)
                    (visibility_modifier)? @{self.KEY_CLASS_VISIBILITY}  ;; Visibility (public, private, internal)
                    (class_modifier)? @{self.KEY_CLASS_MODIFIER}    ;; Modifiers (data, sealed, abstract, etc.)
                )?
                (identifier) @{self.KEY_TYPE_NAME}                 ;; Class/interface name
                (class_body)? @{self.KEY_CLASS_BODY}               ;; Class body content for further analysis
            )
            
            (object_declaration
                (modifiers
                    (annotation)? @{self.KEY_CLASS_ANNOTATION}*    ;; Class annotations (e.g., @Deprecated)
                    (visibility_modifier)? @{self.KEY_CLASS_VISIBILITY}  ;; Visibility (public, private, internal)
                    (class_modifier)? @{self.KEY_CLASS_MODIFIER}    ;; Modifiers (data, sealed, abstract, etc.)
                )?
                (identifier) @{self.KEY_TYPE_NAME}                 ;; Class/interface name
                (class_body)? @{self.KEY_CLASS_BODY}               ;; Class body content for further analysis
            )
        ]
        
        """

    def _get_extends_implements_query(self) -> str:
        """
        Get the inheritance and interface implementation query.
        
        This query extracts inheritance relationships and interface implementations.
        
        **Query Pattern:**
        ```kotlin
        class User : BaseUser(), Serializable, Cloneable {
            // class body
        }
        
        interface UserService : BaseService, Auditable {
            // interface body
        }
        ```
        
        **Captures:**
        - ``{self.KEY_EXTENDS}``: Superclass that this class extends (e.g., "BaseUser")
        - ``{self.KEY_IMPLEMENTS}``: Interfaces that this class implements (e.g., "Serializable", "Cloneable")
        
        **Example Output:**
        - Input: ``class User : BaseUser(), Serializable, Cloneable``
        - Captured:
          - ``{self.KEY_EXTENDS} = "BaseUser"``
          - ``{self.KEY_IMPLEMENTS} = "BaseUser"``
        
        **Use Case:** Building inheritance hierarchies and understanding class relationships.
        """
        return f"""
        ;; Inheritance and interface implementation query
        (delegation_specifiers
            (delegation_specifier 
                (constructor_invocation 
                    (user_type 
                        (identifier) @{self.KEY_CLASS_PARENT}
                    )    ;; Superclass inheritance
                )
            )?
            (delegation_specifier 
                (user_type 
                    (identifier) @{self.KEY_CLASS_INTERFACE}            ;; Interface implementations
                )
            )?
        )
        """

    def _get_function_query(self) -> str:
        """
        Get the function/method declaration query.
        
        This query extracts function and method declarations with their metadata.
        
        **Query Pattern:**
        ```kotlin
        @Override
        public fun calculateSum(a: Int, b: Int): Int {
            return a + b
        }
        
        @Deprecated("Use newCalculate instead")
        private fun oldCalculate(): String? {
            return "deprecated"
        }
        ```
        
        **Captures:**
        - ``{self.KEY_FUNCTION_ANNOTATION}``: Function annotations (e.g., "@Override", "@Deprecated")
        - ``{self.KEY_FUNCTION_VISIBILITY}``: Visibility modifier ("public", "private", "internal")
        - ``{self.KEY_FUNCTION_NAME}``: Function name (e.g., "calculateSum", "oldCalculate")
        - ``{self.KEY_FUNCTION_PARAMS}``: Function parameters (e.g., "a: Int, b: Int")
        - ``{self.KEY_FUNCTION_RETURN_TYPE}``: Return type (e.g., "Int", "String?")
        
        **Example Output:**
        - Input: ``@Override public fun calculateSum(a: Int, b: Int): Int``
        - Captured:
          - ``{self.KEY_FUNCTION_ANNOTATION} = ["@Override"]``
          - ``{self.KEY_FUNCTION_VISIBILITY} = "public"``
          - ``{self.KEY_FUNCTION_NAME} = "calculateSum"``
          - ``{self.KEY_FUNCTION_PARAMS} = "a: Int, b: Int"``
          - ``{self.KEY_FUNCTION_RETURN_TYPE} = "Int"``
        
        **Use Case:** Generating function documentation and understanding method signatures.
        """
        return f"""
        ;; Function/method declaration query - Captures function metadata and signature
        (function_declaration
                (modifiers
                    (annotation)? @{self.KEY_FUNCTION_ANNOTATION}      ;; Function annotations
                    (visibility_modifier)? @{self.KEY_FUNCTION_VISIBILITY}  ;; Function visibility
                )?
                (identifier) @{self.KEY_FUNCTION_NAME}                    ;; Function name
                (function_value_parameters) @{self.KEY_FUNCTION_PARAMS}   ;; Function parameters
                [
                    (user_type (identifier) @{self.KEY_FUNCTION_RETURN_TYPE})      ;; Return type
                    (nullable_type (user_type (identifier) @{self.KEY_FUNCTION_RETURN_TYPE}))  ;; Nullable return type
                ]?
            )
        """

    def _get_members_query(self) -> str:
        """
        Get the class property/member declaration query.
        
        This query extracts class properties and member variables with their metadata.
        
        **Query Pattern:**
        ```kotlin
        @Inject
        @Volatile
        private var counter: Int = 0
        
        @Serializable
        public val name: String = "default"
        
        internal var description: String? = null
        ```
        
        **Captures:**
        - ``{self.KEY_PROPERTY_ANNOTATION}``: Property annotations (e.g., "@Inject", "@Volatile", "@Serializable")
        - ``{self.KEY_PROPERTY_VISIBILITY}``: Visibility modifier ("public", "private", "internal")
        - ``{self.KEY_PROPERTY_NAME}``: Property name (e.g., "counter", "name", "description")
        - ``{self.KEY_PROPERTY_TYPE}``: Property type (e.g., "Int", "String", "String?")
        - ``{self.KEY_PROPERTY_DEFAULT}``: Default value or initialization (e.g., "0", "\"default\"", "null")
        
        **Example Output:**
        - Input: ``@Inject @Volatile private var counter: Int = 0``
        - Captured:
          - ``{self.KEY_PROPERTY_ANNOTATION} = ["@Inject", "@Volatile"]``
          - ``{self.KEY_PROPERTY_VISIBILITY} = "private"``
          - ``{self.KEY_PROPERTY_NAME} = "counter"``
          - ``{self.KEY_PROPERTY_TYPE} = "Int"``
          - ``{self.KEY_PROPERTY_DEFAULT} = "0"``
        
        **Use Case:** Generating property documentation and understanding class structure.
        """
        return f"""
        ;; Class property/member declaration query - Captures property metadata and type info
        (property_declaration
            (modifiers
                (annotation)* @{self.KEY_PROPERTY_ANNOTATION}        ;; Property annotations (e.g., @Inject, @Volatile)
                (visibility_modifier)? @{self.KEY_PROPERTY_VISIBILITY}  ;; Property visibility (public, private, etc.)
            )?
            (variable_declaration 
                (identifier) @{self.KEY_PROPERTY_NAME}                ;; Property name
                [
                    (user_type 
                        (identifier) @{self.KEY_PROPERTY_TYPE}        ;; Property type (e.g., String, Int, List<T>)
                    )
                    (nullable_type 
                        (user_type 
                            (identifier) @{self.KEY_PROPERTY_TYPE}    ;; Nullable property type (e.g., String?)
                        )
                    )
                ]
            )
            (_) @{self.KEY_PROPERTY_DEFAULT}                         ;; Default value or initialization
        )
        """

    def _get_ctor_params_query(self) -> str:
        """
        Get the primary constructor parameters query.
        
        This query extracts primary constructor parameters with their metadata.
        
        **Query Pattern:**
        ```kotlin
        class User(
            @Inject private val id: Int,
            val name: String,
            val email: String? = null
        ) { ... }
        
        data class Product(
            val sku: String,
            @Serializable val price: Double
        )
        ```
        
        **Captures:**
        - ``{self.KEY_CTOR_PARAM_ANNOTATION}``: Parameter annotations (e.g., "@Inject", "@Serializable")
        - ``{self.KEY_CTOR_PARAM_VISIBILITY}``: Parameter visibility ("public", "private", "internal")
        - ``{self.KEY_CTOR_PARAM_NAME}``: Parameter name (e.g., "id", "name", "email")
        - ``{self.KEY_PARAM_TYPE}``: Parameter type (e.g., "Int", "String", "String?")
        - ``{self.KEY_CTOR_PARAM_DEFAULT}``: Default value if specified (e.g., "null")
        
        **Example Output:**
        - Input: ``@Inject private val id: Int``
        - Captured:
          - ``{self.KEY_CTOR_PARAM_ANNOTATION} = ["@Inject"]``
          - ``{self.KEY_CTOR_PARAM_VISIBILITY} = "private"``
          - ``{self.KEY_CTOR_PARAM_NAME} = "id"``
          - ``{self.KEY_CTOR_PARAM_TYPE} = "Int"``
          - ``{self.KEY_CTOR_PARAM_DEFAULT} = ""`` (no default value)
        
        **Use Case:** Understanding constructor signatures and parameter requirements.
        """
        return f"""
        ;; Primary constructor parameters query - Captures constructor parameter metadata
        (primary_constructor
            (class_parameters 
                (class_parameter 
                    (modifiers
                        (annotation)* @{self.KEY_CTOR_PARAM_ANNOTATION}      ;; Parameter annotations (e.g., @Inject)
                        (visibility_modifier)? @{self.KEY_CTOR_PARAM_VISIBILITY}  ;; Parameter visibility
                    )?
                    (identifier) @{self.KEY_CTOR_PARAM_NAME}                    ;; Parameter name
                    [
                        (user_type 
                            (identifier) @{self.KEY_CTOR_PARAM_TYPE}            ;; Parameter type
                        )
                        (nullable_type 
                            (user_type 
                                (identifier) @{self.KEY_CTOR_PARAM_TYPE}        ;; Nullable parameter type
                            )
                        )
                    ]
                )?
            )
        )
        """

    def _get_class_or_object_query(self):
        return f"""
        (
          [
            (class_declaration) 
            (object_declaration)
          ] @{self.KEY_DECLARATION}
        )
        """

    def _get_user_type_query(self):
        return f"""
        ;; Match all type usages
        (user_type 
            (identifier) @{self.KEY_USER_TYPE_NAME}
        )
        """
        # ;; Generics like List<MyType>
        # (type_arguments
        #     (user_type
        #         (identifier) @{self.KEY_USER_TYPE_NAME}
        #     )
        # )
        #
        # ;; Nested identifiers inside generics (Map<String, MyType>)
        # ;; (type_identifier) @{self.KEY_USER_TYPE_NAME}
        # """

    def __init__(self):
        """
        Sets up the tree-sitter language object for Kotlin and initializes
        the parser with the appropriate language support.
        
        Raises:
            Exception: If tree-sitter Kotlin language cannot be loaded
        """
        self.language = Language(tree_sitter_kotlin.language())
        self.parser = Parser()
        self.parser.language = self.language

    def analyze_kotlin_file(self, file_path: str,
                            source_bytes: bytes,
                            print_debug_info: bool = False
                            ) -> list[KotlinAnalysisData] | None:
        """
        Analyze a Kotlin code file and extract structural information.
        
        This method parses the Kotlin source code using tree-sitter and extracts
        comprehensive information about the code structure including packages,
        imports, classes, functions, properties, and inheritance relationships.
        
        Args:
            file_path (str): Path to the Kotlin source file (for reference)
            source_bytes (bytes): Raw bytes of the Kotlin source code
            print_debug_info (bool, optional): Whether to print debug information
                including the full AST tree structure. Defaults to False.
        
        Returns:
            KotlinAnalysisData: A data object containing all extracted information
                about the Kotlin code structure.
        
        Raises:
            Exception: If parsing fails or an error occurs during analysis
        
        Example:
            >>> analyzer = KotlinASTAnalyzer()
            >>> with open('MyClass.kt', 'rb') as f:
            ...     source_bytes = f.read()
            ...     result = analyzer.analyze_kotlin_file('MyClass.kt', source_bytes)
            ...     print(f"Found class: {result.name}")
        """

        try:
            tree = self.parser.parse(source_bytes)
            root_node = tree.root_node
            if print_debug_info:
                print("=== DEBUGGING TREE STRUCTURE ===")
                self._print_tree(source_bytes=source_bytes, node=root_node)
                print("=== END DEBUG ===\n")

            kotlin_analysis = self._start(root_node,file_path)
            print("==" * 60)
            print("=" * 24 + "FINAL RESULT" + "=" * 24)
            print("==" * 60)
            pprint(kotlin_analysis)
            print("==" * 60)
            return kotlin_analysis
        except Exception as err:
            print("*" * 4 + "ERROR" + "*" * 4)
            print(f"{err.__class__.__name__}: {err}")  # exception type + message
            traceback.print_exc()  # <-- this prints the full stack trace
            print("*" * 4 + "ERROR" + "*" * 4)


    def _start(self, root_node: Node , file_path: str) -> list[KotlinAnalysisData]:
        package = self._extract_package_name_wq(root_node)
        imports = self._extract_imports_wq(root_node)
        analysis_data = []
        cursor = self._create_query_cursor(self._get_class_or_object_query())
        matches = cursor.matches(root_node)

        for index, match in enumerate(matches):
            pprint(f"{index}: {match}")
            captures_dict = match[1]

            kotlin_analysis = KotlinAnalysisData()
            kotlin_analysis.filename = file_path
            kotlin_analysis.package_name = package
            kotlin_analysis.imports = imports

            if self.KEY_DECLARATION in captures_dict:
                declaration_node = captures_dict[self.KEY_DECLARATION][0]

                self._extract_high_level_declaration_wq(declaration_node, kotlin_analysis)
                kotlin_analysis.type = f"{kotlin_analysis.type} {self._extract_type(declaration_node)}".strip()

                self._extract_parents(declaration_node, kotlin_analysis)
                self._extract_members_wq(declaration_node, kotlin_analysis)
                self._extract_constructor_params_wq(declaration_node, kotlin_analysis)
                self._extract_classes_used_wq(declaration_node, kotlin_analysis)
                analysis_data.append(kotlin_analysis)

        return analysis_data

    def _extract_classes_used_wq(self, declaration_node, kotlin_analysis):
        print("*" * 4 + "User types" + "*" * 4)
        cursor = self._create_query_cursor(self._get_user_type_query())
        matches = cursor.matches(declaration_node)
        found_types = set()

        for index, match in matches:
            captures_dict = match
            if captures_dict:
                if self.KEY_USER_TYPE_NAME in captures_dict:
                    type_name = self._get_node_text(captures_dict[self.KEY_USER_TYPE_NAME][0])

                    # Skip built-in Kotlin types
                    if type_name in self.KOTLIN_BUILTIN_TYPES:
                        continue

                    fq_name = self._resolve_fully_qualified(type_name, kotlin_analysis)

                    # Skip self-references (class shouldn't list itself as "used")
                    if fq_name == kotlin_analysis.package_name + "." + kotlin_analysis.name:
                        continue

                    found_types.add(fq_name)

        # Merge into existing uses
        kotlin_analysis.uses = sorted(set(kotlin_analysis.uses).union(found_types))

        self._extract_types_from_members_and_functions(kotlin_analysis)

    def _resolve_fully_qualified(self,type_name: str, kotlin_analysis: KotlinAnalysisData) -> str:
        """
        Resolve the fully qualified name of a type based on the package and imports.
        """
        # 1. Direct import match
        for imp in kotlin_analysis.imports:
            if imp.endswith("." + type_name):
                return imp

        # 2. Wildcard import
        for imp in kotlin_analysis.imports:
            if imp.endswith(".*"):
                return imp[:-2] + "." + type_name

        # 3. Same package assumption
        if kotlin_analysis.package_name:
            return kotlin_analysis.package_name + "." + type_name

        # 4. Fallback
        return type_name

    def _extract_types_from_members_and_functions(self,kotlin_analysis: KotlinAnalysisData):
        """
        Ensure member variables, constructor params, and function signatures contribute to uses.
        Excludes built-in types and self-references.
        """
        found_types = set(kotlin_analysis.uses)
        self_fq_name = kotlin_analysis.package_name + "." + kotlin_analysis.name

        # Check member variable types
        for member in kotlin_analysis.members:
            if member.type and member.type not in self.KOTLIN_BUILTIN_TYPES:
                fq = self._resolve_fully_qualified(member.type, kotlin_analysis)
                if fq != self_fq_name:
                    found_types.add(fq)

        # Check constructor param types
        for param in kotlin_analysis.constructor_param_type:
            if param.type and param.type not in self.KOTLIN_BUILTIN_TYPES:
                fq = self._resolve_fully_qualified(param.type, kotlin_analysis)
                if fq != self_fq_name:
                    found_types.add(fq)

        # Check function return + param types
        for fn in kotlin_analysis.functions:
            # Return type
            if fn.return_type and fn.return_type not in self.KOTLIN_BUILTIN_TYPES:
                fq = self._resolve_fully_qualified(fn.return_type, kotlin_analysis)
                if fq != self_fq_name:
                    found_types.add(fq)

            # Parameter types
            for param in fn.parameters:
                if param.type and param.type not in self.KOTLIN_BUILTIN_TYPES:
                    fq = self._resolve_fully_qualified(param.type, kotlin_analysis)
                    if fq != self_fq_name:
                        found_types.add(fq)

        kotlin_analysis.uses = sorted(found_types)

    def _extract_constructor_params_wq(self, root_node: Node, kotlin_analysis: KotlinAnalysisData):
        """
        Extract constructor parameters using tree-sitter queries.

        This method uses the CTOR_PARAMS_QUERY to find and extract information
        about primary constructor parameters including their names, types,
        annotations, visibility modifiers, and default values.

        Args:
            root_node (Node): The root node of the parsed AST
            kotlin_analysis (KotlinAnalysisData): The analysis data object to populate

        Note:
            The 'wq' suffix indicates this method uses tree-sitter queries.
        """
        print("*" * 4 + "Constructor PARAMS" + "*" * 4)
        cursor = self._create_query_cursor(self._get_ctor_params_query())
        matches = cursor.matches(root_node)
        for index, match in enumerate(matches):
            pprint(f"{index}: {match}")
            captures_dict = match[1]
            if captures_dict:
                member_data = VariableData()
                if self.KEY_CTOR_PARAM_NAME in captures_dict:
                    ctor_params = self._get_node_text(captures_dict[self.KEY_CTOR_PARAM_NAME][0])
                    member_data.name = ctor_params

                if self.KEY_CTOR_PARAM_ANNOTATION in captures_dict:
                    for property_annotation_node in captures_dict[self.KEY_CTOR_PARAM_ANNOTATION]:
                        annotation = self._get_node_text(property_annotation_node)
                        member_data.annotations.append(annotation)

                if self.KEY_CTOR_PARAM_VISIBILITY in captures_dict:
                    member_data.visibility = self._get_node_text(captures_dict[self.KEY_CTOR_PARAM_VISIBILITY][0])

                if self.KEY_CTOR_PARAM_TYPE in captures_dict:
                    member_data.type = self._get_node_text(captures_dict[self.KEY_CTOR_PARAM_TYPE][0])

                if self.KEY_CTOR_PARAM_DEFAULT in captures_dict:
                    member_data.default_value = self._get_node_text(captures_dict[self.KEY_CTOR_PARAM_DEFAULT][0])

                kotlin_analysis.constructor_param_type.append(member_data)

    def _extract_members_wq(self, root_node: Node, kotlin_analysis: KotlinAnalysisData):
        """
        Extract class members (properties) using tree-sitter queries.
        
        This method uses the MEMBERS_QUERY to find and extract information
        about class properties including their names, types, annotations,
        visibility modifiers, and default values.
        
        Args:
            root_node (Node): The root node of the parsed AST
            kotlin_analysis (KotlinAnalysisData): The analysis data object to populate
        
        Note:
            The 'wq' suffix indicates this method uses tree-sitter queries.
        """
        print("*" * 4 + "EXTRACTING MEMBERS" + "*" * 4)
        cursor = self._create_query_cursor(self._get_members_query())
        matches = cursor.matches(root_node)
        for index, match in enumerate(matches):
            member_data = VariableData()
            pprint(f"{index}: {match}")
            captures_dict = match[1]
            if self.KEY_PROPERTY_ANNOTATION in captures_dict:
                for property_annotation_node in captures_dict[self.KEY_PROPERTY_ANNOTATION]:
                    annotation = self._get_node_text(property_annotation_node)
                    member_data.annotations.append(annotation)

            if self.KEY_PROPERTY_VISIBILITY in captures_dict:
                member_data.visibility = self._get_node_text(captures_dict[self.KEY_PROPERTY_VISIBILITY][0])

            if self.KEY_PROPERTY_NAME in captures_dict:
                member_data.name = self._get_node_text(captures_dict[self.KEY_PROPERTY_NAME][0])

            if self.KEY_PROPERTY_TYPE in captures_dict:
                member_data.type = self._get_node_text(captures_dict[self.KEY_PROPERTY_TYPE][0])

            if self.KEY_PROPERTY_DEFAULT in captures_dict:
                member_data.default_value = self._get_node_text(captures_dict[self.KEY_PROPERTY_DEFAULT][0])

            kotlin_analysis.members.append(member_data)

    def _extract_package_name_wq(self, root_node: Node) -> Optional[str]:
        """
        Extract package name using tree-sitter queries.
        
        This method uses the PACKAGE_QUERY to find and extract the package
        declaration from the Kotlin source code.
        
        Args:
            root_node (Node): The root node of the parsed AST
        
        Returns:
            Optional[str]: The package name if found, empty string otherwise
        
        Note:
            The 'wq' suffix indicates this method uses tree-sitter queries.
        """
        cursor = self._create_query_cursor(self._get_package_query())
        matches = cursor.matches(root_node)
        for index, match in enumerate(matches):
            pprint(f"{index}: {match}")
            captures_dict = match[1]
            return self._extract_package_name(captures_dict, index)

        return ""

    def _extract_imports_wq(self, root_node: Node) -> List[str]:
        """
        Extract import statements using tree-sitter queries.
        
        This method uses the IMPORT_QUERY to find and extract all import
        statements from the Kotlin source code.
        
        Args:
            root_node (Node): The root node of the parsed AST
        
        Returns:
            List[str]: List of import statements found in the code
        
        Note:
            The 'wq' suffix indicates this method uses tree-sitter queries.
        """
        imports = []
        cursor = self._create_query_cursor(self._get_import_query())
        matches = cursor.matches(root_node)
        for index, match in enumerate(matches):
            pprint(f"{index}: {match}")
            captures_dict = match[1]
            import_name = self._extract_imports(captures_dict, index)
            if import_name != "":
                imports.append(import_name)

        return imports

    def _extract_type(self, node: Node):
        """
        Recursively extract the type of a declaration node.

        This method traverses the AST to find the type of a declaration,
        such as 'class', 'interface', or 'object'.

        Args:
            node (Node): The AST node to analyze

        Returns:
            Optional[str]: The type of the declaration if found, None otherwise
        """
        if node.type == "object_declaration":
            return "object"
        if node.type == "class_declaration":
            for child in node.children:
                if child.type in ("class", "interface" ):
                    return child.type
        for child in node.children:
            result = self._extract_type(child)
            if result:
                return result
        return None

    def _extract_high_level_declaration_wq(self, root_node: Node, analysis: KotlinAnalysisData):
        """
        Extract high-level class/interface declaration details using tree-sitter queries.

        This method uses the HIGH_LEVEL_CLASS_QUERY to extract comprehensive information
        about class declarations including annotations, visibility modifiers, class modifiers,
        names, and function definitions within the class body.

        Args:
            root_node (Node): The root node of the parsed AST
            analysis (KotlinAnalysisData): The analysis data object to populate

        Note:
            The 'wq' suffix indicates this method uses tree-sitter queries.
        """
        print("*" * 4 + "DETAILS " + "*" * 4)
        cursor = self._create_query_cursor(self._get_high_level_class_query())
        matches = cursor.matches(root_node)
        for index, match in enumerate(matches):
            pprint(f"{index}: {match}")
            captures_dict = match[1]
            if self.KEY_CLASS_ANNOTATION in captures_dict:
                anno_names = []
                for annotation_node in captures_dict[self.KEY_CLASS_ANNOTATION]:
                    anno = self._get_node_text(annotation_node)
                    print(f"annotation modifier: {anno}")
                    anno_names.append(anno)
                analysis.annotations = anno_names

            # visiblity modifier
            visibility_modifier = "public" if self.KEY_CLASS_VISIBILITY not in captures_dict else \
                (self._get_node_text(captures_dict[self.KEY_CLASS_VISIBILITY][0]))
            # print(f"visibility_modifier = {visibility_modifier}")
            analysis.visibility = visibility_modifier

            # class modifier (data / sealed etc) to get info like 'data class' 'sealed class' etc.
            if self.KEY_CLASS_MODIFIER in captures_dict:
                class_modifier = self._get_node_text(captures_dict[self.KEY_CLASS_MODIFIER][0])
                # print(f"class_modifier = {class_modifier}")
                analysis.type = class_modifier
            # name
            if self.KEY_TYPE_NAME in captures_dict:
                interface_name = self._get_node_text(captures_dict[self.KEY_TYPE_NAME][0])
                # print(f"interface_name = {interface_name}")
                analysis.name = interface_name

            if self.KEY_CLASS_BODY in captures_dict:
                # print(type(captures_dict[self.KEY_CLASS_BODY]))
                # print(captures_dict[self.KEY_CLASS_BODY][0])
                self._extract_functions_wq(captures_dict[self.KEY_CLASS_BODY][0], analysis)

    def _extract_parents(self, root_node, kotlin_analysis):
        """
        Extract inheritance relationships using tree-sitter queries.

        This method uses the EXTENDS_IMPLEMENTS_QUERY to find and extract
        information about class inheritance (extends) and interface
        implementations (implements).

        Args:
            root_node (Node): The root node of the parsed AST
            kotlin_analysis (KotlinAnalysisData): The analysis data object to populate
        """
        print("*" * 4 + "PARENTS DETAILS " + "*" * 4)
        cursor = self._create_query_cursor(self._get_extends_implements_query())
        matches = cursor.matches(root_node)
        for index, match in enumerate(matches):
            pprint(f"{index}: {match}")
            captures_dict = match[1]
            print(captures_dict)
            if self.KEY_CLASS_PARENT in captures_dict:
                kotlin_analysis.extends = self._get_node_text(captures_dict[self.KEY_CLASS_PARENT][0])

            if self.KEY_CLASS_INTERFACE in captures_dict:
                kotlin_analysis.implements.append(self._get_node_text(captures_dict[self.KEY_CLASS_INTERFACE][0]))

    def _extract_functions_wq(self, root_node: Node, analysis: KotlinAnalysisData) -> List[str]:
        """
        Extract function declarations using tree-sitter queries.

        This method uses the FUNCTION_QUERY to find and extract information
        about function declarations including annotations, names, visibility,
        parameters, and return types.

        Args:
            root_node (Node): The root node of the parsed AST
            analysis (KotlinAnalysisData): The analysis data object to populate

        Returns:
            List[str]: List of function names extracted (for backward compatibility)

        Note:
            The 'wq' suffix indicates this method uses tree-sitter queries.
        """
        print("*" * 4 + "FUNCTION DETAILS " + "*" * 4)
        cursor = self._create_query_cursor(self._get_function_query())
        matches = cursor.matches(root_node)
        for index, match in enumerate(matches):
            pprint(f"{index}: {match}")
            captures_dict = match[1]
            function_data = FunctionData()

            if self.KEY_FUNCTION_ANNOTATION in captures_dict:
                for annotation_node in captures_dict[self.KEY_FUNCTION_ANNOTATION]:
                    function_data.annotations.append(self._get_node_text(annotation_node))

            if self.KEY_FUNCTION_NAME in captures_dict:
                function_data.name = self._get_node_text(captures_dict[self.KEY_FUNCTION_NAME][0])

            if self.KEY_FUNCTION_VISIBILITY in captures_dict:
                function_data.visibility = self._get_node_text(captures_dict[self.KEY_FUNCTION_VISIBILITY][0])

            if self.KEY_FUNCTION_PARAMS in captures_dict:
                for param_node in captures_dict[self.KEY_FUNCTION_PARAMS]:
                    pprint(f"-=-=-=-=-=-=-={index}-=-=-=-: {param_node}")
                    cursor_small = self._create_query_cursor(f"""
                        (function_value_parameters
                            (parameter_modifiers
                                (annotation
                                    (user_type
                                        (identifier) @{self.KEY_FUNCTION_PARAM_ANNOTATION}
                                    )
                                )
                            )?
                            (parameter
                                (identifier) @{self.KEY_FUNCTION_PARAM_NAME}
                                [
                                  (user_type (identifier) @{self.KEY_FUNCTION_PARAM_TYPE})
                                  (nullable_type (user_type (identifier) @{self.KEY_FUNCTION_PARAM_TYPE}))
                                ]?
                            )
                        )
                    """)

                    som_matches = cursor_small.matches(param_node)

                    for idx, som_match in enumerate(som_matches):
                        paramData = VariableData()
                        paramData.visibility = ""

                        captures_dict_2 = som_match[1]
                        pprint(f"{index}::{idx}: {captures_dict_2}")
                        if self.KEY_FUNCTION_PARAM_NAME in captures_dict_2:
                            pprint(captures_dict_2[self.KEY_FUNCTION_PARAM_NAME])
                            paramData.name = self._get_node_text(captures_dict_2[self.KEY_FUNCTION_PARAM_NAME][0])
                            paramData.type = self._get_node_text(captures_dict_2[self.KEY_FUNCTION_PARAM_TYPE][0])

                            if self.KEY_FUNCTION_PARAM_ANNOTATION in captures_dict_2:
                                for annotation in captures_dict_2[self.KEY_FUNCTION_PARAM_ANNOTATION]:
                                    paramData.annotations.append(self._get_node_text(annotation))

                            parameter_node = captures_dict_2[self.KEY_FUNCTION_PARAM_NAME][0].parent
                            siblings = param_node.children
                            try:
                                idx_in_siblings = siblings.index(parameter_node)
                                if (
                                        idx_in_siblings + 2 < len(siblings)
                                        and siblings[idx_in_siblings + 1].type == "="
                                ):
                                    default_node = siblings[idx_in_siblings + 2]
                                    paramData.default_value = self._get_node_text(default_node)
                            except ValueError:
                                pass  # parameter_node not found in siblings

                            function_data.parameters.append(paramData)

            if self.KEY_FUNCTION_RETURN_TYPE in captures_dict:
                function_data.return_type = self._get_node_text(captures_dict[self.KEY_FUNCTION_RETURN_TYPE][0])

            analysis.functions.append(function_data)

    def _extract_imports(self, captures_dict, index):
        """
        Extract import statement from capture dictionary.

        Args:
            captures_dict (dict): Dictionary containing captured nodes from tree-sitter query
            index (int): Index of the current match for debugging purposes

        Returns:
            str: The import statement text if found, empty string otherwise
        """
        print("*" * 4 + "IMPORTS" + "*" * 4)
        if self.KEY_IMPORT in captures_dict:
            import_name = self._get_node_text(captures_dict[self.KEY_IMPORT][0])
            print(f"{index}: Import: {import_name}")
            return import_name
        else:
            return ""

    def _extract_package_name(self, captures_dict, index) -> str:
        """
        Extract package name from capture dictionary.

        Args:
            captures_dict (dict): Dictionary containing captured nodes from tree-sitter query
            index (int): Index of the current match for debugging purposes

        Returns:
            str: The package name text if found, empty string otherwise
        """
        print("*" * 4 + "PACKAGE NAME" + "*" * 4)
        if self.KEY_PACKAGE in captures_dict:
            package_name = self._get_node_text(captures_dict[self.KEY_PACKAGE][0])
            print(f"{index}: Package: {package_name}")
            return package_name
        else:
            return ""

    def _create_query_cursor(self, query_text: str) -> QueryCursor:
        """
        Create a tree-sitter query cursor for executing queries.

        Args:
            query_text (str): The tree-sitter query string to compile

        Returns:
            QueryCursor: A cursor for executing the compiled query

        Raises:
            Exception: If query compilation fails
        """
        try:
            query = Query(self.language, query_text)
            return QueryCursor(query)
        except Exception as err:
            print("*" * 4 + "ERROR" + "*" * 4)
            print(err)
            print("*" * 4 + "ERROR" + "*" * 4)

    def _get_node_text(self, node) -> str:
        """
        Get text content of a tree-sitter node.

        Args:
            node (Node): The tree-sitter node to extract text from

        Returns:
            str: The decoded text content of the node, or empty string if node is None
        """
        return node.text.decode('utf-8') if node else ""

    def _print_tree(self, source_bytes: bytes, node=None, indent=0, max_lines=2000):
        """
        Print a visual representation of the AST tree structure.

        This method recursively traverses the AST and prints each node with
        proper indentation to show the tree hierarchy. Useful for debugging
        and understanding the structure of parsed Kotlin code.

        Args:
            source_bytes (bytes): The original source code bytes for text extraction
            node (Node, optional): The current node to print. Defaults to None.
            indent (int, optional): Current indentation level. Defaults to 0.
            max_lines (int, optional): Maximum lines to print. Defaults to 2000.
        """
        prefix = "  " * indent
        text = self._node_text(source_bytes, node).strip().splitlines()
        sample = text[0][:80] + ("..." if len(text[0]) > 80 else "") if text else ""
        print(f"{prefix}{node.type} [{node.start_point}..{node.end_point}] -- {sample}")
        for child in node.children:
            self._print_tree(source_bytes, child, indent + 1)

    def _node_text(self, source_bytes: bytes, node) -> str:
        """
        Extract text content from a node using byte offsets.

        This method extracts the text content of a tree-sitter node by using
        the node's start and end byte positions to slice the original source bytes.

        Args:
            source_bytes (bytes): The original source code bytes
            node (Node): The tree-sitter node to extract text from

        Returns:
            str: The decoded text content of the node
        """
        return source_bytes[node.start_byte:node.end_byte].decode("utf-8")


def run_():
    """
    Demo function showcasing the KotlinASTAnalyzer capabilities.
    
    This function demonstrates how to use the KotlinASTAnalyzer class
    by analyzing various sample Kotlin code snippets including:
    - Advanced classes with generics and annotations
    - Interfaces with generics
    - Sealed classes and data objects
    - Private data classes
    
    The function creates sample Kotlin code and runs it through the analyzer
    to show the extraction capabilities.
    """
    print("--- Sample 1: Advanced Class Example with Generics & Annotations ---")
    file_path_1 = "src/main/kotlin/org/jay/sample/computing/ProcessorDelay.kt"
    source_code_1 = """
        @file:JvmName("ProcessingUtils")

package org.jay.sample.computing

import org.jay.sample.computing.categories.Chip
import org.jay.sample.pie.categories.Processor
import javax.inject.Inject
import kotlin.random.Random

@Deprecated("This class is deprecated")
class ProcessorDelay<T : Any, V>(
    delayFactor: Int,
    @Inject private val formFactor: FormFactor,
    private val packaging: String?
) : Processor(delayFactor), IProcessorDelay<T>, Chip {

    @Volatile
    private var rando: Random = Random.Default

    internal val pins: Int = 1

    @Inject
    @Suppress("some message")
    public val material: String = "SomeExpensiveMaterial"

    val temp: Float? = null

    @Override
    override fun startProcessing(category: ProcessorCategory): Int {
        return when (category) {
            Alpha -> {
                when (formFactor) {
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
        return extraInfo * delayFactor * rando.nextInt()
    }

    private fun prepare(v: Int?) {

    }
}
        """

    # --- Sample 2: Interface with Generics ---
    print("\n\n--- Sample 2: Interface with Generics and Annotations ---")
    file_path_2 = "src/main/kotlin/org/jay/sample/computing/IProcessorDelay.kt"
    source_code_2 = """
        package org.jay.sample.computing
        
        import kotlin.random.Random
        import org.jay.sample.computing.categories.Processor
        import org.jat.sample.pie.categories.Processor as PiProcessor
        
        @Service
        @Ishqay(modifier = PACKAGE)
        internal interface IProcessorDelay<T : SomeFancyClass> {
            fun startProcessing(category: ProcessorCategory , someThing: SomeThingSomeThing , p: Int) : Boolean
            
            @Nullable
            fun emptyParamFuncName()
            
            @Visibility(private)
            internal fun processData(data: T): Any?
        }
        """

    source_code_3 = """
    package org.jay.sample.computing

sealed class FormFactor

data object ComplexForm : FormFactor()
object SimpleForm : FormFactor()
data class CustomForm(val customization: Float) : FormFactor()
    """

    source_code_4 = """
    package org.jay.sample.computing

        import kotlin.random.Random
     private data class Input(
    val sourcePath : String,
    val destinationPath : String,
)
    """

    source_code_5 = """
        package org.jay.sample.computing
        
        import org.jay.sample.computing.categories.Processor
        import org.jat.sample.pie.categories.Processor as PiProcessor
        import kotlin.random.Random
        
        @Nullable
         private data class Input(
            val sourcePath : String,
            val destinationPath : String,
        )
        
        @Service
        @Ishqay(modifier = PACKAGE)
        internal interface IProcessorDelay<T : SomeFancyClass> {
            fun startProcessing(category: ProcessorCategory , someThing: SomeThingSomeThing , p: Int) : Boolean
            
            @Nullable
            fun emptyParamFuncName()
            
            @Visibility(private)
            internal fun processData(data: T): Any?
        }
        
        sealed class FormFactor

data object ComplexForm : FormFactor()
object SimpleForm : FormFactor()
data class CustomForm(val customization: Float) : FormFactor()
        @Dost
        class SomethingSomething(){
        fun processData(data: T): Any?{
        }
        }
        """

    source_code_6 = """
@Dost
        class SomethingSomething(){
        fun processData(data: T , beta:Boolean = false,@nullable gamma:Int?): Any?{
        }
        }
"""
    KotlinASTAnalyzer().analyze_kotlin_file(file_path=file_path_1,
                                            source_bytes=source_code_1.encode("utf-8"),
                                            print_debug_info=True)


if __name__ == "__main__":
    run_()
