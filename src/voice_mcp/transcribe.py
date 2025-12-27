"""Whisper transcription wrapper using faster-whisper."""

import sys
import numpy as np
from faster_whisper import WhisperModel

# Global model cache
_model: WhisperModel | None = None
_model_name: str = ""


def load_model(model_name: str = "small") -> WhisperModel:
    """Load Whisper model (cached after first load)."""
    global _model, _model_name

    if _model is not None and _model_name == model_name:
        return _model

    print(f"Loading Whisper model '{model_name}'...", file=sys.stderr)
    # Use CPU - GPU requires cuDNN which may not be installed
    _model = WhisperModel(model_name, device="cpu", compute_type="int8")
    _model_name = model_name
    print("Model loaded.", file=sys.stderr)

    return _model


def transcribe(audio: np.ndarray, model_name: str = "small") -> dict:
    """
    Transcribe audio using Whisper.

    Args:
        audio: numpy array of audio at 16kHz mono float32
        model_name: Whisper model size (tiny, base, small, medium, large-v3)

    Returns:
        dict with 'text' and 'language' keys
    """
    if len(audio) == 0:
        return {"text": "", "language": ""}

    model = load_model(model_name)

    # Whisper expects float32 audio normalized to [-1, 1]
    audio = audio.astype(np.float32)

    # Transcribe - faster-whisper handles audio of any length
    segments, info = model.transcribe(audio, beam_size=5)

    # Collect all segment texts
    text_parts = []
    for segment in segments:
        text_parts.append(segment.text)

    full_text = "".join(text_parts).strip()

    return {
        "text": full_text,
        "language": info.language,
    }
