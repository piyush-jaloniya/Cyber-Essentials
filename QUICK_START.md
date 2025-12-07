# Quick Start Guide - Fleet Management in 5 Minutes

Get the Cyber Essentials Fleet Management system up and running quickly.

## Prerequisites

- Docker and Docker Compose (for controller)
- Python 3.10+ (for agent)
- Node.js 18+ (for dashboard)

## Step 1: Start the Controller (2 minutes)

```bash
cd controller
./start.sh
```

This will:
- Create `.env` with secure SECRET_KEY
- Start PostgreSQL database
- Start FastAPI controller
- Create default admin user

**Verify it's running:**
```bash
curl http://localhost:8000/health
# Expected: {"status":"healthy","version":"0.1.0"}
```

**Access API docs:** http://localhost:8000/docs

## Step 2: Register an Agent (1 minute)

```bash
cd ../agent
pip install -r requirements.txt
python agent.py --register --controller http://localhost:8000 --no-verify-ssl
```

**Expected output:**
```
Successfully registered as agent <uuid>
Token stored securely
```

## Step 3: Run a Test Scan (1 minute)

```bash
python agent.py --scan --mode standard
```

**Expected output:**
```
Starting compliance scan...
[1/6] Checking Firewalls... ✓ PASS
[2/6] Checking Secure Configuration... ✓ PASS
...
✓ Scan completed: pass (score: 0.85)
✓ Report uploaded successfully
```

## Step 4: Start the Dashboard (1 minute)

```bash
cd ../frontend
npm install
npm run dev
```

**Access dashboard:** http://localhost:3000

**Login:**
- Username: `admin`
- Password: `changeme`

**⚠️ Change password immediately!**

## Step 5: Verify Everything Works

### In the Dashboard:

1. ✅ See your agent in the list
2. ✅ View agent details
3. ✅ See the report from step 3
4. ✅ Click "Run Scan" to trigger a remote scan

### Start Agent Daemon:

```bash
cd ../agent
python agent.py --daemon
```

The agent will now:
- Send heartbeats every 60 seconds
- Poll for commands every 30 seconds
- Execute remote scan requests
- Upload reports automatically

## What's Next?

### Development

- Explore API docs: http://localhost:8000/docs
- Modify agent configuration: `agent/config.py`
- Customize dashboard: `frontend/src/`

### Production Deployment

1. **Controller:** Follow [docs/deployment/CONTROLLER_DEPLOYMENT.md](docs/deployment/CONTROLLER_DEPLOYMENT.md)
   - Set up SSL/TLS certificates
   - Use PostgreSQL (not SQLite)
   - Configure environment variables
   - Set up monitoring

2. **Agent:** Follow [docs/deployment/AGENT_DEPLOYMENT.md](docs/deployment/AGENT_DEPLOYMENT.md)
   - Deploy via GPO (Windows domains)
   - Deploy via Intune (modern management)
   - Install as service/daemon
   - Configure for your environment

3. **Dashboard:**
   - Build for production: `npm run build`
   - Deploy to web server
   - Configure API proxy

### Testing

See [TESTING_GUIDE.md](TESTING_GUIDE.md) for comprehensive testing procedures.

## Common Commands

### Controller

```bash
# View logs
docker-compose logs -f

# Restart
docker-compose restart

# Stop
docker-compose down
```

### Agent

```bash
# Register
python agent.py --register --controller <URL>

# One-shot scan
python agent.py --scan --mode standard

# Daemon mode
python agent.py --daemon

# Help
python agent.py --help
```

### API

```bash
# Login (get token)
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"changeme"}'

# List agents
curl http://localhost:8000/api/agents \
  -H "Authorization: Bearer $TOKEN"

# Trigger scan
curl -X POST http://localhost:8000/api/agents/$AGENT_ID/scan \
  -H "Authorization: Bearer $TOKEN"

# Get reports
curl http://localhost:8000/api/reports \
  -H "Authorization: Bearer $TOKEN"
```

## Troubleshooting

### Controller won't start

```bash
docker-compose logs controller
# Check DATABASE_URL in .env
# Check SECRET_KEY is set
```

### Agent can't register

```bash
# Test connectivity
curl http://localhost:8000/health

# Check controller URL
echo $CE_CONTROLLER_URL

# Try without SSL verification (testing only)
python agent.py --register --controller http://localhost:8000 --no-verify-ssl
```

### Dashboard login fails

```bash
# Check controller is running
curl http://localhost:8000/health

# Use default credentials
# Username: admin
# Password: changeme
```

## Architecture Overview

```
┌─────────────┐
│  Dashboard  │  http://localhost:3000
└──────┬──────┘
       │ HTTPS + JWT
┌──────▼──────┐
│ Controller  │  http://localhost:8000
│   + DB      │
└──────┬──────┘
       │ HTTPS + Bearer Token
   ┌───┴───┬───────┐
┌──▼──┐ ┌──▼──┐ ┌──▼──┐
│Agent│ │Agent│ │Agent│
└─────┘ └─────┘ └─────┘
```

## Default Credentials

**IMPORTANT:** Change these immediately in production!

- **Controller:** http://localhost:8000
- **Dashboard:** http://localhost:3000
- **Username:** admin
- **Password:** changeme

## Documentation

- [FLEET_README.md](FLEET_README.md) - Complete fleet management guide
- [FLEET_ARCHITECTURE.md](FLEET_ARCHITECTURE.md) - Architecture details
- [TESTING_GUIDE.md](TESTING_GUIDE.md) - Testing procedures
- [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md) - Implementation details

## Support

- Check logs first
- Review documentation
- See TESTING_GUIDE.md for common issues
- File GitHub issues for bugs

## Success!

You now have a working fleet management system! 🎉

- **Agents:** Registered and reporting
- **Controller:** Managing fleet
- **Dashboard:** Visualizing compliance

Continue with production deployment or explore the API documentation.
