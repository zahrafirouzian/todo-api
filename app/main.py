from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="Todo API")

tasks = {}
next_id = 1


class TaskIn(BaseModel):
    title: str
    done: bool = False


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/tasks", status_code=201)
def create_task(task: TaskIn):
    global next_id
    tasks[next_id] = {"id": next_id, **task.model_dump()}
    next_id += 1
    return tasks[next_id - 1]


@app.get("/tasks")
def list_tasks():
    return list(tasks.values())


@app.get("/tasks/{task_id}")
def get_task(task_id: int):
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    return tasks[task_id]


@app.put("/tasks/{task_id}")
def update_task(task_id: int, task: TaskIn):
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    tasks[task_id] = {"id": task_id, **task.model_dump()}
    return tasks[task_id]


@app.delete("/tasks/{task_id}", status_code=204)
def delete_task(task_id: int):
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    del tasks[task_id]
