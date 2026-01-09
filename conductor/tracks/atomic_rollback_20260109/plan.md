# Plan: Atomic Document Creation, Rollback, and Enhanced LLM Reliability

## Phase 1: LLM Reliability & Validation [checkpoint: ]
- [x] Task: Update `OpenRouterClient._make_request` to support `response_format` and handle retries (3 attempts). 2399910
- [x] Task: Implement `AgentBase.generate_structured_draft_with_retry` that validates JSON and minimum content length (> 50 chars). bc80738
- [x] Task: Refactor `pplx_client.verify_draft` to include retry logic. 2911bce
- [x] Task: Add unit tests for retry logic and JSON validation (mocking API failures and short responses). bc80738
- [ ] Task: Conductor - User Manual Verification 'LLM Reliability' (Protocol in workflow.md)

## Phase 2: Atomic Rollback Utilities [checkpoint: ]
- [ ] Task: Create `src/integrations/cleanup_helper.py` with methods to:
    - Delete Notion pages (`API-update-a-block` with `archived: true`).
    - Delete Drive folders (`drive_client.service.files().delete()`).
    - Delete Google Docs (handled by folder deletion, but ensure cleanup).
- [ ] Task: Implement a `RollbackManager` class in `src/utils.py` to track created IDs and execute cleanup on failure.
- [ ] Task: Add unit tests for `RollbackManager` and cleanup utilities using mocks.
- [ ] Task: Conductor - User Manual Verification 'Rollback Utilities' (Protocol in workflow.md)

## Phase 3: Handler Integration & Error Reporting [checkpoint: ]
- [ ] Task: Audit `denuncia_handler`, `demanda_handler`, and `email_handler` to confirm they all have Notion creation, Drive folder creation, and Doc draft file creation logic. Add missing logic if found (using `demanda_handler` as the template).
- [ ] Task: Refactor `denuncia_handler` in `src/handlers.py` to use `RollbackManager` and updated agent methods.
- [ ] Task: Implement detailed error reporting in `update_progress_message` when a rollback occurs.
- [ ] Task: Apply refactoring and rollback logic to `demanda_handler`.
- [ ] Task: Apply refactoring and rollback logic to `email_handler`.
- [ ] Task: Create an E2E test case that simulates a failure mid-process (e.g., mock Drive failure) and verifies all previous artifacts are deleted and the user is notified.
- [ ] Task: Conductor - User Manual Verification 'Handler Integration' (Protocol in workflow.md)
