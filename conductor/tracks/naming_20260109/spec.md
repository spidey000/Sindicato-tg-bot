# Specification: Implement AI-Powered Descriptive Naming

## Context
Currently, the system generates generic identifiers (e.g., `D-2026-001`) for cases, Notion pages, and Drive folders. This makes it difficult for users to identify the content of a case at a glance. The goal is to enhance the system so that the AI analyzes the user's initial input (context) and generates a concise, descriptive summary (e.g., "Falta de EPIs", "Despido Improcedente") to be appended to the ID.

## Core Requirements
1.  **AI Summary Generation:**
    - Update the AI agents (Inspector, Litigante, Comunicador) to return a structured response that includes a short "title_summary" (max 5-7 words) derived from the user's input context.
    - Ensure this summary is generated *before* any external API calls (Notion/Drive) are made.

2.  **Notion Integration Update:**
    - Modify `DelegadoNotionClient.create_case_page` to accept a `title` parameter.
    - Ensure the Notion page title uses the format: `[ID] - [AI Summary]` (e.g., `D-2026-001 - Falta de EPIs`).

3.  **Google Drive Integration Update:**
    - Modify `DelegadoDriveClient.create_case_folder` to accept a `case_name` parameter (the summary).
    - Ensure the root folder for the case is named: `[ID] - [AI Summary]`.

4.  **Google Docs Integration Update:**
    - Ensure the initial draft document created inside the folder also follows the naming convention: `[ID] - [AI Summary] - Borrador`.

5.  **Handler Logic Update:**
    - Refactor `src/handlers.py` (specifically `denuncia_handler`, `demanda_handler`, `email_handler`) to:
        - Call the AI agent to get the summary first.
        - Pass this summary to the Notion and Drive creation functions.

## Non-Functional Requirements
- **Latency:** The AI summary generation must be fast (using the "flash" or "fast" model tier) to avoid delaying the initial response to the user.
- **Fallback:** If the AI fails to generate a summary, the system should gracefully fall back to using just the ID or a generic placeholder (e.g., `[ID] - Sin Título`).

## User Experience
- **Input:** User sends `/denuncia La empresa no ha pagado la nómina de diciembre`.
- **Output:**
    - Bot responds: "✅ Expediente Creado: **D-2026-005 - Impago Nómina Diciembre**"
    - Notion Page: `D-2026-005 - Impago Nómina Diciembre`
    - Drive Folder: `D-2026-005 - Impago Nómina Diciembre`
