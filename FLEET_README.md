# Cyber Essentials Fleet Management

**Transform your single-system scanner into enterprise-scale fleet management**

This extension to the Cyber Essentials Scanner provides a complete controller-agent architecture for managing compliance scanning across multiple endpoints.

## 🚀 Quick Start

### Start the Controller

```bash
cd controller
docker-compose up -d
```

Controller will be available at http://localhost:8000

**Default Admin Credentials:**
- Username: `admin`
- Password: `changeme`

⚠️ **Change these immediately after first login!**

### Register an Agent

```bash
cd agent
pip install -r requirements.txt
python agent.py --register --controller http://localhost:8000 --no-verify-ssl
```

### Start Agent Daemon

```bash
python agent.py --daemon
```

### Access Dashboard

Open http://localhost:3000 (after starting frontend)

```bash
cd frontend
npm install
npm run dev
```

## 📋 What's Included

### Controller Server
- **FastAPI REST API** for agent management
- **PostgreSQL database** for storing agents, reports, and commands
- **JWT authentication** for admins and agents
- **Docker deployment** with docker-compose

### Agent
- **Automatic registration** with controller
- **Periodic heartbeat** to track online status
- **Command polling** for remote scan triggers
- **Scheduled scans** (daily, weekly, or manual)
- **Secure token storage** using OS credential stores

### Web Dashboard
- **Agent inventory** - View all registered endpoints
- **Trigger scans** - Run compliance checks on demand
- **View reports** - See scan results and trends
- **Admin management** - User authentication

### Deployment Tools
- **GPO deployment** scripts for Windows domains
- **Intune deployment** for modern management
- **Systemd service** files for Linux
- **LaunchDaemon** configuration for macOS

## 📁 Repository Structure

```
.
├── controller/              # Backend API server
│   ├── app/
│   │   ├── main.py         # FastAPI application
│   │   ├── models.py       # Database models
│   │   ├── schemas.py      # API schemas
│   │   └── auth.py         # Authentication
│   ├── Dockerfile
│   ├── docker-compose.yml
│   └── requirements.txt
│
├── agent/                   # Fleet agent
│   ├── agent.py            # Main daemon
│   ├── config.py           # Configuration
│   ├── token_store.py      # Secure storage
│   └── requirements.txt
│
├── frontend/                # React dashboard
│   ├── src/
│   │   ├── components/
│   │   └── App.jsx
│   └── package.json
│
├── deployment/              # Deployment scripts
│   ├── gpo/                # Group Policy deployment
│   ├── intune/             # Intune Win32 app
│   ├── systemd/            # Linux service
│   └── macos/              # macOS LaunchDaemon
│
├── docs/deployment/         # Deployment guides
│   ├── CONTROLLER_DEPLOYMENT.md
│   └── AGENT_DEPLOYMENT.md
│
├── scanner/                 # Original scanner (unchanged)
│   └── ...
│
└── FLEET_ARCHITECTURE.md    # Architecture documentation
```

## 🏗️ Architecture

```
Admin Dashboard ←─HTTPS/JWT─→ Controller API ←─HTTPS/Token─→ Agents
                                    ↓
                              PostgreSQL DB
```

**Key Features:**
- ✅ Centralized management of multiple endpoints
- ✅ Real-time agent status tracking
- ✅ Remote scan triggering
- ✅ Automated reporting
- ✅ Secure communication (HTTPS + JWT)
- ✅ Cross-platform support (Windows, macOS, Linux)

See [FLEET_ARCHITECTURE.md](FLEET_ARCHITECTURE.md) for detailed architecture.

## 🔧 Installation

### Prerequisites

**Controller:**
- Docker + Docker Compose (recommended) OR
- Python 3.11+ and PostgreSQL 15+

**Agent:**
- Python 3.10+
- Network access to controller
- Admin privileges (for full scan functionality)

**Dashboard:**
- Node.js 18+
- npm or yarn

### Controller Setup

1. **Clone repository:**
   ```bash
   git clone <repository-url>
   cd Cyber-Essentials
   ```

2. **Configure controller:**
   ```bash
   cd controller
   cp .env.example .env
   # Edit .env and set SECRET_KEY and DATABASE_URL
   ```

3. **Start with Docker Compose:**
   ```bash
   docker-compose up -d
   ```

4. **Verify:**
   ```bash
   curl http://localhost:8000/health
   ```

See [docs/deployment/CONTROLLER_DEPLOYMENT.md](docs/deployment/CONTROLLER_DEPLOYMENT.md) for detailed setup.

### Agent Setup

**Option 1: Manual Installation**

```bash
cd agent
pip install -r requirements.txt
python agent.py --register --controller https://controller.local
python agent.py --daemon
```

**Option 2: Windows Service (NSSM)**

```powershell
cd deployment\windows
.\install-agent-service.ps1 -ControllerUrl "https://controller.local"
```

**Option 3: Linux Systemd**

```bash
sudo cp deployment/systemd/ce-agent.service /etc/systemd/system/
sudo systemctl enable ce-agent
sudo systemctl start ce-agent
```

**Option 4: GPO Deployment**

See [docs/deployment/AGENT_DEPLOYMENT.md](docs/deployment/AGENT_DEPLOYMENT.md) for GPO/Intune deployment.

### Dashboard Setup

```bash
cd frontend
npm install
npm run dev
```

Dashboard will be available at http://localhost:3000

## 🔐 Security

### Authentication

- **Admin:** JWT tokens (30-minute expiration)
- **Agents:** Long-lived tokens (1 year), securely stored

### Communication

- **TLS/SSL:** All traffic encrypted (HTTPS required)
- **Token validation:** Controller validates agent identity
- **Database:** Credentials in environment variables

### Best Practices

1. Change default admin password immediately
2. Use strong SECRET_KEY (generate with `openssl rand -hex 32`)
3. Enable TLS/SSL certificates (Let's Encrypt recommended)
4. Restrict controller access with firewall rules
5. Regular security updates
6. Rotate agent tokens periodically

## 📊 Usage

### Via Dashboard

1. **Login:** http://localhost:3000
2. **View Agents:** See all registered endpoints
3. **Trigger Scan:** Click "Scan All Agents" or select specific agent
4. **View Reports:** Check compliance status and scores

### Via API

**Get all agents:**
```bash
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/agents
```

**Trigger scan:**
```bash
curl -X POST -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/agents/{agent_id}/scan
```

**View reports:**
```bash
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/reports
```

See API documentation at http://localhost:8000/docs

### Agent Commands

**Register:**
```bash
python agent.py --register --controller https://controller.local
```

**One-shot scan:**
```bash
python agent.py --scan --mode standard
```

**Start daemon:**
```bash
python agent.py --daemon
```

## 🚀 Deployment Scenarios

### Small Office (1-50 endpoints)

- Single controller instance (Docker Compose)
- SQLite or PostgreSQL
- Manual agent installation
- Basic monitoring

### Enterprise (50-1000 endpoints)

- Controller on dedicated server/VM
- PostgreSQL database
- GPO or Intune deployment
- Nginx reverse proxy with SSL
- Centralized logging

### Large Enterprise (1000+ endpoints)

- Multiple controller instances (load balanced)
- PostgreSQL with read replicas
- Automated deployment (GPO/Intune/SCCM)
- Full observability stack
- Database partitioning

See [FLEET_ARCHITECTURE.md](FLEET_ARCHITECTURE.md) for scaling guidance.

## 📝 Configuration

### Controller Environment Variables

```bash
# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/ce_controller

# Security
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
AGENT_TOKEN_EXPIRE_DAYS=365

# Application
DEBUG=false
CORS_ORIGINS=http://localhost:3000
```

### Agent Environment Variables

```bash
CE_CONTROLLER_URL=https://controller.local:8000
CE_VERIFY_SSL=true
CE_HEARTBEAT_INTERVAL=60
CE_COMMAND_POLL_INTERVAL=30
CE_SCAN_SCHEDULE=daily
CE_LOG_LEVEL=INFO
```

## 🔍 Monitoring

### Health Checks

- Controller: `GET /health`
- Agent: Heartbeat every 60 seconds
- Database: Connection monitoring

### Logs

**Controller:**
```bash
docker-compose logs -f controller
```

**Agent:**
- Windows: `C:\Program Files\CyberEssentials\Agent\ce-agent.log`
- Linux: `sudo journalctl -u ce-agent -f`
- macOS: `/var/log/ce-agent.log`

## 🐛 Troubleshooting

### Controller Issues

**Won't start:**
- Check logs: `docker-compose logs controller`
- Verify DATABASE_URL
- Ensure SECRET_KEY is set

**Database connection errors:**
- Verify PostgreSQL is running
- Check credentials
- Ensure database exists

### Agent Issues

**Won't register:**
- Verify controller URL is accessible
- Check TLS certificate
- Try with `--no-verify-ssl` for testing

**Not reporting:**
- Check agent is running
- View logs
- Test network connectivity

**Service won't start:**
- Verify Python version (3.10+)
- Check file permissions
- Review service logs

See full troubleshooting in deployment documentation.

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file

## 🙏 Acknowledgments

- Cyber Essentials 2025 guidance
- FastAPI framework
- React and Vite
- Python community

## 📞 Support

- **Documentation:** See [docs/deployment/](docs/deployment/)
- **Issues:** GitHub Issues
- **Security:** Report privately to maintainers

---

**Note:** This fleet management system extends the base Cyber Essentials Scanner. The original standalone scanner functionality remains unchanged and can still be used independently via `python -m scanner.main`.
