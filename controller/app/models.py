"""SQLAlchemy database models"""
from sqlalchemy import Column, String, Integer, Float, DateTime, JSON, ForeignKey, Text, Boolean, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum

from .database import Base


def generate_uuid():
    """Generate a UUID string"""
    return str(uuid.uuid4())


class AgentStatus(str, enum.Enum):
    """Agent status enumeration"""
    online = "online"
    offline = "offline"
    inactive = "inactive"


class CommandStatus(str, enum.Enum):
    """Command status enumeration"""
    pending = "pending"
    running = "running"
    completed = "completed"
    failed = "failed"


class Agent(Base):
    """Agent model - represents a registered endpoint"""
    __tablename__ = "agents"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    hostname = Column(String, nullable=False)
    os = Column(String, nullable=False)
    os_version = Column(String)
    ip = Column(String)
    last_seen = Column(DateTime, default=datetime.utcnow)
    registered_at = Column(DateTime, default=datetime.utcnow)
    status = Column(SQLEnum(AgentStatus), default=AgentStatus.offline)
    auth_key_hash = Column(String)  # Hashed token for authentication
    metadata = Column(JSON)  # Additional agent information
    
    # Relationships
    reports = relationship("Report", back_populates="agent", cascade="all, delete-orphan")
    commands = relationship("Command", back_populates="agent", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Agent(id={self.id}, hostname={self.hostname}, status={self.status})>"


class Report(Base):
    """Report model - stores scan results from agents"""
    __tablename__ = "reports"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    agent_id = Column(String, ForeignKey("agents.id"), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    mode = Column(String)  # standard or strict
    overall_status = Column(String)
    overall_score = Column(Float)
    payload = Column(JSON)  # Full report JSON
    
    # Relationship
    agent = relationship("Agent", back_populates="reports")
    
    def __repr__(self):
        return f"<Report(id={self.id}, agent_id={self.agent_id}, status={self.overall_status})>"


class Command(Base):
    """Command model - represents commands sent to agents"""
    __tablename__ = "commands"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    agent_id = Column(String, ForeignKey("agents.id"), nullable=False)
    command_type = Column(String, nullable=False)  # scan, update, etc.
    payload = Column(JSON)  # Command parameters
    status = Column(SQLEnum(CommandStatus), default=CommandStatus.pending)
    result = Column(JSON)  # Command execution result
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    agent = relationship("Agent", back_populates="commands")
    
    def __repr__(self):
        return f"<Command(id={self.id}, type={self.command_type}, status={self.status})>"


class User(Base):
    """User model - for admin authentication"""
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<User(username={self.username}, is_admin={self.is_admin})>"
