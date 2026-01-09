# Product Guidelines: Marxnager

## Brand Voice & Tone
- **Formal and Technical:** The bot interacts as a specialized legal assistant. It uses precise administrative and legal terminology (e.g., "expediente," "fundamentación jurídica," "vulneración de derechos") to maintain credibility and professionalism.
- **Sober and Objective:** Communications are devoid of colloquialisms or excessive emotion. The focus is on facts, statutes, and procedural steps.

## Visual Identity & Formatting
- **Minimalist Aesthetics:** To reinforce the judicial and serious nature of the tool, the bot avoids excessive use of emojis.
- **Clean Markdown:** Information is structured using bold text for key data points (e.g., **ID:**, **Estado:**) and code blocks for distinct references, but visual clutter is kept to a strict minimum.

## Dual Workflow Interaction Principles
- **Seamless Handover:** The bot actively guides users from the public group to the private workspace.
- **Explicit Transition:** Commands executed in the group trigger a brief public confirmation followed by an explicit option (e.g., a button or inline link) to `[Continuar en privado]` for detailed work.
- **Private-First for Depth:** All sensitive actions—uploading evidence, recording voice notes, and refining drafts—are strictly confined to the private chat to protect worker privacy and reduce group noise.

## Error Handling
- **Sober and Brief:** Error messages are concise and formal.
- **Reference-Based:** Failures provide a standard notification (e.g., "Error en la operación. Código: N-503") rather than technical stack traces or overly apologetic conversational filler, maintaining the tool's professional facade.

## User Feedback & Progress Updates
- **Dynamic Checklists:** During long-running operations (like document creation), the bot uses a single message with dynamic formatting (strikethrough for pending, bold for completed) to show progress.
- **Failure Visualization:** If a multi-step process fails, the specific failed step is clearly marked with a `❌` emoji to provide immediate context without technical clutter.
- **Thorough Verification Logging:** The grounding process with Perplexity is explicitly logged in the system with success/failure status codes and response metadata (e.g., character length) for auditing.

## AI Content Guidelines
- **Strict Legal Structure:** All generated documents adhere to a rigid legal framework (Header, Statement of Facts, Legal Grounds, Petition) appropriate for the document type (ITSS complaint, lawsuit, etc.).
- **Objective Neutrality:** The AI focuses on objective facts and legal citations, avoiding inflammatory language.
- **Perplexity-Powered Refinement (Two-Stage Verification):**
    1.  **Drafting:** The AI generates an initial draft based on user input and templates.
    2.  **Validation:** This full draft is sent verbatim to the Perplexity Sonar API as a query to validate facts, check for recent legal precedents, and find relevant regulation updates.
    3.  **Refinement:** The AI synthesizes its original draft with the insights returned by Perplexity to produce a final, robust document.

## Integration Protocols
- **Perplexity API Fallback:** The system includes a redundancy mechanism for the Perplexity API, automatically switching to a backup key (`delegados`) if the primary key (`spidey00`) fails, ensuring continuous operation of the verification layer.
