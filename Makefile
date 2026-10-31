.PHONY: start
.SHELLFLAGS := -e -c

start:
	for t in hooks/test_*.py scripts/test_*.py adapters/test_*.py optional/*/hooks/test_*.py optional/*/scripts/test_*.py; do python3 "$$t"; done
	python3 -m py_compile hooks/*.py scripts/*.py adapters/*.py optional/*/hooks/*.py optional/*/scripts/*.py && bash -n install.sh install-agy.sh
	T=$$(mktemp -d); CLAUDE_HOME=$$T/c AODD_HOME=$$T/a CODEX_HOME=$$T/x ./install.sh --dry-run --all --codex
