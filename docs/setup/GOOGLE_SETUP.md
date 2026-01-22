# Google Service Account Setup Guide

This guide walks you through setting up a Google Service Account for the Marxnager bot to integrate with Google Drive and Google Docs.

## Overview

The Marxnager bot uses Google Workspace APIs to:
- **Create folders** in Google Drive for each case (organized by type)
- **Create Google Docs** with generated legal documents
- **Enable collaborative editing** (delegates can edit documents before finalizing)

## Prerequisites

- A Google Workspace account or personal Google account
- Admin access to create service accounts (or ability to request one)

## Step 1: Create a Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Sign in with your Google account
3. Click the project dropdown at the top
4. Click "NEW PROJECT"
5. Fill in project details:
   - **Project name**: `Marxnager Bot` (or similar)
   - **Organization**: Select your organization (if applicable)
   - **Location**: No organization (or your org)
6. Click "CREATE"
7. Wait for project creation (usually 10-30 seconds)
8. Select the newly created project from the dropdown

## Step 2: Enable Required APIs

1. In the Google Cloud Console, navigate to:
   **APIs & Services** → **Library**

2. Search for and enable the following APIs:

   **API 1: Google Drive API**
   - Search: "Google Drive API"
   - Click on it
   - Click "ENABLE"

   **API 2: Google Docs API**
   - Search: "Google Docs API"
   - Click on it
   - Click "ENABLE"

3. Verify both APIs are enabled:
   - Go to **APIs & Services** → **Enabled APIs & services**
   - You should see both "Google Drive API" and "Google Docs API" in the list

## Step 3: Create Service Account

1. In Google Cloud Console, navigate to:
   **IAM & Admin** → **Service Accounts**

2. Click "CREATE SERVICE ACCOUNT"

3. Fill in service account details:
   - **Service account name**: `marxnager-bot`
   - **Service account description**: `Telegram bot for legal document automation`
   - **Service account ID**: Auto-generated (e.g., `marxnager-bot-12345`)

4. Click "CREATE AND CONTINUE"

5. Skip granting access to users/accounts (click "DONE")
   - We'll grant permissions later via domain-wide delegation

6. Note your service account email:
   - Format: `marxnager-bot@PROJECT_ID.iam.gserviceaccount.com`
   - You'll need this later

## Step 4: Grant Domain-Wide Delegation (Optional but Recommended)

**⚠️ IMPORTANT:** This step allows the service account to impersonate users and access their Drive/Docs. If you're using a personal Google account, skip to Step 5 and use folder sharing instead.

### For Google Workspace Accounts:

1. In the Service Accounts list, click on your `marxnager-bot` service account

2. Go to the **Details** tab

3. Copy the **Unique ID** (numeric ID, e.g., `123456789012345678901`)

4. Follow the instructions in the "Domain-wide delegation" section to:
   - Create a scope for the service account in your Google Admin console
   - Add the following OAuth scopes:
     - `https://www.googleapis.com/auth/drive`
     - `https://www.googleapis.com/auth/documents`

5. Save the client ID and scopes for reference

### For Personal Google Accounts:

Skip this step and use the folder sharing method (see Step 5).

## Step 5: Create and Download Service Account Key

1. In the Service Accounts list, click on your `marxnager-bot` service account

2. Go to the **Keys** tab

3. Click "ADD KEY" → "Create new key"

4. Select key type:
   - ✅ **JSON** (recommended)
   - ❌ P12 (deprecated)

5. Click "CREATE"

6. **⚠️ IMPORTANT:** The JSON key file will download automatically
   - Filename format: `PROJECT_ID-XXXXXXXX.json`
   - **Keep this file secure!** It grants full access to your Google Workspace
   - Store it in a secure location
   - Never commit it to Git

7. Rename the file to `google_credentials.json` for consistency

## Step 6: Configure Drive Folder Structure

### Option A: Service Account with Domain-Wide Delegation

1. The bot will automatically create folders under the service account's Drive
2. Set the following environment variables in `.env`:
   ```bash
   # Drive folder IDs (case-specific parent folders)
   DRIVE_FOLDER_DENUNCIAS=<folder_id>
   DRIVE_FOLDER_DEMANDAS=<folder_id>
   DRIVE_FOLDER_EMAILS=<folder_id>
   ```

### Option B: Personal Google Account (Folder Sharing)

1. Create folder structure in your personal Google Drive:
   ```
   Marxnager Bot/
   ├── Denuncias/
   ├── Demandas/
   └── Emails/
   ```

2. Share each folder with the service account:
   - Right-click folder → "Share"
   - Enter service account email: `marxnager-bot@PROJECT_ID.iam.gserviceaccount.com`
   - Grant permission: **Editor**
   - Click "Send"

3. Get folder IDs:
   - Open each folder in Google Drive
   - Copy the folder ID from the URL:
     - URL format: `https://drive.google.com/drive/folders/<FOLDER_ID>`
     - Example: `1AbCdEfGhIjKlMnOpQrStUvWxYz`

4. Set environment variables in `.env`:
   ```bash
   DRIVE_FOLDER_DENUNCIAS=1AbCdEfGhIjKlMnOpQrStUvWxYz
   DRIVE_FOLDER_DEMANDAS=1AbCdEfGhIjKlMnOpQrStUvWxYz
   DRIVE_FOLDER_EMAILS=1AbCdEfGhIjKlMnOpQrStUvWxYz
   ```

## Step 7: Configure Environment Variables

Add the following to your `.env` file:

```bash
# Google Service Account Configuration
GOOGLE_CREDENTIALS_PATH=/app/config/google_credentials.json

# Drive Folder IDs (from Step 6)
DRIVE_FOLDER_DENUNCIAS=<your_denuncias_folder_id>
DRIVE_FOLDER_DEMANDAS=<your_demandas_folder_id>
DRIVE_FOLDER_EMAILS=<your_emails_folder_id>

# Google Cloud Project (for reference)
GOOGLE_PROJECT_ID=<your_project_id>
```

## Step 8: Deploy Credentials to Server

### Option A: Docker Volume Mount (Recommended)

1. Store `google_credentials.json` in a secure directory on your server:
   ```bash
   mkdir -p /opt/marxnager/config
   mv ~/Downloads/google_credentials.json /opt/marxnager/config/
   chmod 600 /opt/marxnager/config/google_credentials.json
   ```

2. Update `docker-compose.yml` to mount the credentials:
   ```yaml
   volumes:
     - ./config/google_credentials.json:/app/config/google_credentials.json:ro
   ```

### Option B: Docker Secrets (Production)

1. Create Docker secret:
   ```bash
   cat /opt/marxnager/config/google_credentials.json | docker secret create google_credentials -
   ```

2. Update `docker-compose.yml`:
   ```yaml
   secrets:
     google_credentials:
       external: true

   services:
     bot:
       secrets:
         - google_credentials
   ```

## Step 9: Verify Setup

### Test Connection

1. Restart the bot:
   ```bash
   docker-compose down
   docker-compose up -d
   ```

2. Check logs for successful initialization:
   ```bash
   docker-compose logs -f | grep -i google
   ```

**Expected output:**
```
✅ Google Drive client initialized successfully
✅ Google Docs client initialized successfully
```

### Test Folder Creation

1. Send `/denuncia Test connection` to the bot
2. Wait for document generation
3. Check Google Drive:
   - Navigate to your Denuncias folder
   - Verify a new case folder was created (e.g., `D-2026-001 Test connection`)
   - Verify a Google Doc was created inside the folder

## Troubleshooting

### Issue: "Access denied" or "Insufficient permissions"

**Cause:** Service account doesn't have access to folders

**Solutions:**
1. Verify folder sharing (Step 6B) - service account email must be added as Editor
2. Check service account has Drive API enabled (Step 2)
3. Verify environment variables are correct in `.env`
4. Restart bot after updating `.env`

### Issue: "File not found: google_credentials.json"

**Cause:** Credentials file not mounted correctly

**Solutions:**
1. Verify file exists: `ls -la /opt/marxnager/config/google_credentials.json`
2. Check Docker volume mount in `docker-compose.yml`
3. Verify path in `.env`: `GOOGLE_CREDENTIALS_PATH=/app/config/google_credentials.json`
4. Rebuild container: `docker-compose up -d --build`

### Issue: "Google Docs API not enabled"

**Cause:** Docs API not enabled in Google Cloud Console

**Solution:**
1. Go to APIs & Services → Enabled APIs & services
2. Search for "Google Docs API"
3. Click "ENABLE"
4. Wait 1-2 minutes for propagation
5. Restart bot

### Issue: "Quota exceeded" or rate limiting

**Cause:** Free tier has usage limits (100 requests per 100 seconds)

**Solutions:**
1. Implement retry logic (already in the bot)
2. Add exponential backoff (already in the bot)
3. Consider upgrading to paid tier for production
4. Cache Drive/Docs responses to reduce API calls

### Issue: "Domain-wide delegation failed"

**Cause:** OAuth scopes not properly configured

**Solutions:**
1. Verify scopes in Google Admin console match Step 4
2. Check service account Unique ID matches admin console
3. Ensure user being impersonated has Drive/Docs access
4. Test delegation with [OAuth 2.0 Playground](https://developers.google.com/oauthplayground/)

## Security Best Practices

### 1. Protect the Credentials File

- **Never commit** `google_credentials.json` to Git
- Add to `.gitignore`:
  ```
  google_credentials.json
  client_secret*.json
  token*.json
  ```
- Set file permissions: `chmod 600 google_credentials.json`
- Store in secure directory (e.g., `/opt/marxnager/config`)

### 2. Use Docker Secrets in Production

Instead of volume mounting, use Docker secrets:
```bash
echo "Your secret content" | docker secret create google_credentials -
```

### 3. Limit Service Account Permissions

- Only grant APIs that are needed (Drive, Docs)
- Use domain-wide delegation only if necessary
- Set up VPC Service Controls for Google Workspace (enterprise)
- Monitor service account usage in Cloud Console

### 4. Rotate Credentials Regularly

- Delete old keys and create new ones periodically
- Monitor for unauthorized access in Cloud Console
- Set up alerts for suspicious activity

### 5. Use Environment-Specific Service Accounts

- **Development:** Use a separate service account with test folders
- **Production:** Use a dedicated service account with production folders
- Never mix environments

## Monitoring and Logging

### Monitor Service Account Usage

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Navigate to **IAM & Admin** → **Service Accounts**
3. Click on your service account
4. View "Permissions" tab to see who is using it
5. Check "Logs" for API call history

### Check API Quotas

1. Go to **APIs & Services** → **Dashboard**
2. Click on "Google Drive API" or "Google Docs API"
3. View "Quotas" section
4. Monitor usage against limits

### Log Bot Activity

The Marxnager bot logs all Google API calls:
```bash
# View recent Drive/Docs operations
docker-compose logs | grep -i "drive\|docs"

# Check for errors
docker-compose logs | grep -i "error\|failed"
```

## Advanced Configuration

### Custom Folder Organization

You can organize your Drive structure differently:

```
Marxnager Bot/
├── 2026/
│   ├── Q1/
│   │   ├── Denuncias/
│   │   ├── Demandas/
│   │   └── Emails/
│   └── Q2/
│       ├── Denuncias/
│       ├── Demandas/
│       └── Emails/
```

Just update the folder IDs in `.env` accordingly.

### Multi-Environment Setup

For development and production:

**Development:**
```bash
DRIVE_FOLDER_DENUNCIAS=<dev_folder_id>
DRIVE_FOLDER_DEMANDAS=<dev_folder_id>
DRIVE_FOLDER_EMAILS=<dev_folder_id>
GOOGLE_CREDENTIALS_PATH=/app/config/google_credentials_dev.json
```

**Production:**
```bash
DRIVE_FOLDER_DENUNCIAS=<prod_folder_id>
DRIVE_FOLDER_DEMANDAS=<prod_folder_id>
DRIVE_FOLDER_EMAILS=<prod_folder_id>
GOOGLE_CREDENTIALS_PATH=/app/config/google_credentials_prod.json
```

### Service Account Impersonation

If using domain-wide delegation, the bot can impersonate any user:

```python
# In src/integrations/google_client.py
credentials = service_account.Credentials.from_service_account_file(
    'google_credentials.json',
    scopes=['https://www.googleapis.com/auth/drive']
)

# Impersonate a user
delegated_credentials = credentials.with_subject('user@example.com')
```

## Cost Considerations

### Google Cloud Platform Pricing

- **Free Tier:**
  - Drive API: 100 requests per 100 seconds
  - Docs API: 100 requests per 100 seconds
  - Daily quota: 10,000 requests per day

- **Paid Usage:**
  - Drive API: $0.05 per 1,000 requests (after free tier)
  - Docs API: $0.05 per 1,000 requests (after free tier)

### Estimated Marxnager Usage

Assuming 20 delegates generating 5 documents per week:

- **Requests per week:** ~1,000 (20 delegates × 5 docs × 10 API calls)
- **Requests per month:** ~4,000
- **Monthly cost:** $0.20 (well within free tier)

**Conclusion:** Free tier is sufficient for small to medium deployments.

## Next Steps

After completing Google setup:

1. **Test integration:**
   - Generate a test document with `/denuncia Test Google setup`
   - Verify folder and document creation in Drive
   - Verify document is editable

2. **Set up Notion integration:**
   - See `NOTION_SETUP.md` for instructions

3. **Set up Supabase integration (optional):**
   - See `SUPABASE_SETUP.md` for instructions

4. **Deploy the bot:**
   - See `DEPLOYMENT.md` for deployment instructions

## Resources

- [Google Drive API Documentation](https://developers.google.com/drive/api/v3/about-sdk)
- [Google Docs API Documentation](https://developers.google.com/docs/api/reference/rest)
- [Service Account Authentication](https://developers.google.com/identity/protocols/oauth2/service-account)
- [Domain-Wide Delegation](https://developers.google.com/admin-sdk/directory/v1/guides/delegation)
- [Docker Secrets Documentation](https://docs.docker.com/engine/swarm/secrets/)

## Support

If you encounter issues:

1. Check bot logs: `docker-compose logs -f`
2. Verify credentials file is correct and not corrupted
3. Check Google Cloud Console for API errors
4. Review troubleshooting section above
5. Check `@fix_plan.md` for known issues and workarounds
