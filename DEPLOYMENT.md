# Deployment Guide: Marxnager Bot

This guide explains how to deploy the Marxnager bot on a VPS using Docker and Portainer.

## Prerequisites

- A VPS with Docker and Docker Compose installed.
- Portainer installed and accessible.
- A Telegram Bot Token from @BotFather.
- API keys for Notion, OpenRouter, and Perplexity.

## Deployment via Portainer (Stacks)

1.  **Log in** to your Portainer instance.
2.  **Navigate** to the environment where you want to deploy (e.g., `local`).
3.  **Click on "Stacks"** in the left sidebar.
4.  **Click "+ Add stack"**.
5.  **Name your stack** (e.g., `marxnager-bot`).
6.  **Build method:** Choose "Web editor".
7.  **Paste the content** of `docker-compose.yml` from this repository into the editor.
8.  **Environment variables:**
    - Click "Add environment variable" for each of the following (or use the "Advanced mode" to paste a list):
    
    ```text
    BOT_TOKEN=your_telegram_bot_token
    AUTHORIZED_USER_IDS=comma_separated_ids
    OPENROUTER_API_KEY=your_key
    PERPLEXITY_API_KEY_PRIMARY=your_key
    PERPLEXITY_API_KEY_FALLBACK=your_key
    NOTION_TOKEN=your_token
    NOTION_DATABASE_ID=your_id
    DRIVE_FOLDER_DENUNCIAS=your_folder_id
    DRIVE_FOLDER_DEMANDAS=your_folder_id
    DRIVE_FOLDER_EMAILS=your_folder_id
    ADMIN_EMAIL=your_email
    ```
9.  **Click "Deploy the stack"**.

## Local Docker Deployment (Manual)

If you prefer to deploy manually via CLI:

1.  Clone the repository:
    ```bash
    git clone https://github.com/your-repo/marxnager-tg-bot.git
    cd marxnager-tg-bot
    ```
2.  Create and configure your `.env` file:
    ```bash
    cp .env.example .env
    nano .env
    ```
3.  Build and run the container:
    ```bash
    docker-compose up -d --build
    ```

## Monitoring Logs

- **In Portainer:** Go to Stacks -> marxnager-bot -> Containers -> marxnager-bot -> Logs.
- **Via CLI:**
    ```bash
    docker logs -f marxnager-bot
    ```
