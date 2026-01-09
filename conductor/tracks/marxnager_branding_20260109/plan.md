# Plan: Branding Update to "Marxnager"

## Phase 1: Documentation and Configuration Update
- [x] Task: Update `README.md` and `CHANGELOG.md` with new "Marxnager" branding. e8c6881
- [x] Task: Update `PRD.md` and `conductor/product.md` to reflect the new name. fcd6c1f
- [ ] Task: Update `src/config.py` (or relevant constants) to use "Marxnager" as the default application name for future Notion/Drive resources.
- [ ] Task: Conductor - User Manual Verification 'Phase 1: Documentation and Configuration Update' (Protocol in workflow.md)

## Phase 2: Telegram UI Branding Update
- [ ] Task: Create unit tests in `tests/test_branding.py` to verify that bot handlers/utils return the correct "Marxnager" strings.
- [ ] Task: Update `src/handlers.py` and `src/utils.py` to replace all user-facing instances of "Delegado 360" or "Sindicato" with "Marxnager".
- [ ] Task: Update `/help` command text in `src/handlers.py`.
- [ ] Task: Conductor - User Manual Verification 'Phase 2: Telegram UI Branding Update' (Protocol in workflow.md)

## Phase 3: Verification and Cleanup
- [ ] Task: Run a global search for old branding strings and ensure no user-facing instances remain.
- [ ] Task: Verify that a new case generation flow correctly uses "Marxnager" in its automated naming.
- [ ] Task: Conductor - User Manual Verification 'Phase 3: Verification and Cleanup' (Protocol in workflow.md)