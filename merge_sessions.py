import os
import glob

OUTPUT_DIR = "outputs"
FINAL_OUTPUT_DIR = "final_outputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(FINAL_OUTPUT_DIR, exist_ok=True)

# Find all .txt files but exclude annotated ones
session_files = sorted(
    f for f in glob.glob(os.path.join(OUTPUT_DIR, "*.txt"))
    if "annotated" not in os.path.basename(f)
)

# Output file path
merged_file = os.path.join(FINAL_OUTPUT_DIR, "transcribed.txt")

with open(merged_file, "w", encoding="utf-8") as outfile:
    for file in session_files:
        filename = os.path.splitext(os.path.basename(file))[0]
        with open(file, "r", encoding="utf-8") as infile:
            lines = infile.read().strip().splitlines()
            
            # Drop the first line if it matches the filename
            if lines and lines[0].strip() == filename:
                lines = lines[1:]
            
            text = "\n".join(lines).strip()
            outfile.write(f"{filename}:\n{text}\n\n")

print(f"Merged {len(session_files)} session files into {merged_file}")

