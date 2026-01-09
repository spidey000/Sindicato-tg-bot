# Specification: Observability & Two-Stage Verification

## 1. Overview
This track addresses two missing critical features: the implementation of a `/log` command for system observability and the enforcement of a "Two-Stage Verification" loop using Perplexity (Sonar LLM) for all AI-generated legal documents. This ensures both operational transparency and high legal accuracy for generated content.

## 2. Functional Requirements

### 2.1 `/log` Command
*   **Trigger:** User sends `/log` in the Telegram chat (authorized users only).
*   **Action:** The bot retrieves the system's log file(s).
*   **Content:**
    *   Must include the last **10MB** of logs (tail).
    *   Must encompass **Action Logs** (high-level user interactions).
    *   Must encompass **Error Traces** and debug information.
*   **Output:** The log data is sent back to the user as a downloadable file attachment.

### 2.2 Perplexity Two-Stage Verification (Sonar LLM)
*   **Workflow:** `Draft -> Perplexity Grounding -> Refinement`
    1.  **Draft:** The primary Agent generates an initial draft.
    2.  **Verify (Grounding):** The system **automatically** queries the **Perplexity Sonar LLM** API.
        *   The query must utilize the initial draft to request a **grounded response** with citations to validate legal accuracy.
    3.  **Refine:** The Agent receives the grounded response and uses it to revise the initial draft.
*   **Trigger Scope:** Automatic for **every** document draft.
*   **API Management:**
    *   Use `PERPLEXITY_API_KEY_PRIMARY` and `PERPLEXITY_API_KEY_FALLBACK`.
    *   Implement logic: Try Primary -> Fail -> Try Fallback -> Fail -> Return Unverified.
*   **Failure Mode (Fail Safe):** If all attempts fail, return the **Initial Draft** with a "Verification Failed" warning.

## 3. Non-Functional Requirements
*   **Performance:** `/log` reading must be efficient.
*   **Reliability:** Perplexity integration must handle timeouts/errors gracefully.
*   **Configuration:** API keys loaded from `.env`.

## 4. Acceptance Criteria
*   [ ] `/log` returns correct 10MB log file.
*   [ ] Document generation triggers Perplexity Sonar API call.
*   [ ] Fallback key logic works correctly.
*   [ ] "Verification Failed" warning appears on total API failure.
*   [ ] Final documents show evidence of grounding/refinement.
