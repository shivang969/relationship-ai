import json
import os
import sys
import datetime

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT_DIR)

DATA_DIR    = os.path.join(ROOT_DIR, "data")
OUTPUT_PATH = os.path.join(DATA_DIR, "pipeline_output.json")
DATA_PATH   = os.path.join(DATA_DIR, "chats.json")

from data.synthetic_generator import generate_dataset
from pipeline.features import load_data, extract_all_features
from pipeline.scoring import score_all
from pipeline.decision import run_decision_engine

def run_pipeline(use_ai=True):
    print("\n" + "="*55)
    print("  RELATIONSHIP INTELLIGENCE PIPELINE")
    print("="*55)

    # Step 1
    if not os.path.exists(DATA_PATH):
        print("\n[1/4] Generating synthetic chat data...")
        generate_dataset()
    else:
        print("\n[1/4] Loading existing chat data...")

    df, contacts_meta = load_data(DATA_PATH)
    print(f"      Loaded {len(df)} messages across {len(contacts_meta)} contacts")

    # Step 2
    print("\n[2/4] Extracting behavioral features...")
    features = extract_all_features(df, contacts_meta)
    print(f"      Extracted {len(features[0])} features per contact")

    # Step 3
    print("\n[3/4] Scoring relationships & detecting anomalies...")
    scored = score_all(features)
    for c in scored:
        flag = "🔴" if c["grade"] == "D" else "🟠" if c["grade"] == "C" else "🟡" if c["grade"] == "B" else "🟢"
        print(f"      {flag} {c['contact']:<22} Score: {c['health_score']:>3}/100  Grade: {c['grade']}  Issues: {len(c['anomalies'])}")

    # Step 4
    if use_ai:
        print("\n[4/4] Running AI Decision Engine (Claude)...")
        decisions = run_decision_engine(scored, top_n=6)
    else:
        print("\n[4/4] Skipping AI (--no-ai flag set)...")
        decisions = [{**c, "ai_decision": None} for c in scored]

    output = {
        "pipeline_run": datetime.datetime.now().isoformat(),
        "total_contacts": len(scored),
        "scored_contacts": scored,
        "ai_decisions": decisions,
        "summary": {
            "grade_A": sum(1 for c in scored if c["grade"] == "A"),
            "grade_B": sum(1 for c in scored if c["grade"] == "B"),
            "grade_C": sum(1 for c in scored if c["grade"] == "C"),
            "grade_D": sum(1 for c in scored if c["grade"] == "D"),
            "high_priority": sum(1 for c in scored if c["priority"] == "high"),
        }
    }

    with open(OUTPUT_PATH, "w") as f:
        json.dump(output, f, indent=2, default=str)

    print(f"\n✅ Pipeline complete! Output → {OUTPUT_PATH}")
    print(f"   Summary: {output['summary']}")
    print("="*55 + "\n")
    return output

if __name__ == "__main__":
    run_pipeline(use_ai="--no-ai" not in sys.argv)