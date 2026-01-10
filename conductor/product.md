# Product Guide: Marxnager

## Initial Concept
Marxnager is an advanced union assistant for Telegram, designed to empower union delegates by automating legal document generation and providing centralized case management.

## Target Users
The primary users are union delegates and representatives who need to efficiently manage labor conflicts, automate formal complaints to the ITSS (Labor Inspection), draft judicial claims, and handle corporate communications with HR.

## Core Features
- **Automated AI Document Generation:** Specialized agents (Inspector Laboral, Litigante Procesal, Comunicador Corporativo) generate high-quality drafts for legal complaints, demands, and emails based on user input and legal standards.
- **Two-Stage Verification Loop:** All AI-generated drafts undergo an automatic grounding process using a specialized Spanish Labor Law prompt with Perplexity Sonar LLM. This includes dynamic metadata extraction (thesis, legal area) to verify legal accuracy and provide citations before finalization.
- **AI Refinement Mode:** Ability to update and refine existing drafts in private mode by sending new text context, voice notes, or files, which the AI integrates into the Google Doc.
- **Centralized Management:** Automatic registration of cases in a Notion database and creation of dedicated Google Drive folders for evidence and drafts.
- **Legal Auditing:** Automatic logging of the raw Perplexity verification report into the Notion case page for transparency and review of the grounding process.
- **Smart Naming & ID System:** Automatic assignment of sequential IDs (e.g., D-2026-001) and descriptive titles (ID - Summary) for all created artifacts.
- **Dual Workflow:** Public group commands for team visibility and transparency, with a seamless transition to a secure private chat for deep work and sensitive evidence handling.
- **Action Logging:** Implementation of a `/log` command that retrieves and sends the system's action log file for easy auditing.
- **Real-time Progress Tracking:** A dynamic system that provides live visual feedback with status icons (⬜, ⏳, ✅) and execution timers for each step (e.g., `(2.5s)`), ensuring transparency in the document generation workflow.

## User Experience (UX) Goals
- **Efficiency:** Drastically reduce the time required to move from an initial incident report to a formal legal draft.
- **Professionalism & Organization:** Ensure all documentation is legally sound, formally written, and perfectly organized across Notion and Drive.
- **Transparency:** Keep the entire union team updated on case progress through strategic group notifications.
- **Simplicity:** Provide a frictionless interface that manages complex multi-platform integrations (Notion, Drive, Docs, AI) through simple Telegram commands.

## Technical & Non-functional Requirements
- **Security:** Strict access control via a hardcoded or environment-based whitelist of authorized Telegram IDs.
- **Secret Redaction:** Integrated scanning and redaction system to prevent exposure of API keys and sensitive tokens in documentation and logs.
- **Reliability:** Atomic "all-or-nothing" transaction logic for artifact creation; failures trigger an automatic rollback (hard delete) of all partial results (Notion, Drive, Docs).
- **Modular & Extensible Architecture:** A clean separation of specialized AI agents and integration clients to facilitate future expansion (e.g., LexNet integration).
- **Observability:** Centralized logging of all bot actions to support the auditing and maintenance of the system.