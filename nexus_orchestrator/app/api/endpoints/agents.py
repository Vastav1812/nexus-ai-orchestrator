"""
API endpoints for agent management.
"""
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.agent import AgentCreate, AgentResponse, AgentUpdate
from app.orchestration.agents import agent_service

router = APIRouter()


@router.get("/", response_model=List[AgentResponse])
async def get_all_agents(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all agents."""
    return agent_service.get_all_agents(db, skip=skip, limit=limit)


@router.get("/{agent_id}", response_model=AgentResponse)
async def get_agent(agent_id: int, db: Session = Depends(get_db)):
    """Get agent by ID."""
    agent = agent_service.get_agent(db, agent_id=agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent


@router.post("/", response_model=AgentResponse)
async def create_agent(agent: AgentCreate, db: Session = Depends(get_db)):
    """Create a new agent."""
    return agent_service.create_agent(db, agent=agent)


@router.put("/{agent_id}", response_model=AgentResponse)
async def update_agent(agent_id: int, agent: AgentUpdate, db: Session = Depends(get_db)):
    """Update agent by ID."""
    existing_agent = agent_service.get_agent(db, agent_id=agent_id)
    if not existing_agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent_service.update_agent(db, agent_id=agent_id, agent_update=agent)


@router.delete("/{agent_id}")
async def delete_agent(agent_id: int, db: Session = Depends(get_db)):
    """Delete agent by ID."""
    existing_agent = agent_service.get_agent(db, agent_id=agent_id)
    if not existing_agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    agent_service.delete_agent(db, agent_id=agent_id)
    return {"message": "Agent deleted successfully"}
