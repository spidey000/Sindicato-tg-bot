# Tech Stack: Delegado 360

## Core Technologies
- **Language:** Python 3.11+
- **Primary Framework:** `python-telegram-bot` (v20+) for managing the Telegram interface, command routing, and file handling.
- **Async Execution:** `asyncio` for non-blocking I/O operations with external APIs.

## AI & NLP Layer
- **Orchestrator Models (via OpenRouter):**
    - **Primary:** `deepseek/deepseek-r1-0528:free` for high-reasoning draft generation and refinement.
    - **Fallback:** `mistralai/devstral-2512:free`.
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
- **Configuration:** `python-dotenv` for managing environment variables and API keys.
- **Security:** Hardcoded/Environment whitelist for user authorization.
