# voice-mcp

A local MCP server that provides voice-to-text tools for Claude Code using Whisper.

## Features

- **listen_and_confirm** - Record speech, transcribe with Whisper, return transcript for confirmation
- **listen_for_yes_no** - Quick yes/no detection for binary decisions
- Local transcription using [faster-whisper](https://github.com/SYSTRAN/faster-whisper) (no API calls)
- Automatic silence detection to stop recording
- Audio beeps to indicate recording start/end

## Requirements

- Python 3.10+
- [uv](https://docs.astral.sh/uv/) package manager
- A microphone

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/jochiang/voice-mcp.git
   cd voice-mcp
   ```

2. Install dependencies:
   ```bash
   uv sync
   ```

3. Add to your Claude Code MCP settings (`.mcp.json` in your project or `~/.claude/settings.json`):
   ```json
   {
     "mcpServers": {
       "voice": {
         "command": "uv",
         "args": ["run", "--directory", "/path/to/voice-mcp", "voice-mcp"]
       }
     }
   }
   ```

4. Restart Claude Code to load the MCP server.

## Usage

In Claude Code, trigger voice input by saying something like:
- "let me explain verbally"
- "I'll tell you verbally"

Claude will call `listen_and_confirm`, you'll hear a beep, speak your response, and hear another beep when recording stops. Claude will repeat the transcript back for confirmation.

For yes/no questions, Claude can use `listen_for_yes_no` which interprets your response as "yes", "no", or "unclear".

## Configuration

The Whisper model defaults to `small` running on CPU. To change this, edit `src/voice_mcp/transcribe.py`:

```python
# Model options: tiny, base, small, medium, large-v3
_model = WhisperModel("small", device="cpu", compute_type="int8")
```

For GPU acceleration, change `device="cpu"` to `device="cuda"` (requires cuDNN).

## License

MIT
