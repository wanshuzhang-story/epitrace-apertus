# Publish EpiTrace v0.5.3 to GitHub — step by step

**Important:** Upload the **extracted `epitrace-apertus` folder**, not the ZIP alone. The project contains nested source code, documentation, two saved response files, and a 104-second video.

## Recommended route: Mac Terminal with GitHub CLI

1. Download `EpiTrace_v0.5.3_GITHUB_READY.zip` and save it in `~/Downloads`.
2. Open Terminal. If `gh` is not installed and you use Homebrew: `brew install gh` (GitHub CLI: https://cli.github.com/).
3. Run exactly this, one command per line:

```bash
cd ~/Downloads
unzip -q EpiTrace_v0.5.3_GITHUB_READY.zip
cd epitrace-apertus

# Check the release without making any API calls
python3 track_2b/src/release_check.py
shasum -a 256 -c SHA256SUMS.txt

# Authentication: choose GitHub.com, HTTPS and browser login
# Skip if 'gh auth status' already shows a logged-in account
gh auth login

git init -b main
git add .
git status --short
# If asked, configure your real Git commit name/email using 'git config'
git commit -m "Publish EpiTrace benchmark, recorded Apertus evaluation, and offline replay"

gh repo create epitrace-apertus --public --source=. --remote=origin --push \
  --description "An open benchmark for repetition, source dependence and uncertainty in Apertus 1.5 (8B/70B), with 468 real responses and offline replay."

gh repo view --web
```

**Stop before running `gh repo create` if an `epitrace-apertus` repository already exists in your account.** In that case do not create a duplicate: in this local folder run `git remote add origin https://github.com/YOUR_USERNAME/epitrace-apertus.git`, then `git push -u origin main`, assuming the remote is empty. Do not force-push over existing work.

If you see `Author identity unknown` on commit, run `git config user.name "YOUR DISPLAY NAME"` and `git config user.email "YOUR VERIFIED GITHUB EMAIL"`, then repeat the commit. No credentials or API key should ever be pasted in the repository.

## Alternative: GitHub website plus terminal

Open https://github.com/new and enter the name `epitrace-apertus`, set **Public**, and **do not** initialize with README, .gitignore or license. Create the empty repository. After extracting the project ZIP, in Terminal run:

```bash
cd ~/Downloads/epitrace-apertus
git init -b main
git add .
git commit -m "Publish EpiTrace benchmark, recorded Apertus evaluation, and offline replay"
git remote add origin https://github.com/YOUR_USERNAME/epitrace-apertus.git
git push -u origin main
```

If HTTPS authentication fails, use the GitHub CLI (`gh auth login` + `gh auth setup-git`) or GitHub Desktop. GitHub passwords are not accepted for Git operations over HTTPS.

## Verify GitHub after uploading

1. The repository front page displays its README cover image and data summary.
2. Confirm the two files in `track_2b/results/` beginning `apertus-v1.5-` are both present.
3. Confirm `track_2b/docs/EpiTrace_Demo_v0.5.3_SLIM_CAPTIONS.mp4` is present and shows the subtitle panel at the correct reduced height.
4. Confirm `track_2b/EpiTrace_Report_v0.5.pdf` is available.
5. Open the **Actions** tab: wait for `EpiTrace offline reproducibility` to finish. If the Docker job is red, do not claim Docker is verified.
6. Open repository settings/About (the gear icon near the project description) and add the topics listed below.
7. Publish the **repository URL** into your Devpost `Try it out` field and the Hack Apertus submission portal. Do not submit a URL to your private edit page.

## Try it out links — replace YOUR_USERNAME only after GitHub publication

**Source code**
`https://github.com/YOUR_USERNAME/epitrace-apertus`

**Technical report**
`https://github.com/YOUR_USERNAME/epitrace-apertus/blob/main/track_2b/EpiTrace_Report_v0.5.pdf`

**Demo video** (GitHub file page; a streaming host like YouTube gives judges a smoother watch link)
`https://github.com/YOUR_USERNAME/epitrace-apertus/blob/main/track_2b/docs/EpiTrace_Demo_v0.5.3_SLIM_CAPTIONS.mp4`

**Dataset**
`https://github.com/YOUR_USERNAME/epitrace-apertus/tree/main/track_2b/data`

**Saved outputs**
`https://github.com/YOUR_USERNAME/epitrace-apertus/tree/main/track_2b/results`

**Publication caveat:** The script and ZIP do not themselves create or publish a GitHub repository. Publication takes place only after YOU execute the commands and authenticate.

---

# All copy-ready text for GitHub

### GitHub repository name
`epitrace-apertus`

### Description (About field)
An open benchmark for repetition, source dependence and uncertainty in Apertus 1.5 (8B/70B), with 468 real responses and offline replay.

### Topics (enter individually; up to 20)
`apertus`, `llm-evaluation`, `source-provenance`, `epistemic-uncertainty`, `source-dependence`, `repetition`, `synthetic-benchmark`, `digital-humanities`, `misinformation`, `python`, `reproducible-research`, `hack-apertus`

### Repository website
Leave blank until your Devpost page or video hosting page is public. Do not put the Devpost submission editor URL here.

### Branch / visibility
`main` / `Public` for the hackathon, after reviewing the data and open licenses.

### README
Do **not** create a new README, gitignore or LICENSE through GitHub; the release already includes all three.

### Initial commit message
`Publish EpiTrace benchmark, recorded Apertus evaluation, and offline replay`

### GitHub release title
`EpiTrace v0.5.3 — Hack Apertus 2026 submission`

### GitHub release description
# EpiTrace v0.5.3 — Hack Apertus 2026 Track 2B

EpiTrace is an open benchmark for testing whether language models distinguish repeated reports, independently sourced evidence, and **unknown** source relationships.

**Included:** 39 original fictional seed scenarios; 234 controlled cases for each model; 468 recorded responses from Apertus 1.5 8B and 70B via the Public AI API; deterministic scoring, paired comparisons, reproducibility checks and a 104-second captioned demonstration.

**Key finding:** The models almost always recognized documented copies as dependent but neither returned `UNKNOWN` in the 39 unknown-lineage cases per model. These are diagnostic results from synthetic, author-labeled examples, not claims about historical truth or real-world performance.

**Reproduce offline (no API key or inference charges):**

```bash
python3 -m pip install -r track_2b/requirements.txt
make smoke
make replay
```

**Judge entry point:** `make run` (requires Docker, replays saved results without API requests). The Docker path is checked by GitHub Actions when the repository is pushed; it was not locally validated in the original authoring environment.

The demonstration video has slim captions and quiet background sound, **not** a spoken natural-voice track.

Code: Apache-2.0 · Synthetic data: CDLA-Permissive-2.0 · Documentation: CC BY 4.0.

### Ready-to-paste short explanation for judges
EpiTrace asks whether language models treat repeated reports as independent evidence and whether they preserve uncertainty about where information originated. It evaluates Apertus 1.5 8B and 70B on 234 controlled synthetic cases each. Both models handled known copies well, but neither selected UNKNOWN for any of the 39 ambiguous-source cases per model. The repository includes all 468 responses and an offline replay of the results.

### Project video description
A 104-second, captioned walkthrough of EpiTrace's research question, six test conditions, real Apertus 8B/70B evaluation and reproducibility. This release has subtitles and quiet background audio; it does not contain spoken narration.
