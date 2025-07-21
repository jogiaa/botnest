from pprint import pprint
from textwrap import dedent
from typing import List, Dict

from pydantic import BaseModel
from agno.agent import Agent

from poc_agno.llm_model_config import code_model

instructions_v1 = dedent("""
        You will be given source code for a single file.
        Your task is to analyze the code and extract the following:
        
        1. All class names and their purpose (1-2 lines each)
        2. All functions/methods and what they do (1-2 lines each)
        3. Internal dependencies (e.g., which class calls which function)
        4. External libraries used and what features/functions are being used from each
        5. DO NOT include code or reformat it
        6. DO NOT mention or summarize test classes or test methods
        
        Return this as structured bullet points grouped by:
        - Package Name
        - Classes
        - Functions
        - Internal Relationships
        - External Libraries
        
        If the file has no meaningful content, just say "Skip"
""")

instructions_v2 = dedent("""
        You will be given the source code of a single file.
        Your task is to analyze the code and extract the following insights in a structured and consistent way.
        
        Return the following:
        
        1. 📦 **Package Name** (if applicable)
        2. 🧱 **Classes**:
           - List all class names
           - For each class, describe its purpose in 1–2 lines
        3. 🧰 **Functions/Methods**:
           - List each function or method
           - Include the class it belongs to (if any)
           - Describe its behavior in 1–2 lines
        4. 🔁 **Internal Dependencies**:
           - Describe relationships between classes in this file (e.g., which class uses another, inheritance, method calls)
           - Format: `ClassA → ClassB` or `ClassX extends BaseX`
        5. 🌐 **External Libraries Used**:
           - List all imported libraries
           - For each, mention which class/function/method uses it and for what purpose
        6. 📊 **Class Dependency Graph Info** (for global aggregation):
           - For each class:
             ```json
             {
               "class": "MyClass",
               "extends": "BaseClass",
               "implements": ["SomeInterface"],
               "uses": ["SomeOtherClass", "Logger"],
               "defined_in": "relative/path/to/this_file"
             }
             ```
        
        ⚠️ Do NOT:
        - Include or reformat the actual code
        - Summarize or mention test classes or test methods
        
        Return your output using **structured bullet points**, clearly grouped by the categories above.
        If the file has no meaningful content, just return `"Skip"` (without quotes).

""")

instructions_v3 = dedent("""
        You will be given the source code of a single file.
        Your task is to analyze the code and extract the following insights in a structured and consistent way.
        **Class Dependency Graph Info** (for global aggregation):
           - For each class present in file return the following 
        ```json
               {
                  "type": "Classification of Type Declarations like class, interface etc",
                  "package_name": (if applicable),
                  "class_name": "MyClass",
                  "name": "NameOfTheClass",
                  "summary": "1-2 line description of its purpose",
                  "extends": ["ParentClass"],
                  "implements": ["Interface1", "Interface2"],
                  "uses": ["OtherClass1", "OtherClass2", "LibraryClass"],
                  "external_dependencies": ["Third party or language's internal libraries"],
                  "defined_in": "relative/path/to/this_file"
              }
        ```
        
        
        ⚠️ Do NOT:
        - Include or reformat the actual code
        - Summarize or mention test classes or test methods
""")

instructions_v4 = dedent("""
        You will be given the source code of a single file.
        Your task is to analyze the code and extract the following insights in a structured and consistent way.

        Return the following:

        1. 📦 **Package Name** (if applicable)
        2. ▶︎ **Classification of Type Declarations**
            - If its a **class** or **enum** or **interface** etc
        3. 🧱 **Classes**:
           - List all class names
           - For each class, describe its purpose in 1–2 lines
        4. 🧰 **Functions/Methods**:
           - List each function or method
           - Include the class it belongs to (if any)
           - Describe its behavior in 1–2 lines
        5. 🔁 **Internal Dependencies**:
           - Describe relationships between classes in this file (e.g., which class uses another, inheritance, method calls)
           - Format: `ClassA → ClassB` or `ClassX extends BaseX`
        6. 🌐 **External Libraries Used**:
           - List all imported libraries
           - For each, mention which class/function/method uses it and for what purpose
        7. 📊 **Class Dependency Graph Info** (for global aggregation):
           - For each class:
             ```json
             {
                    "type": "Class" | "Interface" | "Enum" | "SealedClass" | "Object" | "Annotation",
                    "package_name": (if applicable),
                    "name": "MyClass",
                    "extends": "BaseClass",
                    "implements": ["SomeInterface"],
                    "uses": ["SomeOtherClass", "Logger"],
                    "defined_in": "relative/path/to/this_file"
             }
             ```

        ⚠️ Do NOT:
        - Include or reformat the actual code
        - Summarize or mention test classes or test methods

        Return your output using **structured bullet points**, clearly grouped by the categories above.
        If the file has no meaningful content, just return `"Skip"` (without quotes).

""")

instructions_v5 = dedent("""
        You are a code analysis agent designed to process one Kotlin file at a time.

        Your goal is to extract class-level metadata and maintain a structured, cumulative summary across all files.
        
        For each file, extract the following details **per top-level declaration**:
        
        1. `type`: One of `class`, `interface`, `data class`, `enum`, `object`, `sealed class`, `annotation`
        2. `name`: Name of the class/interface/enum/etc.
        3. `package_name`: Extract from the `package` statement
        4. `summary`: A 1–2 line natural language description of the purpose of the class
        5. `extends`: Superclass this class extends (if any)
        6. `implements`: Interfaces this class implements (if any)
        7. `uses`: Other classes/types referenced in the body of this file (ignore basic types like String, Int)
        8. `external_dependencies`: Classes or functions imported from external libraries (standard or third-party)
        9. `used_in`: Leave empty (this will be updated from other class references)
        10. `defined_in`: The full relative file path (provided as context)
        
        Your response must be a **JSON array of objects**, one per declaration, using this format:
        
        ```json
        {
          "type": "class",
          "name": "CapitalizedFileProcessorImpl",
          "package_name": "org.jay.sample.impl",
          "summary": "Processes input files and capitalizes their content.",
          "extends": "",
          "implements": ["FileProcessor"],
          "uses": ["Input", "Logger"],
          "external_dependencies": ["java.io.File", "java.io.IOException"],
          "used_in": [],
          "defined_in": "main/java/org/jay/sample/impl/CapitalizedFileProcessorImpl.kt"
        }
        
        ⚠️ Do NOT:
        - Do NOT include code.
        - Skip test classes.
        - Be accurate and concise.

""")


instructions_v6 = dedent("""
    You are a Kotlin static analyzer. Each time you are given a new Kotlin file, extract and summarize any classes, interfaces, or data classes it contains. Keep a cumulative memory of all previously seen class/interface summaries and update them as new relationships are discovered.
    
    🔁 **Maintain Persistent State**:
    - Track all summaries in a cumulative list across files.
    - When a file references a class/interface already summarized earlier, update the earlier object to:
    - Add this new class's name to its "used_in" array (if not already present).
    - Ensure that each summary object appears only once in the final output.
    
    🧠 **Class Dependency Graph Info** (for global aggregation):
    ```json
        {
          "type": "Class" | "Interface" | "Enum" | "SealedClass" | "Object" | "Annotation",
          "package_name": "<package declared in file>",
          "summary": "<concise explanation of the purpose of the class>",
          "name": "<class/interface name>",
          "extends": "<superclass name if any, empty string if none>",
          "implements": ["<interfaces implemented>"],
          "uses": ["<classes/interfaces used>"],
          "used_in": ["<classes/interfaces that use this one>"],
          "external_dependencies": ["<non-project imports>"],
          "defined_in": "<filepath relative to source root>"
        }
    ```
    🔍 Relationship Rules:
    - A class "uses" another if it references it in method arguments, properties, constructors, or internal logic.
    - A class is "used_in" by another if the other class references it.
    - If class B uses class A, then:
        - Add "A" to B.uses
        - Add "B" to A.used_in
    - Keep both relationships synchronized across passes.
    
    📂 Filepath Convention:
    ```
    main/java/<package-path>/<ClassName>.kt
    ```
    For example:
    package org.jay.sample → main/java/org/jay/sample/Input.kt
    
    🔁 Final Output Format:
    - After analyzing each file, output the complete, updated JSON array of all summaries seen so far—not just the current file’s. This allows tracking of references and usage across the full codebase.
    
    ⚠️ Do NOT:
    - Do NOT include code.
    - Skip test classes.
    - Be accurate and concise.
""")

instructions_v7 = dedent("""
name: SourceSummarizerAgent
description: >
  An Agno agent that processes one source file at a time and incrementally builds
  a structured summary of all types (classes, interfaces, etc.), including inter-class
  dependencies and usage relationships across the codebase.

input_format: |
  The input will be the full source code of a single file.

instructions: |
  Analyze the code and extract all **type declarations**, including:
    - Class
    - Interface
    - Enum
    - Sealed Class
    - Object
    - Annotation

  For each declared type, identify and record:
    - The name of the type
    - The kind of type (e.g. class, interface, enum, etc.)
    - The package it belongs to (if specified)
    - A short 1–2 line description of its purpose
    - Any parent classes it extends
    - Any interfaces it implements
    - Any other classes or types it uses or depends on
    - Any third-party or built-in libraries it depends on
    - The relative file path where this type is defined


  Additionally:
    - Skip any test classes or test methods (e.g. classes or files related to unit testing)
    - Do not include source code or reformat it
    - Focus only on structural and semantic metadata

output_handling: |
  The agent should maintain memory of all processed types.

  When a type references another type that was previously summarized:
    - Update the referenced type by appending the current type to its `used_in` list
    - Do not overwrite the type's original summary, name, or location

  When processing a new type:
    - Merge new information into memory while preserving previously stored fields
    - Ensure fields like `uses`, `implements`, and `external_dependencies` accumulate without duplication

goal: >
  The final result should be a comprehensive, up-to-date dependency and type map
  of the entire codebase, without duplicating or re-parsing earlier summaries.
  The output should be clean, minimal, and focused on helping a developer
  understand how all types relate to one another across multiple source files.
""")

instructions_v8 = dedent("""
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

response_format: Structured YAML ,one entry per class

""")

instructions_v9 = dedent("""
""")


class SummaryResult(BaseModel):
    file_path: str
    package_name: str
    overall_summary: str
    external_libraries: List[str]
    function_name_and_summary: List[Dict[str,str]]
    members_summary: Dict[str, str]

code_summary_agent = Agent(
    name="Code Structure Analyzer",
    role="Analyze source code and summarize structure, dependencies, and libraries used",
    model=code_model,
    # response_model=SummaryResult,
    instructions= instructions_v7
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

    response = code_summary_agent.run(prompt)
    print("*********************"   )
    pprint(response.content)

    print("*********************")

    pprint(response)
