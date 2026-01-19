# Marxnager - Comprehensive Technical Specification
**Version:** 1.0
**Date:** January 19, 2026
**Status:** Pilot Testing Phase

---

## Executive Summary

Marxnager is a **Telegram-based legal document automation system** designed for Spanish labor union delegates at Madrid-Barajas Airport (Skyway ANS company). The bot combines multiple AI services (Perplexity for legal research, OpenRouter LLMs for document generation) with cloud storage (Google Drive, Google Docs, Notion) to automate the creation of professional legal documents including ITSS complaints, judicial demands, and corporate HR communications.

**Current Status:** Pilot testing with small group of delegates
**Deployment:** Docker containerized, manual deployment process
**Primary User:** Juan Manuel Torales Chorne (MVP single-user scope)
**Next Milestone:** Complete demanda pipeline and implement refactoring before adding new features

---

## Table of Contents

1. [Architecture Overview](#1-architecture-overview)
2. [Core Features](#2-core-features)
3. [Technical Stack](#3-technical-stack)
4. [Data Flow & Pipeline](#4-data-flow--pipeline)
5. [External Integrations](#5-external-integrations)
6. [Configuration Management](#6-configuration-management)
7. [Current Implementation Status](#7-current-implementation-status)
8. [Technical Debt & Known Issues](#8-technical-debt--known-issues)
9. [Refactoring Priorities](#9-refactoring-priorities)
10. [Roadmap](#10-roadmap)
11. [Architecture Decision Records](#11-architecture-decision-records)

---

## 1. Architecture Overview

### 1.1 System Type

**Hybrid AI-Orchestrated Document Generation System**
- Multi-stage LLM pipeline (Research → Generation → Verification → Refinement)
- Agent-based architecture with specialized legal personas
- Atomic transaction pattern with automatic rollback
- Cloud-native storage integration

### 1.2 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     TELEGRAM INTERFACE                       │
│              /denuncia | /demanda | /email | /history       │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
              ┌─────────────────────┐
              │  Authorization      │
              │  (Authorized Users) │
              └─────────┬───────────┘
                        │
                        ▼
              ┌─────────────────────┐
              │   Session Manager   │
              │  (IDLE / EDITING)   │
              └─────────┬───────────┘
                        │
           ┌────────────┴────────────┐
           │                         │
           ▼                         ▼
    ┌──────────────┐        ┌──────────────────┐
    │DOCUMENT PIPELINE│      │ PRIVATE MESSAGE  │
    │  (7 Steps)     │      │ HANDLER          │
    └──────┬─────────┘        └────────┬─────────┘
           │                          │
           ├──────────┬──────────┬─────┘
           │          │          │
           ▼          ▼          ▼
    ┌─────────┐ ┌──────────┐ ┌──────────┐
    │ DRIVE   │ │  DOCS    │ │  NOTION  │
    │Storage  │ │Editing   │ │Database  │
    └────┬────┘ └─────┬────┘ └────┬─────┘
         │            │            │
         └────────────┼────────────┘
                      │
                      ▼
        ┌─────────────────────────────────┐
        │      PROGRESS TRACKING          │
        │  Real-time Telegram updates     │
        │  ⬜ → ⏳ → ✅ / ❌              │
        └─────────────────────────────────┘
                      │
                      ▼
        ┌─────────────────────────────────┐
        │      ROLLBACK MANAGER           │
        │  Atomic transaction cleanup     │
        └─────────────────────────────────┘
```

### 1.3 Directory Structure

```
C:\Users\hp\Documents\CODE\Sindicato-tg-bot-1/
├── src/
│   ├── agents/              # AI agent personas (Inspector, Litigante, Comunicador)
│   │   ├── base.py          # Abstract base with verification workflow
│   │   ├── inspector.py     # ITSS complaint agent
│   │   ├── litigante.py     # Judicial demand agent
│   │   ├── comunicador.py   # Corporate email agent
│   │   └── orchestrator.py  # Agent selector based on command
│   ├── integrations/        # External service clients
│   │   ├── notion_client.py      # Notion database operations
│   │   ├── drive_client.py       # Google Drive folder management
│   │   ├── docs_client.py        # Google Docs creation/updates
│   │   ├── openrouter_client.py  # LLM API (DeepSeek, Mistral, etc.)
│   │   ├── perplexity_client.py  # Legal research API
│   │   ├── auth_helper.py        # Google OAuth credentials
│   │   └── cleanup_helper.py     # Rollback utilities
│   ├── data/                # Document templates
│   │   ├── demanda_template.md   # Judicial demand template
│   │   ├── itss_template.md      # ITSS complaint template
│   │   └── email_template.md     # Corporate email template
│   ├── main.py              # Application entry point
│   ├── handlers.py          # Telegram command handlers (950+ lines)
│   ├── config.py            # Environment configuration
│   ├── utils.py             # Progress tracking, rollback, ID generation
│   ├── template_loader.py   # Template loading utility
│   ├── middleware.py        # Authorization decorator
│   ├── session_manager.py   # User session state management
│   └── logging_config.py    # Logging setup
├── tests/                   # 40+ test files (no CI/CD automation)
├── scripts/                 # Maintenance and diagnostic scripts
├── logs/                    # Application logs (volume mounted)
├── conductor/               # Project management tracks
├── .env                     # Secrets (not committed)
├── Dockerfile               # Container definition (python:3.11-slim)
├── docker-compose.yml       # Orchestration
├── requirements.txt         # Python dependencies
├── PRD.md                   # Product Requirements Document
└── README.md                # User documentation
```

---

## 2. Core Features

### 2.1 Document Generation Pipelines

The system supports three document types, each unified under a single 7-step pipeline:

#### 2.1.1 `/denuncia` - ITSS Labor Complaint
**Target:** Inspección Provincial de Trabajo y Seguridad Social de Madrid
**Purpose:** Report labor law violations to labor inspectorate
**Template:** `src/data/itss_template.md`
**Case ID Prefix:** `D-2026-XXX`

**Key Features:**
- Chronological fact listing
- Legal grounding with statutes and case law
- Evidence document attachment
- Specific enforcement requests

#### 2.1.2 `/demanda` - Judicial Labor Demand
**Target:** Juzgado de lo Social de Madrid
**Purpose:** File formal lawsuit against employer for labor violations
**Template:** `src/data/demanda_template.md`
**Case ID Prefix:** `J-2026-XXX`

**Key Features:**
- Court-formatted legal demand
- Plaintiff/Defendant data (hardcoded for MVP)
- Procedural modality selection
- Specific legal petitions
- Conciliation paper reference

#### 2.1.3 `/email` - Corporate HR Communication
**Target:** Skyway HR Department
**Purpose:** Formal professional communication regarding workplace issues
**Template:** `src/data/email_template.md`
**Case ID Prefix:** `E-2026-XXX`

**Key Features:**
- Professional, constructive tone (non-aggressive)
- Context + exposition + legal grounding + request + deadline
- 250-400 word recommended length
- Formal greeting and signature

### 2.2 Unified Pipeline Architecture (Current Branch)

**All three document types follow the same 7-step pipeline:**

```
STEP 1: INITIALIZATION
  ├─ Generate unique case ID (D-2026-001, J-2026-001, E-2026-001)
  ├─ Load appropriate template from src/data/
  └─ Initialize ProgressTracker + RollbackManager

STEP 2: LEGAL RESEARCH (Perplexity AI - sonar-pro)
  ├─ Query Spanish labor law database
  ├─ Context: Madrid-Barajas SDP + XX Convenio Colectivo
  └─ Returns: Normativa, Jurisprudencia, Argumentación, Plazos

STEP 3: DOCUMENT GENERATION (OpenRouter - DeepSeek R1)
  ├─ Combine template + user context + research
  ├─ Fill {{PLACEHOLDER}} fields while preserving [HARDCODED] data
  ├─ Fallback to Gemma 3 if DeepSeek fails
  └─ Returns: {summary, content, thesis, specific_point, area}

STEP 4: GOOGLE DRIVE STRUCTURE
  ├─ Create case folder in type-specific parent
  │   ├─ DRIVE_FOLDER_DENUNCIAS (for /denuncia)
  │   ├─ DRIVE_FOLDER_DEMANDAS (for /demanda)
  │   └─ DRIVE_FOLDER_EMAILS (for /email)
  └─ Create subfolders: "Pruebas", "Respuestas"/"Procedimiento"

STEP 5: GOOGLE DOCS CREATION
  ├─ Create editable Google Doc with generated content
  ├─ Move document to Drive folder
  └─ Return Doc ID for linking

STEP 6: NOTION DATABASE ENTRY
  ├─ Create database page with properties (ID, Status, Type, Links)
  ├─ Link Drive folder + Google Doc
  ├─ Append research + draft as collapsible toggles
  └─ Map status/types to Notion database schema

STEP 7: FINALIZATION
  ├─ Send summary card to Telegram with all links
  ├─ Provide deep link to continue in private chat
  └─ Set session state to EDITING_CASE
```

**Progress Tracking:**
- Real-time Telegram message updates with checkboxes
- State progression: ⬜ (pending) → ⏳ (in_progress) → ✅ (completed) / ❌ (failed)
- Timer tracking for each step
- Final summary with all asset links

**Rollback Mechanism:**
- Automatic cleanup on any step failure
- Tracked artifacts: Notion page, Drive folder, Google Doc
- Atomic transaction guarantee (all-or-nothing)

### 2.3 Private Message Refinement Loop

**After document creation, delegates can:**

1. **Send text messages** in private chat to refine document content
2. **Upload files** (photos, PDFs, audio) as evidence
3. **Automatic updates** via agent's `refine_draft_with_feedback()` method

**Flow:**
```
Private Message (Telegram)
         ↓
SessionManager checks active case
         ↓
Route to appropriate handler:
  ├─ Text → Refine document content (LLM)
  ├─ File → Upload to Drive Pruebas folder
  └─ Audio → Upload to Drive Pruebas folder
         ↓
Update Google Doc with new content
         ↓
Update Notion with file links
```

**Current User Feedback:** "Works well" - delegates actively use refinement

### 2.4 Case Management Commands

#### `/status <ID> <STATE>`
**Purpose:** Update Notion case status
**Usage:** `/status D-2026-001 En edición`
**Status Mapping:**
- "Borrador" → "Pendiente de hacer"
- "En edición" → "En progreso"
- "Listo" → "En revisión"
- "Enviado" → "Presentada"

#### `/update`
**Purpose:** List active cases from Notion database
**Restriction:** Private chat only
**Returns:** All cases with status != "Presentada"

#### `/stop`
**Purpose:** Exit EDITING_CASE mode
**Effect:** Disconnects user from active case

#### `/start case_<ID>`
**Purpose:** Deep linking to reconnect to active case
**Example:** `/start case_D-2026-001`
**Effect:** Sets session to EDITING_CASE for specified case

#### `/log`
**Purpose:** Download system logs
**Restriction:** Admin users only
**Returns:** Last 10MB of logs as file

### 2.5 Feature in Progress: `/history` Command

**Purpose:** Event logging system for building chronological timeline of labor incidents

**Implementation Status:** In development

**Technology Stack:**
- Database: Supabase (PostgreSQL)
- Client Library: supabase-py
- Status: Project already setup, credentials available

**Schema:**
- Basic fields: `date` + `event_text`
- Simple insert/query operations
- Real-time logging workflow

**Use Case:**
Delegates log incidents as they happen to build historical evidence for future legal cases

**Relationship to Notion:**
- **Complementary purposes** (hybrid approach is correct)
- Notion: Active case management
- Supabase: Historical event logging
- No migration planned - both systems serve distinct needs

---

## 3. Technical Stack

### 3.1 Core Technologies

| Component | Technology | Version | Rationale |
|-----------|-----------|---------|-----------|
| **Language** | Python | 3.11+ | AI/ML ecosystem, async support |
| **Bot Framework** | python-telegram-bot | 20.x | Mature, well-documented, async |
| **Container** | Docker | - | python:3.11-slim base image |
| **Orchestration** | docker-compose | - | Single-node deployment |

### 3.2 AI/ML Services

| Service | Provider | Model | Purpose | Fallback |
|---------|----------|-------|---------|----------|
| **Legal Research** | Perplexity AI | sonar-pro | Spanish labor law queries | Primary/fallback API key rotation |
| **Document Generation** | OpenRouter | deepseek/deepseek-r1-0528:free | Template filling, content generation | google/gemma-3-27b-it:free |
| **JSON Repair** | OpenRouter | qwen/qwen3-4b:free | Fix malformed LLM JSON responses | None (final fallback) |

**Budget Constraint:** Free tier models required due to union budget limitations
**Quality Assessment:** Acceptable latency - quality non-negotiable for legal docs

### 3.3 Cloud Services

| Service | Provider | Purpose | Rate Limits |
|---------|----------|---------|-------------|
| **Case Database** | Notion | Case tracking, document linking | ~3 req/sec (no issues in practice) |
| **File Storage** | Google Drive | Evidence uploads, folder organization | Quota-based (no issues) |
| **Document Editing** | Google Docs | Collaborative document editing | Quota-based (no issues) |
| **Event Logging** | Supabase | Historical incident timeline | Not yet in production |

### 3.4 Dependencies

**File:** `requirements.txt`

```
python-telegram-bot==20.*
python-dotenv==1.0.*
notion-client==2.*
google-api-python-client==2.*
google-auth-httplib2==0.*
google-auth-oauthlib==1.*
aiohttp==3.*
httpx==0.*
# openai==1.*  # Temporarily removed due to build issues
```

**Note:** Node.js dependency (`google-gemini-wrapper`) exists but is unused - should be removed

---

## 4. Data Flow & Pipeline

### 4.1 Complete Data Flow Diagram

```
┌──────────────────────────────────────────────────────────────┐
│                    TELEGRAM USER INPUT                       │
│                 /denuncia | /demanda | /email                │
└──────────────────────────┬───────────────────────────────────┘
                           │
                           ▼
              ┌─────────────────────┐
              │   AUTHORIZATION     │
              │  @restricted check  │
              └─────────┬───────────┘
                        │
                        ▼
              ┌─────────────────────┐
              │   SESSION MANAGER   │
              │  Set: IDLE → active │
              └─────────┬───────────┘
                        │
                        ▼
        ┌───────────────────────────────────────┐
        │     STEP 1: INITIALIZATION            │
        │  - generate_case_id()                 │
        │  - template_loader.get_template()     │
        │  - ProgressTracker(message)           │
        │  - RollbackManager()                  │
        └───────────────┬───────────────────────┘
                        │
                        ▼
        ┌───────────────────────────────────────┐
        │     STEP 2: LEGAL RESEARCH            │
        │  perplexity.research_case()           │
        │  - Context: Madrid-Barajas SDP        │
        │  - Convenio: BOE-A-2023-6346          │
        │  - Returns: {Normativa, Jurisprudencia}│
        └───────────────┬───────────────────────┘
                        │
                        ▼
        ┌───────────────────────────────────────┐
        │     STEP 3: DOCUMENT GENERATION       │
        │  openrouter.generate_from_template()  │
        │  - Template + Context + Research      │
        │  - Fill {{PLACEHOLDER}} fields        │
        │  - Preserving [HARDCODED] data        │
        │  - Primary: DeepSeek R1               │
        │  - Fallback: Gemma 3                  │
        │  - Returns: {summary, content, ...}   │
        └───────────────┬───────────────────────┘
                        │
        ┌───────────────┼───────────────┐
        │               │               │
        ▼               ▼               ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│   DRIVE      │ │    DOCS      │ │    NOTION    │
│ create_case  │ │ create_draft │ │ create_page  │
│ _folder()    │ │ _document()  │ │ ()           │
│              │ │              │ │              │
│ - Type       │ │ - Title      │ │ - ID         │
│   specific   │ │ - Content   │ │ - Status     │
│   parent     │ │ - Folder ID │ │ - Type       │
│ - Subfolders │ │              │ │ - Links     │
│   (Pruebas,  │ │              │ │ - Toggles   │
│    Respuestas│ │              │ │   (research,│
│    /         │ │              │ │    draft)   │
│    Procedim.) │ │              │ │              │
└──────┬───────┘ └──────┬───────┘ └──────┬───────┘
       │                │                │
       └────────────────┼────────────────┘
                        │
                        ▼
        ┌───────────────────────────────────────┐
        │     STEP 7: FINALIZATION             │
        │  - Notion append final links         │
        │  - Send Telegram summary card        │
        │  - Create deep link (/start case_ID) │
        │  - Session: IDLE → EDITING_CASE      │
        └───────────────┬───────────────────────┘
                        │
                        ▼
        ┌───────────────────────────────────────┐
        │     PRIVATE MESSAGE HANDLING          │
        │  (User sends text/files)              │
        │  - Refine content (LLM)               │
        │  - Upload evidence (Drive)            │
        │  - Update Docs + Notion               │
        └───────────────────────────────────────┘
```

### 4.2 Error Handling & Rollback

**RollbackManager Triggers:**
- Any step raises exception
- API rate limits exceeded
- Network timeout
- Malformed LLM response (after repair attempts)

**Rollback Process:**
```
Failure detected
        ↓
RollbackManager.trigger_failure()
        ↓
For each tracked artifact:
  - Notion page → notion_client.delete_page()
  - Drive folder → drive_client.delete_folder()
  - Google Doc → docs_client.delete_document()
        ↓
Send error report to Telegram
        ↓
Log full error context
```

**Limitations:**
- No retry logic for transient failures
- No partial upload handling (e.g., 3 of 5 photos)
- No concurrent operation protection
- **User feedback:** Haven't encountered "ghost artifact" problems

### 4.3 Session State Management

**Current Implementation:** In-memory dictionary

```python
# src/session_manager.py
sessions = {
    user_id: {
        'state': 'IDLE' | 'EDITING_CASE',
        'case_id': 'D-2026-001' | None
    }
}
```

**Known Limitation:** Lost on container restart
**User Feedback:** Low restart frequency - not a priority issue
**Planned Improvement:** TODO: Redis for production (long-term goal)

**Session Lifecycle:**
```
IDLE → (command triggered) → EDITING_CASE
  ↑                            ↓
  └─────── (/stop or timeout) ─┘
```

---

## 5. External Integrations

### 5.1 Notion Integration

**File:** `src/integrations/notion_client.py`

**Database Schema:**
- **ID:** Case identifier (D-2026-001, J-2026-001)
- **Status:** Borrador, En edición, Listo, Enviado
- **Type:** ITSS (Denuncia), Defensor del pueblo (Demanda), None (Email)
- **Links:** Drive folder, Google Doc

**Status Mapping:**
```python
status_map = {
    "Borrador": "Pendiente de hacer",
    "En edición": "En progreso",
    "Listo": "En revisión",
    "Enviado": "Presentada"
}

type_map = {
    "Denuncia ITSS": "ITSS",
    "Demanda Judicial": "Defensor del pueblo",
    "Email RRHH": None
}
```

**Key Methods:**
- `create_case_page(case_id, case_type, status, links)` - Create new case
- `get_last_case_id(case_type)` - Retrieve latest ID for auto-increment
- `query_active_cases()` - Get all non-"Presentada" cases
- `append_content_blocks(page_id, research, draft)` - Add collapsible toggles
- `delete_page(page_id)` - Rollback support

**Rationale for Notion:**
- User familiarity (delegates already use Notion)
- No-code flexibility (easy field modification)
- Visual interface for case tracking

**Trade-offs Accepted:**
- API rate limits (~3 req/sec)
- Query latency vs. direct database
- Data ownership (hosted on Notion servers)

### 5.2 Google Drive Integration

**File:** `src/integrations/drive_client.py`

**Folder Structure:**
```
DRIVE_FOLDER_DENUNCIAS/  (from env)
  └── D-2026-001 - Summary/
      ├── Pruebas/          (Evidence uploads)
      └── Respuestas/       (ITSS responses)

DRIVE_FOLDER_DEMANDAS/  (from env)
  └── J-2026-001 - Summary/
      ├── Pruebas/
      └── Procedimiento/    (Court proceedings)

DRIVE_FOLDER_EMAILS/  (from env)
  └── E-2026-001 - Summary/
```

**Key Methods:**
- `create_case_folder(case_id, case_type, summary)` - Create folder structure
- `upload_file(file_path, folder_id)` - Upload evidence
- `find_docs_in_folder(folder_id)` - Locate documents
- `delete_folder(folder_id)` - Rollback support

**File Upload Support:**
- Photos (Telegram auto-download)
- PDFs
- Audio files

**User Feedback:** File uploads work well - no pain points reported

### 5.3 Google Docs Integration

**File:** `src/integrations/docs_client.py`

**Key Methods:**
- `create_draft_document(title, content, folder_id)` - Create + move
- `read_document_content(document_id)` - Retrieve full text
- `update_document_content(document_id, new_content)` - Refinement
- `append_text_annotation(document_id, text)` - Add notes

**Rationale for Google Docs:**
- Collaborative editing (delegates can modify)
- Better than PDF generation for iterative refinement
- Native Google Workspace integration

**User Feedback:** Docs preferred over PDF - collaborative editing is more valuable

### 5.4 OpenRouter LLM Integration

**File:** `src/integrations/openrouter_client.py`

**Model Hierarchy:**
```python
PRIMARY_DRAFT_MODEL = "deepseek/deepseek-r1-0528:free"
FALLBACK_DRAFT_MODEL = "google/gemma-3-27b-it:free"
REPAIR_MODEL = "qwen/qwen3-4b:free"
```

**Key Methods:**
- `generate_from_template(template, context, research)` - Template-based generation
- `refine_draft(current_content, feedback)` - Iterative improvement
- `repair_json(malformed_json)` - Fix LLM errors

**Special Features:**
- Automatic fallback on API failures
- 3-retry logic with exponential backoff
- JSON repair mechanism for malformed responses
- Model-specific max_tokens configuration
- Template placeholder preservation ([HARDCODED] data)

**Performance:**
- **Bottleneck:** LLM generation is slowest step
- **User Feedback:** Acceptable latency - quality over speed

**Template System:**
- Combines template + user context + Perplexity research
- Fills {{PLACEHOLDER}} fields intelligently
- Preserves [HARDCODED] data (DNI, addresses, etc.)
- Maintains legal document structure

### 5.5 Perplexity AI Integration

**File:** `src/integrations/perplexity_client.py`

**Model:** `sonar-pro` (online search-enabled)

**Research Context:**
```
- Fixed: Aeropuerto Adolfo Suárez Madrid-Barajas
- Service: Dirección de Plataforma (SDP)
- Collective Agreement: XX Convenio Colectivo Nacional de Empresas de Ingeniería (BOE-A-2023-6346)
- Dynamic: Document type (denuncia/demanda/email)
```

**Structured Output:**
```python
{
    "Normativa": "Applicable Spanish labor laws",
    "Jurisprudencia": "Relevant court cases",
    "Argumentación": "Legal reasoning for claims",
    "Plazos": "Statute of limitations, deadlines"
}
```

**Key Methods:**
- `research_case(document_type, user_context)` - Generate research
- Primary/fallback API key rotation

**Architectural Decision:**
- **Moved from verification (after generation) to research (before generation)**
- **Rationale:** Provides better context for template filling
- **Trade-off:** Cannot verify generated claims cite real laws
- **User Feedback:** Before generation is better - research provides better context

---

## 6. Configuration Management

### 6.1 Environment Variables

**File:** `.env` (not committed to git)

```ini
# ==================================================
# TELEGRAM CONFIGURATION
# ==================================================
BOT_TOKEN=<telegram_bot_token>
AUTHORIZED_USER_IDS=123456789,987654321
LOG_LEVEL=INFO

# ==================================================
# OPENROUTER (LLM GENERATION)
# ==================================================
OPENROUTER_API_KEY=<openrouter_api_key>
PRIMARY_DRAFT_MODEL=deepseek/deepseek-r1-0528:free
FALLBACK_DRAFT_MODEL=google/gemma-3-27b-it:free
REPAIR_MODEL=qwen/qwen3-4b:free

# ==================================================
# PERPLEXITY AI (LEGAL RESEARCH)
# ==================================================
PERPLEXITY_API_KEY_PRIMARY=<perplexity_api_key_1>
PERPLEXITY_API_KEY_FALLBACK=<perplexity_api_key_2>

# ==================================================
# NOTION (CASE DATABASE)
# ==================================================
NOTION_TOKEN=<notion_integration_token>
NOTION_DATABASE_ID=<notion_database_id>

# ==================================================
# GOOGLE WORKSPACE
# ==================================================
GOOGLE_DRIVE_CREDENTIALS_PATH=credentials.json
DRIVE_FOLDER_DENUNCIAS=<drive_folder_id_denuncias>
DRIVE_FOLDER_DEMANDAS=<drive_folder_id_demandas>
DRIVE_FOLDER_EMAILS=<drive_folder_id_emails>

# ==================================================
# SUPABASE (EVENT LOGGING - In Development)
# ==================================================
SUPABASE_URL=<supabase_project_url>
SUPABASE_KEY=<supabase_anon_key>

# ==================================================
# DEBUGGING
# ==================================================
SAVE_RAW_LLM_RESPONSES=False
```

### 6.2 Configuration Loading

**File:** `src/config.py`

```python
from dotenv import load_dotenv
import os

load_dotenv()

class Config:
    # Telegram
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    AUTHORIZED_USER_IDS = [
        int(uid) for uid in os.getenv("AUTHORIZED_USER_IDS", "").split(",")
    ]

    # OpenRouter
    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
    PRIMARY_DRAFT_MODEL = os.getenv("PRIMARY_DRAFT_MODEL")
    FALLBACK_DRAFT_MODEL = os.getenv("FALLBACK_DRAFT_MODEL")
    REPAIR_MODEL = os.getenv("REPAIR_MODEL")

    # Perplexity
    PERPLEXITY_API_KEY_PRIMARY = os.getenv("PERPLEXITY_API_KEY_PRIMARY")
    PERPLEXITY_API_KEY_FALLBACK = os.getenv("PERPLEXITY_API_KEY_FALLBACK")

    # Notion
    NOTION_TOKEN = os.getenv("NOTION_TOKEN")
    NOTION_DATABASE_ID = os.getenv("NOTION_DATABASE_ID")

    # Google Workspace
    GOOGLE_DRIVE_CREDENTIALS_PATH = os.getenv("GOOGLE_DRIVE_CREDENTIALS_PATH")
    DRIVE_FOLDER_DENUNCIAS = os.getenv("DRIVE_FOLDER_DENUNCIAS")
    DRIVE_FOLDER_DEMANDAS = os.getenv("DRIVE_FOLDER_DEMANDAS")
    DRIVE_FOLDER_EMAILS = os.getenv("DRIVE_FOLDER_EMAILS")

    # Supabase
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY")

    # Debug
    SAVE_RAW_LLM_RESPONSES = os.getenv("SAVE_RAW_LLM_RESPONSES", "False") == "True"
```

### 6.3 Authorization

**File:** `src/middleware.py`

```python
from functools import wraps
from src.config import AUTHORIZED_USER_IDS
import logging

def restricted(func):
    @wraps(func)
    async def wrapped(update, context, *args, **kwargs):
        user_id = update.effective_user.id

        if user_id not in AUTHORIZED_USER_IDS:
            logger.warning(f"Unauthorized access attempt: {user_id}")
            await update.message.reply_text(
                "⛔ You are not authorized to use this bot."
            )
            return

        return await func(update, context, *args, **kwargs)

    return wrapped
```

**Current Implementation:** Informative rejection message
**Alternative:** Silent ignore (commented out in code)

---

## 7. Current Implementation Status

### 7.1 Current Branch

**Branch:** `feature/demanda-pipeline`

**Recent Commits:**
1. `3c8fdb71` - **feat(demanda):** Implement Perplexity→OpenRouter pipeline with template-based document generation
2. `858ca4ca` - **feat(demanda):** Add templates and initial setup for demanda pipeline

**Changed Files:**
- `PRD.md` - Major update (3452 lines removed - needs review)
- `src/data/demanda_template.md` - NEW (85 lines)
- `src/handlers.py` - Refactored demanda handler (+489 lines)
- `src/integrations/notion_client.py` - Added `append_content_blocks()`, `get_last_case_id()`
- `src/integrations/openrouter_client.py` - Model hierarchy fixes
- `src/integrations/perplexity_client.py` - Added `research_case()` method
- `src/utils.py` - Progress tracking improvements
- `src/template_loader.py` - Moved from `src/utils/template_loader.py` (git issue - see below)

### 7.2 Git Status Issues

**File Move Not Committed Properly:**
```
D src/utils/template_loader.py
?? src/template_loader.py
```

**Issue:** File was moved but git shows deletion without addition
**User Feedback:** "Oversight" - forgot to git add
**Impact:** May cause import errors if not updated everywhere
**Priority:** Git cleanup needed

### 7.3 Feature Status

| Feature | Status | Notes |
|---------|--------|-------|
| `/denuncia` pipeline | ✅ Complete | Working in production |
| `/demanda` pipeline | ✅ Complete | Newly implemented |
| `/email` pipeline | ✅ Complete | Working in production |
| `/status` command | ✅ Complete | Working |
| `/update` command | ✅ Complete | Private chat only |
| `/stop` command | ✅ Complete | Working |
| Deep linking | ✅ Complete | Works well - delegates use it |
| Refinement loop | ✅ Complete | Works well - delegates use it |
| File uploads | ✅ Complete | Works well - no pain points |
| Progress tracking | ✅ Complete | Current UX is best - real-time updates |
| Rollback manager | ✅ Complete | No ghost artifact issues |
| `/history` command | 🚧 In Progress | Supabase integration started |
| Multi-user support | 📋 Planned | Long-term goal |
| Redis sessions | 📋 Planned | Low priority (low restart frequency) |
| CI/CD pipeline | 📋 Planned | Immediate need |
| Monitoring/alerts | 📋 Planned | Immediate need |

### 7.4 Production Status

**Current Phase:** Pilot testing
**Deployment Method:** Manual
**User Base:** Small group of delegates
**Stability:** Stable - no critical issues

---

## 8. Technical Debt & Known Issues

### 8.1 Code Quality Issues

#### 8.1.1 handlers.py - 950 Lines
**Issue:** Monolithic file with repeated pipeline code
**User Feedback:** "Post-MVP refactoring" - will split after pipeline stabilizes
**Priority:** Medium (not a blocker yet)
**Planned Action:** Split into separate modules (denuncia_handler.py, demanda_handler.py, etc.)

#### 8.1.2 Template Loader Git Issue
**Issue:** File move not committed properly
**Status:** User acknowledged as oversight
**Priority:** High (git cleanup needed)
**Planned Action:** Fix git tracking with `git add src/template_loader.py`

#### 8.1.3 PRD.md Reduction
**Issue:** 3452 lines removed - unclear what was deleted
**User Feedback:** "Need to review" - should review what was deleted
**Priority:** Medium
**Impact:** May have removed valuable architectural decisions

#### 8.1.4 Missing Node.js Dependency
**Issue:** `package.json` contains `google-gemini-wrapper` (unused)
**Priority:** Low
**Planned Action:** Remove to reduce complexity

### 8.2 Architecture Issues

#### 8.2.1 Session Storage - In-Memory Only
**Issue:** Lost on container restart
**User Feedback:** Low restart frequency - not a priority
**Priority:** Low
**Planned Improvement:** TODO: Redis for production (long-term goal)

#### 8.2.2 Hardcoded User Data
**Issue:** Juan Manuel's personal data embedded in templates
**User Feedback:** Intentional MVP scope - single-user design
**Priority:** Medium (blocks multi-user support)
**Impact:** System cannot scale to other delegates

**Hardcoded Data:**
```markdown
# demanda_template.md
DNI: 44591820-H
Dirección: CALLE PLAYA DE ZARAUZ 18, 2C, 28042, MADRID
Fecha inicio: 17/01/2023
Empresa CIF: A86164894
```

**Planned Solution:** User profile system (Notion or Supabase)

#### 8.2.3 Error Recovery - Partial
**Issue:** No retry logic for API rate limits or transient failures
**User Feedback:** Needs improvement
**Priority:** High
**Impact:** Delegates don't get clear error messages when APIs fail

**Current Behavior:**
- LLM failures fall back but don't always notify user
- Notion/Drive rate limits cause immediate failure
- No exponential backoff for retries

**Planned Improvement:** Comprehensive retry strategy with backoff

### 8.3 Security Concerns

#### 8.3.1 Secret Management
**Issue:** Secrets in `.env` file with hardcoded paths
**User Feedback:** .env works for current deployment
**Priority:** Medium (acceptable risk for pilot phase)
**Planned Improvement:** Docker secrets or Vault for production

**Concerns:**
- `GOOGLE_DRIVE_CREDENTIALS_PATH=credentials.json` (hardcoded path)
- No rotation strategy for expired tokens
- API keys visible in logs if not redacted

#### 8.3.2 Authorization
**Issue:** No audit log for unauthorized attempts
**Current Behavior:** Logger warning only
**Priority:** Low
**Impact:** Cannot detect brute force attempts

#### 8.3.3 Secret Redaction
**Issue:** Risk of API keys leaking into logs
**Mitigation:** `SAVE_RAW_LLM_RESPONSES=False` in production
**Priority:** Medium
**Status:** Secret redaction system exists (implemented Jan 10, 2026)

### 8.4 Testing Gaps

#### 8.4.1 No CI/CD Automation
**Issue:** 40+ test files exist but not run automatically
**User Feedback:** "create ci/cd" - immediate need
**Priority:** High
**Current State:** Manual testing only
**Planned Action:** Implement automated testing pipeline

#### 8.4.2 Test Coverage
**Issue:** Coverage unclear - no integration tests for full pipeline
**Priority:** Medium
**Available Tests:**
- `test_agent_*.py` - Agent behavior tests
- `test_openrouter*.py` - LLM integration tests
- `test_perplexity*.py` - Research API tests
- `test_notion*.py` - Notion client tests
- `test_progress_*.py` - Progress tracking tests
- `test_e2e_rollback.py` - End-to-end failure scenarios
- `e2e_simulation.py` - Full pipeline simulation

### 8.5 Documentation Issues

#### 8.5.1 Missing API Documentation
**Issue:** No docstrings for many integration methods
**Priority:** Medium
**Impact:** Complex prompt engineering not documented

#### 8.5.2 Deployment Guide
**Issue:** DEPLOYMENT.md exists but very brief (1982 bytes)
**Missing Instructions:**
- Google Service Account setup
- Notion integration configuration
- Docker registry deployment
**Priority:** Low (manual deployment works)

### 8.6 Performance Bottlenecks

#### 8.6.1 LLM Generation Speed
**Issue:** DeepSeek R1 is slowest step in pipeline
**User Feedback:** Acceptable latency - quality over speed
**Priority:** Low
**Impact:** 30+ second generation time
**Mitigation:** Real-time progress updates manage UX

#### 8.6.2 Notion API Rate Limits
**Issue:** ~3 req/sec limit
**User Feedback:** No issues in practice (low concurrency)
**Priority:** Low
**Impact:** None with current user base

---

## 9. Refactoring Priorities

### 9.1 Immediate Blockers (Before New Features)

**User Feedback:** Refactoring is a blocker before adding /history and other features

#### 9.1.1 Split handlers.py
**Current State:** 950 lines with repeated pipeline code
**Priority:** High
**Planned Action:**
- Extract common pipeline logic into reusable function
- Split into separate modules by command type
- Create shared pipeline builder

**Target Structure:**
```
src/handlers/
├── __init__.py
├── base.py          # Common pipeline logic
├── denuncia.py      # /denuncia command
├── demanda.py       # /demanda command
├── email.py         # /email command
├── status.py        # /status command
└── history.py       # /history command (new)
```

#### 9.1.2 Extract Common Pipeline
**Current State:** Copy-paste pattern for denuncia/demanda/email
**Priority:** High
**Planned Action:** Create unified pipeline function

**Proposed Signature:**
```python
async def execute_document_pipeline(
    update: Update,
    context: Context,
    document_type: str,  # "denuncia" | "demanda" | "email"
    template_name: str,
    agent: BaseAgent,
    drive_folder_id: str
) -> str:  # Returns case_id
```

**Benefits:**
- Single source of truth for pipeline logic
- Easier to add new document types
- Consistent error handling

#### 9.1.3 Git Cleanup
**Issue:** template_loader.py move not committed
**Priority:** High
**Action Items:**
1. `git rm src/utils/template_loader.py`
2. `git add src/template_loader.py`
3. Update all import statements
4. Verify no broken imports

### 9.2 High Priority (Production Readiness)

#### 9.2.1 CI/CD Pipeline
**Current State:** Manual deployment
**Priority:** High (immediate need)
**Planned Action:** Automated testing and deployment

**Requirements:**
- Run tests on every commit
- Automated Docker build
- Deploy to staging/production
- Rollback capability

#### 9.2.2 Error Recovery & Retry Logic
**Current State:** No retry for API failures
**Priority:** High (needs improvement)
**Planned Action:** Comprehensive retry strategy

**Requirements:**
- Exponential backoff for Notion/Drive APIs
- Retry with user notification for LLM failures
- Clear error messages for delegates
- Partial failure handling (e.g., 3 of 5 photos)

#### 9.2.3 Monitoring & Alerts
**Current State:** Logs only - no alerts
**Priority:** High (alerts needed)
**Planned Action:** Production monitoring

**Requirements:**
- Alert on bot failures
- Track API success rates
- Monitor latency
- Alert on rate limit hits

### 9.3 Medium Priority (Future Scalability)

#### 9.3.1 Multi-User Configuration
**Current State:** Hardcoded single-user data
**Priority:** Medium (blocks scaling)
**Timeline:** Long-term goal
**Planned Action:** User profile system

**Options:**
1. Notion database table for user profiles
2. Supabase user profiles (leverage existing infrastructure)
3. Environment variable per user (not scalable)

**Required Fields:**
- DNI/NIF
- Full name
- Address
- Phone number
- Start date
- Company data (if different)

#### 9.3.2 Redis Session Storage
**Current State:** In-memory sessions
**Priority:** Medium (low restart frequency makes it low priority)
**Timeline:** Long-term goal
**Planned Action:** Migrate to Redis

**Benefits:**
- Persist across container restarts
- Shared sessions across containers (horizontal scaling)
- TTL for automatic cleanup

### 9.4 Low Priority (Technical Debt)

#### 9.4.1 Remove Unused Dependencies
**Issue:** Node.js dependency unused
**Priority:** Low
**Action:** Remove `package.json` and `google-gemini-wrapper`

#### 9.4.2 PRD Review
**Issue:** 3452 lines removed - unclear what was deleted
**Priority:** Low
**Action:** Review git diff to understand what was removed

#### 9.4.3 Add Docstrings
**Issue:** Missing API documentation
**Priority:** Low
**Action:** Add docstrings for all integration methods

---

## 10. Roadmap

### 10.1 Current Milestone: Complete Demanda Pipeline

**Status:** In progress (feature/demanda-pipeline branch)
**Completion Criteria:**
- [x] Template-based generation implemented
- [x] Perplexity research integration
- [x] Google Drive/Docs integration
- [x] Notion database integration
- [x] Progress tracking
- [x] Rollback manager
- [ ] Git cleanup (template_loader.py)
- [ ] Merge to main branch

**Timeline:** Immediate

### 10.2 Next Milestone: Refactoring

**Prerequisites:** Must complete before adding new features

**Completion Criteria:**
- [ ] Split handlers.py into modules
- [ ] Extract common pipeline logic
- [ ] Fix git issues (template_loader.py)
- [ ] Add docstrings to integration methods
- [ ] Review PRD.md changes

**Timeline:** Short-term (1-2 weeks)

### 10.3 Next Milestone: CI/CD Pipeline

**Status:** Immediate need

**Completion Criteria:**
- [ ] GitHub Actions workflow
- [ ] Automated test execution
- [ ] Docker image build automation
- [ ] Staging environment deployment
- [ ] Production deployment automation

**Timeline:** Short-term (1-2 weeks)

### 10.4 Next Milestone: /history Command

**Status:** In development

**Completion Criteria:**
- [ ] Supabase client integration (supabase-py)
- [ ] /history command handler
- [ ] Date + event_text insert
- [ ] Query by date range
- [ ] Integration with Notion (link events to cases)

**Schema:**
```sql
CREATE TABLE history_events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id BIGINT,  -- Telegram user ID
    event_date DATE NOT NULL,
    event_text TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    linked_case_id VARCHAR(20)  -- Optional: D-2026-001, etc.
);
```

**Timeline:** Short-term (after refactoring)

### 10.5 Future Milestones (Long-Term)

#### 10.5.1 Multi-User Support
**Timeline:** Long-term goal
**Prerequisites:** User profile system
**Features:**
- Dynamic template data loading
- Per-user configurations
- User management commands

#### 10.5.2 Enhanced Error Recovery
**Timeline:** TBD
**Features:**
- Retry with exponential backoff
- Clear user error messages
- Partial failure handling
- Dead letter queue for failed operations

#### 10.5.3 Monitoring & Analytics
**Timeline:** TBD
**Features:**
- Production monitoring (Prometheus/Grafana)
- Alert system (PagerDuty/slack)
- Usage analytics
- Performance tracking

#### 10.5.4 Additional Document Types
**Timeline:** TBD
**Potential Types:**
- Contract reviews
- Settlement agreements
- Mediation requests
- Appeal letters

---

## 11. Architecture Decision Records

### 11.1 Why Template-Based Generation?

**Decision:** Use templates with {{PLACEHOLDER}} fields instead of freeform LLM generation

**Context:**
- Initial implementation used freeform LLM generation
- Agents had full control over document structure
- Quality varied between generations

**Rationale:**
- **Consistency:** Templates ensure legal document structure compliance
- **Legal Compliance:** Spanish legal documents require specific formatting
- **Quality Control:** [HARDCODED] data remains accurate (DNI, addresses)
- **Maintainability:** Templates easier to update than prompt engineering

**Trade-offs:**
- Less flexibility in document structure
- Templates become single point of failure
- Requires manual template updates for law changes

**Status:** Correct decision - templates are stable and don't change often

### 11.2 Why Research Before Generation?

**Decision:** Move Perplexity research from verification (after) to context (before)

**Context:**
- Original flow: Generate → Research → Verify → Refine
- Research was used to verify generated claims
- Refinement integrated legal citations

**Rationale:**
- **Better Context:** Research provides legal grounding for generation
- **Efficiency:** LLM generates correct citations initially (fewer refinements)
- **User Feedback:** "Before generation is better"

**Trade-offs:**
- Cannot verify if generated claims cite real laws
- Research might be irrelevant to what LLM generates
- Template structure may prevent incorporating research

**Status:** Correct decision - research provides better context for template filling

### 11.3 Why Notion Instead of Custom Database?

**Decision:** Use Notion as case database instead of PostgreSQL/MongoDB

**Rationale:**
- **User Familiarity:** Delegates already use Notion
- **No-Code Flexibility:** Easy field modification without deployments
- **Visual Interface:** Delegates can see cases without bot commands
- **Rapid Development:** No schema migrations to manage

**Trade-offs Accepted:**
- API rate limits (~3 req/sec)
- Query latency vs. direct database
- Data ownership (hosted on Notion servers)
- No complex queries (joins, aggregations)

**Status:** Correct decision for pilot phase - user familiarity outweighs technical limitations

### 11.4 Why Google Docs Instead of PDF Generation?

**Decision:** Create editable Google Docs instead of final PDFs

**Rationale:**
- **Collaborative Editing:** Delegates can modify documents
- **Iterative Refinement:** Supports ongoing document improvement
- **Native Integration:** Google Workspace synergy with Drive
- **User Preference:** Delegates prefer Docs over PDF

**Trade-offs:**
- Manual export to PDF for court submissions
- No final "locked" document format
- Requires Google account access

**Status:** Correct decision - Docs preferred over PDF for collaborative workflow

### 11.5 Why Polling Instead of Webhooks?

**Decision:** Use Telegram bot polling mode instead of webhooks

**Rationale:**
- **Simpler Deployment:** No SSL certificate required
- **No Public URL:** Bot can run behind firewall
- **Docker-Friendly:** Single container, no exposed ports
- **Reliability:** No webhook registration to manage

**Trade-offs:**
- Higher latency (polling interval)
- Server resource usage (continuous polling)
- No real-time updates

**Status:** Correct decision for current scale - simplicity outweighs latency concerns

### 11.6 Why Free-Tier Models?

**Decision:** Use :free models from OpenRouter (DeepSeek R1, Gemma 3)

**Rationale:**
- **Budget Constraints:** Union project has limited budget
- **Quality Acceptable:** Free models produce good enough quality
- **Fallback Strategy:** Multiple free models provide redundancy

**Trade-offs:**
- Dependency on external provider's free tier offerings
- Quality/availability can change without notice
- No paid tier fallback configured

**Status:** Correct decision given budget constraints - acceptable latency

### 11.7 Why Agent System with Templates?

**Decision:** Keep agent personas (Inspector, Litigante, Comunicador) despite template-based generation

**User Feedback:** Agents are essential - they add value beyond template filling

**Rationale:**
- **Refinement Loop:** Agents' `refine_draft_with_feedback()` method adds value
- **Verification:** Agents verify legal compliance beyond template structure
- **Future Flexibility:** Agents can adapt to law changes without template updates
- **Specialization:** Different system prompts for each document type

**Status:** Correct decision - agents provide value beyond template filling

### 11.8 Why Hybrid Notion + Supabase?

**Decision:** Use both Notion (active cases) and Supabase (history) instead of consolidating

**Rationale:**
- **Different Purposes:**
  - Notion: Active case management with document links
  - Supabase: Historical event logging and timeline building
- **User Workflow:** Delegates use Notion daily for cases
- **Data Model Mismatch:** Event logging doesn't fit Notion's case-focused schema
- **Query Requirements:** Supabase better suited for time-series queries

**Status:** Correct decision - hybrid approach serves distinct needs

### 11.9 Why Python + python-telegram-bot?

**Decision:** Use Python with python-telegram-bot framework

**User Feedback:** Happy with stack - would choose again

**Rationale:**
- **AI/ML Ecosystem:** Python native language for LLM integrations
- **Async Support:** python-telegram-bot v20 has native async
- **Mature Framework:** Well-documented, active community
- **Library Support:** Excellent HTTP clients (aiohttp, httpx)

**Alternatives Considered:** Node.js (rejected)

**Status:** Correct decision - Python ideal for AI bot development

### 11.10 Why Manual Deployment?

**Decision:** Manual Docker deployment instead of CI/CD

**Current State:** Pilot phase - manual works fine
**Planned Change:** CI/CD is immediate need

**Rationale (Historical):**
- **Rapid Prototyping:** Manual deployment faster for iteration
- **Small Team:** Single developer managing deployment
- **Simple Infrastructure:** Single container, no orchestration complexity

**Trade-offs:**
- Human error risk
- No automated testing before deploy
- Slower deployment process
- No rollback automation

**Status:** Was correct for initial development - now needs CI/CD pipeline

---

## 12. Key Success Metrics

### 12.1 User Feedback Summary

**What's Working Well:**
- ✅ "Easy of use and easy of starting a case" - **BIGGEST WIN**
- ✅ Deep linking works well - delegates use it
- ✅ File uploads work well - no pain points
- ✅ Refinement loop works well - delegates use it
- ✅ Current progress UX is best - real-time updates
- ✅ Docs preferred over PDF - collaborative editing

**What Needs Improvement:**
- ⚠️ Code maintenance (technical debt accumulating)
- ⚠️ Multi-user support (long-term goal)
- ⚠️ Ease of use (can always be improved)
- ⚠️ Error recovery (needs improvement)
- ⚠️ Monitoring/alerts (needed)

### 12.2 Production Metrics

**Current Status:**
- **Phase:** Pilot testing
- **User Base:** Small group of delegates
- **Deployment:** Manual
- **Stability:** Stable - no critical issues
- **Performance:** Acceptable latency (LLM bottleneck acceptable)

---

## 13. Conclusion

**Marxnager** is a sophisticated legal document automation system that successfully combines multiple AI services with cloud storage to serve Spanish labor union delegates. The current implementation demonstrates:

**Strengths:**
1. **Sophisticated AI Pipeline** - Multi-stage LLM orchestration with verification
2. **Resilience** - Atomic transactions with automatic rollback
3. **User Experience** - Real-time progress tracking, deep linking
4. **Template System** - Separates structure from dynamic content
5. **Flexibility** - Agent-based architecture allows easy extension

**Areas for Improvement:**
1. **Code Maintenance** - Handlers at 950 lines, needs refactoring
2. **Multi-User Support** - Hardcoded single-user data blocks scaling
3. **Error Recovery** - No retry logic for API failures
4. **Testing** - No CI/CD automation despite 40+ test files
5. **Monitoring** - No alerts or production monitoring

**Immediate Priorities:**
1. Complete demanda pipeline and merge to main
2. Refactor handlers.py and extract common pipeline
3. Fix git issues (template_loader.py)
4. Implement CI/CD pipeline
5. Add error recovery and retry logic

**Long-Term Vision:**
- Multi-user support with user profiles
- Enhanced monitoring and alerting
- Additional document types
- Improved error handling and resilience

The system is **production-ready for pilot testing** with a small group of delegates. The biggest success is the **ease of use** - delegates can start cases quickly and efficiently. The architecture decisions made during development have proven sound, with the template-based generation and agent system providing the right balance of consistency and flexibility.

---

**Document Version:** 1.0
**Last Updated:** January 19, 2026
**Next Review:** After demanda pipeline merge to main
