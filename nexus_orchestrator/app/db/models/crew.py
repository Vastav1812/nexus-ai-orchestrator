"""
Database models for crews.
"""
from sqlalchemy import Boolean, Column, Integer, String, JSON
from sqlalchemy.dialects.postgresql import ARRAY

from app.db.session import Base


class Crew(Base):
    """Database model for crews."""
    
    __tablename__ = "crews"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String)
    goal = Column(String)
    tasks_sequential = Column(Boolean, default=True)
    verbose = Column(Boolean, default=False)
    config = Column(JSON, default={})
    agent_ids = Column(ARRAY(Integer), nullable=False)
    task_ids = Column(ARRAY(Integer), default=[])
