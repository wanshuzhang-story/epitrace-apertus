IMAGE ?= epitrace-apertus-v05
ENV_FILE ?= track_2b/.env
MODEL ?= swiss-ai/Apertus-v1.5-8B
.PHONY: run run-live run-8b run-70b run-both run-hf-8b run-hf-70b run-hf-both pilot-hf-8b pilot-hf-70b run-publicai-8b run-publicai-70b run-publicai-both build-image validate test smoke build-data report final-pdf

build-image:
	docker build -f track_2b/Dockerfile -t $(IMAGE) .

# Contest-default entry point: Docker replay of the 468 SAVED genuine responses.
# No credentials or new inference charges. The container validates the dataset,
# checks the saved records and regenerates the full comparative report.
run: build-image
	docker run --rm \
	  -v "$(abspath track_2b/results):/app/track_2b/results" $(IMAGE)

# Explicit opt-in: new live inference, consuming authorized provider credits.
# Do not call for reproducibility; 'make run' already replays genuine outputs.
run-live: build-image
	@if [ -f "$(ENV_FILE)" ]; then \
	  docker run --rm --env-file "$(abspath $(ENV_FILE))" -e LLM_NAME="$(MODEL)" \
	  -v "$(abspath track_2b/results):/app/track_2b/results" $(IMAGE) \
	  python src/run_benchmark.py; \
	else \
	  docker run --rm -e LLM_NAME="$(MODEL)" -e LLM_API_KEY -e CSCS_INFERENCE_API_KEY -e LLM_BASE_URL \
	  -v "$(abspath track_2b/results):/app/track_2b/results" $(IMAGE) \
	  python src/run_benchmark.py; \
	fi

run-8b:
	$(MAKE) run-live MODEL=swiss-ai/Apertus-v1.5-8B

run-70b:
	$(MAKE) run-live MODEL=swiss-ai/Apertus-v1.5-70B

run-both: run-8b run-70b

# Public AI uses lower-case model IDs and an independent self-service key.
run-publicai-8b:
	@test -f track_2b/.env.publicai || (echo "Create track_2b/.env.publicai from .env.publicai.example first"; exit 2)
	$(MAKE) run-live MODEL=swiss-ai/apertus-v1.5-8b ENV_FILE=track_2b/.env.publicai

run-publicai-70b:
	@test -f track_2b/.env.publicai || (echo "Create track_2b/.env.publicai from .env.publicai.example first"; exit 2)
	$(MAKE) run-live MODEL=swiss-ai/apertus-v1.5-70b ENV_FILE=track_2b/.env.publicai

run-publicai-both: run-publicai-8b run-publicai-70b

# HF Inference Providers: use hackathon credits through HF billing.
# Ensure track_2b/.env.huggingface contains your own token and no custom provider key is configured in HF settings.
run-hf-8b:
	@test -f track_2b/.env.huggingface || (echo "Copy .env.huggingface.example to .env.huggingface, insert HF API token"; exit 2)
	$(MAKE) run-live MODEL=swiss-ai/Apertus-v1.5-8B:publicai ENV_FILE=track_2b/.env.huggingface

run-hf-70b:
	@test -f track_2b/.env.huggingface || (echo "Copy .env.huggingface.example to .env.huggingface, insert HF API token"; exit 2)
	$(MAKE) run-live MODEL=swiss-ai/Apertus-v1.5-70B:publicai ENV_FILE=track_2b/.env.huggingface

# Each pilot makes three *real* API requests, saved outside full-run discovery.
pilot-hf-8b: build-image
	@test -f track_2b/.env.huggingface || (echo "Create track_2b/.env.huggingface first"; exit 2)
	docker run --rm --env-file "$(abspath track_2b/.env.huggingface)" \
	  -v "$(abspath track_2b/results):/app/track_2b/results" $(IMAGE) \
	  python src/run_benchmark.py --model swiss-ai/Apertus-v1.5-8B:publicai \
	  --limit 3 --max-attempts 1 --out results/PILOT_HF_8B.jsonl

pilot-hf-70b: build-image
	@test -f track_2b/.env.huggingface || (echo "Create track_2b/.env.huggingface first"; exit 2)
	docker run --rm --env-file "$(abspath track_2b/.env.huggingface)" \
	  -v "$(abspath track_2b/results):/app/track_2b/results" $(IMAGE) \
	  python src/run_benchmark.py --model swiss-ai/Apertus-v1.5-70B:publicai \
	  --limit 3 --max-attempts 1 --out results/PILOT_HF_70B.jsonl

run-hf-both: run-hf-8b run-hf-70b

build-data:
	cd track_2b && python src/build_dataset.py

validate:
	python track_2b/src/validate.py --data track_2b/data/epitrace_benchmark_public_v0.3.jsonl --seeds track_2b/data/epitrace_seeds_public_v0.3.jsonl

test:
	cd track_2b && python -m unittest discover -s tests -v

smoke: validate test
	python track_2b/src/release_check.py

report:
	cd track_2b && python src/report_results.py --auto --protocol neutral

# Recalculate the published experiment (468 existing records) without any API key.
replay:
	cd track_2b && python src/report_results.py --auto --protocol neutral

# Re-create secondary audit, grouped CSVs, and plots. matplotlib is required.
audit-results:
	cd track_2b && python src/audit_results_v04.py

# Generate the updated 5-body-page + references competition report from verified data.
final-pdf:
	cd track_2b && python src/create_final_pdf.py
