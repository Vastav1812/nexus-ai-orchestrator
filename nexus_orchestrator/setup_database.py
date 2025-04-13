"""
Database setup script for Nexus AI Orchestrator.
"""
import os
import sys
import sqlalchemy as sa
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database connection parameters from .env
DB_USER = os.getenv("POSTGRES_USER")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD")
DB_SERVER = os.getenv("POSTGRES_SERVER")
DB_NAME = os.getenv("POSTGRES_DB")

# Create SQLAlchemy connection URL
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_SERVER}/{DB_NAME}"

# Define models
Base = declarative_base()

class Agent(Base):
    """Database model for AI agents."""
    __tablename__ = "agents"
    
    id = sa.Column(sa.Integer, primary_key=True, index=True)
    name = sa.Column(sa.String, index=True)
    description = sa.Column(sa.String)
    model_name = sa.Column(sa.String)
    provider = sa.Column(sa.String)
    api_key_env = sa.Column(sa.String)
    goal = sa.Column(sa.String)
    role = sa.Column(sa.String)
    backstory = sa.Column(sa.String, nullable=True)
    created_at = sa.Column(sa.DateTime, server_default=sa.func.now())
    updated_at = sa.Column(sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now())
    
class Task(Base):
    """Database model for tasks."""
    __tablename__ = "tasks"
    
    id = sa.Column(sa.Integer, primary_key=True, index=True)
    title = sa.Column(sa.String, index=True)
    description = sa.Column(sa.String)
    prompt = sa.Column(sa.String)
    agent_id = sa.Column(sa.Integer, sa.ForeignKey("agents.id"))
    status = sa.Column(sa.String, default="pending")
    created_at = sa.Column(sa.DateTime, server_default=sa.func.now())
    completed_at = sa.Column(sa.DateTime, nullable=True)
    
class BlockchainRecord(Base):
    """Database model for blockchain records."""
    __tablename__ = "blockchain_records"
    
    id = sa.Column(sa.Integer, primary_key=True, index=True)
    record_type = sa.Column(sa.String, index=True)  # "task", "agent_decision", "consensus"
    reference_id = sa.Column(sa.String)  # ID of the referenced item
    hash_value = sa.Column(sa.String, index=True)
    data = sa.Column(sa.JSON)
    tx_hash = sa.Column(sa.String, nullable=True)  # Actual blockchain tx hash
    verified = sa.Column(sa.Boolean, default=False)
    created_at = sa.Column(sa.DateTime, server_default=sa.func.now())

class Thought(Base):
    """Database model for agent thoughts."""
    __tablename__ = "thoughts"
    
    id = sa.Column(sa.Integer, primary_key=True, index=True)
    agent_id = sa.Column(sa.Integer, sa.ForeignKey("agents.id"))
    task_id = sa.Column(sa.Integer, sa.ForeignKey("tasks.id"))
    content = sa.Column(sa.String)
    references = sa.Column(sa.JSON, default=[])  # IDs of thoughts this references
    created_at = sa.Column(sa.DateTime, server_default=sa.func.now())
    blockchain_record_id = sa.Column(sa.Integer, sa.ForeignKey("blockchain_records.id"), nullable=True)

def create_database():
    """Create database tables if they don't exist."""
    try:
        # Create an engine
        engine = sa.create_engine(DATABASE_URL)
        
        # Create tables
        Base.metadata.create_all(engine)
        
        # Add default agents based on available APIs
        Session = sessionmaker(bind=engine)
        session = Session()
        
        # Check if agents table is empty
        agent_count = session.query(Agent).count()
        if agent_count == 0:
            # Create default agents
            default_agents = [
                Agent(
                    name="OpenAI Developer",
                    description="AI developer using OpenAI's GPT models",
                    model_name="gpt-3.5-turbo",
                    provider="openai",
                    api_key_env="OPENAI_API_KEY",
                    goal="Provide code solutions and technical analysis",
                    role="developer",
                    backstory="As a skilled AI developer, I analyze requirements and produce efficient code solutions."
                ),
                Agent(
                    name="Google UI Designer",
                    description="UI/UX designer using Google's Gemini models",
                    model_name="gemini-pro",
                    provider="google",
                    api_key_env="GOOGLE_API_KEY",
                    goal="Create beautiful and functional UI designs",
                    role="ui_designer",
                    backstory="I specialize in creating user-friendly interfaces with modern design principles."
                ),
                Agent(
                    name="Hugging Face Researcher",
                    description="Research specialist using Hugging Face models",
                    model_name="mistralai/Mixtral-8x7B-Instruct-v0.1",
                    provider="huggingface",
                    api_key_env="HUGGINGFACE_API_KEY",
                    goal="Perform research and provide analytical insights",
                    role="researcher",
                    backstory="I'm dedicated to finding and synthesizing information from various sources."
                ),
                Agent(
                    name="DeepSeek Strategist",
                    description="Strategic planner using DeepSeek models",
                    model_name="deepseek-coder",
                    provider="deepseek",
                    api_key_env="DEEPSEEK_API_KEY",
                    goal="Create strategic plans and roadmaps",
                    role="strategist",
                    backstory="I help organizations plan their technical roadmaps and strategic initiatives."
                )
            ]
            
            session.add_all(default_agents)
            session.commit()
            print("Created default agents.")
        
        print("Database setup completed successfully.")
        
    except Exception as e:
        print(f"Error setting up database: {e}")
        sys.exit(1)
    finally:
        if 'session' in locals():
            session.close()

if __name__ == "__main__":
    create_database()
