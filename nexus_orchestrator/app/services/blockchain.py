"""
Blockchain service for decision tracking and smart contract interaction.
"""
import json
import hashlib
import time
import os
from typing import Dict, Any, Optional, List
from web3 import Web3
from eth_account import Account
from eth_account.signers.local import LocalAccount

from app.core.config import settings

class BlockchainService:
    """Service for blockchain interactions."""
    
    def __init__(self):
        """Initialize blockchain service."""
        self.simulation_mode = True
        self.storage_dir = os.path.join(os.getcwd(), "blockchain_sim")
        os.makedirs(self.storage_dir, exist_ok=True)
        
        # Try to connect to Web3 provider if configured
        if settings.WEB3_PROVIDER_URI:
            try:
                self.w3 = Web3(Web3.HTTPProvider(settings.WEB3_PROVIDER_URI))
                if self.w3.is_connected():
                    self.simulation_mode = False
            except Exception as e:
                print(f"Failed to connect to Web3 provider: {e}")
                print("Falling back to simulation mode")
    
    def log_decision(self, task_id: str, data: Dict[str, Any]) -> str:
        """
        Log a decision to blockchain or simulation.
        
        Args:
            task_id: The ID of the task
            data: The data to log
            
        Returns:
            Transaction hash
        """
        if self.simulation_mode:
            return self._simulate_log_decision(task_id, data)
        else:
            return self._blockchain_log_decision(task_id, data)
    
    def _simulate_log_decision(self, task_id: str, data: Dict[str, Any]) -> str:
        """Simulate logging a decision to blockchain."""
        # Convert data to JSON
        data_json = json.dumps(data, default=str)
        
        # Create a hash
        data_hash = hashlib.sha256(data_json.encode()).hexdigest()
        
        # Create record with metadata
        record = {
            "task_id": task_id,
            "timestamp": time.time(),
            "data_hash": data_hash,
            "data": data,
            "tx_hash": f"sim_{data_hash[:16]}"  # Simulated transaction hash
        }
        
        # Save to file
        filename = os.path.join(self.storage_dir, f"{task_id}.json")
        with open(filename, 'w') as f:
            json.dump(record, f, default=str, indent=2)
            
        return record["tx_hash"]
    
    def _blockchain_log_decision(self, task_id: str, data: Dict[str, Any]) -> str:
        """Log a decision to actual blockchain."""
        # This would be implemented with actual blockchain contract calls
        # For now, we'll just simulate
        return self._simulate_log_decision(task_id, data)
    
    def verify_record(self, task_id: str, data: Dict[str, Any]) -> bool:
        """
        Verify a record against blockchain or simulation.
        
        Args:
            task_id: The ID of the task
            data: The data to verify
            
        Returns:
            Whether the record is valid
        """
        if self.simulation_mode:
            return self._simulate_verify_record(task_id, data)
        else:
            return self._blockchain_verify_record(task_id, data)
    
    def _simulate_verify_record(self, task_id: str, data: Dict[str, Any]) -> bool:
        """Simulate verification of blockchain record."""
        filename = os.path.join(self.storage_dir, f"{task_id}.json")
        
        if not os.path.exists(filename):
            return False
            
        # Load stored record
        with open(filename, 'r') as f:
            record = json.load(f)
            
        # Convert current data to JSON and hash
        data_json = json.dumps(data, default=str)
        current_hash = hashlib.sha256(data_json.encode()).hexdigest()
        
        # Compare with stored hash
        return record["data_hash"] == current_hash
    
    def _blockchain_verify_record(self, task_id: str, data: Dict[str, Any]) -> bool:
        """Verify a record against actual blockchain."""
        # This would be implemented with actual blockchain contract calls
        # For now, we'll just simulate
        return self._simulate_verify_record(task_id, data)
    
    def create_contract(self, agents: List[int], task_id: str, terms: Dict[str, Any]) -> str:
        """
        Create a smart contract between agents.
        
        Args:
            agents: List of agent IDs participating in the contract
            task_id: The ID of the task the contract is for
            terms: The terms of the contract
            
        Returns:
            Contract ID
        """
        contract_data = {
            "agents": agents,
            "task_id": task_id,
            "terms": terms,
            "status": "active",
            "created_at": time.time()
        }
        
        # In simulation mode, just log the contract
        contract_id = f"contract_{hashlib.sha256(json.dumps(contract_data, default=str).encode()).hexdigest()[:16]}"
        contract_data["contract_id"] = contract_id
        
        # Log contract creation
        self.log_decision(f"contract_{contract_id}", contract_data)
        
        return contract_id

# Create singleton instance
blockchain_service = BlockchainService()
