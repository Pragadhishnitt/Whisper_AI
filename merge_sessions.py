import os
import glob
from collections import defaultdict

OUTPUT_DIR = "outputs"
FINAL_OUTPUT_DIR = "final_outputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(FINAL_OUTPUT_DIR, exist_ok=True)

# Find all .txt files but exclude annotated ones
session_files = sorted(
    f for f in glob.glob(os.path.join(OUTPUT_DIR, "*.txt"))
    if "annotated" not in os.path.basename(f)
)

# Group by subject+year
grouped = defaultdict(list)

for file in session_files:
    filename = os.path.splitext(os.path.basename(file))[0]  # e.g. atlas_2025_1
    parts = filename.split("_")  # ["atlas", "2025", "1"]
    subject = parts[0].capitalize()
    year = parts[1]
    session_num = parts[2]

    with open(file, "r", encoding="utf-8") as infile:
        lines = infile.readlines()
        text = "".join(lines[1:]).strip()  # skip first line (header)
    
    grouped[f"{subject} {year}"].append((int(session_num), text))

# Output file path
merged_file = os.path.join(FINAL_OUTPUT_DIR, "transcript.txt")

with open(merged_file, "w", encoding="utf-8") as outfile:
    for subj_year, sessions in grouped.items():
        outfile.write(f"Subject: {subj_year}\n\n")
        for session_num, text in sorted(sessions):
            outfile.write(f"• Session {session_num}: \"{text}\"\n")
        outfile.write("\n")

print(f"Final transcript written to {merged_file}")
