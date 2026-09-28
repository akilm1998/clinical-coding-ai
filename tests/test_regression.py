"""
Checker tier — validates SAVED pipeline decisions against the ground truth.

For each case, the codes in tests/outputs/<case_id>.json (selected + additional)
must contain every `required` code and no `forbidden` code from expected_codes.yaml.
Matching is on code presence (role/bucket not asserted).

Important: this tier compares saved files, it does NOT run the pipeline. It only
becomes a real regression signal when tests/outputs/*.json is regenerated from a
fresh run (manually, or via the live tier with REFRESH_OUTPUTS=1). A case with no
output file is skipped, not failed.
"""
from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from conftest import assert_case, load_output_codes

_EXPECTED = yaml.safe_load((Path(__file__).resolve().parent / "expected_codes.yaml").read_text(encoding="utf-8"))
CASE_IDS = sorted(_EXPECTED.keys())


@pytest.mark.parametrize("case_id", CASE_IDS)
def test_case_codes(case_id, expected):
    got = load_output_codes(case_id)
    if got is None:
        pytest.skip(f"no output file for {case_id} (tests/outputs/{case_id}.json)")
    assert_case(case_id, expected[case_id], got)
