"""
Database models for agents.
"""
from sqlalchemy import Boolean, Column, Integer, String, JSON
from sqlalchemy.dialects.postgresql import ARRAY

from app.db.session import Base


class Agent(Base):
    """Database model for agents."""
    
    __tablename__ = "agents"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String)
    model_name = Column(String)
    provider = Column(String)
    goal = Column(String)
    role = Column(String)
    backstory = Column(String, nullable=True)
    max_iterations = Column(Integer, default=5)
    memory_enabled = Column(Boolean, default=True)
    verbose = Column(Boolean, default=False)
    config = Column(JSON, default={})
    skills = Column(ARRAY(String), default=[])
