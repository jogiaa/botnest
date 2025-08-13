import logging
from dataclasses import dataclass, field
from typing import List, Dict, Optional

import tree_sitter_kotlin
from tree_sitter import Language, Parser, Query, QueryCursor
import os

@dataclass
class KotlinAnalysis:
    """Data class to hold all extracted information."""
    filename: str = ""
    package_name: str = ""
    imports: List[str] = field(default_factory=list)
    name: str = ""
    type: str = ""  # class|interface|data class|enum|object|sealed class etc.
    visibility: str = "public"  # private | internal | public
    members: List[Dict] = field(default_factory=list)  # [{'name':..., 'type':...}, ...]
    constructor_param_type: List[str] = field(default_factory=list)
    extends: str = ""
    implements: List[str] = field(default_factory=list)
    functions: List[Dict] = field(default_factory=list)  # [{'name','visibility','return_type','param_types'}, ...]
    uses: List[str] = field(default_factory=list)
    used_by: List[str] = field(default_factory=list)


class KotlinASTAnalyzer:
    """
    Query-driven Kotlin AST analyzer using tree-sitter and tree-sitter-kotlin.

    Usage:
      from tree_sitter_kotlin import language as kotlin_lang_module
      KOTLIN_LANGUAGE = Language(kotlin_lang_module.language())   # or however you obtain the Language
      analyzer = KotlinASTAnalyzer(KOTLIN_LANGUAGE)
      results = analyzer.analyze_file('/path/to/File.kt', source_bytes=None)
    """

    # A default "comprehensive" query string. You may need to tweak capture names/node types depending on
    # which version of the kotlin grammar you have installed.
    # - Each capture has a name like @package.name, @import.path, @class.decl, etc.
    default_query = r"""
    ;; package header
    (package_header (qualified_identifier) @package.name)

    ;; imports
    (import (qualified_identifier) @import.path)
    ;;(import_directive (identifier (simple_identifier) @import.path))

    ;; class / interface / object / enum / sealed / data class declarations
    ;; these captures match the top-level declarations; grammar names may vary
    (class_declaration
        name: (identifier) @type.name
        (#match? @type.name ".*")
        (modifiers)? @type.modifiers
    ) @class.decl

    (interface
        name: (identifier) @type.name
        (modifiers)? @type.modifiers
    ) @interface.decl

    (object_declaration
        name: (identifier) @type.name
        (modifiers)? @type.modifiers
    ) @object.decl

    (enum_class
        name: (identifier) @type.name
        (modifiers)? @type.modifiers
    ) @enum.decl

    (sealed_class
        name: (identifier) @type.name
        (modifiers)? @type.modifiers
    ) @sealed.decl

    (data_class
        name: (identifier) @type.name
        (modifiers)? @type.modifiers
    ) @data.decl

    ;; constructors (primary constructor with parameter list)
    (primary_constructor
        (function_value_parameters (parameter) @ctor.param)
    ) @ctor.decl

    ;; properties (members)
    (property_declaration (variable_declaration (identifier) @member.name) type: (type) @member.type) @member.decl
    (property_declaration (identifier) @member.name) @member.decl

    ;; functions
    (function_declaration
        name: (identifier) @fun.name
        (value_parameters (parameter) @fun.param)
        (type? (type) @fun.return_type)
        (modifiers)? @fun.modifiers
    ) @fun.decl

    ;; super types (extends/implements)
    ;; look for super_type_list or delegation_specifier
    (delegation_specifier (user_type (identifier) @super.name)) @super.decl
    (super_types (user_type (identifier) @super.name)) @super.decl
    """

    def __init__(self,  comprehensive_query: Optional[str] = None):
        self.language = Language(tree_sitter_kotlin.language())
        query_text = comprehensive_query if comprehensive_query is not None else self.default_query
        self.query_text = query_text
        self.parser = Parser()
        self.parser.language = self.language
        # self.parser.logger = logging.getLogger(__name__)

    # utility: decode node text
    def node_text(self, source_bytes: bytes, node) -> str:
        return source_bytes[node.start_byte:node.end_byte].decode("utf-8")

    def analyze_file(self, file_path: str, source_bytes: Optional[bytes] = None) -> List[KotlinAnalysis]:
        """
        Analyze a single Kotlin file and return a list of KotlinAnalysis items.
        (One file can produce multiple analyses -- e.g., a sealed class + nested objects)
        """
        if source_bytes is None:
            with open(file_path, "rb") as f:
                source_bytes = f.read()

        tree = self.parser.parse(source_bytes)
        root_node = tree.root_node
        query = Query(self.language, self.query_text)
        cursor = QueryCursor(query)

        # Collect captured nodes by capture name for convenience
        captures_by_name = {}  # capture_name -> list of nodes
        matches = list(cursor.matches(root_node))
        for match in matches:
            for capture in match.captures:
                node, capture_name = capture
                captures_by_name.setdefault(capture_name, []).append(node)

        # helper to get first capture text for a capture_name
        def first_text(name):
            nodes = captures_by_name.get(name, [])
            return self.node_text(source_bytes, nodes[0]) if nodes else ""

        # package name (try a couple capture names)
        package_name = first_text("package.name")
        # gather imports (dedupe)
        imports = []
        for node in captures_by_name.get("import.path", []):
            txt = self.node_text(source_bytes, node).strip()
            if txt and txt not in imports:
                imports.append(txt)

        results: List[KotlinAnalysis] = []

        # We will find high-level declarations by looking for @class.decl, @interface.decl, @object.decl etc.
        decl_capture_keys = [
            ("class.decl", "class"),
            ("interface.decl", "interface"),
            ("object.decl", "object"),
            ("enum.decl", "enum"),
            ("sealed.decl", "sealed class"),
            ("data.decl", "data class"),
        ]

        # helper to find captures that belong inside a declaration node
        def find_within(node, capture_key):
            nodes = captures_by_name.get(capture_key, [])
            return [n for n in nodes if self._node_contains(node, n)]

        # iterate declarations
        for cap_key, kind_name in decl_capture_keys:
            for decl_node in captures_by_name.get(cap_key, []):
                # capture name node inside declaration (captured as @type.name)
                name_nodes = captures_by_name.get("type.name", [])
                name = ""
                # find corresponding name node under this decl_node
                for n in name_nodes:
                    if self._node_contains(decl_node, n):
                        name = self.node_text(source_bytes, n)
                        break
                if not name:
                    # fallback to whole-decl text first token
                    name = self.node_text(source_bytes, decl_node).split()[0]

                analysis = KotlinAnalysis()
                analysis.filename = os.path.relpath(file_path)
                analysis.package_name = package_name
                analysis.imports = imports.copy()
                analysis.name = name
                analysis.type = kind_name

                # modifiers -> visibility (look for 'private', 'internal', 'public')
                visibility = "public"
                mod_nodes = captures_by_name.get("type.modifiers", []) + captures_by_name.get("fun.modifiers", [])
                for mn in mod_nodes:
                    if self._node_contains(decl_node, mn):
                        maybe = self.node_text(source_bytes, mn)
                        if "private" in maybe:
                            visibility = "private"
                        elif "internal" in maybe:
                            visibility = "internal"
                        elif "public" in maybe:
                            visibility = "public"
                analysis.visibility = visibility

                # members: properties captured as @member.decl with @member.name and @member.type
                members = []
                for mem_node in captures_by_name.get("member.decl", []):
                    if self._node_contains(decl_node, mem_node):
                        # look up the member.name and member.type under this mem_node
                        member_name = ""
                        member_type = ""
                        for mn in captures_by_name.get("member.name", []):
                            if self._node_contains(mem_node, mn):
                                member_name = self.node_text(source_bytes, mn)
                                break
                        for mt in captures_by_name.get("member.type", []):
                            if self._node_contains(mem_node, mt):
                                member_type = self.node_text(source_bytes, mt)
                                break
                        members.append({"name": member_name, "type": member_type})
                analysis.members = members

                # constructor parameters (look for ctor.param that lie inside this decl)
                ctor_types = []
                for p in captures_by_name.get("ctor.param", []):
                    if self._node_contains(decl_node, p):
                        # parameter node text: attempt to find its type by walking siblings or children
                        full = self.node_text(source_bytes, p)
                        # crude split: split on ':' and take right side as type if present
                        if ":" in full:
                            typ = full.split(":", 1)[1].strip()
                            # remove possible default or commas
                            typ = typ.split("=")[0].strip().rstrip(",")
                            ctor_types.append(typ)
                        else:
                            # fallback: entire param text
                            ctor_types.append(full.strip())
                analysis.constructor_param_type = ctor_types

                # super types (extends/implements) - find super.name captures inside this declaration
                sup = []
                for s in captures_by_name.get("super.name", []):
                    if self._node_contains(decl_node, s):
                        sup.append(self.node_text(source_bytes, s))
                if sup:
                    # heuristics: if there's one, it's extends; if multiple, first is extends others are implements
                    analysis.extends = sup[0]
                    if len(sup) > 1:
                        analysis.implements = sup[1:]

                # functions inside this declaration
                functions = []
                for fnode in captures_by_name.get("fun.decl", []):
                    if self._node_contains(decl_node, fnode):
                        # find name, params, return_type, modifiers for this function
                        fname = ""
                        for fn in captures_by_name.get("fun.name", []):
                            if self._node_contains(fnode, fn):
                                fname = self.node_text(source_bytes, fn)
                                break
                        # parameters: collect any @fun.param nodes within this fun.decl
                        param_types = []
                        for p in captures_by_name.get("fun.param", []):
                            if self._node_contains(fnode, p):
                                txt = self.node_text(source_bytes, p)
                                if ":" in txt:
                                    typ = txt.split(":", 1)[1].strip().split("=")[0].strip().rstrip(",")
                                    param_types.append(typ)
                                else:
                                    param_types.append(txt.strip())
                        # return type
                        ret = ""
                        for rt in captures_by_name.get("fun.return_type", []):
                            if self._node_contains(fnode, rt):
                                ret = self.node_text(source_bytes, rt)
                                break
                        # visibility from fun.modifiers (private/internal/public)
                        fvis = "public"
                        for fm in captures_by_name.get("fun.modifiers", []):
                            if self._node_contains(fnode, fm):
                                mt = self.node_text(source_bytes, fm)
                                if "private" in mt:
                                    fvis = "private"
                                elif "internal" in mt:
                                    fvis = "internal"
                                elif "public" in mt:
                                    fvis = "public"
                                break
                        functions.append({"name": fname, "visibility": fvis, "return_type": ret or "Unit", "param_types": param_types})
                analysis.functions = functions

                # uses: accumulate referenced types inside this declaration by scanning tokens for capitalized identifiers or user_type captures
                uses = set()
                # check captured super types
                for s in sup:
                    uses.add(s)
                # add constructor param types
                for t in ctor_types:
                    if t:
                        uses.add(t)
                # add member types
                for m in members:
                    if m.get("type"):
                        uses.add(m["type"])
                # add function parameter types and return types
                for f in functions:
                    for p in f["param_types"]:
                        if p:
                            uses.add(p)
                    if f["return_type"] and f["return_type"] != "Unit":
                        uses.add(f["return_type"])
                analysis.uses = sorted([u for u in uses if u])

                results.append(analysis)

        # If no top-level declarations matched (e.g., file contains only interface or sealed children),
        # we also try to detect top-level function or interface decls that might not be covered above.
        # (You can extend this section as needed.)
        # For example handle top-level interface if the above didn't catch any
        if not results:
            # attempt to find any interface.decl captured nodes (a second pass)
            for n in captures_by_name.get("interface.decl", []):
                name = ""
                for nm in captures_by_name.get("type.name", []):
                    if self._node_contains(n, nm):
                        name = self.node_text(source_bytes, nm)
                        break
                analysis = KotlinAnalysis(
                    filename=os.path.relpath(file_path),
                    package_name=package_name,
                    imports=imports.copy(),
                    name=name or self.node_text(source_bytes, n).split()[0],
                    type="interface",
                    visibility="public",
                    members=[],
                    constructor_param_type=[],
                    extends="",
                    implements=[],
                    functions=[], uses=[]
                )
                # capture its functions
                functions = []
                for fnode in captures_by_name.get("fun.decl", []):
                    if self._node_contains(n, fnode):
                        fname = ""
                        for fn in captures_by_name.get("fun.name", []):
                            if self._node_contains(fnode, fn):
                                fname = self.node_text(source_bytes, fn)
                        param_types = []
                        for p in captures_by_name.get("fun.param", []):
                            if self._node_contains(fnode, p):
                                txt = self.node_text(source_bytes, p)
                                if ":" in txt:
                                    typ = txt.split(":", 1)[1].strip().split("=")[0].strip().rstrip(",")
                                    param_types.append(typ)
                                else:
                                    param_types.append(txt.strip())
                        ret = ""
                        for rt in captures_by_name.get("fun.return_type", []):
                            if self._node_contains(fnode, rt):
                                ret = self.node_text(source_bytes, rt)
                                break
                        functions.append({"name": fname, "visibility": "public", "return_type": ret or "Unit", "param_types": param_types})
                analysis.functions = functions
                # find uses from param types
                uses = set()
                for f in functions:
                    for p in f["param_types"]:
                        if p:
                            uses.add(p)
                    if f["return_type"] and f["return_type"] != "Unit":
                        uses.add(f["return_type"])
                analysis.uses = sorted(list(uses))
                results.append(analysis)

        return results

    # small helper: returns True if 'inner' is inside 'outer' in source tree
    def _node_contains(self, outer, inner) -> bool:
        return (outer.start_byte <= inner.start_byte) and (outer.end_byte >= inner.end_byte)

    # Debug helpers
    def print_tree(self, source_bytes: bytes, node=None, indent=0, max_lines=2000):
        """Recursively print node types and text (useful to find exact node names in your grammar)."""
        if node is None:
            tree = self.parser.parse(source_bytes)
            node = tree.root_node

        prefix = "  " * indent
        text = self.node_text(source_bytes, node).strip().splitlines()
        sample = text[0][:80] + ("..." if len(text[0]) > 80 else "") if text else ""
        print(f"{prefix}{node.type} [{node.start_point}..{node.end_point}] -- {sample}")
        for child in node.children:
            self.print_tree(source_bytes, child, indent + 1)

    def debug_query_matches(self, source_bytes: bytes, root_node=None):
        """Run the current compiled query and print matches/captures for debugging."""
        if root_node is None:
            tree = self.parser.parse(source_bytes)
            root_node = tree.root_node
        cursor = QueryCursor()
        cursor.exec(self.query, root_node)
        matches = list(cursor.matches(root_node))
        for mi, m in enumerate(matches):
            print(f"Match {mi}: pattern_index={m.pattern_index}")
            for capture_node, capture_name in m.captures:
                txt = self.node_text(source_bytes, capture_node).replace("\n", "\\n")
                print(f"  Capture: {capture_name} -> '{txt[:120]}' (node.type={capture_node.type})")



if __name__ == "__main__":
    # --- Sample 1: Class with Inheritance and Implementation, Generics, and Annotations ---
    print("--- Sample 1: Advanced Class Example with Generics & Annotations ---")
    file_path_1 = "src/main/kotlin/org/jay/sample/computing/ProcessorDelay.kt"
    source_code_1 = """
    @file:JvmName("ProcessingUtils")
    package org.jay.sample.computing

    import kotlin.random.Random
    import org.jay.sample.computing.categories.Processor

    @Deprecated("This class is deprecated")
    class ProcessorDelay<T : Any, V>(private val delayFactor: Int, @Inject private val formFactor : FormFactor) : Processor(delayFactor), IProcessorDelay<T> {

        @Volatile
        private var actuater : Random.Default

        @Override
        override fun startProcessing(category: ProcessorCategory): Int {
            return when (category) {
                Alpha -> {
                    when(formFactor){
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
            return extraInfo * delayFactor * actuater.nextInt()
        }

        private fun prepare(){

        }
    }
    """

    # --- Sample 2: Interface with Generics ---
    print("\n\n--- Sample 2: Interface with Generics and Annotations ---")
    file_path_2 = "src/main/kotlin/org/jay/sample/computing/IProcessorDelay.kt"
    source_code_2 = """
    package org.jay.sample.computing

    @Service
    interface IProcessorDelay<T> {
        fun startProcessing(category: ProcessorCategory) : Int
        fun processData(data: T): Any?
    }
    """

    KotlinASTAnalyzer().print_tree(
        source_bytes=source_code_2.encode("utf-8"),
    )
    KotlinASTAnalyzer().analyze_file(
        file_path=file_path_1,
        source_bytes=source_code_2.encode("utf-8"),
    )
