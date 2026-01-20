# Deployment Guide: Marxnager Bot

This guide explains how to deploy the Marxnager bot on a VPS using Docker and Portainer.

## Prerequisites

- A VPS with Docker and Docker Compose installed
- Portainer installed and accessible (optional but recommended)
- A Telegram Bot Token from @BotFather
- API keys for Notion, Google Workspace, OpenRouter, and Perplexity

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

**Last Updated:** 2026-01-20
**Documentation Version:** 2.0
