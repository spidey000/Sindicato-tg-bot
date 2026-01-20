# Marxnager Testing Checklist - Multi-User Profile System

## Overview
This document outlines the testing strategy for the newly implemented multi-user profile system with Supabase integration.

## Prerequisites

### 1. Supabase Setup
- [ ] Create Supabase project (https://supabase.com)
- [ ] Run migration: `supabase/migrations/20260120_create_user_profiles.sql`
- [ ] Get SUPABASE_URL and SUPABASE_KEY (service_role key)
- [ ] Add to `.env` file:
  ```bash
  SUPABASE_URL=https://xxxxxxxxxxxxx.supabase.co
  SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
  ```

### 2. Bot Restart
- [ ] Stop bot container: `docker-compose down`
- [ ] Rebuild container: `docker-compose build`
- [ ] Start bot: `docker-compose up -d`
- [ ] Check logs for: `✅ Supabase client initialized successfully`

## Test Cases

### Test Suite 1: Profile Creation Wizard

**Test 1.1: Create profile via wizard**
- [ ] Send `/profile create` to bot
- [ ] Verify bot responds with welcome message and first question (Nombre)
- [ ] Answer all 21 questions with valid data
- [ ] Verify profile is created successfully
- [ ] Send `/profile` to view profile
- [ ] Verify all fields are displayed correctly

**Test 1.2: Cancel profile creation**
- [ ] Send `/profile create`
- [ ] Answer first question
- [ ] Send `/cancel`
- [ ] Verify profile creation is cancelled
- [ ] Verify no profile exists with `/profile`

**Test 1.3: Create duplicate profile**
- [ ] Create a profile for user
- [ ] Try to create another profile with `/profile create`
- [ ] Verify error message: "Perfil ya existe"

### Test Suite 2: Profile Field Updates

**Test 2.1: Update single field**
- [ ] Create profile
- [ ] Send `/profile set email test@example.com`
- [ ] Verify success message
- [ ] Send `/profile` to view profile
- [ ] Verify email field is updated

**Test 2.2: Update multiple fields**
- [ ] Update telefono field: `/profile set telefono 612345678`
- [ ] Update ciudad field: `/profile set ciudad BARCELONA`
- [ ] Verify both fields are updated

**Test 2.3: Invalid field name**
- [ ] Send `/profile set invalid_field value`
- [ ] Verify error message: "Campo desconocido"

**Test 2.4: Invalid DNI format**
- [ ] Send `/profile set dni 12345678` (missing letter)
- [ ] Verify validation error

**Test 2.5: Invalid phone format**
- [ ] Send `/profile set telefono 12345678` (wrong prefix)
- [ ] Verify validation error

**Test 2.6: Update profile without creating one**
- [ ] Delete profile or use new user
- [ ] Send `/profile set email test@example.com`
- [ ] Verify error: "Perfil no encontrado"

### Test Suite 3: Profile Display

**Test 3.1: View existing profile**
- [ ] Create profile
- [ ] Send `/profile`
- [ ] Verify all sections are displayed:
  - [ ] Personal data (Nombre, DNI, Email, Teléfono)
  - [ ] Address (Dirección, CP, Ciudad, Provincia)
  - [ ] Employment (Empresa, Centro, Puesto, NAF, Fecha de alta)
  - [ ] Company data (CIF, Dirección, Actividad, Trabajadores, Horario)

**Test 3.2: View non-existent profile**
- [ ] Use user without profile
- [ ] Send `/profile`
- [ ] Verify error: "Perfil no encontrado"
- [ ] Verify suggestion to use `/profile create`

### Test Suite 4: Profile Deletion

**Test 4.1: Delete existing profile**
- [ ] Create profile
- [ ] Send `/profile delete`
- [ ] Verify success message
- [ ] Send `/profile` to verify profile is gone

**Test 4.2: Delete non-existent profile**
- [ ] Use user without profile
- [ ] Send `/profile delete`
- [ ] Verify error: "Perfil no encontrado"

### Test Suite 5: Profile Injection in Documents

**Test 5.1: Generate denuncia with profile**
- [ ] Create profile for user
- [ ] Send `/denuncia Test case`
- [ ] Let document generation complete
- [ ] Open generated Google Doc
- [ ] Verify profile data is injected:
  - [ ] Nombre appears correctly
  - [ ] DNI appears correctly
  - [ ] Email appears correctly
  - [ ] Teléfono appears correctly
  - [ ] Dirección appears correctly
  - [ ] All company data appears correctly

**Test 5.2: Generate demanda with profile**
- [ ] Create profile for user
- [ ] Send `/demanda Test case`
- [ ] Let document generation complete
- [ ] Open generated Google Doc
- [ ] Verify profile data is injected correctly

**Test 5.3: Generate email with profile**
- [ ] Create profile for user
- [ ] Send `/email Test case`
- [ ] Let document generation complete
- [ ] Open generated Google Doc
- [ ] Verify profile data is injected correctly

**Test 5.4: Generate document without profile**
- [ ] Delete user profile or use new user
- [ ] Send `/denuncia Test case`
- [ ] Let document generation complete
- [ ] Open generated Google Doc
- [ ] Verify [HARDCODED] markers are NOT replaced
- [ ] Verify Juan Manuel's hardcoded data appears

### Test Suite 6: Multi-User Scenarios

**Test 6.1: Two different users**
- [ ] Create profile for User A with different data
- [ ] Create profile for User B with different data
- [ ] Generate document as User A
- [ ] Verify User A's data is in document
- [ ] Generate document as User B
- [ ] Verify User B's data is in document
- [ ] Verify data is different between documents

**Test 6.2: Profile isolation**
- [ ] User A updates their profile
- [ ] User B views their profile
- [ ] Verify User B's profile is unchanged

### Test Suite 7: Error Handling

**Test 7.1: Supabase not configured**
- [ ] Remove SUPABASE_URL and SUPABASE_KEY from .env
- [ ] Restart bot
- [ ] Send `/profile`
- [ ] Verify error: "Sistema de perfiles no disponible"

**Test 7.2: Supabase connection failure**
- [ ] Configure invalid SUPABASE_URL
- [ ] Restart bot
- [ ] Send `/profile create`
- [ ] Verify graceful error handling
- [ ] Check logs for error details

**Test 7.3: Retry logic**
- [ ] Simulate network timeout during profile creation
- [ ] Verify retry mechanism activates
- [ ] Verify exponential backoff works

### Test Suite 8: Data Validation

**Test 8.1: Required fields**
- [ ] Try to create profile with empty nombre
- [ ] Verify validation error: "Campo requerido faltante: nombre"

**Test 8.2: Email format**
- [ ] Try invalid email: `invalid-email`
- [ ] Verify validation error: "Email con formato inválido"

**Test 8.3: Postal code format**
- [ ] Try invalid CP: `1234` (4 digits)
- [ ] Verify validation error: "Código postal inválido"

**Test 8.4: Company CIF format**
- [ ] Try invalid CIF: `12345678` (missing letter)
- [ ] Verify validation error: "CIF con formato inválido"

### Test Suite 9: Cache Performance

**Test 9.1: Profile caching**
- [ ] Create profile
- [ ] Send `/profile` multiple times quickly
- [ ] Verify cache hit in logs: "Profile cache hit for user X"
- [ ] Verify response time is fast

**Test 9.2: Cache invalidation**
- [ ] Create profile
- [ ] Update profile field: `/profile set email new@email.com`
- [ ] Verify cache is invalidated in logs
- [ ] Send `/profile` to view profile
- [ ] Verify updated data is displayed

### Test Suite 10: Integration with History

**Test 10.1: Profile creation logged to history**
- [ ] Create profile
- [ ] Send `/history`
- [ ] Verify profile creation event is logged

**Test 10.2: Profile updates logged to history**
- [ ] Update profile field
- [ ] Send `/history`
- [ ] Verify update event is logged

## Success Criteria

### Must Pass (Critical)
- ✅ Profile creation wizard works end-to-end
- ✅ Profile data is correctly injected into documents
- ✅ Multi-user isolation works (User A's data doesn't leak to User B)
- ✅ Validation prevents invalid data
- ✅ Error handling is graceful

### Should Pass (Important)
- ✅ Profile updates work correctly
- ✅ Profile display shows all fields
- ✅ Cache improves performance
- ✅ Integration with history logging

### Nice to Have (Optional)
- ✅ Delete profile works
- ✅ Retry logic handles transient failures
- ✅ Cancel profile creation works

## Test Data

### Valid Test Profile
```
Nombre: MARÍA GARCÍA LÓPEZ
DNI: 12345678-Z
Email: maria.garcia@example.com
Teléfono: 611223344
Dirección: CALLE EJEMPLO 123, 1A
Código Postal: 28010
Ciudad: MADRID
Provincia: MADRID
NAF: 28/12345678/90
Fecha de alta: 15/03/2020
Centro de trabajo: AEROPUERTO ADOLFO SUÁREZ MADRID - BARAJAS
Puesto: Delegada de Sindicales
Empresa nombre: IBERIA AIRLINES
Empresa CIF: B28123456
Empresa dirección: AVENIDA DE LA HISPANIDAD 1
Empresa CP: 28042
Empresa ciudad: MADRID
Empresa provincia: MADRID
Empresa actividad: TRANSPORTE DE PASAJEROS POR VÍA AÉREA
Empresa CCC: 2801234567890
Empresa trabajadores: 150
Empresa horario: 06.00 a 23.59
```

## Notes

### Current Limitations
1. RLS policies use JWT claims - may not work with service_role key
2. Sample profile uses telegram_user_id=0 (should be updated)
3. In-memory fallback means profiles are lost on restart if Supabase fails

### Future Improvements
1. Add profile photo support
2. Add multiple workplaces per user
3. Add profile export/import functionality
4. Add profile history/audit log
5. Add profile templates for common companies

## Test Execution Log

### Session 1: 2026-01-20
- [ ] Supabase project setup
- [ ] Migration execution
- [ ] Bot restart and verification
- [ ] Profile creation wizard test
- [ ] Document generation test

### Session 2: TBD
- [ ] Multi-user scenarios
- [ ] Error handling tests
- [ ] Performance tests
