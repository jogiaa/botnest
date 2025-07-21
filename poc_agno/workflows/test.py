from fastapi import FastAPI

from poc_agno.llm_model_config import llm_model

app = FastAPI()

@app.get("/ask")
def ask(prompt: str):
    return {"response": llm_model.invoke(prompt)}