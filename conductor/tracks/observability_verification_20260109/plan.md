# Plan: Observability & Perplexity Verification

## Phase 1: Configuration & Environment
- [x] Task: Update `.env.example` and `.env` (user instruction) to include `PERPLEXITY_API_KEY_PRIMARY` and `PERPLEXITY_API_KEY_FALLBACK`. e49122e
- [x] Task: Conductor - User Manual Verification 'Configuration' (Protocol in workflow.md)

## Phase 2: `/log` Command Implementation
- [x] Task: Create `tests/test_log_command.py` with failing tests for the log retrieval logic (file reading, size limit). d82e9a1
- [x] Task: Implement `get_logs` function in `src/utils.py` (or similar) to handle safe file reading and tailing. 03c0d4d
- [x] Task: Update `src/handlers.py` to register the `/log` command handler. 3f021fc
- [x] Task: Verify `/log` command tests pass. 3f021fc
- [ ] Task: Conductor - User Manual Verification 'Log Command' (Protocol in workflow.md)

## Phase 3: Perplexity Client & Integration
- [ ] Task: Create `tests/test_perplexity_client.py` with failing tests for the dual-key fallback logic and API client wrapper.
- [ ] Task: Implement `PerplexityClient` in `src/integrations/perplexity_client.py` handling the Sonar LLM request and fallback logic.
- [ ] Task: Verify Perplexity client tests pass.
- [ ] Task: Update `src/agents/base.py` (or specific agent classes) to integrate the `Draft -> Verify -> Refine` workflow.
- [ ] Task: Create `tests/test_agent_verification.py` to verify the agent calls the client and handles the response/failure.
- [ ] Task: Conductor - User Manual Verification 'Perplexity Integration' (Protocol in workflow.md)

## Phase 4: Final Polish
- [ ] Task: Run full regression test suite.
- [ ] Task: Conductor - User Manual Verification 'Final Polish' (Protocol in workflow.md)
