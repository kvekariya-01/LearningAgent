from fastapi import FastAPI
from agent.agent import run_agent

app = FastAPI()

@app.get("/")
def home():
    return {"message": "AI Agent is Running!"}

@app.get("/run")
def run(task: str):
    result = run_agent(task)
    return {"task": task, "result": result}
