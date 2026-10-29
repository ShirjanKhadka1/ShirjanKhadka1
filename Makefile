.PHONY: verify generate stats screenshots
stats:
	python3 scripts/fetch_stats.py
generate:
	python3 scripts/generate.py
screenshots:
	python3 scripts/screenshot.py
verify:
	python3 scripts/verify.py
	python3 scripts/screenshot.py
