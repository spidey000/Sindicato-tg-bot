# Quick Start: Webhook Autodeploy for Marxnager Bot

This guide will help you set up automatic deployments when you push to GitHub.

## Prerequisites

- Portainer installed on your VPS
- GitHub repository with your bot code
- Basic knowledge of SSH and command line

## Option 1: Portainer Business Edition (Easiest)

If you have Portainer Business Edition, you get native webhooks for free:

### Steps:

1. **Create your stack in Portainer**
   - Stacks → Add stack
   - Use "Git Repository" as build method
   - Enter your repo URL: `https://github.com/your-username/Sindicato-tg-bot-1.git`
   - Deploy

2. **Get webhook URL**
   - Go to your stack → Editor tab
   - Copy the Webhook URL

3. **Add GitHub webhook**
   - GitHub → Settings → Webhooks → Add webhook
   - Paste the Portainer webhook URL
   - Select "Pushes" events
   - Add webhook

Done! Every push now auto-deploys.

---

## Option 2: Custom Webhook Server (Free Portainer)

For Portainer Community Edition, set up your own webhook handler.

### Step 1: Copy Files to VPS

```bash
# Copy the deployment files
scp deploy/update-marxnager.sh root@your-vps-ip:/tmp/
scp deploy/webhook-server.py root@your-vps-ip:/tmp/
scp deploy/webhook-server.service root@your-vps-ip:/tmp/
```

### Step 2: Install Dependencies

```bash
# SSH into your VPS
ssh root@your-vps-ip

# Install required packages
apt update
apt install -y python3-pip python3-flask jq

# Or if you prefer gunicorn (production-ready)
apt install -y python3-gunicorn
```

### Step 3: Configure and Deploy Scripts

```bash
# Move update script
mv /tmp/update-marxnager.sh /usr/local/bin/
chmod +x /usr/local/bin/update-marxnager.sh

# Edit the script with your Portainer credentials
nano /usr/local/bin/update-marxnager.sh

# Update these values:
# - PORTAINER_URL (usually http://localhost:9000)
# - PORTAINER_USERNAME
# - PORTAINER_PASSWORD
# - ENDPOINT_ID (check in Portainer URL, usually 1)
# - STACK_NAME (should be "marxnager-bot")

# Test the script
/usr/local/bin/update-marxnager.sh
```

### Step 4: Deploy Webhook Server

```bash
# Move webhook server
mv /tmp/webhook-server.py /opt/

# Generate webhook secret (use this in GitHub webhook setup)
WEBHOOK_SECRET=$(openssl rand -hex 32)
echo "Your webhook secret: $WEBHOOK_SECRET"

# Move systemd service file
mv /tmp/webhook-server.service /etc/systemd/system/

# Edit the service file with your secret
nano /etc/systemd/system/webhook-server.service

# Update this line with your generated secret:
# Environment="WEBHOOK_SECRET=<your-secret-here>"

# Reload systemd and start service
systemctl daemon-reload
systemctl enable webhook-server
systemctl start webhook-server

# Check it's running
systemctl status webhook-server
```

### Step 5: Configure Firewall

```bash
# Allow webhook port (default 5000)
ufw allow 5000/tcp
# or if using firewalld
firewall-cmd --permanent --add-port=5000/tcp
firewall-cmd --reload
```

### Step 6: Set Up GitHub Webhook

1. Go to your GitHub repository
2. Settings → Webhooks → Add webhook
3. Configure:
   - **Payload URL:** `http://your-vps-ip:5000/webhook`
   - **Content type:** `application/json`
   - **Secret:** Paste your webhook secret (generated in Step 4)
   - **Events:** Select "Pushes" and "Branch deletions"
4. Click "Add webhook"

### Step 7: Test It

```bash
# Test the webhook endpoint
curl -X POST http://your-vps-ip:5000/health

# Make a change to your code and push
git commit --allow-empty -m "test webhook"
git push origin main

# Check webhook server logs
journalctl -u webhook-server -f

# Check Portainer stack logs
# Portainer UI → Stacks → marxnager-bot → Logs
```

---

## Environment Variables for Webhook Server

You can configure the webhook server using environment variables in the systemd service file:

| Variable | Default | Description |
|----------|---------|-------------|
| `PORT` | `5000` | Port to listen on |
| `WEBHOOK_SECRET` | (required) | GitHub webhook secret |
| `UPDATE_SCRIPT` | `/usr/local/bin/update-marxnager.sh` | Path to update script |
| `LOG_FILE` | `/var/log/webhook-server.log` | Log file path |

---

## Troubleshooting

### Webhook server not starting

```bash
# Check status
systemctl status webhook-server

# View logs
journalctl -u webhook-server -n 50

# Check if port is already in use
ss -tlnp | grep 5000
```

### GitHub webhook failing

1. Check webhook deliveries in GitHub (Settings → Webhooks → Your webhook)
2. Test the webhook URL manually:
   ```bash
   curl -X POST http://your-vps-ip:5000/webhook \
     -H "Content-Type: application/json" \
     -d '{"test": true}'
   ```

### Portainer redeploy fails

```bash
# Test the update script manually
/usr/local/bin/update-marxnager.sh

# Check Portainer logs
docker logs marxnager-bot

# Verify Portainer credentials are correct
curl -X POST http://localhost:9000/api/auth \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"your-password"}'
```

### Firewall blocking connections

```bash
# Check firewall status
ufw status

# Allow the port
ufw allow 5000/tcp

# Or temporarily disable for testing
ufw disable  # ⚠️ Only for testing!
```

---

## Production Considerations

1. **Use HTTPS** (recommended for production):
   - Set up nginx as reverse proxy with SSL
   - Use Let's Encrypt for free certificates

2. **Security hardening**:
   - Use strong webhook secrets
   - Limit GitHub webhook to specific branches
   - Regular security updates

3. **Monitoring**:
   - Set up log rotation for webhook logs
   - Monitor webhook success rate
   - Alert on deployment failures

---

## Useful Commands

```bash
# View webhook server logs in real-time
journalctl -u webhook-server -f

# Restart webhook server
systemctl restart webhook-server

# Test update script manually
/usr/local/bin/update-marxnager.sh

# Check if webhook server is listening
ss -tlnp | grep 5000

# View recent GitHub webhook deliveries
# (In GitHub UI: Settings → Webhooks → Your webhook → Recent Deliveries)
```

---

## Need Help?

- Check the main deployment guide: `DEPLOYMENT.md`
- Review webhook server logs: `journalctl -u webhook-server -n 100`
- Test your webhook setup using GitHub's "Redeliver" feature
