#!/usr/bin/env python3
"""Gmail MCP Server - Provides Gmail operations via MCP protocol."""

import asyncio
import json

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
from gmail_client import GmailClient

DEFAULT_MAX_RESULTS = 10
SERVER_NAME = "gmail-mcp-server"

# Initialise Gmail client
gmail = GmailClient()

# Create MCP server
server = Server(SERVER_NAME)


@server.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools"""
    return [
        Tool(
            name="get_unread_emails",
            description="Fetches unread emails from Gmail. Returns sender, subject, body snippet, message ID, and thread ID for each email.",
            inputSchema={
                "type": "object",
                "properties": {
                    "max_results": {
                        "type": "number",
                        "description": "Maximum number of emails to fetch (default: 10)",
                        "default": 10
                    }
                }
            }
        ),
        Tool(
            name="create_draft_reply",
            description="Creates a draft reply to an email. The reply will be properly threaded with the original message.",
            inputSchema={
                "type": "object",
                "properties": {
                    "message_id": {
                        "type": "string",
                        "description": "The ID of the message to reply to"
                    },
                    "thread_id": {
                        "type": "string",
                        "description": "The thread ID of the conversation"
                    },
                    "reply_body": {
                        "type": "string",
                        "description": "The text content of the reply"
                    }
                },
                "required": ["message_id", "thread_id", "reply_body"]
            }
        )
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Handle tool calls"""
    try:
        arguments = arguments or {}

        if name == "get_unread_emails":
            max_results = arguments.get("max_results", DEFAULT_MAX_RESULTS)
            emails = gmail.get_unread_emails(max_results=int(max_results))

            return [TextContent(
                type="text",
                text=json.dumps(emails, indent=2)
            )]

        elif name == "create_draft_reply":
            message_id = arguments.get("message_id")
            thread_id = arguments.get("thread_id")
            reply_body = arguments.get("reply_body")

            if not all([message_id, thread_id, reply_body]):
                return [TextContent(
                    type="text",
                    text=json.dumps({"error": "Missing required parameters"})
                )]

            result = gmail.create_draft_reply(message_id, thread_id, reply_body)

            return [TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]

        else:
            return [TextContent(
                type="text",
                text=json.dumps({"error": f"Unknown tool: {name}"})
            )]

    except Exception as e:
        return [TextContent(
            type="text",
            text=json.dumps({"error": f"Tool execution failed: {str(e)}"})
        )]

async def main() -> None:
    """Run the MCP server"""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())