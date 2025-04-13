"""
Schema definitions for agents.
"""
from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class AgentBase(BaseModel):
    """Base schema for agents."""
    
    name: str = Field(..., description="Agent name")
    description: str = Field(..., description="Agent description")
    model_name: str = Field(..., description="Model name (e.g., gpt-4, claude-3-opus)")
    provider: str = Field(..., description="AI provider (e.g., openai, anthropic, cohere)")
    goal: str = Field(..., description="The agent's goal")
    role: str = Field(..., description="The agent's role description")
    backstory: Optional[str] = Field(None, description="The agent's backstory")
    max_iterations: Optional[int] = Field(5, description="Maximum number of iterations")
    memory_enabled: bool = Field(True, description="Whether agent memory is enabled")
    verbose: bool = Field(False, description="Verbose mode")
    config: Optional[Dict] = Field({}, description="Additional configuration parameters")


class AgentCreate(AgentBase):
    """Schema for creating agents."""
    
    skills: List[str] = Field([], description="Agent skills")


class AgentUpdate(BaseModel):
    """Schema for updating agents."""
    
    name: Optional[str] = None
    description: Optional[str] = None
    model_name: Optional[str] = None
    provider: Optional[str] = None
    goal: Optional[str] = None
    role: Optional[str] = None
    backstory: Optional[str] = None
    max_iterations: Optional[int] = None
    memory_enabled: Optional[bool] = None
    verbose: Optional[bool] = None
    config: Optional[Dict] = None
    skills: Optional[List[str]] = None


class AgentInDB(AgentBase):
    """Schema for agents in the database."""
    
    id: int
    skills: List[str] = []
    
    class Config:
        """Pydantic config."""
        orm_mode = True


class AgentResponse(AgentInDB):
    """Schema for agent responses."""
    
    pass
