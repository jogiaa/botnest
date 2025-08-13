from dataclasses import dataclass, field
from pprint import pprint
from typing import List, Optional

import tree_sitter_kotlin
from tree_sitter import Language, Parser, Node, Query, QueryCursor


@dataclass
class FunctionData:
    name: str = ""
    parameters: str = ""
    annotations: List[str] = field(default_factory=list)
    visibility: str = field(default="public")
    return_type: str = field(default="Unit")


@dataclass
class VariableData:
    name: str = ""
    type: str = ""
    annotations: List[str] = field(default_factory=list)
    visibility: str = field(default="public")
    default_value: Optional[str] = None


@dataclass
class KotlinAnalysis:
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


class KotlinASTAnalyzer:
    PACKAGE_QUERY = """
    ;; Package declaration
    (package_header (qualified_identifier) @package)
    """

    IMPORT_QUERY = """
    ; Matches normal import statements
    (import (qualified_identifier) @import)
    """

    HIGH_LEVEL_CLASS_QUERY = """
    (class_declaration
        (modifiers
            (annotation)? @class.annotation*
            (visibility_modifier)? @class.visibility
            (class_modifier)? @class.modifier
        )?
        (identifier) @type.name
        (class_body)? @class.body
    )
    """

    EXTENDS_IMPLEMENTS_QUERY = """
    (delegation_specifiers
        (delegation_specifier 
            (constructor_invocation 
                (user_type (identifier) @extends)
            )
        )
        (delegation_specifier 
            (user_type 
                (identifier) @implements
            )*
        )
    )
    """

    FUNCTION_QUERY = """
    (function_declaration
            (modifiers
                (annotation)? @function.annotation
                (visibility_modifier)? @function.visibility
            )?
            (identifier) @function.name
            (function_value_parameters) @function.params
            [
                (user_type (identifier) @function.return_type)
                (nullable_type (user_type (identifier) @function.return_type))
            ]?
        )
    """

    MEMBERS_QUERY = """
    (property_declaration
        (modifiers
            (annotation)* @property.annotation
            (visibility_modifier)? @property.visibility
        )?
        (variable_declaration 
            (identifier) @property.name
            [
                (user_type 
                    (identifier) @property.type
                )
                (nullable_type 
                    (user_type 
                        (identifier) @property.type
                    )
                )
            ]
        )
        (_) @property.default
    )
    """

    CTOR_PARAMS_QUERY = """
    (primary_constructor
        (class_parameters 
            (class_parameter 
                (modifiers
                    (annotation)* @ctor.param.annotation
                    (visibility_modifier)? @ctor.param.visibility
                )?
                (identifier) @ctor.param.name
                [
                    (user_type 
                        (identifier) @ctor.param.type
                    )
                    (nullable_type 
                        (user_type 
                            (identifier) @ctor.param.type
                        )
                    )
                ]
            )?
        )
    )
    """

    OBJECT_QUERY = """
    (object_declaration
    (modifiers
        (class_modifier) @object.modifier
    )?
    (identifier) @object.name
    (delegation_specifiers
        (delegation_specifier
            (constructor_invocation
                (user_type
                    (identifier) @object.superclass
                )
            )
        )
    )?
)

    """

    def __init__(self):
        """
        Initialize the KotlinASTAnalyzer class with language and parser.
        """
        self.language = Language(tree_sitter_kotlin.language())
        self.parser = Parser()
        self.parser.language = self.language

    def analyze_kotlin_file(self, file_path: str,
                            source_bytes: bytes,
                            print_debug_info: bool = False
                            ) -> KotlinAnalysis:
        """
        Analyze a Kotlin code file.
        """
        kotlin_analysis = KotlinAnalysis()
        try:
            tree = self.parser.parse(source_bytes)
            root_node = tree.root_node
            if print_debug_info:
                print("=== DEBUGGING TREE STRUCTURE ===")
                self._print_tree(source_bytes=source_bytes, node=root_node)
                print("=== END DEBUG ===\n")

            self._start(root_node, kotlin_analysis)
            print("==" * 60)
            print("=" * 24 + "FINAL RESULT" + "=" * 24)
            print("==" * 60)
            pprint(kotlin_analysis)
            print("==" * 60)
        except Exception as err:
            print("*" * 4 + "ERROR" + "*" * 4)
            print(err)
            print("*" * 4 + "ERROR" + "*" * 4)

        return kotlin_analysis

    def _start(self, root_node: Node, kotlin_analysis: KotlinAnalysis):
        try:
            kotlin_analysis.imports = self._extract_imports_wq(root_node)
            kotlin_analysis.package_name = self._extract_package_name_wq(root_node)
            self._extract_high_level_declaration_wq(root_node, kotlin_analysis)
            kotlin_analysis.type = f"{kotlin_analysis.type} {self._extract_type(root_node)}".strip()

            self._extract_parents(root_node, kotlin_analysis)
            self._extract_members_wq(root_node, kotlin_analysis)
            self._extract_constructor_params_wq(root_node, kotlin_analysis)

        except Exception as err:
            print("=" * 40 + "ERROR" + "=" * 40)
            print(err)
            print("=" * 4 + "ERROR" + "=" * 40)

    def _extract_constructor_params_wq(self, root_node: Node, kotlin_analysis: KotlinAnalysis):
        print("*" * 4 + "Constructor PARAMS" + "*" * 4)
        cursor = self._create_query_cursor(self.CTOR_PARAMS_QUERY)
        matches = cursor.matches(root_node)
        for index, match in enumerate(matches):
            member_data = VariableData()
            pprint(f"{index}: {match}")
            captures_dict = match[1]
            if "ctor.param.name" in captures_dict:
                ctor_params = self._get_node_text(captures_dict["ctor.param.name"][0])
                member_data.name = ctor_params

            if "ctor.param.annotation" in captures_dict:
                for property_annotation_node in captures_dict["ctor.param.annotation"]:
                    annotation = self._get_node_text(property_annotation_node)
                    member_data.annotations.append(annotation)

            if "ctor.param.visibility" in captures_dict:
                member_data.visibility = self._get_node_text(captures_dict["ctor.param.visibility"][0])

            if "ctor.param.type" in captures_dict:
                member_data.type = self._get_node_text(captures_dict["ctor.param.type"][0])

            if "ctor.param.default" in captures_dict:
                member_data.default_value = self._get_node_text(captures_dict["ctor.param.default"][0])

            kotlin_analysis.constructor_param_type.append(member_data)

    def _extract_members_wq(self, root_node: Node, kotlin_analysis: KotlinAnalysis):
        print("*" * 4 + "EXTRACTING MEMBERS" + "*" * 4)
        cursor = self._create_query_cursor(self.MEMBERS_QUERY)
        matches = cursor.matches(root_node)
        for index, match in enumerate(matches):
            member_data = VariableData()
            pprint(f"{index}: {match}")
            captures_dict = match[1]
            if "property.annotation" in captures_dict:
                for property_annotation_node in captures_dict["property.annotation"]:
                    annotation = self._get_node_text(property_annotation_node)
                    member_data.annotations.append(annotation)

            if "property.visibility" in captures_dict:
                member_data.visibility = self._get_node_text(captures_dict["property.visibility"][0])

            if "property.name" in captures_dict:
                member_data.name = self._get_node_text(captures_dict["property.name"][0])

            if "property.type" in captures_dict:
                member_data.type = self._get_node_text(captures_dict["property.type"][0])

            if "property.default" in captures_dict:
                member_data.default_value = self._get_node_text(captures_dict["property.default"][0])

            kotlin_analysis.members.append(member_data)

    def _extract_package_name_wq(self, root_node: Node) -> Optional[str]:
        cursor = self._create_query_cursor(self.PACKAGE_QUERY)
        matches = cursor.matches(root_node)
        for index, match in enumerate(matches):
            pprint(f"{index}: {match}")
            captures_dict = match[1]
            return self._extract_package_name(captures_dict, index)

        return ""

    def _extract_imports_wq(self, root_node: Node) -> List[str]:
        imports = []
        cursor = self._create_query_cursor(self.IMPORT_QUERY)
        matches = cursor.matches(root_node)
        for index, match in enumerate(matches):
            pprint(f"{index}: {match}")
            captures_dict = match[1]
            import_name = self._extract_imports(captures_dict, index)
            if import_name != "":
                imports.append(import_name)

        return imports

    def _extract_type(self, node: Node):
        if node.type == "class_declaration":
            for child in node.children:
                if child.type in ("class", "interface"):
                    return child.type
        for child in node.children:
            result = self._extract_type(child)
            if result:
                return result
        return None

    def _extract_high_level_declaration_wq(self, root_node: Node, analysis: KotlinAnalysis):
        print("*" * 4 + "DETAILS " + "*" * 4)
        cursor = self._create_query_cursor(self.HIGH_LEVEL_CLASS_QUERY)
        matches = cursor.matches(root_node)
        for index, match in enumerate(matches):
            pprint(f"{index}: {match}")
            captures_dict = match[1]
            if "class.annotation" in captures_dict:
                anno_names = []
                for annotation_node in captures_dict["class.annotation"]:
                    anno = self._get_node_text(annotation_node)
                    print(f"annotation modifier: {anno}")
                    anno_names.append(anno)
                analysis.annotations = anno_names

            # visiblity modifier
            visibility_modifier = "public" if "class.visibility" not in captures_dict else \
                (self._get_node_text(captures_dict["class.visibility"][0]))
            # print(f"visibility_modifier = {visibility_modifier}")
            analysis.visibility = visibility_modifier

            # class modifier (data / sealed etc) to get info like 'data class' 'sealed class' etc.
            if "class.modifier" in captures_dict:
                class_modifier = self._get_node_text(captures_dict["class.modifier"][0])
                # print(f"class_modifier = {class_modifier}")
                analysis.type = class_modifier
            # name
            if "type.name" in captures_dict:
                interface_name = self._get_node_text(captures_dict["type.name"][0])
                # print(f"interface_name = {interface_name}")
                analysis.name = interface_name

            if "class.body" in captures_dict:
                # print(type(captures_dict["class.body"]))
                # print(captures_dict["class.body"][0])
                self._extract_functions_wq(captures_dict["class.body"][0], analysis)

    def _extract_parents(self, root_node, kotlin_analysis):
        print("*" * 4 + "PARENTS DETAILS " + "*" * 4)
        cursor = self._create_query_cursor(self.EXTENDS_IMPLEMENTS_QUERY)
        matches = cursor.matches(root_node)
        for index, match in enumerate(matches):
            pprint(f"{index}: {match}")
            captures_dict = match[1]
            print(captures_dict)
            if "extends" in captures_dict:
                kotlin_analysis.extends = self._get_node_text(captures_dict["extends"][0])

            if "implements" in captures_dict:
                kotlin_analysis.implements.append(self._get_node_text(captures_dict["implements"][0]))

    def _extract_functions_wq(self, root_node: Node, analysis: KotlinAnalysis) -> List[str]:
        print("*" * 4 + "FUNCTION DETAILS " + "*" * 4)
        cursor = self._create_query_cursor(self.FUNCTION_QUERY)
        matches = cursor.matches(root_node)
        for index, match in enumerate(matches):
            pprint(f"{index}: {match}")
            captures_dict = match[1]
            data = FunctionData()

            if "function.annotation" in captures_dict:
                for annotation_node in captures_dict["function.annotation"]:
                    data.annotations.append(self._get_node_text(annotation_node))

            if "function.name" in captures_dict:
                data.name = self._get_node_text(captures_dict["function.name"][0])

            if "function.visibility" in captures_dict:
                data.visibility = self._get_node_text(captures_dict["function.visibility"][0])

            if "function.params" in captures_dict:
                for param_node in captures_dict["function.params"]:
                    params = self._get_node_text(param_node)
                    data.parameters = params

            if "function.return_type" in captures_dict:
                data.return_type = self._get_node_text(captures_dict["function.return_type"][0])

            analysis.functions.append(data)

    def _extract_imports(self, captures_dict, index):
        print("*" * 4 + "IMPORTS" + "*" * 4)
        if "import" in captures_dict:
            import_name = self._get_node_text(captures_dict["import"][0])
            print(f"{index}: Import: {import_name}")
            return import_name
        else:
            return ""

    def _extract_package_name(self, captures_dict, index) -> str:
        print("*" * 4 + "PACKAGE NAME" + "*" * 4)
        if "package" in captures_dict:
            package_name = self._get_node_text(captures_dict["package"][0])
            print(f"{index}: Package: {package_name}")
            return package_name
        else:
            return ""

    def _create_query_cursor(self, query_text: str) -> QueryCursor:
        try:
            query = Query(self.language, query_text)
            return QueryCursor(query)
        except Exception as err:
            print("*" * 4 + "ERROR" + "*" * 4)
            print(err)
            print("*" * 4 + "ERROR" + "*" * 4)

    def _get_node_text(self, node) -> str:
        """Get text content of a node."""
        return node.text.decode('utf-8') if node else ""

    def _print_tree(self, source_bytes: bytes, node=None, indent=0, max_lines=2000):
        prefix = "  " * indent
        text = self._node_text(source_bytes, node).strip().splitlines()
        sample = text[0][:80] + ("..." if len(text[0]) > 80 else "") if text else ""
        print(f"{prefix}{node.type} [{node.start_point}..{node.end_point}] -- {sample}")
        for child in node.children:
            self._print_tree(source_bytes, child, indent + 1)

    def _node_text(self, source_bytes: bytes, node) -> str:
        return source_bytes[node.start_byte:node.end_byte].decode("utf-8")


def run_():
    print("--- Sample 1: Advanced Class Example with Generics & Annotations ---")
    file_path_1 = "src/main/kotlin/org/jay/sample/computing/ProcessorDelay.kt"
    source_code_1 = """
        @file:JvmName("ProcessingUtils")

package org.jay.sample.computing

import org.jay.sample.computing.categories.Chip
import org.jay.sample.pie.categories.Processor
import javax.inject.Inject
import kotlin.random.Random

@Deprecated("This class is deprecated")
class ProcessorDelay<T : Any, V>(
    delayFactor: Int,
    @Inject private val formFactor: FormFactor,
    private val packaging: String?
) : Processor(delayFactor), IProcessorDelay<T>, Chip {

    @Volatile
    private var rando: Random = Random.Default

    internal val pins: Int = 1

    @Inject
    @Suppress("some message")
    public val material: String = "SomeExpensiveMaterial"

    val temp: Float? = null

    @Override
    override fun startProcessing(category: ProcessorCategory): Int {
        return when (category) {
            Alpha -> {
                when (formFactor) {
                    SimpleForm -> calculateDelay()
                    ComplexForm -> calculateDelay(extraInfo = 5)
                }
            }

            Beta -> {
                delayFactor
            }

            is Gamma -> {
                calculateDelay(extraInfo = category.extraCapacity)
            }
        }
    }

    fun processData(data: T): V? = null
    fun processData(data: T, key: String): V = TODO()

    private fun calculateDelay(extraInfo: Int = 1): Int {
        return extraInfo * delayFactor * rando.nextInt()
    }

    private fun prepare(v: Int?) {

    }
}
        """

    # --- Sample 2: Interface with Generics ---
    print("\n\n--- Sample 2: Interface with Generics and Annotations ---")
    file_path_2 = "src/main/kotlin/org/jay/sample/computing/IProcessorDelay.kt"
    source_code_2 = """
        package org.jay.sample.computing
        
        import kotlin.random.Random
        import org.jay.sample.computing.categories.Processor
        import org.jat.sample.pie.categories.Processor as PiProcessor
        
        @Service
        @Ishqay(modifier = PACKAGE)
        internal interface IProcessorDelay<T : SomeFancyClass> {
            fun startProcessing(category: ProcessorCategory , someThing: SomeThingSomeThing , p: Int) : Boolean
            
            @Nullable
            fun emptyParamFuncName()
            
            @Visibility(private)
            internal fun processData(data: T): Any?
        }
        """

    source_code_3 = """
    package org.jay.sample.computing

sealed class FormFactor

data object ComplexForm : FormFactor()
object SimpleForm : FormFactor()
    """

    source_code_4 = """
    package org.jay.sample.computing

        import kotlin.random.Random
     private data class Input(
    val sourcePath : String,
    val destinationPath : String,
)
    """
    KotlinASTAnalyzer().analyze_kotlin_file(file_path=file_path_1,
                                            source_bytes=source_code_3.encode("utf-8"),
                                            print_debug_info=True)


if __name__ == "__main__":
    run_()
