# Changelog

## [Unreleased]

### Added
- **Detailed AI Prompts**: Updated `InspectorLaboral`, `LitiganteProcesal`, and `ComunicadorCorporativo` agents with rich, specialized system prompts from the PRD.
- **AI Document Refinement**: Implemented a "Refinement Mode" in private chat. The bot now reads the current Google Doc, incorporates new user input using AI, and updates the document content (instead of just appending notes).
- **Sequential Case IDs**: Implemented logic to query Notion for the last used Case ID (e.g., D-2026-005) and increment it for new cases, replacing random ID generation.
- **Notion 'Enlace Doc'**: Added support for storing the Google Doc URL in the "Enlace Doc" property of the Notion database.
- **Google Docs Integration**: Added `read_document_content` and `update_document_content` to `DelegadoDocsClient` to support the refinement feature.

### Changed
- Refactored `src/handlers.py` to use sequential ID generation and the new AI refinement workflow.
- Updated `src/utils.py` to support ID incrementation.

### Fixed
- **Notion Integration**: Fixed a critical error where the Notion client would fail due to a missing `databases.query` method. Implemented a robust fallback using `data_sources.query` for managed databases.
- **Notion Database Schema**: Updated property mapping to match the actual database schema (`Perplexity` property used as a fallback for document links when `Enlace Doc` is missing).
- Fixed missing Google Doc link persistence in Notion.

### Improved

- **Descriptive Naming**: Ensured all Notion pages, Drive folders, and Google Docs use a descriptive title format (`ID - Summary`) instead of just the Case ID, fulfilling user request for better organization.
