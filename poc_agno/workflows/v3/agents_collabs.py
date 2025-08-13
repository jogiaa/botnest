"""
Agno-based Code Documentation Agent with RAG using ChromaDB
Automatically generates documentation for codebases while maintaining context awareness
"""
import ast
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Any

import chromadb
import javalang
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.workflow import Workflow


@dataclass
class CodeElement:
    """Represents a code element (class, method, function) with metadata"""
    name: str
    type: str  # class, method, function, variable
    file_path: str
    start_line: int
    end_line: int
    content: str
    dependencies: List[str]
    doc_exists: bool
    language: str


class CodebaseAnalyzer:
    """Analyzes codebase and extracts code elements for documentation"""

    def __init__(self, root_dir: str):
        self.root_dir = Path(root_dir)
        self.supported_extensions = {'.py', '.java', '.kt', '.js', '.ts'}

    def analyze_codebase(self) -> List[CodeElement]:
        """Analyze entire codebase and return code elements"""
        elements = []

        for file_path in self._get_code_files():
            try:
                file_elements = self._analyze_file(file_path)
                elements.extend(file_elements)
            except Exception as e:
                print(f"Error analyzing {file_path}: {e}")

        return elements

    def _get_code_files(self) -> List[Path]:
        """Get all code files in the directory"""
        files = []
        for ext in self.supported_extensions:
            files.extend(self.root_dir.rglob(f"*{ext}"))
        return files

    def _analyze_file(self, file_path: Path) -> List[CodeElement]:
        """Analyze a single file and extract code elements"""
        extension = file_path.suffix.lower()

        if extension == '.py':
            return self._analyze_python_file(file_path)
        elif extension == '.java':
            return self._analyze_java_file(file_path)
        elif extension == '.kt':
            return self._analyze_kotlin_file(file_path)
        else:
            return []

    def _analyze_python_file(self, file_path: Path) -> List[CodeElement]:
        """Analyze Python file using AST"""
        elements = []

        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        try:
            tree = ast.parse(content)

            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    elements.append(self._create_python_element(
                        node, file_path, content, 'class'
                    ))
                elif isinstance(node, ast.FunctionDef):
                    elements.append(self._create_python_element(
                        node, file_path, content, 'function'
                    ))

        except SyntaxError as e:
            print(f"Syntax error in {file_path}: {e}")

        return elements

    def _create_python_element(self, node: ast.AST, file_path: Path,
                               content: str, element_type: str) -> CodeElement:
        """Create CodeElement from Python AST node"""
        lines = content.split('\n')
        start_line = node.lineno
        end_line = getattr(node, 'end_lineno', node.lineno)

        # Extract dependencies (imports, class inheritance, etc.)
        dependencies = self._extract_python_dependencies(node, content)

        # Check if documentation exists
        doc_exists = ast.get_docstring(node) is not None

        element_content = '\n'.join(lines[start_line - 1:end_line])

        return CodeElement(
            name=node.name,
            type=element_type,
            file_path=str(file_path),
            start_line=start_line,
            end_line=end_line,
            content=element_content,
            dependencies=dependencies,
            doc_exists=doc_exists,
            language='python'
        )

    def _analyze_java_file(self, file_path: Path) -> List[CodeElement]:
        """Analyze Java file using javalang"""
        elements = []

        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        try:
            tree = javalang.parse.parse(content)

            # Extract classes and methods
            for _, node in tree.filter(javalang.tree.ClassDeclaration):
                elements.append(self._create_java_element(
                    node, file_path, content, 'class'
                ))

            for _, node in tree.filter(javalang.tree.MethodDeclaration):
                elements.append(self._create_java_element(
                    node, file_path, content, 'method'
                ))

        except Exception as e:
            print(f"Error parsing Java file {file_path}: {e}")

        return elements

    def _analyze_kotlin_file(self, file_path: Path) -> List[CodeElement]:
        """Analyze Kotlin file using regex patterns (simplified)"""
        elements = []

        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Simple regex patterns for Kotlin (can be enhanced with proper parser)
        class_pattern = r'(?:class|object|interface)\s+(\w+)'
        function_pattern = r'fun\s+(\w+)\s*\('

        lines = content.split('\n')

        for i, line in enumerate(lines):
            # Find classes
            class_match = re.search(class_pattern, line)
            if class_match:
                elements.append(CodeElement(
                    name=class_match.group(1),
                    type='class',
                    file_path=str(file_path),
                    start_line=i + 1,
                    end_line=i + 1,  # Simplified
                    content=line,
                    dependencies=[],
                    doc_exists='/**' in line or '/*' in line,
                    language='kotlin'
                ))

            # Find functions
            func_match = re.search(function_pattern, line)
            if func_match:
                elements.append(CodeElement(
                    name=func_match.group(1),
                    type='function',
                    file_path=str(file_path),
                    start_line=i + 1,
                    end_line=i + 1,  # Simplified
                    content=line,
                    dependencies=[],
                    doc_exists='/**' in line or '/*' in line,
                    language='kotlin'
                ))

        return elements

    def _extract_python_dependencies(self, node: ast.AST, content: str) -> List[str]:
        """Extract dependencies for Python code element"""
        dependencies = []

        # Extract imports at module level
        tree = ast.parse(content)
        for n in ast.walk(tree):
            if isinstance(n, ast.Import):
                for alias in n.names:
                    dependencies.append(alias.name)
            elif isinstance(n, ast.ImportFrom):
                if n.module:
                    dependencies.append(n.module)

        # Extract class inheritance
        if isinstance(node, ast.ClassDef):
            for base in node.bases:
                if isinstance(base, ast.Name):
                    dependencies.append(base.id)

        return dependencies


class DocumentationGenerator:
    """Generates documentation based on language standards"""

    DOCUMENTATION_TEMPLATES = {
        'python': {
            'class': '''"""
{description}

{attributes_section}
{methods_section}
{examples_section}
{see_also_section}
"""''',
            'function': '''"""
{description}

{args_section}
{returns_section}
{raises_section}
{examples_section}
{see_also_section}
"""'''
        },
        'java': {
            'class': '''/**
 * {description}
 *
{author_section}
{since_section}
{see_also_section}
 */''',
            'method': '''/**
 * {description}
 *
{params_section}
{returns_section}
{throws_section}
{see_also_section}
 */'''
        },
        'kotlin': {
            'class': '''/**
 * {description}
 *
{author_section}
{since_section}
{see_also_section}
 */''',
            'function': '''/**
 * {description}
 *
{param_section}
{return_section}
{throws_section}
{see_also_section}
 */'''
        }
    }

    def generate_documentation(self, element: CodeElement,
                               context_info: Dict[str, Any]) -> str:
        """Generate documentation for a code element"""
        language = element.language
        element_type = element.type

        if language not in self.DOCUMENTATION_TEMPLATES:
            return ""

        template = self.DOCUMENTATION_TEMPLATES[language].get(element_type, "")
        if not template:
            return ""

        # Format template with context information
        return template.format(**context_info)


# Agno Agents Definition
class CodeAnalysisAgent(Agent):
    """Agent responsible for analyzing codebase structure"""

    def __init__(self):
        super().__init__(
            name="CodeAnalysisAgent",
            role="Codebase Analyzer",
            goal="Analyze codebase structure and extract code elements",
            backstory="Expert in static code analysis across multiple programming languages"
        )
        self.analyzer = None

    def setup_analyzer(self, root_dir: str):
        """Setup the codebase analyzer"""
        self.analyzer = CodebaseAnalyzer(root_dir)

    def analyze_codebase(self, root_dir: str) -> List[CodeElement]:
        """Analyze the codebase and return elements"""
        if not self.analyzer:
            self.setup_analyzer(root_dir)
        return self.analyzer.analyze_codebase()


class DocumentationAgent(Agent):
    """Agent responsible for generating documentation"""

    def __init__(self):
        super().__init__(
            name="DocumentationAgent",
            role="Documentation Generator",
            goal="Generate high-quality documentation following language standards",
            backstory="Expert technical writer specializing in API documentation and code comments",
            llm=OpenAIChat(model="gpt-4")
        )
        self.doc_generator = DocumentationGenerator()

    def generate_docs(self, element: CodeElement,
                      related_elements: List[CodeElement]) -> str:
        """Generate documentation for a code element with context"""

        # Prepare context information
        context_info = {
            'description': f'TODO: Add description for {element.name}',
            'see_also_section': self._generate_see_also(element, related_elements),
            'examples_section': '',
            'author_section': '@author Generated Documentation',
            'since_section': '@since 1.0'
        }

        # Language-specific sections
        if element.language == 'python':
            context_info.update({
                'args_section': self._generate_python_args(element),
                'returns_section': 'Returns:\n    TODO: Describe return value',
                'raises_section': '',
                'attributes_section': '',
                'methods_section': ''
            })
        elif element.language in ['java', 'kotlin']:
            context_info.update({
                'params_section': self._generate_java_params(element),
                'param_section': self._generate_java_params(element),
                'returns_section': '@return TODO: Describe return value',
                'return_section': '@return TODO: Describe return value',
                'throws_section': '',
            })

        return self.doc_generator.generate_documentation(element, context_info)

    def _generate_see_also(self, element: CodeElement,
                           related_elements: List[CodeElement]) -> str:
        """Generate see also section with related elements"""
        see_also = []

        for dep in element.dependencies:
            matching_elements = [e for e in related_elements if e.name == dep]
            if matching_elements:
                if element.language == 'python':
                    see_also.append(f'    {dep}: Related class/function')
                else:
                    see_also.append(f' * @see {dep}')

        return '\n'.join(see_also) if see_also else ''

    def _generate_python_args(self, element: CodeElement) -> str:
        """Generate Python args section"""
        # Simple extraction - can be enhanced with AST analysis
        if 'def ' in element.content and '(' in element.content:
            return 'Args:\n    TODO: Document parameters'
        return ''

    def _generate_java_params(self, element: CodeElement) -> str:
        """Generate Java/Kotlin params section"""
        if '(' in element.content:
            return ' * @param TODO Document parameters'
        return ''


class FileWriterAgent(Agent):
    """Agent responsible for writing documented files"""

    def __init__(self):
        super().__init__(
            name="FileWriterAgent",
            role="File Writer",
            goal="Write back documented code files without altering original code",
            backstory="Expert in file I/O operations and maintaining code integrity"
        )

    def write_documented_file(self, element: CodeElement, documentation: str):
        """Write documentation to file without altering original code"""

        with open(element.file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        # Insert documentation before the code element
        insert_line = element.start_line - 1

        # Format documentation according to language
        if element.language == 'python':
            # For Python, insert docstring inside function/class
            if element.type in ['class', 'function']:
                # Find the line after the definition
                for i in range(insert_line, len(lines)):
                    if ':' in lines[i]:
                        insert_line = i + 1
                        break
                doc_lines = [f'    {line}\n' for line in documentation.split('\n')]
            else:
                doc_lines = [f'{line}\n' for line in documentation.split('\n')]
        else:
            # For Java/Kotlin, insert before the element
            doc_lines = [f'{line}\n' for line in documentation.split('\n')]

        # Insert documentation
        for i, doc_line in enumerate(doc_lines):
            lines.insert(insert_line + i, doc_line)

        # Write back to file
        with open(element.file_path, 'w', encoding='utf-8') as f:
            f.writelines(lines)


# RAG Knowledge Base Setup
class CodeKnowledgeBase:
    """RAG-based knowledge base for code context"""

    def __init__(self, persist_directory: str = "./chroma_db"):
        self.client = chromadb.PersistentClient(path=persist_directory)
        self.collection = self.client.get_or_create_collection(
            name="code_knowledge",
            metadata={"description": "Codebase knowledge for documentation"}
        )

    def add_code_elements(self, elements: List[CodeElement]):
        """Add code elements to knowledge base"""
        documents = []
        metadatas = []
        ids = []

        for i, element in enumerate(elements):
            # Create searchable document
            doc_content = f"""
            Name: {element.name}
            Type: {element.type}
            Language: {element.language}
            File: {element.file_path}
            Dependencies: {', '.join(element.dependencies)}
            Content: {element.content}
            """

            documents.append(doc_content)
            metadatas.append({
                "name": element.name,
                "type": element.type,
                "language": element.language,
                "file_path": element.file_path,
                "has_docs": element.doc_exists
            })
            ids.append(f"{element.file_path}_{element.name}_{i}")

        self.collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )

    def search_related_elements(self, element: CodeElement,
                                top_k: int = 5) -> List[Dict]:
        """Search for related code elements"""
        query = f"{element.name} {element.type} {' '.join(element.dependencies)}"

        results = self.collection.query(
            query_texts=[query],
            n_results=top_k,
            where={"language": element.language}
        )

        return results


# Main Workflow Definition
class CodeDocumentationWorkflow(Workflow):
    """Main workflow for code documentation"""

    def __init__(self, root_directory: str):
        # Initialize agents
        self.code_analyzer = CodeAnalysisAgent()
        self.doc_generator = DocumentationAgent()
        self.file_writer = FileWriterAgent()

        # Initialize knowledge base
        self.knowledge_base = CodeKnowledgeBase()

        # Setup workflow
        super().__init__(
            name="CodeDocumentationWorkflow",
            agents=[self.code_analyzer, self.doc_generator, self.file_writer],
            tasks=[],
            verbose=True
        )

        self.root_directory = root_directory

    def execute(self):
        """Execute the documentation workflow"""
        print(f"Starting documentation workflow for: {self.root_directory}")

        # Step 1: Analyze codebase
        print("Step 1: Analyzing codebase...")
        elements = self.code_analyzer.analyze_codebase(self.root_directory)
        print(f"Found {len(elements)} code elements")

        # Step 2: Build knowledge base
        print("Step 2: Building knowledge base...")
        self.knowledge_base.add_code_elements(elements)

        # Step 3: Generate documentation for elements without docs
        print("Step 3: Generating documentation...")
        undocumented_elements = [e for e in elements if not e.doc_exists]
        print(f"Found {len(undocumented_elements)} undocumented elements")

        for element in undocumented_elements:
            print(f"Documenting {element.name} in {element.file_path}")

            # Get related elements from knowledge base
            related_results = self.knowledge_base.search_related_elements(element)
            related_elements = elements  # Use all elements for now

            # Generate documentation
            documentation = self.doc_generator.generate_docs(element, related_elements)

            if documentation.strip():
                # Write documentation to file
                self.file_writer.write_documented_file(element, documentation)
                print(f"✓ Documented {element.name}")
            else:
                print(f"✗ Failed to generate docs for {element.name}")

        print("Documentation workflow completed!")


# Usage Example
def main():
    """Main function to run the documentation workflow"""

    # Configure the root directory of your codebase
    ROOT_DIRECTORY = "/path/to/your/codebase"

    # Create and execute the workflow
    workflow = CodeDocumentationWorkflow(ROOT_DIRECTORY)
    workflow.execute()


if __name__ == "__main__":
    # Example usage
    import sys

    if len(sys.argv) > 1:
        root_dir = sys.argv[1]
    else:
        root_dir = input("Enter the root directory of your codebase: ")

    workflow = CodeDocumentationWorkflow(root_dir)
    workflow.execute()
