package com.poc.koog.utils

import kotlinx.serialization.Serializable

@Serializable
data class FileWriteResult(
    val successful: Boolean,
    val comment: String? = null
)