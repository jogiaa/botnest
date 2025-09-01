package com.poc.code.analysis.model

data class Analysis(
    val name: String,
    val inherits: Set<String>,
    val uses: Set<String>,
)

data class UsageReport(
    val name: String,
    val inheritors: Set<String>,
    val users: Set<String>,
)

fun List<Analysis>.toUsageReport(): List<UsageReport> = map { entity ->
    UsageReport(
        name = entity.name,
        inheritors = filter { it.inherits.contains(entity.name) }
            .map { it.name }.toSet(),
        users = filter { it.uses.contains(entity.name) }
            .map { it.name }.toSet(),
    )
}