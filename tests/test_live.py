"""
Live tier — actually RUNS the pipeline end-to-end and checks the result.

Opt-in (not run by default): `pytest -m live`
Requires: OPENAI_API_KEY (in the environment or the repo .env), network access to
OpenAI and icd10data.com, and the pipeline deps (openai, python-dotenv, requests,
beautifulsoup4). Each case makes 2 OpenAI calls + many scrapes, so it is slow and
costs money — that's why it's separate from the fast checker tier.

Refresh the checker baseline from a live run:
    REFRESH_OUTPUTS=1 pytest -m live
This overwrites tests/outputs/<case_id>.json with the fresh decisions, so a later
plain `pytest` compares the current pipeline's behavior against the ground truth.
"""
from __future__ import annotations

import json
import os
from pathlib import Path

import pytest
import yaml

from conftest import assert_case, codes_from_decision

TESTS_DIR = Path(__file__).resolve().parent
OUTPUTS_DIR = TESTS_DIR / "outputs"
_EXPECTED = yaml.safe_load((TESTS_DIR / "expected_codes.yaml").read_text(encoding="utf-8"))
CASE_IDS = sorted(_EXPECTED.keys())

# Load .env so a key stored only there still enables the live run.
try:
    from dotenv import load_dotenv

    load_dotenv(TESTS_DIR.parent / ".env")
except Exception:
    pass

REFRESH = os.getenv("REFRESH_OUTPUTS") == "1"


@pytest.mark.live
@pytest.mark.parametrize("case_id", CASE_IDS)
def test_live_pipeline(case_id, expected):
    if not os.getenv("OPENAI_API_KEY"):
        pytest.skip("OPENAI_API_KEY not set (needed for the live pipeline run)")

    # Imported lazily so the checker tier never needs the pipeline deps installed.
    from pipeline_runner import resolve_patient_file, run_pipeline

    decision = run_pipeline(resolve_patient_file(case_id))

    if REFRESH:
        OUTPUTS_DIR.mkdir(exist_ok=True)
        (OUTPUTS_DIR / f"{case_id}.json").write_text(
            json.dumps(decision, indent=2) + "\n", encoding="utf-8"
        )

    assert_case(case_id, expected[case_id], codes_from_decision(decision))
