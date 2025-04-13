"""
AI Orchestrator - Coordinates multiple AI agents to solve complex tasks.
"""
import asyncio
import uuid
from typing import Dict, List, Any, Optional, Tuple
import json
import httpx
import os
from pydantic import BaseModel

from app.core.config import settings
from app.orchestration.agents.agent_service import get_agent
from app.orchestration.workflows.cross_thought import cross_thought_engine
from app.services.blockchain import blockchain_service


class AgentRole(BaseModel):
    """An agent role with specific prompts and instructions."""
    role_name: str
    agent_id: int
    instructions: str
    prompt_template: str
    response_format: Optional[str] = None
    model_name: Optional[str] = None
    provider: Optional[str] = None
    

class OrchestrationTask(BaseModel):
    """A task for the orchestrator to process."""
    task_id: str
    prompt: str
    roles: List[AgentRole]
    workflow_type: str = "parallel"  # "parallel", "sequential", or "consensus"
    max_iterations: int = 3
    consensus_threshold: float = 0.7  # For consensus workflows
    metadata: Dict[str, Any] = {}


class AIOrchestrator:
    """
    Orchestrates multiple AI agents to solve complex tasks.
    
    This service coordinates multiple AI models through different workflows
    and manages cross-agent communication patterns.
    """
    
    def __init__(self):
        """Initialize the AI orchestrator."""
        self.session = httpx.AsyncClient(timeout=60.0)
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.session.aclose()
    
    async def orchestrate(self, task: OrchestrationTask) -> Dict[str, Any]:
        """
        Orchestrate a task across multiple AI agents.
        
        Args:
            task: The orchestration task
            
        Returns:
            Results from the orchestration
        """
        # Create a thought chain for this task
        thought_chain_id = cross_thought_engine.create_thought_chain(
            task.task_id,
            metadata={"prompt": task.prompt, "workflow_type": task.workflow_type}
        )
        
        # Create a contract for this task
        contract_id = blockchain_service.create_contract(
            agents=[role.agent_id for role in task.roles],
            task_id=task.task_id,
            terms={"prompt": task.prompt, "workflow_type": task.workflow_type}
        )
        
        # Execute the appropriate workflow
        if task.workflow_type == "parallel":
            results = await self._execute_parallel_workflow(task, thought_chain_id)
        elif task.workflow_type == "sequential":
            results = await self._execute_sequential_workflow(task, thought_chain_id)
        elif task.workflow_type == "consensus":
            results = await self._execute_consensus_workflow(task, thought_chain_id)
        else:
            raise ValueError(f"Unknown workflow type: {task.workflow_type}")
        
        # Close the thought chain
        cross_thought_engine.close_thought_chain(
            thought_chain_id,
            summary=json.dumps(results)
        )
        
        # Add blockchain verification
        results["blockchain"] = {
            "contract_id": contract_id,
            "thought_chain_id": thought_chain_id,
            "verification": "Complete"
        }
        
        return results
    
    async def _execute_parallel_workflow(
        self, task: OrchestrationTask, thought_chain_id: str
    ) -> Dict[str, Any]:
        """
        Execute a parallel workflow where all agents work simultaneously.
        
        Args:
            task: The orchestration task
            thought_chain_id: ID of the thought chain
            
        Returns:
            Results from all agents
        """
        # Create tasks for all agents
        tasks = []
        for role in task.roles:
            tasks.append(
                self._call_agent(role, task.prompt, thought_chain_id)
            )
        
        # Execute all tasks in parallel
        agent_results = await asyncio.gather(*tasks)
        
        # Combine results
        results = {
            "task_id": task.task_id,
            "prompt": task.prompt,
            "agent_results": {},
            "combined_output": "# Multi-Agent Analysis\n\n"
        }
        
        for i, role in enumerate(task.roles):
            results["agent_results"][role.role_name] = agent_results[i]
            results["combined_output"] += f"## {role.role_name.capitalize()} Perspective\n{agent_results[i]}\n\n"
        
        return results
    
    async def _execute_sequential_workflow(
        self, task: OrchestrationTask, thought_chain_id: str
    ) -> Dict[str, Any]:
        """
        Execute a sequential workflow where agents work one after another.
        
        Args:
            task: The orchestration task
            thought_chain_id: ID of the thought chain
            
        Returns:
            Results from the sequential process
        """
        results = {
            "task_id": task.task_id,
            "prompt": task.prompt,
            "agent_results": {},
            "iterations": [],
            "final_output": ""
        }
        
        current_prompt = task.prompt
        
        # Execute roles in sequence
        for iteration in range(task.max_iterations):
            iteration_results = {}
            
            for role in task.roles:
                # Call agent with current prompt
                response = await self._call_agent(role, current_prompt, thought_chain_id)
                
                # Store result
                iteration_results[role.role_name] = response
                
                # Update current prompt with this agent's response
                current_prompt = f"""
Previous prompt: {current_prompt}

{role.role_name.capitalize()}'s response:
{response}

Continue building on this work.
"""
            
            # Store iteration results
            results["iterations"].append({
                "iteration": iteration + 1,
                "results": iteration_results
            })
            
            # Store final result of this iteration
            if iteration == task.max_iterations - 1:
                results["final_output"] = current_prompt
                results["agent_results"] = iteration_results
        
        return results
    
    async def _execute_consensus_workflow(
        self, task: OrchestrationTask, thought_chain_id: str
    ) -> Dict[str, Any]:
        """
        Execute a consensus workflow where agents must reach agreement.
        
        Args:
            task: The orchestration task
            thought_chain_id: ID of the thought chain
            
        Returns:
            Results from the consensus process
        """
        results = {
            "task_id": task.task_id,
            "prompt": task.prompt,
            "agent_results": {},
            "iterations": [],
            "consensus_reached": False,
            "final_output": ""
        }
        
        current_prompt = task.prompt
        
        # Execute multiple iterations to reach consensus
        for iteration in range(task.max_iterations):
            iteration_results = {}
            
            # Get all agent responses
            for role in task.roles:
                response = await self._call_agent(role, current_prompt, thought_chain_id)
                iteration_results[role.role_name] = response
            
            # Check for consensus
            consensus_score, consensus_output = await self._evaluate_consensus(
                iteration_results, task.prompt
            )
            
            # Store iteration results
            results["iterations"].append({
                "iteration": iteration + 1,
                "results": iteration_results,
                "consensus_score": consensus_score
            })
            
            # If consensus reached, stop
            if consensus_score >= task.consensus_threshold:
                results["consensus_reached"] = True
                results["final_output"] = consensus_output
                results["agent_results"] = iteration_results
                break
            
            # Otherwise, update prompt and try again
            current_prompt = f"""
Previous prompt: {current_prompt}

All agents have provided their perspectives but haven't reached consensus.
Here are their responses:

{json.dumps(iteration_results, indent=2)}

Please reconsider and try to find common ground.
"""
        
        # If we didn't reach consensus, take the last iteration
        if not results["consensus_reached"]:
            results["final_output"] = "No consensus reached. Final perspectives:\n\n"
            for role_name, response in iteration_results.items():
                results["final_output"] += f"## {role_name.capitalize()}\n{response}\n\n"
            results["agent_results"] = iteration_results
        
        return results
    
    async def _call_agent(
        self, role: AgentRole, prompt: str, thought_chain_id: str
    ) -> str:
        """
        Call an AI agent with a prompt.
        
        Args:
            role: The agent role
            prompt: The prompt to send to the agent
            thought_chain_id: ID of the thought chain
            
        Returns:
            Agent response
        """
        # Format the prompt according to the role's template
        formatted_prompt = role.prompt_template.format(prompt=prompt)
        
        # Get agent details
        try:
            db_agent = None  # We'd normally get this from the database
            
            # Determine which provider to use
            provider = role.provider or (db_agent.provider if db_agent else "openai")
            model_name = role.model_name or (db_agent.model_name if db_agent else "gpt-3.5-turbo")
            
            # Call the appropriate API
            if provider == "openai":
                response = await self._call_openai(formatted_prompt, model_name)
            elif provider == "anthropic":
                response = await self._call_anthropic(formatted_prompt, model_name)
            elif provider == "google":
                response = await self._call_google(formatted_prompt, model_name)
            else:
                raise ValueError(f"Unknown provider: {provider}")
            
            # Add thought to the thought chain
            thought_id = cross_thought_engine.add_thought(
                thought_chain_id,
                role.agent_id,
                response,
                context={"prompt": formatted_prompt, "role": role.role_name}
            )
            
            return response
        except Exception as e:
            # In case of error, return error message
            error_msg = f"Error calling agent: {str(e)}"
            cross_thought_engine.add_thought(
                thought_chain_id,
                role.agent_id,
                error_msg,
                context={"prompt": formatted_prompt, "role": role.role_name, "error": True}
            )
            return error_msg
    
    async def _call_openai(self, prompt: str, model: str = "gpt-3.5-turbo") -> str:
        """Call OpenAI API."""
        try:
            response = await self.session.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": model,
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 1000,
                    "temperature": 0.7
                }
            )
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]
        except Exception as e:
            return f"Error calling OpenAI: {str(e)}"
    
    async def _call_anthropic(self, prompt: str, model: str = "claude-3-haiku-20240307") -> str:
        """Call Anthropic API."""
        try:
            response = await self.session.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": settings.ANTHROPIC_API_KEY,
                    "anthropic-version": "2023-06-01",
                    "Content-Type": "application/json"
                },
                json={
                    "model": model,
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 1000
                }
            )
            response.raise_for_status()
            data = response.json()
            return data["content"][0]["text"]
        except Exception as e:
            return f"Error calling Anthropic: {str(e)}"
    
    async def _call_google(self, prompt: str, model: str = "gemini-pro") -> str:
        """Call Google API."""
        try:
            response = await self.session.post(
                f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
                params={"key": settings.GOOGLE_API_KEY},
                json={
                    "contents": [{"parts": [{"text": prompt}]}],
                    "generationConfig": {
                        "temperature": 0.7,
                        "maxOutputTokens": 1000,
                    }
                }
            )
            response.raise_for_status()
            data = response.json()
            return data["candidates"][0]["content"]["parts"][0]["text"]
        except Exception as e:
            return f"Error calling Google: {str(e)}"
    
    async def _evaluate_consensus(
        self, agent_results: Dict[str, str], original_prompt: str
    ) -> Tuple[float, str]:
        """
        Evaluate consensus among agent results.
        
        Args:
            agent_results: Results from different agents
            original_prompt: The original prompt
            
        Returns:
            Tuple of (consensus score, consensus output)
        """
        # Format a prompt to evaluate consensus
        consensus_prompt = f"""
The following agents have provided responses to this prompt:

Original prompt: {original_prompt}

Agent responses:
{json.dumps(agent_results, indent=2)}

Your task is to:
1. Evaluate how much consensus exists between the agents (0.0 to 1.0)
2. Provide a synthesized response that represents their collective wisdom

Format your response as a JSON object with these fields:
- consensus_score: A number between 0.0 and 1.0
- consensus_output: The synthesized response

JSON RESPONSE:
"""
        
        try:
            # Call OpenAI to evaluate consensus
            response = await self._call_openai(consensus_prompt, "gpt-4")
            
            # Parse JSON response
            response_data = json.loads(response)
            consensus_score = float(response_data.get("consensus_score", 0.0))
            consensus_output = response_data.get("consensus_output", "No consensus output provided")
            
            return consensus_score, consensus_output
        except Exception as e:
            # In case of error, return low consensus
            return 0.0, f"Error evaluating consensus: {str(e)}"


# Create singleton instance
ai_orchestrator = AIOrchestrator()
