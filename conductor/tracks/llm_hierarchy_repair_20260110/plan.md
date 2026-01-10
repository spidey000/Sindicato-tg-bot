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

## Phase 2: Implementation of Model Hierarchy (Drafting) [checkpoint: d2fc406]
Implement the sequential fallback for the first draft generation.

- [x] **Task 1: Write Tests for Drafting Hierarchy** <!-- 084e601 -->
- [x] **Task 2: Implement Drafting Fallback Logic** <!-- 084e601 -->
    - [ ] Modify `OpenRouterClient` to handle the try-except block for Primary -> Fallback models when `task_type=DRAFT`.
- [ ] **Task: Conductor - User Manual Verification 'Phase 2: Implementation of Model Hierarchy (Drafting)' (Protocol in workflow.md)**

## Phase 3: JSON Repair Mechanism [checkpoint: 0e1cb21]
Implement the global logic that catches invalid JSON and sends it to Qwen.

- [x] **Task 1: Write Tests for JSON Repair** <!-- 868d413 -->
- [x] **Task 2: Implement `_repair_json` Private Method** <!-- 868d413 -->
- [x] **Task 3: Integrate Repair into Main Execution Flow** <!-- 868d413 -->
- [ ] **Task: Conductor - User Manual Verification 'Phase 3: JSON Repair Mechanism' (Protocol in workflow.md)**

## Phase 4: Integration and Refinement Stage [checkpoint: 251d961]
Ensure the existing refinement flow uses the new repair logic but keeps its current models.

- [x] **Task 1: Verify Refinement Logic** <!-- e66a77d -->
    - [ ] Add integration tests ensuring `REFINEMENT` tasks still use `deepseek-r1` (or current config) but *do* trigger Qwen repair on failure.
- [x] **Task 2: Update Agent Handlers** <!-- d6efda9 -->
    - [ ] Update calls in `Inspector`, `Litigante`, and `Comunicador` to pass the correct `task_type`.
- [ ] **Task: Conductor - User Manual Verification 'Phase 4: Integration and Refinement Stage' (Protocol in workflow.md)**
