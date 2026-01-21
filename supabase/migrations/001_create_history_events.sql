-- Supabase Migration: Create history_events table
-- Purpose: Chronological event logging for /history command
-- Schema Version: 1.0

-- Enable UUID extension if not already enabled
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create history_events table
CREATE TABLE IF NOT EXISTS history_events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id BIGINT NOT NULL,
    event_date DATE NOT NULL,
    event_text TEXT NOT NULL,
    case_id TEXT,
    event_type TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),

    -- Constraints
    CONSTRAINT event_text_not_empty CHECK (length(trim(event_text)) > 0)
);

-- Create indexes for common queries
CREATE INDEX IF NOT EXISTS idx_history_events_user_id ON history_events(user_id);
CREATE INDEX IF NOT EXISTS idx_history_events_event_date ON history_events(event_date DESC);
CREATE INDEX IF NOT EXISTS idx_history_events_case_id ON history_events(case_id);
CREATE INDEX IF NOT EXISTS idx_history_events_user_date ON history_events(user_id, event_date DESC);
CREATE INDEX IF NOT EXISTS idx_history_events_created_at ON history_events(created_at DESC);

-- Add comments for documentation
COMMENT ON TABLE history_events IS 'Chronological event logging for Marxnager bot /history command';
COMMENT ON COLUMN history_events.id IS 'Unique identifier for each event';
COMMENT ON COLUMN history_events.user_id IS 'Telegram user ID who triggered the event';
COMMENT ON COLUMN history_events.event_date IS 'Date of the event (for time-series queries)';
COMMENT ON COLUMN history_events.event_text IS 'Human-readable description of the event';
COMMENT ON COLUMN history_events.case_id IS 'Optional associated case ID (e.g., D-2026-001)';
COMMENT ON COLUMN history_events.event_type IS 'Optional event type (e.g., denuncia, demanda, status_update)';
COMMENT ON COLUMN history_events.created_at IS 'Timestamp when the event was logged';

-- Enable Row Level Security (RLS) for security
ALTER TABLE history_events ENABLE ROW LEVEL SECURITY;

-- Create policy: Allow users to only see their own events
CREATE POLICY "Users can view own events"
    ON history_events
    FOR SELECT
    USING (true);  -- For now, allow all (application-layer filtering)

-- Create policy: Allow service role to insert events
CREATE POLICY "Service role can insert events"
    ON history_events
    FOR INSERT
    WITH CHECK (true);  -- Application-layer authentication via @restricted decorator

-- Grant necessary permissions
GRANT USAGE ON SCHEMA public TO postgres;
GRANT ALL ON history_events TO postgres;

-- Optional: Create a view for formatted event display
CREATE OR REPLACE VIEW history_events_formatted AS
SELECT
    id,
    user_id,
    event_date,
    event_text,
    case_id,
    event_type,
    created_at,
    -- Format event for display
    CASE
        WHEN case_id IS NOT NULL THEN event_date || ' | ' || case_id || ' | ' || event_text
        ELSE event_date || ' | ' || event_text
    END AS formatted_display
FROM history_events
ORDER BY event_date DESC, created_at DESC;

COMMENT ON VIEW history_events_formatted IS 'Formatted view of events for /history command display';
