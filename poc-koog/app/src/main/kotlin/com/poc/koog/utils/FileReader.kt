package com.poc.koog.utils

import java.nio.file.Files
import java.nio.file.Path

class FileReader(private val rootProjectPath: Path) {

    fun readFile(relativePath: String): FileReadResult {
        val path = rootProjectPath.resolve(relativePath).normalize()
        return try {
            if (!Files.exists(path)) {
                return FileReadResult(
                    successful = false,
                    comment = "File does not exist at the provided path: $path"
                )
            }
            if (!Files.isRegularFile(path)) {
                return FileReadResult(
                    successful = false,
                    comment = "$path is NOT a file"
                )
            }

            val content = Files.readString(path)
            FileReadResult(successful = true, fileContent = content)
        } catch (e: Exception) {
            FileReadResult(
                successful = false,
                comment = "Failed to read file: ${e::class.qualifiedName} ${e.message}\nStacktrace: ${
                    e.stackTraceToString().take(300)
                }"
            )
        }
    }
}

