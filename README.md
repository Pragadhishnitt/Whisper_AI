
# Truth Weaver Pipeline (Two-Stage)

**Stage 1**: Transcribe 5 audio files -> clean transcripts (for edit distance) + annotated segments (emotion + RMS).  
**Stage 2**: Feed all sessions to Gemini via LangChain/LangGraph + validate with Pydantic -> `truth.json`.

## Setup
```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
export GOOGLE_API_KEY="YOUR_KEY" # Windows PS: $env:GOOGLE_API_KEY="YOUR_KEY"
```

Put your five files in `audio_inputs/1.mp3 ... 5.mp3` (or edit `config.py`).

## Run
```bash
python stage_1.py
python stage_2.py
```

Outputs land in `outputs/`.

# Truth Weaver Pipeline

This project is built for the **Eightfold AI Competition**.  
It implements a **two-stage pipeline** that processes candidate audio files to:

1. **Stage 1 – Transcription & Annotation**
   - Convert 5 audio testimonies into transcripts using **Whisper**.
   - Produce **clean transcripts** (for edit-distance evaluation).
   - Produce **annotated transcripts** with tags like `[shouting]`, `[whispered]`, `[sobbing]`, `[static interference]`.
   - Attach **emotion labels** (from a HuggingFace Speech Emotion Recognition model) and **RMS values** (volume features).
   - Save structured data into `sessions.json`.

2. **Stage 2 – Truth Extraction**
   - Feed the transcripts + annotations into **Gemini** (via LangChain + LangGraph).
   - Detect contradictions and infer the most plausible truth.
   - Validate output against a **Pydantic schema**.
   - Generate a **competition-ready JSON** (`truth.json`).

---

## 📂 Project Structure

```
truth_weaver_pipeline/
│
├── inputs/                  # Place your 5 audio files here (1.mp3 ... 5.mp3)
├── outputs/                 # Generated outputs (Stage 1 + Stage 2)
│   ├── session_1.txt
│   ├── session_1_annotated.txt
│   ├── sessions.json
│   ├── truth.json
│   └── ...
│
├── config.py                # Configuration (models, thresholds, file paths)
├── utils_audio.py           # Emotion classifier + feature extraction
├── stage_1.py
├── stage_2.py
├── pipeline.sh          # Bash runner (Stage 1 → Stage 2)
├── requirements.txt
└── README.md
```

---

## ⚙️ Setup

1. **Clone / open this repo**
   ```bash
   cd Whisper_AI
   ```

2. **Create virtual environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate        # Linux/Mac
   .venv\Scripts\activate           # Windows
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Install ffmpeg (needed for Whisper)**
   - Ubuntu/Debian:
     ```bash
     sudo apt update && sudo apt install ffmpeg
     ```
   - Mac (Homebrew):
     ```bash
     brew install ffmpeg
     ```
   - Windows (Chocolatey):
     ```powershell
     choco install ffmpeg
     ```

5. **Configure Gemini API Key**
  *Can set it up in a .env file as well*
   ```bash
   export GOOGLE_API_KEY="YOUR_KEY"    # Linux/Mac
   $env:GOOGLE_API_KEY="YOUR_KEY"      # Windows PowerShell
   ```

---

## 🎙️ Inputs

- Place your 5 audio files in the `inputs/` folder:
  ```
  audio_inputs/1.mp3
  audio_inputs/2.mp3
  audio_inputs/3.mp3
  audio_inputs/4.mp3
  audio_inputs/5.mp3
  ```

- By default, **Session N = Audio File N**.

---

## 🚀 Run the Pipeline

Use the provided bash script:

```bash
chmod +x pipeline.sh
./pipeline.sh
```

It will:

1. Run **Stage 1** (`stage_1.py`) → generate transcripts & annotations.
2. Run **Stage 2** (`stage_2.py`) → produce `truth.json`.

---

## 📄 Outputs

After running:

- `session_1.txt … session_5.txt`  
  → Clean transcripts (for edit-distance evaluation).  

- `session_1_annotated.txt …`  
  → Annotated transcripts (with `[tags]`, emotion, RMS).  

- `sessions.json`  
  → Machine-readable version of all transcripts with segment-level metadata.  

- `truth.json`  
  → Final structured JSON in required schema (for competition submission). Example:

```json
{
  "shadow_id": "shadow_candidate_1",
  "revealed_truth": {
    "programming_experience": "3-4 years",
    "programming_language": "python",
    "skill_mastery": "intermediate",
    "leadership_claims": "fabricated",
    "team_experience": "individual contributor",
    "skills and other keywords": ["Machine Learning"]
  },
  "deception_patterns": [
    {
      "lie_type": "experience_inflation",
      "contradictory_claims": ["6 years", "3 years"]
    }
  ]
}
```

---

## 🛠️ Configuration

Check `config.py` to adjust:
- `WHISPER_MODEL` → `"turbo"` (fast) or `"large-v3"` (most accurate).
- `WHISPER_BACKEND` → `"openai-whisper"` (GitHub/PyPI whisper) or `"faster-whisper"`.
- `SER_MODEL_ID` → HuggingFace emotion model (`superb/hubert-large-superb-er`).
- `RMS_SHOUT`, `RMS_WHISPER`, `RMS_STATIC` → thresholds for style tagging.

---

## 🔮 Future Plans

- Option to replace rule-based annotation with **LLM-based tagger**.  
- Also looking out for Audio Language Models to replace OpenAI's whisper model
- Batch pipeline runner with retries and JSON repair.  
- Convert into an **agentic AI system** (monitoring inputs folder, auto-execution, feedback loop).  

