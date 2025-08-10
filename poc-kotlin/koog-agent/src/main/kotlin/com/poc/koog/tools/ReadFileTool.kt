package com.poc.koog.tools

import ai.koog.agents.core.tools.*
import com.poc.koog.utils.FileReader
import kotlinx.serialization.KSerializer
import kotlinx.serialization.Serializable
import kotlinx.serialization.json.Json
import java.nio.file.Path

class ReadFileTool(rootProjectPath: Path) : Tool<ReadFileTool.Args, ReadFileTool.Result>() {
    private val fileReader = FileReader(rootProjectPath)

    @Serializable
    data class Args(val path: String) : Tool.Args

    @Serializable
    data class Result(
        val successful: Boolean,
        val fileContent: String? = null,
        val comment: String? = null
    ) : ToolResult {
        override fun toStringDefault(): String = Json.encodeToString(serializer(), this)
    }

    override val argsSerializer: KSerializer<Args> = Args.serializer()

    override val descriptor: ToolDescriptor = ToolDescriptor(
        name = "read_file",
        description = "Reads a file under the provided RELATIVE path, with the specified content",
        requiredParameters = listOf(
            ToolParameterDescriptor(
                name = "path",
                description = "Path to the file",
                type = ToolParameterType.String,
            )
        )
    )

    override suspend fun execute(args: Args): Result {
        val readResult = fileReader.readFile(args.path)
        return Result(
            successful = readResult.successful,
            fileContent = readResult.fileContent,
            comment = readResult.comment
        )
    }
}

