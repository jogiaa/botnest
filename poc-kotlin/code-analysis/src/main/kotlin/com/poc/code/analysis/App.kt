package com.poc.code.analysis

import com.poc.code.analysis.model.toUsageReport
import poc_kotlin.code_analysis.BuildConfig
import java.io.File

fun main() {
    val projectFile = BuildConfig.CODE_ANALYSIS_BASE_PATH
    val inputFileRelative = File("test/fixture/StockPriceFetcher.kt")
    val analysis = SourceAnalyzer().analyzeSourceRoot(projectFile.resolve(inputFileRelative).toPath())
    println("Got analysis: $analysis")
    println("With usage report: ${analysis.toUsageReport()}")
}