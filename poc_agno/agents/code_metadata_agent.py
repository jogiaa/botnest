import datetime
from dataclasses import Field
from textwrap import dedent
from typing import Literal, Optional, List

from pydantic import BaseModel

class ClassMeta(BaseModel):
    name: str  # Simple class name (e.g., "MyClass")
    type: Literal["Class", "Interface", "Enum", "SealedClass", "Object", "Annotation"]
    package_name: Optional[str] = None
    summary: str  # 1-2 line description
    extends: List[str] = []
    implements: List[str] = []
    uses: List[str] = []
    used_in: List[str] = []  # List of other classes that use this one
    external_dependencies: List[str] = []
    defined_in: str  # Relative file path (to disambiguate duplicates)
    last_updated: datetime = Field(default_factory=datetime.utcnow)

    def update_used_in(self, user_class: str):
        if user_class not in self.used_in:
            self.used_in.append(user_class)

instruction_v1 = dedent("""
name: ClassSummaryAgent
description: |
  Analyze source files one at a time and maintain a cumulative memory of class-level metadata and inter-class dependencies.
  For each file, extract structured summaries of relevant types and update existing memory as needed.

goals:
  - Extract class-level metadata from a single source file (Kotlin/Java style)
  - Update existing records in memory if a class is referenced ("used")
  - Maintain a cumulative view of all types across files

rules:
  - Only consider non-test source files
  - Do not include code or formatting
  - Do not summarize test classes, test methods, or test-related files

for_each_file:
  extract:
    - type: |
        One of: Class, Interface, Enum, SealedClass, Object, Annotation
    - name: The name of the type
    - package_name: Package declaration if present
    - summary: 1–2 sentence explanation of its purpose
    - extends: List of parent classes (if any)
    - implements: List of implemented interfaces (if any)
    - uses: Other internal or external types used within this file
    - used_in: Automatically update any previously seen class that is used here
    - external_dependencies: List of third-party or standard library features used
    - defined_in: Relative file path (e.g., src/main/java/.../Class.kt)

memory:
  strategy: |
    - Keep a running list of previously summarized classes
    - When a known class is found in `uses`, update its `used_in` list with the current class
    - Avoid duplicate summaries unless metadata has changed
    - Use memory to establish a project-wide class dependency graph

edge_cases:
  - If a file contains no relevant class-level definitions, return: "Skip"
  - Ignore import-only references unless the class is clearly used in the body

response_format: Structured YAML or JSON (as configured), one entry per class

""")

