# Supabase Setup Guide for Marxnager Testing

This guide walks you through setting up Supabase for testing the multi-user profile system and history logging features.

## Overview

The Marxnager bot uses Supabase for two purposes:
1. **User Profile Management** - Store delegate personal/employment data for multi-user support
2. **Event Logging** - Chronological timeline of case-related events for `/history` command

## Prerequisites

- A Supabase account (free tier is sufficient)
- Basic familiarity with SQL and database migrations

## Step 1: Create Supabase Project

1. Go to https://supabase.com
2. Click "Start your project"
3. Sign in with GitHub or create an account
4. Click "New Project"
5. Fill in project details:
   - **Organization**: Create new or use existing
   - **Name**: `marxnager-production` (or similar)
   - **Database Password**: Generate a secure password (save it!)
   - **Region**: Choose closest to your users (e.g., EU West)
6. Click "Create new project" and wait for provisioning (~2 minutes)

## Step 2: Get Credentials

Once your project is ready:

1. Go to **Settings** → **API**
2. Copy these values:
   - **Project URL** (looks like: `https://xxxxxxxxxxxxx.supabase.co`)
   - **service_role key** (NOT the anon key - scroll down to find it)
   - ⚠️ **IMPORTANT**: Keep the service_role key secret! It bypasses RLS policies.

## Step 3: Run Migrations

### Option A: Using Supabase Dashboard (Recommended for Testing)

1. Go to **SQL Editor** in the left sidebar
2. Click "New Query"
3. Run each migration file in order:

**Migration 1: Create history_events table**
```bash
# Copy contents from: supabase/migrations/001_create_history_events.sql
# Paste into SQL Editor and click "Run"
```

**Migration 2: Create user_profiles table**
```bash
# Copy contents from: supabase/migrations/20260120_create_user_profiles.sql
# Paste into SQL Editor and click "Run"
```

### Option B: Using Supabase CLI (Recommended for Production)

```bash
# Install Supabase CLI
brew install supabase/tap/supabase  # macOS
# Or visit: https://supabase.com/docs/guides/cli

# Link your project
supabase link --project-ref <your-project-id>

# Push migrations
supabase db push
```

## Step 4: Configure Environment Variables

Add Supabase credentials to your `.env` file:

```bash
# Supabase Configuration
SUPABASE_URL=https://xxxxxxxxxxxxx.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

Replace the placeholder values with your actual credentials from Step 2.

## Step 5: Verify Setup

### Restart the Bot

```bash
# Stop the bot
docker-compose down

# Rebuild (to pick up new env vars)
docker-compose build

# Start the bot
docker-compose up -d

# Check logs for success message
docker-compose logs -f | grep -i supabase
```

**Expected output:**
```
✅ Supabase client initialized successfully
```

### Test Database Connection

Send `/metrics` command to the bot and look for:
- Supabase connection status
- API success rates

## Step 6: Test Profile Creation

1. Send `/profile create` to the bot
2. Follow the wizard questions (21 questions total)
3. Complete the profile creation
4. Verify success message

### Verify in Supabase Dashboard

1. Go to **Table Editor** in Supabase
2. Click on `user_profiles` table
3. Verify your profile appears with all data

## Step 7: Test Profile Injection in Documents

1. Create a profile (if you haven't already)
2. Send `/denuncia Test case` to bot
3. Wait for document generation
4. Open the generated Google Doc
5. Verify your profile data is injected:
   - Your nombre appears (not Juan Manuel's)
   - Your DNI appears
   - Your email, phone, address, etc.

## Step 8: Test History Logging

1. Generate any document (`/denuncia`, `/demanda`, or `/email`)
2. Send `/history` command
3. Verify the event is logged with:
   - Correct date
   - Case ID
   - Event description

### Verify in Supabase Dashboard

1. Go to **Table Editor**
2. Click on `history_events` table
3. Verify events are being logged

## Troubleshooting

### Issue: "Supabase client not initialized"

**Cause**: Missing or invalid credentials in `.env`

**Solution**:
1. Verify `SUPABASE_URL` and `SUPABASE_KEY` are set in `.env`
2. Ensure you're using the `service_role` key, not `anon` key
3. Restart bot after updating `.env`

### Issue: "Permission denied" errors

**Cause**: RLS policies blocking access with service_role key

**Solution**: The service_role key should bypass RLS. If you still see errors:
1. Check your migration ran successfully
2. Verify policies exist in **Authentication** → **Policies**
3. Try temporarily disabling RLS: `ALTER TABLE user_profiles DISABLE ROW LEVEL SECURITY;`

### Issue: "Profile creation failed"

**Cause**: Validation errors or missing required fields

**Solution**:
1. Check bot logs for specific error: `docker-compose logs | grep -i error`
2. Verify all required fields are provided
3. Check data format (DNI: `12345678-Z`, Email: `user@example.com`, Phone: `6xxxxxxxx`)

### Issue: "Profile data not injected in document"

**Cause**: Profile not loaded or template injection failed

**Solution**:
1. Verify profile exists: `/profile` command
2. Check bot logs for "Loading profile for user X"
3. Verify template has `{{PLACEHOLDER}}` fields matching profile data

## Security Notes

### Service Role Key vs Anon Key

- **Service Role Key**: Full database access, bypasses RLS, for backend use only
- **Anon Key**: Limited access, respects RLS policies, for client-side use

**Marxnager uses service_role key because:**
- Bot is a trusted backend service
- Already protected by `@restricted` decorator (AUTHORIZED_USER_IDS)
- Simplifies RLS policy management

### RLS Policies

The migrations include RLS policies for future migration to anon key:
- Users can only read/update their own profile
- Users can only read their own history events

**Current limitation**: Policies use JWT claims that don't work with service_role key. This is acceptable for now since the bot is already authorized via `@restricted` decorator.

## Testing Checklist

Use `TESTING_CHECKLIST.md` for comprehensive testing:

- [ ] Profile creation wizard works end-to-end
- [ ] Profile updates work correctly
- [ ] Profile display shows all fields
- [ ] Profile deletion works
- [ ] Profile data is injected into documents
- [ ] Multi-user isolation works (User A's data doesn't leak to User B)
- [ ] Validation prevents invalid data
- [ ] History events are logged
- [ ] `/history` command displays events
- [ ] Cache improves performance
- [ ] Error handling is graceful

## Next Steps After Testing

1. **Remove sample profile**: Delete Juan Manuel's sample profile from migration
2. **Create profiles for all users**: Have each delegate create their profile
3. **Monitor usage**: Check `/metrics` command regularly
4. **Plan Redis migration**: For session persistence (future)

## Production Deployment

When deploying to production:

1. Use a separate Supabase project (not the test one)
2. Enable database backups in Supabase settings
3. Set up monitoring alerts in Supabase dashboard
4. Consider upgrading to Pro plan for:
   - More disk space
   - Daily backups
   - Pause/resume functionality

## Resources

- Supabase Documentation: https://supabase.com/docs
- Supabase Python Client: https://supabase.com/docs/reference/python
- Migration Guide: https://supabase.com/docs/guides/cli/local-development

## Support

If you encounter issues:

1. Check bot logs: `docker-compose logs -f`
2. Check Supabase logs: **Dashboard** → **Logs**
3. Review `TESTING_CHECKLIST.md` for test procedures
4. Check `@fix_plan.md` for known issues and workarounds
