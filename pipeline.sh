#!/bin/bash
set -e  

echo "[Pipeline] Stage 1: Transcribing & annotating..."
python stage_1.py

echo "[Pipeline] Stage 1 complete. Outputs written to outputs/"

echo "[Pipeline] Stage 2: Truth extraction with Gemini..."
python stage_2.py

echo "[Pipeline] Stage 2 complete. Final JSON at outputs/truth.json"
