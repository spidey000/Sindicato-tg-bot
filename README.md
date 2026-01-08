# Sindicato Telegram Bot (Delegado 360)

This is a specialized Telegram bot for managing union activities, generating legal documents, and integrating with Notion and Google Drive.

## Features
- **Public/Private Workflow**: Log incidents in group chats, refine details in private DMs.
- **AI Agents**: Specialized agents for ITSS Complaints, Judicial Claims, and HR Emails.
- **Integrations**: Auto-creates Notion entries, Drive folders, and Google Docs.

## Setup

### 1. Environment Variables
Create a `.env` file based on `.env.example`:
```bash
BOT_TOKEN=your_telegram_bot_token
AUTHORIZED_USER_IDS=123456789,987654321
NOTION_TOKEN=your_notion_integration_token
NOTION_DATABASE_ID=your_database_id
GOOGLE_DRIVE_CREDENTIALS_PATH=google_credentials.json
GOOGLE_DRIVE_ROOT_FOLDER_ID=your_drive_folder_id
```

### 2. Google Cloud Integration
To enable Drive and Docs:
1.  Create a Project in Google Cloud Console.
2.  Enable **Google Drive API** and **Google Docs API**.
3.  Create a **Service Account** and download the **JSON Key**.
4.  Save the key as `google_credentials.json` in the project root.
5.  **Share** your target Google Drive folder with the Service Account email (give "Editor" access).
6.  Copy the Folder ID from the URL into `.env`.

### 3. Running the Bot
```bash
# Install dependencies
pip install -r requirements.txt

# Run
python src/main.py
```

## Testing
Run unit tests:
```bash
python -m unittest discover tests
```