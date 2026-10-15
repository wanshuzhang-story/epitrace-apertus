# Data card | EpiTrace public synthetic v0.3

**Dataset:** EpiTrace public synthetic v0.3 (39 authorship seeds, 234 condition dossiers).
**License:** CDLA-Permissive-2.0 on the dataset; see `LICENSE-DATA.md`. Documentation CC BY 4.0. Code Apache-2.0.
**Provenance:** New fictional nineteenth-century-style microstories, authored solely to illustrate different epistemic presentation patterns. Neither the newspaper names nor incidents are intended as real historical claims. The content does NOT reproduce the private Livingstone data, pages, OCR, labels, article excerpts or citation identifiers from the original historical research pipeline.
**Generation:** `python src/build_dataset.py`, deterministic, with no neural or external calls; the seed JSONL defines 39 vignettes; six generation treatments per seed. `validate.py` checks counts, linkage and key constraints.
**Benchmark unit:** one seed family, with six dependent evaluation cases per seed. These rows must not be analyzed as 234 independent observations in inferential procedures.
**Reference labels:** Author-assigned construction states. Source-independence control labels are stipulated by explicit, missing or separately originated provenance presented in the *fictional dossier*. These are **not independently human-adjudicated historical ground truth** and do not establish whether any real event happened.
**License metadata:** `data/epitrace_public_metadata_v0.3.csv`, 234 rows, explicitly marking each synthetic instance and its `CDLA-Permissive-2.0` data license.
**Personal data:** Fictional place and person names in deliberately created vignettes; no participant information is collected.
**Design limits:** Linked dispatch credits make source commonality visible but do not replicate complicated real-world syndication chains; unknown-provenance variants use varied paraphrases, which introduces a wording change and should not be scored for state invariance; independence-positive controls add new evidence and may legitimately change state or closure. The same project designed test cases and reference answers; independent annotation is a follow-up need.
**Release status:** Public candidate pending submitter sign-off. Output predictions are absent and must only be uploaded after genuine verified runs.
