# Public AI run status (15 October 2026)

**The 8B and 70B runs have already been completed successfully.** The exact 468 original responses and derived analysis are bundled under `track_2b/results`. Do NOT repeat the full inference solely to regenerate the technical report.

Run these free, offline validation commands:

```bash
python3 -m pip install -r track_2b/requirements.txt
make smoke
make replay
```

Install the additional reporting packages from `track_2b/requirements-report.txt` and execute `make final-pdf` if needed.

If and only if you decide to conduct an additional study, `publicai_faststart.py` remains an authenticated runner. An API key is required for live calls and is not part of this repository. See `track_2b/docs/REPRODUCE.md` for protocol and original model IDs.
