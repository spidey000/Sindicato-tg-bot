# Specification: LLM Hierarchy and JSON Repair Strategy

## 1. Overview
This feature implements a cost-effective and robust model hierarchy for the `OpenRouterClient`. It introduces specific model selection for drafting versus refinement and adds a novel "JSON Repair" mechanism using `qwen/qwen3-4b:free` to correct malformed outputs before falling back to a full retry.

## 2. Functional Requirements

### 2.1 Model Selection Strategies
The `OpenRouterClient` must support distinct model configurations for different stages:

*   **Stage A: First Draft Generation**
    *   **Primary Model:** `openai/gpt-oss-120b:free`
    *   **Fallback Model:** `google/gemma-3-27b-it:free` (Used if Primary fails on network/API errors).

*   **Stage B: Refinement**
    *   **Models:** Continue using the existing configured models (e.g., `deepseek/deepseek-r1-0528:free` or as currently defined in `config.py`).

### 2.2 System Prompt Enforcement
*   All requests (Drafting and Refinement) must include a system instruction explicitly demanding **structured JSON output**.

### 2.3 JSON Validation & Repair Logic (Global)
This logic applies to **BOTH** Drafting and Refinement steps (but excludes Perplexity):
1.  **Validate:** Attempt to parse the LLM output as JSON.
2.  **Success:** If valid, return the data.
3.  **Failure (Repair Step):** If the output is not valid JSON:
    *   **Action:** Call `qwen/qwen3-4b:free`.
    *   **Parameters:** Enable `structured_outputs` (via `response_format: { type: "json_object" }` or provider equivalent).
    *   **Prompt:** Use a simple wrapper: "Convert this text into valid JSON matching this schema: [Schema] 

 [Invalid Output Text]".
4.  **Final Fallback:** If the Qwen repair step fails or returns invalid JSON, trigger the existing standard retry mechanism (retrying the original query).

### 2.4 Scope & Exclusions
*   **In Scope:**
    *   `OpenRouterClient` logic for model selection based on task type.
    *   JSON Repair logic for OpenRouter calls.
*   **Out of Scope / Excluded:**
    *   **Perplexity/Sonar Calls:** The `PerplexityClient` and its verification logic remain unchanged and are excluded from this repair strategy.

## 3. Non-Functional Requirements
*   **Latency:** Prioritize speed for drafts.
*   **Reasoning:** Prioritize capability for refinement (maintain existing).
*   **Resilience:** The repair step should prevent full regeneration cycles for minor syntax errors.

## 4. Acceptance Criteria
*   [ ] `OpenRouterClient` selects `openai/gpt-oss-120b:free` -> `google/gemma-3-27b-it:free` specifically for drafting tasks.
*   [ ] Refinement tasks continue to use their currently configured models.
*   [ ] Malformed JSON responses from EITHER stage trigger a call to `qwen/qwen3-4b:free`.
*   [ ] The Qwen call utilizes `structured_outputs` parameters.
*   [ ] Perplexity calls continue to function without these changes.
*   [ ] Unit tests verify the fallback and repair flows using mocks.
