.PHONY: help lint push-both push-all doc-sync doc-dry

help:
	@echo "Targets:"
	@echo "  lint       - Run Ren'Py lint"
	@echo "  push-both  - Push current branch and tags to all origin push URLs"
	@echo "  push-all   - Push all branches and tags"
	@echo "  doc-sync   - Sync Doc/ to GitHub wiki"
	@echo "  doc-dry    - Dry-run doc sync"

lint:
	@~/renpy-8.4.1-sdk/renpy.sh . lint

push-both:
	@bash scripts/push-both.sh

push-all:
	@bash scripts/push-both.sh all

doc-sync:
	@bash scripts/sync-github-doc.sh

doc-dry:
	@bash scripts/sync-github-doc.sh dry-run
