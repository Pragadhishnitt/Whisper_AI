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
Whisper_AI/
│
├── inputs/                  # Place your 5 audio files here (__1.mp3 ... __5.mp3)
│   └── audio.zip           # Compressed audio files for easy distribution
├── final_outputs/           # Final results directory
│   ├── truth.json          # Combined json (Competition submission file 2)
│   └── transcript.txt      # Combined transcript (Competition submission file 1)
├── outputs/                 # Generated outputs (Stage 1 + Stage 2)
│   ├── session_1.txt
│   ├── session_1_annotated.txt
│   ├── sessions.json
│   └── ...
│
├── config.py                # Configuration (models, thresholds, file paths)
├── utils_audio.py           # Emotion classifier + feature extraction
├── stage_1.py
├── stage_2.py
├── pipeline.sh              # Complete pipeline runner - Linux/Mac
├── run_all.bat             # Complete pipeline runner - Windows
├── requirements.txt
└── README.md
```

---

## 🚀 Choose Your Platform

Select your operating system or preferred environment:

### [🪟 Windows Setup](#-windows)
### [🐧 Ubuntu/Linux Setup](#-ubuntulinux)  
### [☁️ Google Colab Setup](#️-google-colab-recommended-for-8gb-ram-systems)

---

## 🪟 **Windows**

1. **Clone the repository**
   ```cmd
   git clone https://github.com/Pragadhishnitt/Whisper_AI
   cd Whisper_AI
   ```

2. **Create virtual environment**
   ```cmd
   python -m venv .venv
   .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```cmd
   pip install -r requirements.txt
   ```

4. **Install ffmpeg**
   - Download from: https://ffmpeg.org/download.html
   - Or use Chocolatey: `choco install ffmpeg`

5. **Prepare audio files**
   - Extract `audio.zip` 

6. **Run complete pipeline**
   ```cmd
   run_all.bat
   ```

7. **Check results**
   ```cmd
   dir final_outputs
   ```
   - `truth.json` - Competition submission file
   - `transcript.txt` - Combined transcript

---

## 🐧 **Ubuntu/Linux**

1. **Clone the repository**
   ```bash
   git clone https://github.com/Pragadhishnitt/Whisper_AI
   cd Whisper_AI
   ```

2. **Create virtual environment**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Install system dependencies**
   ```bash
   sudo apt update && sudo apt install ffmpeg
   ```

4. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Prepare audio files**
   ```bash
   unzip audio.zip  # If using the provided zip file
   ```

6. **Run complete pipeline**
   ```bash
   chmod +x pipeline.sh
   ./pipeline.sh
   ```

7. **Check results**
   ```bash
   ls final_outputs/
   ```
   - `truth.json` - Competition submission file
   - `transcript.txt` - Combined transcript

---

## ☁️ **Google Colab (Recommended for 8GB RAM systems)**

**⚠️ Important**: Enable GPU runtime in Colab for optimal performance.


```bash
chmod +x pipeline.sh # inculde this line for Linux/Mac
./pipeline.sh

#### Setup and Run

```python
# Enable GPU Runtime: Runtime → Change Runtime Type → Hardware Accelerator → GPU (T4)

# Clone repository
!git clone https://github.com/Pragadhishnitt/Whisper_AI
%cd Whisper_AI

# Install system dependencies
!apt update && apt install -y ffmpeg

# Install Python dependencies
!pip install -r requirements.txt

# Setup API key using Colab Secrets (🔑 icon in sidebar)
# Key name: GOOGLE_API_KEY
from google.colab import userdata
import os
os.environ['GOOGLE_API_KEY'] = userdata.get('GOOGLE_API_KEY')

# Extract audio files
!cd inputs && unzip -o audio.zip

# Run complete pipeline
!chmod +x pipeline.sh
!./pipeline.sh

# Check results
!ls final_outputs/

# Download results
from google.colab import files
files.download('final_outputs/truth.json')
files.download('final_outputs/transcript.txt')


---

## 🎙️ Audio Input Requirements

- **Naming**: Files should be named `__1.mp3`, `__2.mp3`, `__3.mp3`, `__4.mp3`, `__5.mp3`
- **Format**: MP3, WAV, M4A, or other common audio formats

---

## 📄 Results

After successful execution, check the `final_outputs/` directory for:

- **`truth.json`** - Final competition submission file
- **`transcript.txt`** - Combined transcript of all sessions

### Sample `truth.json` Output:
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

Modify `config.py` to adjust:
- `WHISPER_MODEL` → `"turbo"` (fast) or `"large-v3"` (most accurate)
- `WHISPER_BACKEND` → `"openai-whisper"` or `"faster-whisper"`
- `SER_MODEL_ID` → HuggingFace emotion model
- Audio thresholds → `RMS_SHOUT`, `RMS_WHISPER`, `RMS_STATIC`

---

## 🚨 Troubleshooting

**Out of Memory (8GB RAM)** → Use Google Colab with GPU

**Permission Denied (Linux/Mac)** → `chmod +x pipeline.sh`

**FFmpeg Not Found** → Install ffmpeg for your platform

**API Key Issues** → Ensure `GOOGLE_API_KEY` is properly set

**Audio File Issues** → Check naming: `__1.mp3`, `__2.mp3`, etc.

---

## 🏆 Competition Submission

The `truth.json` file in the `final_outputs/` directory is ready for competition submission.
