package com.poc.koog.tools

import ai.koog.agents.core.tools.Tool
import ai.koog.agents.core.tools.ToolDescriptor
import ai.koog.agents.core.tools.ToolParameterDescriptor
import ai.koog.agents.core.tools.ToolParameterType
import ai.koog.agents.core.tools.ToolResult
import kotlinx.serialization.KSerializer
import kotlinx.serialization.Serializable
import kotlinx.serialization.json.Json
import java.nio.file.Path
import java.util.concurrent.TimeUnit

class RunCommand(val rootProjectPath: Path) : Tool<RunCommand.Args, RunCommand.Result>() {
    @Serializable
    data class Args(val bashCommand: String) : Tool.Args

    @Serializable
    data class Result(val successful: Boolean, val comment: String? = null) : ToolResult {
        override fun toStringDefault(): String = Json.Default.encodeToString(serializer(), this)
    }

    override val argsSerializer: KSerializer<Args> = Args.serializer()

    override val descriptor: ToolDescriptor = ToolDescriptor(
        name = "run_bash_command",
        description = "Runs the provided bash command in the project root directory",
        requiredParameters = listOf(
            ToolParameterDescriptor(
                name = "bashCommand",
                description = "Command to run",
                type = ToolParameterType.String,
            )
        )
    )

    override suspend fun execute(args: Args): Result {
        if (args.bashCommand.isBlank()) {
            return Result(successful = false, comment = "Bash command is blank")
        }
        if (args.bashCommand.startsWith("ls")) {
            return Result(
                successful = false,
                comment = "Please, use `${LSDirectoriesTool::class.java.simpleName}` tool for listing files and directories"
            )
        }
        if (args.bashCommand.startsWith("cat")) {
            return Result(
                successful = false,
                comment = "Please, use `${ReadFileTool::class.java.simpleName}` tool for reading files"
            )
        }
        if (args.bashCommand.startsWith("rm")) {
            return Result(
                successful = false,
                comment = "Removing files or directories is not allowed! Please, only observe and run builds/tests/etc."
            )
        }

        return try {
            val processBuilder = ProcessBuilder()
                .command("bash", "-c", args.bashCommand)
                .directory(rootProjectPath.toFile())
                .redirectErrorStream(true)

            val process = processBuilder.start()
            val output = process.inputStream.bufferedReader().readText()
            val successful = process.waitFor(50, TimeUnit.SECONDS)

            if (successful) {
                Result(successful = true, comment = output)
            } else {
                Result(
                    successful = false,
                    comment = "Command failed. Output: ${process.errorStream.bufferedReader().readText()}"
                )
            }
        } catch (e: Exception) {
            Result(
                successful = false,
                comment = "Exception occurred: ${e::class.qualifiedName} ${e.message}\nStacktrace: ${
                    e.stackTraceToString().take(300)
                }"
            )
        }
    }
}