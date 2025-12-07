"""Pydantic schemas for request/response validation"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


# Agent schemas
class AgentRegister(BaseModel):
    """Schema for agent registration"""
    hostname: str
    os: str
    os_version: Optional[str] = None
    ip: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class AgentResponse(BaseModel):
    """Schema for agent response"""
    agent_id: str
    agent_token: str


class AgentInfo(BaseModel):
    """Schema for agent information"""
    id: str
    hostname: str
    os: str
    os_version: Optional[str] = None
    ip: Optional[str] = None
    last_seen: datetime
    registered_at: datetime
    status: str
    metadata: Optional[Dict[str, Any]] = None
    
    class Config:
        from_attributes = True


class AgentList(BaseModel):
    """Schema for list of agents"""
    agents: List[AgentInfo]
    total: int


# Report schemas
class ReportSubmit(BaseModel):
    """Schema for submitting a report"""
    mode: str = "standard"
    overall_status: str
    overall_score: float
    payload: Dict[str, Any]


class ReportInfo(BaseModel):
    """Schema for report information"""
    id: str
    agent_id: str
    timestamp: datetime
    mode: Optional[str] = None
    overall_status: str
    overall_score: float
    
    class Config:
        from_attributes = True


class ReportDetail(BaseModel):
    """Schema for detailed report"""
    id: str
    agent_id: str
    timestamp: datetime
    mode: Optional[str] = None
    overall_status: str
    overall_score: float
    payload: Dict[str, Any]
    
    class Config:
        from_attributes = True


class ReportList(BaseModel):
    """Schema for list of reports"""
    reports: List[ReportInfo]
    total: int


# Command schemas
class CommandCreate(BaseModel):
    """Schema for creating a command"""
    command_type: str
    payload: Optional[Dict[str, Any]] = None


class CommandInfo(BaseModel):
    """Schema for command information"""
    id: str
    agent_id: str
    command_type: str
    payload: Optional[Dict[str, Any]] = None
    status: str
    result: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class CommandResult(BaseModel):
    """Schema for submitting command result"""
    status: str
    result: Optional[Dict[str, Any]] = None


# Auth schemas
class Token(BaseModel):
    """Schema for authentication token"""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Schema for token payload data"""
    username: Optional[str] = None
    agent_id: Optional[str] = None


class UserLogin(BaseModel):
    """Schema for user login"""
    username: str
    password: str


class UserCreate(BaseModel):
    """Schema for creating a user"""
    username: str
    email: Optional[str] = None
    password: str
    is_admin: bool = False


# Heartbeat schema
class Heartbeat(BaseModel):
    """Schema for agent heartbeat"""
    status: Optional[str] = "online"
    metadata: Optional[Dict[str, Any]] = None
