"""
Service for agent operations.
"""
from typing import List, Optional

from sqlalchemy.orm import Session

from app.db.models.agent import Agent
from app.schemas.agent import AgentCreate, AgentUpdate


def get_agent(db: Session, agent_id: int) -> Optional[Agent]:
    """Get an agent by ID."""
    return db.query(Agent).filter(Agent.id == agent_id).first()


def get_all_agents(db: Session, skip: int = 0, limit: int = 100) -> List[Agent]:
    """Get all agents."""
    return db.query(Agent).offset(skip).limit(limit).all()


def create_agent(db: Session, agent: AgentCreate) -> Agent:
    """Create a new agent."""
    db_agent = Agent(
        name=agent.name,
        description=agent.description,
        model_name=agent.model_name,
        provider=agent.provider,
        goal=agent.goal,
        role=agent.role,
        backstory=agent.backstory,
        max_iterations=agent.max_iterations,
        memory_enabled=agent.memory_enabled,
        verbose=agent.verbose,
        config=agent.config,
        skills=agent.skills
    )
    db.add(db_agent)
    db.commit()
    db.refresh(db_agent)
    return db_agent


def update_agent(db: Session, agent_id: int, agent_update: AgentUpdate) -> Agent:
    """Update an agent."""
    db_agent = get_agent(db, agent_id=agent_id)
    
    # Update fields
    update_data = agent_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_agent, field, value)
    
    db.commit()
    db.refresh(db_agent)
    return db_agent


def delete_agent(db: Session, agent_id: int) -> None:
    """Delete an agent."""
    db_agent = get_agent(db, agent_id=agent_id)
    db.delete(db_agent)
    db.commit()


def create_agent_instance(db: Session, agent_id: int):
    """Create a CrewAI agent instance from database model."""
    from crewai import Agent
    
    db_agent = get_agent(db, agent_id=agent_id)
    
    if not db_agent:
        raise ValueError(f"Agent with ID {agent_id} not found")
    
    # Create CrewAI agent
    agent = Agent(
        role=db_agent.role,
        goal=db_agent.goal,
        backstory=db_agent.backstory or "",
        verbose=db_agent.verbose,
        memory=db_agent.memory_enabled,
        allow_delegation=db_agent.config.get("allow_delegation", True),
        tools=db_agent.config.get("tools", [])
    )
    
    return agent
