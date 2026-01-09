# Plan: Dynamic Progress Tracking

## Phase 1: Core Logic & Helpers
- [x] Task: Create `src/utils.py` helper function `send_progress_message(update, steps)` that sends the initial message and returns the `message_id`. 709f9b8
- [x] Task: Create `src/utils.py` helper function `update_progress_message(context, chat_id, message_id, steps_status)` to edit the existing message. ceb0b88
- [ ] Task: Refactor `AgentBase` in `src/agents/base.py` to expose granular methods:
    - Ensure `generate_structured_draft` is public and accessible.
    - Expose `verify_draft_content` (wrapping `pplx_client.verify_draft`).
    - Expose `refine_draft_with_feedback` (the refinement logic).
    - *Alternatively, keep `generate_structured_draft_verified` but add a `callback` parameter.* (Decided: Split for better control in handlers).
- [ ] Task: Conductor - User Manual Verification 'Core Logic' (Protocol in workflow.md)

## Phase 2: Handler Integration (`/denuncia`, `/demanda`, `/email`)
- [ ] Task: Refactor `denuncia_handler` in `src/handlers.py`:
    - Initialize progress message.
    - Step 1: Call `agent.generate_structured_draft`. Update Progress.
    - Step 2: Call `agent.verify_draft_content` (Perplexity). Update Progress.
    - Step 3: Call `agent.refine_draft_with_feedback`. Update Progress.
    - Step 4: Generate ID & Title. Update Progress.
    - Step 5: Notion Entry. Update Progress.
    - Step 6: Drive Folder. Update Progress.
    - Step 7: Docs Creation. Update Progress.
    - Final Step: Replace progress message with Success card.
- [ ] Task: Apply same refactoring to `demanda_handler`.
- [ ] Task: Apply same refactoring to `email_handler`.
- [ ] Task: Conductor - User Manual Verification 'Handlers Integration' (Protocol in workflow.md)

## Phase 3: Testing & Polish
- [ ] Task: Create `tests/test_progress_updates.py` to mock the bot and verify message edit sequence.
- [ ] Task: Verify error handling (ensure `❌` is shown if any step raises exception).
- [ ] Task: Conductor - User Manual Verification 'Testing' (Protocol in workflow.md)
