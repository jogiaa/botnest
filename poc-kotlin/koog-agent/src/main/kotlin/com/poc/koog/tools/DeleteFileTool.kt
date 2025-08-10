package com.poc.koog.tools

import ai.koog.agents.core.tools.Tool
import ai.koog.agents.core.tools.ToolDescriptor
import ai.koog.agents.core.tools.ToolParameterDescriptor
import ai.koog.agents.core.tools.ToolParameterType
import ai.koog.agents.core.tools.ToolResult
import kotlinx.serialization.KSerializer
import kotlinx.serialization.Serializable
import kotlinx.serialization.json.Json
import java.nio.file.Files
import java.nio.file.Path

class DeleteFileTool(val rootProjectPath: Path) : Tool<DeleteFileTool.Args, DeleteFileTool.Result>() {
    @Serializable
    data class Args(val path: String) : Tool.Args

    @Serializable
    data class Result(val successful: Boolean, val comment: String? = null) : ToolResult {
        override fun toStringDefault(): String = Json.Default.encodeToString(serializer(), this)
    }

    override val argsSerializer: KSerializer<Args> = Args.serializer()

    override val descriptor: ToolDescriptor = ToolDescriptor(
        name = "delete_file",
        description = "Deletes a file under the provided relative path",
        requiredParameters = listOf(
            ToolParameterDescriptor(
                name = "path",
                description = "Path to the file to delete",
                type = ToolParameterType.String,
            )
        )
    )

    override suspend fun execute(args: Args): Result {
        val path = rootProjectPath.resolve(args.path).normalize()
        return try {
            val filePath = path
            if (!Files.exists(filePath)) {
                return Result(successful = false, comment = "File does not exist")
            }
            if (!Files.isRegularFile(filePath)) {
                return Result(successful = false, comment = "The provided path is not a file")
            }
            Files.delete(filePath)
            Result(successful = true)
        } catch (e: Exception) {
            Result(successful = false, comment = e.message)
        }
    }
}