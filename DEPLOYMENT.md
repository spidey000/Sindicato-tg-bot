# Deployment Guide: Marxnager Bot

This guide explains how to deploy the Marxnager bot on a VPS using Docker and Portainer, including automated webhook deployment.

## Prerequisites

- A VPS with Docker and Docker Compose installed.
- Portainer installed and accessible.
- A Telegram Bot Token from @BotFather.
- API keys for Notion, OpenRouter, and Perplexity.
- GitHub repository with your bot code (for webhook autodeploy).

## Deployment via Portainer (Stacks)

1.  **Log in** to your Portainer instance.
2.  **Navigate** to the environment where you want to deploy (e.g., `local`).
3.  **Click on "Stacks"** in the left sidebar.
4.  **Click "+ Add stack"**.
5.  **Name your stack** (e.g., `marxnager-bot`).
6.  **Build method:** Choose "Web editor".
7.  **Paste the content** of `docker-compose.yml` from this repository into the editor.
8.  **Environment variables:**
    - Click "Add environment variable" for each of the following (or use the "Advanced mode" to paste a list):
    
    ```text
    BOT_TOKEN=<REDACTED_SECRET>
    AUTHORIZED_USER_IDS=comma_separated_ids
    OPENROUTER_API_KEY=your_key
    PERPLEXITY_API_KEY_PRIMARY=your_key
    PERPLEXITY_API_KEY_FALLBACK=your_key
    NOTION_TOKEN=your_token
    NOTION_DATABASE_ID=your_id
    DRIVE_FOLDER_DENUNCIAS=your_folder_id
    DRIVE_FOLDER_DEMANDAS=your_folder_id
    DRIVE_FOLDER_EMAILS=your_folder_id
    ADMIN_EMAIL=your_email
    ```
9.  **Click "Deploy the stack"**.

## Local Docker Deployment (Manual)

If you prefer to deploy manually via CLI:

1.  Clone the repository:
    ```bash
    git clone https://github.com/your-repo/marxnager-tg-bot.git
    cd marxnager-tg-bot
    ```
2.  Create and configure your `.env` file:
    ```bash
    cp .env.example .env
    nano .env
    ```
3.  Build and run the container:
    ```bash
    docker-compose up -d --build
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

- **In Portainer:** Go to Stacks -> marxnager-bot -> Containers -> marxnager-bot -> Logs.
- **Via CLI:**
    ```bash
    docker logs -f marxnager-bot
    ```

- **Webhook server logs:**
    ```bash
    sudo journalctl -u webhook-server -f
    ```

---

## Troubleshooting Webhooks

### Webhook not triggering:
1. Check GitHub webhook delivery status in Settings -> Webhooks
2. Verify your VPS firewall allows port 5000 (or your webhook port)
3. Test the webhook URL manually:
   ```bash
   curl -X POST http://your-vps-ip:5000/webhook -d '{"test": true}'
   ```

### Deployment fails:
1. Check Portainer logs for the stack
2. Verify environment variables are correctly set
3. Test the update script manually:
   ```bash
   sudo /usr/local/bin/update-marxnager.sh
   ```

### Container won't start:
1. Check logs: `docker logs marxnager-bot`
2. Verify all required environment variables are set
3. Ensure `.env` file exists or variables are in Portainer
