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

## Examples

### Get unread emails - Claude

<img width="800" height="326" alt="" src="https://github.com/user-attachments/assets/99621814-8d2f-416e-9a1c-1ce94bb56ef2" />
<img width="952" height="534" alt="" src="https://github.com/user-attachments/assets/25120b4b-6ebe-48d9-bed8-c7a6d7773df5" />

### Unread emails - Gmail

![1000014875](https://github.com/user-attachments/assets/3e41587f-6337-4a10-b4df-1e6d6db8c770)



### Create draft email - Claude

<img width="862" height="602" alt="" src="https://github.com/user-attachments/assets/c7335ec9-4558-4f96-b491-5b51479c2f8d" />
<img width="911" height="596" alt="" src="https://github.com/user-attachments/assets/48db4ddb-7312-406a-816f-3ea54e3ec359" />

### Draft email - Gmail

![1000014877](https://github.com/user-attachments/assets/a1a8027b-0533-409d-b639-ea59bba2f8dc)

