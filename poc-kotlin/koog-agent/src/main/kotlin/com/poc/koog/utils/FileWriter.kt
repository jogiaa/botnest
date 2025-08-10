package com.poc.koog.utils

import java.nio.file.Files
import java.nio.file.Path

class FileWriter(private val rootProjectPath: Path) {

    fun writeFile(relativePath: String, content: String): FileWriteResult {
        val path = rootProjectPath.resolve(relativePath).normalize()
        return try {
            val filePath = path.toAbsolutePath()
            if (!Files.exists(filePath.parent)) {
                return FileWriteResult(
                    successful = false,
                    comment = "Parent directory does not exist"
                )
            }
            Files.writeString(filePath, content)
            FileWriteResult(successful = true)
        } catch (e: Exception) {
            FileWriteResult(successful = false, comment = e.message)
        }
    }
}