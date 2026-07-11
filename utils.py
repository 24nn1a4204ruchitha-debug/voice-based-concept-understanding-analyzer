"""
utils.py
--------
Shared helper functions: file I/O, directory setup, and reference concept
loading.
"""

import os
import json
import uuid


def ensure_directories(dirs):
    for d in dirs:
        os.makedirs(d, exist_ok=True)


def load_reference_concepts(json_path: str) -> dict:
    """Load the predefined concept -> reference definition mapping."""
    with open(json_path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_uploaded_file(uploaded_file, upload_dir: str = "uploads") -> str:
    """
    Save a Streamlit UploadedFile object to disk and return its path.
    A UUID prefix avoids filename collisions between concurrent users.
    """
    os.makedirs(upload_dir, exist_ok=True)
    ext = os.path.splitext(uploaded_file.name)[1] or ".wav"
    filename = f"{uuid.uuid4().hex}{ext}"
    path = os.path.join(upload_dir, filename)

    with open(path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    return path
