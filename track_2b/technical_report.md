# EpiTrace: Epistemic Integrity Under Repetition - real-results technical report

Hack Apertus 2026, Track 2B / Own Project. Version 0.5, dated 15 October 2026.

**Status:** Apertus 8B and 70B completed 234 cases each. The author has not yet published a GitHub repository, published a public video, tested Docker in the authoring runtime, or submitted the project.

## Problem and impact

In news monitoring, document intelligence and AI-assisted scholarship, repeated reports can look like new corroboration. EpiTrace measures whether models interpret the structure of evidence origins rather than simply counting documents. Its source-oriented outputs expose the difference between genuine independence, documented copying, and unknown lineage.

## Models, inference and architecture

Models: `swiss-ai/apertus-v1.5-8b` and `swiss-ai/apertus-v1.5-70b` (actual served IDs). Client: `requests` Python, optional Docker, OpenAI-compatible chat completions. Serving: `https://api.publicai.co/v1` (Public AI, not CSCS). Same `temperature=0`, `max_tokens=350`, input and prompt fingerprints for each model. Prompt defines eight epistemic states, four closure values, three evidence-independence values and a numeric event-claim support rating. It does not reveal condition IDs or author labels.

39 original fictional newspaper-style seed cases (7 RUMOURED, 5 each TENTATIVE/PROBABLE/CONFIRMED/CONTESTED/REJECTED/SETTLED, 2 NOT_APPLICABLE) expand into 234 controlled dossiers: original, exact x3, exact x5, known-linked five newspapers, unknown-origin five publications, and two added independent firsthand records. The last two variants are not subjected to state invariance tests because they change or add evidence.

**Frozen input SHA-256** `eec19b80367947138a54b9b3e5188a6ccc70811bf722ca3a6eb275d53f574900`  
**Frozen prompt SHA-256** `b7ced5bf89b70205adc855412b78f878314715de2fbed04681d30dedb7c22485`

## Evaluation method

Scores measure baseline agreement with *author-constructed synthetic reference labels*, state/closure invariance for known copies, independent-source labels YES/NO/UNKNOWN, and elicited support-score inflation >0.10 when documents are duplicated. Bootstrap CIs draw 5,000 samples of 39 paired seed families, not 234 pseudo-independent rows. Model-output IDs, provider, hashes, HTTP status, tokens and latency were logged. 25 offline tests and the strict score replay passed.

## Results from original inference logs

| Metric | 8B | 70B | 70B - 8B paired 95% bootstrap interval |
|---|---:|---:|---:|
| Baseline synthetic state-reference agreement (39) | 21/39, 53.8% | 21/39, 53.8% | 0.0 pp [-10.3,+10.3] |
| Known-copy state invariance (117) | 93/117, 79.5% | 94/117, 80.3% | +0.9 pp [-10.3,+12.0] |
| Known-copy closure invariance (117) | 108/117, 92.3% | 107/117, 91.5% | -0.9 pp [-6.8,+5.1] |
| Known-copy NO independence (117) | 117/117, 100.0% | 115/117, 98.3% | -1.7 pp [-5.1,0.0] |
| Unknown lineage UNKNOWN (39) | 0/39, 0.0% | 0/39, 0.0% | 0.0 pp [0.0,0.0] |
| Independent records YES (39) | 39/39, 100.0% | 39/39, 100.0% | 0.0 pp [0.0,0.0] |
| Known-copy support inflation >0.10 (117) | 2/117, 1.7% | 1/117, 0.9% | -0.9 pp [-5.1,+2.6] |
| Full-seed joint pass (39) | 0/39 | 0/39 | 0.0 pp [0.0,0.0] |

**Interpretation:** Neither model routinely mistakes explicitly duplicated sources for independent confirmations in this controlled design. The major reproducible failure is labeling all five-source *unknown-origin* dossiers NO (no independently corroborating origin proven) rather than UNKNOWN (relationship untraceable). The zero full-seed joint score is wholly driven by this condition and should not be treated as a holistic model rating. No statistically distinguishable aggregate 70B advantage appears in these seed-paired measures.

## Manual-review priorities (not independently adjudicated errors)

105 flags comprise 78 unknown-lineage observations (39 per model), 22 baseline one-source independence disagreements (10 for 8B, 12 for 70B), 2 known-copy false YES predictions by 70B (`PUB029__repeat_3`, `PUB029__repeat_5`), and 3 known-copy event-support inflation cases (8B `PUB037__repeat_3`, `PUB037__repeat_5`; 70B `PUB018__repeat_5`). The baseline disputes may conflate official verification with genuinely separate evidentiary origin, so require further adjudication.

Baselines show systematic reference mismatches for PROBABLE, SETTLED and NOT_APPLICABLE. Some may reflect author-defined category boundaries and not model mistakes in an external sense. The original `per_case_audit.csv`, 105-row flagged audit, seed table, figures, and full raw outputs are included.

## Compute, cost and scalability

Both models logged 132,149 prompt tokens. 8B produced 18,202 output tokens, 70B 18,038. Recorded median latency was 5.123 vs 1.739 seconds; total logged latencies were 1306.67 vs 1218.17 seconds, respectively. Provider serving conditions and tail delays are uncontrolled, so speed measurements are descriptive only.

At Public AI published 12 Oct 2026 token tariffs ($0.10/$0.20 input/output for 8B, $0.82/$2.92 for 70B per million), calculated main-experiment API calls cost ~$0.178 total, excluding pilot, rounding and credits. This is a tariff-based *estimate*, not a user billing record.

The serialized benchmark is <1 MB, the Python/Docker client is lightweight, and the archive contains source, tests, separate run identities and data cards. Repeated study runs would scale linearly in billed tokens for comparable prompt sizes, apart from provider-dependent caching/batching/retries.

## Sovereign deployability and constraints

The models are open and Swiss-developed. The reference client can point to a separately hosted OpenAI-compatible endpoint, including appropriate Swiss sovereign deployments. **This experiment did not use Swiss-hosted CSCS inference** and cannot claim local data residency or air-gapped availability. The Docker image has been built into the project, but Docker runtime testing remains outstanding.

## Limitations and responsible release

The cases are original synthetic text, not 19th-century archival excerpts. No original Livingstone quotations or private research-derived labels are included. Construction labels have not been independently human-adjudicated; similar synthetic templates constrain the generalizability of all 39 seed families. The neutral prompt explicitly describes source independence, so the test measures instruction following under a source-aware rubric, not spontaneous epistemic reasoning. The elicited 0-1 support score is not a calibrated probability, and the >0.10 change cut-off is a diagnostic heuristic. There is one recorded run per model, at requested temperature zero; backend load, sampling repeatability and hardware are not controlled.

After copyright/label review, future work should add independently adjudicated historical reuse graphs, paraphrases, OCR noise, blind-source dependence labels and genuinely uncertain source histories to test external validity.

## Exact reproduction and verification

From the root: `python3 -m pip install -r track_2b/requirements.txt`, `make smoke` then `make replay`. Replays use the actual saved inference records and do **not** send tokens to an endpoint. `make run` now executes an offline Docker replay of the verified 468 responses without API credentials or charges; new inference requires explicit `make run-live` with `LLM_NAME`, `LLM_BASE_URL`, `LLM_API_KEY`. Docker execution could not be independently tested in the authoring runtime; CI will check it after publication. `make audit-results` needs `matplotlib` and regenerates the supplementary CSVs and figures. `make final-pdf` uses `reportlab` to recreate the actual-results PDF. No credential is published.

See `results/analysis/EpiTrace_Independent_Methodological_Audit.md` for detailed interpretation, and `docs/REPRODUCE.md` for commands.

## Open licences and citations

Source code: Apache License 2.0. This technical report and documents: CC BY 4.0. Synthetic dataset: CDLA-Permissive 2.0. Full organiser requirements: https://hackapertus.ch/online-hack and https://github.com/HackApertus/project-template . Public AI model catalog and tariff: https://platform.publicai.co/models .

The candidate includes a 118-second synthetic-voice narrated MP4 and caption/voiceover files in `docs/`. This preview was generated using the measured results; participants should review and approve it before publication.
