# Plan: Enhanced Perplexity Legal Verification

This plan implements a more robust legal verification workflow by using a specialized Spanish Labor Law prompt for Perplexity, dynamically extracting case metadata, and logging the raw verification results to Notion for auditing.

## Phase 1: Metadata Extraction & Agent Logic [checkpoint: 9aba70a]
Implement the logic to extract or generate Case Metadata (Thesis, Specific Point, Legal Area) during the drafting process.

- [x] Task: Create `tests/test_metadata_extraction.py` to verify the extraction of legal thesis and area from draft content. 0000000
- [x] Task: Update `AgentBase.generate_structured_draft_with_retry` in `src/agents/base.py` to include `thesis`, `specific_point`, and `area` in the structured JSON output from the LLM. 0000000
- [x] Task: Verify metadata extraction tests pass. 0000000
- [ ] Task: Conductor - User Manual Verification 'Metadata Extraction' (Protocol in workflow.md)

## Phase 2: Perplexity Client Enhancement
Update the Perplexity integration to use the specialized prompt template and handle dynamic variables.

- [ ] Task: Update `tests/test_perplexity_client.py` to test the new `verify_draft` signature and prompt construction.
- [ ] Task: Modify `PerplexityClient.verify_draft` in `src/integrations/perplexity_client.py` to accept `context`, `thesis`, `specific_point`, and `area`.
- [ ] Task: Implement the "Spanish Labor Law Expert" prompt template in `PerplexityClient`.
- [ ] Task: Verify Perplexity client tests pass.
- [ ] Task: Conductor - User Manual Verification 'Enhanced Perplexity Prompt' (Protocol in workflow.md)

## Phase 3: Notion Auditing Implementation
Extend the Notion client to support logging the raw verification report as a visible block in the case page.

- [ ] Task: Create `tests/test_notion_audit_log.py` to verify appending a toggle block to a page.
- [ ] Task: Implement `append_verification_report` in `src/integrations/notion_client.py` using Notion's block append API (Toggle or Callout).
- [ ] Task: Verify Notion auditing tests pass.
- [ ] Task: Conductor - User Manual Verification 'Notion Auditing' (Protocol in workflow.md)

## Phase 4: Full Workflow Integration
Tie all components together in the main agent generation loop.

- [ ] Task: Update `AgentBase.generate_structured_draft_verified` in `src/agents/base.py` to orchestrate:
    1. Extract metadata from the initial draft.
    2. Call the enhanced Perplexity verification.
    3. Trigger the Notion audit log.
    4. Refine the draft.
- [ ] Task: Update `tests/test_agent_verification.py` to reflect the full integrated flow.
- [ ] Task: Verify the full integration tests pass.
- [ ] Task: Conductor - User Manual Verification 'Full Workflow Integration' (Protocol in workflow.md)
