from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.orm import Session
from typing import List

from src.database.session import get_db
from src.database.models import Project, Task
from src.models.schemas import ProjectOut, ProjectCreate, TaskCreate, TaskOut, TaskUpdateActuals
from src.document_processor import DocumentProcessor

router = APIRouter(prefix="/projects", tags=["projects"])
doc_processor = DocumentProcessor()

@router.get("/", response_model=List[ProjectOut])
def get_projects(db: Session = Depends(get_db)):
    projects = db.query(Project).all()
    return projects

@router.post("/", response_model=ProjectOut)
def create_project(project: ProjectCreate, db: Session = Depends(get_db)):
    db_project = Project(name=project.name, description=project.description, budget=project.budget)
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    
    for task in project.tasks:
        db_task = Task(
            project_id=db_project.id,
            task_id=task.task_id,
            name=task.name,
            start_day=task.start_day,
            duration=task.duration,
            cost=task.cost,
            predecessors=task.predecessors
        )
        db.add(db_task)
    
    db.commit()
    db.refresh(db_project)
    return db_project

@router.get("/{project_id}", response_model=ProjectOut)
def get_project(project_id: int, db: Session = Depends(get_db)):
    db_project = db.query(Project).filter(Project.id == project_id).first()
    if db_project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return db_project

@router.post("/{project_id}/upload_gantt")
async def upload_gantt(project_id: int, file: UploadFile = File(...), db: Session = Depends(get_db)):
    db_project = db.query(Project).filter(Project.id == project_id).first()
    if db_project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    
    content = await file.read()
    
    # Process file based on extension
    filename = file.filename.lower()
    df = None
    try:
        if filename.endswith(".pdf"):
            df = doc_processor.parse_pdf_to_wbs(content)
        elif filename.endswith(".xml"):
            df = doc_processor.parse_project_xml(content)
        elif filename.endswith(".csv"):
            df = doc_processor.parse_gantt_csv(content)
        else:
            raise HTTPException(status_code=400, detail="Formato de archivo no soportado. Usa PDF, XML o CSV.")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error parseando archivo: {str(e)}")

    if df is None or df.empty:
         raise HTTPException(status_code=400, detail="El archivo parseado está vacío o es inválido")

    # Clear existing tasks
    db.query(Task).filter(Task.project_id == project_id).delete()
    
    # Add new tasks
    for _, row in df.iterrows():
        db_task = Task(
            project_id=db_project.id,
            task_id=int(row.get("Task_ID", 0)),
            name=str(row.get("Task", "Unknown")),
            start_day=int(row.get("Start_Day", 1)),
            duration=int(row.get("Duration", 1)),
            cost=float(row.get("Cost", 0.0)),
            predecessors=str(row.get("Predecessors", ""))
        )
        db.add(db_task)
    
    # Update project budget
    db_project.budget = float(df["Cost"].sum())
    
    db.commit()
    db.refresh(db_project)
    return {"message": "Gantt subido y estructurado con éxito", "tasks_imported": len(df)}

@router.put("/tasks/{task_db_id}/actuals", response_model=TaskOut)
def update_task_actuals(task_db_id: int, actuals: TaskUpdateActuals, db: Session = Depends(get_db)):
    db_task = db.query(Task).filter(Task.id == task_db_id).first()
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    
    db_task.actual_progress = actuals.actual_progress
    db_task.actual_cost = actuals.actual_cost
    db.commit()
    db.refresh(db_task)
    return db_task
