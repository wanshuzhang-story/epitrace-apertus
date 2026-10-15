# EpiTrace v0.5 - submission checklist (15 Oct 2026)

## Verified
- [x] Original fictional 39-seed / 234-dossier benchmark; source hash frozen
- [x] 468 complete real API responses; served model identity and dataset/prompt fingerprints checked
- [x] 25 offline tests and release screening passed; `make replay` confirms results
- [x] Error review differentiating 105 automated flags from independently adjudicated mistakes
- [x] Technical report PDF with genuine results (5 content pages + references)
- [x] Saved raw response logs and reproducible paired bootstrap
- [x] Code Apache-2.0, docs CC-BY-4.0, original synthetic data CDLA-Permissive-2.0

## Must be completed by project owner
- [ ] Inspect repository files and approve public release/licensing (no historical/private material included)
- [ ] On own machine or GitHub Actions: verify Docker `make run` offline; clearly disclose that no Docker engine was available in the authoring runtime
- [x] Generated a 104-second caption-first MP4 preview from genuine results (owner review required; robotic voice removed)
- [ ] Review/approve the captioned preview, or use the optional online neural narrator builder before publishing the video
- [ ] Upload the candidate to an owner-controlled *public* GitHub repository; confirm raw logs are actually tracked despite .gitignore
- [ ] Complete official Hack Apertus website submission with working GitHub URL, technical report, dataset, and video before **16 Oct 2026, 12:00 CEST**

Never upload `.env`, an API key, or the separate private Livingstone audit. The Public AI run is not evidence of Swiss-hosted data residency.
