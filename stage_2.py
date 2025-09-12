# stage2_truth_extractor.py
import os
import json
from typing import List, Dict, Any
from pydantic import BaseModel, Field
from langgraph.graph import StateGraph
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from config import OUTPUT_DIR
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

import re, json

def extract_json(text: str) -> dict:
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        raise ValueError("No JSON object found in LLM output")
    try:
        return json.loads(match.group(0))
    except json.JSONDecodeError as e:
        print("LLM RAW OUTPUT (first 300):", text[:300])
        raise ValueError(f"JSON decoding failed: {e}")


# -------- Pydantic schema (exact competition format) --------
class RevealedTruth(BaseModel):
    programming_experience: str
    programming_language: str
    skill_mastery: str
    leadership_claims: str
    team_experience: str
    skills_and_other_keywords: List[str] = Field(alias="skills and other keywords")

class DeceptionPattern(BaseModel):
    lie_type: str
    contradictory_claims: List[str]

class TruthWeaverOutput(BaseModel):
    shadow_id: str
    revealed_truth: RevealedTruth
    deception_patterns: List[DeceptionPattern]

# -------- Load sessions.json --------
def load_sessions() -> Dict[str, List[Dict[str, Any]]]:
    sessions_path = os.path.join(OUTPUT_DIR, "sessions.json")
    if not os.path.exists(sessions_path):
        raise FileNotFoundError(f"sessions.json not found at {sessions_path}")
    
    with open(sessions_path, "r", encoding="utf-8") as f:
        return json.load(f)

def load_clean_sessions_text() -> Dict[str, str]:
    sessions_text = {}
    for i in range(1, 6):
        p = os.path.join(OUTPUT_DIR, f"session_{i}.txt")
        if os.path.exists(p):
            with open(p, "r", encoding="utf-8") as f:
                _ = f.readline()  # Skip "Session i" header
                sessions_text[str(i)] = f.read().strip()
        else:
            print(f"Warning: session_{i}.txt not found at {p}")
            sessions_text[str(i)] = ""
    return sessions_text

# -------- LLM Setup --------
llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash-exp", google_api_key=api_key)
prompt = ChatPromptTemplate.from_messages([
    ("system", """You are an AI Truth Extractor for technical interviews.
You will receive 5 sessions of transcripts (clean text) and segment-level annotations (emotion + RMS).
Your goals:
1) Detect contradictions across sessions.
2) Infer the most plausible truth (later sessions can be more truthful).
3) Output STRICT JSON only with this schema:

{{
  "shadow_id": "string",
  "revealed_truth": {{
    "programming_experience": "string",
    "programming_language": "string",
    "skill_mastery": "string",
    "leadership_claims": "string",
    "team_experience": "string",
    "skills and other keywords": ["list"]
  }},
  "deception_patterns": [{{
    "lie_type": "string",
    "contradictory_claims": ["list of claims"]
  }}]
}}

NO extra text. JSON only.

### Example Input
The Five Sessions (audio quality varies):
• Session 1 (clear audio): "I've mastered Python for 6 years... built incredible systems..."
• Session 2 (static interference): "Actually... crackle... maybe 3 years? Still learning advanced... bzzt"
• Session 3 (shouting over noise): "LED A TEAM OF FIVE! EIGHT MONTHS! MACHINE LEARNING!"
• Session 4 (whispered): "I... I work alone mostly... never been comfortable with... with people..."
• Session 5 (emotional breakdown): "*sobbing* Just 2 months debugging... I'm not... I'm not what they think..."

### Example Output
{{
  "shadow_id": "phoenix_2024",
  "revealed_truth": {{
    "programming_experience": "3-4 years",
    "programming_language": "python",
    "skill_mastery": "intermediate",
    "leadership_claims": "fabricated",
    "team_experience": "individual contributor",
    "skills and other keywords": ["Machine Learning"]
  }},
  "deception_patterns": [
    {{
      "lie_type": "experience_inflation",
      "contradictory_claims": ["6 years", "3 years"]
    }}
  ]
}}
"""),
    ("human", """Shadow ID: {shadow_id}

CLEAN SESSIONS (for edit distance reference; do NOT modify for scoring):
Session 1: {s1}
Session 2: {s2}
Session 3: {s3}
Session 4: {s4}
Session 5: {s5}

ANNOTATED SEGMENTS (guide for emotions; use for reasoning):
{annotated_json}

Return ONLY the JSON in the required schema.""")
])


# -------- Fixed LangGraph state & nodes --------
class TruthExtractorState(BaseModel):
    shadow_id: str = ""
    s1: str = ""
    s2: str = ""
    s3: str = ""
    s4: str = ""
    s5: str = ""
    annotated_json: str = ""
    raw: str = ""
    json: str = ""

def llm_node(state: TruthExtractorState) -> Dict[str, Any]:
    try:
        chain = prompt | llm
        # Convert state to dict for the prompt
        state_dict = {
            "shadow_id": state.shadow_id,
            "s1": state.s1,
            "s2": state.s2,
            "s3": state.s3,
            "s4": state.s4,
            "s5": state.s5,
            "annotated_json": state.annotated_json
        }
        
        print(f"DEBUG: Sending prompt with state keys: {list(state_dict.keys())}")
        print(f"DEBUG: State s1 length: {len(state_dict['s1'])}")
        
        resp = chain.invoke(state_dict)
        
        print(f"DEBUG: LLM response type: {type(resp.content)}")
        print(f"DEBUG: LLM response length: {len(resp.content) if resp.content else 0}")
        print(f"DEBUG: LLM response preview: {repr(resp.content[:100]) if resp.content else 'None'}")
        
        return {"raw": resp.content}
    except Exception as e:
        print(f"Error in LLM node: {e}")
        raise

def validate_node(state: TruthExtractorState) -> Dict[str, Any]:
    try:
        raw = state.raw
        if raw.startswith("```"):
            raw = raw.strip("`").replace("json","")
        print("\n")
        print(type(raw))
        print("\n")
        data = json.loads(raw)
        print("\n")
        print(type(data))
        print("\n")
        tw = TruthWeaverOutput.model_validate(data)  
        canonical = tw.model_dump(by_alias=True)
        return {"json": json.dumps(canonical, ensure_ascii=False, indent=2)}
    except json.JSONDecodeError as e:
        print(f"JSON decode error: {e}")
        print(f"Raw response: {raw}")
        raise
    except Exception as e:
        print(f"Validation error: {e}")
        print(f"Raw response: {raw}")
        raise

# Build the graph
graph = StateGraph(TruthExtractorState)
graph.add_node("llm", llm_node)
graph.add_node("validate", validate_node)
graph.set_entry_point("llm")
graph.add_edge("llm", "validate")
truth_flow = graph.compile()

def check_required_files():
    """Check if all required input files exist"""
    required_files = [
        "sessions.json",
        "session_1.txt",
        "session_2.txt", 
        "session_3.txt",
        "session_4.txt",
        "session_5.txt"
    ]
    
    missing_files = []
    for file in required_files:
        file_path = os.path.join(OUTPUT_DIR, file)
        if not os.path.exists(file_path):
            missing_files.append(file)
    
    if missing_files:
        print("Missing required files:")
        for file in missing_files:
            print(f"  - {file}")
        return False
    
    print("All required files found!")
    return True

def main():
    print(f"Output directory: {OUTPUT_DIR}")
    
    # Check if required files exist
    if not check_required_files():
        print("\nPlease ensure all required files are present before running stage 2.")
        return
    
    try:
        # Load data
        annotated = load_sessions()
        clean = load_clean_sessions_text()
        
        # Build initial state
        annotated_str = json.dumps(annotated, ensure_ascii=False, indent=2)
        initial_state = TruthExtractorState(
            shadow_id="shadow_candidate_1",
            s1=clean.get("1", ""),
            s2=clean.get("2", ""),
            s3=clean.get("3", ""),
            s4=clean.get("4", ""),
            s5=clean.get("5", ""),
            annotated_json=annotated_str
        )
        
        # Run the graph
        print("\nRunning truth extraction...")
        result = truth_flow.invoke(initial_state)
        
        # Save output
        final_json = result["json"]

        print(f'\n\nResult\n{result}\n\n')
        out_path = os.path.join(OUTPUT_DIR, "truth.json")
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(final_json)
        
        print(f"\n[Stage2] Successfully wrote: {out_path}")
        print("\nGenerated truth.json:")
        print(final_json)
        
    except Exception as e:
        print(f"\nError during execution: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()