# Offline by default: judges can reproduce completed genuine experiments without a key.
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY src ./src
COPY tests ./tests
COPY data ./data
COPY docs ./docs
COPY results ./results
COPY technical_report.md ./technical_report.md
CMD ["sh", "-c", "python src/validate.py && python -m unittest discover -s tests -q && python src/report_results.py --auto --protocol neutral"]
