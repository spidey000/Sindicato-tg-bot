# Supabase Setup Guide for /history Command

This guide explains how to set up Supabase for the `/history` command in Marxnager.

## Overview

The `/history` command provides a chronological timeline of all case-related events. It uses Supabase (PostgreSQL) for time-series queries, complementing Notion's active case management.

## Architecture

**Why Supabase + Notion?**
- **Notion**: Active case management with document links (user-friendly interface)
- **Supabase**: Historical event logging and timeline building (time-series queries)
- **Complementary purposes**: No migration planned - both systems serve distinct needs

## Prerequisites

1. Supabase account (free tier available)
2. Supabase project URL and API key (service role key for writes)
3. PostgreSQL database enabled (default in Supabase)

## Step 1: Create Supabase Project

1. Go to https://supabase.com
2. Click "New Project"
3. Choose organization or create one
4. Set project name: `marxnager-events`
5. Set database password (save it securely)
6. Choose region closest to your users
7. Click "Create new project"
8. Wait for project to be provisioned (2-3 minutes)

## Step 2: Run Database Migration

1. In Supabase dashboard, go to **SQL Editor**
2. Click **New Query**
3. Copy the contents of `supabase/migrations/001_create_history_events.sql`
4. Paste into SQL Editor
5. Click **Run** (or press Ctrl+Enter)
6. Verify table creation in **Table Editor**

**Migration creates:**
- `history_events` table with indexes
- Row Level Security (RLS) policies
- `history_events_formatted` view for display

## Step 3: Get API Credentials

1. In Supabase dashboard, go to **Settings → API**
2. Copy the following values:
   - **Project URL** (looks like: `https://xxxxxxxxxxxxx.supabase.co`)
   - **service_role key** (NOT the anon key - service role has write access)

**Security Note:**
- The `service_role` key bypasses RLS and can write to the database
- Store this key securely - never commit it to git
- Add to `.env` file (see Step 4)

## Step 4: Configure Environment Variables

Add to your `.env` file:

```bash
# Supabase Configuration
SUPABASE_URL=https://xxxxxxxxxxxxx.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Important:**
- Replace `SUPABASE_URL` with your project URL
- Replace `SUPABASE_KEY` with your `service_role` key (NOT anon key)
- Keep these values secret - never commit `.env` to git

## Step 5: Install Dependencies

If not already installed, add supabase-py:

```bash
pip install supabase==2.*
```

Or update from requirements.txt:

```bash
pip install -r requirements.txt
```

## Step 6: Test Connection

Restart the bot and check logs for:

```
✅ Supabase client initialized successfully
```

If you see warnings, verify:
1. `SUPABASE_URL` and `SUPABASE_KEY` are set correctly
2. No typos in `.env` file
3. Bot is reading the correct `.env` file

## Step 7: Test /history Command

1. Create a test case (e.g., `/denuncia Test case`)
2. Wait for case to be created successfully
3. Run `/history` in private chat
4. You should see the event logged:

```
📋 Historial de Eventos
Periodo: últimos 30 días
Total: 1 eventos

📅 2026-01-20
🆔 D-2026-001
🏷️ denuncia
📝 Se creó Denuncia ITSS con ID D-2026-001: Test case
────────────────────────────────────────
```

## Usage Examples

### View last 30 days (default)
```
/history
```

### View last 7 days
```
/history 7
```

### View date range
```
/history 01/01/2026 31/01/2026
```

## Event Types Logged

The system automatically logs:
- **Case creation**: When denuncia/demanda/email is created
- **Status updates**: When `/status` command changes case status
- **Future events**: Can be extended for document refinement, file uploads, etc.

## Database Schema

```sql
CREATE TABLE history_events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id BIGINT NOT NULL,           -- Telegram user ID
    event_date DATE NOT NULL,           -- Date of event (for queries)
    event_text TEXT NOT NULL,           -- Human-readable description
    case_id TEXT,                       -- Optional: D-2026-001
    event_type TEXT,                    -- Optional: denuncia, status_update
    created_at TIMESTAMPTZ DEFAULT NOW() -- Timestamp logged
);
```

## Troubleshooting

### "Sistema de historial no disponible"
- Supabase client not initialized
- Check `SUPABASE_URL` and `SUPABASE_KEY` in `.env`
- Restart bot after updating credentials

### No events shown
- Check Supabase Table Editor to see if events exist
- Try creating a new case and check logs for errors
- Verify service_role key (not anon key)

### Connection errors
- Verify Supabase project is active (not paused)
- Check network connectivity
- Try manual test in SQL Editor

## Security Considerations

1. **Service Role Key**: Use `service_role` key (bypasses RLS for writes)
2. **Environment Variables**: Never commit `.env` to git
3. **Row Level Security**: Enabled - users can only see their own events
4. **Application Filtering**: `@restricted` decorator ensures only authorized users

## Future Enhancements

Potential improvements to event logging:
- File upload events (evidence added to cases)
- Document refinement events (user feedback iterations)
- Error/failure events (for monitoring)
- Export events (case data exported)

## Monitoring

Check event logging health:
```bash
# In bot logs
grep "Logged event to Supabase" logs/bot.log | tail -20

# In Supabase dashboard
# Table Editor → history_events → View rows
```

## Support

For issues:
1. Check Supabase dashboard → Logs → Postgres logs
2. Check bot logs: `logs/bot.log`
3. Verify migration ran successfully
4. Test connection manually in SQL Editor
