package com.poc.koog.utils

import kotlinx.serialization.Serializable

@Serializable
data class FileReadResult(
    val successful: Boolean,
    val fileContent: String? = null,
    val comment: String? = null
)