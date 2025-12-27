"""Text-to-speech using Supertonic."""

import sys
import numpy as np
import sounddevice as sd
from supertonic import TTS

# Global TTS instance cache
_tts: TTS | None = None
_voice_style = None

# Audio playback settings
PLAYBACK_SAMPLE_RATE = 24000  # Supertonic outputs 24kHz audio


def load_tts() -> TTS:
    """Load TTS model (cached after first load)."""
    global _tts, _voice_style

    if _tts is not None:
        return _tts

    print("Loading Supertonic TTS model...", file=sys.stderr)
    _tts = TTS(auto_download=True)
    _voice_style = _tts.get_voice_style(voice_name="M1")
    print("TTS model loaded.", file=sys.stderr)

    return _tts


def speak(text: str, voice: str = "M1") -> dict:
    """
    Synthesize and play speech from text.

    Args:
        text: The text to speak
        voice: Voice name (default: M1)

    Returns:
        dict with 'success' and 'duration' keys
    """
    if not text.strip():
        return {"success": False, "error": "No text provided", "duration": 0}

    try:
        global _voice_style

        tts = load_tts()

        # Get voice style if different from cached
        if voice != "M1" or _voice_style is None:
            _voice_style = tts.get_voice_style(voice_name=voice)

        # Synthesize speech
        wav, duration = tts.synthesize(text, voice_style=_voice_style)

        # Convert to numpy array if needed and ensure float32
        if not isinstance(wav, np.ndarray):
            wav = np.array(wav, dtype=np.float32)
        else:
            wav = wav.astype(np.float32)

        # Play audio (stereo for compatibility with DACs)
        stereo = np.column_stack([wav, wav])
        sd.play(stereo, PLAYBACK_SAMPLE_RATE, blocking=True)

        return {
            "success": True,
            "duration": duration,
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "duration": 0,
        }
