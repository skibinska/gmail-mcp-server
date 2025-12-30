# Gmail MCP Server

An MCP server that allows Claude Desktop to read unread emails and create draft replies in Gmail.

## Features

- **get_unread_emails**: Fetches unread emails with sender, subject, body, message ID, and thread ID
- **create_draft_reply**: Creates properly threaded draft replies

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
2. Create a new project
3. Enable the Gmail API
4. Go to "APIs and services" → "Credentials" → "Create Credentials" → "OAuth client ID"
5. Choose "Desktop app" as application type
6. Download the credentials and save as `credentials.json` in the root directory
7. Add test user with your Gmail address under "Audience"

### 3. First Run - Authentication

```bash
python server.py
```

This will open a browser for OAuth authentication. Grant permissions and `token.json` will be created in the root directory.

### 4. Configure Claude Desktop

Edit your Claude Desktop config file:

**Mac/Linux:** `~/Library/Application Support/Claude/claude_desktop_config.json`

**Windows:** `%APPDATA%\Claude\claude_desktop_config.json`

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

- mcpServers - Root object containing all MCP server configurations
- gmail - Unique name for this server (you can choose any name)
- command - Path to the Python executable that will run the server
- args - Arguments passed to the command (the server script path)

What you need to replace:

`/absolute/path/to/python` - Full path to your Python interpreter
`/absolute/path/to/server.py` - Full path to your server.py file

Restart Claude Desktop.

## Usage Examples

In Claude Desktop:
```
"Show me my unread emails"

"Create a draft reply to the email from john@example.com saying I'll review the document by Friday"
```

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