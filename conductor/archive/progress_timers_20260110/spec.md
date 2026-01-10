# Specification: Progress Message & Timer Enhancement

## 1. Overview
This feature aims to improve the user experience of the `/demanda` and `/email` workflows by aligning the Telegram progress message with the actual system execution order. It also introduces execution timers for each step to provide visibility into performance and updates the visual status indicators.

## 2. Functional Requirements

### 2.1 Progress Message Structure
The progress message MUST display steps in the following order (matching the actual execution flow):
1.  **Initialization** (Immediate upon command)
2.  **Drafting** (AI working)
3.  **Notion Entry** (First Notion page creation)
4.  **Drive Structure** (Folder creation)
5.  **Perplexity Check** (Legal verification)
6.  **Refinement** (Applying verification insights)
7.  **Docs Creation** (Final Google Doc)
8.  **Finalization** (Updating Notion with links)

### 2.2 Visual Status Indicators
- **Pending/Future:** No icon or a neutral placeholder (e.g., `⬜`).
- **In Progress (Waiting):** `⏳` (Sand Clock).
- **Completed:** `✅` (Check Mark).

### 2.3 Execution Timers
- A timer MUST track the duration of each step.
- Upon completion of a step, the elapsed time MUST be appended to the line.
- **Format:** `✅ Step Name (12.5s)`

### 2.4 Renaming
- Rename the step "Verification" to "Perplexity Check" in all user-facing messages.

## 3. Non-Functional Requirements
- **Accuracy:** The displayed time must reflect the wall-clock time taken for that specific async operation.
- **Responsiveness:** The Telegram message edit API should be called after each step completes.
- **Error Handling:** If a step fails, the timer should stop, and the error state should be clearly visible (though error handling logic is largely existing).

## 4. Acceptance Criteria
- [ ] The progress message lists steps in the **exact order** they occur in the code.
- [ ] The "Verification" step is displayed as "Perplexity Check".
- [ ] The currently running step shows a `⏳` icon.
- [ ] Completed steps show a `✅` icon and the elapsed time (e.g., `(2s)`).
- [ ] The final message shows all steps as completed with their respective times.
