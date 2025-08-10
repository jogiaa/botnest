package com.poc.koog.agent.provider

import ai.koog.agents.core.agent.AIAgent

fun interface AgentProvider {
    operator fun invoke(): AIAgent
}