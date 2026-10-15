# EpiTrace - ready-to-record 115-second demonstration (actual results)

**Important:** Do not display an API key or private historical source. This demo uses the completed full runs; every claim below is supported by the saved outputs. Recording/editing remains the participant's task.

**0:00-0:15 - Hook / show title and five-clipping visual.**

> Five newspaper reports can look like five confirmations. But what if all five came from one dispatch - or we simply do not know where they originated? EpiTrace tests whether Apertus preserves that distinction.

**0:15-0:35 - Show `python track_2b/src/show_case.py --seed PUB001` or sample JSONL.**

> We constructed 39 completely fictional news-style cases. Each becomes six controlled evidence conditions: one excerpt, repeated copies, linked syndication, untraceable sources and truly separate firsthand accounts. That is 234 dossiers per model.

**0:35-0:53 - Show `make smoke`, two raw result files and `make replay`.**

> Apertus 8B and 70B each completed all 234 requests through Public AI. The runner records actual served models, prompt and dataset hashes, raw responses and latency. The scorer compares 39 paired seed families rather than treating copies as independent observations.

**0:53-1:25 - Show independence figure and highlight unknown-lineage rows.**

> Both sizes almost always recognized known copies: 8B was correct in 117 of 117 trials, and 70B in 115. But neither returned UNKNOWN on any of the 39 cases where sources could not be traced. Both answered NO, as if a missing source history proved that reports shared an origin.

**1:25-1:43 - Show 105 flags and exact example PUB029.**

> We flagged 105 observations for review, but 78 reflect that single repeated unknown-lineage error. There were two clear 70B mistakes on repeated retractions and three sharp support-score increases even though the evidence had not changed.

**1:43-1:55 - Show summary/limitations.**

> The models are not clearly separated by size. These are synthetic, author-labeled diagnostic examples, not a historical accuracy study. The client is open and can be pointed at a compatible sovereign model endpoint; our actual run used Public AI.

**1:55-2:00 - Closing frame.**

> EpiTrace: do not mistake frequency for independent evidence - and do not mistake unknown provenance for known dependence.

**Screens:** title -> original and variants -> terminal success and replay -> Figure 1 -> 105 flags/PUB029 -> limitation banner -> closing.
