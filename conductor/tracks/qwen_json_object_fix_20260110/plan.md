# Plan: Implement `json_object` for Qwen JSON Repair

## Phase 1: Create a Failing Test for `response_format` in Qwen Repair [checkpoint: 9348660]
- [x] Task: Create a new test case, `test_qwen_json_repair_response_format`, in `tests/test_openrouter.py`.
- [x] Task: Within this test, mock `OpenRouterClient._make_request`. The first call (primary model) should return a malformed JSON string to trigger the repair mechanism.
- [x] Task: Assert that `OpenRouterClient._repair_json` is called.
- [x] Task: Assert that the `_make_request` call originating from `_repair_json` *does not* receive `response_format={"type": "json_object"}`. (This is the failing condition that will be fixed later).
- [x] Task: Run the test and confirm that it fails as expected due to `response_format` not being passed to the mocked `_make_request` in the repair call.
- [ ] Task: Conductor - User Manual Verification 'Create a Failing Test for `response_format` in Qwen Repair' (Protocol in workflow.md)

## Phase 2: Implement the Fix for Qwen `json_object` [checkpoint: c68f1ba]
- [~] Task: Modify `src/integrations/openrouter_client.py` to re-enable conditional passing of `response_format` in `_make_request`. Specifically, add `if response_format: payload["response_format"] = response_format`.
- [x] Task: Modify `src/integrations/openrouter_client.py` to ensure that `_repair_json` explicitly passes `response_format={"type": "json_object"}` to its `_make_request` call.
- [ ] Task: Conductor - User Manual Verification 'Implement the Fix for Qwen `json_object`' (Protocol in workflow.md)

## Phase 3: Verify the Solution and Regression [checkpoint: ce6adc6]
- [x] Task: Run the new `test_qwen_json_repair_response_format` and confirm it now passes (i.e., `_make_request` in repair call receives `response_format={"type": "json_object"}`).
- [x] Task: Mock `OpenRouterClient._make_request` (for the repair call) to return a known *valid* JSON string, and assert that the final output of `OpenRouterClient.completion` is valid JSON.
- [x] Task: Run existing regression tests (`test_json_forcing_failure` and `test_qwen_json_fixing_passing_case`) to ensure no regressions are introduced.
- [ ] Task: Conductor - User Manual Verification 'Verify the Solution and Regression' (Protocol in workflow.md)