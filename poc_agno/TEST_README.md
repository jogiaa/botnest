# Unit Tests for tree_hugger2.0.py

This directory contains comprehensive unit tests for the `tree_hugger2.0.py` module, which provides Kotlin AST analysis capabilities.

## Test Coverage

The test suite covers:

### 1. Data Classes
- **FunctionData**: Tests for function metadata extraction
- **VariableData**: Tests for variable/property metadata extraction  
- **KotlinAnalysis**: Tests for the main analysis result container

### 2. Core Analyzer (KotlinASTAnalyzer)
- **Initialization**: Parser and language setup
- **Simple Class Analysis**: Basic class parsing
- **Interface Analysis**: Interface parsing
- **Data Class Analysis**: Data class with constructor parameters
- **Complex Class Analysis**: Classes with annotations, inheritance, generics
- **Edge Cases**: Empty files, invalid code, various Kotlin constructs

### 3. Specific Features
- Package name extraction
- Import statement parsing
- Annotation extraction
- Member/property analysis
- Function/method analysis
- Constructor parameter analysis
- Error handling

## Running the Tests

### Option 1: Using the Test Runner Script
```bash
python run_tests.py
```

### Option 2: Using unittest directly
```bash
python -m unittest test_tree_hugger2_0.py -v
```

### Option 3: Using pytest (if installed)
```bash
pytest test_tree_hugger2_0.py -v
```

## Test Structure

```
test_tree_hugger2_0.py
├── TestFunctionData          # FunctionData dataclass tests
├── TestVariableData          # VariableData dataclass tests  
├── TestKotlinAnalysis        # KotlinAnalysis dataclass tests
├── TestKotlinASTAnalyzer     # Main analyzer functionality tests
└── TestKotlinASTAnalyzerEdgeCases  # Edge case and error handling tests
```

## Sample Test Data

The tests use various Kotlin code samples:

1. **Simple Class**: Basic class with properties and methods
2. **Interface**: Interface with abstract methods
3. **Data Class**: Data class with constructor parameters
4. **Complex Class**: Class with annotations, inheritance, generics
5. **Object Declaration**: Singleton object
6. **Sealed Class**: Sealed class with data classes

## Dependencies

Install test dependencies:
```bash
pip install -r test_requirements.txt
```

Or install core dependencies only:
```bash
pip install tree-sitter tree-sitter-kotlin
```

## Expected Output

When tests pass successfully, you should see:
```
============================================================
Running Unit Tests for tree_hugger2.0.py
============================================================
test_analyzer_initialization (__main__.TestKotlinASTAnalyzer) ... ok
test_analyze_complex_class (__main__.TestKotlinASTAnalyzer) ... ok
test_analyze_data_class (__main__.TestKotlinASTAnalyzer) ... ok
...

============================================================
TEST SUMMARY
============================================================
Tests run: 25
Failures: 0
Errors: 0
Skipped: 0

✅ All tests passed successfully!
```

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure the project root is in your Python path
2. **Missing Dependencies**: Install required packages from `test_requirements.txt`
3. **Tree-sitter Issues**: Make sure `tree-sitter-kotlin` is properly installed

### Debug Mode

Some tests include debug output. To see detailed parsing information:
```python
result = analyzer.analyze_kotlin_file(
    "test.kt", 
    source_code, 
    print_debug_info=True  # Enable debug output
)
```

## Contributing

When adding new features to `tree_hugger2.0.py`:

1. Add corresponding test cases
2. Ensure all existing tests pass
3. Test with various Kotlin code patterns
4. Include edge cases and error conditions

## Coverage

The test suite aims for comprehensive coverage of:
- ✅ Happy path scenarios
- ✅ Edge cases and boundary conditions  
- ✅ Error handling and recovery
- ✅ Different Kotlin language constructs
- ✅ Various annotation and modifier combinations 