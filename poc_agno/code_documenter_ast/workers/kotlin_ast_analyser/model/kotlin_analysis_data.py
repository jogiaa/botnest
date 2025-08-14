from dataclasses import dataclass, field
from typing import List

from poc_agno.code_documenter_ast.workers.kotlin_ast_analyser.model import FunctionData
from poc_agno.code_documenter_ast.workers.kotlin_ast_analyser.model.variable_data import VariableData


@dataclass
class KotlinAnalysisData:
    """Data class to hold all extracted information."""
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
    functions: List[FunctionData] = field(
        default_factory=list)  # [{'name','visibility','return_type','param_types'}, ...]
    uses: List[str] = field(default_factory=list)
    used_by: List[str] = field(default_factory=list)
