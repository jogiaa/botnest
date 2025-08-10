### System Requirements
| Software | Version |
|----------|---------|
| Java     | 17      |
| Kotlin   | 2.1.20  |
| Gradle   | 8.14.3  |

> Note: Koog requires a minimum of JDK 17.

###  How to start application?

#### Pre-requisites
- You will need to have ["llama3.2"](https://ollama.com/library/llama3.2) running locally before you can start the application.
- Create a `local.properties` folder in the root of the `poc-koog` module. 
  - Ensure that you set the `file_tool_base_path` in `local.properties`
    Example: file_tool_base_path=/path/to/poc-koog/app/src/main/kotlin/com/poc/koog

#### Run the application
Run the following gradle command to run the application.
```bash
./gradlew :koog-agent:run
```
