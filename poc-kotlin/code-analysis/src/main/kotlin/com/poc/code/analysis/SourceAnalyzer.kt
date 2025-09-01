package com.poc.code.analysis

import com.poc.code.analysis.model.Analysis
import java.nio.file.Files
import java.nio.file.Path
import java.util.stream.Stream
import kotlin.io.path.isRegularFile

class SourceAnalyzer(
    private val kotlinAnalyzer: KotlinAstAnalyzer = KotlinAstAnalyzer(),
) {
    fun analyzeSourceRoot(sourceRoot: Path): List<Analysis> {
        // Ensure the path exists before walking
        println("Input directory: $sourceRoot")

        // Walk directories or handle a single file
        val stream: Stream<Path> =
            if (Files.isDirectory(sourceRoot)) Files.walk(sourceRoot)
            else Stream.of(sourceRoot)

        return stream.use { stream ->
            stream.filter { it.isRegularFile() }.map { path ->
                val content = Files.readString(path)
                when (path.fileName.toString().substringAfterLast('.', "")) {
                    "kt" -> kotlinAnalyzer.analyze(path.toString(), content)
                    else -> emptyList()
                }
            }.toList().flatten()
        }
    }
}