### System Requirements
| Software | Version |
|----------|---------|
| Java     | 17      |
| Kotlin   | 2.1.20  |
| Gradle   | 8.14.3  |

###  How to start application?

#### Pre-requisites
- Create a `local.properties` folder in the root of the `poc-kotlin` module.
    - Ensure that you set the `code_analysis_base_path` in `local.properties`
      Example: code_analysis_base_path=/path/to/code-analysis/app/src/main/kotlin/com/poc/code/analysis

#### Run the application
Run the following gradle command to run the application.
```bash
./gradlew :code-analysis:run
```
