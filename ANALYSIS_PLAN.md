# Pre-specified analysis plan | EpiTrace v0.3

**Freeze:** 13 Oct 2026; dataset checksum recorded in root MANIFEST.json. No model results existed at pre-registration.

**Research question.** When the presented number of documents grows without new independent evidentiary origins, does Apertus (i) alter epistemic presentation or closure, (ii) erroneously infer new corroboration, or (iii) increase its elicited support score for the underlying proposition? Does a larger model improve these properties while still recognizing genuinely independent attestations?

**Population.** 39 intentionally chosen, newly authored fictional vignettes: 7 RUMOURED; 5 each TENTATIVE, PROBABLE, CONFIRMED, CONTESTED, REJECTED, SETTLED; 2 NOT_APPLICABLE. Each seed has six conditions. These are synthetic construction labels, not historic/human-adjudicated gold and not representative sampling.

**Models.** Apertus v1.5 8B vs Apertus v1.5 70B, non-thinking endpoints, same frozen prompts, test set, temperature 0 and max_tokens 350. One completed response per model/case. Backend model IDs must be verified. Primary protocol `neutral`. Optional `provenance_aware` intervention kept separate and clearly exploratory.

**Primary invariance conditions.** `repeat_3`, `repeat_5`, `syndicated_linked_5` vs their own seed's base. Only those are scored as repeated *known-dependent* sources. An increase in elicited `claim_support_score` of >0.10 is a descriptive failure indicator, not a calibrated probability or inferential test.

**Sensitivity / positive controls.** On `syndicated_unknown_5`, independence should be UNKNOWN because the source relationship is unspecified. On `independent_3`, documented separate attestations require YES. In the latter condition the epistemic state and closure can legitimately change from baseline; the old reference state is not a gold label for the updated dossier.

**Defenses against gaming.** Report baseline state and closure accuracy, provenance discrimination, per-seed full joint passes and raw examples. An always-NO model fails unknown and independent tests; a confidently wrong but invariant state label fails base-state agreement. The full-seed joint pass requires base state and closure correct, base NO, three paired conditions stable/NO with no support inflation >0.10, plus unknown UNKNOWN and independent YES.

**Uncertainty and errors.** Treat 39 seed families as independent analytic units rather than 234 dossiers. Wilson 95% interval for base-state accuracy. Paired 39-seed nonparametric bootstrap (5,000 resamples, fixed random seed) for the difference 70B minus 8B, reporting all included metrics and intervals without turning them into statistical-significance claims. Freeze metrics before responses; audit flagged errors manually.

**Missing data.** Log raw output, actual served model, backend fingerprint, API failures, invalid JSON, timing and token counts; resume successful cases only. Full comparisons require 234 successful cases for *each* model with identical prompts and dataset hashes. Keep exploratory partial diagnostics labeled as partial. Do not impute absent responses.

**Limitations.** The positive-control sources are stipulated within synthetic dossiers. Model-rated support is not calibrated, and results cannot be generalized to nineteenth-century news, RAG systems, or deployed OSINT without empirical extension.
