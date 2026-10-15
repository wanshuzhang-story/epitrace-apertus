# Reproducing the real EpiTrace results

Use a clean clone of this release, Python 3.12+ and Git. This route makes **zero new model requests**.

```bash
python3 -m pip install -r track_2b/requirements.txt
make smoke
make replay
```

The reporter strictly verifies that both prediction files contain 234 successful case IDs with matching model, dataset and prompt fingerprints, and then recreates `results/analysis/{paired_comparison.json,per_case_audit.csv,model_a_summary.json,model_b_summary.json,model_comparison.svg,RESULTS_SUMMARY.md}`.

For additional diagnostics or PDF:

```bash
python3 -m pip install -r track_2b/requirements-report.txt
make audit-results
make final-pdf
```

### Verify each raw file against the manifest

```bash
python3 - <<'PY'
import json,hashlib,pathlib
m=json.loads(pathlib.Path('MANIFEST.json').read_text())
for name,expected in m['inference_output_sha256'].items():
 p=pathlib.Path('track_2b/results')/name
 actual=hashlib.sha256(p.read_bytes()).hexdigest()
 print(name, 'OK' if actual==expected else 'MISMATCH')
PY
```

### Live inference requires authorization

The recorded run used direct Public AI OpenAI-compatible endpoints via `python publicai_faststart.py full` with a locally supplied, hidden API key and two model IDs `swiss-ai/apertus-v1.5-8b` / `swiss-ai/apertus-v1.5-70b`. `make run` is the competition's Docker pathway: it replays the published 468 original responses offline and does not need a key. `make run-live` requires `LLM_NAME`, `LLM_BASE_URL`, `LLM_API_KEY`. `make run-publicai-8b` and `make run-publicai-70b` additionally support a locally saved `track_2b/.env.publicai`. Never publish `.env*` or raw keys. Docker path has not been verified on the report-authoring machine.

### What the logs establish

The verified model identity is the model ID returned by the Public AI endpoint (plus model-specific `system_fingerprint`). That shows the claimed models were served according to their provider's metadata; it is not an external audit of remote GPU hardware or Swiss hosting. This dataset is synthetic and source-relationship labels are author-imposed.
