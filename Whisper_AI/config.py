# config.py

WHISPER_BACKEND = "openai-whisper"   # or "faster-whisper"
WHISPER_MODEL = "turbo"              # try "large-v3" for best accuracy (needs more VRAM/CPU)

AUDIO_FILES = [
    "audio/buried_confession.mp3",
    "audio/drifted_anecdote.mp3",
    "audio/hedge_and_dodge.mp3",
    "audio/rehearsed_evasion.mp3",
    "audio/selfcorrect_contradictions.mp3",
]

OUTPUT_DIR = "outputs"
SER_MODEL_ID = "superb/hubert-large-superb-er"

# Heuristic thresholds
RMS_SHOUT = 0.020
RMS_WHISPER = 0.015
RMS_STATIC = 0.005
