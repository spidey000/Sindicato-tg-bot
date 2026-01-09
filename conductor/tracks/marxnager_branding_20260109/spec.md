# Spec: Branding Update to "Marxnager"

## Overview
Rename the application from its current name (Delegado 360) to "Marxnager" across all primary user touchpoints and documentation to align with the new branding.

## Functional Requirements
- **Telegram UI:** Update all bot messages, menus, and `/help` text to use "Marxnager".
- **Documentation:** Replace the old name with "Marxnager" in `README.md`, `PRD.md`, `CHANGELOG.md`, and any other relevant `.md` files in the root or `conductor/` directory.
- **New External Resources:** Ensure that any future Notion pages or Google Drive folders created by the bot reference "Marxnager" if the application name is part of the naming convention.

## Non-Functional Requirements
- **Tone Consistency:** The bot's professional and formal tone must remain unchanged.
- **Consistency:** Ensure the name is spelled and capitalized correctly ("Marxnager") in all instances.

## Acceptance Criteria
- Running `/start` or `/help` in Telegram displays the name "Marxnager".
- A search for the old name in `README.md`, `PRD.md`, and `CHANGELOG.md` returns no results.
- New cases created after this update do not reference the old name in their Notion/Drive metadata (where applicable).

## Out of Scope
- Renaming existing/historical folders in Google Drive or pages in Notion.
- Changing internal code identifiers (variable names, class names) or project directory names (e.g., `sindicato-tg-bot`).
- Modifying the bot's personality or conversational logic.