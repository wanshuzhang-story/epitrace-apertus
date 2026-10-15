# EpiTrace complete-run analysis (neutral)

Frozen dataset SHA-256: `eec19b80367947138a54b9b3e5188a6ccc70811bf722ca3a6eb275d53f574900`
Prompt source SHA-256: `b7ced5bf89b70205adc855412b78f878314715de2fbed04681d30dedb7c22485`
API base: `https://api.publicai.co/v1`

Model A: `swiss-ai/apertus-v1.5-8b`. Model B: `swiss-ai/apertus-v1.5-70b`. All 234 cases succeeded for each model.

| Metric | Apertus 8B | Apertus 70B | 70B - 8B [paired bootstrap 95%] |
|---|---:|---:|---:|
| Baseline state agreement (synthetic reference) | 0.538 | 0.538 | +0.000 [-0.103,+0.103] |
| Known-copy state invariance | 0.795 | 0.803 | +0.009 [-0.103,+0.120] |
| Known-copy closure invariance | 0.923 | 0.915 | -0.009 [-0.068,+0.051] |
| Known-copy NO independence | 1.000 | 0.983 | -0.017 [-0.051,+0.000] |
| Unresolved-lineage UNKNOWN | 0.000 | 0.000 | +0.000 [+0.000,+0.000] |
| Independent-witness YES | 1.000 | 1.000 | +0.000 [+0.000,+0.000] |
| Support inflation rate (>0.10; lower is better) | 0.017 | 0.009 | -0.009 [-0.051,+0.026] |
| All-criteria joint pass per seed | 0.000 | 0.000 | +0.000 [+0.000,+0.000] |

## Runtime and tokens (recorded, not estimated)

| Statistic | 8B | 70B |
|---|---:|---:|
| median_latency_seconds | 5.123 | 1.739 |
| total_logged_latency_seconds | 1306.67 | 1218.17 |
| prompt_tokens | 132149 | 132149 |
| completion_tokens | 18202 | 18038 |

## Priority examples for manual adjudication

The examples below are DIAGNOSTIC flags; they are not automatically validated human errors.

### PUB001__syndicated_unknown_5 — 8B
- Reference independence: `UNKNOWN`; predicted: `NO`
- Claim support change from baseline: +0.100
- Model rationale: All five documents repeat the same unverified claim with no named sources or independent origins; no evidence of corroboration exists.
- Excerpt: DOCUMENT 1 | Alderwick Herald
A brief unsigned report says that the north canal gate at Alderwick was forced open overnight. This copy has no attribution field.

DOCUMENT 2 | Briar Ledger
A news note  ...

### PUB002__syndicated_unknown_5 — 8B
- Reference independence: `UNKNOWN`; predicted: `NO`
- Claim support change from baseline: -0.100
- Model rationale: All five documents repeat the same unverified claim with no named sources or independent origins; no corroborating evidence is documented.
- Excerpt: DOCUMENT 1 | Alderwick Herald
A brief unsigned report says that the stone footbridge at Braehampton lost its central railing. This copy has no attribution field.

DOCUMENT 2 | Briar Ledger
A news note ...

### PUB003__syndicated_unknown_5 — 8B
- Reference independence: `UNKNOWN`; predicted: `NO`
- Claim support change from baseline: +0.000
- Model rationale: All five documents repeat the same unverified claim with no named sources or independent origins; no corroborating evidence is documented.
- Excerpt: DOCUMENT 1 | Alderwick Herald
A brief unsigned report says that the west market bell at Carrow stopped at midnight. This copy has no attribution field.

DOCUMENT 2 | Briar Ledger
A news note describes ...

### PUB004__syndicated_unknown_5 — 8B
- Reference independence: `UNKNOWN`; predicted: `NO`
- Claim support change from baseline: +0.100
- Model rationale: All five documents repeat the same claim without independent sourcing or attribution; no corroborating evidence is documented.
- Excerpt: DOCUMENT 1 | Alderwick Herald
A brief unsigned report says that a sealed cargo chest went missing from Dunstmere quay. This copy has no attribution field.

DOCUMENT 2 | Briar Ledger
A news note descri ...

### PUB005__syndicated_unknown_5 — 8B
- Reference independence: `UNKNOWN`; predicted: `NO`
- Claim support change from baseline: +0.100
- Model rationale: All five documents repeat the same unverified claim with no named sources or independent origins; no corroborating evidence is documented.
- Excerpt: DOCUMENT 1 | Alderwick Herald
A brief unsigned report says that a new water wheel was damaged at Eglinton mill. This copy has no attribution field.

DOCUMENT 2 | Briar Ledger
A news note describes a r ...

### PUB006__syndicated_unknown_5 — 8B
- Reference independence: `UNKNOWN`; predicted: `NO`
- Claim support change from baseline: +0.000
- Model rationale: All five documents repeat the same unverified claim with no named sources or independent origins; no corroborating evidence is documented.
- Excerpt: DOCUMENT 1 | Alderwick Herald
A brief unsigned report says that the southern watch hut at Fairhaven was deserted. This copy has no attribution field.

DOCUMENT 2 | Briar Ledger
A news note describes a ...

### PUB007__syndicated_unknown_5 — 8B
- Reference independence: `UNKNOWN`; predicted: `NO`
- Claim support change from baseline: -0.100
- Model rationale: All five documents repeat the same unverified claim with no named sources or independent origins; no corroborating evidence is documented.
- Excerpt: DOCUMENT 1 | Alderwick Herald
A brief unsigned report says that a packet of registry maps disappeared at Greyford. This copy has no attribution field.

DOCUMENT 2 | Briar Ledger
A news note describes  ...

### PUB008__syndicated_unknown_5 — 8B
- Reference independence: `UNKNOWN`; predicted: `NO`
- Claim support change from baseline: -0.100
- Model rationale: All five documents repeat the same unverified claim with no named sources or independent origins; no corroborating evidence is documented.
- Excerpt: DOCUMENT 1 | Alderwick Herald
A brief unsigned report says that the telegraph relay at Halestone stopped transmitting. This copy has no attribution field.

DOCUMENT 2 | Briar Ledger
A news note descri ...

### PUB009__syndicated_unknown_5 — 8B
- Reference independence: `UNKNOWN`; predicted: `NO`
- Claim support change from baseline: +0.000
- Model rationale: All five documents repeat the same claim without independent sourcing or attribution; no corroborating evidence is documented.
- Excerpt: DOCUMENT 1 | Alderwick Herald
A brief unsigned report says that two crates of seed grain were damaged at Ironmere station. This copy has no attribution field.

DOCUMENT 2 | Briar Ledger
A news note de ...

### PUB010__syndicated_unknown_5 — 8B
- Reference independence: `UNKNOWN`; predicted: `NO`
- Claim support change from baseline: -0.100
- Model rationale: All five documents repeat the same claim without independent sourcing or attribution; they appear to be copies of the same unverified report.
- Excerpt: DOCUMENT 1 | Alderwick Herald
A brief unsigned report says that the east sluice at Juniperford failed its spring test. This copy has no attribution field.

DOCUMENT 2 | Briar Ledger
A news note descri ...

### PUB011__syndicated_unknown_5 — 8B
- Reference independence: `UNKNOWN`; predicted: `NO`
- Claim support change from baseline: -0.100
- Model rationale: All five documents repeat the same anonymous claim with no independent sourcing or attribution; no verification steps are documented.
- Excerpt: DOCUMENT 1 | Alderwick Herald
A brief unsigned report says that the council minute book at Kingshollow was misplaced. This copy has no attribution field.

DOCUMENT 2 | Briar Ledger
A news note describ ...

### PUB012__syndicated_unknown_5 — 8B
- Reference independence: `UNKNOWN`; predicted: `NO`
- Claim support change from baseline: +0.000
- Model rationale: All five documents repeat the same claim without independent sourcing or attribution; no corroborating evidence is documented.
- Excerpt: DOCUMENT 1 | Alderwick Herald
A brief unsigned report says that the ferry at Larchport struck a submerged timber. This copy has no attribution field.

DOCUMENT 2 | Briar Ledger
A news note describes a ...

## Interpretive safeguards

- Authors constructed the synthetic references; no independent annotator adjudicated them.
- The support score is elicited, not a calibrated probability.
- Independent-control cases add evidence; their state may legitimately change.
- Bootstrap resamples 39 seeds, not 234 dependent rows.
- Do not call these results historical accuracy or proof of reliability in real OSINT.
