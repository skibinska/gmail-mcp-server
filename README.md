# Gmail MCP Server

An MCP server that allows Claude Desktop to read unread emails and create draft replies in Gmail.

## Features

- **get_unread_emails**: Fetches unread emails with sender, subject, body, message ID, and thread ID
- **create_draft_reply**: Creates properly threaded draft replies

## Requirements

- Python 3.14+
- Gmail account
- Google Cloud Console access

## Setup

### 1. Install Dependencies
```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Gmail API Configuration

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. [Create a new project](https://developers.google.com/workspace/guides/create-project)
3. [Enable Gmail API](https://support.google.com/googleapi/answer/6158841?hl=en)
4. Go to "APIs and services" → "Credentials" → "Create Credentials" → "OAuth client ID"
5. Choose "Desktop app" as application type
6. Download the credentials and save as `credentials.json` in the root directory
7. Add test user with your Gmail address under "Audience"

### 3. First Run - Authentication

```bash
python server.py
```

This will open a browser for OAuth authentication. `token.json` will be created in the root directory.

### 4. Configure Claude Desktop

Edit your Claude Desktop config file:

**Mac:** `~/Library/Application Support/Claude/claude_desktop_config.json`

Add:
```json
{
  "mcpServers": {
    "gmail": {
      "command": "/absolute/path/to/python",
      "args": ["/absolute/path/to/server.py"]
    }
  }
}
```

This configuration tells Claude Desktop how to connect to your Gmail MCP server:

- **mcpServers** - Root object containing all MCP server configurations
- **gmail** - Unique name for this server (you can choose any name)
- **command** - Path to the Python executable that will run the server
- **args** - Arguments passed to the command (the server script path)

What you need to replace:

- `/absolute/path/to/python` - Full path to your Python interpreter
- `/absolute/path/to/server.py` - Full path to your server.py file

Restart Claude Desktop.

## OAuth Scopes

- `gmail.readonly` - Read emails
- `gmail.compose` - Create drafts

## Project Structure

- `server.py` - MCP server implementation
- `gmail_client.py` - Gmail API wrapper
- `credentials.json` - OAuth credentials (not in git)
- `token.json` - OAuth token (auto-generated, not in git)

## Troubleshooting

- **Authentication fails**: Delete `token.json` and run `python server.py` again
- **Claude can't connect**: Check the absolute path in config file

## Usage Examples

### Get unread emails - Claude

<img width="500" height="280" src="https://github.com/user-attachments/assets/25120b4b-6ebe-48d9-bed8-c7a6d7773df5" />
<img width="450" height="360" src="https://github.com/user-attachments/assets/930b15c3-4689-4147-a25e-c06a1bf1f1e0" />

### Unread emails - Gmail

<img width="400" src="https://github.com/user-attachments/assets/3e41587f-6337-4a10-b4df-1e6d6db8c770" />

### Create draft email - Claude

<img width="450" height="315" src="https://github.com/user-attachments/assets/c7335ec9-4558-4f96-b491-5b51479c2f8d" />
<img width="851" height="380" alt="" src="https://github.com/user-attachments/assets/b3f75261-4a7e-4cea-8846-46b46be20c87" />

### Draft email - Gmail

<img width="400" src="https://github.com/user-attachments/assets/a1a8027b-0533-409d-b639-ea59bba2f8dc" />

