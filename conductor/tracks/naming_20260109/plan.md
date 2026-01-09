# Plan: Implement AI-Powered Descriptive Naming

## Phase 1: AI Agent Enhancement
- [x] Task: Update Agent Prompts for Summary Generation 19bad46
    - [ ] Subtask: Write Tests for Agent Summary: Create unit tests ensuring agents return a JSON/Structured output with a `summary` field.
    - [ ] Subtask: Implement Summary Logic: Modify `src/agents/base.py` (or specific agent classes) to prompt the LLM for a 5-7 word summary alongside the draft.
    - [ ] Subtask: Verify Output: Ensure the summary is stripped of special characters and suitable for file naming.
- [x] Task: Conductor - User Manual Verification 'AI Agent Enhancement' (Protocol in workflow.md) [checkpoint: b1c4942]

## Phase 2: Integration Client Updates
- [x] Task: Update Notion Client for Titles
    - [ ] Subtask: Write Tests for Notion Title: Mock Notion API to verify `create_case_page` accepts and uses the new title format.
    - [ ] Subtask: Modify Notion Client: Update `create_case_page` signature to accept `case_title` and use it in the `Name` property.
- [x] Task: Update Drive and Docs Clients for Titles
    - [ ] Subtask: Write Tests for Drive/Docs Naming: Mock Google APIs to verify folder and file creation uses the new naming convention.
    - [ ] Subtask: Modify Drive Client: Update `create_case_folder` to accept `case_name` and use it for the folder name.
    - [ ] Subtask: Modify Docs Client: Update document creation logic to include the summary in the filename.
- [ ] Task: Conductor - User Manual Verification 'Integration Client Updates' (Protocol in workflow.md)

## Phase 3: Handler Refactoring and Wiring
- [ ] Task: Refactor Command Handlers
    - [ ] Subtask: Update `denuncia_handler`: Extract context, call Agent for summary *first*, then call Notion/Drive/Docs with the generated title.
    - [ ] Subtask: Update `demanda_handler`: Replicate logic for judicial claims.
    - [ ] Subtask: Update `email_handler`: Replicate logic for emails.
- [ ] Task: Conductor - User Manual Verification 'Handler Refactoring and Wiring' (Protocol in workflow.md)

## Phase 4: End-to-End Verification
- [ ] Task: Full System Test
    - [ ] Subtask: Execute E2E Test: Run a full `/denuncia` command flow and verify the actual names created in Notion and Drive (using mocks or a test environment).
    - [ ] Subtask: Verify Fallbacks: Test the system's behavior when the AI summary generation fails (should fallback to ID).
- [ ] Task: Conductor - User Manual Verification 'End-to-End Verification' (Protocol in workflow.md)
