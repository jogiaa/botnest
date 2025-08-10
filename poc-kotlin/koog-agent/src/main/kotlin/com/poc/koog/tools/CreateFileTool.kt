package com.poc.koog.tools

import ai.koog.agents.core.tools.Tool
import ai.koog.agents.core.tools.ToolDescriptor
import ai.koog.agents.core.tools.ToolParameterDescriptor
import ai.koog.agents.core.tools.ToolParameterType
import ai.koog.agents.core.tools.ToolResult
import com.poc.koog.utils.FileWriter
import kotlinx.serialization.KSerializer
import kotlinx.serialization.Serializable
import kotlinx.serialization.json.Json
import java.nio.file.Path

class CreateFileTool(rootProjectPath: Path) : Tool<CreateFileTool.Args, CreateFileTool.Result>() {
    private val fileWriter = FileWriter(rootProjectPath)

    @Serializable
    data class Args(val path: String, val content: String) : Tool.Args

    @Serializable
    data class Result(val successful: Boolean, val comment: String? = null) : ToolResult {
        override fun toStringDefault(): String = Json.Default.encodeToString(serializer(), this)
    }

    override val argsSerializer: KSerializer<Args> = Args.serializer()

    override val descriptor: ToolDescriptor = ToolDescriptor(
        name = "create_file",
        description = "Creates a file under the provided relative path, with the specified content",
        requiredParameters = listOf(
            ToolParameterDescriptor(
                name = "path",
                description = "Path to the file",
                type = ToolParameterType.String,
            ),
            ToolParameterDescriptor(
                name = "content",
                description = "Content of the file",
                type = ToolParameterType.String,
            )
        )
    )

    override suspend fun execute(args: Args): Result {
        val writeResult = fileWriter.writeFile(args.path, args.content)
        return Result(
            successful = writeResult.successful,
            comment = writeResult.comment
        )
    }
}