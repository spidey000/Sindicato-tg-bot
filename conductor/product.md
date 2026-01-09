# Product Guide: Marxnager

## Initial Concept
Marxnager is an advanced union assistant for Telegram, designed to empower union delegates by automating legal document generation and providing centralized case management.

## Target Users
The primary users are union delegates and representatives who need to efficiently manage labor conflicts, automate formal complaints to the ITSS (Labor Inspection), draft judicial claims, and handle corporate communications with HR.

## Core Features
- **Automated AI Document Generation:** Specialized agents (Inspector Laboral, Litigante Procesal, Comunicador Corporativo) generate high-quality drafts for legal complaints, demands, and emails based on user input and legal standards.
- **Two-Stage Verification Loop:** All AI-generated drafts undergo an automatic grounding process using Perplexity Sonar LLM to verify legal accuracy and provide citations before finalization.
- **AI Refinement Mode:** Ability to update and refine existing drafts in private mode by sending new text context, voice notes, or files, which the AI integrates into the Google Doc.
- **Centralized Management:** Automatic registration of cases in a Notion database and creation of dedicated Google Drive folders for evidence and drafts.
- **Smart Naming & ID System:** Automatic assignment of sequential IDs (e.g., D-2026-001) and descriptive titles (ID - Summary) for all created artifacts.
- **Dual Workflow:** Public group commands for team visibility and transparency, with a seamless transition to a secure private chat for deep work and sensitive evidence handling.
- **Action Logging:** Implementation of a `/log` command that retrieves and sends the system's action log file as a reply in the channel for easy auditing and troubleshooting.
- **Real-time Progress Tracking:** A dynamic checklist system that provides live visual feedback (bold/strikethrough) during document generation workflows, improving user transparency.

## User Experience (UX) Goals
- **Efficiency:** Drastically reduce the time required to move from an initial incident report to a formal legal draft.
- **Professionalism & Organization:** Ensure all documentation is legally sound, formally written, and perfectly organized across Notion and Drive.
- **Transparency:** Keep the entire union team updated on case progress through strategic group notifications.
- **Simplicity:** Provide a frictionless interface that manages complex multi-platform integrations (Notion, Drive, Docs, AI) through simple Telegram commands.

## Technical & Non-functional Requirements
- **Security:** Strict access control via a hardcoded or environment-based whitelist of authorized Telegram IDs.
- **Reliability:** Robust handling of external API failures with comprehensive logging and graceful degradation.
- **Modular & Extensible Architecture:** A clean separation of specialized AI agents and integration clients to facilitate future expansion (e.g., LexNet integration).
- **Observability:** Centralized logging of all bot actions to support the auditing and maintenance of the system.