package com.poc.koog.agent.provider

import ai.koog.agents.core.agent.AIAgent
import ai.koog.agents.core.agent.config.AIAgentConfig
import ai.koog.agents.core.agent.singleRunStrategy
import ai.koog.agents.core.tools.ToolRegistry
import ai.koog.agents.ext.tool.SayToUser
import ai.koog.prompt.dsl.prompt
import ai.koog.prompt.executor.llms.all.simpleOllamaAIExecutor
import ai.koog.prompt.llm.OllamaModels
import ai.koog.prompt.params.LLMParams
import com.poc.koog.DOCUMENTATION_AGENT_SYSTEM_PROMPT
import com.poc.koog.agent.enableDebugging
import com.poc.koog.tools.CreateFileTool
import com.poc.koog.tools.ReadFileTool
import poc_kotlin.koog_agent.BuildConfig
import kotlin.uuid.ExperimentalUuidApi

private val projectFile = BuildConfig.FILE_TOOL_BASE_PATH
private val projectPath = projectFile.toPath()

private val readFileTool = ReadFileTool(projectPath)
private val createFileTool = CreateFileTool(projectPath)

private val toolRegistry = ToolRegistry {
    tool(readFileTool)
    tool(createFileTool)
    tool(SayToUser) // prints out progress to user
}

private val agentConfig = AIAgentConfig(
    prompt = prompt(id = "setup-prompt", params = LLMParams(temperature = 0.0)) {
        system(DOCUMENTATION_AGENT_SYSTEM_PROMPT)
    },
    model = OllamaModels.Meta.LLAMA_3_2,
    maxAgentIterations = 200,
)

@OptIn(ExperimentalUuidApi::class)
val documenterAgent = AgentProvider {
    AIAgent(
        promptExecutor = simpleOllamaAIExecutor(), // defaults to port 11434
        agentConfig = agentConfig,
        strategy = singleRunStrategy(),
        toolRegistry = toolRegistry,
        installFeatures = { enableDebugging() }
    )
}