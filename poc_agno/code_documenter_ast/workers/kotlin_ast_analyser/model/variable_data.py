from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class VariableData:
    name: str = ""
    type: str = ""
    annotations: List[str] = field(default_factory=list)
    visibility: str = field(default="public")
    default_value: Optional[str] = None
