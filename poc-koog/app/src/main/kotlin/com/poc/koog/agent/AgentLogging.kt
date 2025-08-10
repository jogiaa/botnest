package com.poc.koog.agent

import ai.koog.agents.core.agent.AIAgent
import ai.koog.agents.features.eventHandler.feature.handleEvents
import ai.koog.prompt.message.Message
import kotlin.uuid.ExperimentalUuidApi

@OptIn(ExperimentalUuidApi::class)
fun AIAgent.FeatureContext.enableDebugging() {
    handleEvents {
        onBeforeLLMCall { prompt, tools, model, uuid ->
            println(
                """
                    ···············································································································
                    :                                                                                                             :
                    :                                                                                                             :
                    :   _      _      ___ ___         __   ____  _      _              ____     ___  _____   ___   ____     ___   :
                    :  | |    | |    |   |   |       /  ] /    || |    | |     __     |    \   /  _]|     | /   \ |    \   /  _]  :
                    :  | |    | |    | _   _ |      /  / |  o  || |    | |    |  |    |  o  ) /  [_ |   __||     ||  D  ) /  [_   :
                    :  | |___ | |___ |  \_/  |     /  /  |     || |___ | |___ |__|    |     ||    _]|  |_  |  O  ||    / |    _]  :
                    :  |     ||     ||   |   |    /   \_ |  _  ||     ||     | __     |  O  ||   [_ |   _] |     ||    \ |   [_   :
                    :  |     ||     ||   |   |    \     ||  |  ||     ||     ||  |    |     ||     ||  |   |     ||  .  \|     |  :
                    :  |_____||_____||___|___|     \____||__|__||_____||_____||__|    |_____||_____||__|    \___/ |__|\_||_____|  :
                    :                                                                                                             :
                    :                                                                                                             :
                    ···············································································································
                """.trimIndent()
            )
            println("Prompt >>>")
            prompt.messages.forEach { message ->
                println("Role: ${message.role}")
                println("Content: ${message.content}")
            }
            println("Tools >>>")
            tools.forEach { tool ->
                println("Name: ${tool.name}")
                println("Description: ${tool.description}")
            }
            println("Model >>>")
            println("Id: ${model.id}")
            println("Capabilities: ${model.capabilities}")
        }
        onAfterLLMCall { prompt, tools, model, responses, sessionUuid ->
            println(
                """
                    ·········································································································
                    :                                                                                                       :
                    :                                                                                                       :
                    :   _      _      ___ ___         __   ____  _      _               ____  _____  ______    ___  ____    :
                    :  | |    | |    |   |   |       /  ] /    || |    | |     __      /    ||     ||      |  /  _]|    \   :
                    :  | |    | |    | _   _ |      /  / |  o  || |    | |    |  |    |  o  ||   __||      | /  [_ |  D  )  :
                    :  | |___ | |___ |  \_/  |     /  /  |     || |___ | |___ |__|    |     ||  |_  |_|  |_||    _]|    /   :
                    :  |     ||     ||   |   |    /   \_ |  _  ||     ||     | __     |  _  ||   _]   |  |  |   [_ |    \   :
                    :  |     ||     ||   |   |    \     ||  |  ||     ||     ||  |    |  |  ||  |     |  |  |     ||  .  \  :
                    :  |_____||_____||___|___|     \____||__|__||_____||_____||__|    |__|__||__|     |__|  |_____||__|\_|  :
                    :                                                                                                       :
                    :                                                                                                       :
                    ·········································································································
                """.trimIndent()
            )
            println("Response >>>")
            responses.forEach { message ->
                println("Role: ${message.role}")
                println("Content: ${message.content}")
                when (message) {
                    is Message.Assistant -> {
                        println("Finish Reason: ${message.finishReason}")
                    }
                    is Message.Tool.Call -> {
                        println("Tool: ${message.tool}")
                        println("Tool: ${message.contentJson}")
                    }
                }
            }
        }
        onToolCall { tool, args ->
            println(
                """
                    ···································································
                    :                                                                 :
                    :                                                                 :
                    :   ______   ___    ___   _             __   ____  _      _       :
                    :  |      | /   \  /   \ | |           /  ] /    || |    | |      :
                    :  |      ||     ||     || |          /  / |  o  || |    | |      :
                    :  |_|  |_||  O  ||  O  || |___      /  /  |     || |___ | |___   :
                    :    |  |  |     ||     ||     |    /   \_ |  _  ||     ||     |  :
                    :    |  |  |     ||     ||     |    \     ||  |  ||     ||     |  :
                    :    |__|   \___/  \___/ |_____|     \____||__|__||_____||_____|  :
                    :                                                                 :
                    :                                                                 :
                    ···································································
                """.trimIndent()
            )
            println("Calling tool: ${tool.name} with args: $args")
        }
        onAgentFinished { strategyName, result ->
            println("Agent finished strategy: $strategyName with result $result")
        }
    }
}