# EpiTrace - submission and publication checklist

This is an **unpublished** competition submission candidate, not a confirmation of official entry. Only the participant can approve releasing the project and submit it through the event website.

## Project details (copy into form)

**Project name:** EpiTrace - Epistemic Integrity Under Repetition

**Track:** Hack Apertus 2026, Track 2B (Own Project)

**Tagline:** Five publications do not necessarily mean five independent sources.

**Short description:**

EpiTrace is an open-source, reproducible benchmark for source-dependence and uncertainty preservation in language models. It asks whether Apertus interprets repeated newspaper-style reports as independent confirmation, and whether it distinguishes documented dependence from *unknown* source lineage. Thirty-nine original fictional scenarios generate 234 controlled evaluation dossiers. We tested Apertus v1.5 8B and 70B on the same dossier set via the Public AI API, retaining 468 real responses with model, prompt, dataset and timing metadata. Both models correctly identify nearly all explicitly copied reports (117/117 for 8B; 115/117 for 70B), but neither returns UNKNOWN in any of 39 untraceable-origin cases per model. Baseline synthetic state-label agreement is 21/39 for both. These findings concern author-labeled synthetic templates, not human-adjudicated historical truth or Swiss-resident inference. The repository includes data, raw results, deterministic scoring, reproducibility documentation, an offline Docker replay and a short demonstration video.

**Core contribution:** A source-aware diagnostic that distinguishes lack of independently verified evidence from proven common source lineage.

**Code license:** Apache-2.0. **Synthetic data license:** CDLA-Permissive-2.0. **Documentation:** CC BY 4.0.

## 1. Verify locally (no API calls)

Unzip `EpiTrace_v0.5.3_GITHUB_READY.zip`, open Terminal in the extracted folder, and run:

```bash
python3 -m pip install -r track_2b/requirements.txt
make smoke
make replay
```

Optional Docker test (requires Docker Desktop running). This uses the **same saved real responses** and does not consume credits:

```bash
docker info
make run
```

Docker verification could not be done inside the assistant's environment; the GitHub Actions workflow will run this on push. `make run-live` is a DIFFERENT, billable command and should not be needed.

## 2. Review the public release before publishing

Confirm that all 39 fictional seeds, original reference labels, raw responses, and multiple licenses may be made public. Do not commit `.env`, credentials or any private Livingstone material. `make smoke` includes a heuristic release screen, **not legal clearance**. Review the video and replace synthetic voiceover if desired.

## 3. Push to GitHub (from the extracted project root)

Install Git and the GitHub CLI (`gh`) or use the web-based new-repository flow. To publish using `gh` after reviewing the file list:

```bash
git init -b main
git add README.md LICENSE LICENSE-DATA.md LICENSE-DOCS.md MANIFEST.json Makefile .gitignore CHANGELOG.md SUBMISSION_AND_PUBLISH.md .github track_2b publicai_faststart.py PUBLICAI_START_HERE.md
git status --short
git commit -m "EpiTrace: benchmark, verified Apertus evaluation and offline replay"
gh auth login
gh repo create epitrace-apertus --public --source=. --remote=origin --push
```

If the target repository already exists, do not create another. Add the correct remote and push only after inspecting it. Confirm both raw `track_2b/results/apertus-*.jsonl` files and the 104-second MP4 are visible on the *public* GitHub repository. In GitHub Actions, check `EpiTrace offline reproducibility` for a green run before the deadline.

## 4. Official submission

The stated event deadline is **16 Oct 2026, 12:00 CEST**: https://hackapertus.ch/online-hack/submissions

Submit the public repository URL, `track_2b/EpiTrace_Report_v0.5.pdf` (five main pages and one references page), and the public video link (for example the MP4 in the public repository if the form accepts it, or a public/unlisted video hosting URL). Add the dataset or link to `track_2b/data/` where relevant. Carefully check the event form's current video and upload fields; they may vary.

## 5. Honest limitations for the jury

- Diagnostic on 39 author-labeled fictional seed families; no independent human gold labels or real historical newspaper inference.
- Unknown-lineage cases reuse one template, limiting generalization.
- Some baseline 'independence' disputes require annotation adjudication.
- One temperature-zero run per model; no controlled server hardware or calibration study.
- Actual API was Public AI, **not CSCS or Swiss-hosted deployment**.
- Container launch is awaiting participant/CI verification; the offline Python replay and 25 tests passed.

Do not claim public submission, successful Docker deployment, human gold-standard accuracy, or Swiss data residency until independently verified.

### Demo voice correction (v0.5.2)

Use `track_2b/docs/EpiTrace_Demo_v0.5.3_SLIM_CAPTIONS.mp4` in preference to prior robotic-narration previews. It has full read-along captions and quiet ambient sound, but no spoken voice. For an optional humanlike neural voice, see `track_2b/docs/neural_narrator_kit/README.md`, run the supplied Mac command, check the new runtime is below two minutes, and verify the generated speech before uploading.


**Video layout update (v0.5.3):** The included caption-first video has a 33.6% shorter bottom subtitle panel to keep the main slide content visible. There is no synthetic speech.

**GitHub-ready package:** The v0.5.3 file paths and SHA-256 list were aligned with the current slim-caption video. For upload steps and metadata use [GITHUB_UPLOAD_AND_TEXT.md](GITHUB_UPLOAD_AND_TEXT.md).
