"""Emit tests/outputs/case_XX.json baseline fixtures from the 2026-09-28 run.
Each fixture holds the selected_codes + additional_codes actually produced.
Run once: python _build_fixtures.py
"""
import json
from pathlib import Path

OUT = Path(__file__).resolve().parent / "outputs"
OUT.mkdir(exist_ok=True)

# (selected: [(code, role)], additional: [code])
RUN = {
    "case_01_diabetes_single":            ([("E11.9", "primary")], []),
    "case_02_diabetes_ckd_explicit":      ([("E11.22", "primary"), ("N18.1", "secondary")], []),
    "case_03_diabetes_ckd_coexistence":   ([("E11.9", "primary"), ("N18.1", "secondary")], []),
    "case_04_diabetes_hypertension_explicit":     ([("E11.9", "primary"), ("I10", "secondary")], []),
    "case_05_diabetes_hypertension_coexistence":  ([("E11.9", "primary"), ("I10", "secondary")], []),
    "case_06_hypertension_single":        ([("I10", "primary")], []),
    "case_07_ckd_stage_three":            ([("N18.30", "primary")], []),
    "case_08_hypertension_ckd_relationship":      ([("I12.9", "primary")], ["N18.30"]),
    "case_09_diabetes_obesity":           ([("E11.9", "primary"), ("E66.9", "secondary")], []),
    "case_10_diabetes_hyperlipidemia":    ([("E11.9", "primary"), ("E78.5", "secondary")], []),
    "case_11_diabetes_ckd_hypertension":  ([("E11.22", "primary"), ("I10", "secondary")], ["N18.1"]),
    "case_12_copd_single":                ([("J44.9", "primary")], []),
    "case_13_copd_hypertension":          ([("J44.9", "primary"), ("I10", "secondary")], []),
    "case_14_asthma_single":              ([("J45.909", "primary")], []),
    "case_15_asthma_rhinitis":            ([("J45.909", "primary")], []),
    "case_16_heart_failure_single":       ([("I50.9", "primary")], []),
    "case_17_heart_failure_hypertension": ([("I50.9", "primary"), ("I10", "secondary")], []),
    "case_18_obesity_hypertension_diabetes": ([("E66.9", "primary"), ("E11.9", "secondary"), ("I10", "secondary")], []),
    "case_19_hypothyroidism_single":      ([("E03.9", "primary")], []),
    "case_20_gerd_single":                ([("K21.9", "primary")], []),
    "case_21_osteoarthritis_single":      ([("M17.9", "primary")], []),
    "case_22_depression_single":          ([("F32.A", "primary")], []),
    "case_23_acute_bronchitis":           ([("J20.9", "primary")], []),
    "case_24_viral_respiratory_illness":  ([("J06.9", "primary")], []),
    "case_25_dental_caries":              ([("K02.9", "primary")], []),
    "case_26_acute_with_diabetes_history": ([("J20.9", "primary")], []),
    "case_27_historical_diabetes_current_uri": ([("J06.9", "primary")], []),
    "case_28_historical_multiple_current_htn": ([("I10", "primary")], []),
    "case_29_diabetes_ckd_anemia":        ([("E11.22", "primary"), ("D64.9", "secondary")], ["N18.1"]),
    "case_30_multiple_relationships":     ([("E11.22", "primary"), ("I10", "secondary")], ["N18.1"]),
}

for case_id, (selected, additional) in RUN.items():
    doc = {
        "selected_codes": [{"code": c, "role": r, "reason": ""} for c, r in selected],
        "additional_codes": [{"code": c, "reason": ""} for c in additional],
        "rejected_candidates": [],
    }
    (OUT / f"{case_id}.json").write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")

print(f"wrote {len(RUN)} fixtures to {OUT}")
