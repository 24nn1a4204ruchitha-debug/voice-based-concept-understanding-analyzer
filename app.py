"""
Voice-Based Concept Understanding Analyser (VBCUA)
====================================================
An AI-powered web application to evaluate how effectively users understand
and explain conceptual topics through spoken communication.

Run with:
    streamlit run app.py
"""

import os
import json
import datetime

import streamlit as st

from modules.transcription import transcribe_audio
from modules.semantic_analysis import compute_semantic_similarity, classify_understanding
from modules.audio_features import extract_audio_features, plot_waveform
from modules.scoring import compute_overall_score, generate_feedback
from modules.report_generator import generate_pdf_report
from modules.utils import (
    load_reference_concepts,
    save_uploaded_file,
    ensure_directories,
)

# --------------------------------------------------------------------------
# App configuration
# --------------------------------------------------------------------------
st.set_page_config(
    page_title="VBCUA - Voice-Based Concept Understanding Analyser",
    page_icon="🎙️",
    layout="wide",
)

ensure_directories(["uploads", "reports"])

REFERENCE_CONCEPTS = load_reference_concepts("data/reference_concepts.json")

# --------------------------------------------------------------------------
# Sidebar
# --------------------------------------------------------------------------
st.sidebar.title("🎙️ VBCUA")
st.sidebar.caption("Voice-Based Concept Understanding Analyser")

mode = st.sidebar.radio(
    "Choose Analysis Scenario",
    [
        "Scenario 1: Concept Understanding",
        "Scenario 2: Speech Fluency Analysis",
    ],
)

st.sidebar.markdown("---")
st.sidebar.markdown(
    """
    **About**

    VBCUA combines speech-to-text transcription, semantic similarity
    analysis, audio feature extraction, and intelligent scoring to assess
    conceptual understanding and speech delivery fluency.

    Built with **Streamlit**, **OpenAI Whisper**, and **Sentence-BERT**.
    """
)

# --------------------------------------------------------------------------
# Header
# --------------------------------------------------------------------------
st.title("Voice-Based Concept Understanding Analyser")
st.write(
    "Upload a spoken explanation and get an automated evaluation of "
    "conceptual understanding and/or speech fluency."
)

# ==========================================================================
# SCENARIO 1: Semantic Understanding and Concept Evaluation
# ==========================================================================
if mode.startswith("Scenario 1"):
    st.header("📘 Scenario 1: Semantic Understanding & Concept Evaluation")

    col1, col2 = st.columns([1, 1])

    with col1:
        concept_names = list(REFERENCE_CONCEPTS.keys())
        selected_concept = st.selectbox("Select a concept to explain", concept_names)
        st.info(f"**Reference definition:**\n\n{REFERENCE_CONCEPTS[selected_concept]}")

    with col2:
        audio_file = st.file_uploader(
            "Upload your spoken explanation (wav/mp3/m4a)",
            type=["wav", "mp3", "m4a"],
            key="concept_audio",
        )

    student_name = st.text_input("Student / User name (optional)", value="Anonymous")

    if audio_file is not None:
        st.audio(audio_file)

        if st.button("🔍 Analyze Explanation", type="primary"):
            with st.spinner("Saving audio..."):
                audio_path = save_uploaded_file(audio_file, "uploads")

            with st.spinner("Transcribing speech (Whisper)..."):
                transcript, transcript_segments = transcribe_audio(audio_path)

            with st.spinner("Extracting audio features..."):
                audio_features = extract_audio_features(audio_path, transcript_segments)

            with st.spinner("Computing semantic similarity (Sentence-BERT)..."):
                similarity_score = compute_semantic_similarity(
                    transcript, REFERENCE_CONCEPTS[selected_concept]
                )
                understanding_label = classify_understanding(similarity_score)

            overall_score, breakdown = compute_overall_score(
                similarity_score=similarity_score,
                fluency_metrics=audio_features,
                mode="understanding",
            )
            feedback = generate_feedback(
                mode="understanding",
                similarity_score=similarity_score,
                understanding_label=understanding_label,
                fluency_metrics=audio_features,
            )

            st.success("Analysis complete!")

            # ---- Results ----
            st.subheader("📝 Transcript")
            st.write(transcript if transcript else "_No speech detected._")

            m1, m2, m3 = st.columns(3)
            m1.metric("Semantic Similarity", f"{similarity_score * 100:.1f}%")
            m2.metric("Understanding Level", understanding_label)
            m3.metric("Overall Score", f"{overall_score:.1f} / 100")

            st.subheader("🔊 Waveform")
            fig = plot_waveform(audio_path)
            st.pyplot(fig)

            st.subheader("📊 Score Breakdown")
            st.json(breakdown)

            st.subheader("💡 Feedback")
            for line in feedback:
                st.write(f"- {line}")

            report_data = {
                "type": "Concept Understanding Evaluation",
                "student_name": student_name,
                "concept": selected_concept,
                "reference_text": REFERENCE_CONCEPTS[selected_concept],
                "transcript": transcript,
                "similarity_score": similarity_score,
                "understanding_label": understanding_label,
                "overall_score": overall_score,
                "breakdown": breakdown,
                "audio_features": audio_features,
                "feedback": feedback,
                "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }

            pdf_path = generate_pdf_report(report_data, "reports")
            with open(pdf_path, "rb") as f:
                st.download_button(
                    "⬇️ Download PDF Report",
                    data=f,
                    file_name=os.path.basename(pdf_path),
                    mime="application/pdf",
                )

# ==========================================================================
# SCENARIO 2: Speech Fluency and Communication Analysis
# ==========================================================================
else:
    st.header("🗣️ Scenario 2: Speech Fluency & Communication Analysis")

    audio_file = st.file_uploader(
        "Upload a spoken explanation / interview / presentation clip",
        type=["wav", "mp3", "m4a"],
        key="fluency_audio",
    )
    student_name = st.text_input("Speaker name (optional)", value="Anonymous")

    if audio_file is not None:
        st.audio(audio_file)

        if st.button("🔍 Analyze Fluency", type="primary"):
            with st.spinner("Saving audio..."):
                audio_path = save_uploaded_file(audio_file, "uploads")

            with st.spinner("Transcribing speech (Whisper)..."):
                transcript, transcript_segments = transcribe_audio(audio_path)

            with st.spinner("Extracting fluency & audio features..."):
                audio_features = extract_audio_features(audio_path, transcript_segments)

            overall_score, breakdown = compute_overall_score(
                similarity_score=None,
                fluency_metrics=audio_features,
                mode="fluency",
            )
            feedback = generate_feedback(
                mode="fluency",
                similarity_score=None,
                understanding_label=None,
                fluency_metrics=audio_features,
            )

            st.success("Analysis complete!")

            st.subheader("📝 Transcript")
            st.write(transcript if transcript else "_No speech detected._")

            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Filler Words", audio_features["filler_word_count"])
            m2.metric("Pause Ratio", f"{audio_features['pause_ratio'] * 100:.1f}%")
            m3.metric("Speech Rate (wpm)", f"{audio_features['words_per_minute']:.0f}")
            m4.metric("Fluency Score", f"{overall_score:.1f} / 100")

            st.subheader("🔊 Waveform")
            fig = plot_waveform(audio_path)
            st.pyplot(fig)

            st.subheader("📊 Score Breakdown")
            st.json(breakdown)

            st.subheader("💡 Feedback")
            for line in feedback:
                st.write(f"- {line}")

            report_data = {
                "type": "Speech Fluency & Communication Analysis",
                "student_name": student_name,
                "transcript": transcript,
                "overall_score": overall_score,
                "breakdown": breakdown,
                "audio_features": audio_features,
                "feedback": feedback,
                "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }

            pdf_path = generate_pdf_report(report_data, "reports")
            with open(pdf_path, "rb") as f:
                st.download_button(
                    "⬇️ Download PDF Report",
                    data=f,
                    file_name=os.path.basename(pdf_path),
                    mime="application/pdf",
                )

st.markdown("---")
st.caption("VBCUA © 2026 — Built with Streamlit, Whisper & Sentence-BERT")
