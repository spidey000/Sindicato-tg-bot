-- Marxnager User Profiles Table Migration
-- This migration creates the user_profiles table for multi-user support
-- Enables each delegate to have their own personal and employment data

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create user_profiles table
CREATE TABLE IF NOT EXISTS user_profiles (
    -- Primary key
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    -- Telegram identification
    telegram_user_id BIGINT UNIQUE NOT NULL,
    telegram_username TEXT,
    telegram_first_name TEXT,

    -- Personal identification
    nombre TEXT NOT NULL,
    dni TEXT NOT NULL UNIQUE,

    -- Contact information
    email TEXT NOT NULL,
    telefono TEXT NOT NULL,

    -- Address
    direccion TEXT NOT NULL,
    codigo_postal TEXT NOT NULL,
    ciudad TEXT NOT NULL,
    provincia TEXT NOT NULL,

    -- Employment
    naf TEXT NOT NULL,
    fecha_alta TEXT NOT NULL,
    centro_trabajo TEXT NOT NULL,
    puesto TEXT,

    -- Company data
    empresa_nombre TEXT NOT NULL,
    empresa_cif TEXT NOT NULL,
    empresa_direccion TEXT NOT NULL,
    empresa_codigo_postal TEXT NOT NULL,
    empresa_ciudad TEXT NOT NULL,
    empresa_provincia TEXT NOT NULL,
    empresa_actividad TEXT,
    empresa_ccc TEXT NOT NULL,
    empresa_trabajadores INTEGER DEFAULT 0 CHECK (empresa_trabajadores >= 0),
    empresa_horario TEXT,

    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    is_active BOOLEAN DEFAULT TRUE,

    -- Constraints
    CONSTRAINT valid_dni CHECK (dni ~ '^\d{8}-[A-Z]$'),
    CONSTRAINT valid_email CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$'),
    CONSTRAINT valid_cif CHECK (empresa_cif ~ '^[A-Z]{1}\d{8}$'),
    CONSTRAINT valid_phone CHECK (telefono ~ '^[67]\d{8}$'),
    CONSTRAINT valid_postal_code CHECK (codigo_postal ~ '^\d{5}$'),
    CONSTRAINT valid_empresa_postal_code CHECK (empresa_codigo_postal ~ '^\d{5}$')
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_user_profiles_telegram_id ON user_profiles(telegram_user_id);
CREATE INDEX IF NOT EXISTS idx_user_profiles_dni ON user_profiles(dni);
CREATE INDEX IF NOT EXISTS idx_user_profiles_active ON user_profiles(is_active);
CREATE INDEX IF NOT EXISTS idx_user_profiles_email ON user_profiles(email);

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION update_user_profiles_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger to auto-update updated_at
DROP TRIGGER IF EXISTS update_user_profiles_updated_at_trigger ON user_profiles;
CREATE TRIGGER update_user_profiles_updated_at_trigger
    BEFORE UPDATE ON user_profiles
    FOR EACH ROW
    EXECUTE FUNCTION update_user_profiles_updated_at();

-- Row Level Security (RLS) - Enable RLS
ALTER TABLE user_profiles ENABLE ROW LEVEL SECURITY;

-- RLS Policies
-- Users can only read their own profile
CREATE POLICY "Users can read own profile"
    ON user_profiles
    FOR SELECT
    USING (telegram_user_id = current_setting('jwt.claims.user_id')::BIGINT);

-- Users can insert their own profile
CREATE POLICY "Users can insert own profile"
    ON user_profiles
    FOR INSERT
    WITH CHECK (telegram_user_id = current_setting('jwt.claims.user_id')::BIGINT);

-- Users can update their own profile
CREATE POLICY "Users can update own profile"
    ON user_profiles
    FOR UPDATE
    USING (telegram_user_id = current_setting('jwt.claims.user_id')::BIGINT);

-- Users can delete their own profile
CREATE POLICY "Users can delete own profile"
    ON user_profiles
    FOR DELETE
    USING (telegram_user_id = current_setting('jwt.claims.user_id')::BIGINT);

-- Grant permissions
GRANT USAGE ON SCHEMA public TO anon, authenticated;
GRANT ALL ON user_profiles TO authenticated;
GRANT SELECT ON user_profiles TO anon;

-- Insert sample profile for Juan Manuel (for testing)
-- This should be removed or disabled in production
INSERT INTO user_profiles (
    telegram_user_id,
    telegram_username,
    telegram_first_name,
    nombre,
    dni,
    email,
    telefono,
    direccion,
    codigo_postal,
    ciudad,
    provincia,
    naf,
    fecha_alta,
    centro_trabajo,
    puesto,
    empresa_nombre,
    empresa_cif,
    empresa_direccion,
    empresa_codigo_postal,
    empresa_ciudad,
    empresa_provincia,
    empresa_actividad,
    empresa_ccc,
    empresa_trabajadores,
    empresa_horario,
    is_active
) VALUES (
    0, -- Replace with actual Telegram user ID
    'juanmanuel_torales',
    'Juan Manuel',
    'JUAN MANUEL TORALES CHORNE',
    '44591820-H',
    'delegados.sdpmad@gmail.com',
    '627228904',
    'CALLE PLAYA DE ZARAUZ 18, 2C',
    '28042',
    'MADRID',
    'MADRID',
    '29/10177911/13',
    '17/01/2023',
    'AEROPUERTO ADOLFO SUÁREZ MADRID - BARAJAS',
    'Delegado de Prevención',
    'SKYWAY AIR NAVIGATION SERVICES',
    'A86164894',
    'CALLE QUINTANAVIDES 21',
    '28050',
    'MADRID',
    'MADRID',
    'ACTIVIDADES ANEXAS AL TRANSPORTE AÉREO',
    '28184193088',
    37,
    '00.00 a 23.59',
    true
) ON CONFLICT (telegram_user_id) DO NOTHING;

-- Add comment to table
COMMENT ON TABLE user_profiles IS 'User profiles for Marxnager multi-user support. Contains personal and employment information for each delegate.';
