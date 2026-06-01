from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from src.database.session import Base
import datetime

class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String, nullable=True)
    budget = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    tasks = relationship("Task", back_populates="project", cascade="all, delete-orphan")


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    task_id = Column(Integer)  # ID from MS Project (WBS)
    name = Column(String, index=True)
    start_day = Column(Integer)
    duration = Column(Integer)
    cost = Column(Float, default=0.0)
    predecessors = Column(String, default="")  # Comma separated IDs
    
    # Tracking actuals
    actual_progress = Column(Float, default=0.0) # 0.0 to 1.0
    actual_cost = Column(Float, default=0.0)
    
    project = relationship("Project", back_populates="tasks")
