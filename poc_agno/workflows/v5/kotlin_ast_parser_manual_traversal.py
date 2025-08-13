from typing import List

import tree_sitter_kotlin
from tree_sitter import Language, Parser

from poc_agno.workflows.v5.model.kotlin_analysis import KotlinAnalysis


class KotlinASTParserManualTraversal:
    """
    Manual traversal approach - for comparison

    Disadvantages:
    - More verbose code
    - Potentially slower (multiple passes)
    - More error-prone
    - Harder to maintain
    - Need to handle tree structure manually
    """

    def __init__(self, kotlin_language_path: str):
        self.kotlin_language = Language(tree_sitter_kotlin.language())
        self.parser = parser = Parser()
        self.parser.language = self.kotlin_language

    def parse_file(self, filename: str, content: str) -> List[KotlinAnalysis]:
        """Parse using manual traversal - less efficient."""
        tree = self.parser.parse(bytes(content, "utf8"))
        root_node = tree.root_node

        # Multiple passes through the tree
        package_name = self._find_package_manual(root_node)
        imports = self._find_imports_manual(root_node)
        class_declarations = self._find_class_declarations_manual(root_node)

        analyses = []
        for class_node in class_declarations:
            analysis = KotlinAnalysis(filename=filename)
            analysis.package_name = package_name
            analysis.imports = imports.copy()
            analysis.name = self._extract_class_name_manual(class_node)
            analysis.type = self._extract_class_type_manual(class_node)
            analysis.visibility = self._extract_visibility_manual(class_node)
            analysis.functions = self._extract_functions_manual(class_node)
            analysis.uses = self._extract_type_uses_manual(class_node)
            analyses.append(analysis)

        return analyses

    def _find_package_manual(self, node) -> str:
        """Manual recursive search for package."""
        if node.type == "package_header":
            for child in node.children:
                if child.type == "identifier":
                    return self._get_node_text(child)

        for child in node.children:
            result = self._find_package_manual(child)
            if result:
                return result
        return ""

    def _find_imports_manual(self, node) -> List[str]:
        """Manual recursive search for imports."""
        imports = []
        self._collect_imports_recursive(node, imports)
        return imports

    def _collect_imports_recursive(self, node, imports: List[str]):
        """Recursively collect imports."""
        if node.type == "import_header":
            for child in node.children:
                if child.type == "identifier":
                    imports.append(self._get_node_text(child))

        for child in node.children:
            self._collect_imports_recursive(child, imports)

    def _find_class_declarations_manual(self, node) -> List:
        """Manual recursive search for class declarations."""
        declarations = []
        self._collect_class_declarations_recursive(node, declarations)
        return declarations

    def _collect_class_declarations_recursive(self, node, declarations: List):
        """Recursively collect class declarations."""
        if node.type in ["class_declaration", "interface_declaration",
                         "enum_declaration", "object_declaration"]:
            declarations.append(node)

        for child in node.children:
            self._collect_class_declarations_recursive(child, declarations)

    # ... (rest of manual methods would be similar to the original implementation)

    def _get_node_text(self, node) -> str:
        """Get text content of a node."""
        return node.text.decode('utf-8') if node else ""
