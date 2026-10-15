# Build from the repository root.
FROM python:3.12-slim

WORKDIR /app/track_2b

COPY track_2b/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Preserve root files needed by release_check.py.
COPY README.md LICENSE LICENSE-DATA.md LICENSE-DOCS.md MANIFEST.json Makefile /app/

# Preserve the actual project folder structure.
COPY track_2b/ ./

CMD ["sh", "-c", "python src/validate.py && python -m unittest discover -s tests -q && python src/report_results.py --auto --protocol neutral"]
