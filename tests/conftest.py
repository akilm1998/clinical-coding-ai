"""Shared fixtures/helpers for the coding regression suite (checker + live tiers)."""
from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml

TESTS_DIR = Path(__file__).resolve().parent
EXPECTED_FILE = TESTS_DIR / "expected_codes.yaml"
OUTPUTS_DIR = TESTS_DIR / "outputs"


def _norm(code) -> str:
    """Normalize an ICD-10 code for comparison (strip, upper, no inner spaces)."""
    return "".join(str(code).split()).upper()


@pytest.fixture(scope="session")
def expected() -> dict:
    with EXPECTED_FILE.open(encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def codes_from_decision(data: dict) -> set[str]:
    """Extract the selected + additional code set from an LLM #2 decision dict."""
    codes: set[str] = set()
    for bucket in ("selected_codes", "additional_codes"):
        for entry in data.get(bucket, []) or []:
            code = entry.get("code") if isinstance(entry, dict) else entry
            if code:
                codes.add(_norm(code))
    return codes


def load_output_codes(case_id: str) -> set[str] | None:
    """Codes from a saved decision file, or None if the file is absent (checker tier)."""
    path = OUTPUTS_DIR / f"{case_id}.json"
    if not path.exists():
        return None
    return codes_from_decision(json.loads(path.read_text(encoding="utf-8")))


def check_alternative(got: set[str], required, forbidden) -> list[str]:
    """Failure messages for one required/forbidden spec (empty list = pass)."""
    problems = []
    missing = [c for c in (required or []) if _norm(c) not in got]
    present_forbidden = [c for c in (forbidden or []) if _norm(c) in got]
    if missing:
        problems.append(f"missing required {missing}")
    if present_forbidden:
        problems.append(f"forbidden present {present_forbidden}")
    return problems


def assert_case(case_id: str, spec: dict, got: set[str]) -> None:
    """Assert a case's codes satisfy its spec (supports required/forbidden and any_of).
    Shared by both the checker and live tiers so they judge identically."""
    if "any_of" in spec:
        problems = []
        for i, alt in enumerate(spec["any_of"]):
            p = check_alternative(got, alt.get("required", []), alt.get("forbidden", []))
            if not p:
                return  # one acceptable coding matched
            problems.append(f"alt{i}: {'; '.join(p)}")
        pytest.fail(f"{case_id}: no accepted coding matched. got={sorted(got)}; " + " | ".join(problems))
    problems = check_alternative(got, spec.get("required", []), spec.get("forbidden", []))
    assert not problems, f"{case_id}: {'; '.join(problems)}. got={sorted(got)}"
