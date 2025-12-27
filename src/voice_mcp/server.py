"""MCP server for voice tools (speech-to-text and text-to-speech)."""

import asyncio
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from .tools import listen_and_confirm, listen_for_yes_no, speak_and_listen, speak_and_confirm
from .tts import speak

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
                "Recording stops automatically after 2.5 seconds of silence. "
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
        Tool(
            name="speak",
            description=(
                "Speak text aloud to the user using text-to-speech. "
                "Use this to verbally communicate with the user instead of just displaying text. "
                "Good for announcing results, reading content, or having a voice conversation."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "The text to speak aloud",
                    },
                    "voice": {
                        "type": "string",
                        "description": "Voice to use (default: M1)",
                        "default": "M1",
                    },
                },
                "required": ["text"],
            },
        ),
        Tool(
            name="speak_and_listen",
            description=(
                "Speak text aloud then immediately listen for a full response. "
                "Combines speak and listen_and_confirm in one call to reduce round trips. "
                "Use this for conversational exchanges where you ask a question and wait for an answer."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "The text to speak aloud",
                    },
                    "voice": {
                        "type": "string",
                        "description": "Voice to use (default: M1)",
                        "default": "M1",
                    },
                    "timeout_seconds": {
                        "type": "integer",
                        "description": "Maximum recording duration in seconds",
                        "default": 30,
                    },
                },
                "required": ["text"],
            },
        ),
        Tool(
            name="speak_and_confirm",
            description=(
                "Speak text aloud then immediately listen for a yes/no response. "
                "Combines speak and listen_for_yes_no in one call to reduce round trips. "
                "Use this for confirmations like 'Should I proceed?' or 'Is that correct?'"
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "The text to speak aloud",
                    },
                    "voice": {
                        "type": "string",
                        "description": "Voice to use (default: M1)",
                        "default": "M1",
                    },
                    "timeout_seconds": {
                        "type": "integer",
                        "description": "Maximum recording duration in seconds",
                        "default": 15,
                    },
                },
                "required": ["text"],
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

    elif name == "speak":
        text = arguments.get("text", "")
        voice = arguments.get("voice", "M1")
        result = await asyncio.get_event_loop().run_in_executor(
            None, lambda: speak(text, voice)
        )

        if result["success"]:
            return [TextContent(
                type="text",
                text=f"Spoke: {text[:100]}{'...' if len(text) > 100 else ''}\nDuration: {result['duration']:.2f}s"
            )]
        else:
            return [TextContent(
                type="text",
                text=f"Error: {result.get('error', 'Unknown error')}"
            )]

    elif name == "speak_and_listen":
        text = arguments.get("text", "")
        voice = arguments.get("voice", "M1")
        timeout = arguments.get("timeout_seconds", 30)
        result = await asyncio.get_event_loop().run_in_executor(
            None, lambda: speak_and_listen(text, voice, timeout)
        )

        if result["success"]:
            return [TextContent(
                type="text",
                text=f"Spoke: {text[:100]}{'...' if len(text) > 100 else ''}\nTranscript: {result['transcript']}\nLanguage: {result['language']}"
            )]
        else:
            return [TextContent(
                type="text",
                text=f"Spoke: {result['spoke']}\nError: {result.get('error', 'Unknown error')}"
            )]

    elif name == "speak_and_confirm":
        text = arguments.get("text", "")
        voice = arguments.get("voice", "M1")
        timeout = arguments.get("timeout_seconds", 15)
        result = await asyncio.get_event_loop().run_in_executor(
            None, lambda: speak_and_confirm(text, voice, timeout)
        )

        if result["success"]:
            return [TextContent(
                type="text",
                text=f"Spoke: {text[:100]}{'...' if len(text) > 100 else ''}\nAnswer: {result['answer']}\nTranscript: {result['transcript']}"
            )]
        else:
            return [TextContent(
                type="text",
                text=f"Spoke: {result['spoke']}\nAnswer: unclear\nError: {result.get('error', 'Unknown error')}"
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
