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
    with open(os.path.join(OUTPUT_DIR, "sessions.json"), "r", encoding="utf-8") as f:
        return json.load(f)

def load_clean_sessions_text() -> Dict[str, str]:
    sessions_text = {}
    for i in range(1, 6):
        p = os.path.join(OUTPUT_DIR, f"session_{i}.txt")
        if os.path.exists(p):
            with open(p, "r", encoding="utf-8") as f:
                _ = f.readline()  # "Session i"
                sessions_text[str(i)] = f.read().strip()
    return sessions_text

# -------- LLM Setup -------- (will include groq in future)

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

NO extra text. JSON only."""),
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

# -------- LangGraph state & nodes --------
class State(dict): pass

def build_state(clean_texts: Dict[str,str], annotated: Dict[str, List[Dict[str,Any]]]) -> State:
    annotated_str = json.dumps(annotated, ensure_ascii=False, indent=2)
    return State({
        "shadow_id": "shadow_candidate_1",
        "s1": clean_texts.get("1",""),
        "s2": clean_texts.get("2",""),
        "s3": clean_texts.get("3",""),
        "s4": clean_texts.get("4",""),
        "s5": clean_texts.get("5",""),
        "annotated_json": annotated_str
    })

def llm_node(state: State) -> State:
    chain = prompt | llm
    resp = chain.invoke(state)
    return State({"raw": resp.content})

def validate_node(state: State) -> State:
    raw = state["raw"]
    data = json.loads(raw)
    tw = TruthWeaverOutput.model_validate(data)
    canonical = tw.model_dump(by_alias=True, indent=2)
    return State({"json": json.dumps(canonical, ensure_ascii=False, indent=2)})

graph = StateGraph(State)
graph.add_node("llm", llm_node)
graph.add_node("validate", validate_node)
graph.set_entry_point("llm")
graph.add_edge("llm", "validate")
truth_flow = graph.compile()

def main():
    annotated = load_sessions()
    clean = load_clean_sessions_text()
    state = build_state(clean, annotated)
    out = truth_flow.invoke(state)
    final_json = out["json"]
    out_path = os.path.join(OUTPUT_DIR, "truth.json")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(final_json)
    print("\n[Stage2] Wrote:", out_path)
    print(final_json)

if __name__ == "__main__":
    main()
