"""Audio recording with voice activity detection."""

import sys
import threading
import queue
import numpy as np
import sounddevice as sd

SAMPLE_RATE = 16000  # Whisper expects 16kHz
CHANNELS = 1
DTYPE = np.float32
BLOCK_DURATION_MS = 30  # Process audio in 30ms blocks
SILENCE_THRESHOLD = 0.01  # RMS threshold for silence detection
SILENCE_DURATION_S = 2.5  # Seconds of silence before auto-stop

# Beep settings
BEEP_FREQ_START = 880  # Hz (A5 note) - start recording
BEEP_FREQ_END = 440  # Hz (A4 note) - end recording (lower pitch)
BEEP_DURATION = 0.25  # seconds
BEEP_SAMPLE_RATE = 44100  # Standard audio output rate


def play_beep(frequency: float = BEEP_FREQ_START, duration: float = BEEP_DURATION):
    """Play a short beep tone."""
    t = np.linspace(0, duration, int(BEEP_SAMPLE_RATE * duration), False)
    # Generate sine wave with fade in/out to avoid clicks
    tone = np.sin(2 * np.pi * frequency * t)
    fade_samples = int(BEEP_SAMPLE_RATE * 0.01)  # 10ms fade
    tone[:fade_samples] *= np.linspace(0, 1, fade_samples)
    tone[-fade_samples:] *= np.linspace(1, 0, fade_samples)
    tone = (tone * 0.5).astype(np.float32)  # Volume level
    # Convert to stereo for DACs that require it
    stereo = np.column_stack([tone, tone])
    sd.play(stereo, BEEP_SAMPLE_RATE, blocking=True)


class AudioRecorder:
    """Records audio with silence detection."""

    def __init__(
        self,
        sample_rate: int = SAMPLE_RATE,
        silence_threshold: float = SILENCE_THRESHOLD,
        silence_duration: float = SILENCE_DURATION_S,
    ):
        self.sample_rate = sample_rate
        self.silence_threshold = silence_threshold
        self.silence_duration = silence_duration
        self._audio_queue: queue.Queue[np.ndarray] = queue.Queue()
        self._stop_event = threading.Event()

    def _audio_callback(self, indata: np.ndarray, frames: int, time_info, status):
        """Callback for sounddevice stream."""
        if status:
            print(f"Audio status: {status}", file=sys.stderr)
        self._audio_queue.put(indata.copy())

    def _calculate_rms(self, audio: np.ndarray) -> float:
        """Calculate RMS (root mean square) of audio for volume detection."""
        return float(np.sqrt(np.mean(audio**2)))

    def record(self, timeout_seconds: float = 30.0) -> np.ndarray:
        """
        Record audio until silence detected or timeout.

        Returns:
            numpy array of recorded audio at 16kHz mono float32
        """
        self._stop_event.clear()
        self._audio_queue = queue.Queue()

        recorded_chunks: list[np.ndarray] = []
        silence_samples = 0
        samples_for_silence = int(self.silence_duration * self.sample_rate)
        total_samples = 0
        max_samples = int(timeout_seconds * self.sample_rate)

        block_size = int(self.sample_rate * BLOCK_DURATION_MS / 1000)

        # Play beep to indicate recording start
        play_beep(BEEP_FREQ_START)

        with sd.InputStream(
            samplerate=self.sample_rate,
            channels=CHANNELS,
            dtype=DTYPE,
            blocksize=block_size,
            callback=self._audio_callback,
        ):
            while not self._stop_event.is_set():
                try:
                    chunk = self._audio_queue.get(timeout=0.1)
                    recorded_chunks.append(chunk)
                    total_samples += len(chunk)

                    # Check for silence
                    rms = self._calculate_rms(chunk)
                    if rms < self.silence_threshold:
                        silence_samples += len(chunk)
                    else:
                        silence_samples = 0

                    # Stop if enough silence accumulated (but only after some audio recorded)
                    if silence_samples >= samples_for_silence and total_samples > samples_for_silence:
                        print("Silence detected, stopping.", file=sys.stderr)
                        break

                    # Stop if timeout reached
                    if total_samples >= max_samples:
                        print("Timeout reached, stopping.", file=sys.stderr)
                        break

                except queue.Empty:
                    continue

        # Play beep to indicate recording ended
        play_beep(BEEP_FREQ_END)

        if not recorded_chunks:
            return np.array([], dtype=DTYPE)

        # Concatenate all chunks and flatten to 1D
        audio = np.concatenate(recorded_chunks).flatten()
        return audio
