from dataclasses import dataclass, field
from typing import List

from .variable_data import VariableData


@dataclass
class FunctionData:
    """
    Data class representing a function or method declaration in Kotlin code.
    
    This class stores information about individual function declarations
    extracted from Kotlin source code. It captures the essential metadata
    needed to understand the signature and behavior of each function.
    
    Attributes:
        name (str): The name of the function or method
        parameters (str): The parameter list of the function (e.g., 'name: String, age: Int')
        annotations (List[str]): List of annotations applied to the function
        visibility (str): Visibility modifier ('private', 'internal', 'public', 'protected')
        return_type (str): The return type of the function (defaults to 'Unit' for void functions)
    
    Example:
        >>> func_data = FunctionData()
        >>> func_data.name = "calculateSum"
        >>> func_data.parameters = "(a: Int, b: Int)"
        >>> func_data.return_type = "Int"
        >>> func_data.visibility = "public"
        >>> print(f"{func_data.visibility} fun {func_data.name}({func_data.parameters}): {func_data.return_type}")
        public fun calculateSum(a: Int, b: Int): Int
    """
    name: str = ""
    parameters: List[VariableData] = field(default_factory=list)
    annotations: List[str] = field(default_factory=list)
    visibility: str = field(default="public")
    return_type: str = field(default="Unit")
