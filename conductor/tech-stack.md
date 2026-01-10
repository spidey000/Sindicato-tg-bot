# Tech Stack: Marxnager

## Core Technologies
- **Language:** Python 3.11+
- **Primary Framework:** `python-telegram-bot` (v20+) for managing the Telegram interface, command routing, and file handling.
- **Async Execution:** `asyncio` for non-blocking I/O operations with external APIs.

## AI & NLP Layer
- **Orchestrator Models (via OpenRouter):**
    - **Hierarchy Strategy:** Specialized model selection based on task type.
    - **Drafting:** `openai/gpt-oss-120b:free` (Primary) -> `google/gemma-3-27b-it:free` (Fallback).
    - **Refinement:** `deepseek/deepseek-r1-0528:free` (Primary) -> `moonshotai/moonlight-2:free` (Fallback).
    - **Validation & Repair:** 
        - Enforced JSON output (`json_object`).
        - **JSON Repair:** Malformed outputs trigger a repair call to `qwen/qwen3-4b:free` using `structured_outputs`.
        - **Retry Logic:** Mandatory 3-attempt retry logic for all LLM calls if repair fails.
- **Validation & Search (Perplexity Sonar):**
    - `sonar-pro` model used for real-time legal research and fact-checking of drafts.
    - Dual-key fallback system for API reliability.
- **Transcription:** OpenAI Whisper (or equivalent) for converting voice notes into text context.

## External Integrations
- **Notion API:** Used as the central database for case tracking, status management, and metadata storage.
- **Google Drive API:** Handles hierarchical folder creation and secure storage of evidence and final documents.
- **Google Docs API:** Facilitates dynamic creation and AI-driven refinement of legal drafts.

## Development & Infrastructure
- **Environment:** Termux (Android) for local development and execution.
- **Deployment:** Docker & Docker Compose for containerized VPS execution, managed via Portainer.
- **Configuration:** `python-dotenv` for managing environment variables and API keys.
- **Security:** 
    - Hardcoded/Environment whitelist for user authorization.
    - Custom regex-based secret scanning and redaction tool for repository safety.
