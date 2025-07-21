package org.jay.sample.impl

import org.jay.sample.Input
import org.jay.sample.util.Logger
import java.io.File
import java.io.IOException


open class CapitalizedFileProcessorImpl(private val logger: Logger?) {
    companion object {
        const val TAG = "FileProcessor"
    }

    fun processFile(input: Input): Boolean {
        logger?.i(TAG, "Starting file processing for source: ${input.sourcePath}")
        logger?.i(TAG, "Destination path: ${input.destinationPath}")

        val sourceFile = File(input.sourcePath)
        val destinationFile = File(input.destinationPath)

        val originalContent: String
        try {
            if (!sourceFile.exists()) {
                return false
            }
            if (!sourceFile.isFile) {
                return false
            }
            originalContent = sourceFile.readText(Charsets.UTF_8)
        } catch (e: IOException) {
            return false
        } catch (e: SecurityException) {
            return false
        }
        val capitalizedContent = doAlterations(originalContent)
        try {
            destinationFile.parentFile?.mkdirs()
            destinationFile.writeText(
                capitalizedContent,
                Charsets.UTF_8
            )
            return true
        } catch (e: IOException) {
            logger?.e(
                TAG,
                "Error writing to file ${input.destinationPath}: ${e.message}"
            )
            return false
        } catch (e: SecurityException) {
            logger?.e(
                TAG,
                "Security permission denied for writing to destination file ${input.destinationPath}: ${e.message}"
            )
            return false
        }
    }

    internal open fun doAlterations(originalContent: String): String = originalContent.toUpperCase()
}