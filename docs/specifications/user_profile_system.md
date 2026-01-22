# User Profile System Design

## Overview
This document describes the design and implementation of a multi-user profile system to replace hardcoded delegate data in Marxnager templates.

## Problem Statement
Currently, all templates contain hardcoded personal data for Juan Manuel Torales Chorne (DNI: 44591820-H). This prevents multi-user support and requires manual template editing for each delegate.

**Current Hardcoded Data Locations:**
- `src/data/itss_template.md` - 73 lines, 17 hardcoded fields
- `src/data/demanda_template.md` - Similar personal and company data

**Examples of Hardcoded Data:**
- Delegate: JUAN MANUEL TORALES CHORNE, DNI: 44591820-H
- Address: CALLE PLAYA DE ZARAUZ 18, 2C, 28042 MADRID
- Phone: 627228904, Email: delegados.sdpmad@gmail.com
- Company: SKYWAY AIR NAVIGATION SERVICES, CIF: A86164894
- Employment: Start date 17/01/2023, NAF: 29/10177911/13

## Solution: User Profile System

### Data Model

#### UserProfile Class
```python
@dataclass
class UserProfile:
    """Complete user profile for legal document generation."""

    # Telegram identification
    telegram_user_id: int  # Primary key
    telegram_username: Optional[str] = None
    telegram_first_name: Optional[str] = None

    # Personal identification
    nombre: str = ""  # Full name: "JUAN MANUEL TORALES CHORNE"
    dni: str = ""  # Spanish ID: "44591820-H"

    # Contact information
    email: str = ""
    telefono: str = ""  # Mobile: "627228904"

    # Address
    direccion: str = ""  # Street + number: "CALLE PLAYA DE ZARAUZ 18, 2C"
    codigo_postal: str = ""  # "28042"
    ciudad: str = ""  # "MADRID"
    provincia: str = ""  # "MADRID"

    # Employment
    naf: str = ""  # Social Security affiliation: "29/10177911/13"
    fecha_alta: str = ""  # Employment start date: "17/01/2023"
    centro_trabajo: str = ""  # "Aeropuerto Adolfo Suárez Madrid - Barajas"
    puesto: str = ""  # Job title (optional)

    # Company data (employer)
    empresa_nombre: str = ""  # "SKYWAY AIR NAVIGATION SERVICES"
    empresa_cif: str = ""  # "A86164894"
   _empresa_direccion: str = ""  # "CALLE QUINTANVIDES 21"
    empresa_codigo_postal: str = ""  # "28050"
    empresa_ciudad: str = ""  # "MADRID"
    empresa_provincia: str = ""  # "MADRID"
    empresa_actividad: str = ""  # "ACTIVIDADES ANEXAS AL TRANSPORTE AÉREO"
    empresa_ccc: str = ""  # Social Security: "28184193088"
    empresa_trabajadores: int = 0  # Number of workers: 37
    empresa_horario: str = ""  # "00.00 a 23.59"

    # Metadata
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    is_active: bool = True  # For soft deletes
```

#### Supabase Schema
```sql
CREATE TABLE user_profiles (
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
    empresa_trabajadores INTEGER DEFAULT 0,
    empresa_horario TEXT,

    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    is_active BOOLEAN DEFAULT TRUE,

    CONSTRAINT valid_dni CHECK (dni ~ '^[0-9]{8}-[A-Z]$'),
    CONSTRAINT valid_email CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$')
);

-- Indexes for performance
CREATE INDEX idx_user_profiles_telegram_id ON user_profiles(telegram_user_id);
CREATE INDEX idx_user_profiles_dni ON user_profiles(dni);
CREATE INDEX idx_user_profiles_active ON user_profiles(is_active);

-- Updated at trigger
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_user_profiles_updated_at
    BEFORE UPDATE ON user_profiles
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
```

### Architecture

#### Components

1. **UserProfile Model** (`src/user_profile.py`)
   - Dataclass definition
   - Validation methods
   - Serialization/deserialization

2. **UserProfileManager** (`src/user_profile.py`)
   - Load profile by Telegram user ID
   - Create/update/delete profiles
   - Cache profiles in memory (optional)

3. **Supabase Integration** (`src/integrations/supabase_client.py`)
   - New table: `user_profiles`
   - CRUD operations with retry logic
   - Query by telegram_user_id or DNI

4. **Template Preprocessing** (`src/template_loader.py`)
   - New function: `inject_user_profile(template: str, profile: UserProfile) -> str`
   - Replace `[HARDCODED]` markers with profile data
   - Maintain backward compatibility

5. **Pipeline Integration** (`src/pipeline.py`)
   - Load user profile before document generation
   - Inject profile data into template
   - Pass preprocessed template to LLM

6. **Profile Management Commands** (`src/handlers/profile.py`)
   - `/profile` - View current profile
   - `/profile set <field> <value>` - Update profile field
   - `/profile create` - Create new profile (wizard)
   - `/profile delete` - Delete profile (admin only)

### Data Flow

#### Current Flow (Single User)
```
Template (with hardcoded data) → LLM → Document
```

#### New Flow (Multi-User)
```
User Input (Telegram) → Load User Profile → Inject into Template → LLM → Document
```

#### Template Processing

**Before:**
```markdown
## 3. DATOS DEL DENUNCIANTE (TRABAJADOR/REPRESENTANTE)

* **Nombre y Apellidos:** [HARDCODED] JUAN MANUEL TORALES CHORNE
* **NIF:** [HARDCODED] 44591820-H
```

**After Injection:**
```markdown
## 3. DATOS DEL DENUNCIANTE (TRABAJADOR/REPRESENTANTE)

* **Nombre y Apellidos:** JUAN MANUEL TORALES CHORNE
* **NIF:** 44591820-H
```

**Implementation:**
```python
def inject_user_profile(template: str, profile: UserProfile) -> str:
    """
    Replace [HARDCODED] markers with user profile data.

    Preserves template structure while injecting dynamic user data.
    """
    # Map of template markers to profile fields
    replacements = {
        "[HARDCODED] JUAN MANUEL TORALES CHORNE": profile.nombre.upper(),
        "[HARDCODED] 44591820-H": profile.dni,
        "[HARDCODED] delegados.sdpmad@gmail.com": profile.email,
        # ... more mappings
    }

    result = template
    for marker, value in replacements.items():
        result = result.replace(marker, value)

    return result
```

### User Interface

#### /profile Command

**View Profile:**
```
/profile
```
**Response:**
```
👤 *Perfil de Usuario*

*Nombre:* Juan Manuel Torales Chorne
*DNI:* 44591820-H
*Email:* delegados.sdpmad@gmail.com
*Teléfono:* 627228904

📍 Dirección:
Calle Playa de Zarauz 18, 2C
28042 Madrid, Madrid

💼 Empleo:
*Empresa:* Skyway Air Navigation Services
*Centro:* Aeropuerto Adolfo Suárez Madrid - Barajas
*NAF:* 29/10177911/13
*Fecha de alta:* 17/01/2023
```

**Update Profile:**
```
/profile set telefono 612345678
/profile set email nuevo@email.com
```

**Create Profile (Wizard):**
```
/profile create
```
**Interactive Flow:**
```
🔧 *Configuración de Perfil*

Vamos a crear tu perfil. Por favor, responde a las siguientes preguntas:

1️⃣ Nombre completo (ej: Juan Manuel Torales Chorne):
[User input]

2️⃣ DNI (ej: 44591820-H):
[User input]

... (continues for all required fields)
```

### Migration Strategy

#### Phase 1: Backward Compatibility
- Implement profile system alongside hardcoded data
- Check if user profile exists before injecting
- Fall back to hardcoded data if profile not found
- No breaking changes to existing users

#### Phase 2: Profile Creation
- Create profile for Juan Manuel from existing hardcoded data
- Test profile injection with one user
- Verify document generation works correctly

#### Phase 3: Multi-User Rollout
- Add profile creation wizard for new users
- Remove hardcoded data from templates (convert to markers)
- Update documentation

#### Phase 4: Cleanup
- Remove fallback to hardcoded data
- All users must have profiles
- Templates contain only [HARDCODED] markers (no actual data)

### Error Handling

#### Profile Not Found
```python
# In pipeline.py
profile = profile_manager.get_profile(user_id)
if not profile:
    await update.message.reply_text(
        "❌ *Perfil no encontrado*\n\n"
        "Por favor, crea tu perfil con /profile create antes de generar documentos.",
        parse_mode="Markdown"
    )
    return
```

#### Incomplete Profile
```python
# Validate required fields before document generation
required_fields = ['nombre', 'dni', 'email', 'telefono', 'direccion']
missing = [field for field in required_fields if not getattr(profile, field)]

if missing:
    await update.message.reply_text(
        f"❌ *Perfil incompleto*\n\n"
        f"Faltan los siguientes campos requeridos: {', '.join(missing)}\n\n"
        f"Completa tu perfil con /profile set",
        parse_mode="Markdown"
    )
    return
```

#### Supabase Unavailable
- Graceful degradation: Use in-memory cache
- Log warnings for administrators
- Notify users of temporary limitation

### Security Considerations

1. **Authorization:**
   - Users can only view/edit their own profiles
   - Admin commands for profile management (superuser)

2. **Data Privacy:**
   - Personal data stored encrypted at rest (Supabase)
   - No logging of sensitive information
   - GDPR compliance (right to deletion)

3. **Validation:**
   - DNI format validation (Spanish ID format)
   - Email format validation
   - Phone number format (Spanish mobile)

4. **Access Control:**
   - Profile queries filtered by telegram_user_id
   - No cross-user data leakage

### Testing Strategy

#### Unit Tests
- `test_user_profile_validation()` - DNI, email formats
- `test_profile_injection()` - Template marker replacement
- `test_profile_crud()` - Supabase CRUD operations

#### Integration Tests
- `test_profile_creation_wizard()` - Complete profile creation flow
- `test_document_generation_with_profile()` - End-to-end pipeline
- `test_multi_user_isolation()` - User A cannot access User B's profile

#### Manual Testing
1. Create profile for Juan Manuel
2. Generate denuncia with profile data
3. Verify document contains correct personal information
4. Create profile for another user
5. Verify documents use correct data per user

### Performance Considerations

1. **Caching:**
   - In-memory profile cache (dict: telegram_user_id -> UserProfile)
   - Cache TTL: 1 hour
   - Invalidate on profile update

2. **Lazy Loading:**
   - Load profiles only when needed (document generation)
   - Don't load on bot startup

3. **Batch Operations:**
   - Supabase queries already optimized with indexes
   - Retry logic handles transient failures

### Rollback Plan

If profile system causes issues:
1. Disable profile loading in pipeline.py (feature flag)
2. Fall back to hardcoded data in templates
3. Investigate and fix issues
4. Re-enable when resolved

Feature flag:
```python
USE_USER_PROFILES = os.getenv("USE_USER_PROFILES", "true").lower() == "true"
```

## Implementation Checklist

- [x] Design data model and schema
- [ ] Create UserProfile dataclass
- [ ] Implement Supabase user_profiles table
- [ ] Create UserProfileManager class
- [ ] Implement template profile injection
- [ ] Update pipeline to load profiles
- [ ] Create /profile command handler
- [ ] Add profile validation
- [ ] Implement profile creation wizard
- [ ] Add error handling for missing profiles
- [ ] Write unit tests
- [ ] Write integration tests
- [ ] Create migration from hardcoded data
- [ ] Update documentation
- [ ] Test with multiple users
- [ ] Deploy to production

## Future Enhancements

1. **Profile Import/Export:**
   - JSON export for backup
   - Bulk import for multiple delegates

2. **Profile Templates:**
   - Pre-fill profiles from company data
   - Shared company data across delegates

3. **Advanced Validation:**
   - DNI verification algorithm
   - Address validation via API
   - Company CIF verification

4. **Audit Log:**
   - Log profile changes to Supabase
   - Track who changed what and when

5. **Profile Versioning:**
   - Keep history of profile changes
   - Rollback to previous versions

## Conclusion

This user profile system will eliminate hardcoded data, enable multi-user support, and maintain the template-based architecture that ensures legal document quality. The implementation is phased to maintain backward compatibility and minimize disruption to existing users.
