# Coding regression suite

Locks the pipeline's ICD-10-CM output for the 30 regression cases against a
reviewed ground truth, so a change that alters coding behavior is caught.

## Two tiers
- **Checker tier** (`test_regression.py`, default) — validates *saved* decisions in
  `outputs/<case_id>.json` against the ground truth. Fast, offline, free. It compares
  files; it does **not** run the pipeline, so it's a real regression signal only when
  `outputs/*.json` is refreshed from a fresh run.
- **Live tier** (`test_live.py`, opt-in `-m live`) — actually runs the pipeline
  end-to-end (`pipeline_runner.py` replicates `main.py`'s steps via imports, without
  touching `main.py`), then checks the result. Slow, needs a key + network, costs API.

## Layout
- `expected_codes.yaml` — ground truth per case (`required` / `forbidden`, or
  `any_of`). Grounding principle: **documentation-required** (link conditions only
  when the note documents the relationship).
- `test_regression.py` / `test_live.py` — the two tiers (above).
- `pipeline_runner.py` — test-only driver that runs the pipeline for a case id
  without modifying `main.py`. **If `main.py`'s sequence changes, update this.**
- `conftest.py` — shared helpers; both tiers judge with the same `assert_case`.
- `outputs/case_XX.json` — per-case LLM #2 decision. Ships with a **baseline snapshot
  from the 2026-09-28 validated run** so the checker tier is green out of the box.

## Run
```bash
# Fast checker tier (default): compares saved outputs vs ground truth
pip install pytest pyyaml
pytest

# Live tier: runs the real pipeline (needs OPENAI_API_KEY + network + pipeline deps)
pip install pytest pyyaml openai python-dotenv requests beautifulsoup4
pytest -m live

# Live run that also refreshes the checker baseline from the fresh outputs:
REFRESH_OUTPUTS=1 pytest -m live      # Windows: set REFRESH_OUTPUTS=1 && pytest -m live
```
A checker case with no `outputs/*.json` is **skipped**, not failed. Live cases
**skip** if `OPENAI_API_KEY` is unset.

## Re-validating after a change (two ways)
- **Automatic:** `REFRESH_OUTPUTS=1 pytest -m live` — runs the pipeline, writes fresh
  `outputs/*.json`, and asserts against ground truth in one shot.
- **Manual:** run the pipeline, save each decision to `outputs/<case_id>.json`, `pytest`.
Failures show exactly which code is missing or shouldn't be there.

## Notes on specific cases
- **03, 11, 30** — HTN/CKD/diabetes coexist but the relationship isn't documented,
  so codes stay separate (I10, not I12.9; no E11.22 collapse). Deliberate divergence
  from the ICD-10 "with" convention, per project design.
- **09** — obesity is not a diabetic complication; `E11.69` is forbidden.
- **15** — J30 has an Excludes1 for "allergic rhinitis with asthma (J45.909)", so
  `J30.9` is forbidden; the asthma code carries it.
- **17** — contested area (AAFP documentation-required vs the "with"-convention reading
  of hypertensive heart disease). A coder reviews every case before submission, so the
  pipeline's defensible `I50.9 + I10` is locked as the baseline; `I11.0 + I50.9` is also
  acceptable if the pipeline ever emits it (review and update the lock).
- **26, 27, 28** — historical conditions must not be coded at the current encounter.

## Notes
- The live tier drives the pipeline through `pipeline_runner.py`, which re-implements
  `main.py`'s orchestration by importing `functions`/`prompt`/`text_to_icd10`. `main.py`
  itself is unchanged. Keep `pipeline_runner.run_pipeline()` in sync if that flow changes.
- Live runs are non-deterministic (two LLM calls per case). Treat a single red as a
  signal to review, not necessarily a hard bug — re-run to see if it reproduces.
