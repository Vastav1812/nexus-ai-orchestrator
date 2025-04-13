"""
API endpoints for AI orchestration workflows.
"""
from typing import Dict, List, Any, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.orchestration.workflows.orchestrator import (
    AIOrchestrator, OrchestrationTask, AgentRole
)
from app.orchestration.workflows.cross_thought import cross_thought_engine


router = APIRouter()


class OrchestrationRequest(BaseModel):
    """Request model for orchestration."""
    prompt: str
    roles: List[Dict[str, Any]]
    workflow_type: str = "parallel"  # "parallel", "sequential", or "consensus"
    max_iterations: int = 3
    consensus_threshold: float = 0.7  # For consensus workflows
    metadata: Dict[str, Any] = {}


@router.post("/orchestrate")
async def orchestrate(request: OrchestrationRequest):
    """
    Orchestrate a task across multiple AI agents.
    """
    # Create agent roles
    roles = []
    for role_data in request.roles:
        roles.append(
            AgentRole(
                role_name=role_data["role_name"],
                agent_id=role_data.get("agent_id", 0),  # Default to 0 if not provided
                instructions=role_data.get("instructions", ""),
                prompt_template=role_data.get("prompt_template", "{prompt}"),
                response_format=role_data.get("response_format"),
                model_name=role_data.get("model_name"),
                provider=role_data.get("provider")
            )
        )
    
    # Create task
    task = OrchestrationTask(
        task_id=f"task_{len(request.prompt) % 1000}_{hash(request.prompt) % 10000}",
        prompt=request.prompt,
        roles=roles,
        workflow_type=request.workflow_type,
        max_iterations=request.max_iterations,
        consensus_threshold=request.consensus_threshold,
        metadata=request.metadata
    )
    
    # Orchestrate
    async with AIOrchestrator() as orchestrator:
        results = await orchestrator.orchestrate(task)
    
    return results


@router.get("/thought-chains/{chain_id}")
async def get_thought_chain(chain_id: str):
    """
    Get a thought chain by ID.
    """
    try:
        thought_chain = cross_thought_engine.get_thought_chain(chain_id)
        return thought_chain
    except ValueError:
        raise HTTPException(status_code=404, detail="Thought chain not found")


@router.get("/thought-chains/{chain_id}/thoughts")
async def get_thoughts(chain_id: str, agent_id: Optional[int] = None, limit: int = 10):
    """
    Get thoughts from a thought chain.
    """
    try:
        if agent_id is not None:
            thoughts = cross_thought_engine.get_agent_thoughts(chain_id, agent_id)
        else:
            thoughts = cross_thought_engine.get_latest_thoughts(chain_id, limit)
        return thoughts
    except ValueError:
        raise HTTPException(status_code=404, detail="Thought chain not found")
