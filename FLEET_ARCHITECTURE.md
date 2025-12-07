# Cyber Essentials Fleet Management Architecture

**Version:** 2025 v3.2 "Willow" — Controller + Agent Architecture

## Overview

This document describes the complete architecture for scaling the Cyber Essentials Scanner from a single-system tool into a fleet-capable solution that can manage compliance scanning across multiple endpoints.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                     Administrator                               │
│                   (Web Dashboard)                               │
└───────────────────────────┬─────────────────────────────────────┘
                            │ HTTPS/TLS
                            │ JWT Auth
┌───────────────────────────▼─────────────────────────────────────┐
│                    CONTROLLER SERVER                            │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              FastAPI REST API                             │  │
│  │  • Agent Registration     • Command Dispatch              │  │
│  │  • Report Ingestion       • Authentication                │  │
│  │  • Admin Endpoints        • Heartbeat Tracking            │  │
│  └─────────────┬────────────────────────────────────────────┘  │
│                │                                                 │
│  ┌─────────────▼────────────────────────────────────────────┐  │
│  │          PostgreSQL Database                              │  │
│  │  • Agents     • Reports     • Commands     • Users        │  │
│  └────────────────────────────────────────────────────────────┘  │
└───────────────────────────┬─────────────────────────────────────┘
                            │ HTTPS/TLS
                            │ Bearer Token Auth
        ┌───────────────────┼───────────────────┐
        │                   │                   │
┌───────▼────────┐  ┌──────▼─────────┐  ┌─────▼──────────┐
│   Agent (PC)   │  │   Agent (PC)   │  │   Agent (PC)   │
│   Windows 11   │  │   macOS 14     │  │   Ubuntu 22.04 │
│                │  │                │  │                │
│ ┌────────────┐ │  │ ┌────────────┐ │  │ ┌────────────┐ │
│ │  Scanner   │ │  │ │  Scanner   │ │  │ │  Scanner   │ │
│ │  Modules   │ │  │ │  Modules   │ │  │ │  Modules   │ │
│ └────────────┘ │  │ └────────────┘ │  │ └────────────┘ │
│                │  │                │  │                │
│ • Register     │  │ • Register     │  │ • Register     │
│ • Heartbeat    │  │ • Heartbeat    │  │ • Heartbeat    │
│ • Poll Cmds    │  │ • Poll Cmds    │  │ • Poll Cmds    │
│ • Run Scans    │  │ • Run Scans    │  │ • Run Scans    │
│ • Upload       │  │ • Upload       │  │ • Upload       │
└────────────────┘  └────────────────┘  └────────────────┘
```

## Components

### 1. Controller Server

**Technology:** FastAPI (Python 3.11+)

**Responsibilities:**
- Agent registration and authentication
- Command dispatch (trigger scans, update agents)
- Report ingestion and storage
- Admin authentication and authorization
- Agent status tracking (heartbeat monitoring)
- Web API for dashboard

**Key Files:**
```
controller/
├── app/
│   ├── main.py          # FastAPI application
│   ├── models.py        # SQLAlchemy database models
│   ├── schemas.py       # Pydantic request/response schemas
│   ├── auth.py          # Authentication & authorization
│   ├── database.py      # Database connection
│   └── config.py        # Configuration settings
├── requirements.txt     # Python dependencies
├── Dockerfile          # Container image
└── docker-compose.yml  # Full stack deployment
```

**Database Schema:**

```sql
-- Agents table
CREATE TABLE agents (
    id UUID PRIMARY KEY,
    hostname VARCHAR NOT NULL,
    os VARCHAR NOT NULL,
    os_version VARCHAR,
    ip VARCHAR,
    last_seen TIMESTAMP,
    registered_at TIMESTAMP,
    status VARCHAR,  -- online, offline, inactive
    auth_key_hash VARCHAR,
    metadata JSONB
);

-- Reports table
CREATE TABLE reports (
    id UUID PRIMARY KEY,
    agent_id UUID REFERENCES agents(id),
    timestamp TIMESTAMP,
    mode VARCHAR,  -- standard, strict
    overall_status VARCHAR,  -- pass, warn, fail
    overall_score FLOAT,
    payload JSONB  -- Full report JSON
);

-- Commands table
CREATE TABLE commands (
    id UUID PRIMARY KEY,
    agent_id UUID REFERENCES agents(id),
    command_type VARCHAR,  -- scan, update, etc.
    payload JSONB,
    status VARCHAR,  -- pending, running, completed, failed
    result JSONB,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

-- Users table (admin access)
CREATE TABLE users (
    id UUID PRIMARY KEY,
    username VARCHAR UNIQUE NOT NULL,
    email VARCHAR UNIQUE,
    hashed_password VARCHAR NOT NULL,
    is_active BOOLEAN,
    is_admin BOOLEAN,
    created_at TIMESTAMP
);
```

### 2. Agent

**Technology:** Python 3.10+

**Responsibilities:**
- Register with controller on first run
- Send periodic heartbeats
- Poll for commands
- Execute compliance scans (wraps existing scanner)
- Upload scan reports
- Secure token storage

**Key Files:**
```
agent/
├── agent.py          # Main agent daemon
├── config.py         # Configuration
├── token_store.py    # Secure credential storage
└── requirements.txt  # Python dependencies
```

**Agent Lifecycle:**

```
┌──────────────┐
│   Startup    │
└──────┬───────┘
       │
       ▼
┌──────────────────┐      ┌─────────────────┐
│ Load Config      │─────▶│ Token Exists?   │
└──────────────────┘      └────┬────────┬───┘
                               │ No     │ Yes
                               ▼        ▼
                         ┌──────────┐  ┌──────────┐
                         │ Register │  │ Validate │
                         └────┬─────┘  └────┬─────┘
                              └────────────┬┘
                                           ▼
                              ┌─────────────────────┐
                              │   Main Loop         │
                              │                     │
                              │ • Send Heartbeat    │
                              │   (every 60s)       │
                              │                     │
                              │ • Poll Commands     │
                              │   (every 30s)       │
                              │                     │
                              │ • Execute Commands  │
                              │   (scan, update)    │
                              │                     │
                              │ • Scheduled Scans   │
                              │   (daily @ 2am)     │
                              └─────────────────────┘
```

### 3. Web Dashboard

**Technology:** React + Vite

**Features:**
- Admin login
- Agent inventory (list all registered agents)
- Agent details (view agent info and recent reports)
- Trigger scans (single agent or bulk)
- View reports
- Export data

**Key Files:**
```
frontend/
├── src/
│   ├── App.jsx                  # Main app component
│   ├── components/
│   │   ├── Login.jsx           # Login page
│   │   ├── AgentsList.jsx      # Agent inventory
│   │   ├── AgentDetails.jsx    # Agent details + reports
│   │   └── ReportsList.jsx     # All reports view
│   └── index.css               # Styling
├── package.json
└── vite.config.js
```

## API Endpoints

### Authentication

**POST /api/auth/login**
- Request: `{username, password}`
- Response: `{access_token, token_type}`
- Used by: Admin dashboard

### Agent Endpoints

**POST /api/agents/register**
- Request: `{hostname, os, os_version, ip, metadata}`
- Response: `{agent_id, agent_token}`
- Used by: Agent on first run

**POST /api/agents/{agent_id}/heartbeat**
- Request: `{status, metadata}`
- Response: `{status: "ok"}`
- Auth: Bearer token (agent)
- Used by: Agent every 60 seconds

**POST /api/agents/{agent_id}/report**
- Request: `{mode, overall_status, overall_score, payload}`
- Response: `{status: "ok", report_id}`
- Auth: Bearer token (agent)
- Used by: Agent after scan completion

**GET /api/agents/{agent_id}/commands**
- Response: `[{id, command_type, payload, status}, ...]`
- Auth: Bearer token (agent)
- Used by: Agent polling for commands

**POST /api/agents/{agent_id}/command/{cmd_id}/result**
- Request: `{status, result}`
- Response: `{status: "ok"}`
- Auth: Bearer token (agent)
- Used by: Agent after command execution

### Admin Endpoints

**GET /api/agents**
- Response: `{agents: [...], total}`
- Auth: Bearer token (admin)
- Used by: Dashboard agent list

**GET /api/agents/{agent_id}**
- Response: Agent details
- Auth: Bearer token (admin)
- Used by: Dashboard agent details

**POST /api/agents/{agent_id}/scan**
- Request: `{mode: "standard|strict"}`
- Response: `{status: "ok", command_id}`
- Auth: Bearer token (admin)
- Used by: Dashboard trigger scan

**POST /api/agents/scan**
- Request: `{agent_ids: [...], mode}`
- Response: `{status: "ok", command_ids: [...], agents_count}`
- Auth: Bearer token (admin)
- Used by: Dashboard bulk scan

**GET /api/reports**
- Query params: `?agent_id=...&skip=0&limit=100`
- Response: `{reports: [...], total}`
- Auth: Bearer token (admin)
- Used by: Dashboard reports view

## Security

### Authentication

1. **Admin Authentication:**
   - JWT tokens with 30-minute expiration
   - Passwords hashed with bcrypt
   - HTTPS/TLS required

2. **Agent Authentication:**
   - Long-lived JWT tokens (365 days)
   - Issued during registration
   - Stored securely using OS-native credential stores:
     - Windows: DPAPI (Credential Manager)
     - macOS: Keychain
     - Linux: keyring or encrypted file

### Communication Security

1. **TLS/SSL:**
   - All communication over HTTPS
   - Certificate verification enabled by default
   - Self-signed certificates supported for testing (--no-verify-ssl)

2. **Token Security:**
   - Agent tokens include agent_id claim
   - Controller validates token ownership before executing commands
   - Tokens cannot be used to access other agents' data

### Data Protection

1. **Database:**
   - Connection string stored in environment variables
   - Support for database encryption at rest
   - Regular backups recommended

2. **Reports:**
   - Contain system configuration data
   - No PII by default
   - Access restricted to authenticated admins

## Deployment

### Controller Deployment

**Docker Compose (Recommended):**
```bash
cd controller
docker-compose up -d
```

**Manual:**
```bash
cd controller
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

See [CONTROLLER_DEPLOYMENT.md](docs/deployment/CONTROLLER_DEPLOYMENT.md)

### Agent Deployment

**Manual:**
```bash
cd agent
pip install -r requirements.txt
python agent.py --register --controller https://controller.local
python agent.py --daemon
```

**GPO (Windows Domain):**
- Copy agent files to NETLOGON share
- Create GPO startup script
- Link to Workstations OU

**Intune (Modern Management):**
- Package as Win32 app
- Deploy via Intune
- Auto-register and start service

See [AGENT_DEPLOYMENT.md](docs/deployment/AGENT_DEPLOYMENT.md)

## Scaling Considerations

### Small Deployments (1-100 agents)

- Single controller instance
- SQLite or PostgreSQL
- No load balancer needed
- Basic monitoring

### Medium Deployments (100-1000 agents)

- Multiple controller instances behind load balancer
- PostgreSQL with connection pooling
- Redis for caching (optional)
- Prometheus + Grafana monitoring

### Large Deployments (1000+ agents)

- Kubernetes cluster for controller
- PostgreSQL read replicas
- Redis for caching and session management
- Message queue (RabbitMQ/Redis Streams) for command dispatch
- Full observability stack (Prometheus, Grafana, ELK)
- Database partitioning for reports

## Monitoring and Telemetry

### Health Checks

- Controller: `GET /health`
- Agent: Heartbeat every 60 seconds
- Database: Connection pool monitoring

### Metrics

- Active agents count
- Offline agents (last seen > 5 minutes)
- Reports processed per hour
- API response times
- Database query performance

### Logging

- Controller: uvicorn logs + application logs
- Agent: Rotating file logs + syslog/journal
- Centralized logging (ELK stack) recommended

## Future Enhancements

1. **WebSockets:** Real-time command push (instead of polling)
2. **Auto-Updater:** Agent self-update capability
3. **Multi-Tenancy:** Support for MSPs managing multiple organizations
4. **Remediation:** Automated fixing of common issues
5. **Alerting:** Email/Slack notifications for failures
6. **Reporting:** PDF/Excel export, compliance dashboards
7. **Policy Management:** Custom compliance policies per organization
8. **Audit Logs:** Track all admin actions

## Troubleshooting

### Common Issues

1. **Agent won't register:**
   - Check controller URL and network connectivity
   - Verify TLS certificate
   - Check controller logs for errors

2. **Agent not reporting:**
   - Verify agent service is running
   - Check agent logs
   - Test network connectivity to controller

3. **Dashboard login fails:**
   - Default credentials: admin / changeme
   - Check controller logs
   - Verify DATABASE_URL is correct

4. **Database connection errors:**
   - Verify PostgreSQL is running
   - Check DATABASE_URL format
   - Ensure database exists

See full troubleshooting guides in deployment documentation.

## Support and Contributing

- Report issues on GitHub
- Deployment questions: See docs/deployment/
- Security issues: Report privately to maintainers
- Contributions: Submit pull requests

## License

MIT License (or as specified in LICENSE file)
