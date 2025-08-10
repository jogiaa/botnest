package com.poc.koog.agent.factory

import ai.koog.agents.core.agent.AIAgent
import com.poc.koog.agent.provider.documenterAgent
import com.poc.koog.agent.provider.readerAgent

enum class AgentType {
    Documenter,
    FileReader,
}

fun createAgent(agentType: AgentType): AIAgent {
    return when(agentType) {
        AgentType.Documenter -> documenterAgent()
        AgentType.FileReader -> readerAgent()
    }
}