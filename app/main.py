import os

from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import Boolean, Column, Integer, String, create_engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./test.db")

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(bind=engine, autoflush=False)
Base = declarative_base()


class Task(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    done = Column(Boolean, default=False)


class TaskIn(BaseModel):
    title: str
    done: bool = False


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def to_dict(t: Task):
    return {"id": t.id, "title": t.title, "done": t.done}


app = FastAPI(title="Todo API")


@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/tasks", status_code=201)
def create_task(task: TaskIn, db: Session = Depends(get_db)):
    t = Task(title=task.title, done=task.done)
    db.add(t)
    db.commit()
    db.refresh(t)
    return to_dict(t)


@app.get("/tasks")
def list_tasks(db: Session = Depends(get_db)):
    return [to_dict(t) for t in db.query(Task).all()]


@app.get("/tasks/{task_id}")
def get_task(task_id: int, db: Session = Depends(get_db)):
    t = db.get(Task, task_id)
    if not t:
        raise HTTPException(status_code=404, detail="Task not found")
    return to_dict(t)


@app.put("/tasks/{task_id}")
def update_task(task_id: int, task: TaskIn, db: Session = Depends(get_db)):
    t = db.get(Task, task_id)
    if not t:
        raise HTTPException(status_code=404, detail="Task not found")
    t.title = task.title
    t.done = task.done
    db.commit()
    return to_dict(t)


@app.delete("/tasks/{task_id}", status_code=204)
def delete_task(task_id: int, db: Session = Depends(get_db)):
    t = db.get(Task, task_id)
    if not t:
        raise HTTPException(status_code=404, detail="Task not found")
    db.delete(t)
    db.commit()
