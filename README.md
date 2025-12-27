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

**Tips for better TTS output:**
- Describe code/links instead of reading them verbatim (e.g., "the GitHub repo link" instead of spelling out URLs)
- Summarize code blocks rather than reading syntax (e.g., "the function takes a timeout and returns a dictionary")
- Keep spoken responses concise - long text is tedious to listen to

## Notes

- **First-run downloads**: Models download automatically on first use - Whisper small (~460MB) and Supertonic (~260MB)
- **Silence detection**: Recording stops after 2.5 seconds of silence
- **Platform**: Developed on Windows, should work on macOS/Linux

## Troubleshooting

**No audio output from TTS:**
- Some DACs require stereo output - the speak tool outputs stereo by default
- Check your default audio output device

**Recording stops too quickly:**
- The silence threshold may be too sensitive for your microphone
- Adjust `SILENCE_THRESHOLD` in `src/voice_mcp/audio.py` (default: 0.01)
- Increase `SILENCE_DURATION_S` if you need more pause time between phrases (default: 2.5 seconds)

**Recording doesn't stop fast enough:**
- Decrease `SILENCE_DURATION_S` in `src/voice_mcp/audio.py` for quicker cutoff

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
