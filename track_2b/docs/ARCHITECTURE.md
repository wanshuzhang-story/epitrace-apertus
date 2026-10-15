# Architecture | EpiTrace v0.3

```
39 newly authored fictional seed vignettes (public)
    | deterministic source builder (no API use)
    v
234 dossiers: base / repeat3 / repeat5 / linked5 / unknown5 / independent3
    | validation + SHA256 freeze
    |                                   CSCS / Swiss sovereign deployment
    v                                       +--------------------+
Docker container (Python 3.12) ------------> | Apertus v1.5 8B    |
  prompt builder + JSON parser              | Apertus v1.5 70B   |
  run model IDs independently <------------- | chat/completions   |
    |                                       +--------------------+
    v
Append-only JSONL responses; actual served-model identity + prompt/data hashes
    |
    v
Strict full-run scorer -> 39 paired-seed bootstrap -> case audit CSV + SVG + report
```

**Architecture choice:** **(c) sovereign Swiss cloud**, through Swiss CSCS-hosted Apertus inference. Data for v0.3 are synthetic and contain no personal data; a Swiss-cloud orchestration deployment is feasible when infrastructure is available. On-premise compatible OpenAI API is an alternative, provided served-model IDs are accurately configured. No air-gap capability is claimed for the CSCS API pathway.

**External runtime dependency:** Authorized Apertus inference endpoint and HTTPS networking. The Docker image builds from a Python image and `requests`. Build-time dependencies are distinct from runtime model calls. No separate inference service is running inside Docker.

**Verifiability:** Case IDs stay private to scorer; the prompt never leaks variant or reference labels. API-key material never appears in files committed to Git. Only real verified response files can pass main reporting checks.
