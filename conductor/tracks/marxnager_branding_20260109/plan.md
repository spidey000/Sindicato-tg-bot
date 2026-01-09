# Plan: Branding Update to "Marxnager"

## Phase 1: Documentation and Configuration Update [checkpoint: d62c2ef]
- [x] Task: Update `README.md` and `CHANGELOG.md` with new "Marxnager" branding. e8c6881
- [x] Task: Update `PRD.md` and `conductor/product.md` to reflect the new name. fcd6c1f
- [x] Task: Update `src/config.py` (or relevant constants) to use "Marxnager" as the default application name for future Notion/Drive resources. f8e45ad
- [x] Task: Conductor - User Manual Verification 'Phase 1: Documentation and Configuration Update' (Protocol in workflow.md) d62c2ef

## Phase 2: Telegram UI Branding Update [checkpoint: f21119a]
- [x] Task: Create unit tests in `tests/test_branding.py` to verify that bot handlers/utils return the correct "Marxnager" strings. 221c242
- [x] Task: Update `src/handlers.py` and `src/utils.py` to replace all user-facing instances of "Delegado 360" or "Sindicato" with "Marxnager". febdc8e
- [x] Task: Update `/help` command text in `src/handlers.py`. 6aaaa1e
- [x] Task: Conductor - User Manual Verification 'Phase 2: Telegram UI Branding Update' (Protocol in workflow.md) f21119a

## Phase 3: Verification and Cleanup
- [x] Task: Run a global search for old branding strings and ensure no user-facing instances remain. 06096db
- [x] Task: Verify that a new case generation flow correctly uses "Marxnager" in its automated naming. a679f58
- [ ] Task: Conductor - User Manual Verification 'Phase 3: Verification and Cleanup' (Protocol in workflow.md)