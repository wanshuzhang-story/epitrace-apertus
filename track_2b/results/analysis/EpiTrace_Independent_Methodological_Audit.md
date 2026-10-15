# EpiTrace - independent post-evaluation audit

**Assessment date:** 15 October 2026. **Source:** full original logs uploaded as `EpiTrace_REAL_RESULTS.zip`. **Purpose:** separate measured results from design assumptions.

## Integrity and coverage

- Validated all 234 unique case IDs for each of two actual served models, plus consistent dataset/prompt SHA-256 values. Both runs completed on `https://api.publicai.co/v1` with `temperature=0`, 350-token generation cap and 39 paired seed families.
- Re-executed project `make smoke` (25 tests pass) and `make report` (same 105 flags) without a new API request.
- Frozen dataset SHA-256: `eec19b80367947138a54b9b3e5188a6ccc70811bf722ca3a6eb275d53f574900`. Prompt source SHA-256: `b7ced5bf89b70205adc855412b78f878314715de2fbed04681d30dedb7c22485`.
- The model IDs are recorded by the API as `swiss-ai/apertus-v1.5-8b` and `swiss-ai/apertus-v1.5-70b` respectively; system fingerprint differs per model. The requested provider is Public AI, not CSCS. No Swiss residency was tested.

## Principal experimental results

| Measure | 8B | 70B | Comment |
|---|---:|---:|---|
| Baseline synthetic state agreement | 21/39 (53.8%) | 21/39 (53.8%) | Same aggregate, four different predictions; 19 both correct, 16 both incorrect, two unique to each. |
| Known-copy state invariance | 93/117 (79.5%) | 94/117 (80.3%) | Stable relative to each model's baseline, not correctness against author label. |
| Known-copy closure invariance | 108/117 (92.3%) | 107/117 (91.5%) | Same limitation. |
| Known-copy NO source independence | 117/117 (100%) | 115/117 (98.3%) | Two 70B errors occur in PUB029 x3 and x5 repeated retractions. |
| Unknown provenance labelled UNKNOWN | 0/39 | 0/39 | Both consistently returned NO. |
| Separate eyewitness sources labelled YES | 39/39 | 39/39 | Explicitly independent notebook/diary template, comparatively easy control. |
| Dependent-copy support inflation > 0.10 | 2/117 | 1/117 | 8B PUB037 x3/x5; 70B PUB018 x5. |
| Full-seed joint pass | 0/39 | 0/39 | Forced to zero by universal failure of unknown provenance; should not be used as a global ranking. |

Paired seed bootstrap for baseline state difference (70B minus 8B): **0.0 percentage points** with 95% interval **[-10.3,+10.3] pp**. No measured paired accuracy advantage of 70B is established; compare `paired_comparison.json` for all intervals.

## Decomposition of the 105 automated flags

The flagged entries are **model-case observations**, not distinct sources, seeds, or independently validated human errors.

- **78/105:** unknown-lineage case predicted NO by both models (39 per model). This is the dominant systematic failure under the benchmark's specified three-class definition.
- **22/105:** base excerpts predicting YES or UNKNOWN rather than author-reference NO (10 from 8B, 12 from 70B). Several cite official documents or corrections; these deserve independent adjudication because *independent origin* and *official verification* are being conflated by the model and perhaps ambiguity of annotation.
- **2/105:** 70B falsely returned YES on `PUB029__repeat_3` and `PUB029__repeat_5`, treating repeated retractions from a single newspaper as independent evidence.
- **3/105:** support increase >0.10 despite exact repetition: 8B `PUB037__repeat_3` and `PUB037__repeat_5` (0.75 to 0.95); 70B `PUB018__repeat_5` (0.75 to 0.95).

## Counterexamples and epistemic interpretation

**PUB001__syndicated_unknown_5 (both models):** Five unsigned publications share a claim without lineage. Both label NO, and their rationales explain lack of demonstrated independent corroboration rather than established common sourcing. This illustrates collapsing absence of demonstrated independence into evidence of dependence. Since the input deliberately withholds links, UNKNOWN is the construction label, not externally proven ground truth.

**PUB029__repeat_3 / repeat_5 (70B):** The same newspaper retracts its earlier claim in identical copies. The two YES predictions explicitly confuse correction/verification with independent evidentiary origins, a genuine protocol-defined error.

**PUB021__base (both models):** A single newspaper cites a signed bridge order. Both label YES, as if documentary verification implied independent corroboration. Under the author's stipulated single-source baseline this is marked wrong, but a human should check the conceptual boundary between publication and underlying official document before calling it a validated failure.

**PUB038__base / PUB039__base:** Neither model classified the clearly figurative comic/advertising input as NOT_APPLICABLE. This is a separate discourse-classification difficulty, not evidence repetition.

## Systematic state-reference mismatches

- `PROBABLE`: 0/5 baseline cases correct for **both** models; all five downgraded to TENTATIVE.
- `SETTLED`: 0/5 for **both**; usually downgraded to CONFIRMED (four seeds) or PROBABLE (one).
- `NOT_APPLICABLE`: 0/2 for **both**, despite overtly figurative text.
- `CONFIRMED`: 0/5 for 8B, 2/5 for 70B (mostly PROBABLE), indicating a systematic difference in how models read official confirmation.

The baseline reference labels are authored for synthetic material; some mismatches may reflect rubric interpretation. They should not be reported as newspaper-domain factual inaccuracies.

## Known limitations relevant to the contest jury

1. **Synthetic author labels, no blind human adjudication.** The data do not support claims of historical or real-world deployment accuracy.
2. **Templates make positive controls easy.** The independently maintained inspector/caretaker accounts openly establish their independence, and the common dispatch IDs visibly identify shared origin.
3. **Guide already explains source independence.** Even the 'neutral' prompt operationally defines YES, NO and UNKNOWN, so performance measures following the schema, not spontaneous uninstructed reasoning.
4. **Unknown cases are homogeneous.** All 39 unknown dossiers are created by one five-clipping template with substituted claims. The 0/39 result is systematic in this design, not evidence of universal model behavior.
5. **Elicited support is not calibrated probability.** Support-score inflation threshold 0.10 was chosen as a diagnostic threshold.
6. **No repeated sampling or controlled serving hardware.** Differences in median API latency cannot be interpreted as hardware-scaled throughput differences.
7. **Backend sovereignty is not demonstrated.** Apertus models have Swiss origin and are open, but these results were served through Public AI; do not assert Swiss data residency.

## Logged resource use and cost estimate

| Measure | 8B | 70B |
|---|---:|---:|
| Prompt tokens | 132,149 | 132,149 |
| Completion tokens | 18,202 | 18,038 |
| Median recorded latency | 5.123 s | 1.739 s |
| Total logged latency | 1306.67 s | 1218.17 s |
| Theoretical API charges* | $0.017 | $0.161 |

* At listed Public AI rates as of 12 October 2026: 8B $0.10/$0.20 and 70B $0.82/$2.92 per million input/output tokens. Approximate full benchmark call charges are **$0.178** before pilots, credits, retries, tax, rounding or billing adjustments. These are NOT an invoice or verified account charges.

## Conclusion appropriate for release

> In 39 synthetic case families (234 dossiers per model), Apertus v1.5 8B and 70B almost always refused to treat explicitly shared-origin reports as independent, with no demonstrated scaling advantage on baseline state agreement. Both nevertheless returned NO rather than UNKNOWN for every case where source lineage was deliberately left unspecified. EpiTrace therefore identifies a reproducible uncertainty-representation failure within a controlled benchmark, not a general failure of Apertus to recognize copied articles.

**Files:** `EpiTrace_Flagged_Observations_105.csv`, `EpiTrace_39_Seed_Paired_Review.csv`, `EpiTrace_Condition_Results.csv`, two diagnostic plots, original verified raw predictions and the original analysis are included in the release candidate. No API credentials are part of this output.
