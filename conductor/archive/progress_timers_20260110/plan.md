# Implementation Plan - Track: Progress Message & Timer Enhancement

## Phase 1: Research & Setup [checkpoint: 5b98a24b]
- [x] Task: Analyze current progress message logic in `src/handlers.py` and `src/utils.py`. b4ef054
- [x] Task: Identify where `Perplexity Verification` is called and how to hook into the start/end of each step for timing. b4ef054
- [x] Task: Create a new helper class `ProgressTracker` in `src/utils.py` to manage state, timers, and formatting. b4ef054
- [x] Task: Conductor - User Manual Verification 'Research & Setup' (Protocol in workflow.md) b4ef054

## Phase 2: Implementation - Core Logic
- [x] Task: Implement `ProgressTracker` class with methods: `start_step`, `complete_step`, `get_message_text`. 57987a0e
    - [x] Sub-task: TDD - Write tests for `ProgressTracker` (ordering, timer formatting, icons). 57987a0e
    - [x] Sub-task: Implement the class. 57987a0e
- [x] Task: Integrate `ProgressTracker` into `src/handlers.py` (Command handlers). 57987a0e
    - [x] Sub-task: Initialize tracker at the start of `/demanda` and `/email`. 57987a0e
    - [x] Sub-task: Replace hardcoded status messages with dynamic tracker calls. 57987a0e
- [x] Task: Conductor - User Manual Verification 'Implementation - Core Logic' (Protocol in workflow.md) 57987a0e

## Phase 3: Integration & Refinement [checkpoint: bc256adb]
- [x] Task: Update `src/agents/base.py` and `src/integrations/*.py` to accept and use the tracker (or callbacks) if necessary, OR update the tracker from the main loop in `src/main.py` / handlers. 57987a0e
- [x] Task: Rename "Verification" to "Perplexity Check" in all outputs. 57987a0e
- [x] Task: Verify the visual output matches the spec (Order: Init -> Drafting -> Notion -> Drive -> Perplexity -> Refinement -> Docs -> Final Notion). 57987a0e
- [x] Task: Conductor - User Manual Verification 'Integration & Refinement' (Protocol in workflow.md) 57987a0e

## Phase 4: Final Verification
- [x] Task: Run full system test with `/demanda` command to verify real-time updates and timer accuracy.
- [x] Task: Conductor - User Manual Verification 'Final Verification' (Protocol in workflow.md)
