"""MCP server for voice-to-text tools."""

import asyncio
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from .tools import listen_and_confirm, listen_for_yes_no

# Create MCP server
server = Server("voice-mcp")


@server.list_tools()
async def list_tools() -> list[Tool]:
    """List available voice tools."""
    return [
        Tool(
            name="listen_and_confirm",
            description=(
                "Record audio from the user's microphone and transcribe it using Whisper. "
                "Use this when you need to hear the user explain something verbally. "
                "Recording stops automatically after 1.5 seconds of silence, or the user can press Enter. "
                "After calling this, repeat the transcript back to the user so they can confirm or correct it."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "timeout_seconds": {
                        "type": "integer",
                        "description": "Maximum recording duration in seconds",
                        "default": 30,
                    },
                },
            },
        ),
        Tool(
            name="listen_for_yes_no",
            description=(
                "Record a short audio response and interpret it as yes or no. "
                "Use this for quick confirmations or binary decisions. "
                "Returns 'yes', 'no', or 'unclear' based on what the user says."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "timeout_seconds": {
                        "type": "integer",
                        "description": "Maximum recording duration in seconds",
                        "default": 10,
                    },
                },
            },
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Handle tool calls."""
    if name == "listen_and_confirm":
        timeout = arguments.get("timeout_seconds", 30)
        # Run in thread pool since audio recording is blocking
        result = await asyncio.get_event_loop().run_in_executor(
            None, lambda: listen_and_confirm(timeout)
        )

        if result["success"]:
            return [TextContent(
                type="text",
                text=f"Transcript: {result['transcript']}\nLanguage: {result['language']}"
            )]
        else:
            return [TextContent(
                type="text",
                text=f"Error: {result.get('error', 'Unknown error')}"
            )]

    elif name == "listen_for_yes_no":
        timeout = arguments.get("timeout_seconds", 10)
        result = await asyncio.get_event_loop().run_in_executor(
            None, lambda: listen_for_yes_no(timeout)
        )

        if result["success"]:
            return [TextContent(
                type="text",
                text=f"Answer: {result['answer']}\nTranscript: {result['transcript']}"
            )]
        else:
            return [TextContent(
                type="text",
                text=f"Answer: unclear\nError: {result.get('error', 'Unknown error')}"
            )]

    else:
        return [TextContent(type="text", text=f"Unknown tool: {name}")]


async def run_server():
    """Run the MCP server."""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


def main():
    """Entry point."""
    asyncio.run(run_server())


if __name__ == "__main__":
    main()
