# voice-mcp

A local MCP server that provides voice tools for Claude Code - speech-to-text using Whisper and text-to-speech using Supertonic.

## Features

### Speech-to-Text (Whisper)
- **listen_and_confirm** - Record speech, transcribe with Whisper, return transcript for confirmation
- **listen_for_yes_no** - Quick yes/no detection for binary decisions
- Local transcription using [faster-whisper](https://github.com/SYSTRAN/faster-whisper) (no API calls)
- Automatic silence detection to stop recording
- Audio beeps to indicate recording start/end

### Text-to-Speech (Supertonic)
- **speak** - Speak text aloud to the user
- Local synthesis using [Supertonic](https://github.com/supertone-inc/supertonic) (no API calls)
- Fast on-device generation (66M parameters)

### Combined Tools
- **speak_and_listen** - Speak then listen for a full response (reduces round trips)
- **speak_and_confirm** - Speak then listen for yes/no (reduces round trips)

## Requirements

- Python 3.10+
- [uv](https://docs.astral.sh/uv/) package manager
- A microphone (for speech-to-text)
- Speakers/headphones (for text-to-speech)

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

### Voice Input
Trigger voice input by saying something like:
- "let me explain verbally"
- "I'll tell you verbally"

Claude will call `listen_and_confirm`, you'll hear a beep, speak your response, and hear another beep when recording stops. Claude will repeat the transcript back for confirmation.

For yes/no questions, Claude can use `listen_for_yes_no` which interprets your response as "yes", "no", or "unclear".

### Voice Output
Ask Claude to speak responses:
- "say that out loud"
- "read that to me"

Claude will call `speak` to synthesize and play the audio through your speakers.

### Voice Conversations
For back-and-forth voice conversations, Claude can use the combined tools:
- `speak_and_listen` - Ask a question and wait for a full answer
- `speak_and_confirm` - Ask a yes/no question and get confirmation

These reduce latency by combining speak + listen in a single tool call.

### Dynamic Silence Detection

All listening tools accept a `silence_seconds` parameter (default: 2.5, minimum: 2.0). Claude can adjust this per-call based on context - for example, using a longer silence period if the user needs more time to think, or keeping it shorter for quick confirmations.

### Customizing Speech Behavior

The tool descriptions include default guidance for how Claude speaks. To customize this behavior, add instructions to your `CLAUDE.md` file. Examples:

```markdown
# Voice preferences
- When speaking, be brief and conversational
- Describe code changes at a high level, don't read syntax
- Summarize URLs instead of spelling them out
```

You can encourage different styles - more verbose explanations, different tone, etc.

## Notes

- **First-run downloads**: Models download automatically on first use - Whisper small (~460MB) and Supertonic (~260MB)
- **Silence detection**: Recording stops after 2.5 seconds of silence (configurable per-call, min 2.0s)
- **Platform**: Developed on Windows, should work on macOS/Linux

## Troubleshooting

**No audio output from TTS:**
- Some DACs require stereo output - the speak tool outputs stereo by default
- Check your default audio output device

**Recording stops too quickly:**
- The silence threshold may be too sensitive for your microphone
- Adjust `SILENCE_THRESHOLD` in `src/voice_mcp/audio.py` (default: 0.01)
- Claude can also pass a higher `silence_seconds` parameter per-call (default: 2.5, min: 2.0)

**Recording doesn't stop fast enough:**
- Claude can pass a lower `silence_seconds` parameter (minimum 2.0 seconds)

## Configuration

### Whisper (Speech-to-Text)
The Whisper model defaults to `small` running on CPU. To change this, edit `src/voice_mcp/transcribe.py`:

```python
# Model options: tiny, base, small, medium, large-v3
_model = WhisperModel("small", device="cpu", compute_type="int8")
```

For GPU acceleration, change `device="cpu"` to `device="cuda"` (requires cuDNN).

### Supertonic (Text-to-Speech)
The default voice is `M1`. Available voices can be found at the [Supertonic voice gallery](https://supertone-inc.github.io/supertonic-py/voices/).

## License

MIT
