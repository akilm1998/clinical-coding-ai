"""
Test-only driver for the coding pipeline.

It reproduces the orchestration in src/main.py WITHOUT modifying main.py: it puts
src/ on sys.path, imports the same functions main.py uses, and runs them in the
same order — minus the debug-artifact file writes and prints. Used by the live
test tier.

If the sequence in main.py changes, update run_pipeline() to match.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

TESTS_DIR = Path(__file__).resolve().parent
REPO = TESTS_DIR.parent
SRC = REPO / "src"
CASES_DIR = REPO / "regression_cases"

# Make the intra-src imports (`from functions import ...`, etc.) resolve, exactly
# as they do when main.py runs from src/.
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

_INFRA_PREFIXES = ("hospitalInformation", "practitionerInformation")


def resolve_patient_file(case_id: str) -> Path:
    """Return the single patient FHIR bundle for a case's generated output."""
    fhir = CASES_DIR / case_id / "generated" / "fhir"
    if not fhir.is_dir():
        raise FileNotFoundError(f"no generated/fhir dir for {case_id}: {fhir}")
    candidates = [p for p in sorted(fhir.glob("*.json")) if not p.name.startswith(_INFRA_PREFIXES)]
    if len(candidates) != 1:
        raise RuntimeError(
            f"expected exactly one patient bundle in {fhir}, found {[p.name for p in candidates]}"
        )
    return candidates[0]


def _parse_json(text: str):
    """Parse LLM output that should be JSON; tolerate stray ```json fences."""
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```[a-zA-Z]*\n?", "", text)
        text = re.sub(r"\n?```$", "", text).strip()
    return json.loads(text)


def make_client():
    """Build an OpenAI client from .env, the same way main.py does."""
    import os

    from dotenv import load_dotenv
    from openai import OpenAI

    load_dotenv(REPO / ".env")
    return OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def run_pipeline(patient_data_file, client=None) -> dict:
    """Run the full pipeline for one patient bundle and return the parsed LLM #2
    decision dict ({selected_codes, additional_codes, rejected_candidates}).

    Mirrors src/main.py step for step. Makes real OpenAI calls and live
    icd10data.com requests — the caller supplies/holds the API key.
    """
    from functions import (
        build_coding_context,
        expand_non_billable_codes,
        get_data,
        prepare_coding_context,
    )
    from prompt import generate_clinical_conditions, generate_coding_decision
    from text_to_icd10 import text_to_icd10

    if client is None:
        client = make_client()

    data = get_data(str(patient_data_file))

    encounters = [
        entry["resource"]
        for entry in data.get("entry", [])
        if entry.get("resource", {}).get("resourceType") == "Encounter"
    ]
    latest_encounter = max(encounters, key=lambda enc: enc["period"]["start"])

    coding_context = build_coding_context(data, latest_encounter["id"])
    if not coding_context["patient"]["alive"]:
        raise SystemExit("Patient is deceased. Skipping coding pipeline.")

    clinical_conditions = generate_clinical_conditions(coding_context, client)  # LLM #1
    clinical_extraction = _parse_json(clinical_conditions)

    icd10_candidates = text_to_icd10(clinical_extraction)              # live scraping
    coding_candidates = expand_non_billable_codes(icd10_candidates["results"])  # live scraping
    prepared_icd_context = prepare_coding_context(list(coding_candidates.values()))

    coding_decision_context = {
        "clinical_context": coding_context,
        "clinical_extraction": clinical_extraction,
        "icd10_context": prepared_icd_context,
    }
    coding_decision = generate_coding_decision(coding_decision_context, client)  # LLM #2
    return _parse_json(coding_decision)
