# Deployment Guide: Marxnager Bot

This guide explains how to deploy the Marxnager bot on a VPS using Docker and Portainer, including automated webhook deployment.

## Prerequisites

- A VPS with Docker and Docker Compose installed
- Portainer installed and accessible (optional but recommended)
- A Telegram Bot Token from @BotFather
- API keys for Notion, Google Workspace, OpenRouter, and Perplexity
- GitHub repository with your bot code (for webhook autodeploy)

## Setup Guides

**Before deploying**, you need to configure the required services. Follow these step-by-step guides:

1. **[Notion Setup Guide](NOTION_SETUP.md)** - Create database, configure integration, get API token
2. **[Google Setup Guide](GOOGLE_SETUP.md)** - Create service account, configure Drive/Docs APIs, set up folders
3. **[Supabase Setup Guide](SUPABASE_SETUP.md)** (Optional) - For multi-user profile system and event logging

These guides provide detailed instructions with screenshots and troubleshooting for each service integration.

## Quick Start (Summary)

### 1. Configure Services

**Notion:**
- Create integration at https://www.notion.so/my-integrations
- Create database with properties: Case ID, Type, Description, Status, Created Date, Google Doc, Drive Folder, Delegate
- Share database with integration
- Copy NOTION_TOKEN and NOTION_DATABASE_ID

**Google Workspace:**
- Create service account in Google Cloud Console
- Enable Drive API and Docs API
- Create and download JSON key file
- Create folder structure: Denuncias/, Demandas/, Emails/
- Share folders with service account email
- Copy folder IDs for DRIVE_FOLDER_DENUNCIAS, DRIVE_FOLDER_DEMANDAS, DRIVE_FOLDER_EMAILS

**Supabase (Optional):**
- Create project at https://supabase.com
- Run migrations from `supabase/migrations/`
- Copy SUPABASE_URL and SUPABASE_KEY (service_role)

### 2. Configure Environment Variables

Create a `.env` file with all required variables:

```bash
# Telegram Configuration
BOT_TOKEN=<your_bot_token_from_botfather>
AUTHORIZED_USER_IDS=<comma_separated_telegram_user_ids>

# Notion Configuration
NOTION_TOKEN=secret_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
NOTION_DATABASE_ID=1a2b3c4d5e6f7g8h9i0j1k2l3m4n5o6p

# Google Workspace Configuration
GOOGLE_CREDENTIALS_PATH=/app/config/google_credentials.json
DRIVE_FOLDER_DENUNCIAS=<folder_id_1>
DRIVE_FOLDER_DEMANDAS=<folder_id_2>
DRIVE_FOLDER_EMAILS=<folder_id_3>

# AI Services Configuration
OPENROUTER_API_KEY=sk-or-v1-xxxxxxxxxxxxxxxxxxxxxxxxxxxx
PERPLEXITY_API_KEY_PRIMARY=pplx-xxxxxxxxxxxxxxxxxxxxxxxxxxxx
PERPLEXITY_API_KEY_FALLBACK=pplx-xxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Supabase Configuration (Optional)
SUPABASE_URL=https://xxxxxxxxxxxxx.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# Administrative
ADMIN_EMAIL=your_email@example.com
LOG_LEVEL=INFO
SAVE_RAW_LLM_RESPONSES=False
```

### 3. Deploy

Choose one of the following deployment methods:

## Deployment via Portainer (Stacks)

**Recommended for production deployments with GUI management.**

1. **Log in** to your Portainer instance
2. **Navigate** to the environment where you want to deploy (e.g., `local`)
3. **Click on "Stacks"** in the left sidebar
4. **Click "+ Add stack"**
5. **Name your stack** (e.g., `marxnager-bot`)
6. **Build method:** Choose "Upload from git" or "Web editor"
   - **Git:** Clone repository URL
   - **Web editor:** Paste content of `docker-compose.yml`
7. **Environment variables:**
   - Click "Add environment variable" for each variable
   - Or use "Advanced mode" to paste the entire list from Step 2
8. **Volumes/Secrets:**
   - Mount `google_credentials.json` to `/app/config/google_credentials.json:ro`
   - Or use Docker secrets for production
9. **Click "Deploy the stack"**
10. **Verify deployment:** Check container logs for initialization messages

## Local Docker Deployment (Manual)

**Good for development and testing.**

1. **Clone repository:**
   ```bash
   git clone https://github.com/spidey000/Sindicato-tg-bot.git
   cd Sindicato-tg-bot
   ```

2. **Create .env file:**
   ```bash
   cp .env.example .env
   nano .env
   # Add your configuration from Step 2
   ```

3. **Set up Google credentials:**
   ```bash
   mkdir -p config
   # Copy your google_credentials.json to config/
   chmod 600 config/google_credentials.json
   ```

4. **Build and run:**
   ```bash
   docker-compose up -d --build
   ```

5. **Check logs:**
   ```bash
   docker-compose logs -f
   ```

## Deployment via Docker Compose (CLI)

**For production servers without Portainer.**

1. **Clone repository:**
   ```bash
   git clone https://github.com/spidey000/Sindicato-tg-bot.git
   cd Sindicato-tg-bot
   ```

2. **Configure environment:**
   ```bash
   cp .env.example .env
   nano .env
   # Add all required variables
   ```

3. **Set up credentials:**
   ```bash
   mkdir -p config
   # Copy google_credentials.json to config/
   chmod 600 config/google_credentials.json
   ```

4. **Deploy:**
   ```bash
   docker-compose up -d --build
   ```

5. **Verify:**
   ```bash
   docker-compose ps
   docker-compose logs -f --tail=100
   ```

---

## Webhook Autodeploy Setup (Recommended)

This setup enables automatic redeployment when you push changes to your GitHub repository.

### Step 1: Initial Portainer Stack Setup

1. **Log in** to your Portainer instance
2. **Navigate** to your environment (e.g., `local`)
3. **Click "Stacks"** in the left sidebar
4. **Click "+ Add stack"**
5. **Name your stack** (e.g., `marxnager-bot`)
6. **Build method:** Choose "Git Repository" (if available) or "Web editor"

#### Option A: Using Git Repository (Recommended for Portainer Business)
   - **Repository URL:** `https://github.com/your-username/Sindicato-tg-bot-1.git`
   - **Git Branch:** `main` (or your default branch)
   - **Compose Path:** `docker-compose.yml`
   - **Authentication:** Add your GitHub credentials if private repo

#### Option B: Using Web Editor (Free Portainer)
   - **Paste the content** of `docker-compose.yml` into the editor
   - **Note:** You'll need to manually update the stack when pulling changes (see Step 3)

7. **Add environment variables** (same as listed above)
8. **Click "Deploy the stack"**

### Step 2: Get the Portainer Webhook URL

1. **Go to** Stacks -> marxnager-bot
2. **Click on** "Editor" or "Settings" tab
3. **Look for** "Webhook" section
4. **Copy the webhook URL** (looks like: `https://your-portainer-url/api/stacks/webhooks/<uuid>`)

**Note:** Webhooks are available in Portainer Business Edition. For Community Edition, use Option B below.

### Step 3: Configure GitHub Webhook

#### Option A: Using Portainer Webhook (Business Edition)

1. **Go to** your GitHub repository -> Settings -> Webhooks
2. **Click "Add webhook"**
3. **Payload URL:** Paste your Portainer webhook URL
4. **Content type:** `application/json`
5. **Secret:** (Optional but recommended) Create a random secret
   - Generate one with: `openssl rand -hex 32`
   - Save it for later configuration
6. **Events:** Choose "Let me select individual events"
   - Select: "Pushes" and "Branch deletions"
7. **Active:** Checked
8. **Click "Add webhook"**

Now every push to your repository will trigger automatic redeployment!

#### Option B: Custom Webhook Handler (Community Edition)

If using Portainer Community Edition, set up a custom webhook handler:

1. **Create a webhook handler script** on your VPS:

```bash
# Create the webhook script
sudo nano /usr/local/bin/update-marxnager.sh
```

2. **Add this content** (replace with your details):

```bash
#!/bin/bash
# Auto-deploy webhook for Marxnager Bot

# Configuration
STACK_NAME="marxnager-bot"
PORTAINER_URL="http://localhost:9000"  # or your Portainer URL
PORTAINER_USERNAME="admin"
PORTAINER_PASSWORD="your-password"
ENDPOINT_ID="1"  # Check in Portainer URL

# Get authentication token
TOKEN=$(curl -s -X POST "$PORTAINER_URL/api/auth" \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"$PORTAINER_USERNAME\",\"password\":\"$PORTAINER_PASSWORD\"}" \
  | jq -r '.jwt')

# Get stack ID
STACK_ID=$(curl -s -X GET "$PORTAINER_URL/api/stacks" \
  -H "Authorization: Bearer $TOKEN" \
  | jq -r ".[] | select(.Name==\"$STACK_NAME\") | .Id")

# Redeploy stack
curl -X POST "$PORTAINER_URL/api/stacks/$STACK_ID/redeploy?endpointId=$ENDPOINT_ID" \
  -H "Authorization: Bearer $TOKEN"

echo "Redeploy triggered for $STACK_NAME"
```

3. **Make it executable:**
```bash
sudo chmod +x /usr/local/bin/update-marxnager.sh
```

4. **Set up a simple webhook server** using Python:

```bash
# Install dependencies
sudo apt install python3-flask python3-gunicorn -y

# Create webhook server
sudo nano /opt/webhook-server.py
```

```python
from flask import Flask, request, jsonify
import subprocess
import hmac
import hashlib

app = Flask(__name__)

# Configure these
WEBHOOK_SECRET = b'your-github-webhook-secret'  # Same as in GitHub webhook settings
UPDATE_SCRIPT = '/usr/local/bin/update-marxnager.sh'

@app.route('/webhook', methods=['POST'])
def webhook():
    # Verify webhook signature
    signature = request.headers.get('X-Hub-Signature-256')
    if signature:
        sha_name, signature = signature.split('=')
        if sha_name != 'sha256':
            return '', 501

        mac = hmac.new(WEBHOOK_SECRET, request.data, hashlib.sha256)
        if not hmac.compare_digest(mac.hexdigest(), signature):
            return '', 403

    # Trigger update script
    try:
        subprocess.run([UPDATE_SCRIPT], check=True)
        return jsonify({'status': 'success'}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```

5. **Create a systemd service** for the webhook server:

```bash
sudo nano /etc/systemd/system/webhook-server.service
```

```ini
[Unit]
Description=Webhook Auto-Deploy Server
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt
ExecStart=/usr/bin/python3 /opt/webhook-server.py
Restart=always

[Install]
WantedBy=multi-user.target
```

6. **Enable and start** the service:

```bash
sudo systemctl daemon-reload
sudo systemctl enable webhook-server
sudo systemctl start webhook-server
sudo systemctl status webhook-server
```

7. **Set up GitHub webhook** (if not done already):
   - Go to repository Settings -> Webhooks -> Add webhook
   - Payload URL: `http://your-vps-ip:5000/webhook`
   - Secret: Same as `WEBHOOK_SECRET` in the script
   - Events: Pushes, Branch deletions
   - Click "Add webhook"

### Step 4: Test Your Webhook

1. **Make a small change** to your code (e.g., update a comment)
2. **Commit and push** to GitHub:
   ```bash
   git add .
   git commit -m "test webhook deployment"
   git push origin main
   ```
3. **Check GitHub webhook delivery:**
   - Go to repository Settings -> Webhooks
   - Click on your webhook
   - Check recent deliveries for status 200

4. **Verify deployment in Portainer:**
   - Go to Stacks -> marxnager-bot
   - Check the "Logs" section
   - You should see the container rebuilding

### Step 5: Verify Your Bot

1. **Check container status:**
   - In Portainer: Containers -> marxnager-bot -> Should be "Running"
   - Via CLI: `docker ps | grep marxnager-bot`

2. **Test the bot:**
   - Open Telegram
   - Start a conversation with your bot
   - Send `/start` command

---

## Monitoring Logs

### Via Portainer

1. Go to **Stacks** → **marxnager-bot**
2. Click on **Containers** → **marxnager-bot**
3. Click **Logs** tab
4. Select output type: **Stdout** + **Stderr**

### Via CLI

```bash
# Follow logs in real-time
docker-compose logs -f

# Last 100 lines
docker-compose logs --tail=100

# Filter by service
docker-compose logs | grep -i "notion\|drive\|docs"

# Check for errors
docker-compose logs | grep -i "error\|failed"
```

### Webhook Server Logs (if autodeploy is configured)

```bash
# Follow webhook server logs
sudo journalctl -u webhook-server -f

# Last 100 lines
sudo journalctl -u webhook-server -n 100

# Check for webhook events
sudo journalctl -u webhook-server | grep "Received webhook"
```

### Important Log Messages

**Successful startup:**
```
✅ Notion client initialized successfully
✅ Google Drive client initialized successfully
✅ Google Docs client initialized successfully
✅ Supabase client initialized successfully (if enabled)
✅ Marxnager bot started successfully
```

**Common errors:**
```
❌ Notion client not initialized - Check NOTION_TOKEN and NOTION_DATABASE_ID
❌ Google credentials not found - Check GOOGLE_CREDENTIALS_PATH and file mount
❌ Supabase not enabled - This is OK if you don't need multi-user support
```

## Verification Checklist

After deployment, verify the following:

- [ ] Container is running: `docker-compose ps` shows "Up"
- [ ] No errors in logs: Check for ❌ symbols
- [ ] Bot responds to `/start` command in Telegram
- [ ] Bot responds to `/metrics` command with API status
- [ ] Notion database is accessible: Generate test document with `/denuncia Test`
- [ ] Google Drive folders are created: Check Drive after test document
- [ ] Google Docs are created: Open document link from Notion
- [ ] Profile system works (if Supabase enabled): `/profile create`

## Updating the Bot

### Via Portainer

1. Go to **Stacks** → **marxnager-bot**
2. Click **Editor**
3. Click **Update the stack**
4. Select **Pull latest image** or **Rebuild**
5. Click **Update**

### Via CLI

```bash
# Pull latest code
git pull origin main

# Rebuild and restart
docker-compose down
docker-compose up -d --build

# Or just restart (no code changes)
docker-compose restart
```

## Backup and Recovery

### Backup Configuration

```bash
# Backup .env file
cp .env .env.backup

# Backup Google credentials
cp config/google_credentials.json config/google_credentials.json.backup

# Backup Notion database
# Export from Notion UI (File → Export)

# Backup Supabase (if enabled)
# Use Supabase Dashboard → Database → Backups
```

### Recovery

```bash
# Restore from backup
cp .env.backup .env
cp config/google_credentials.json.backup config/google_credentials.json

# Restart bot
docker-compose restart
```

## Troubleshooting

### Container Won't Start

**Symptoms:** `docker-compose ps` shows "Exit 1" or restarting

**Solutions:**
1. Check logs: `docker-compose logs`
2. Verify .env file has all required variables
3. Verify google_credentials.json exists and is readable
4. Check for port conflicts (default is no ports exposed)

### Bot Not Responding

**Symptoms:** Container running but no response in Telegram

**Solutions:**
1. Check logs: `docker-compose logs | grep -i error`
2. Verify BOT_TOKEN is correct
3. Verify AUTHORIZED_USER_IDS includes your Telegram user ID
4. Check if bot is blocked by Telegram (send /start to @BotFather)
5. Verify network connectivity: `docker-compose exec bot ping api.telegram.org`

### Notion Integration Failing

**Symptoms:** "Object not found" or "Unauthorized" in logs

**Solutions:**
1. Verify NOTION_TOKEN is correct and not expired
2. Verify NOTION_DATABASE_ID is correct
3. Check integration has access to database (see NOTION_SETUP.md)
4. Test integration manually using Notion API docs

### Google Integration Failing

**Symptoms:** "File not found" or "Access denied" in logs

**Solutions:**
1. Verify google_credentials.json exists and is mounted correctly
2. Check service account has Drive/Docs APIs enabled
3. Verify folder IDs are correct and folders are shared
4. Test service account manually using Google APIs Explorer

### LLM Integration Failing

**Symptoms:** Document generation hangs or times out

**Solutions:**
1. Check OPENROUTER_API_KEY is valid
2. Check PERPLEXITY_API_KEY_PRIMARY is valid
3. Verify API keys have credits/quota available
4. Check logs for specific error messages
5. Test API keys manually using curl or Postman

### Webhook Autodeploy Not Working

**Symptoms:** Pushing to GitHub doesn't trigger redeployment

**Solutions:**

**Webhook not triggering:**
1. Check GitHub webhook delivery status in Settings → Webhooks
2. Verify your VPS firewall allows port 5000 (or your webhook port)
3. Test the webhook URL manually:
   ```bash
   curl -X POST http://your-vps-ip:5000/webhook -d '{"test": true}'
   ```

**Deployment fails:**
1. Check Portainer logs for the stack
2. Verify environment variables are correctly set
3. Test the update script manually:
   ```bash
   sudo /usr/local/bin/update-marxnager.sh
   ```

**Webhook server not running:**
1. Check webhook server status:
   ```bash
   sudo systemctl status webhook-server
   ```
2. View webhook server logs:
   ```bash
   sudo journalctl -u webhook-server -n 50
   ```
3. Restart webhook server:
   ```bash
   sudo systemctl restart webhook-server
   ```

For more webhook troubleshooting, see `deploy/WEBHOOK_SETUP.md`.

## Production Best Practices

### Security

1. **Use Docker Secrets** instead of environment variables for sensitive data:
   ```bash
   echo "your_secret" | docker secret create notion_token -
   ```

2. **Limit Container Privileges:**
   - Run as non-root user (if supported)
   - Use read-only filesystem where possible
   - Limit container resources (CPU, memory)

3. **Network Isolation:**
   - Use Docker networks to isolate services
   - Don't expose unnecessary ports
   - Use firewall rules to restrict access

4. **Secret Rotation:**
   - Rotate API keys regularly (monthly recommended)
   - Rotate bot tokens if compromised
   - Update .env and restart after rotation

### Monitoring

1. **Health Checks:**
   - Container has built-in health check
   - Monitor via Portainer or `docker ps`
   - Set up alerts for container restarts

2. **Log Aggregation:**
   - Use Docker logging drivers (syslog, journald)
   - Send logs to centralized logging (ELK, Splunk)
   - Monitor for error patterns

3. **Metrics:**
   - Use `/metrics` command regularly
   - Monitor API success rates
   - Track latency and error rates
   - Set up alerts for high failure rates

### High Availability

1. **Container Restart Policy:**
   - `restart: unless-stopped` in docker-compose.yml
   - Automatic restart on failure
   - Survives server reboots

2. **Database Backups:**
   - Export Notion database weekly
   - Backup Supabase daily (if enabled)
   - Store backups in separate location

3. **Graceful Shutdown:**
   - Container handles SIGTERM gracefully
   - In-flight operations complete before shutdown
   - No data loss on restart

## Performance Tuning

### Container Resources

```yaml
# In docker-compose.yml
services:
  bot:
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 1G
        reservations:
          cpus: '0.5'
          memory: 512M
```

### API Rate Limits

- Notion: 3 requests/second (handled by retry logic)
- Google Drive: 100 requests/100 seconds (handled by retry logic)
- OpenRouter: Depends on plan (handled by retry logic)
- Perplexity: Depends on plan (handled by retry logic)

### Database Optimization

- Use filtered views in Notion for faster queries
- Index Supabase tables on frequently queried columns
- Cache frequently accessed data (user profiles, etc.)

## Scaling Considerations

### Horizontal Scaling

For high-volume deployments (100+ delegates):

1. **Load Balancing:**
   - Use Telegram's webhook mode instead of polling
   - Configure multiple bot instances behind load balancer
   - Shared Redis for session storage (planned feature)

2. **Database Optimization:**
   - Use Supabase for all data (not just profiles)
   - Implement proper indexing
   - Use connection pooling

3. **Caching:**
   - Cache user profiles (already implemented)
   - Cache template data
   - Use Redis for distributed caching

### Vertical Scaling

For medium deployments (20-100 delegates):

- Increase container memory/CPU limits
- Use faster disk I/O for database
- Optimize LLM prompt sizes

## Cost Estimation

### Infrastructure Costs (Monthly)

- **VPS:** $5-20/month (DigitalOcean, Linode, Hetzner)
- **Notion:** Free tier sufficient for <1000 cases
- **Google Workspace:** Free tier sufficient for <10K API calls/month
- **OpenRouter:** $0.10-1/month depending on usage (DeepSeek R1: $1/1M tokens)
- **Perplexity:** $5-20/month (sonar-pro: $1/1M tokens)
- **Supabase:** Free tier sufficient for <500MB database

**Total:** $10-50/month for typical deployment (20 delegates)

### Time Investment

- **Initial Setup:** 2-4 hours (following setup guides)
- **Maintenance:** 1-2 hours/month (updates, monitoring)
- **Support:** 1-2 hours/week (user questions, issues)

## Next Steps

After successful deployment:

1. **Test All Features:**
   - Generate denuncia: `/denuncia Test deployment`
   - Generate demanda: `/demanda Test judicial`
   - Generate email: `/email Test corporate`
   - Update status: `/status D-2026-001 presentada`
   - List active cases: `/update`
   - View metrics: `/metrics`

2. **Create User Profiles** (if Supabase enabled):
   - `/profile create` for each delegate
   - Test profile injection in documents

3. **Set Up Monitoring:**
   - Schedule regular `/metrics` checks
   - Set up log aggregation
   - Configure alerts for failures

4. **Train Users:**
   - Share quick start guide with delegates
   - Provide Telegram bot username
   - Explain available commands
   - Share troubleshooting tips

## Support and Resources

### Documentation

- **[README.md](README.md)** - Project overview and quick start
- **[NOTION_SETUP.md](NOTION_SETUP.md)** - Notion integration guide
- **[GOOGLE_SETUP.md](GOOGLE_SETUP.md)** - Google Workspace setup guide
- **[SUPABASE_SETUP.md](SUPABASE_SETUP.md)** - Supabase integration guide
- **[TESTING_CHECKLIST.md](TESTING_CHECKLIST.md)** - Comprehensive testing guide
- **[@fix_plan.md](@fix_plan.md)** - Development roadmap and known issues

### External Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Portainer Documentation](https://docs.portainer.io/)
- [Telegram Bot API](https://core.telegram.org/bots/api)
- [python-telegram-bot Documentation](https://python-telegram-bot.readthedocs.io/)

### Getting Help

If you encounter issues:

1. **Check logs:** `docker-compose logs -f`
2. **Review troubleshooting sections** in setup guides
3. **Check @fix_plan.md** for known issues and workarounds
4. **Review GitHub issues** (if public)
5. **Contact system administrator** for deployment-specific issues

## Changelog

### 2026-01-20

- Added comprehensive setup guides (Notion, Google, Supabase)
- Enhanced troubleshooting section
- Added monitoring and verification checklist
- Added production best practices
- Added cost estimation and scaling considerations

### Previous Versions

See [CHANGELOG.md](CHANGELOG.md) for full version history.

---

**Last Updated:** 2026-01-21
**Documentation Version:** 2.1
