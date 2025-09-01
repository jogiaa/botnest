from dataclasses import dataclass, field
from typing import List

from poc_agno.code_documenter_ast.workers.kotlin_ast_analyser.model import FunctionData
from poc_agno.code_documenter_ast.workers.kotlin_ast_analyser.model.variable_data import VariableData


@dataclass
class KotlinAnalysisData:
    """
    Data class to hold all extracted information from Kotlin code analysis.
    
    This class serves as the primary container for all structural information
    extracted from Kotlin source code by the KotlinASTAnalyzer. It stores
    comprehensive details about packages, classes, functions, properties,
    and relationships.
    
    Attributes:
        filename (str): The name of the analyzed Kotlin source file
        package_name (str): The package declaration of the Kotlin code
        imports (List[str]): List of import statements found in the code
        name (str): The name of the main class, interface, or object
        type (str): The type of declaration (e.g., 'class', 'interface', 
                   'data class', 'enum', 'object', 'sealed class')
        annotations (List[str]): List of annotations applied to the declaration
        visibility (str): Visibility modifier ('private', 'internal', 'public')
        members (List[VariableData]): List of class properties and member variables
        constructor_param_type (List[VariableData]): List of primary constructor parameters
        extends (str): The superclass that this declaration extends
        implements (List[str]): List of interfaces that this declaration implements
        functions (List[FunctionData]): List of function declarations within the class
        uses (List[str]): List of dependencies or types used by this declaration
        used_by (List[str]): List of types that use or depend on this declaration
    
    Example:
        >>> analysis = KotlinAnalysisData()
        >>> analysis.name = "MyClass"
        >>> analysis.type = "data class"
        >>> analysis.visibility = "public"
        >>> print(f"Found {analysis.type}: {analysis.name}")
        Found data class: MyClass
    """
    filename: str = ""
    package_name: str = ""
    imports: List[str] = field(default_factory=list)
    name: str = ""
    type: str = ""  # class|interface|data class|enum|object|sealed class etc.
    annotations: List[str] = field(default_factory=list)
    visibility: str = "public"  # private | internal | public
    members: List[VariableData] = field(default_factory=list)
    constructor_param_type: List[VariableData] = field(default_factory=list)
    extends: str = ""
    implements: List[str] = field(default_factory=list)
    functions: List[FunctionData] = field(default_factory=list)  # [{'name','visibility','return_type','param_types'}, ...]
    uses: List[str] = field(default_factory=list)
    used_by: List[str] = field(default_factory=list)
