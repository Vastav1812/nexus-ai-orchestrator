"""
Simple AI Orchestrator - A lightweight prototype for AI agent orchestration.
"""
import os
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import httpx
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI(title="AI Orchestrator Prototype")

class OrchestrationRequest(BaseModel):
    prompt: str
    roles: List[str] = ["developer", "ui_designer", "project_manager"]

@app.post("/orchestrate")
async def orchestrate(request: OrchestrationRequest):
    results = {}
    
    # Use blockchain tracking for verification if available
    try:
        from setup_database import BlockchainRecord
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        import hashlib
        import json
        
        # Create a unique hash for this request
        request_hash = hashlib.sha256(request.prompt.encode()).hexdigest()[:10]
        blockchain_enabled = True
    except ImportError:
        blockchain_enabled = False
    
    # Define role-specific prompts
    for role in request.roles:
        if role == "developer":
            # Use local mock developer
            results[role] = await call_mock_developer(request.prompt)
        elif role == "ui_designer":
            # Use local mock UI designer
            results[role] = await call_mock_ui_designer(request.prompt)
        elif role == "project_manager":
            # Use local mock project manager
            results[role] = await call_mock_project_manager(request.prompt)
    
    # Record to blockchain simulation if enabled
    blockchain_info = ""
    if blockchain_enabled:
        try:
            # Connect to database
            db_user = os.getenv("POSTGRES_USER")
            db_password = os.getenv("POSTGRES_PASSWORD")
            db_server = os.getenv("POSTGRES_SERVER")
            db_name = os.getenv("POSTGRES_DB")
            database_url = f"postgresql://{db_user}:{db_password}@{db_server}/{db_name}"
            
            engine = create_engine(database_url)
            Session = sessionmaker(bind=engine)
            session = Session()
            
            # Import time module for timestamp
            import time
            
            # Create blockchain record
            data = {
                "prompt": request.prompt,
                "roles": request.roles,
                "results": {k: v[:100] + "..." for k, v in results.items()},  # Truncate for storage
                "timestamp": str(time.time())
            }
            
            # Create hash
            data_json = json.dumps(data, sort_keys=True)
            data_hash = hashlib.sha256(data_json.encode()).hexdigest()
            
            # Store in database
            record = BlockchainRecord(
                record_type="orchestration",
                reference_id=f"request_{request_hash}",
                hash_value=data_hash,
                data=data,
                tx_hash=f"local_{data_hash[:8]}",
                verified=True
            )
            
            session.add(record)
            session.commit()
            
            blockchain_info = f"\n\n## Verification\nThis analysis is blockchain-verified with ID: {record.id}\nVerification hash: {data_hash[:15]}..."
            
            session.close()
        except Exception as e:
            blockchain_info = f"\n\nNote: Blockchain verification attempted but encountered an error: {str(e)}"
    
    # Simple integration of results
    final_output = "# Multi-Agent Analysis\n\n"
    for role, output in results.items():
        final_output += f"## {role.capitalize()} Perspective\n{output}\n\n"
    
    # Add blockchain info if available
    final_output += blockchain_info
    
    return {"result": final_output}

# Mock AI Agents for local development
async def call_mock_developer(prompt: str) -> str:
    """Generate developer responses without external API calls."""
    topic = prompt.lower()
    
    # Simple template responses based on content
    if "website" in topic or "web" in topic:
        return (
            "Based on the requirements, I recommend creating a responsive website with:"
            "\n\n1. **Frontend**: React.js with TypeScript for type safety"
            "\n2. **State Management**: Redux or Context API depending on complexity"
            "\n3. **Styling**: Tailwind CSS for rapid development"
            "\n4. **Backend**: Node.js with Express or FastAPI with Python"
            "\n5. **Database**: PostgreSQL for structured data"
            "\n6. **Authentication**: JWT-based auth flow"
            "\n\nInitial development roadmap:\n"
            "1. Set up project structure and CI/CD pipeline\n"
            "2. Implement core features with proper testing\n"
            "3. Integrate APIs and optimize performance\n"
            "4. Deploy to production with monitoring"
        )
    elif "mobile" in topic or "app" in topic:
        return (
            "For this mobile application, I recommend the following architecture:\n\n"
            "1. **Cross-platform Framework**: React Native or Flutter for code sharing\n"
            "2. **State Management**: Redux/MobX (React Native) or Provider/Bloc (Flutter)\n"
            "3. **API Integration**: RESTful or GraphQL depending on data needs\n"
            "4. **Local Storage**: Secure storage with encryption for sensitive data\n"
            "5. **Authentication**: OAuth2 with refresh token pattern\n\n"
            "Implementation strategy:\n"
            "- Start with core navigation and authentication\n"
            "- Implement feature modules incrementally\n"
            "- Add offline capability with local caching\n"
            "- Optimize performance and battery usage"
        )
    elif "ai" in topic or "machine learning" in topic or "ml" in topic:
        return (
            "For this AI/ML system, I recommend:\n\n"
            "1. **Framework**: TensorFlow or PyTorch depending on the specific use case\n"
            "2. **Deployment**: Docker containers with Kubernetes for scaling\n"
            "3. **Data Pipeline**: Apache Airflow for orchestration\n"
            "4. **Infrastructure**: Cloud-based GPUs for training\n"
            "5. **API Layer**: FastAPI for serving predictions\n\n"
            "Development approach:\n"
            "- Start with data preprocessing and feature engineering\n"
            "- Build MVP model to establish baseline\n"
            "- Improve through iterative experimentation\n"
            "- Set up monitoring for model performance and drift"
        )
    else:
        return (
            f"For the {topic} project, I recommend a modular architecture with:\n\n"
            "1. **Domain-Driven Design**: Separating business logic from infrastructure\n"
            "2. **Clean Architecture**: Core domain independent of frameworks\n"
            "3. **Testing Strategy**: Unit, integration, and end-to-end tests\n"
            "4. **Documentation**: Automated API docs and system diagrams\n\n"
            "Technical stack considerations:\n"
            "- Programming language based on team expertise and performance requirements\n"
            "- Database selection based on data structure and query patterns\n"
            "- Deployment strategy using containerization for consistency"
        )

async def call_mock_ui_designer(prompt: str) -> str:
    """Generate UI/UX design responses without external API calls."""
    topic = prompt.lower()
    
    if "website" in topic or "web" in topic:
        return (
            "For this website design, I recommend:\n\n"
            "1. **Design System**: Create a consistent component library with:\n"
            "   - Typography: Primary font (headers): Poppins, Secondary font (body): Inter\n"
            "   - Color Palette: Primary: #3B82F6, Secondary: #10B981, Neutrals: #1F2937, #6B7280, #F3F4F6\n"
            "   - Spacing system based on 4px increments\n\n"
            "2. **Layout**: Responsive grid system with:\n"
            "   - Mobile-first approach, adapting to tablet and desktop\n"
            "   - Max content width of 1200px with appropriate padding\n\n"
            "3. **Navigation**: \n"
            "   - Mobile: Bottom navigation or hamburger menu\n"
            "   - Desktop: Horizontal navigation with clear hierarchy\n\n"
            "4. **Key UI Components**:\n"
            "   - Hero section with clear CTA\n"
            "   - Feature cards with visual icons\n"
            "   - Testimonial carousel\n"
            "   - Pricing comparison table\n"
            "   - Contact form with inline validation"
        )
    elif "mobile" in topic or "app" in topic:
        return (
            "For this mobile app design, I recommend:\n\n"
            "1. **Visual Language**:\n"
            "   - Clean interface with plenty of whitespace\n"
            "   - Consistent iconography (outline or filled style)\n"
            "   - Subtle shadows for depth (8px blur, 2px y-offset, 5% opacity)\n\n"
            "2. **Navigation Pattern**:\n"
            "   - Tab bar for main sections (5 items maximum)\n"
            "   - Gesture-based interactions for common tasks\n"
            "   - Floating action button for primary actions\n\n"
            "3. **UI Components**:\n"
            "   - Card-based content containers\n"
            "   - Pull-to-refresh for content updates\n"
            "   - Skeleton screens for loading states\n"
            "   - Bottom sheets for additional options\n\n"
            "4. **Accessibility**:\n"
            "   - High contrast text (minimum 4.5:1 ratio)\n"
            "   - Touch targets minimum 44×44 points\n"
            "   - Support for dynamic text sizing"
        )
    elif "dashboard" in topic or "admin" in topic:
        return (
            "For this dashboard design, I recommend:\n\n"
            "1. **Information Architecture**:\n"
            "   - Left sidebar for main navigation\n"
            "   - Top header for account, notifications, and global actions\n"
            "   - Content area with card-based widgets\n\n"
            "2. **Data Visualization**:\n"
            "   - Overview KPI cards with comparison to previous period\n"
            "   - Line charts for time-series data\n"
            "   - Bar/column charts for comparisons\n"
            "   - Tables with sorting and filtering\n\n"
            "3. **Interaction Design**:\n"
            "   - Drag-and-drop for customization\n"
            "   - Filters that persist across sessions\n"
            "   - Context menus for quick actions\n\n"
            "4. **Responsive Behavior**:\n"
            "   - Collapsible sidebar on smaller screens\n"
            "   - Stacked layouts for mobile devices\n"
            "   - Prioritized content for different viewport sizes"
        )
    else:
        return (
            f"For the {topic} interface, I propose the following design approach:\n\n"
            "1. **User Research**:\n"
            "   - Conduct interviews with primary user segments\n"
            "   - Create personas and user journey maps\n"
            "   - Define key user tasks and goals\n\n"
            "2. **Interface Design**:\n"
            "   - Clean, minimal aesthetic with focused content\n"
            "   - Strategic use of color to guide attention\n"
            "   - Typography hierarchy for clear information scanning\n\n"
            "3. **Interaction Patterns**:\n"
            "   - Intuitive, common patterns that require minimal learning\n"
            "   - Microinteractions for feedback and delight\n"
            "   - Progressive disclosure to manage complexity\n\n"
            "4. **Testing Recommendations**:\n"
            "   - Usability testing with 5-7 participants per round\n"
            "   - A/B testing for key conversion elements\n"
            "   - Accessibility audit using WCAG 2.1 AA guidelines"
        )

async def call_mock_project_manager(prompt: str) -> str:
    """Generate project management responses without external API calls."""
    topic = prompt.lower()
    
    if "website" in topic or "web" in topic:
        return (
            "Project plan for website development:\n\n"
            "**Phase 1: Discovery & Planning (2 weeks)**\n"
            "- Stakeholder interviews and requirements gathering\n"
            "- Technical specification document\n"
            "- Information architecture and sitemap\n"
            "- Project timeline and resource allocation\n\n"
            "**Phase 2: Design (3 weeks)**\n"
            "- Wireframes and user flows\n"
            "- Visual design concepts\n"
            "- Design system development\n"
            "- Prototype for usability testing\n\n"
            "**Phase 3: Development (6-8 weeks)**\n"
            "- Frontend development (component-based approach)\n"
            "- Backend API development\n"
            "- Content integration\n"
            "- Cross-browser testing\n\n"
            "**Phase 4: Launch & Iteration (3 weeks)**\n"
            "- QA and bug fixes\n"
            "- Performance optimization\n"
            "- Deployment strategy\n"
            "- Analytics implementation\n"
            "- Post-launch support\n\n"
            "**Key Milestones:**\n"
            "1. Design approval: End of week 5\n"
            "2. Development complete: End of week 13\n"
            "3. Website launch: End of week 16\n\n"
            "**Team Required:**\n"
            "- Project Manager (full-time)\n"
            "- UX/UI Designer (full-time during design phase)\n"
            "- Frontend Developer (2, full-time)\n"
            "- Backend Developer (1, full-time)\n"
            "- QA Engineer (part-time)"
        )
    elif "mobile" in topic or "app" in topic:
        return (
            "Project plan for mobile app development:\n\n"
            "**Phase 1: Strategy & Planning (3 weeks)**\n"
            "- Market research and competitive analysis\n"
            "- User personas and journey mapping\n"
            "- Feature prioritization (MoSCoW method)\n"
            "- Technical architecture planning\n\n"
            "**Phase 2: Design & Prototyping (4 weeks)**\n"
            "- Wireframing key user flows\n"
            "- UI design for multiple device sizes\n"
            "- Interactive prototype development\n"
            "- Usability testing and design iteration\n\n"
            "**Phase 3: Development (10-12 weeks)**\n"
            "- Core functionality development\n"
            "- API integration\n"
            "- Authentication and user management\n"
            "- Offline functionality\n"
            "- Analytics integration\n\n"
            "**Phase 4: Testing & Deployment (5 weeks)**\n"
            "- Alpha and beta testing\n"
            "- Performance optimization\n"
            "- App store submission preparation\n"
            "- Marketing assets creation\n"
            "- Launch strategy execution\n\n"
            "**Key Milestones:**\n"
            "1. Design approval: End of week 7\n"
            "2. Alpha version: End of week 15\n"
            "3. Beta testing: Weeks 16-19\n"
            "4. App store submission: Week 20\n\n"
            "**Team Required:**\n"
            "- Project Manager (full-time)\n"
            "- Product Owner (full-time)\n"
            "- UX/UI Designer (1, full-time)\n"
            "- Mobile Developers (2-3, full-time)\n"
            "- Backend Developer (1, full-time)\n"
            "- QA Engineers (2, full-time during testing phases)"
        )
    elif "software" in topic or "system" in topic:
        return (
            "Project plan for software system development:\n\n"
            "**Phase 1: Inception (4 weeks)**\n"
            "- Business requirements documentation\n"
            "- Technical feasibility assessment\n"
            "- Architecture design and approval\n"
            "- Risk assessment and mitigation planning\n\n"
            "**Phase 2: Elaboration (6 weeks)**\n"
            "- Detailed user stories and acceptance criteria\n"
            "- Database schema design\n"
            "- API specifications\n"
            "- Technical prototype of critical components\n\n"
            "**Phase 3: Construction (16 weeks)**\n"
            "- Sprint planning (2-week sprints)\n"
            "- Progressive development of features\n"
            "- Continuous integration and testing\n"
            "- Regular stakeholder demos\n"
            "- Documentation development\n\n"
            "**Phase 4: Transition (6 weeks)**\n"
            "- User acceptance testing\n"
            "- Performance and security auditing\n"
            "- Production environment setup\n"
            "- Data migration planning\n"
            "- Training and knowledge transfer\n"
            "- Phased deployment strategy\n\n"
            "**Key Milestones:**\n"
            "1. Architecture approval: End of week 4\n"
            "2. First sprint completion: End of week 12\n"
            "3. Feature complete: End of week 26\n"
            "4. System deployment: End of week 32\n\n"
            "**Team Required:**\n"
            "- Project Manager (full-time)\n"
            "- Business Analyst (full-time during inception and elaboration)\n"
            "- Solutions Architect (part-time)\n"
            "- Technical Lead (full-time)\n"
            "- Developers (4-6, full-time)\n"
            "- QA Engineers (2-3, full-time)\n"
            "- DevOps Engineer (part-time)\n"
            "- Technical Writer (part-time)"
        )
    else:
        return (
            f"Project plan for {topic}:\n\n"
            "**Phase 1: Project Initiation (2-3 weeks)**\n"
            "- Project charter development\n"
            "- Stakeholder identification and analysis\n"
            "- Initial scope definition\n"
            "- Resource planning and budgeting\n\n"
            "**Phase 2: Planning & Requirements (4-5 weeks)**\n"
            "- Detailed requirements gathering\n"
            "- Work breakdown structure creation\n"
            "- Schedule development with critical path analysis\n"
            "- Risk register establishment\n"
            "- Communication plan\n\n"
            "**Phase 3: Execution (timeframe depends on project scope)**\n"
            "- Regular status meetings and reporting\n"
            "- Issue and change management\n"
            "- Quality assurance activities\n"
            "- Progress tracking against baselines\n\n"
            "**Phase 4: Monitoring & Controlling (ongoing)**\n"
            "- Performance metrics tracking\n"
            "- Scope verification\n"
            "- Budget control\n"
            "- Risk response implementation\n\n"
            "**Phase 5: Closing (2-3 weeks)**\n"
            "- Deliverable acceptance\n"
            "- Lessons learned documentation\n"
            "- Project documentation archiving\n"
            "- Team recognition and reassignment\n\n"
            "**Recommended Project Management Approach:**\n"
            "- Consider hybrid methodology (Agile with traditional governance)\n"
            "- Implement regular retrospectives for continuous improvement\n"
            "- Use collaborative project management tools\n"
            "- Establish clear escalation paths for issues"
        )

# Mount static files
import pathlib
static_dir = pathlib.Path(__file__).parent.absolute() / "static"
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Redirect root to the index.html page
@app.get("/", include_in_schema=False)
async def read_root():
    return RedirectResponse(url="/static/index.html", status_code=303)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("simple_orchestrator:app", host="0.0.0.0", port=8000, reload=True)
