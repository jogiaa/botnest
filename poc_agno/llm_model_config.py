import copy

from agno.debug import enable_debug_mode
from agno.models.ollama import Ollama

# --- Model Constants ---
MODEL_NAME_LLAMA_3 = "llama3.2"
MODEL_NAME_GEMMA_3_1B = "gemma3:1b"
MODEL_NAME_CODE_LLAMA_7b = "codellama:7b"
MODEL_NAME_CODE_GEMMA_7b = "codegemma:7b"
MODEL_NAME_DEEPSEEK_R_1_8B = "deepseek-r1:8b"

# --- Enable Debug Mode ---
enable_debug_mode()

# --- Initialize a default models ---
llm_model = Ollama(id=MODEL_NAME_LLAMA_3)

# this can work without tools option
code_model = Ollama(
    id=MODEL_NAME_CODE_GEMMA_7b,
    options={
        "temperature": 0.0,
        "top_p": 1.0,
        "frequency_penalty": 0.0,
        "presence_penalty": 0.0,
    }
)

def set_llm_model(model_id: str):
    """
    Reassigns the global llm_model to a new Ollama instance with the given model_id.
    """
    print(f"Switching model to: {model_id}")

    # Switch base LLM model
    global llm_model
    llm_model = Ollama(id=model_id)

    # Switch code model
    global code_model
    code_model.id = model_id

# API-KEY - gpt-4o-mini
# openai_model = OpenAIChat(
#     id = "gpt-4o-mini",
#     api_key=get(OPEN_AI_API_KEY),
# )
