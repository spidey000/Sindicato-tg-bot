# Deployment Files for Marxnager Bot

This directory contains configuration files and scripts for automated webhook deployment of the Marxnager Telegram bot.

## Files Overview

### Core Scripts

1. **update-marxnager.sh**
   - Bash script that triggers Portainer stack redeployment via API
   - Retrieves Portainer auth token and initiates stack redeploy
   - Must be configured with your Portainer credentials

2. **webhook-server.py**
   - Flask-based webhook server that receives GitHub webhooks
   - Validates webhook signatures for security
   - Executes the update script on push to main branch
   - Includes health check endpoint

3. **webhook-server.service**
   - Systemd service file for running the webhook server
   - Configured to auto-restart on failure
   - Includes security hardening options

### Documentation

4. **WEBHOOK_SETUP.md**
   - Quick start guide for webhook autodeploy setup
   - Covers both Portainer Business and Community Edition
   - Includes troubleshooting steps

## Quick Setup

### Option 1: Portainer Business (Easy)

Use native Portainer webhooks - see `WEBHOOK_SETUP.md`

### Option 2: Portainer Community (Custom Webhook)

```bash
# Copy files to VPS
scp deploy/* root@your-vps:/tmp/

# SSH to VPS and follow WEBHOOK_SETUP.md
ssh root@your-vps
```

See `WEBHOOK_SETUP.md` for detailed instructions.

## Configuration Required

### Before deploying, you must update:

**update-marxnager.sh:**
- `PORTAINER_URL` - Your Portainer URL
- `PORTAINER_USERNAME` - Your Portainer admin username
- `PORTAINER_PASSWORD` - Your Portainer admin password
- `ENDPOINT_ID` - Usually "1" for local environment
- `STACK_NAME` - Should match your Portainer stack name

**webhook-server.service:**
- `WEBHOOK_SECRET` - Generate with: `openssl rand -hex 32`
- Keep this secret - you'll need it for GitHub webhook configuration

## Security Notes

- Never commit secrets to git
- Use strong webhook secrets
- Keep Portainer credentials secure
- Consider using HTTPS in production (nginx reverse proxy)
- The webhook server validates GitHub signatures

## Testing

Test your setup:

```bash
# Test webhook server health
curl http://your-vps:5000/health

# Test update script manually
/usr/local/bin/update-marxnager.sh

# View webhook server logs
journalctl -u webhook-server -f
```

## Production Deployment

For production:

1. Use HTTPS with nginx reverse proxy
2. Set up log rotation
3. Monitor webhook success rate
4. Use environment-specific Portainer credentials
5. Consider using Portainer Business Edition for native webhooks

## Architecture

```
GitHub Push Event
       ↓
GitHub Webhook
       ↓
Your VPS (webhook-server.py :5000)
       ↓
Validates Signature
       ↓
Executes update-marxnager.sh
       ↓
Portainer API (/api/stacks/{id}/redeploy)
       ↓
Docker Container Rebuilds
       ↓
Bot Updated
```

## Support

- Main deployment guide: `../DEPLOYMENT.md`
- Quick setup guide: `WEBHOOK_SETUP.md`
- Project README: `../README.md`
