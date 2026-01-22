# 🚀 Webhook Autodeploy - Quick Summary

This document provides a quick overview of webhook autodeploy setup for your Telegram bot.

## 📋 What You Need

### Prerequisites
- ✅ VPS with Docker and Portainer installed
- ✅ GitHub repository with your bot code
- ✅ Bot already deployed in Portainer

### Time Investment
- **Portainer Business Edition**: ~15 minutes
- **Portainer Community Edition**: ~30-45 minutes

---

## 🎯 Two Ways to Set Up

### Method 1: Portainer Business (Recommended - Easiest)

**Steps:**
1. Create stack using "Git Repository" method
2. Copy webhook URL from stack settings
3. Add webhook in GitHub repository settings
4. Done! 🎉

**See**: `WEBHOOK_SETUP.md` → "Option 1"

### Method 2: Portainer Community (Free - Custom Webhook)

**Steps:**
1. Copy deployment files to VPS (`/tmp/`)
2. Install dependencies: `python3-flask`, `jq`
3. Configure and deploy `update-marxnager.sh`
4. Deploy and start `webhook-server.py` as systemd service
5. Configure GitHub webhook
6. Test with a git push

**See**: `WEBHOOK_SETUP.md` → "Option 2"

---

## 📁 Files Created

All files are in the `deploy/` directory:

| File | Purpose |
|------|---------|
| `WEBHOOK_SETUP.md` | Quick start guide (START HERE!) |
| `update-marxnager.sh` | Triggers Portainer redeploy |
| `webhook-server.py` | Flask webhook receiver |
| `webhook-server.service` | Systemd service config |
| `ARCHITECTURE.md` | Detailed architecture diagram |
| `README.md` | Overview of deployment files |

---

## ⚡ Quick Start (Business Edition)

1. **Portainer** → Stacks → Add stack
2. Choose "Git Repository"
3. Enter repo: `https://github.com/your-username/Sindicato-tg-bot-1.git`
4. Deploy
5. Copy webhook URL from stack settings
6. **GitHub** → Settings → Webhooks → Add webhook
7. Paste webhook URL, select "Pushes"
8. Add webhook

✅ Done! Every push now auto-deploys.

---

## ⚙️ Configuration Values Needed

### For update-marxnager.sh:
```bash
PORTAINER_URL="http://localhost:9000"      # Your Portainer URL
PORTAINER_USERNAME="admin"                  # Your username
PORTAINER_PASSWORD="your-password"          # Your password
ENDPOINT_ID="1"                             # Usually 1
STACK_NAME="marxnager-bot"                  # Your stack name
```

### For webhook-server.service:
```bash
WEBHOOK_SECRET=$(openssl rand -hex 32)      # Generate and save this!
```

### For GitHub Webhook:
```
URL: http://your-vps-ip:5000/webhook
Secret: <same as WEBHOOK_SECRET above>
Events: Pushes, Branch deletions
```

---

## 🧪 Testing Your Setup

### 1. Test webhook server health:
```bash
curl http://your-vps-ip:5000/health
```

### 2. Test deployment script:
```bash
/usr/local/bin/update-marxnager.sh
```

### 3. Make a test commit:
```bash
git commit --allow-empty -m "test webhook deployment"
git push origin main
```

### 4. Check logs:
```bash
# Webhook server logs
journalctl -u webhook-server -f

# Container logs
docker logs -f marxnager-bot
```

---

## 🔍 Troubleshooting

### Webhook not triggering?
- Check GitHub webhook delivery status
- Verify VPS firewall allows port 5000
- Test webhook URL manually:
  ```bash
  curl -X POST http://your-vps:5000/webhook -d '{"test":true}'
  ```

### Deployment fails?
- Check Portainer logs in UI
- Test script manually: `/usr/local/bin/update-marxnager.sh`
- Verify environment variables are set

### Container won't start?
- Check logs: `docker logs marxnager-bot`
- Verify all required env vars in Portainer
- Ensure stack name matches script

---

## 📚 Documentation Guide

| You want to... | Read this file |
|----------------|----------------|
| Set up webhook quickly | `deploy/WEBHOOK_SETUP.md` |
| Understand how it works | `deploy/ARCHITECTURE.md` |
| Detailed deployment steps | `DEPLOYMENT.md` (root) |
| See all deployment files | `deploy/README.md` |

---

## 🔄 How It Works (Simplified)

```
You push code to GitHub
    ↓
GitHub sends webhook to your VPS
    ↓
webhook-server.py receives it
    ↓
update-marxnager.sh triggers Portainer
    ↓
Portainer rebuilds container
    ↓
Your bot updates! ✨
```

---

## ✅ Checklist

Before starting, ensure you have:

- [ ] VPS with Portainer running
- [ ] Bot already deployed in Portainer
- [ ] SSH access to VPS as root or sudo user
- [ ] GitHub repository access
- [ ] 30-45 minutes of time

For Portainer Business Edition, you also need:
- [ ] Portainer Business license

---

## 🆘 Need Help?

1. **Read the detailed guide**: `WEBHOOK_SETUP.md`
2. **Check the architecture**: `ARCHITECTURE.md`
3. **Review troubleshooting**: `WEBHOOK_SETUP.md` → "Troubleshooting"
4. **Test each component** individually before testing the full flow

---

## 🎉 Success Indicators

You'll know it's working when:

1. ✅ `curl http://your-vps:5000/health` returns success
2. ✅ `/usr/local/bin/update-marxnager.sh` runs without errors
3. ✅ GitHub webhook shows "200 OK" in delivery status
4. ✅ `journalctl -u webhook-server` shows webhook received
5. ✅ Portainer stack logs show rebuild after push
6. ✅ `docker ps` shows container as "Up" with recent restart

Good luck with your deployment! 🚀
