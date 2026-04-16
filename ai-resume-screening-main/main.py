# ============================================================
# main.py — AI Resume Screening System
# Runs the full LCEL pipeline for 3 candidates, saves JSON
# results, and includes a debug re-run for LangSmith analysis.
# ============================================================

import json
import os
import sys

from dotenv import load_dotenv
load_dotenv()

from config import validate_config, OPENAI_MODEL, OPENAI_TEMPERATURE
from chains.screening_chain import ResumeScreeningChain


# ── Helpers ──────────────────────────────────────────────────

def load_file(filepath: str) -> str:
    """Read a text file or exit with an error."""
    try:
        with open(filepath, "r", encoding="utf-8") as fh:
            content = fh.read()
        print(f"  ✅ Loaded: {filepath}")
        return content
    except FileNotFoundError:
        print(f"  ❌ File not found: {filepath}")
        sys.exit(1)


def save_results(results: dict, output_dir: str = "outputs") -> None:
    """Persist pipeline results as a JSON file."""
    os.makedirs(output_dir, exist_ok=True)
    name_slug = results["candidate_name"].replace(" ", "_")
    filepath = os.path.join(output_dir, f"result_{name_slug}.json")

    with open(filepath, "w", encoding="utf-8") as fh:
        json.dump(results, fh, indent=2, ensure_ascii=False)
    print(f"  💾 Saved → {filepath}")


def print_section(title: str) -> None:
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")


def display_results(results: dict) -> None:
    """Pretty-print pipeline results to the terminal."""
    name = results.get("candidate_name", "Unknown")
    print_section(f"RESULTS: {name}  [{results.get('candidate_type', '')}]")

    if results["status"] == "FAILED":
        print(f"\n❌ Pipeline FAILED — {results.get('error', 'unknown')}")
        return

    print("\n📄 STEP 1 — Extracted Information:")
    print("-" * 40)
    print(results.get("extracted_info", "N/A"))

    print("\n🔍 STEP 2 — Match Analysis:")
    print("-" * 40)
    print(results.get("match_analysis", "N/A"))

    print("\n📊 STEP 3 — Score & Explanation:")
    print("-" * 40)
    print(results.get("score_explanation", "N/A"))


# ── Main ─────────────────────────────────────────────────────

def main():
    print_section("AI RESUME SCREENING SYSTEM")
    print("  Powered by LangChain (LCEL) + OpenAI + LangSmith\n")

    # 1. Validate environment
    print_section("PHASE 1 — Configuration")
    if not validate_config():
        sys.exit(1)

    # 2. Load data files
    print_section("PHASE 2 — Loading Data")
    job_description = load_file("data/job_description.txt")
    resume_strong   = load_file("data/resume_strong.txt")
    resume_average  = load_file("data/resume_average.txt")
    resume_weak     = load_file("data/resume_weak.txt")
    print("\n✅ All files loaded.")

    # 3. Build the LCEL pipeline
    print_section("PHASE 3 — Building Pipeline")
    pipeline = ResumeScreeningChain(
        model_name=OPENAI_MODEL,
        temperature=OPENAI_TEMPERATURE,
    )

    # 4. Define candidates (with LangSmith tags)
    candidates = [
        {"name": "Priya Sharma",  "resume": resume_strong,  "type": "strong"},
        {"name": "Rahul Gupta",   "resume": resume_average, "type": "average"},
        {"name": "Amit Kumar",    "resume": resume_weak,    "type": "weak"},
    ]

    # 5. Run the pipeline for each candidate
    print_section("PHASE 4 — Running Pipeline")
    print(f"\n📋 Screening {len(candidates)} candidates …")
    for i, c in enumerate(candidates, 1):
        print(f"\n  {i}. {c['name']}  ({c['type']})")
    print("\n⏳ Starting … (each candidate ≈ 30-60 s)")
    print("📡 All steps are traced in LangSmith automatically.\n")

    all_results = []
    for i, c in enumerate(candidates, 1):
        results = pipeline.run_pipeline(
            resume_text=c["resume"],
            job_description=job_description,
            candidate_name=c["name"],
            candidate_type=c["type"],
        )
        all_results.append(results)
        display_results(results)
        save_results(results)

    # 6. Debug run — re-run the weak candidate with high temperature
    #    to deliberately produce a potentially incorrect / inconsistent
    #    output that can be compared in LangSmith.
    print_section("PHASE 5 — Debug Run (high temperature)")
    print("  Re-running weak candidate with temperature=0.9 for LangSmith debugging …\n")

    debug_pipeline = ResumeScreeningChain(
        model_name=OPENAI_MODEL,
        temperature=0.9,  # deliberately high for variation
    )
    debug_results = debug_pipeline.run_pipeline(
        resume_text=resume_weak,
        job_description=job_description,
        candidate_name="Amit Kumar (DEBUG)",
        candidate_type="debug",
    )
    display_results(debug_results)
    save_results(debug_results)

    # 7. Summary
    print_section("FINAL SUMMARY")
    successful = sum(1 for r in all_results if r["status"] == "SUCCESS")
    failed     = sum(1 for r in all_results if r["status"] == "FAILED")
    print(f"\n  Candidates screened : {len(all_results)}")
    print(f"  Successful          : {successful}")
    print(f"  Failed              : {failed}")
    print(f"\n  📁 Results saved in : outputs/")
    print(f"  🔗 LangSmith traces : https://smith.langchain.com")
    print(f"     Project          : ai-resume-screening")
    print(f"\n{'='*60}")
    print("  ✅ AI RESUME SCREENING COMPLETE")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()