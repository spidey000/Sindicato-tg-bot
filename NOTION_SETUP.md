# Notion Setup Guide

This guide walks you through setting up Notion integration for the Marxnager bot to manage case databases and track document generation.

## Overview

The Marxnager bot uses Notion to:
- **Create database entries** for each legal case (denuncia, demanda, email)
- **Track case status** (Preparación, Revisión, Presentada, Resuelta, Archivada)
- **Store links** to Google Docs and Drive folders
- **Provide case management** via `/status` and `/update` commands

## Prerequisites

- A Notion account (free tier is sufficient)
- Basic familiarity with Notion databases
- The bot will need access to create/edit database entries

## Step 1: Create a Notion Integration

1. Go to [Notion My Integrations](https://www.notion.so/my-integrations)
2. Click "+ New integration"
3. Fill in integration details:
   - **Name**: `Marxnager Bot` (or similar)
   - **Associated workspace**: Select your workspace
   - **Type**: Internal
   - **Capabilities**: Read/Write user content (required)
4. Click "Submit"
5. **⚠️ IMPORTANT:** Copy the **Internal Integration Token**
   - Format: `secret_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`
   - Keep this secure! It grants access to your Notion workspace
   - You'll need this for the `.env` file

## Step 2: Create a Notion Database

### Option A: Manual Database Creation (Recommended for Control)

1. In Notion, create a new page or use an existing one
2. Click the "+" to add a database
3. Select "Table - Database"
4. Name the database (e.g., "Casos Marxnager" or "Legal Cases")

5. Add the following columns (properties):

   **Property 1: Case ID (Title)**
   - Type: **Title**
   - Name: `Case ID` or `Caso`
   - This is the default title property

   **Property 2: Type**
   - Type: **Select**
   - Name: `Type` or `Tipo`
   - Options: `Denuncia`, `Demanda`, `Email`
   - Colors: Red (Denuncia), Blue (Demanda), Green (Email)

   **Property 3: Description**
   - Type: **Text**
   - Name: `Description` or `Descripción`
   - Format: Plain text

   **Property 4: Status**
   - Type: **Select**
   - Name: `Status` or `Estado`
   - Options:
     - `Preparación` (Yellow - default)
     - `Revisión` (Orange)
     - `Presentada` (Blue)
     - `Resuelta` (Green)
     - `Archivada` (Gray)

   **Property 5: Created Date**
   - Type: **Date**
   - Name: `Created Date` or `Fecha de Creación`
   - Format: Date (include time if preferred)

   **Property 6: Google Doc**
   - Type: **URL**
   - Name: `Google Doc` or `Documento`
   - Format: https://docs.google.com/document/d/...

   **Property 7: Drive Folder**
   - Type: **URL**
   - Name: `Drive Folder` or `Carpeta`
   - Format: https://drive.google.com/drive/folders/...

   **Property 8: Delegate**
   - Type: **Text**
   - Name: `Delegate` or `Delegado`
   - Format: Plain text (delegate name)

6. (Optional) Add more properties as needed:
   - `Priority` (Select: Alta, Media, Baja)
   - `Last Updated` (Date)
   - `Tags` (Multi-select: Urgente, Revisión Legal, etc.)
   - `Notes` (Text)

### Option B: Use the Provided Template (Coming Soon)

A Notion template will be provided in future updates that you can duplicate to your workspace.

## Step 3: Share Database with Integration

1. Open the database you created in Step 2
2. Click the "..." (more options) menu in the top-right corner
3. Scroll down and find "Add connections"
4. Search for your integration name (e.g., "Marxnager Bot")
5. Click on it to add the connection
6. Click "Confirm" to grant access

**⚠️ IMPORTANT:** The integration must be added to the **database**, not just the page.

### Verify Connection

1. In the database, click the "..." menu
2. Check that "Marxnager Bot" appears under "Connections"
3. If not, repeat the steps above

## Step 4: Get Database ID

1. Open the database in Notion
2. Copy the URL from your browser
3. Extract the Database ID from the URL:
   - URL format: `https://www.notion.so/USERNAME/DATABASE_NAME?v=DATABASE_ID&p=...`
   - The Database ID is the 32-character string after `v=`
   - Example: `https://www.notion.so/john/Marxnager-Cases?v=1a2b3c4d5e6f7g8h9i0j1k2l3m4n5o6p`

   **Database ID**: `1a2b3c4d5e6f7g8h9i0j1k2l3m4n5o6p`

4. Alternative method:
   - Click the "..." menu → "Add connections" → "Marxnager Bot"
   - Notion will show the Database ID in the API reference

## Step 5: Configure Environment Variables

Add the following to your `.env` file:

```bash
# Notion Configuration
NOTION_TOKEN=secret_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
NOTION_DATABASE_ID=1a2b3c4d5e6f7g8h9i0j1k2l3m4n5o6p
```

Replace with your actual values from Steps 1 and 4.

## Step 6: Test Notion Integration

### Verify Connection

1. Restart the bot:
   ```bash
   docker-compose down
   docker-compose up -d
   ```

2. Check logs for successful initialization:
   ```bash
   docker-compose logs -f | grep -i notion
   ```

**Expected output:**
```
✅ Notion client initialized successfully
```

### Test Database Entry Creation

1. Send `/denuncia Test Notion setup` to the bot
2. Wait for document generation
3. Check Notion database:
   - A new entry should appear with:
     - Case ID: `D-2026-001 Test Notion setup`
     - Type: `Denuncia`
     - Status: `Preparación`
     - Google Doc: Link to the generated document
     - Drive Folder: Link to the case folder
     - Created Date: Today's date

## Step 7: Configure Case Status Updates

The Marxnager bot allows updating case status via the `/status` command.

### Available Status Values

The bot supports the following status values (Spanish):

- `preparacion` - Initial state when document is generated
- `revision` - When delegate is reviewing the document
- `presentada` - When the case is officially submitted (ITSS, court, etc.)
- `resuelta` - When the case is resolved/closed
- `archivada` - When the case is archived

### Update Case Status

1. Send `/status D-2026-001 presentada` to the bot
2. Check Notion database:
   - The status should change to "Presentada"
   - The status update should be logged in Supabase (if enabled)

## Step 8: Configure Active Cases View

The bot provides an `/update` command to list all non-"Presentada" cases.

### Create a Filtered View (Optional)

1. In your Notion database, click "+ Add a view"
2. Select "Table"
3. Name it "Active Cases" or "Casos Activos"
4. Add a filter:
   - Property: `Status`
   - Condition: `is not`
   - Value: `Presentada`
5. Sort by `Created Date` (newest first)

This view matches what the `/update` command returns.

## Troubleshooting

### Issue: "Unauthorized" or "Invalid API key"

**Cause:** NOTION_TOKEN is incorrect or integration token has been revoked

**Solutions:**
1. Verify NOTION_TOKEN in `.env` matches the integration token from Step 1
2. Check that integration is not disabled in Notion
3. Regenerate integration token if necessary
4. Restart bot after updating `.env`

### Issue: "Object not found" or "Database not found"

**Cause:** NOTION_DATABASE_ID is incorrect or database doesn't exist

**Solutions:**
1. Verify NOTION_DATABASE_ID in `.env` matches the database ID from Step 4
2. Check that database exists in your Notion workspace
3. Ensure integration has access to the database (Step 3)
4. Try extracting database ID again from URL

### Issue: "Insufficient permissions" or "Access denied"

**Cause:** Integration doesn't have access to the database

**Solutions:**
1. Verify integration is added to the database (Step 3)
2. Check that integration is enabled in Notion
3. Ensure you're using the correct integration token
4. Try removing and re-adding the integration to the database

### Issue: "Property not found" or "Invalid property"

**Cause:** Database properties don't match expected names

**Solutions:**
1. Verify database has all required properties (Step 2)
2. Check property names match exactly (case-insensitive):
   - `Case ID` or `Caso`
   - `Type` or `Tipo`
   - `Description` or `Descripción`
   - `Status` or `Estado`
   - `Created Date` or `Fecha de Creación`
   - `Google Doc` or `Documento`
   - `Drive Folder` or `Carpeta`
   - `Delegate` or `Delegado`
3. Add missing properties if needed
4. Restart bot after modifying database

### Issue: "Rate limit exceeded" or "Too many requests"

**Cause:** Notion API has rate limits (3 requests per second for free tier)

**Solutions:**
1. Implement retry logic (already in the bot)
2. Add exponential backoff (already in the bot)
3. Consider upgrading to paid tier for production
4. Reduce frequency of database queries

### Issue: Database entry created but with missing data

**Cause:** Property types don't match expected types

**Solutions:**
1. Verify property types match Step 2:
   - Case ID: **Title** (required)
   - Type: **Select**
   - Description: **Text**
   - Status: **Select**
   - Created Date: **Date**
   - Google Doc: **URL**
   - Drive Folder: **URL**
   - Delegate: **Text**
2. Change property types if needed
3. Restart bot after modifying database

## Security Best Practices

### 1. Protect the Integration Token

- **Never commit** NOTION_TOKEN to Git
- Add to `.gitignore`:
  ```
  .env
  .env.local
  ```
- Store in environment variable only
- Rotate token if compromised

### 2. Limit Integration Scope

- Only grant access to specific databases, not entire workspace
- Use separate integrations for development and production
- Regularly review integration permissions in Notion
- Disable unused integrations

### 3. Monitor Integration Usage

1. Go to [Notion My Integrations](https://www.notion.so/my-integrations)
2. Click on your integration
3. View "Usage" tab to see API call history
4. Set up alerts for suspicious activity (if available)

### 4. Use Environment-Specific Integrations

- **Development:** Create a test integration with a test database
- **Production:** Use a separate integration with production database
- Never mix environments

## Monitoring and Logging

### Monitor Notion API Usage

1. Check integration usage in Notion (see Security section above)
2. Monitor bot logs for API calls:
   ```bash
   docker-compose logs | grep -i notion
   ```

### Track Database Changes

1. Enable Notion's database history (if available)
2. Check "Page activity" in Notion for recent changes
3. Use the `/history` command (if Supabase is enabled)

### Log Bot Activity

The Marxnager bot logs all Notion API calls:
```bash
# View recent Notion operations
docker-compose logs | grep -i "notion.*create\|notion.*update"

# Check for errors
docker-compose logs | grep -i "notion.*error\|notion.*failed"
```

## Advanced Configuration

### Custom Property Names

The bot supports flexible property names. If you prefer different names, you can map them in the configuration:

```python
# In src/integrations/notion_client.py
PROPERTY_MAPPING = {
    "case_id": ["Case ID", "Caso", "ID"],
    "type": ["Type", "Tipo", "Document Type"],
    "description": ["Description", "Descripción", "Summary"],
    "status": ["Status", "Estado", "State"],
    "created_date": ["Created Date", "Fecha de Creación", "Date Created"],
    "google_doc": ["Google Doc", "Documento", "Document Link"],
    "drive_folder": ["Drive Folder", "Carpeta", "Folder Link"],
    "delegate": ["Delegate", "Delegado", "Created By"]
}
```

### Custom Status Values

You can add custom status values to the Status property:
- `Enviada a Revisión` (Sent for Review)
- `Aceptada` (Accepted)
- `Rechazada` (Rejected)
- `En Trámite` (In Progress)

Just add them to the Status Select property in Notion. The bot will accept any status value.

### Multi-Database Setup

For different document types, you can use separate databases:

```bash
# .env configuration
NOTION_TOKEN=secret_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
NOTION_DATABASE_DENUNCIAS=1a2b3c4d5e6f7g8h9i0j1k2l3m4n5o6p
NOTION_DATABASE_DEMANDAS=2b3c4d5e6f7g7h8h9i0j1k2l3m4n5o6p7q
NOTION_DATABASE_EMAILS=3c4d5e6f6g7h7h8i9j0j1k2l3m4n5o6p7q8r
```

The bot will automatically route cases to the correct database.

### Database Templates

1. Create a template database with all properties
2. Duplicate it for different environments (dev, staging, prod)
3. Use separate NOTION_DATABASE_ID for each environment
4. Keeps data isolated and clean

## Notion API Limits and Quotas

### Rate Limits

- **Free Tier:** 3 requests per second
- **Paid Tier:** 3 requests per second (same for all plans)

### Best Practices to Avoid Rate Limits

1. **Batch operations:** Group multiple updates into one API call
2. **Retry with backoff:** Already implemented in the bot
3. **Cache responses:** Reduce redundant API calls
4. **Queue requests:** Delay non-urgent operations

### Estimated Marxnager Usage

Assuming 20 delegates generating 5 documents per week:

- **API calls per week:** ~150 (20 delegates × 5 docs × 3 API calls per doc)
- **API calls per month:** ~600
- **Rate limit:** 3 requests per second = 259,200 per day

**Conclusion:** Well within Notion's rate limits for small to medium deployments.

## Integration with Other Services

### Notion + Google Drive

The bot automatically links Notion database entries to Google Drive folders:

1. When a document is generated:
   - Creates folder in Google Drive
   - Creates Google Doc in that folder
   - Adds both links to Notion database entry

2. Users can click links in Notion to navigate to Drive/Docs

### Notion + Supabase

When Supabase is enabled, the bot logs events to both:

1. **Notion:** Active case management (current state)
2. **Supabase:** Historical event logging (chronological timeline)

Example:
- Notion shows: "Case D-2026-001 is in Revisión state"
- Supabase shows: "D-2026-001 changed from Preparación to Revisión on 2026-01-20"

### Notion + Telegram

The bot uses Notion for:

1. **Case creation:** `/denuncia`, `/demanda`, `/email` commands
2. **Status updates:** `/status <ID> <STATE>` command
3. **Active cases:** `/update` command lists non-"Presentada" cases

All operations are synced with Notion database in real-time.

## Next Steps

After completing Notion setup:

1. **Test integration:**
   - Generate a test document with `/denuncia Test Notion setup`
   - Verify database entry is created
   - Update status with `/status D-2026-001 revision`
   - List active cases with `/update`

2. **Set up Google integration:**
   - See `GOOGLE_SETUP.md` for instructions

3. **Set up Supabase integration (optional):**
   - See `SUPABASE_SETUP.md` for instructions

4. **Deploy the bot:**
   - See `DEPLOYMENT.md` for deployment instructions

## Resources

- [Notion API Documentation](https://developers.notion.com/reference)
- [Notion Integration Guide](https://developers.notion.com/docs/create-a-notion-integration)
- [Notion Database Guide](https://www.notion.so/help/notion-databases)
- [Notion API Limits](https://developers.notion.com/reference/request-limits)

## Support

If you encounter issues:

1. Check bot logs: `docker-compose logs -f`
2. Verify integration token is correct and not revoked
3. Check database has all required properties
4. Verify integration has access to the database
5. Review troubleshooting section above
6. Check `@fix_plan.md` for known issues and workarounds

## Example Database Setup

Here's a complete example of a properly configured database:

**Database Name:** Casos Marxnager

**Properties:**
1. **Case ID** (Title) - `D-2026-001 Test setup`
2. **Type** (Select) - `Denuncia`
3. **Description** (Text) - `Test case for verifying Notion integration`
4. **Status** (Select) - `Preparación`
5. **Created Date** (Date) - `2026-01-20`
6. **Google Doc** (URL) - `https://docs.google.com/document/d/1AbCdEf...`
7. **Drive Folder** (URL) - `https://drive.google.com/drive/folders/1XyZwVu...`
8. **Delegate** (Text) - `Juan Manuel`

**Views:**
- **All Cases:** No filters, sorted by Created Date (newest first)
- **Active Cases:** Filter: Status ≠ Presentada, sorted by Created Date
- **By Type:** Group by Type, sorted by Created Date

This setup provides a comprehensive case management system integrated with the Marxnager bot.
