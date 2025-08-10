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
import kotlin.io.path.pathString

class LSDirectoriesTool(val rootProjectPath: Path) : Tool<LSDirectoriesTool.Args, LSDirectoriesTool.Result>() {
    @Serializable
    data class Args(val path: String) : Tool.Args

    @Serializable
    data class Result(
        val successful: Boolean,
        val comment: String? = null,
        val content: List<String>? = null,
    ) : ToolResult {
        override fun toStringDefault(): String = Json.Default.encodeToString(serializer(), this)
    }

    override val argsSerializer: KSerializer<Args> = Args.serializer()

    override val descriptor: ToolDescriptor = ToolDescriptor(
        name = "ls_directory",
        description = "Lists all the files and directories under the provided RELATIVE path",
        requiredParameters = listOf(
            ToolParameterDescriptor(
                name = "path",
                description = "Path to the directory",
                type = ToolParameterType.String,
            )
        )
    )

    override suspend fun execute(args: Args): Result {
        val path = rootProjectPath.resolve(args.path).normalize()
        return try {
            if (!Files.exists(path)) {
                return Result(
                    successful = false,
                    comment = "Directory does not exist at the provided path: $path"
                )
            }
            if (!Files.isDirectory(path)) {
                return Result(
                    successful = false,
                    comment = "$path is NOT a directory"
                )
            }

            val content = Files.list(path).map { rootProjectPath.relativize(it).pathString }.toList()
            Result(successful = true, content = content)
        } catch (e: Exception) {
            Result(
                successful = false,
                comment = "Failed to read file: ${e::class.qualifiedName} ${e.message}\nStacktrace: ${
                    e.stackTraceToString().take(300)
                }"
            )
        }
    }
}