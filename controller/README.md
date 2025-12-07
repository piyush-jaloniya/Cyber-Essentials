# Cyber Essentials Controller

Backend API server for fleet management of Cyber Essentials agents.

## Quick Start

### With Docker Compose (Recommended)

```bash
# Copy and edit environment file
cp .env.example .env
# Edit .env and set SECRET_KEY

# Start services
docker-compose up -d

# Check logs
docker-compose logs -f

# Access API
curl http://localhost:8000/health
```

### Without Docker

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export DATABASE_URL="postgresql://user:pass@localhost/ce_controller"
export SECRET_KEY="your-secret-key-here"

# Run server
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## Default Credentials

- Username: `admin`
- Password: `changeme`

⚠️ **Change immediately after first login!**

## API Documentation

Once running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Key Endpoints

### Authentication
- `POST /api/auth/login` - Admin login

### Agent Management
- `POST /api/agents/register` - Register new agent
- `GET /api/agents` - List all agents
- `POST /api/agents/{id}/scan` - Trigger scan

### Reports
- `GET /api/reports` - List all reports
- `GET /api/reports/{id}` - Get report details

## Configuration

Edit `.env` file:

```bash
# Database
DATABASE_URL=postgresql://ce_user:ce_password@postgres:5432/ce_controller

# Security (CHANGE IN PRODUCTION)
SECRET_KEY=your-secret-key-generate-with-openssl-rand-hex-32
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
AGENT_TOKEN_EXPIRE_DAYS=365

# Application
DEBUG=false

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:8000
```

## Deployment

See [../docs/deployment/CONTROLLER_DEPLOYMENT.md](../docs/deployment/CONTROLLER_DEPLOYMENT.md)

## Troubleshooting

### Database Connection Error

```bash
# Check PostgreSQL is running
docker-compose ps postgres

# Check DATABASE_URL is correct
echo $DATABASE_URL
```

### Port Already in Use

```bash
# Change port in docker-compose.yml or use different port:
uvicorn app.main:app --port 8001
```

## Development

```bash
# Install dev dependencies
pip install -r requirements.txt

# Run with auto-reload
uvicorn app.main:app --reload

# Run tests (if available)
pytest
```
