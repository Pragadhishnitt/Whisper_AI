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

Put your five files in `inputs/1.mp3 ... 5.mp3` (or edit `config.py`).

## Run
```bash
python stage1_transcribe_annotate.py
python stage2_truth_extractor.py
```

Outputs land in `outputs/`.
