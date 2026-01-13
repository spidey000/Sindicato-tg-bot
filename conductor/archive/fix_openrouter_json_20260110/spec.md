# Spec: Fix OpenRouter API Call Failures

## 1. Overview

This track addresses a critical bug where calls to the OpenRouter API are consistently failing with various HTTP error codes (404, 400, 429), preventing the application from getting a valid response from the language models. The original request suggests this might be due to a "json parameter forcing" issue.

## 2. Functional Requirements

- **Remove JSON Forcing:** The primary change is to modify the OpenRouter API call to remove any parameter that forces a JSON response, as this is the suspected root cause of the failures.
- **Successful API Calls:** After the fix, API calls to OpenRouter should complete successfully (HTTP 200 OK) for both primary and fallback models.
- **Valid LLM Response:** The application must be able to correctly parse the response from the LLM after the change is implemented.
- **Maintain Retry Logic:** The existing retry and fallback logic in `openrouter_client` should be preserved and function as expected.

## 3. Non-Functional Requirements

- **Performance:** The change should not negatively impact the performance of the API calls.

## 4. Acceptance Criteria

- **AC-1:** When a request is made to an agent that uses the `openrouter_client`, the call to the OpenRouter API completes with an HTTP 200 status code.
- **AC-2:** The application correctly receives and processes the content from the LLM's response.
- **AC-3:** The retry and fallback mechanisms are still functional and are triggered only on genuine, transient failures, not on persistent failures caused by the client's request format.

## 5. Out of Scope

- Changes to the retry logic itself, other than ensuring it works with the corrected API call.
- Modifications to any other part of the application not directly related to the OpenRouter integration.