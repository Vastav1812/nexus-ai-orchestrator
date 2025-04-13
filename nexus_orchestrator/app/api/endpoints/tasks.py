"""
API endpoints for task management.
"""
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.task import TaskCreate, TaskResponse, TaskUpdate
from app.orchestration.tasks import task_service

router = APIRouter()


@router.get("/", response_model=List[TaskResponse])
async def get_all_tasks(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all tasks."""
    return task_service.get_all_tasks(db, skip=skip, limit=limit)


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(task_id: int, db: Session = Depends(get_db)):
    """Get task by ID."""
    task = task_service.get_task(db, task_id=task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.post("/", response_model=TaskResponse)
async def create_task(task: TaskCreate, db: Session = Depends(get_db)):
    """Create a new task."""
    return task_service.create_task(db, task=task)


@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(task_id: int, task: TaskUpdate, db: Session = Depends(get_db)):
    """Update task by ID."""
    existing_task = task_service.get_task(db, task_id=task_id)
    if not existing_task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task_service.update_task(db, task_id=task_id, task_update=task)


@router.delete("/{task_id}")
async def delete_task(task_id: int, db: Session = Depends(get_db)):
    """Delete task by ID."""
    existing_task = task_service.get_task(db, task_id=task_id)
    if not existing_task:
        raise HTTPException(status_code=404, detail="Task not found")
    task_service.delete_task(db, task_id=task_id)
    return {"message": "Task deleted successfully"}
