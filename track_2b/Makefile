# Hack Apertus Track 2B - run live Docker pipeline or replay actual results.
.PHONY: run smoke test replay audit-results final-pdf
run:
	$(MAKE) -C .. run
smoke:
	python src/validate.py
	python -m unittest discover -s tests -v
	python src/release_check.py
test: smoke
replay:
	python src/report_results.py --auto --protocol neutral
audit-results:
	python src/audit_results_v04.py
final-pdf:
	python src/create_final_pdf.py
