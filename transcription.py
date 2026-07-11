"""
transcription.py
-----------------
Handles speech-to-text transcription using OpenAI Whisper.

Whisper is loaded lazily (only when first needed) and cached so that the
model is not reloaded on every Streamlit rerun.
"""

from functools import lru_cache
from typing import List, Tuple, Dict

import streamlit as st


@st.cache_resource(show_spinner=False)
def _load_whisper_model(model_size: str = "base"):
    """
    Load and cache the Whisper model.

    model_size options: tiny, base, small, medium, large
    'base' is a good default trade-off between speed and accuracy.
    """
    import whisper  # imported lazily to keep app import time low

    model = whisper.load_model(model_size)
    return model


def transcribe_audio(audio_path: str, model_size: str = "base") -> Tuple[str, List[Dict]]:
    """
    Transcribe an audio file into text.

    Parameters
    ----------
    audio_path : str
        Path to the audio file (wav/mp3/m4a).
    model_size : str
        Whisper model size to use.

    Returns
    -------
    transcript : str
        Full transcribed text.
    segments : list[dict]
        Whisper segment-level output, each containing 'start', 'end',
        'text', and word-level timing info if available. Used downstream
        for pause-ratio and speech-rate calculations.
    """
    model = _load_whisper_model(model_size)
    result = model.transcribe(audio_path, verbose=False)

    transcript = result.get("text", "").strip()
    segments = result.get("segments", [])

    return transcript, segments
