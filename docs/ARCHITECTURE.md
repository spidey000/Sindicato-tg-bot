# Webhook Deployment Architecture

## Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                         DEVELOPMENT WORKSTATION                      │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    │ git push
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│                          GITHUB REPOSITORY                           │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │ Webhook Configuration                                         │  │
│  │ - Payload URL: http://your-vps:5000/webhook                   │  │
│  │ - Secret: <your-webhook-secret>                               │  │
│  │ - Events: Push, Branch deletions                              │  │
│  └──────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    │ HTTP POST (webhook)
                                    │ X-Hub-Signature-256: <signature>
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         YOUR VPS (Portainer)                         │
│                                                                      │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │          webhook-server.py (Flask on port 5000)              │   │
│  │  ┌───────────────────────────────────────────────────────┐  │   │
│  │  │ 1. Verify GitHub signature                             │  │   │
│  │  │ 2. Parse webhook event (push/ping/etc)                 │  │   │
│  │  │ 3. Check if push to main branch                        │  │   │
│  │  │ 4. Trigger update script                               │  │   │
│  │  └───────────────────────────────────────────────────────┘  │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                              │                                       │
│                              │ subprocess.run()                      │
│                              ▼                                       │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │        update-marxnager.sh (Bash script)                     │   │
│  │  ┌───────────────────────────────────────────────────────┐  │   │
│  │  │ 1. Authenticate with Portainer API                     │  │   │
│  │  │ 2. Get stack ID for "marxnager-bot"                    │  │   │
│  │  │ 3. Trigger stack redeployment                          │  │   │
│  │  └───────────────────────────────────────────────────────┘  │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                              │                                       │
│                              │ Portainer API                         │
│                              ▼                                       │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                   PORTAINER STACK                            │   │
│  │  ┌───────────────────────────────────────────────────────┐  │   │
│  │  │ Stack: marxnager-bot                                   │  │   │
│  │  │ - Pulls latest from Git / Uses compose config         │  │   │
│  │  │ - Builds Docker image                                 │  │   │
│  │  │ - Stops old container                                 │  │   │
│  │  │ - Starts new container                                │  │   │
│  │  └───────────────────────────────────────────────────────┘  │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                              │                                       │
│                              ▼                                       │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │              DOCKER CONTAINER (marxnager-bot)                │   │
│  │  - Python 3.11-slim                                          │   │
│  │  - Telegram bot (python-telegram-bot)                        │   │
│  │  - Integrations: Notion, Google Drive/Docs, OpenRouter      │   │
│  │  - Environment variables from Portainer                      │   │
│  └─────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
```

## Component Details

### 1. GitHub Webhook
**Purpose**: Notify your VPS when code changes

**Configuration**:
- URL: `http://your-vps-ip:5000/webhook`
- Content Type: `application/json`
- Secret: Generated secret (e.g., `openssl rand -hex 32`)
- Events: `push`, `delete`

**Payload Example**:
```json
{
  "ref": "refs/heads/main",
  "repository": {
    "name": "Sindicato-tg-bot-1",
    "full_name": "your-username/Sindicato-tg-bot-1"
  },
  "pusher": {
    "name": "developer"
  },
  "sender": {
    "login": "developer"
  }
}
```

### 2. webhook-server.py (Flask)
**Purpose**: Receive GitHub webhooks and trigger deployment

**Endpoints**:
- `POST /webhook` - GitHub webhook endpoint
- `GET /health` - Health check
- `GET /` - Service information

**Security**:
- Verifies HMAC-SHA256 signatures
- Only processes pushes to main branch
- Configurable webhook secret

**Dependencies**:
- `python3-flask`
- `systemd` (for service management)

### 3. update-marxnager.sh (Bash)
**Purpose**: Trigger Portainer stack redeployment via API

**Steps**:
1. Authenticate with Portainer
2. Retrieve JWT token
3. Find stack ID by name
4. Call redeploy endpoint

**Required Configuration**:
```bash
PORTAINER_URL="http://localhost:9000"
PORTAINER_USERNAME="admin"
PORTAINER_PASSWORD="your-password"
ENDPOINT_ID="1"
STACK_NAME="marxnager-bot"
```

### 4. Portainer Stack
**Purpose**: Orchestrate Docker deployment

**Two Configuration Methods**:

**Method A: Git Repository (Business Edition)**
```yaml
Repository URL: https://github.com/your-username/Sindicato-tg-bot-1.git
Branch: main
Compose Path: docker-compose.yml
```

**Method B: Web Editor (Community Edition)**
- Paste `docker-compose.yml` content
- Manually update when needed

**Environment Variables**:
```yaml
BOT_TOKEN=your_bot_token
AUTHORIZED_USER_IDS=id1,id2,id3
OPENROUTER_API_KEY=your_key
PERPLEXITY_API_KEY_PRIMARY=your_key
NOTION_TOKEN=your_token
NOTION_DATABASE_ID=your_id
DRIVE_FOLDER_DENUNCIAS=your_folder_id
DRIVE_FOLDER_DEMANDAS=your_folder_id
DRIVE_FOLDER_EMAILS=your_folder_id
ADMIN_EMAIL=your_email
```

### 5. Docker Container
**Purpose**: Run the Telegram bot

**Base Image**: `python:3.11-slim`

**Key Components**:
- `src/main.py` - Entry point
- `src/handlers.py` - Telegram command handlers
- `src/agents/orchestrator.py` - AI orchestration
- `src/integrations/` - External API clients

**Volumes**:
- `/app/logs` - Persistent logs

**Restart Policy**: `unless-stopped`

## Security Considerations

### 1. Webhook Security
- ✅ HMAC-SHA256 signature verification
- ✅ Only accept webhooks from GitHub
- ✅ Use strong, random secrets
- ⚠️ Consider using HTTPS in production

### 2. Portainer Security
- ✅ Use strong admin password
- ✅ Restrict Portainer to local/private network
- ✅ Use environment variables for secrets
- ⚠️ Don't expose Portainer to public internet

### 3. Container Security
- ✅ Run as non-root user (`marxnager`)
- ✅ Minimal base image (slim)
- ✅ No unnecessary packages
- ✅ Read-only root filesystem (optional)

## Monitoring & Logging

### Log Locations

**Webhook Server**:
```bash
journalctl -u webhook-server -f
```

**Portainer Stack**:
```bash
# Via Portainer UI
# Or via CLI:
docker logs -f marxnager-bot
```

**Docker Logs**:
```bash
# Follow logs
docker logs -f marxnager-bot

# Last 100 lines
docker logs --tail 100 marxnager-bot

# With timestamps
docker logs -t marxnager-bot
```

### Health Checks

**Webhook Server**:
```bash
curl http://localhost:5000/health
```

**Expected Response**:
```json
{
  "status": "healthy",
  "update_script": "/usr/local/bin/update-marxnager.sh",
  "script_exists": true
}
```

**Container Status**:
```bash
docker ps | grep marxnager-bot
# Should show: "Up X minutes"
```

## Performance Considerations

### Typical Timeline (From Push to Deployed)

| Step | Time | Notes |
|------|------|-------|
| Git push | 1-2s | GitHub processing |
| Webhook delivery | <1s | Network latency |
| Signature verification | <1s | Server processing |
| Portainer API call | 1-2s | Authentication + trigger |
| Docker build | 30-60s | Depends on dependencies |
| Container restart | 5-10s | Stop old, start new |
| Bot ready | 2-5s | Python startup + Telegram connection |
| **Total** | **~40-80s** | From push to operational |

### Optimization Tips

1. **Use Docker build cache** - Dependencies don't change often
2. **Minimize layers** - Combined RUN commands in Dockerfile
3. **Use .dockerignore** - Exclude unnecessary files
4. **Consider pre-built images** - Push to Docker Hub, pull instead of build

## Failure Recovery

### Automatic Recovery
- Webhook server auto-restarts (systemd)
- Container auto-restarts (Docker restart policy)
- Failed webhook deliveries can be redelivered (GitHub UI)

### Manual Recovery
```bash
# Restart webhook server
systemctl restart webhook-server

# Redeploy stack manually
/usr/local/bin/update-marxnager.sh

# Restart container
docker restart marxnager-bot

# Check logs for errors
journalctl -u webhook-server -n 50
docker logs marxnager-bot --tail 50
```

## Advanced: HTTPS with nginx (Production)

For production, add nginx as a reverse proxy:

```nginx
server {
    listen 443 ssl http2;
    server_name your-domain.com;

    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;

    location /webhook {
        proxy_pass http://localhost:5000/webhook;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /health {
        proxy_pass http://localhost:5000/health;
    }
}
```

Then update GitHub webhook URL to: `https://your-domain.com/webhook`
