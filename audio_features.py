"""
audio_features.py
------------------
Extracts fluency-related audio features from a recording:
- filler word usage ("um", "like", "uh", etc.)
- pause ratio (silence vs. speech duration)
- speech rate (words per minute)
- pitch / energy statistics
- waveform visualization
"""

import re
from typing import List, Dict

import numpy as np

FILLER_WORDS = {
    "um", "uh", "umm", "uhh", "like", "you know", "so", "actually",
    "basically", "literally", "right", "i mean", "kind of", "sort of",
}


def _count_filler_words(text: str) -> int:
    if not text:
        return 0
    text_lower = text.lower()
    count = 0
    for filler in FILLER_WORDS:
        count += len(re.findall(rf"\b{re.escape(filler)}\b", text_lower))
    return count


def _compute_pause_ratio(segments: List[Dict], total_duration: float) -> float:
    """
    Estimate the fraction of total duration that is silence/pauses,
    based on gaps between consecutive Whisper segments.
    """
    if not segments or total_duration <= 0:
        return 0.0

    speech_time = sum(max(0.0, seg["end"] - seg["start"]) for seg in segments)
    pause_time = max(0.0, total_duration - speech_time)
    return min(1.0, pause_time / total_duration)


def _compute_words_per_minute(text: str, total_duration: float) -> float:
    if not text or total_duration <= 0:
        return 0.0
    word_count = len(text.split())
    minutes = total_duration / 60.0
    return word_count / minutes if minutes > 0 else 0.0


def extract_audio_features(audio_path: str, segments: List[Dict]) -> Dict:
    """
    Extract a dictionary of fluency and acoustic features from the audio
    file and the Whisper transcription segments.
    """
    import librosa

    y, sr = librosa.load(audio_path, sr=None, mono=True)
    total_duration = librosa.get_duration(y=y, sr=sr)

    full_text = " ".join(seg.get("text", "") for seg in segments)

    filler_count = _count_filler_words(full_text)
    pause_ratio = _compute_pause_ratio(segments, total_duration)
    wpm = _compute_words_per_minute(full_text, total_duration)

    # Pitch (fundamental frequency) statistics via librosa's pyin
    try:
        f0, voiced_flag, _ = librosa.pyin(
            y, fmin=librosa.note_to_hz("C2"), fmax=librosa.note_to_hz("C7"), sr=sr
        )
        voiced_f0 = f0[~np.isnan(f0)] if f0 is not None else np.array([])
        pitch_mean = float(np.mean(voiced_f0)) if voiced_f0.size else 0.0
        pitch_std = float(np.std(voiced_f0)) if voiced_f0.size else 0.0
    except Exception:
        pitch_mean, pitch_std = 0.0, 0.0

    # RMS energy (loudness / expressiveness proxy)
    rms = librosa.feature.rms(y=y)[0]
    energy_mean = float(np.mean(rms))
    energy_std = float(np.std(rms))

    return {
        "duration_seconds": round(total_duration, 2),
        "filler_word_count": filler_count,
        "pause_ratio": round(pause_ratio, 4),
        "words_per_minute": round(wpm, 2),
        "pitch_mean_hz": round(pitch_mean, 2),
        "pitch_std_hz": round(pitch_std, 2),
        "energy_mean": round(energy_mean, 5),
        "energy_std": round(energy_std, 5),
    }


def plot_waveform(audio_path: str):
    """
    Generate a matplotlib waveform plot for the given audio file.
    Returns a matplotlib Figure suitable for st.pyplot().
    """
    import librosa
    import librosa.display
    import matplotlib.pyplot as plt

    y, sr = librosa.load(audio_path, sr=None, mono=True)

    fig, ax = plt.subplots(figsize=(10, 3))
    librosa.display.waveshow(y, sr=sr, ax=ax, color="#4C8BF5")
    ax.set_title("Audio Waveform")
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Amplitude")
    fig.tight_layout()

    return fig
