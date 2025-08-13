#!/usr/bin/env python3
"""
Multi-Agent Codebase Analysis and Documentation System

This system consists of several specialized agents that work together to:
1. Read and parse codebases from local directories
2. Track relationships between classes, functions, and modules
3. Generate comprehensive documentation

Agents:
- FileSystemAgent: Handles file discovery and reading
- ParserAgent: Analyzes code structure and extracts metadata
- RelationshipAgent: Tracks dependencies and relationships
- DocumentationAgent: Generates and manages documentation
- CoordinatorAgent: Orchestrates the entire process
"""

import os
import ast
import json
import re
from pathlib import Path
from typing import Dict, List, Set, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from abc import ABC, abstractmethod
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class CodeElement:
    """Represents a code element (class, function, module, etc.)"""
    name: str
    type: str  # 'class', 'function', 'module', 'variable'
    file_path: str
    line_number: int
    docstring: Optional[str] = None
    parameters: List[str] = None
    return_type: Optional[str] = None
    decorators: List[str] = None
    parent_class: Optional[str] = None
    imports: List[str] = None

    def __post_init__(self):
        if self.parameters is None:
            self.parameters = []
        if self.decorators is None:
            self.decorators = []
        if self.imports is None:
            self.imports = []


@dataclass
class Relationship:
    """Represents a relationship between code elements"""
    source: str
    target: str
    relationship_type: str  # 'inherits', 'calls', 'imports', 'uses', 'instantiates'
    file_path: str
    line_number: int


class Agent(ABC):
    """Base class for all agents in the system"""

    def __init__(self, name: str):
        self.name = name
        self.logger = logging.getLogger(f"{__name__}.{name}")

    @abstractmethod
    def process(self, data: Any) -> Any:
        """Main processing method for the agent"""
        pass


class FileSystemAgent(Agent):
    """Agent responsible for file discovery and reading"""

    def __init__(self):
        super().__init__("FileSystemAgent")
        self.supported_extensions = {'.py', '.js', '.ts', '.java', '.cpp', '.c', '.h'}

    def discover_files(self, directory: str, extensions: Set[str] = None) -> List[str]:
        """Discover all code files in the given directory"""
        if extensions is None:
            extensions = self.supported_extensions

        files = []
        directory_path = Path(directory)

        if not directory_path.exists():
            self.logger.error(f"Directory {directory} does not exist")
            return files

        for file_path in directory_path.rglob("*"):
            if file_path.suffix in extensions and file_path.is_file():
                # Skip common non-source directories
                if any(part.startswith('.') or part in ['__pycache__', 'node_modules', 'build', 'dist']
                       for part in file_path.parts):
                    continue
                files.append(str(file_path))

        self.logger.info(f"Discovered {len(files)} files in {directory}")
        return files

    def read_file(self, file_path: str) -> Optional[str]:
        """Read the contents of a file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            self.logger.error(f"Error reading file {file_path}: {e}")
            return None

    def process(self, directory: str) -> Dict[str, str]:
        """Process a directory and return file contents"""
        files = self.discover_files(directory)
        file_contents = {}

        for file_path in files:
            content = self.read_file(file_path)
            if content is not None:
                file_contents[file_path] = content

        return file_contents


class PythonParserAgent(Agent):
    """Agent specialized in parsing Python code"""

    def __init__(self):
        super().__init__("PythonParserAgent")

    def extract_imports(self, node: ast.AST) -> List[str]:
        """Extract import statements from AST"""
        imports = []
        for child in ast.walk(node):
            if isinstance(child, ast.Import):
                for alias in child.names:
                    imports.append(alias.name)
            elif isinstance(child, ast.ImportFrom):
                module = child.module or ""
                for alias in child.names:
                    imports.append(f"{module}.{alias.name}" if module else alias.name)
        return imports

    def extract_decorators(self, node) -> List[str]:
        """Extract decorator names from a function or class"""
        decorators = []
        if hasattr(node, 'decorator_list'):
            for decorator in node.decorator_list:
                if isinstance(decorator, ast.Name):
                    decorators.append(decorator.id)
                elif isinstance(decorator, ast.Call) and isinstance(decorator.func, ast.Name):
                    decorators.append(decorator.func.id)
        return decorators

    def extract_parameters(self, node: ast.FunctionDef) -> List[str]:
        """Extract parameter names from a function"""
        params = []
        for arg in node.args.args:
            params.append(arg.arg)
        return params

    def parse_file(self, file_path: str, content: str) -> List[CodeElement]:
        """Parse a Python file and extract code elements"""
        elements = []

        try:
            tree = ast.parse(content)
            imports = self.extract_imports(tree)

            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    element = CodeElement(
                        name=node.name,
                        type='class',
                        file_path=file_path,
                        line_number=node.lineno,
                        docstring=ast.get_docstring(node),
                        decorators=self.extract_decorators(node),
                        imports=imports
                    )
                    elements.append(element)

                elif isinstance(node, ast.FunctionDef):
                    parent_class = None
                    # Check if function is inside a class
                    for parent in ast.walk(tree):
                        if isinstance(parent, ast.ClassDef):
                            for child in ast.walk(parent):
                                if child is node:
                                    parent_class = parent.name
                                    break

                    element = CodeElement(
                        name=node.name,
                        type='function',
                        file_path=file_path,
                        line_number=node.lineno,
                        docstring=ast.get_docstring(node),
                        parameters=self.extract_parameters(node),
                        decorators=self.extract_decorators(node),
                        parent_class=parent_class,
                        imports=imports
                    )
                    elements.append(element)

        except SyntaxError as e:
            self.logger.error(f"Syntax error in {file_path}: {e}")
        except Exception as e:
            self.logger.error(f"Error parsing {file_path}: {e}")

        return elements

    def process(self, file_data: Dict[str, str]) -> List[CodeElement]:
        """Process multiple Python files"""
        all_elements = []

        for file_path, content in file_data.items():
            if file_path.endswith('.py'):
                elements = self.parse_file(file_path, content)
                all_elements.extend(elements)

        self.logger.info(f"Extracted {len(all_elements)} code elements")
        return all_elements


class RelationshipAgent(Agent):
    """Agent responsible for tracking relationships between code elements"""

    def __init__(self):
        super().__init__("RelationshipAgent")

    def find_inheritance_relationships(self, file_path: str, content: str) -> List[Relationship]:
        """Find class inheritance relationships"""
        relationships = []

        try:
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef) and node.bases:
                    for base in node.bases:
                        if isinstance(base, ast.Name):
                            relationship = Relationship(
                                source=node.name,
                                target=base.id,
                                relationship_type='inherits',
                                file_path=file_path,
                                line_number=node.lineno
                            )
                            relationships.append(relationship)
        except Exception as e:
            self.logger.error(f"Error finding inheritance in {file_path}: {e}")

        return relationships

    def find_function_calls(self, file_path: str, content: str, known_functions: Set[str]) -> List[Relationship]:
        """Find function call relationships"""
        relationships = []

        try:
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, ast.Call):
                    if isinstance(node.func, ast.Name) and node.func.id in known_functions:
                        # Find the containing function or class
                        parent_name = self._find_parent_name(tree, node)
                        if parent_name:
                            relationship = Relationship(
                                source=parent_name,
                                target=node.func.id,
                                relationship_type='calls',
                                file_path=file_path,
                                line_number=node.lineno
                            )
                            relationships.append(relationship)
        except Exception as e:
            self.logger.error(f"Error finding function calls in {file_path}: {e}")

        return relationships

    def _find_parent_name(self, tree: ast.AST, target_node: ast.AST) -> Optional[str]:
        """Find the name of the parent function or class containing the target node"""
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                for child in ast.walk(node):
                    if child is target_node:
                        return node.name
        return None

    def process(self, data: Tuple[Dict[str, str], List[CodeElement]]) -> List[Relationship]:
        """Process files and code elements to find relationships"""
        file_data, elements = data
        all_relationships = []

        # Create a set of known function names for faster lookup
        known_functions = {elem.name for elem in elements if elem.type == 'function'}

        for file_path, content in file_data.items():
            if file_path.endswith('.py'):
                # Find inheritance relationships
                inheritance_rels = self.find_inheritance_relationships(file_path, content)
                all_relationships.extend(inheritance_rels)

                # Find function call relationships
                call_rels = self.find_function_calls(file_path, content, known_functions)
                all_relationships.extend(call_rels)

        self.logger.info(f"Found {len(all_relationships)} relationships")
        return all_relationships


class DocumentationAgent(Agent):
    """Agent responsible for generating documentation"""

    def __init__(self):
        super().__init__("DocumentationAgent")

    def generate_class_doc(self, element: CodeElement, relationships: List[Relationship]) -> str:
        """Generate documentation for a class"""
        doc = f"## Class: {element.name}\n\n"
        doc += f"**File:** `{element.file_path}` (Line {element.line_number})\n\n"

        if element.docstring:
            doc += f"**Description:**\n{element.docstring}\n\n"

        # Find inheritance relationships
        inherits_from = [r.target for r in relationships
                         if r.source == element.name and r.relationship_type == 'inherits']
        if inherits_from:
            doc += f"**Inherits from:** {', '.join(inherits_from)}\n\n"

        # Find classes that inherit from this one
        inherited_by = [r.source for r in relationships
                        if r.target == element.name and r.relationship_type == 'inherits']
        if inherited_by:
            doc += f"**Inherited by:** {', '.join(inherited_by)}\n\n"

        if element.decorators:
            doc += f"**Decorators:** {', '.join(element.decorators)}\n\n"

        return doc

    def generate_function_doc(self, element: CodeElement, relationships: List[Relationship]) -> str:
        """Generate documentation for a function"""
        doc = f"## Function: {element.name}\n\n"
        doc += f"**File:** `{element.file_path}` (Line {element.line_number})\n\n"

        if element.parent_class:
            doc += f"**Class:** {element.parent_class}\n\n"

        if element.parameters:
            doc += f"**Parameters:** {', '.join(element.parameters)}\n\n"

        if element.docstring:
            doc += f"**Description:**\n{element.docstring}\n\n"

        # Find functions this one calls
        calls = [r.target for r in relationships
                 if r.source == element.name and r.relationship_type == 'calls']
        if calls:
            doc += f"**Calls:** {', '.join(calls)}\n\n"

        # Find functions that call this one
        called_by = [r.source for r in relationships
                     if r.target == element.name and r.relationship_type == 'calls']
        if called_by:
            doc += f"**Called by:** {', '.join(called_by)}\n\n"

        if element.decorators:
            doc += f"**Decorators:** {', '.join(element.decorators)}\n\n"

        return doc

    def generate_overview_doc(self, elements: List[CodeElement], relationships: List[Relationship]) -> str:
        """Generate an overview documentation"""
        doc = "# Codebase Overview\n\n"

        # Statistics
        classes = [e for e in elements if e.type == 'class']
        functions = [e for e in elements if e.type == 'function']
        files = set(e.file_path for e in elements)

        doc += f"## Statistics\n\n"
        doc += f"- **Files analyzed:** {len(files)}\n"
        doc += f"- **Classes:** {len(classes)}\n"
        doc += f"- **Functions:** {len(functions)}\n"
        doc += f"- **Relationships:** {len(relationships)}\n\n"

        # File structure
        doc += f"## File Structure\n\n"
        for file_path in sorted(files):
            file_elements = [e for e in elements if e.file_path == file_path]
            doc += f"### {file_path}\n"
            doc += f"- Classes: {len([e for e in file_elements if e.type == 'class'])}\n"
            doc += f"- Functions: {len([e for e in file_elements if e.type == 'function'])}\n\n"

        return doc

    def process(self, data: Tuple[List[CodeElement], List[Relationship]]) -> Dict[str, str]:
        """Generate comprehensive documentation"""
        elements, relationships = data
        documentation = {}

        # Generate overview
        documentation['overview.md'] = self.generate_overview_doc(elements, relationships)

        # Generate documentation for each element
        for element in elements:
            if element.type == 'class':
                doc_content = self.generate_class_doc(element, relationships)
                documentation[f"class_{element.name}.md"] = doc_content
            elif element.type == 'function' and not element.parent_class:
                doc_content = self.generate_function_doc(element, relationships)
                documentation[f"function_{element.name}.md"] = doc_content

        self.logger.info(f"Generated documentation for {len(documentation)} items")
        return documentation


class CoordinatorAgent(Agent):
    """Main coordinator that orchestrates all other agents"""

    def __init__(self):
        super().__init__("CoordinatorAgent")
        self.filesystem_agent = FileSystemAgent()
        self.parser_agent = PythonParserAgent()
        self.relationship_agent = RelationshipAgent()
        self.documentation_agent = DocumentationAgent()

    def analyze_codebase(self, directory: str, output_dir: str = "docs") -> Dict[str, Any]:
        """Main method to analyze a codebase and generate documentation"""
        self.logger.info(f"Starting codebase analysis for: {directory}")

        # Step 1: Discover and read files
        self.logger.info("Step 1: Reading files...")
        file_contents = self.filesystem_agent.process(directory)

        if not file_contents:
            self.logger.error("No files found to analyze")
            return {}

        # Step 2: Parse code elements
        self.logger.info("Step 2: Parsing code elements...")
        elements = self.parser_agent.process(file_contents)

        # Step 3: Find relationships
        self.logger.info("Step 3: Finding relationships...")
        relationships = self.relationship_agent.process((file_contents, elements))

        # Step 4: Generate documentation
        self.logger.info("Step 4: Generating documentation...")
        documentation = self.documentation_agent.process((elements, relationships))

        # Step 5: Save documentation
        self.logger.info("Step 5: Saving documentation...")
        self._save_documentation(documentation, output_dir)

        # Return analysis results
        return {
            'elements': [asdict(e) for e in elements],
            'relationships': [asdict(r) for r in relationships],
            'documentation': documentation,
            'stats': {
                'files_analyzed': len(file_contents),
                'elements_found': len(elements),
                'relationships_found': len(relationships),
                'docs_generated': len(documentation)
            }
        }

    def _save_documentation(self, documentation: Dict[str, str], output_dir: str):
        """Save documentation files to disk"""
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)

        for filename, content in documentation.items():
            file_path = output_path / filename
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                self.logger.info(f"Saved documentation: {file_path}")
            except Exception as e:
                self.logger.error(f"Error saving {file_path}: {e}")

    def process(self, directory: str) -> Dict[str, Any]:
        """Process method implementation"""
        return self.analyze_codebase(directory)


def main():
    """Example usage of the multi-agent system"""
    # Initialize the coordinator
    coordinator = CoordinatorAgent()

    # Analyze a codebase (replace with your directory path)
    directory = "."  # Current directory
    results = coordinator.analyze_codebase(directory)

    # Print summary
    if results:
        print("\n=== Analysis Complete ===")
        print(f"Files analyzed: {results['stats']['files_analyzed']}")
        print(f"Code elements found: {results['stats']['elements_found']}")
        print(f"Relationships found: {results['stats']['relationships_found']}")
        print(f"Documentation files generated: {results['stats']['docs_generated']}")
        print("\nCheck the 'docs' directory for generated documentation.")
    else:
        print("Analysis failed or no files found.")


if __name__ == "__main__":
    main()