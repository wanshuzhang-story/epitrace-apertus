# Public AI access (verified 14 October 2026)

**The fastest route is `PUBLICAI_START_HERE.md` in the repository root.** This does not require a CSCS allocation, Hugging Face voucher or local Docker installation to perform the model benchmark.

The direct provider says new accounts get $2 starter credit at https://platform.publicai.co/docs, and both models appear at https://platform.publicai.co/models. After signup, check your account billing. In the extracted repository run:

```sh
python3 -m pip install -r track_2b/requirements.txt
python3 publicai_faststart.py setup
python3 publicai_faststart.py pilot
python3 publicai_faststart.py full
python3 publicai_faststart.py report
```

`setup` saves the key only in the local gitignored `.env.publicai` file, not in the published ZIP or chat. The script checks served-model identity and requires 3 successful pilots per model before a full run. The official Docker command `make run` is preserved for competition evaluation; the fast path changes no dataset or prompts.

API identities (different from CSCS and HF router): `swiss-ai/apertus-v1.5-8b` and `swiss-ai/apertus-v1.5-70b`.

Actual credit and model availability need confirmation in your own account. Do not claim an inference result until it exists and passes validation.
