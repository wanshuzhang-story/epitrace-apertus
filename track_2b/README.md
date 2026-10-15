# EpiTrace - Hack Apertus Track 2B

**Status (15 Oct 2026):** full Apertus 8B and 70B experiment complete, strict scores reproduced; Docker execution/video/public submission not yet verified.

## One sentence

Can a Swiss open model distinguish five newspaper publications from five genuinely independent evidentiary origins - and acknowledge when their origin is unknown?

## Files and evaluation

- `data/`: 39 original fictional news-like seeds, 234 cases in 6 evidence conditions; synthetic labels are author-defined.
- `src/run_benchmark.py`: resumable OpenAI-compatible, model-identity verified inference.
- `src/score.py` / `src/compare_models.py` / `src/report_results.py`: strict scoring and 39-family paired bootstrap.
- `results/*.jsonl`: 234 actual responses per size from the Public AI endpoint.
- `results/analysis/`: scores, 105 diagnostic flags, per-case audit and charts.
- `technical_report.md` and `EpiTrace_Report_v0.4.pdf`: genuine findings and limitations.
- `docs/REPRODUCE.md`: offline and live reproduction.

## Verify the published experiment without credentials

From project root:

```bash
python3 -m pip install -r track_2b/requirements.txt
make smoke
make replay
```

For charts and PDF additionally install `track_2b/requirements-report.txt` and run `make audit-results && make final-pdf`. No live tokens are spent.

## Required live entry point

The root `make run` builds a Docker image and replays the original results **offline** (no key; no new requests). To run new live inference use `make run-live` or provider-specific live targets with the environment variables:

- `LLM_NAME`: exact Apertus model name
- `LLM_BASE_URL`: OpenAI-compatible inference API base URL
- `LLM_API_KEY`: private credential, never commit it

The default `make run` reads bundled verified Public AI responses, using no external inference. For new Public AI requests use `make run-publicai-8b` / `make run-publicai-70b` with local `.env.publicai`. Docker was not independently available on the authoring machine; the GitHub Actions workflow will check it after publication.

## Measured outcomes

Baseline synthetic state-reference agreement is 21/39 for each model. Duplicate-independence judgments are correct in 117/117 for 8B and 115/117 for 70B. Both identify all 39 independent-witness controls but mislabel all 39 unresolved-lineage controls as NO. A 5,000-seed-bootstrap comparison finds no clear aggregate 70B advantage on the recorded measures. **See report for protocol caveats; no archival correctness is implied.**
