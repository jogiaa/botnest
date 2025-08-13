from dataclasses import dataclass, field
from typing import List, Dict


@dataclass
class KotlinAnalysis:
    """Data class to hold all extracted information."""
    filename: str = ""
    package_name: str = ""
    imports: List[str] = field(default_factory=list)
    name: str = ""
    type: str = ""  # class or interface or data class or enum or object
    visibility: str = ""  # private | internal | public
    functions: List[Dict] = field(default_factory=list)
    uses: List[str] = field(default_factory=list)
