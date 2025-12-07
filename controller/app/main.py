"""Main FastAPI application for Cyber Essentials Controller"""
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List, Optional

from .config import settings
from .database import get_db, engine, Base
from .models import Agent, Report, Command, User, AgentStatus, CommandStatus
from .schemas import (
    AgentRegister, AgentResponse, AgentInfo, AgentList,
    ReportSubmit, ReportInfo, ReportDetail, ReportList,
    CommandCreate, CommandInfo, CommandResult,
    Token, UserLogin, UserCreate, Heartbeat
)
from .auth import (
    create_access_token, create_agent_token, authenticate_user,
    get_current_user, get_current_admin, get_current_agent,
    get_password_hash
)

# Create database tables
Base.metadata.create_all(bind=engine)

# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Cyber Essentials Controller - Fleet Management API"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health check
@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "version": settings.app_version}


# ============================================================================
# Authentication Endpoints
# ============================================================================

@app.post("/api/auth/login", response_model=Token)
def login(user_login: UserLogin, db: Session = Depends(get_db)):
    """Admin login endpoint"""
    user = authenticate_user(db, user_login.username, user_login.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
    
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/api/auth/register", response_model=Token)
def register_admin(
    user_create: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """Register a new admin user (requires admin privileges)"""
    # Check if username already exists
    existing_user = db.query(User).filter(User.username == user_create.username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # Create new user
    hashed_password = get_password_hash(user_create.password)
    new_user = User(
        username=user_create.username,
        email=user_create.email,
        hashed_password=hashed_password,
        is_admin=user_create.is_admin
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    access_token = create_access_token(data={"sub": new_user.username})
    return {"access_token": access_token, "token_type": "bearer"}


# ============================================================================
# Agent Endpoints
# ============================================================================

@app.post("/api/agents/register", response_model=AgentResponse)
def register_agent(agent_data: AgentRegister, db: Session = Depends(get_db)):
    """Register a new agent"""
    # Create agent record
    agent = Agent(
        hostname=agent_data.hostname,
        os=agent_data.os,
        os_version=agent_data.os_version,
        ip=agent_data.ip,
        status=AgentStatus.online,
        metadata=agent_data.metadata
    )
    db.add(agent)
    db.commit()
    db.refresh(agent)
    
    # Generate agent token
    agent_token = create_agent_token(agent.id)
    
    # Store hashed token (in production, hash the token)
    # For now, we'll store a placeholder
    agent.auth_key_hash = agent_token[:32]  # Store first 32 chars as reference
    db.commit()
    
    return {"agent_id": agent.id, "agent_token": agent_token}


@app.post("/api/agents/{agent_id}/heartbeat")
def agent_heartbeat(
    agent_id: str,
    heartbeat_data: Heartbeat,
    db: Session = Depends(get_db),
    current_agent: Agent = Depends(get_current_agent)
):
    """Agent heartbeat endpoint"""
    # Verify agent ID matches authenticated agent
    if current_agent.id != agent_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot send heartbeat for another agent"
        )
    
    # Update last_seen and status
    current_agent.last_seen = datetime.utcnow()
    if heartbeat_data.status:
        current_agent.status = AgentStatus(heartbeat_data.status)
    if heartbeat_data.metadata:
        current_agent.metadata = heartbeat_data.metadata
    
    db.commit()
    
    return {"status": "ok", "agent_id": agent_id}


@app.post("/api/agents/{agent_id}/report")
def submit_report(
    agent_id: str,
    report_data: ReportSubmit,
    db: Session = Depends(get_db),
    current_agent: Agent = Depends(get_current_agent)
):
    """Submit a scan report"""
    # Verify agent ID matches authenticated agent
    if current_agent.id != agent_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot submit report for another agent"
        )
    
    # Create report record
    report = Report(
        agent_id=agent_id,
        mode=report_data.mode,
        overall_status=report_data.overall_status,
        overall_score=report_data.overall_score,
        payload=report_data.payload
    )
    db.add(report)
    db.commit()
    db.refresh(report)
    
    return {"status": "ok", "report_id": report.id}


@app.get("/api/agents/{agent_id}/commands", response_model=List[CommandInfo])
def get_agent_commands(
    agent_id: str,
    db: Session = Depends(get_db),
    current_agent: Agent = Depends(get_current_agent)
):
    """Get pending commands for an agent"""
    # Verify agent ID matches authenticated agent
    if current_agent.id != agent_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot retrieve commands for another agent"
        )
    
    # Get pending commands
    commands = db.query(Command).filter(
        Command.agent_id == agent_id,
        Command.status == CommandStatus.pending
    ).all()
    
    # Mark commands as running
    for cmd in commands:
        cmd.status = CommandStatus.running
    db.commit()
    
    return commands


@app.post("/api/agents/{agent_id}/command/{cmd_id}/result")
def submit_command_result(
    agent_id: str,
    cmd_id: str,
    result_data: CommandResult,
    db: Session = Depends(get_db),
    current_agent: Agent = Depends(get_current_agent)
):
    """Submit command execution result"""
    # Verify agent ID matches authenticated agent
    if current_agent.id != agent_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot submit result for another agent"
        )
    
    # Get command
    command = db.query(Command).filter(
        Command.id == cmd_id,
        Command.agent_id == agent_id
    ).first()
    
    if not command:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Command not found"
        )
    
    # Update command status and result
    command.status = CommandStatus(result_data.status)
    command.result = result_data.result
    command.updated_at = datetime.utcnow()
    db.commit()
    
    return {"status": "ok"}


# ============================================================================
# Admin Endpoints
# ============================================================================

@app.get("/api/agents", response_model=AgentList)
def list_agents(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all registered agents"""
    agents = db.query(Agent).offset(skip).limit(limit).all()
    total = db.query(Agent).count()
    
    return {"agents": agents, "total": total}


@app.get("/api/agents/{agent_id}", response_model=AgentInfo)
def get_agent(
    agent_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get agent details"""
    agent = db.query(Agent).filter(Agent.id == agent_id).first()
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found"
        )
    
    return agent


@app.post("/api/agents/{agent_id}/scan")
def trigger_agent_scan(
    agent_id: str,
    command_data: Optional[CommandCreate] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Trigger a scan on a specific agent"""
    # Verify agent exists
    agent = db.query(Agent).filter(Agent.id == agent_id).first()
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found"
        )
    
    # Create scan command
    command = Command(
        agent_id=agent_id,
        command_type="scan",
        payload=command_data.payload if command_data else {"mode": "standard"}
    )
    db.add(command)
    db.commit()
    db.refresh(command)
    
    return {"status": "ok", "command_id": command.id}


@app.post("/api/agents/scan")
def trigger_bulk_scan(
    agent_ids: Optional[List[str]] = None,
    command_data: Optional[CommandCreate] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Trigger scan on multiple agents"""
    # If no agent IDs provided, scan all active agents
    if agent_ids is None:
        agents = db.query(Agent).filter(Agent.status == AgentStatus.online).all()
        agent_ids = [agent.id for agent in agents]
    
    # Create scan commands for all agents
    command_ids = []
    for agent_id in agent_ids:
        command = Command(
            agent_id=agent_id,
            command_type="scan",
            payload=command_data.payload if command_data else {"mode": "standard"}
        )
        db.add(command)
        command_ids.append(command.id)
    
    db.commit()
    
    return {"status": "ok", "command_ids": command_ids, "agents_count": len(agent_ids)}


@app.get("/api/reports", response_model=ReportList)
def list_reports(
    agent_id: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all reports, optionally filtered by agent"""
    query = db.query(Report)
    
    if agent_id:
        query = query.filter(Report.agent_id == agent_id)
    
    reports = query.order_by(Report.timestamp.desc()).offset(skip).limit(limit).all()
    total = query.count()
    
    return {"reports": reports, "total": total}


@app.get("/api/reports/{report_id}", response_model=ReportDetail)
def get_report(
    report_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get detailed report"""
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found"
        )
    
    return report


@app.get("/api/commands", response_model=List[CommandInfo])
def list_commands(
    agent_id: Optional[str] = None,
    status_filter: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List commands, optionally filtered by agent and status"""
    query = db.query(Command)
    
    if agent_id:
        query = query.filter(Command.agent_id == agent_id)
    
    if status_filter:
        query = query.filter(Command.status == CommandStatus(status_filter))
    
    commands = query.order_by(Command.created_at.desc()).offset(skip).limit(limit).all()
    
    return commands


# ============================================================================
# Startup event to create default admin
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Create default admin user if none exists"""
    from .database import SessionLocal
    
    db = SessionLocal()
    try:
        # Check if any admin exists
        admin_exists = db.query(User).filter(User.is_admin == True).first()
        
        if not admin_exists:
            # Create default admin
            default_admin = User(
                username="admin",
                email="admin@localhost",
                hashed_password=get_password_hash("changeme"),
                is_admin=True
            )
            db.add(default_admin)
            db.commit()
            print("=" * 60)
            print("Default admin user created:")
            print("  Username: admin")
            print("  Password: changeme")
            print("  ⚠️  CHANGE THIS PASSWORD IMMEDIATELY!")
            print("=" * 60)
    finally:
        db.close()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
