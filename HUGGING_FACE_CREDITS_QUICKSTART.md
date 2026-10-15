# EpiTrace v0.3.3 - Hack Apertus Hugging Face voucher is OPTIONAL

**Preferred time-critical route:** Read `PUBLICAI_START_HERE.md` and use the verified direct Public AI starter credit. The official Notion voucher guide link currently returns 404 and no activation method has been verified.

**Competition deadline:** 16 October 2026 at 12:00 CEST (Luxembourg time).

## 1. Confirm credit eligibility before running

The official Devpost resources page promises **$10 Hugging Face credits for each hacker**, but the eligibility, activation/redemption instructions, supported service categories and account-specific balance must be checked in the hackathon Getting Started guide and your HF billing settings. The linked Notion Getting Started page was inaccessible to our independent checker on 14 October, so do **not** assume the credit is already active. Ask in the hackathon Discord if the guide is unavailable. The live Hugging Face Inference Providers pricing documentation now lists **no included inference credit for Free users**; this is separate from the unverified $10 hackathon promotion. Do not assume a model repository means a model is deployed for paid inference.

- Resources: https://hackapertus.devpost.com/resources
- Discord: https://discord.com/invite/hack-apertus
- Hugging Face Inference billing: https://huggingface.co/settings/billing
- HF inference models: https://huggingface.co/inference/models
- HF provider pricing: https://huggingface.co/docs/inference-providers/pricing
- API token page: https://huggingface.co/settings/tokens

For this experiment choose **Hugging Face-routed inference**. **Do not configure a custom provider API key in HF settings**, because that bills the external provider and bypasses HF credits. Confirm the $10 voucher is valid for routed Inference Providers rather than only GPU endpoints or other services.

## 2. Token with minimum necessary permission

Create a fine-grained HF token with **Make calls to Inference Providers** permission. Accept official Apertus model access/usage terms on the 8B and 70B model pages if prompted. Keep token entirely on your machine. Never paste it into ChatGPT, demo scripts, source code or GitHub.

## 3. Inspect model availability and pricing

The public HF Inference Providers catalog has listed both models through Public AI, even though the 8B model card has intermittently said it has no deployed provider. Provider availability is dynamic: the live API preflight and three-case pilots are the deciding checks.

Model requests are pinned as:

- `swiss-ai/Apertus-v1.5-8B:publicai`
- `swiss-ai/Apertus-v1.5-70B:publicai`

The Hugging Face backend selector is **not** part of the canonical model ID. A response identifying `swiss-ai/Apertus-v1.5-8B` to the request ending `:publicai` is normal; a response identifying 70B when 8B was requested is not. Backend selection is a request-level provenance assertion; it does not attest Swiss data residency. Running 8B and 70B through different backend providers is rejected for paired inference comparison. If HF does not advertise both models via the same provider, use Public AI directly for both or clearly report a single-model evaluation. Do not silently switch the provider of just one run.

If `GET /v1/models` says provider offline/absent, DO NOT launch the full run. Contact the hackathon support channel and/or use the direct Public AI route in `PUBLICAI_QUICKSTART.md` with its separate billing. Do not attempt to run 70B on a normal laptop or treat the HF model repo as a serverless endpoint.

## 4. Run locally

From the project ROOT, with Docker Desktop running:

```sh
make smoke
cp track_2b/.env.huggingface.example track_2b/.env.huggingface
# Edit track_2b/.env.huggingface to insert your actual HF token.
make pilot-hf-8b
make pilot-hf-70b
```

**Only after both pilots succeed** (3/3 successful actual model responses per model):

```sh
make run-hf-both
make report
```

`make run-hf-both` issues 234 requests per model (468 total, plus six pilot requests). It resumes already-completed cases. The runners record the canonical served model ID, pinned backend, prompt/data fingerprints, outputs and token counts. The public ZIP contains **zero** actual Apertus responses. The report exporter refuses incomplete 234-case runs; the six pilot predictions are never misrepresented as a full evaluation.

### Cost indication

Published HF Public AI listed rates: 8B $0.10 input/$0.20 output per 1M tokens; 70B $0.82 input/$2.92 output per 1M tokens (check live pricing and credit coverage). If each request were 2,000 input and 350 output tokens, 234 requests/model would cost about **$0.06 for 8B + $0.62 for 70B**, so $10 seems ample. This is **only an illustrative token budget**, not a measured cost or guaranteed bill. Budget can rise with retries, alternate pricing, or a provider not accepting the requested model.

### Critical research limitations

- 39 original, fictional source vignettes. Their reference judgments are authored, not independent historical/human gold. No historical accuracy claim can be inferred.
- No model test is completed by `make smoke`; its mock HTTP transport test is explicitly NOT a model result.
- If you change the prompt or dataset, rerun both models: hashes intentionally prevent mixed comparisons.
- Comparisons are paired over **39 seeds**, not 234 independent participants/observations.
- Hugging Face routing is not evidence of sovereign Switzerland-hosted processing. The open Apertus weights still permit sovereign deployment, but that is a different claim.
