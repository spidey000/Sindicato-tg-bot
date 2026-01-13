# Spec: Implement `json_object` for Qwen JSON Repair

## 1. Overview

This track aims to ensure the Qwen JSON repair mechanism within the `OpenRouterClient` consistently returns valid JSON by explicitly setting `response_format={"type": "json_object"}` for its API calls. This addresses previous issues where the Qwen repair model might not have been correctly instructed to return JSON, leading to malformed outputs. The change will specifically target the `_repair_json` function to avoid reintroducing issues with other models that do not support `response_format`.

## 2. Functional Requirements

- **Re-enable `response_format` in `_make_request` (Conditionally):** The `_make_request` method must be modified to accept and apply the `response_format` parameter, but only when it is explicitly provided by the caller. This will revert the previous change that completely removed `response_format`.
- **Explicit `json_object` for Qwen Repair:** The `_repair_json` method must explicitly pass `response_format={"type": "json_object"}` when it calls `_make_request` for the `REPAIR_MODEL` (Qwen).
- **Valid JSON Output from Qwen Repair:** When `_repair_json` is invoked, it should successfully guide the `REPAIR_MODEL` to return valid JSON.
- **Maintain General Model Behavior:** Other calls to `OpenRouterClient.completion` (i.e., for primary and fallback models) should continue to function as before, without implicitly forcing a JSON response unless `response_format` is explicitly passed to `completion`.

## 3. Non-Functional Requirements

- **No Regression:** The change must not reintroduce the "Bad Request" error (400) for primary or fallback models when `response_format` is not explicitly requested.
- **Maintain Performance:** The change should not negatively impact the performance of the API calls.

## 4. Acceptance Criteria

- **AC-1:** A test case exists that mocks an initial malformed JSON response from a primary model.
- **AC-2:** This test case then asserts that `_repair_json` is called with `response_format={"type": "json_object"}`.
- **AC-3:** The test case mocks a successful valid JSON response from the `REPAIR_MODEL`.
- **AC-4:** The final output of the `OpenRouterClient.completion` method is a valid JSON object.
- **AC-5:** Running the existing `test_json_forcing_failure` (which expects success without explicit JSON forcing) and `test_qwen_json_fixing_passing_case` (which verifies repair) tests should still pass, ensuring no regression.

## 5. Out of Scope

- Implementing `json_schema` with specific schemas for other models.
- Changes to the core logic of `OpenRouterClient` beyond what is necessary to correctly apply `json_object` for Qwen repair.
