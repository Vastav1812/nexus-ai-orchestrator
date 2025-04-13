# Nexus AI Orchestrator

A multi-agent AI orchestration system that combines specialized AI models through a coordinated workflow.

## Project Overview

Nexus AI Orchestrator is designed to integrate multiple AI services (like Claude, GPT, etc.) and coordinate them effectively using their APIs. The system enables specialized AI models to work together to accomplish complex tasks through a sophisticated orchestration layer.

## Tech Stack

- **Backend**: FastAPI (Python)
- **Orchestration**: CrewAI and LangChain
- **Database**:
  - Vector DB: Qdrant
  - Traditional: PostgreSQL
- **Message Queue**: Redis
- **AI Integration**: OpenAI, Anthropic, Cohere APIs
- **Authentication**: JWT-based with secure key management
- **Blockchain** (optional): Ethereum/Web3 for decision trails
- **Frontend** (admin dashboard): React with TypeScript

## Project Structure

```
nexus_orchestrator/
│
├── app/                          # Main application package
│   ├── api/                      # API endpoints
│   ├── core/                     # Core functionality
│   ├── db/                       # Database models and connections
│   ├── models/                   # Pydantic models
│   ├── schemas/                  # Schema definitions
│   ├── services/                 # External service integrations
│   ├── orchestration/            # AI orchestration logic
│   │   ├── agents/               # Individual AI agent definitions
│   │   ├── crews/                # Agent groups and teams
│   │   ├── tasks/                # Task definitions
│   │   └── workflows/            # Workflow definitions
│   ├── utils/                    # Utility functions
│   └── config/                   # Configuration files
│
├── tests/                        # Test directory
├── docs/                         # Documentation
├── .env.example                  # Example environment variables
├── requirements.txt              # Python dependencies
├── Dockerfile                    # Docker configuration
├── docker-compose.yml            # Docker Compose configuration
└── README.md                     # Project documentation
```

## Getting Started

### Prerequisites

- Python 3.10+
- PostgreSQL
- Redis
- API keys for OpenAI, Anthropic, etc.

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/nexus-orchestrator.git
   cd nexus-orchestrator
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file based on `.env.example` and add your API keys.

5. Start the application:
   ```bash
   uvicorn app.main:app --reload
   ```

## Docker Deployment

```bash
docker-compose up -d
```

## License

[MIT License](LICENSE)
