# Controller Deployment Guide

## Overview

The Cyber Essentials Controller is a FastAPI-based backend that manages fleet agents, receives compliance reports, and provides a web dashboard for administrators.

## Prerequisites

- Docker and Docker Compose (recommended) OR
- Python 3.11+
- PostgreSQL 15+ (or SQLite for development)

## Deployment Options

### Option 1: Docker Compose (Recommended)

1. **Clone the repository:**
   ```bash
   cd controller
   ```

2. **Create environment file:**
   ```bash
   cp .env.example .env
   ```

3. **Edit `.env` and set secure values:**
   ```env
   SECRET_KEY=$(openssl rand -hex 32)
   DATABASE_URL=postgresql://ce_user:SECURE_PASSWORD@postgres:5432/ce_controller
   ```

4. **Start services:**
   ```bash
   docker-compose up -d
   ```

5. **Check logs:**
   ```bash
   docker-compose logs -f controller
   ```

6. **Access the API:**
   - API: http://localhost:8000
   - API Docs: http://localhost:8000/docs
   - Health Check: http://localhost:8000/health

7. **Default Admin Credentials:**
   - Username: `admin`
   - Password: `changeme`
   - **⚠️ Change immediately after first login!**

### Option 2: Manual Deployment

1. **Install Python dependencies:**
   ```bash
   cd controller
   pip install -r requirements.txt
   ```

2. **Set up PostgreSQL:**
   ```bash
   sudo -u postgres psql
   CREATE DATABASE ce_controller;
   CREATE USER ce_user WITH PASSWORD 'your_password';
   GRANT ALL PRIVILEGES ON DATABASE ce_controller TO ce_user;
   \q
   ```

3. **Configure environment:**
   ```bash
   export DATABASE_URL="postgresql://ce_user:your_password@localhost:5432/ce_controller"
   export SECRET_KEY=$(openssl rand -hex 32)
   ```

4. **Run migrations (if using Alembic):**
   ```bash
   alembic upgrade head
   ```

5. **Start the server:**
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000
   ```

### Option 3: Production with Systemd

1. **Create systemd service:**
   ```bash
   sudo nano /etc/systemd/system/ce-controller.service
   ```

2. **Service file content:**
   ```ini
   [Unit]
   Description=Cyber Essentials Controller
   After=network.target postgresql.service

   [Service]
   Type=simple
   User=cecontroller
   WorkingDirectory=/opt/ce-controller
   Environment="DATABASE_URL=postgresql://ce_user:password@localhost:5432/ce_controller"
   Environment="SECRET_KEY=your-secret-key-here"
   ExecStart=/opt/ce-controller/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
   Restart=on-failure

   [Install]
   WantedBy=multi-user.target
   ```

3. **Enable and start:**
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable ce-controller
   sudo systemctl start ce-controller
   sudo systemctl status ce-controller
   ```

## TLS/SSL Configuration

### Option 1: Using Nginx as Reverse Proxy

1. **Install Nginx:**
   ```bash
   sudo apt install nginx certbot python3-certbot-nginx
   ```

2. **Create Nginx configuration:**
   ```nginx
   server {
       listen 80;
       server_name controller.yourdomain.com;
       return 301 https://$host$request_uri;
   }

   server {
       listen 443 ssl http2;
       server_name controller.yourdomain.com;

       ssl_certificate /etc/letsencrypt/live/controller.yourdomain.com/fullchain.pem;
       ssl_certificate_key /etc/letsencrypt/live/controller.yourdomain.com/privkey.pem;

       location / {
           proxy_pass http://localhost:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
       }
   }
   ```

3. **Get SSL certificate:**
   ```bash
   sudo certbot --nginx -d controller.yourdomain.com
   ```

### Option 2: Using Traefik (with Docker)

Add to `docker-compose.yml`:

```yaml
services:
  traefik:
    image: traefik:v2.10
    command:
      - "--providers.docker=true"
      - "--entrypoints.web.address=:80"
      - "--entrypoints.websecure.address=:443"
      - "--certificatesresolvers.letsencrypt.acme.email=admin@yourdomain.com"
      - "--certificatesresolvers.letsencrypt.acme.storage=/letsencrypt/acme.json"
      - "--certificatesresolvers.letsencrypt.acme.tlschallenge=true"
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
      - ./letsencrypt:/letsencrypt

  controller:
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.controller.rule=Host(`controller.yourdomain.com`)"
      - "traefik.http.routers.controller.entrypoints=websecure"
      - "traefik.http.routers.controller.tls.certresolver=letsencrypt"
```

## Database Management

### Backups

**PostgreSQL:**
```bash
# Backup
docker exec ce-postgres pg_dump -U ce_user ce_controller > backup.sql

# Restore
docker exec -i ce-postgres psql -U ce_user ce_controller < backup.sql
```

**SQLite:**
```bash
# Backup
cp ce_controller.db ce_controller.db.backup

# Restore
cp ce_controller.db.backup ce_controller.db
```

### Migrations

If using Alembic for database migrations:

```bash
# Create a new migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Rollback one version
alembic downgrade -1
```

## Monitoring

### Health Checks

```bash
curl http://localhost:8000/health
```

### Logs

**Docker:**
```bash
docker-compose logs -f controller
```

**Systemd:**
```bash
sudo journalctl -u ce-controller -f
```

## Security Best Practices

1. **Change default admin password immediately**
2. **Use strong SECRET_KEY** (generate with `openssl rand -hex 32`)
3. **Enable TLS/SSL** for all connections
4. **Restrict database access** to controller only
5. **Use firewall rules** to limit access to port 8000 (or expose only via reverse proxy)
6. **Regular security updates** for all dependencies
7. **Enable database encryption** at rest
8. **Use environment variables** or secret managers for sensitive data

## Troubleshooting

### Controller won't start

1. Check logs: `docker-compose logs controller`
2. Verify database connection
3. Ensure SECRET_KEY is set
4. Check port 8000 is not in use

### Database connection errors

1. Verify PostgreSQL is running: `docker-compose ps postgres`
2. Check DATABASE_URL is correct
3. Ensure database exists: `docker exec -it ce-postgres psql -U ce_user -l`

### Agents can't connect

1. Verify controller is accessible from agent network
2. Check firewall rules
3. Verify TLS certificate is valid (if using HTTPS)
4. Check controller logs for authentication errors

## Scaling

### Horizontal Scaling

Use a load balancer (e.g., HAProxy, Nginx) to distribute traffic across multiple controller instances:

```yaml
# docker-compose.yml
services:
  controller-1:
    build: .
    environment:
      DATABASE_URL: postgresql://ce_user:password@postgres:5432/ce_controller

  controller-2:
    build: .
    environment:
      DATABASE_URL: postgresql://ce_user:password@postgres:5432/ce_controller

  nginx:
    image: nginx:alpine
    ports:
      - "8000:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
```

### Database Scaling

- Use connection pooling
- Set up read replicas for reporting queries
- Consider using PgBouncer for connection management

## Maintenance

### Updating the Controller

1. **Pull latest code:**
   ```bash
   git pull origin main
   ```

2. **Rebuild and restart:**
   ```bash
   docker-compose down
   docker-compose build
   docker-compose up -d
   ```

3. **Verify health:**
   ```bash
   curl http://localhost:8000/health
   ```

### Cleaning Up Old Data

```sql
-- Delete reports older than 90 days
DELETE FROM reports WHERE timestamp < NOW() - INTERVAL '90 days';

-- Delete inactive agents (not seen in 30 days)
DELETE FROM agents WHERE last_seen < NOW() - INTERVAL '30 days';
```

## Support

For issues or questions:
- Check logs first
- Review API documentation at `/docs`
- File an issue in the GitHub repository
