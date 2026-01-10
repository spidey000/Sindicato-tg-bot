# Specification: Docker Deployment with Portainer

## 1. Overview
This feature establishes a containerized deployment strategy for Marxnager, enabling seamless execution on a Virtual Private Server (VPS) managed by Portainer. It involves creating a robust `Dockerfile`, a `docker-compose.yml` for stack definition, and comprehensive documentation for deployment.

## 2. Functional Requirements

### 2.1 Container Image
*   **Base Image:** `python:3.11-slim` (Debian-based) to ensure maximum compatibility with dependencies.
*   **Working Directory:** `/app`.
*   **Dependencies:** Install system dependencies (if any) and Python packages from `requirements.txt`.
*   **Execution:** The container must launch the bot entry point (`src/main.py`) upon startup.

### 2.2 Configuration Management
*   **Environment Variables:** The application must accept configuration via environment variables loaded from a `.env` file or defined directly in the container environment.
*   **Secrets:** Sensitive data (API keys, tokens) will be managed via the environment variable injection method supported by Portainer Stacks.

### 2.3 Portainer Integration
*   **Stack Definition:** A `docker-compose.yml` file must be provided to define:
    *   The `marxnager-bot` service.
    *   Restart policies (e.g., `unless-stopped` or `always`).
    *   Volume mounts (if persistent storage is needed for logs or temporary files).
    *   Network configuration.

## 3. Non-Functional Requirements
*   **Efficiency:** The Docker image should be optimized for size where possible (using multi-stage builds is optional but good practice, though simple single-stage is accepted for the slim image).
*   **Maintainability:** The Docker setup should remain consistent with the project's structure.
*   **Documentation:** Clear instructions must be provided for a user to copy-paste the stack definition into Portainer.

## 4. Acceptance Criteria
*   [ ] A valid `Dockerfile` exists in the project root that builds the bot image successfully.
*   [ ] A `docker-compose.yml` file exists, suitable for use as a Portainer Stack.
*   [ ] A `DEPLOYMENT.md` (or updated `README.md`) provides step-by-step instructions for Portainer deployment.
*   [ ] The bot successfully connects to Telegram when running inside the container.
*   [ ] Environment variables are correctly read by the application within the container.
