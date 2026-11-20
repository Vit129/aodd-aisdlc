.PHONY: start check preview patch minor major
.SHELLFLAGS := -e -c
ifneq ($(origin msg), undefined)
export COMMIT_MESSAGE := $(msg)
endif

ifneq ($(word 2,$(filter patch minor major,$(MAKECMDGOALS))),)
$(error Choose only one of patch, minor, or major)
endif

# Non-interactive callers keep the existing test entrypoint. A release choice is explicit.
start:
	@if [ -n "$(filter patch minor major,$(MAKECMDGOALS))" ]; then :; \
	elif [ -t 0 ]; then \
	  printf '1) check\n2) patch\n3) minor\n4) major\nChoose: '; read choice; \
	  case "$$choice" in 1) $(MAKE) check ;; 2) $(MAKE) patch ;; 3) $(MAKE) minor ;; 4) $(MAKE) major ;; *) echo 'Invalid choice' >&2; exit 2 ;; esac; \
	else $(MAKE) check; fi

check:
	for t in hooks/test_*.py scripts/test_*.py adapters/test_*.py optional/*/hooks/test_*.py optional/*/scripts/test_*.py; do python3 "$$t" || exit 1; done
	python3 -m py_compile hooks/*.py scripts/*.py adapters/*.py optional/*/hooks/*.py optional/*/scripts/*.py && bash -n install.sh install-agy.sh
	T=$$(mktemp -d); CLAUDE_HOME=$$T/c AODD_HOME=$$T/a CODEX_HOME=$$T/x ./install.sh --dry-run --all --codex

patch minor major:
	python3 scripts/release.py $@

# Local preview: the installer's dry run. Writes nothing outside .tmp/ (gitignored).
preview:
	mkdir -p .tmp && T=$$(mktemp -d "$$PWD/.tmp/preview.XXXX"); CLAUDE_HOME=$$T/c AODD_HOME=$$T/a CODEX_HOME=$$T/x ./install.sh --dry-run --all --codex
