# Implementation Plan - LLM Hierarchy and JSON Repair

This plan implements a multi-stage LLM strategy with specific models for drafting, existing models for refinement, and a global JSON repair mechanism using Qwen.

## Phase 1: Infrastructure & Configuration [checkpoint: af3d0f6]
Focus on updating `config.py` and `OpenRouterClient` to handle the new model sets and the Qwen repair call.

- [x] **Task 1: Update Configuration and Constants** <!-- 838b319 -->
    - [ ] Add `PRIMARY_DRAFT_MODEL` (`openai/gpt-oss-120b:free`) and `FALLBACK_DRAFT_MODEL` (`google/gemma-3-27b-it:free`) to `src/config.py`.
    - [ ] Add `REPAIR_MODEL` (`qwen/qwen3-4b:free`) to `src/config.py`.
- [x] **Task 2: Enhance `OpenRouterClient` Interface** <!-- 6efda95 -->
    - [ ] Update `OpenRouterClient.generate_completion` (or similar method) to accept a `task_type` parameter (e.g., `DRAFT`, `REFINEMENT`, `REPAIR`).
- [ ] **Task: Conductor - User Manual Verification 'Phase 1: Infrastructure & Configuration' (Protocol in workflow.md)**

## Phase 2: Implementation of Model Hierarchy (Drafting)
Implement the sequential fallback for the first draft generation.

- [ ] **Task 1: Write Tests for Drafting Hierarchy**
    - [ ] Create `tests/test_llm_hierarchy.py`.
    - [ ] Test that `DRAFT` task type correctly attempts Primary then Fallback on failure.
- [ ] **Task 2: Implement Drafting Fallback Logic**
    - [ ] Modify `OpenRouterClient` to handle the try-except block for Primary -> Fallback models when `task_type=DRAFT`.
- [ ] **Task: Conductor - User Manual Verification 'Phase 2: Implementation of Model Hierarchy (Drafting)' (Protocol in workflow.md)**

## Phase 3: JSON Repair Mechanism
Implement the global logic that catches invalid JSON and sends it to Qwen.

- [ ] **Task 1: Write Tests for JSON Repair**
    - [ ] Add tests to `tests/test_llm_hierarchy.py` for malformed JSON triggers.
    - [ ] Mock a malformed response and verify that `qwen/qwen3-4b:free` is called with the correct prompt and `structured_outputs`.
- [ ] **Task 2: Implement `_repair_json` Private Method**
    - [ ] Create a dedicated method in `OpenRouterClient` for the Qwen repair call.
    - [ ] Ensure it uses the `response_format: { "type": "json_object" }` parameter.
- [ ] **Task 3: Integrate Repair into Main Execution Flow**
    - [ ] Update the `OpenRouterClient` completion loop to wrap JSON parsing in a try-repair-retry logic.
- [ ] **Task: Conductor - User Manual Verification 'Phase 3: JSON Repair Mechanism' (Protocol in workflow.md)**

## Phase 4: Integration and Refinement Stage
Ensure the existing refinement flow uses the new repair logic but keeps its current models.

- [ ] **Task 1: Verify Refinement Logic**
    - [ ] Add integration tests ensuring `REFINEMENT` tasks still use `deepseek-r1` (or current config) but *do* trigger Qwen repair on failure.
- [ ] **Task 2: Update Agent Handlers**
    - [ ] Update calls in `Inspector`, `Litigante`, and `Comunicador` to pass the correct `task_type`.
- [ ] **Task: Conductor - User Manual Verification 'Phase 4: Integration and Refinement Stage' (Protocol in workflow.md)**
