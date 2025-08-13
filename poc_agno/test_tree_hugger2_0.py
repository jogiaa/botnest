import unittest
from unittest.mock import Mock, patch
import tempfile
import os

from code_documenter.workers.tree_hugger2_0 import (
    KotlinASTAnalyzer,
    KotlinAnalysis,
    FunctionData,
    VariableData
)


class TestFunctionData(unittest.TestCase):
    """Test cases for FunctionData dataclass."""
    
    def test_function_data_default_values(self):
        """Test FunctionData with default values."""
        func_data = FunctionData()
        self.assertEqual(func_data.name, "")
        self.assertEqual(func_data.parameters, "")
        self.assertEqual(func_data.annotations, [])
        self.assertEqual(func_data.visibility, "public")
        self.assertEqual(func_data.return_type, "Unit")
    
    def test_function_data_custom_values(self):
        """Test FunctionData with custom values."""
        func_data = FunctionData(
            name="testFunction",
            parameters="param1: String, param2: Int",
            annotations=["@Test", "@Deprecated"],
            visibility="private",
            return_type="Boolean"
        )
        self.assertEqual(func_data.name, "testFunction")
        self.assertEqual(func_data.parameters, "param1: String, param2: Int")
        self.assertEqual(func_data.annotations, ["@Test", "@Deprecated"])
        self.assertEqual(func_data.visibility, "private")
        self.assertEqual(func_data.return_type, "Boolean")


class TestVariableData(unittest.TestCase):
    """Test cases for VariableData dataclass."""
    
    def test_variable_data_default_values(self):
        """Test VariableData with default values."""
        var_data = VariableData()
        self.assertEqual(var_data.name, "")
        self.assertEqual(var_data.type, "")
        self.assertEqual(var_data.annotations, [])
        self.assertEqual(var_data.visibility, "public")
        self.assertIsNone(var_data.default_value)
    
    def test_variable_data_custom_values(self):
        """Test VariableData with custom values."""
        var_data = VariableData(
            name="testVar",
            type="String",
            annotations=["@NotNull"],
            visibility="internal",
            default_value="default"
        )
        self.assertEqual(var_data.name, "testVar")
        self.assertEqual(var_data.type, "String")
        self.assertEqual(var_data.annotations, ["@NotNull"])
        self.assertEqual(var_data.visibility, "internal")
        self.assertEqual(var_data.default_value, "default")


class TestKotlinAnalysis(unittest.TestCase):
    """Test cases for KotlinAnalysis dataclass."""
    
    def test_kotlin_analysis_default_values(self):
        """Test KotlinAnalysis with default values."""
        analysis = KotlinAnalysis()
        self.assertEqual(analysis.filename, "")
        self.assertEqual(analysis.package_name, "")
        self.assertEqual(analysis.imports, [])
        self.assertEqual(analysis.name, "")
        self.assertEqual(analysis.type, "")
        self.assertEqual(analysis.annotations, [])
        self.assertEqual(analysis.visibility, "public")
        self.assertEqual(analysis.members, [])
        self.assertEqual(analysis.constructor_param_type, [])
        self.assertEqual(analysis.extends, "")
        self.assertEqual(analysis.implements, [])
        self.assertEqual(analysis.functions, [])
        self.assertEqual(analysis.uses, [])
        self.assertEqual(analysis.used_by, [])
    
    def test_kotlin_analysis_custom_values(self):
        """Test KotlinAnalysis with custom values."""
        analysis = KotlinAnalysis(
            filename="test.kt",
            package_name="com.example",
            name="TestClass",
            type="class",
            visibility="private"
        )
        self.assertEqual(analysis.filename, "test.kt")
        self.assertEqual(analysis.package_name, "com.example")
        self.assertEqual(analysis.name, "TestClass")
        self.assertEqual(analysis.type, "class")
        self.assertEqual(analysis.visibility, "private")


class TestKotlinASTAnalyzer(unittest.TestCase):
    """Test cases for KotlinASTAnalyzer class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.analyzer = KotlinASTAnalyzer()
        
        # Sample Kotlin source codes for testing
        self.simple_class_code = """
package com.example

class SimpleClass {
    val property: String = "test"
    
    fun method(): Int = 42
}
""".encode('utf-8')
        
        self.interface_code = """
package com.example

interface TestInterface {
    fun abstractMethod(): String
}
""".encode('utf-8')
        
        self.data_class_code = """
package com.example

data class DataClass(
    val name: String,
    val age: Int
) {
    fun getInfo(): String = "$name is $age years old"
}
""".encode('utf-8')
        
        self.complex_class_code = """
package com.example

import java.util.List
import javax.inject.Inject

@Deprecated("Use new version")
public class ComplexClass<T : Any> : BaseClass<T>(), Interface1, Interface2 {
    
    @Inject
    private val dependency: Dependency = Dependency()
    
    @Volatile
    var mutableProperty: String = "initial"
    
    constructor(param: String) : super(param) {
        // constructor body
    }
    
    override fun process(data: T): Result<T> {
        return Result.success(data)
    }
    
    private fun helper(): Unit {
        // helper method
    }
}
""".encode('utf-8')
    
    def test_analyzer_initialization(self):
        """Test that the analyzer initializes correctly."""
        self.assertIsNotNone(self.analyzer.language)
        self.assertIsNotNone(self.analyzer.parser)
        self.assertEqual(self.analyzer.parser.language, self.analyzer.language)
    
    def test_analyze_simple_class(self):
        """Test analysis of a simple class."""
        result = self.analyzer.analyze_kotlin_file(
            "simple.kt",
            self.simple_class_code,
            print_debug_info=False
        )
        
        self.assertEqual(result.package_name, "com.example")
        self.assertEqual(result.name, "SimpleClass")
        self.assertEqual(result.type, "class")
        self.assertEqual(result.visibility, "public")
        self.assertEqual(len(result.members), 1)
        self.assertEqual(len(result.functions), 1)
        
        # Check member
        member = result.members[0]
        self.assertEqual(member.name, "property")
        self.assertEqual(member.type, "String")
        self.assertEqual(member.default_value, '"test"')
        
        # Check function
        func = result.functions[0]
        self.assertEqual(func.name, "method")
        self.assertEqual(func.return_type, "Int")
    
    def test_analyze_interface(self):
        """Test analysis of an interface."""
        result = self.analyzer.analyze_kotlin_file(
            "interface.kt",
            self.interface_code,
            print_debug_info=False
        )
        
        self.assertEqual(result.package_name, "com.example")
        self.assertEqual(result.name, "TestInterface")
        self.assertEqual(result.type, "interface")
        self.assertEqual(len(result.functions), 1)
        
        func = result.functions[0]
        self.assertEqual(func.name, "abstractMethod")
        self.assertEqual(func.return_type, "String")
    
    def test_analyze_data_class(self):
        """Test analysis of a data class."""
        result = self.analyzer.analyze_kotlin_file(
            "data_class.kt",
            self.data_class_code,
            print_debug_info=False
        )
        
        self.assertEqual(result.package_name, "com.example")
        self.assertEqual(result.name, "DataClass")
        self.assertEqual(result.type, "data class")
        self.assertEqual(len(result.constructor_param_type), 2)
        self.assertEqual(len(result.functions), 1)
        
        # Check constructor parameters
        param1 = result.constructor_param_type[0]
        self.assertEqual(param1.name, "name")
        self.assertEqual(param1.type, "String")
        
        param2 = result.constructor_param_type[1]
        self.assertEqual(param2.name, "age")
        self.assertEqual(param2.type, "Int")
    
    def test_analyze_complex_class(self):
        """Test analysis of a complex class with annotations and inheritance."""
        result = self.analyzer.analyze_kotlin_file(
            "complex.kt",
            self.complex_class_code,
            print_debug_info=False
        )
        
        self.assertEqual(result.package_name, "com.example")
        self.assertEqual(result.name, "ComplexClass")
        self.assertEqual(result.type, "class")
        self.assertEqual(result.visibility, "public")
        self.assertEqual(len(result.annotations), 1)
        self.assertEqual(result.annotations[0], "@Deprecated")
        self.assertEqual(len(result.imports), 2)
        self.assertEqual(len(result.members), 2)
        self.assertEqual(len(result.functions), 2)
        
        # Check imports
        self.assertIn("java.util.List", result.imports)
        self.assertIn("javax.inject.Inject", result.imports)
        
        # Check members
        member1 = result.members[0]
        self.assertEqual(member1.name, "dependency")
        self.assertEqual(member1.type, "Dependency")
        self.assertIn("@Inject", member1.annotations)
        
        member2 = result.members[1]
        self.assertEqual(member2.name, "mutableProperty")
        self.assertEqual(member2.type, "String")
        self.assertEqual(member2.default_value, '"initial"')
        self.assertIn("@Volatile", member2.annotations)
    
    def test_extract_package_name(self):
        """Test package name extraction."""
        result = self.analyzer.analyze_kotlin_file(
            "test.kt",
            self.simple_class_code,
            print_debug_info=False
        )
        self.assertEqual(result.package_name, "com.example")
    
    def test_extract_imports(self):
        """Test import extraction."""
        result = self.analyzer.analyze_kotlin_file(
            "test.kt",
            self.complex_class_code,
            print_debug_info=False
        )
        self.assertEqual(len(result.imports), 2)
        self.assertIn("java.util.List", result.imports)
        self.assertIn("javax.inject.Inject", result.imports)
    
    def test_extract_annotations(self):
        """Test annotation extraction."""
        result = self.analyzer.analyze_kotlin_file(
            "test.kt",
            self.complex_class_code,
            print_debug_info=False
        )
        self.assertEqual(len(result.annotations), 1)
        self.assertEqual(result.annotations[0], "@Deprecated")
    
    def test_extract_members(self):
        """Test member extraction."""
        result = self.analyzer.analyze_kotlin_file(
            "test.kt",
            self.complex_class_code,
            print_debug_info=False
        )
        self.assertEqual(len(result.members), 2)
        
        # Check first member
        member = result.members[0]
        self.assertEqual(member.name, "dependency")
        self.assertEqual(member.type, "Dependency")
        self.assertIn("@Inject", member.annotations)
    
    def test_extract_functions(self):
        """Test function extraction."""
        result = self.analyzer.analyze_kotlin_file(
            "test.kt",
            self.complex_class_code,
            print_debug_info=False
        )
        self.assertEqual(len(result.functions), 2)
        
        # Check first function
        func = result.functions[0]
        self.assertEqual(func.name, "process")
        self.assertEqual(func.return_type, "Result<T>")
    
    def test_extract_constructor_params(self):
        """Test constructor parameter extraction."""
        result = self.analyzer.analyze_kotlin_file(
            "test.kt",
            self.data_class_code,
            print_debug_info=False
        )
        self.assertEqual(len(result.constructor_param_type), 2)
        
        param1 = result.constructor_param_type[0]
        self.assertEqual(param1.name, "name")
        self.assertEqual(param1.type, "String")
    
    def test_error_handling(self):
        """Test error handling with invalid input."""
        # Test with empty source
        result = self.analyzer.analyze_kotlin_file(
            "empty.kt",
            b"",
            print_debug_info=False
        )
        self.assertIsInstance(result, KotlinAnalysis)
        
        # Test with invalid Kotlin code
        invalid_code = "this is not valid kotlin code".encode('utf-8')
        result = self.analyzer.analyze_kotlin_file(
            "invalid.kt",
            invalid_code,
            print_debug_info=False
        )
        self.assertIsInstance(result, KotlinAnalysis)
    
    def test_get_node_text(self):
        """Test _get_node_text method."""
        # Create a mock node
        mock_node = Mock()
        mock_node.text = b"test text"
        
        result = self.analyzer._get_node_text(mock_node)
        self.assertEqual(result, "test text")
        
        # Test with None node
        result = self.analyzer._get_node_text(None)
        self.assertEqual(result, "")
    
    def test_create_query_cursor(self):
        """Test _create_query_cursor method."""
        cursor = self.analyzer._create_query_cursor("(identifier) @name")
        self.assertIsNotNone(cursor)
        
        # Test with invalid query
        cursor = self.analyzer._create_query_cursor("invalid query syntax")
        self.assertIsNone(cursor)


class TestKotlinASTAnalyzerEdgeCases(unittest.TestCase):
    """Test edge cases and error conditions."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.analyzer = KotlinASTAnalyzer()
    
    def test_empty_file(self):
        """Test analysis of an empty file."""
        result = self.analyzer.analyze_kotlin_file(
            "empty.kt",
            b"",
            print_debug_info=False
        )
        self.assertIsInstance(result, KotlinAnalysis)
        self.assertEqual(result.package_name, "")
        self.assertEqual(result.name, "")
    
    def test_file_with_only_package(self):
        """Test analysis of a file with only package declaration."""
        code = """
package com.example
""".encode('utf-8')
        
        result = self.analyzer.analyze_kotlin_file(
            "package_only.kt",
            code,
            print_debug_info=False
        )
        self.assertEqual(result.package_name, "com.example")
        self.assertEqual(result.name, "")
    
    def test_file_with_only_imports(self):
        """Test analysis of a file with only imports."""
        code = """
package com.example

import java.util.List
import java.util.Map
""".encode('utf-8')
        
        result = self.analyzer.analyze_kotlin_file(
            "imports_only.kt",
            code,
            print_debug_info=False
        )
        self.assertEqual(result.package_name, "com.example")
        self.assertEqual(len(result.imports), 2)
        self.assertEqual(result.name, "")
    
    def test_object_declaration(self):
        """Test analysis of an object declaration."""
        code = """
package com.example

object Singleton {
    val value: String = "singleton"
    
    fun getValue(): String = value
}
""".encode('utf-8')
        
        result = self.analyzer.analyze_kotlin_file(
            "object.kt",
            code,
            print_debug_info=False
        )
        self.assertEqual(result.package_name, "com.example")
        self.assertEqual(result.name, "Singleton")
        self.assertEqual(len(result.members), 1)
        self.assertEqual(len(result.functions), 1)
    
    def test_sealed_class(self):
        """Test analysis of a sealed class."""
        code = """
package com.example

sealed class Result<out T> {
    data class Success<T>(val data: T) : Result<T>()
    data class Error(val message: String) : Result<Nothing>()
}
""".encode('utf-8')
        
        result = self.analyzer.analyze_kotlin_file(
            "sealed.kt",
            code,
            print_debug_info=False
        )
        self.assertEqual(result.package_name, "com.example")
        self.assertEqual(result.name, "Result")
        self.assertEqual(result.type, "sealed class")


if __name__ == '__main__':
    unittest.main() 