# Specification: Enhanced Perplexity Legal Verification

## 1. Overview
This feature updates the Perplexity (Sonar LLM) verification prompt to enforce a strict "Spanish Labor Law Expert" persona. It introduces a dynamic prompt construction mechanism where specific case details (Thesis, Specific Point, Legal Area) are extracted from the draft and injected into the prompt before verification. Additionally, the full raw verification report from Perplexity will be logged to the corresponding Notion page for auditing purposes.

## 2. Functional Requirements

### 2.1 Prompt Engineering & Dynamic Injection
*   **Update `PerplexityClient.verify_draft`** (or create a new specialized method) to use the following prompt template:
    > "Actúa como abogado laboralista especializado en derecho laboral español. CONTEXTO DEL CASO: **{context}** OBJETIVO: Busca y analiza: 1. Normativa española aplicable (leyes, reales decretos, convenios colectivos) 2. Jurisprudencia del Tribunal Supremo y tribunales superiores que apoye **{thesis}** 3. Doctrina judicial relevante sobre **{specific_point}** REQUISITOS ESPECÍFICOS: - Jurisdicción: España - Ámbito: Derecho laboral **{area}** - Cita fuentes verificables... FORMATO DE RESPUESTA: Estructura en: (A) Normativa aplicable citada, (B) Jurisprudencia favorable con referencias exactas, (C) Líneas argumentales principales, (D) Posibles debilidades y cómo refutarlas"

*   **Extraction Logic:**
    *   The system must extract the following variables before calling Perplexity:
        *   `{context}`: The full content of the generated draft.
        *   `{thesis}`: The central legal argument (e.g., "Null dismissal due to discrimination").
        *   `{specific_point}`: Key legal doctrine to research (e.g., "Burden of proof reversal").
        *   `{area}`: Specific labor law domain (e.g., "Despido", "Modificación sustancial").
    *   *Implementation Note:* This metadata should be generated during the initial draft generation phase (via `generate_structured_draft`) or inferred via a lightweight analysis step.

### 2.2 Notion Auditing
*   **Log Verification Report:**
    *   After receiving the response from Perplexity, the system must append the **raw content** of the verification report to the associated Notion page.
    *   **Format:** Append as a "Toggle Block" (Toggle List) or "Callout" named "🔍 Auditoría de Verificación Legal (Perplexity)" containing the full text to keep the page clean while preserving data.

### 2.3 Refinement Workflow
*   The system continues to use the Perplexity response to refine the draft (Hybrid approach).
*   The verification report is treated as "Internal Feedback" for the refinement LLM pass.

## 3. Acceptance Criteria
*   [ ] **Prompt structure:** The Perplexity request matches the new template exactly, with all placeholders populated with relevant data from the current case.
*   [ ] **Perplexity Response:** The response follows the requested structure (A, B, C, D).
*   [ ] **Notion Logging:** The full Perplexity response appears in the Notion page body (not just a property link) under a distinct section/block.
*   [ ] **Refinement:** The final Google Doc reflects the legal corrections suggested by Perplexity.
*   [ ] **Error Handling:** If extraction of `{thesis}`/`{area}` fails, fall back to a generic prompt version or reasonable defaults.

## 4. Out of Scope
*   Changing the LLM model (remains `sonar-pro`).
*   Modifying the Google Drive folder structure.
