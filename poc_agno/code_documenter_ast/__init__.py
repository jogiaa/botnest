"""
Code Documenter AST - A package for analyzing and documenting code using Abstract Syntax Trees.
"""

from .workers.kotlin_ast_analyser import KotlinASTAnalyzer

__version__ = "0.1.0"
__all__ = [
    "KotlinASTAnalyzer",
]
