"""
Service for crew operations.
"""
from typing import List, Optional, Dict, Any

from sqlalchemy.orm import Session
from crewai import Crew as CrewAIInstance
from crewai import Task as CrewAITask

from app.db.models.crew import Crew
from app.schemas.crew import CrewCreate, CrewUpdate
from app.orchestration.agents.agent_service import create_agent_instance
from app.orchestration.tasks.task_service import get_task, create_task_instance


def get_crew(db: Session, crew_id: int) -> Optional[Crew]:
    """Get a crew by ID."""
    return db.query(Crew).filter(Crew.id == crew_id).first()


def get_all_crews(db: Session, skip: int = 0, limit: int = 100) -> List[Crew]:
    """Get all crews."""
    return db.query(Crew).offset(skip).limit(limit).all()


def create_crew(db: Session, crew: CrewCreate) -> Crew:
    """Create a new crew."""
    db_crew = Crew(
        name=crew.name,
        description=crew.description,
        goal=crew.goal,
        tasks_sequential=crew.tasks_sequential,
        verbose=crew.verbose,
        config=crew.config,
        agent_ids=crew.agent_ids,
        task_ids=crew.task_ids
    )
    db.add(db_crew)
    db.commit()
    db.refresh(db_crew)
    return db_crew


def update_crew(db: Session, crew_id: int, crew_update: CrewUpdate) -> Crew:
    """Update a crew."""
    db_crew = get_crew(db, crew_id=crew_id)
    
    # Update fields
    update_data = crew_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_crew, field, value)
    
    db.commit()
    db.refresh(db_crew)
    return db_crew


def delete_crew(db: Session, crew_id: int) -> None:
    """Delete a crew."""
    db_crew = get_crew(db, crew_id=crew_id)
    db.delete(db_crew)
    db.commit()


def create_crew_instance(db: Session, crew_id: int):
    """Create a CrewAI crew instance from database model."""
    db_crew = get_crew(db, crew_id=crew_id)
    
    if not db_crew:
        raise ValueError(f"Crew with ID {crew_id} not found")
    
    # Create agent instances
    agents = [create_agent_instance(db, agent_id) for agent_id in db_crew.agent_ids]
    
    # Create task instances if there are any
    tasks = []
    if db_crew.task_ids:
        tasks = [create_task_instance(db, task_id) for task_id in db_crew.task_ids]
    
    # Create CrewAI crew
    crew = CrewAIInstance(
        agents=agents,
        tasks=tasks,
        verbose=db_crew.verbose,
        process=db_crew.tasks_sequential
    )
    
    return crew


def execute_crew_task(db: Session, crew_id: int, task_data: Dict[str, Any]):
    """Execute a task with the crew."""
    # Create crew instance
    crew_instance = create_crew_instance(db, crew_id)
    
    # If we have a specific task to run that's not in the crew's task list
    if "task_description" in task_data:
        # Create a one-off task
        task = CrewAITask(
            description=task_data["task_description"],
            expected_output=task_data.get("expected_output", "Detailed analysis and results"),
            agent=crew_instance.agents[0]  # Assign to first agent as default
        )
        result = crew_instance.execute_task(task)
    else:
        # Run the crew with its predefined tasks
        result = crew_instance.kickoff()
    
    return result
