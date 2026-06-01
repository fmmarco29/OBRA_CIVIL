from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class TaskBase(BaseModel):
    task_id: int
    name: str
    start_day: int
    duration: int
    cost: float
    predecessors: Optional[str] = ""

class TaskCreate(TaskBase):
    pass

class TaskUpdateActuals(BaseModel):
    actual_progress: float
    actual_cost: float

class TaskOut(TaskBase):
    id: int
    project_id: int
    actual_progress: float
    actual_cost: float

    class Config:
        from_attributes = True

class ProjectBase(BaseModel):
    name: str
    description: Optional[str] = None
    budget: float = 0.0

class ProjectCreate(ProjectBase):
    tasks: List[TaskCreate] = []

class ProjectOut(ProjectBase):
    id: int
    created_at: datetime
    tasks: List[TaskOut] = []

    class Config:
        from_attributes = True
