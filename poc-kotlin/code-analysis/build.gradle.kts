import java.util.Properties

plugins {
    alias(libs.plugins.kotlin.jvm)
    alias(libs.plugins.build.config)
    application
}

kotlin {
    jvmToolchain(17)
}

repositories {
    mavenCentral()
    maven("https://jitpack.io")
}

buildConfig {
    val properties = Properties()
    rootProject.file("local.properties").reader().use { reader ->
        properties.load(reader)
        if (properties["code_analysis_base_path"] == null) {
            throw IllegalArgumentException(
                """
                    Ensure that you set the `code_analysis_base_path` in `local.properties`
                    Example:
                    code_analysis_base_path=/path/to/poc-kotlin/code-analysis/src/main/kotlin/com/poc/code/analysis
                """.trimIndent()
            )
        }
        buildConfigField("CODE_ANALYSIS_BASE_PATH", File(properties["code_analysis_base_path"] as String))
    }
}

dependencies {
    implementation(libs.ast.antlr.kotlin)
    implementation(libs.ast.common.jvm)
}

application {
    // Define the main class for the application.
    mainClass = "com.poc.code.analysis.AppKt"
}