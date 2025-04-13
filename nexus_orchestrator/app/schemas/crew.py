"""
Schema definitions for crews.
"""
from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class CrewBase(BaseModel):
    """Base schema for crews."""
    
    name: str = Field(..., description="Crew name")
    description: str = Field(..., description="Crew description")
    goal: str = Field(..., description="The crew's goal")
    tasks_sequential: bool = Field(True, description="Whether tasks are executed sequentially")
    verbose: bool = Field(False, description="Verbose mode")
    config: Optional[Dict] = Field({}, description="Additional configuration parameters")


class CrewCreate(CrewBase):
    """Schema for creating crews."""
    
    agent_ids: List[int] = Field(..., description="List of agent IDs in this crew")
    task_ids: Optional[List[int]] = Field([], description="List of task IDs assigned to this crew")


class CrewUpdate(BaseModel):
    """Schema for updating crews."""
    
    name: Optional[str] = None
    description: Optional[str] = None
    goal: Optional[str] = None
    tasks_sequential: Optional[bool] = None
    verbose: Optional[bool] = None
    config: Optional[Dict] = None
    agent_ids: Optional[List[int]] = None
    task_ids: Optional[List[int]] = None


class CrewInDB(CrewBase):
    """Schema for crews in the database."""
    
    id: int
    agent_ids: List[int]
    task_ids: List[int] = []
    
    class Config:
        """Pydantic config."""
        orm_mode = True


class CrewResponse(CrewInDB):
    """Schema for crew responses."""
    
    pass
