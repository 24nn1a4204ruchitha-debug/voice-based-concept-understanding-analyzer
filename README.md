# 🎙️ VBCUA — Voice-Based Concept Understanding Analyser

VBCUA is an AI-powered web application that evaluates how effectively users
understand and explain conceptual topics through spoken communication. It
combines **speech-to-text transcription**, **semantic similarity analysis**,
**audio feature extraction**, and **intelligent scoring** to assess both
conceptual understanding and speech delivery fluency.

Built with **Streamlit** and **Python**, the app is modular, interactive, and
includes waveform visualization, automated evaluation, and downloadable PDF
reports — suitable for students, educators, trainers, and researchers.

---

## ✨ Features

- 🎤 **Speech-to-Text** — transcribes uploaded audio using OpenAI Whisper
- 🧠 **Semantic Similarity** — compares spoken explanations to reference
  concepts using Sentence-BERT embeddings
- 📈 **Audio Feature Extraction** — filler word count, pause ratio, speech
  rate (wpm), pitch, and energy statistics via Librosa
- 🎯 **Intelligent Scoring** — weighted scoring engine producing an overall
  0–100 score with a detailed breakdown
- 📊 **Waveform Visualization** — interactive waveform plots per recording
- 📄 **PDF Reports** — downloadable, structured evaluation reports
- 🧩 **Two Analysis Scenarios**:
  1. **Concept Understanding Evaluation** — semantic accuracy against a
     reference definition (e.g. "Machine Learning", "Cloud Computing")
  2. **Speech Fluency Analysis** — filler words, pauses, and pacing for
     interview/presentation practice

---

## 📁 Project Structure

```
VBCUA/
├── app.py                       # Main Streamlit application
├── requirements.txt             # Python dependencies
├── README.md
├── modules/
│   ├── __init__.py
│   ├── transcription.py         # Whisper speech-to-text
│   ├── semantic_analysis.py     # Sentence-BERT similarity scoring
│   ├── audio_features.py        # Fluency metrics + waveform plotting
│   ├── scoring.py                # Scoring engine & feedback generation
│   ├── report_generator.py      # PDF report builder (fpdf2)
│   └── utils.py                  # Shared helpers
├── data/
│   └── reference_concepts.json  # Predefined concept reference definitions
├── uploads/                      # Uploaded audio files (runtime, gitignored)
└── reports/                      # Generated PDF reports (runtime, gitignored)
```

---

## 🛠️ Setup

1. **Clone / unzip the project** and move into the directory:
   ```bash
   cd VBCUA
   ```

2. **Create a virtual environment** (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate   # On Windows: venv\Scripts\activate
   ```

3. **Install system dependency — FFmpeg** (required by Whisper):
   - macOS: `brew install ffmpeg`
   - Ubuntu/Debian: `sudo apt install ffmpeg`
   - Windows: download from https://ffmpeg.org and add to PATH

4. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

5. **Run the app**:
   ```bash
   streamlit run app.py
   ```

6. Open the local URL shown in the terminal (typically
   `http://localhost:8501`).

---

## 🧪 How It Works

1. User uploads a spoken audio explanation (wav/mp3/m4a).
2. **Whisper** transcribes the speech to text.
3. **Librosa** extracts fluency/audio features (filler words, pause ratio,
   speech rate, pitch, energy) from the audio + transcript segments.
4. **Sentence-BERT** computes semantic similarity between the transcript and
   a reference concept definition (Scenario 1 only).
5. The **scoring engine** blends these signals into an overall 0–100 score
   with a full breakdown and generates structured feedback.
6. Results are displayed in the UI (waveform, metrics, feedback) and can be
   exported as a **PDF report**.

---

## ⚙️ Customization

- **Add new concepts**: edit `data/reference_concepts.json` and add a new
  `"Concept Name": "Reference definition..."` entry.
- **Change Whisper model size**: edit `model_size` in
  `modules/transcription.py` (`tiny`, `base`, `small`, `medium`, `large`) —
  larger models are more accurate but slower.
- **Adjust scoring weights**: tune the weighting logic in
  `modules/scoring.py` (`compute_overall_score`).

---

## 📌 Notes

- First run will download the Whisper and Sentence-BERT models, which
  requires an internet connection and may take a few minutes.
- For best transcription accuracy, use clear audio with minimal background
  noise.

---

## 📄 License

This project is provided as a starter template for educational and
research purposes.
