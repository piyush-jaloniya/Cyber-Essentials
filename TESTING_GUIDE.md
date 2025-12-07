# Testing Guide - Fleet Management System

This guide walks through testing the complete controller-agent architecture.

## Prerequisites

- Docker and Docker Compose installed
- Python 3.10+ installed
- Node.js 18+ installed (for frontend)
- Network connectivity between components

## Quick Test Sequence

### 1. Test Controller Deployment

**Start the controller:**

```bash
cd controller
./start.sh
```

**Verify health:**

```bash
curl http://localhost:8000/health
```

Expected output:
```json
{"status": "healthy", "version": "0.1.0"}
```

**Test API documentation:**

Open in browser: http://localhost:8000/docs

You should see Swagger UI with all API endpoints.

**Test admin login:**

```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"changeme"}'
```

Expected output:
```json
{
  "access_token": "eyJ...",
  "token_type": "bearer"
}
```

### 2. Test Agent Registration

**Install agent dependencies:**

```bash
cd ../agent
pip install -r requirements.txt
```

**Register agent:**

```bash
python agent.py --register --controller http://localhost:8000 --no-verify-ssl
```

Expected output:
```
Initializing CE Agent (Controller: http://localhost:8000)
Attempting to register with controller...
Successfully registered as agent <uuid>
```

**Verify registration in controller:**

```bash
# Save your admin token from step 1
TOKEN="eyJ..."

curl http://localhost:8000/api/agents \
  -H "Authorization: Bearer $TOKEN"
```

Expected output:
```json
{
  "agents": [
    {
      "id": "...",
      "hostname": "...",
      "os": "...",
      "status": "online",
      ...
    }
  ],
  "total": 1
}
```

### 3. Test One-Shot Scan

**Run a scan:**

```bash
python agent.py --scan --mode standard
```

Expected output:
```
Starting compliance scan...
✓ Scan completed: pass (score: 0.85)
✓ Report uploaded successfully: <report_id>
```

**Verify report in controller:**

```bash
curl http://localhost:8000/api/reports \
  -H "Authorization: Bearer $TOKEN"
```

Expected output:
```json
{
  "reports": [
    {
      "id": "...",
      "agent_id": "...",
      "overall_status": "pass",
      "overall_score": 0.85,
      ...
    }
  ],
  "total": 1
}
```

### 4. Test Remote Scan Trigger

**Get your agent ID:**

```bash
AGENT_ID=$(curl -s http://localhost:8000/api/agents \
  -H "Authorization: Bearer $TOKEN" | \
  python -c "import sys, json; print(json.load(sys.stdin)['agents'][0]['id'])")

echo $AGENT_ID
```

**Trigger a scan:**

```bash
curl -X POST http://localhost:8000/api/agents/$AGENT_ID/scan \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"command_type":"scan","payload":{"mode":"standard"}}'
```

**Start agent daemon to process command:**

```bash
# In a separate terminal
python agent.py --daemon
```

Agent should:
1. Poll for commands
2. Execute the scan
3. Upload the report
4. Submit command result

### 5. Test Dashboard

**Install frontend dependencies:**

```bash
cd ../frontend
npm install
```

**Start development server:**

```bash
npm run dev
```

**Access dashboard:**

Open browser: http://localhost:3000

**Test login:**
- Username: `admin`
- Password: `changeme`

**Verify functionality:**
1. ✓ Login successful
2. ✓ See agent in list
3. ✓ Click agent to view details
4. ✓ See reports
5. ✓ Click "Run Scan" button
6. ✓ Verify new report appears

## Integration Test Checklist

### Controller Tests

- [ ] Controller starts successfully
- [ ] Health endpoint responds
- [ ] Database connection works
- [ ] Admin login works
- [ ] API documentation accessible
- [ ] Agent registration endpoint works
- [ ] Reports endpoint works
- [ ] Commands endpoint works

### Agent Tests

- [ ] Agent compiles without errors
- [ ] Agent registers with controller
- [ ] Token stored securely
- [ ] Heartbeat works
- [ ] Command polling works
- [ ] Scan execution works
- [ ] Report upload works
- [ ] Daemon mode runs continuously

### Dashboard Tests

- [ ] Frontend builds successfully
- [ ] Login page loads
- [ ] Authentication works
- [ ] Agents list displays
- [ ] Agent details page works
- [ ] Reports page works
- [ ] Scan trigger works
- [ ] UI updates after actions

### End-to-End Test

- [ ] Register multiple agents
- [ ] Trigger bulk scan from dashboard
- [ ] All agents execute scans
- [ ] All reports uploaded
- [ ] Dashboard shows updated data
- [ ] Agent status shows online
- [ ] Reports show correct scores

## Performance Tests

### Load Testing

**Register multiple agents:**

```bash
for i in {1..10}; do
  python agent.py --register --controller http://localhost:8000 --no-verify-ssl
done
```

**Trigger bulk scan:**

```bash
curl -X POST http://localhost:8000/api/agents/scan \
  -H "Authorization: Bearer $TOKEN"
```

**Monitor:**
- Response times
- Database queries
- Memory usage
- CPU usage

### Stress Testing

**High-frequency heartbeats:**

```bash
# Multiple agents sending heartbeats simultaneously
for i in {1..50}; do
  (python agent.py --daemon &)
done
```

**Monitor:**
- Controller response times
- Database connection pool
- Error rates
- System resources

## Security Tests

### Authentication Tests

**Test without token:**

```bash
curl http://localhost:8000/api/agents
# Expected: 403 Forbidden
```

**Test with invalid token:**

```bash
curl http://localhost:8000/api/agents \
  -H "Authorization: Bearer invalid_token"
# Expected: 401 Unauthorized
```

**Test token expiration:**

```bash
# Wait 31 minutes (token expires after 30 min)
curl http://localhost:8000/api/agents \
  -H "Authorization: Bearer $OLD_TOKEN"
# Expected: 401 Unauthorized
```

### Authorization Tests

**Agent trying to access another agent's data:**

```bash
# Get agent 1 token
TOKEN1="..."

# Try to send heartbeat for agent 2
curl -X POST http://localhost:8000/api/agents/<agent2_id>/heartbeat \
  -H "Authorization: Bearer $TOKEN1"
# Expected: 403 Forbidden
```

## Deployment Tests

### Docker Deployment

```bash
cd controller
docker-compose up -d
docker-compose ps
docker-compose logs
```

**Verify:**
- [ ] All containers running
- [ ] No errors in logs
- [ ] Health check passes
- [ ] Database connected

### Service Deployment

**Linux (systemd):**

```bash
sudo cp deployment/systemd/ce-agent.service /etc/systemd/system/
sudo systemctl start ce-agent
sudo systemctl status ce-agent
```

**Windows (NSSM):**

```powershell
cd deployment\windows
.\install-agent-service.ps1 -ControllerUrl "http://localhost:8000"
nssm status CEAgent
```

## Troubleshooting Common Issues

### Controller won't start

```bash
# Check logs
docker-compose logs controller

# Check database
docker-compose logs postgres

# Check environment
cat .env
```

### Agent can't register

```bash
# Check connectivity
curl http://localhost:8000/health

# Check controller logs
docker-compose logs -f controller

# Check SSL (use --no-verify-ssl for testing)
python agent.py --register --controller http://localhost:8000 --no-verify-ssl
```

### Dashboard won't load

```bash
# Check frontend build
npm run build

# Check API proxy
cat vite.config.js

# Check browser console for errors
```

## Automated Testing

### Unit Tests (Future)

```bash
# Controller
cd controller
pytest tests/

# Agent
cd agent
pytest tests/

# Frontend
cd frontend
npm test
```

### CI/CD Integration (Future)

```yaml
# .github/workflows/test.yml
name: Test Fleet Management
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Start controller
        run: cd controller && docker-compose up -d
      - name: Test registration
        run: cd agent && python agent.py --register --controller http://localhost:8000
      - name: Test scan
        run: cd agent && python agent.py --scan
```

## Success Criteria

All tests pass when:

✅ Controller starts and responds to health checks
✅ Database connection established
✅ Admin can login
✅ Agent can register
✅ Agent can send heartbeats
✅ Agent can execute scans
✅ Reports uploaded successfully
✅ Dashboard displays data
✅ Remote scan triggers work
✅ No security vulnerabilities
✅ Performance acceptable under load

## Next Steps

After successful testing:

1. Deploy to staging environment
2. Security audit
3. Performance optimization
4. User acceptance testing
5. Production deployment
6. Monitoring setup
7. Documentation updates
