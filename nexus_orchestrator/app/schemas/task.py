"""
Schema definitions for tasks.
"""
from typing import Dict, Optional
from pydantic import BaseModel, Field


class TaskBase(BaseModel):
    """Base schema for tasks."""
    
    description: str = Field(..., description="Task description")
    expected_output: str = Field(..., description="Expected output description")
    agent_id: int = Field(..., description="ID of the agent assigned to this task")
    context: Optional[str] = Field(None, description="Additional context for the task")
    async_execution: bool = Field(False, description="Whether the task should be executed asynchronously")
    config: Optional[Dict] = Field({}, description="Additional configuration parameters")


class TaskCreate(TaskBase):
    """Schema for creating tasks."""
    
    pass


class TaskUpdate(BaseModel):
    """Schema for updating tasks."""
    
    description: Optional[str] = None
    expected_output: Optional[str] = None
    agent_id: Optional[int] = None
    context: Optional[str] = None
    async_execution: Optional[bool] = None
    config: Optional[Dict] = None


class TaskInDB(TaskBase):
    """Schema for tasks in the database."""
    
    id: int
    
    class Config:
        """Pydantic config."""
        orm_mode = True


class TaskResponse(TaskInDB):
    """Schema for task responses."""
    
    pass
