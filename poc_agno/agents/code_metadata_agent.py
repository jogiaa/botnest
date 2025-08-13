from datetime import datetime, timezone
from pprint import pprint
from textwrap import dedent
from typing import Literal, Optional, List

from agno.agent import Agent
from pydantic import BaseModel, Field

from poc_agno.llm_model_config import code_model


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
    last_updated: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    def update_used_in(self, user_class: str):
        if user_class not in self.used_in:
            self.used_in.append(user_class)


instruction_v1 = dedent("""
name: class_meta_store_agent
description: >
  Analyze a single source file to extract class-level metadata and update the global memory store
  with accurate summaries, structure, and inter-class dependencies using the ClassMeta model.

tasks:

  - Parse the source code and extract all top-level types such as:
      - Class
      - Interface
      - Enum
      - Sealed class
      - Object
      - Annotation

  - For each extracted type:
      - Determine its `name` (simple class name, e.g., `MyClass`)
      - Classify the `type` using standard categories: Class, Interface, Enum, SealedClass, Object, Annotation
      - Identify the `package_name` (if defined)
      - Summarize its purpose in 1–2 lines (`summary`)
      - Extract the names of classes it:
          - Extends (inherits from)
          - Implements (interfaces)
          - Uses (instantiates or calls from other classes)
      - Identify `external_dependencies`, such as Java/Kotlin standard libraries or third-party imports
      - Track the file it was defined in as `defined_in` using the provided `filepath`
      - Set `last_updated` as current UTC timestamp

output:
  - Returns a list of updated or created `ClassMeta` objects from this file

constraints:
  - Do not include code content or reformat any code
  - Do not summarize test classes or methods
  - Ensure consistency in class references (case-sensitive matching)

""")

code_meta_agent = Agent(
    name="Code Structure Analyzer",
    role="Analyze source code and summarize structure, dependencies, and libraries used",
    model=code_model,
    response_model=ClassMeta,
    reasoning=True,
    # debug_mode=True,
    instructions=instruction_v1
)

if __name__ == "__main__":
    prompt = dedent(""" Add this class to the metadata graph
    package org.koin.example.two

    import kotlin.random.Random

    data class Casing(val capacity:Int) 

    class Processor {
        private val capacity:Int

        fun startProcessing(type: ProcessorType): Int {
            return when (type) {
                Alpha -> calculateDelay(type.numberOfProcessors)
                Beta -> type.numberOfProcessors
                Gamma -> type.numberOfProcessors + 10
            }
        }

        private fun calculateDelay(processors: Int): Int {
            return processors * Random.Default.nextInt() 
        }
    }
    """)

    response = code_meta_agent.run(prompt)
    print("*********************")
    pprint(response.content)

    print("*********************")

    pprint(response)
