from fastapi import FastAPI
from agent.agent import run_agent

app = FastAPI(
    title="AI Agent System",
    version="1.0.0"
)

@app.get("/")
def home():
    return {"message": "AI Agent API Running!"}

@app.get("/run")
def run(task: str):
    result = run_agent(task)
    return {"input": task, "result": result}
