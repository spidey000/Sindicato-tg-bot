# Plan: Secret Scanning and Redaction

## Phase 1: Core Detection & Redaction Logic [checkpoint: 623d6fe]
- [x] Task: Initialize scanning module and test suite c418574
    - [x] Subtask: Create `scripts/security/__init__.py` and `scripts/security/secret_scanner.py`.
    - [x] Subtask: Create `tests/test_secret_scanner.py`.
- [x] Task: Implement Secret Detection (TDD) 10d15b3
    - [x] Subtask: Write failing test for detecting dummy secrets (e.g., `API_KEY="12345"`).
    - [x] Subtask: Implement regex-based detection in `secret_scanner.py`.
    - [x] Subtask: Verify tests pass.
- [x] Task: Implement Redaction Logic (TDD) 698154a
    - [x] Subtask: Write failing test for replacing detected secret with `<REDACTED_SECRET>`.
    - [x] Subtask: Implement replacement method.
    - [x] Subtask: Verify tests pass.
- [x] Task: Conductor - User Manual Verification 'Core Detection & Redaction Logic' (Protocol in workflow.md)

## Phase 2: File Processing & CLI
- [x] Task: Implement File Walking & filtering (TDD) 1859f14
    - [ ] Subtask: Write failing test for scanning a directory, ignoring `.git` and binary files.
    - [ ] Subtask: Implement file walker in `secret_scanner.py`.
    - [ ] Subtask: Verify tests pass.
- [x] Task: Implement CLI entry point and Reporting f649ab3
    - [ ] Subtask: Add `main` block to `scripts/security/secret_scanner.py` to accept arguments.
    - [ ] Subtask: Implement console reporting of changed files and found secrets.
- [ ] Task: Conductor - User Manual Verification 'File Processing & CLI' (Protocol in workflow.md)

## Phase 3: Execution & Cleanup
- [ ] Task: Execute Secret Scan
    - [ ] Subtask: Run the scanner against the repository root.
    - [ ] Subtask: Review the `README.md` and other files for unintended redactions or missed secrets.
- [ ] Task: Conductor - User Manual Verification 'Execution & Cleanup' (Protocol in workflow.md)
