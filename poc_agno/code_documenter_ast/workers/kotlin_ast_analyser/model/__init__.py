"""
Kotlin AST Analysis Data Models

This module provides data classes for representing the structural information
extracted from Kotlin source code by the KotlinASTAnalyzer.

Classes:
    KotlinAnalysisData: Main container for all extracted analysis data
    VariableData: Represents individual variables, properties, or parameters
    FunctionData: Represents individual function or method declarations

Example:
    >>> from poc_agno.code_documenter_ast.workers.kotlin_ast_analyser.model import KotlinAnalysisData
    >>> analysis = KotlinAnalysisData()
    >>> analysis.name = "MyClass"
    >>> analysis.type = "class"
"""

from .function_data import FunctionData
from .kotlin_analysis_data import KotlinAnalysisData
from .variable_data import VariableData

__all__ = [
    'FunctionData',
    'KotlinAnalysisData', 
    'VariableData'
]
