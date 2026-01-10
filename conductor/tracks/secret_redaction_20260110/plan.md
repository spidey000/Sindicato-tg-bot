# Plan: Secret Scanning and Redaction

## Phase 1: Core Detection & Redaction Logic
- [x] Task: Initialize scanning module and test suite c418574
    - [ ] Subtask: Create `scripts/security/__init__.py` and `scripts/security/secret_scanner.py`.
    - [ ] Subtask: Create `tests/test_secret_scanner.py`.
- [x] Task: Implement Secret Detection (TDD) 10d15b3
    - [ ] Subtask: Write failing test for detecting dummy secrets (e.g., `API_KEY="12345"`).
    - [ ] Subtask: Implement regex-based detection in `secret_scanner.py`.
    - [ ] Subtask: Verify tests pass.
- [x] Task: Implement Redaction Logic (TDD) 698154a
    - [ ] Subtask: Write failing test for replacing detected secret with `<REDACTED_SECRET>`.
    - [ ] Subtask: Implement replacement method.
    - [ ] Subtask: Verify tests pass.
- [ ] Task: Conductor - User Manual Verification 'Core Detection & Redaction Logic' (Protocol in workflow.md)

## Phase 2: File Processing & CLI
- [ ] Task: Implement File Walking & filtering (TDD)
    - [ ] Subtask: Write failing test for scanning a directory, ignoring `.git` and binary files.
    - [ ] Subtask: Implement file walker in `secret_scanner.py`.
    - [ ] Subtask: Verify tests pass.
- [ ] Task: Implement CLI entry point and Reporting
    - [ ] Subtask: Add `main` block to `scripts/security/secret_scanner.py` to accept arguments.
    - [ ] Subtask: Implement console reporting of changed files and found secrets.
- [ ] Task: Conductor - User Manual Verification 'File Processing & CLI' (Protocol in workflow.md)

## Phase 3: Execution & Cleanup
- [ ] Task: Execute Secret Scan
    - [ ] Subtask: Run the scanner against the repository root.
    - [ ] Subtask: Review the `README.md` and other files for unintended redactions or missed secrets.
- [ ] Task: Conductor - User Manual Verification 'Execution & Cleanup' (Protocol in workflow.md)
