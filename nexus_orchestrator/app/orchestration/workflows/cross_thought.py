"""
Cross-thought workflow engine for complex agent communication patterns.
"""
from typing import Dict, List, Any, Optional
import uuid
import time
import json
from pydantic import BaseModel

from app.services.blockchain import blockchain_service


class Thought(BaseModel):
    """A thought from an agent."""
    id: str
    agent_id: int
    content: str
    references: List[str] = []
    created_at: float
    context: Dict[str, Any] = {}


class ThoughtChain(BaseModel):
    """A chain of thoughts from multiple agents."""
    id: str
    task_id: str
    thoughts: List[Thought] = []
    status: str = "active"
    created_at: float
    updated_at: float
    metadata: Dict[str, Any] = {}


class CrossThoughtEngine:
    """
    Engine for managing cross-agent thought processes.
    
    This enables agents to build on each other's thoughts and
    generate collaborative insights.
    """
    
    def __init__(self):
        """Initialize the cross-thought engine."""
        self._thought_chains: Dict[str, ThoughtChain] = {}
    
    def create_thought_chain(self, task_id: str, metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Create a new thought chain.
        
        Args:
            task_id: The ID of the task this thought chain is for
            metadata: Optional metadata for the thought chain
            
        Returns:
            Chain ID
        """
        chain_id = str(uuid.uuid4())
        now = time.time()
        
        thought_chain = ThoughtChain(
            id=chain_id,
            task_id=task_id,
            created_at=now,
            updated_at=now,
            metadata=metadata or {}
        )
        
        self._thought_chains[chain_id] = thought_chain
        
        # Log on blockchain
        blockchain_service.log_decision(
            f"thought_chain_{chain_id}",
            thought_chain.dict()
        )
        
        return chain_id
    
    def add_thought(self, chain_id: str, agent_id: int, content: str, 
                   references: Optional[List[str]] = None, 
                   context: Optional[Dict[str, Any]] = None) -> str:
        """
        Add a thought to a chain.
        
        Args:
            chain_id: The ID of the thought chain
            agent_id: The ID of the agent adding the thought
            content: The content of the thought
            references: Optional list of IDs of thoughts this one references
            context: Optional context for the thought
            
        Returns:
            Thought ID
        """
        if chain_id not in self._thought_chains:
            raise ValueError(f"Thought chain {chain_id} not found")
        
        thought_id = str(uuid.uuid4())
        thought = Thought(
            id=thought_id,
            agent_id=agent_id,
            content=content,
            references=references or [],
            created_at=time.time(),
            context=context or {}
        )
        
        # Add to chain
        self._thought_chains[chain_id].thoughts.append(thought)
        self._thought_chains[chain_id].updated_at = time.time()
        
        # Log on blockchain
        blockchain_service.log_decision(
            f"thought_{thought_id}",
            thought.dict()
        )
        
        return thought_id
    
    def get_thought_chain(self, chain_id: str) -> ThoughtChain:
        """
        Get a thought chain.
        
        Args:
            chain_id: The ID of the thought chain
            
        Returns:
            The thought chain
        """
        if chain_id not in self._thought_chains:
            raise ValueError(f"Thought chain {chain_id} not found")
        
        return self._thought_chains[chain_id]
    
    def get_agent_thoughts(self, chain_id: str, agent_id: int) -> List[Thought]:
        """
        Get all thoughts from a specific agent in a chain.
        
        Args:
            chain_id: The ID of the thought chain
            agent_id: The ID of the agent
            
        Returns:
            List of thoughts from the agent
        """
        if chain_id not in self._thought_chains:
            raise ValueError(f"Thought chain {chain_id} not found")
        
        return [
            thought for thought in self._thought_chains[chain_id].thoughts
            if thought.agent_id == agent_id
        ]
    
    def get_latest_thoughts(self, chain_id: str, limit: int = 5) -> List[Thought]:
        """
        Get the latest thoughts in a chain.
        
        Args:
            chain_id: The ID of the thought chain
            limit: Maximum number of thoughts to return
            
        Returns:
            List of latest thoughts
        """
        if chain_id not in self._thought_chains:
            raise ValueError(f"Thought chain {chain_id} not found")
        
        sorted_thoughts = sorted(
            self._thought_chains[chain_id].thoughts,
            key=lambda t: t.created_at,
            reverse=True
        )
        
        return sorted_thoughts[:limit]
    
    def close_thought_chain(self, chain_id: str, summary: Optional[str] = None) -> None:
        """
        Close a thought chain.
        
        Args:
            chain_id: The ID of the thought chain
            summary: Optional summary of the thought chain
        """
        if chain_id not in self._thought_chains:
            raise ValueError(f"Thought chain {chain_id} not found")
        
        self._thought_chains[chain_id].status = "closed"
        self._thought_chains[chain_id].updated_at = time.time()
        
        if summary:
            self._thought_chains[chain_id].metadata["summary"] = summary
        
        # Log on blockchain
        blockchain_service.log_decision(
            f"thought_chain_close_{chain_id}",
            self._thought_chains[chain_id].dict()
        )
    
    def export_thought_chain(self, chain_id: str) -> Dict[str, Any]:
        """
        Export a thought chain as a dictionary.
        
        Args:
            chain_id: The ID of the thought chain
            
        Returns:
            Dictionary representation of the thought chain
        """
        if chain_id not in self._thought_chains:
            raise ValueError(f"Thought chain {chain_id} not found")
        
        return self._thought_chains[chain_id].dict()
    
    def import_thought_chain(self, data: Dict[str, Any]) -> str:
        """
        Import a thought chain from a dictionary.
        
        Args:
            data: Dictionary representation of the thought chain
            
        Returns:
            Chain ID
        """
        thought_chain = ThoughtChain(**data)
        self._thought_chains[thought_chain.id] = thought_chain
        return thought_chain.id


# Create singleton instance
cross_thought_engine = CrossThoughtEngine()
