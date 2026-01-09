# Specification: Dynamic Progress Tracking for Document Workflows

## 1. Overview
This track implements a real-time progress tracking system for all document generation and refinement workflows (`/denuncia`, `/demanda`, `/email`, and private chat refinements). Instead of a static "Processing..." message, the bot will provide a dynamic checklist that updates as each internal stage is completed, improving user feedback and transparency.

## 2. Functional Requirements

### 2.1 Dynamic Progress Message
*   **Trigger:** Initiated by `/denuncia`, `/demanda`, `/email` commands, or when a document refinement is triggered in private chat.
*   **UI Component:** A single Telegram message that is edited multiple times throughout the process.
*   **Initial State:** The message displays the full list of steps. All steps are formatted in *italic strikethrough* to indicate they are pending.
*   **Update Logic:** As each step completes, the bot edits the message to change that step's formatting to **bold text**.
*   **Final State:** The progress message is either replaced or updated one last time to include the final success message with links to Notion/Drive/Docs.

### 2.2 Sequence of Operations
To fulfill the requirement of setting the title early, the sequence MUST be:
1.  **Drafting:** `Generando borrador inicial...` (AI generates the draft and extracts a descriptive title).
2.  **Initialization:** `Iniciando expediente...`
3.  **Database Entry:** `Registrando en Notion...`
4.  **File Structure:** `Creando carpetas en Drive...`
5.  **Verification:** `Verificando con Perplexity...` (Grounding/Two-Stage Verification).
6.  **Refinement:** `Aplicando correcciones y verificaciones...` (Final AI polishing).
7.  **Completion:** `¡Listo! Expediente creado.`

### 2.3 Formatting Rules
*   **Pending/In Progress:** `~_Step Name_~` (Telegram Markdown for Strikethrough + Italic).
*   **Completed:** `**Step Name**` (Telegram Markdown for Bold).
*   **Failure:** Mark the active step with a `❌` emoji and halt updates.

## 3. Technical Requirements
*   **Message Management:** Store the `message_id` of the progress message in the `context` or a session object to ensure handlers can edit it reliably.
*   **Rate Limiting:** Ensure the frequency of edits (approx. 7 edits per request) stays well within Telegram's API limits.
*   **Asynchronous Updates:** Edits must be awaited to ensure the UI reflects the current state accurately.

## 4. Acceptance Criteria
*   [ ] Triggering a document command shows a checklist of ~7 steps in strikethrough italics.
*   [ ] The "Drafting" step completes first, enabling the use of a descriptive title in Notion/Drive.
*   [ ] Steps turn bold one by one as they succeed.
*   [ ] If a step fails, the message shows a `❌` next to that step.
*   [ ] The final message contains the links to the generated artifacts.
