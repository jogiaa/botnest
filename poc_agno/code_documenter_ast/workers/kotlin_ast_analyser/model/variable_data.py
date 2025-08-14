from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class VariableData:
    """
    Data class representing a variable or property declaration in Kotlin code.
    
    This class stores information about individual variables, properties,
    or constructor parameters extracted from Kotlin source code. It captures
    the essential metadata needed to understand the structure and behavior
    of each variable declaration.
    
    Attributes:
        name (str): The name of the variable or property
        type (str): The data type of the variable (e.g., 'String', 'Int', 'List<String>')
        annotations (List[str]): List of annotations applied to the variable
        visibility (str): Visibility modifier ('private', 'internal', 'public', 'protected')
        default_value (Optional[str]): The default value assigned to the variable, if any
    
    Example:
        >>> var_data = VariableData()
        >>> var_data.name = "userName"
        >>> var_data.type = "String"
        >>> var_data.visibility = "private"
        >>> var_data.default_value = "Anonymous"
        >>> print(f"{var_data.visibility} {var_data.type} {var_data.name} = {var_data.default_value}")
        private String userName = Anonymous
    """
    name: str = ""
    type: str = ""
    annotations: List[str] = field(default_factory=list)
    visibility: str = field(default="public")
    default_value: Optional[str] = None
