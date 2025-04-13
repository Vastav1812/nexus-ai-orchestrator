"""
API endpoints for crew management.
"""
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.crew import CrewCreate, CrewResponse, CrewUpdate
from app.orchestration.crews import crew_service

router = APIRouter()


@router.get("/", response_model=List[CrewResponse])
async def get_all_crews(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all crews."""
    return crew_service.get_all_crews(db, skip=skip, limit=limit)


@router.get("/{crew_id}", response_model=CrewResponse)
async def get_crew(crew_id: int, db: Session = Depends(get_db)):
    """Get crew by ID."""
    crew = crew_service.get_crew(db, crew_id=crew_id)
    if not crew:
        raise HTTPException(status_code=404, detail="Crew not found")
    return crew


@router.post("/", response_model=CrewResponse)
async def create_crew(crew: CrewCreate, db: Session = Depends(get_db)):
    """Create a new crew."""
    return crew_service.create_crew(db, crew=crew)


@router.put("/{crew_id}", response_model=CrewResponse)
async def update_crew(crew_id: int, crew: CrewUpdate, db: Session = Depends(get_db)):
    """Update crew by ID."""
    existing_crew = crew_service.get_crew(db, crew_id=crew_id)
    if not existing_crew:
        raise HTTPException(status_code=404, detail="Crew not found")
    return crew_service.update_crew(db, crew_id=crew_id, crew_update=crew)


@router.delete("/{crew_id}")
async def delete_crew(crew_id: int, db: Session = Depends(get_db)):
    """Delete crew by ID."""
    existing_crew = crew_service.get_crew(db, crew_id=crew_id)
    if not existing_crew:
        raise HTTPException(status_code=404, detail="Crew not found")
    crew_service.delete_crew(db, crew_id=crew_id)
    return {"message": "Crew deleted successfully"}


@router.post("/{crew_id}/run", response_model=dict)
async def run_crew(crew_id: int, task_data: dict, db: Session = Depends(get_db)):
    """Run a crew with specified task data."""
    crew = crew_service.get_crew(db, crew_id=crew_id)
    if not crew:
        raise HTTPException(status_code=404, detail="Crew not found")
    
    # Execute the crew's task
    result = crew_service.execute_crew_task(db, crew_id=crew_id, task_data=task_data)
    return {"status": "success", "result": result}
