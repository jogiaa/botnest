package com.poc.code.analysis

import com.poc.code.analysis.model.Analysis
import kotlinx.ast.common.AstSource
import kotlinx.ast.common.ast.AstNode
import kotlinx.ast.common.ast.DefaultAstNode
import kotlinx.ast.common.klass.KlassDeclaration
import kotlinx.ast.common.klass.KlassIdentifier
import kotlinx.ast.common.klass.KlassInheritance
import kotlinx.ast.common.klass.identifierNameOrNull
import kotlinx.ast.grammar.kotlin.common.summary
import kotlinx.ast.grammar.kotlin.target.antlr.kotlin.KotlinGrammarAntlrKotlinParser
import java.io.File

class KotlinAstAnalyzer {

    fun analyze(filePath: String, content: String) : List<Analysis> {
        val file = File(filePath)
        val source = AstSource.String(
            description = "Kotlin file: ${file.name}",
            content = content,
        )
        val parseResult = KotlinGrammarAntlrKotlinParser.parseKotlinFile(source)
        val analysisResult: MutableList<Analysis> = mutableListOf()
        parseResult.summary(attachRawAst = true)
            .onSuccess { astList ->
                val analysis = astList.filterIsInstance<KlassDeclaration>()
                    .filter { declaration -> declaration.identifier != null }
                    .map { declaration ->
                        val name = declaration.identifier!!.rawName
                        val inherits = declaration.children.filterIsInstance<KlassInheritance>()
                            .flatMap { it.children.filterIsInstance<KlassIdentifier>() }
                            .map { identifier -> identifier.rawName }
                        val uses = (
                            declaration.children.filterIsInstance<KlassDeclaration>().findComposition() +
                            declaration.children.filterIsInstance<DefaultAstNode>().findComposition()
                        )
                       Analysis(name, inherits.toSet(), uses.toSet())
                    }
                analysisResult.addAll(analysis)
            }
        return analysisResult
    }
    
    fun List<AstNode>.findComposition() =
        flatMap { child -> child.children.filterIsInstance<KlassDeclaration>() }
            .map { child ->
                when (child.keyword) {
                    "val" -> {
                        child.type.identifierNameOrNull() ?: "N/A"
                    }
                    "parameter" -> {
                        child.type.identifierNameOrNull() ?: "N/A"
                    }
                    "fun" -> {
                        child.type.identifierNameOrNull() ?: "N/A"
                    }
                    else -> {
                        "N/A"
                    }
                }
            }
            .filter { type -> type != "N/A" }
}