# Specification: Atomic Document Creation, Rollback, and Enhanced LLM Reliability

## 1. Overview
This track implements a robust "all-or-nothing" (atomic) transaction logic for document generation workflows. If any stage of the creation process fails (Notion, Drive, or Google Docs), all previously created artifacts for that request must be permanently deleted (Hard Delete). Additionally, it strengthens LLM interactions with mandatory retries, JSON validation, and detailed error reporting.

## 2. Functional Requirements

### 2.1 Atomic Creation & Rollback
*   **Scope:** Applies to `/denuncia`, `/demanda`, and `/email` commands.
*   **Transaction Logic:**
    1.  The bot tracks every artifact created during the flow (Notion Page ID, Drive Folder ID, Google Doc ID).
    2.  If an exception occurs at any step (e.g., Google Drive API failure after Notion entry), a rollback is triggered.
*   **Rollback Actions:**
    *   **Hard Delete:** Permanently delete the Notion page, the Google Drive folder, and the Google Doc.
    *   **Notification:** Update the progress message with a "Critical Error" status.
    *   **Detailed Feedback:** The error message must specify exactly what step caused the failure and provide a log of the rollback actions (e.g., "❌ Fallo en 'Creación de Google Doc'. Revertiendo cambios: Notion eliminado, Carpeta eliminada.").

### 2.2 LLM Reliability & Validation
*   **Global Retry Policy:** All LLM integrations (OpenRouter for drafting and Perplexity for verification) must implement a 3-attempt retry logic.
*   **Validation Rules:**
    *   **JSON Format:** Responses must be valid JSON (utilizing `response_format: {"type": "json_object"}`).
    *   **Minimum Length:** The `content` field within the JSON must be longer than 50 characters. If shorter, the attempt is considered a failure and triggers a retry.
*   **Exhaustion:** If all 3 attempts fail, the entire document generation flow is aborted and triggers the rollback described in 2.1.

## 3. Technical Requirements
*   **Cleanup Service:** Create a utility to handle deletions across different APIs (Notion, Drive).
*   **Context Management:** Ensure the `context` or a temporary state object tracks created IDs throughout the handler's execution.
*   **Error Handling:** Use specific try/except blocks around each integration call to catch failures early and initiate rollback.

## 4. Acceptance Criteria
* [ ] Triggering a failure at any point in `/denuncia` results in no orphan files/pages remaining.
* [ ] The progress message clearly indicates the cause of failure and the items reverted.
* [ ] LLM calls automatically retry if the JSON is invalid or the content is too short (< 50 chars).
* [ ] After 3 failed LLM attempts, the process stops and cleans up existing artifacts.
* [ ] All document generation commands (`/denuncia`, `/demanda`, `/email`) strictly adhere to the atomic creation logic.
