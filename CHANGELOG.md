## v0.5.3 (15 October 2026) — slim subtitle panel

- Reduced the caption overlay height from 125 px to 83 px (33.6% smaller), anchoring it to the bottom of the video and removing the redundant READ-ALONG header.
- Kept the slide artwork, caption words and timing, duration (104.33 seconds), and ambient audio unchanged.
- No synthetic speech; no new model runs; benchmark, saved outputs, calculations and technical report unchanged.

## v0.5.1 - 15 October 2026 (narration continuity correction)

- Fixed the demonstration video: removed the 1.15-second artificial silence added after every narration scene in v0.5.
- Preserved all ten original voiceover passages, figures, visual panels, and evaluation results; no new model inference.
- Resynchronized the 10 slides and SRT captions. Final MP4 is approximately 104 seconds, under the two-minute demo requirement.
- Verified that no interior silence longer than 0.45 seconds remains. This is still synthetic eSpeak narration, not a human voice recording.

## v0.5 - 15 October 2026 (submission hardening)

- Changed default Docker `make run` to use the 468 saved real model responses **offline** (no credentials or token charges). The original model inference is still available via explicit `make run-live`.
- Added saved results to the Docker build context and a default verification/replay command; added a GitHub Actions Docker check on clean checkout.
- Updated the written technical report and replay instructions. Kept the original dataset, prompt, raw API responses, statistical results and original hashes unchanged.
- Local authoring environment does not have Docker: **Docker runtime verification is still pending** until GitHub Actions or a participant machine runs `make run`.
- Included a separately authored demonstration video preview and a minimal submission checklist. Video should be reviewed by the project owner before publication.

## v0.3.3 (14 October 2026) - Verified Public AI fallback

- Corrected the incorrectly presumed automatic Hack Apertus HF voucher; official Notion guide link returned 404; direct redemption remains unverified.
- Confirmed Public AI starter credit and both Apertus 1.5 model entries on live provider documentation.
- Added an interactive, hidden-token setup and a Mac/Linux native-Python pilot/full/report wrapper; no Docker required for model experimentation.
- Retained official Docker `make run` route for competition evaluation.
- Preserved benchmark dataset and prompt fingerprints; no model-generated results have been claimed.

# v0.3.2 - Hugging Face credit adapter (14 October 2026)

- Adds Hugging Face-routed OpenAI-compatible inference using hackathon promotional credits once activated.
- Pins Public AI as backend through `:publicai` suffix; checks `/models` availability and live provider metadata when advertised.
- Canonicalizes returned model name without falsely equating provider suffix with model identity.
- Logs requested backend; refuses paired comparison if two model runs use different backend providers.
- Adds 3-case 8B/70B pilots, token safety quickstart, tests and release checks.
- Keeps the dataset and prompts byte-for-byte unchanged; zero actual Apertus inference responses included.

# Changelog

## 2026-10-13: v0.3.1 - Public AI access fallback

- Added self-service Public AI access configuration with its exact lowercase Apertus v1.5 model IDs and required User-Agent header.
- Added `make run-publicai-8b`, `make run-publicai-70b`, `make run-publicai-both`.
- Extended run fingerprints and output metadata to record endpoint base URLs, so CSCS and Public AI results cannot be inadvertently reused together.
- Allowed report and PDF generation after verified Public AI output, with explicit note that this provider does not establish Swiss data residency.
- **No benchmark, reference labels or prompt wording changed. Dataset frozen SHA-256 unchanged.**
- No real inference was run. CI tests are software checks only.

# Changelog

## 2026-10-13: v0.3 release-preparation candidate (no model findings)

- Rebuilt synthetic dossiers deterministically from 39 public seed vignettes; output 234 cases and new SHA-256.
- Reduced answer-cue leakage in known-dependent and independence-positive controls; unknown-provenance copies are now five differently worded, unattributed briefs with no named common original publisher. Unknown condition is not used to assert state invariance.
- Added `src/build_dataset.py`, source generator, reproducible per-instance data/license metadata and structural input checks.
- Implemented explicit CSCS `/models` API preflight and strict per-response `model` identity check, frozen prompt SHA-256, data SHA-256, and run ID; rejected stale/mixed outputs in scoring.
- Implemented `make run-8b`, `make run-70b`, `make run-both`, `make report`, `--dry-run`, seed-paired bootstrap and full case audit exporter.
- Expanded offline unit tests (HTTP mock, wrong-model/sha handling, generator condition constraints, report export). **These are software tests, not Apertus results.**
- Reorganized submission documentation and clearly marked the technical report as incomplete pending real model responses.

## 2026-10-13: v0.2 public candidate

- Isolated private research-derived Livingstone examples from all public candidate files.
- Created 39 new fictional vignettes and six controlled conditions (234 cases), paired scoring and two Apertus model pathways.
- Established anonymous base/no and positive/unknown provenance controls.
- Changed the erroneous classification-confidence metric to event-claim support inflation.

## Before submission

- Confirm public-release ownership, obtain model access, run *real* Apertus, inspect errors, add real-result report PDF, video and public official-template GitHub. Do not publish private research audit or pass mock outputs off as model findings.

## v0.5.2 (15 October 2026) — narration source repair

Replaced the phoneme-disconnected, offline robotic TTS demo with a caption-first MP4 and added an optional online neural narrator generator. Benchmark, model outputs, analysis and report are unchanged. The optional neural voice could not be synthesized or audited in this offline authoring environment.
