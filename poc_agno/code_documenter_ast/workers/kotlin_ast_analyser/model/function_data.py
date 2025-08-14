from dataclasses import dataclass, field
from typing import List


@dataclass
class FunctionData:
    name: str = ""
    parameters: str = ""
    annotations: List[str] = field(default_factory=list)
    visibility: str = field(default="public")
    return_type: str = field(default="Unit")
