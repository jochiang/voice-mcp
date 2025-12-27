"""MCP tool implementations."""

from .audio import AudioRecorder
from .transcribe import transcribe

# Words/phrases that indicate "yes"
YES_PATTERNS = {
    "yes", "yeah", "yep", "yup", "sure", "correct", "right", "affirmative",
    "absolutely", "definitely", "of course", "ok", "okay", "uh huh", "uh-huh",
    "go ahead", "do it", "proceed", "confirm", "confirmed", "that's right",
    "yes please", "please do", "sounds good", "go for it",
}

# Words/phrases that indicate "no"
NO_PATTERNS = {
    "no", "nope", "nah", "negative", "wrong", "incorrect", "don't", "do not",
    "stop", "cancel", "abort", "wait", "hold on", "not yet", "no thanks",
    "no thank you", "i don't think so", "that's wrong", "that's not right",
}


def listen_and_confirm(timeout_seconds: int = 30) -> dict:
    """
    Record and transcribe user speech for confirmation.

    Args:
        timeout_seconds: Maximum recording duration

    Returns:
        dict with 'transcript' and 'success' keys
    """
    recorder = AudioRecorder()

    try:
        audio = recorder.record(timeout_seconds=float(timeout_seconds))

        if len(audio) == 0:
            return {
                "transcript": "",
                "success": False,
                "error": "No audio recorded",
            }

        result = transcribe(audio)

        return {
            "transcript": result["text"],
            "language": result["language"],
            "success": True,
        }
    except Exception as e:
        return {
            "transcript": "",
            "success": False,
            "error": str(e),
        }


def listen_for_yes_no(timeout_seconds: int = 10) -> dict:
    """
    Record and interpret user speech as yes/no response.

    Args:
        timeout_seconds: Maximum recording duration

    Returns:
        dict with 'answer' (yes/no/unclear), 'transcript', and 'success' keys
    """
    recorder = AudioRecorder(
        silence_duration=1.0,  # Shorter silence threshold for quick responses
    )

    try:
        audio = recorder.record(timeout_seconds=float(timeout_seconds))

        if len(audio) == 0:
            return {
                "answer": "unclear",
                "transcript": "",
                "success": False,
                "error": "No audio recorded",
            }

        result = transcribe(audio)
        transcript = result["text"].lower().strip()

        # Check for yes/no patterns
        answer = "unclear"

        # Check exact matches and common phrases
        for pattern in YES_PATTERNS:
            if pattern in transcript:
                answer = "yes"
                break

        if answer == "unclear":
            for pattern in NO_PATTERNS:
                if pattern in transcript:
                    answer = "no"
                    break

        return {
            "answer": answer,
            "transcript": result["text"],
            "language": result["language"],
            "success": True,
        }
    except Exception as e:
        return {
            "answer": "unclear",
            "transcript": "",
            "success": False,
            "error": str(e),
        }
