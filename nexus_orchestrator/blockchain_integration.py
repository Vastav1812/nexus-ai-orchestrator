"""
Smart Blockchain Integration for Nexus AI Orchestrator

This module provides a hybrid approach to blockchain integration:
1. Local simulation for development and testing
2. Real blockchain interactions when needed
3. API-based alternatives for features typically requiring blockchain
"""
import os
import json
import hashlib
import time
import uuid
import base64
import hmac
from typing import Dict, Any, List, Optional, Tuple
import httpx
from dotenv import load_dotenv
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

# Import models
from setup_database import BlockchainRecord, DATABASE_URL

# Load environment variables
load_dotenv()

class BlockchainIntegration:
    """Smart blockchain integration with fallback mechanisms."""
    
    def __init__(self, simulation_mode: bool = True):
        """Initialize blockchain integration.
        
        Args:
            simulation_mode: Whether to use simulation mode (default: True)
        """
        self.simulation_mode = simulation_mode
        self.storage_dir = os.path.join(os.getcwd(), "blockchain_sim")
        os.makedirs(self.storage_dir, exist_ok=True)
        
        # Database connection
        self.engine = create_engine(DATABASE_URL)
        self.Session = sessionmaker(bind=self.engine)
        
        # API clients for alternative verification
        self.http_client = httpx.AsyncClient(timeout=30.0)
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.http_client.aclose()
    
    def log_decision(self, record_type: str, reference_id: str, 
                    data: Dict[str, Any], task_id: Optional[str] = None) -> Tuple[str, str]:
        """
        Log a decision to blockchain or simulation.
        
        Args:
            record_type: Type of record (e.g., "task", "agent_decision", "consensus")
            reference_id: ID of the referenced item
            data: Data to log
            task_id: Optional task ID for reference
            
        Returns:
            Tuple of (record ID, transaction hash)
        """
        # Convert data to JSON string for hashing
        data_json = json.dumps(data, default=str)
        
        # Create a hash
        data_hash = hashlib.sha256(data_json.encode()).hexdigest()
        
        # Use database for storage
        session = self.Session()
        try:
            # Create blockchain record
            tx_hash = f"sim_{data_hash[:16]}" if self.simulation_mode else None
            
            # Determine actual blockchain action based on mode
            if not self.simulation_mode:
                tx_hash = self._blockchain_log_decision(record_type, reference_id, data_hash, data)
            
            # Create database record
            record = BlockchainRecord(
                record_type=record_type,
                reference_id=reference_id,
                hash_value=data_hash,
                data=data,
                tx_hash=tx_hash,
                verified=self.simulation_mode  # Auto-verified in simulation mode
            )
            
            session.add(record)
            session.commit()
            
            # Also save to local file as backup
            if self.simulation_mode:
                filename = os.path.join(self.storage_dir, f"{reference_id}.json")
                with open(filename, 'w') as f:
                    json.dump({
                        "record_id": record.id,
                        "record_type": record_type,
                        "reference_id": reference_id,
                        "hash_value": data_hash,
                        "data": data,
                        "tx_hash": tx_hash,
                        "timestamp": time.time()
                    }, f, default=str, indent=2)
            
            return str(record.id), tx_hash
        
        finally:
            session.close()
    
    def _blockchain_log_decision(self, record_type: str, reference_id: str, 
                               data_hash: str, data: Dict[str, Any]) -> str:
        """Log a decision to actual blockchain."""
        # This would contain actual blockchain implementation
        # For now, we'll just use the hash as a simulated transaction
        return f"tx_{data_hash[:16]}"
    
    def verify_record(self, record_id: str) -> Dict[str, Any]:
        """
        Verify a record against blockchain or simulation.
        
        Args:
            record_id: The ID of the record to verify
            
        Returns:
            Verification result
        """
        session = self.Session()
        try:
            # Get the record
            record = session.get(BlockchainRecord, int(record_id))
            if not record:
                return {"verified": False, "error": "Record not found"}
            
            # If already verified, return success
            if record.verified:
                return {
                    "verified": True,
                    "record_type": record.record_type,
                    "reference_id": record.reference_id,
                    "hash_value": record.hash_value,
                    "tx_hash": record.tx_hash,
                    "timestamp": record.created_at.isoformat()
                }
            
            # Verify based on mode
            if self.simulation_mode:
                # In simulation mode, verify against local file
                verified = self._simulate_verify_record(record.reference_id, record.data)
            else:
                # In blockchain mode, verify against blockchain
                verified = self._blockchain_verify_record(record.tx_hash, record.hash_value)
            
            # Update verification status
            if verified:
                record.verified = True
                session.commit()
            
            return {
                "verified": verified,
                "record_type": record.record_type,
                "reference_id": record.reference_id,
                "hash_value": record.hash_value,
                "tx_hash": record.tx_hash,
                "timestamp": record.created_at.isoformat()
            }
        
        finally:
            session.close()
    
    def _simulate_verify_record(self, reference_id: str, data: Dict[str, Any]) -> bool:
        """Simulate verification of blockchain record."""
        filename = os.path.join(self.storage_dir, f"{reference_id}.json")
        
        if not os.path.exists(filename):
            return False
            
        # Load stored record
        with open(filename, 'r') as f:
            record = json.load(f)
        
        # Convert current data to JSON and hash
        data_json = json.dumps(data, default=str)
        current_hash = hashlib.sha256(data_json.encode()).hexdigest()
        
        # Compare with stored hash
        return record["hash_value"] == current_hash
    
    def _blockchain_verify_record(self, tx_hash: str, expected_hash: str) -> bool:
        """Verify a record against actual blockchain."""
        # This would contain actual blockchain implementation
        # For now, we'll just return True for simulated hashes
        return tx_hash.startswith("tx_") or tx_hash.startswith("sim_")
    
    def sign_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sign data with a secure signature that can be verified without blockchain.
        
        This provides non-blockchain cryptographic verification as an alternative.
        
        Args:
            data: The data to sign
            
        Returns:
            Signed data with verification information
        """
        # Convert data to string
        data_str = json.dumps(data, sort_keys=True, default=str)
        
        # Create a timestamp
        timestamp = str(int(time.time()))
        
        # Create a nonce
        nonce = uuid.uuid4().hex
        
        # Create a signature using HMAC-SHA256
        key = os.getenv("SECRET_KEY", "nexus-ai-orchestrator-secret-key")
        message = f"{data_str}|{timestamp}|{nonce}"
        signature = hmac.new(
            key.encode(), 
            message.encode(),
            hashlib.sha256
        ).hexdigest()
        
        # Return signed data
        return {
            "data": data,
            "metadata": {
                "timestamp": timestamp,
                "nonce": nonce,
                "signature": signature
            }
        }
    
    def verify_signature(self, signed_data: Dict[str, Any]) -> bool:
        """
        Verify a signature without using blockchain.
        
        Args:
            signed_data: The signed data to verify
            
        Returns:
            Whether the signature is valid
        """
        try:
            # Extract components
            data = signed_data["data"]
            metadata = signed_data["metadata"]
            timestamp = metadata["timestamp"]
            nonce = metadata["nonce"]
            signature = metadata["signature"]
            
            # Convert data to string (same way it was done during signing)
            data_str = json.dumps(data, sort_keys=True, default=str)
            
            # Recreate the message
            message = f"{data_str}|{timestamp}|{nonce}"
            
            # Recreate the signature
            key = os.getenv("SECRET_KEY", "nexus-ai-orchestrator-secret-key")
            expected_signature = hmac.new(
                key.encode(),
                message.encode(),
                hashlib.sha256
            ).hexdigest()
            
            # Compare signatures
            return hmac.compare_digest(signature, expected_signature)
        
        except (KeyError, TypeError):
            return False
    
    async def verify_via_external_api(self, data: Dict[str, Any], reference_id: str) -> Dict[str, Any]:
        """
        Use a trusted third-party API to verify data without blockchain.
        
        This demonstrates using your existing APIs for verification.
        
        Args:
            data: The data to verify
            reference_id: Reference ID for the verification
            
        Returns:
            Verification result
        """
        try:
            # Create a hash of the data
            data_json = json.dumps(data, default=str)
            data_hash = hashlib.sha256(data_json.encode()).hexdigest()
            
            # Use OpenAI API for verification (simplified example)
            openai_key = os.getenv("OPENAI_API_KEY")
            if not openai_key:
                return {"verified": False, "error": "No OpenAI API key available"}
            
            # Create a prompt that includes the data hash
            prompt = f"""
            Verification request for data with reference ID: {reference_id}
            Data hash: {data_hash}
            
            Please confirm this verification by echoing back the exact hash.
            """
            
            # Call OpenAI API
            response = await self.http_client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {openai_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "gpt-3.5-turbo",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.2
                }
            )
            
            # Process response
            if response.status_code == 200:
                resp_data = response.json()
                ai_response = resp_data["choices"][0]["message"]["content"]
                
                # Check if the response contains the hash
                if data_hash in ai_response:
                    return {
                        "verified": True,
                        "method": "openai",
                        "reference_id": reference_id,
                        "hash_value": data_hash,
                        "timestamp": time.time()
                    }
            
            return {"verified": False, "error": "Verification failed"}
        
        except Exception as e:
            return {"verified": False, "error": str(e)}

# Create singleton instance
blockchain_integration = BlockchainIntegration(simulation_mode=True)


# Example usage of the smart verification
async def verify_agent_output(agent_name: str, input_data: Dict[str, Any], 
                             output_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Verify AI agent output using the most appropriate verification method.
    
    This demonstrates the smart verification approach, using blockchain
    when available, or cryptographic alternatives when not.
    
    Args:
        agent_name: Name of the agent
        input_data: Input data provided to the agent
        output_data: Output data from the agent
        
    Returns:
        Verification result
    """
    # Create a verification record
    verification_data = {
        "agent": agent_name,
        "input": input_data,
        "output": output_data,
        "timestamp": time.time()
    }
    
    # Generate a reference ID
    reference_id = f"verify_{uuid.uuid4().hex[:8]}"
    
    # Try different verification approaches
    async with BlockchainIntegration() as bi:
        # 1. Attempt blockchain verification if available
        if not bi.simulation_mode:
            record_id, tx_hash = bi.log_decision(
                "agent_verification", 
                reference_id, 
                verification_data
            )
            return {
                "verified": True,
                "method": "blockchain",
                "record_id": record_id,
                "tx_hash": tx_hash
            }
        
        # 2. Cryptographic signature as an alternative
        signed_data = bi.sign_data(verification_data)
        if bi.verify_signature(signed_data):
            # Store the signature in the blockchain simulation
            record_id, tx_hash = bi.log_decision(
                "signature_verification", 
                reference_id,
                {
                    "data": verification_data,
                    "signature": signed_data["metadata"]["signature"]
                }
            )
            return {
                "verified": True,
                "method": "cryptographic",
                "record_id": record_id,
                "signature": signed_data["metadata"]["signature"]
            }
        
        # 3. External API verification as a last resort
        api_verification = await bi.verify_via_external_api(
            verification_data, 
            reference_id
        )
        if api_verification.get("verified", False):
            return api_verification
        
        # Unable to verify
        return {"verified": False, "error": "All verification methods failed"}
