#!/usr/bin/env bash
# Install aodd-aisdlc into an Antigravity environment (default ~/.gemini/antigravity-cli, override with AGY_HOME).
#   ./install-agy.sh [--dry-run]
# Copies skills, agents, and adapters; writes AODD rules into the Antigravity instruction file
# (AGENTS.md) between <!-- aodd:begin --> and <!-- aodd:end --> markers; registers the lifecycle hook
# adapter in Antigravity's config/hooks.json (additive, idempotent, fail-open).
# An existing file that differs is printed as UPDATE and its old content is kept next to it as <file>.aodd-bak.
# Nothing is ever deleted. Never chmods files it did not install.
set -euo pipefail

DRY=0
for a in "$@"; do
  case "$a" in
    --dry-run) DRY=1 ;;
    -h|--help) sed -n '2,9p' "$0"; exit 0 ;;
    *) echo "unknown option: $a" >&2; exit 2 ;;
  esac
done

SRC="$(cd "$(dirname "$0")" && pwd)"
AGY_HOME="${AGY_HOME:-$HOME/.gemini/antigravity-cli}"

if [ -n "${GEMINI_HOME:-}" ]; then
  GEMINI_DIR="$GEMINI_HOME"
elif [ -f "$AGY_HOME/AGENTS.md" ] || [ -f "$AGY_HOME/GEMINI.md" ] || [ -f "$AGY_HOME/config/hooks.json" ]; then
  GEMINI_DIR="$AGY_HOME"
elif [ "$(basename "$AGY_HOME")" = "antigravity-cli" ]; then
  GEMINI_DIR="$(dirname "$AGY_HOME")"
elif [ -f "$(dirname "$AGY_HOME")/AGENTS.md" ] || [ -f "$(dirname "$AGY_HOME")/GEMINI.md" ] || [ -f "$(dirname "$AGY_HOME")/config/hooks.json" ]; then
  GEMINI_DIR="$(dirname "$AGY_HOME")"
else
  GEMINI_DIR="$(dirname "$AGY_HOME")"
fi

if [ -f "$GEMINI_DIR/GEMINI.md" ] && [ ! -f "$GEMINI_DIR/AGENTS.md" ]; then
  AG="$GEMINI_DIR/GEMINI.md"
else
  AG="$GEMINI_DIR/AGENTS.md"
fi

HFILE="$GEMINI_DIR/config/hooks.json"

[ "$DRY" = 1 ] && echo "[dry-run] nothing will be written"
echo "install into: $AGY_HOME (agy)"
echo "instruction file: $AG"
echo "hooks config: $HFILE"

copy_file() {  # copy_file <src> <dest>
  local s="$1" d="$2"
  if [ -e "$d" ]; then
    if cmp -s "$s" "$d"; then return 0; fi
    echo "UPDATE  $d (old content kept as $d.aodd-bak)"
    [ "$DRY" = 1 ] || { [ -e "$d.aodd-bak" ] || cp "$d" "$d.aodd-bak"; }
  else
    echo "NEW     $d"
  fi
  [ "$DRY" = 1 ] || { mkdir -p "$(dirname "$d")"; cp "$s" "$d"; if [ -x "$s" ]; then chmod +x "$d"; fi; }
}

copy_tree() {  # copy_tree <relative dir> [dest root]: every file except tests and caches
  local rel="$1" f DEST="${2:-$AGY_HOME}"
  [ -d "$SRC/$rel" ] || return 0
  while IFS= read -r f; do
    copy_file "$SRC/$f" "$DEST/$f"
  done < <(cd "$SRC" && find "$rel" -type f ! -name 'test_*.py' ! -name '*.pyc' ! -path '*/__pycache__/*' ! -path '*/git-hooks/*' | sort)
}

for d in skills agents adapters; do copy_tree "$d"; done

# Instruction file (AGENTS.md / GEMINI.md)
BLOCK="$(printf '<!-- aodd:begin -->\n'; cat "$SRC/rules/aodd.md"; printf '\n'; cat "$SRC/rules/ai-sdlc-workflow.md"; printf '\n<!-- aodd:end -->\n')"
if [ "$DRY" = 1 ]; then
  echo "AGENTS  $AG <- aodd block (would write)"
else
  mkdir -p "$GEMINI_DIR"
  [ -f "$AG" ] && [ ! -e "$AG.aodd-bak" ] && cp "$AG" "$AG.aodd-bak" && echo "backup  $AG.aodd-bak"
  AG="$AG" BLOCK="$BLOCK" python3 - <<'PY'
import os, re
from pathlib import Path

f, block = Path(os.environ["AG"]), os.environ["BLOCK"].rstrip("\n") + "\n"
old = f.read_text() if f.is_file() else ""
pat = re.compile(r"<!-- aodd:begin -->.*?<!-- aodd:end -->\n?", re.S)
new = pat.sub(lambda _: block, old) if pat.search(old) else (old + ("\n" if old and not old.endswith("\n\n") else "") + block)
if new != old:
    f.write_text(new)
    print(f"AGENTS  {f} <- aodd block")
else:
    print(f"AGENTS  {f}: aodd block up to date")
PY
fi

# Hooks config (config/hooks.json)
ADAPTER_PATH="$AGY_HOME/adapters/antigravity-hook-adapter.py"
register_hooks() {
  DRY="$DRY" HFILE="$HFILE" ADAPTER_PATH="$ADAPTER_PATH" python3 - <<'PY'
import json, os, sys
from pathlib import Path

hfile = Path(os.environ["HFILE"])
adapter = os.environ["ADAPTER_PATH"]
dry = os.environ["DRY"] == "1"

want_block = {
    "PreToolUse": [
        {
            "matcher": "run_command|view_file|write_to_file|replace_file_content",
            "hooks": [
                {
                    "type": "command",
                    "command": f'python3 "{adapter}" pre' if " " in adapter else f'python3 {adapter} pre',
                    "timeout": 10
                }
            ]
        }
    ],
    "PostToolUse": [
        {
            "matcher": "run_command|view_file",
            "hooks": [
                {
                    "type": "command",
                    "command": f'python3 "{adapter}" post' if " " in adapter else f'python3 {adapter} post',
                    "timeout": 10
                }
            ]
        }
    ],
    "Stop": [
        {
            "type": "command",
            "command": f'python3 "{adapter}" stop' if " " in adapter else f'python3 {adapter} stop',
            "timeout": 10
        }
    ]
}

try:
    data = json.loads(hfile.read_text()) if hfile.is_file() else {}
except json.JSONDecodeError as e:
    sys.exit(f"{hfile.name} is not valid JSON ({e}); fix it and re-run. Hooks NOT registered.")
if not isinstance(data, dict):
    sys.exit(f"{hfile.name} is not a JSON object; hooks NOT registered.")

current = data.get("aodd-guardrails")
if current == want_block:
    print(f"hook    aodd-guardrails: already registered in {hfile}")
else:
    print(f"hook    PreToolUse   {adapter} pre: {'would register' if dry else 'registered'}")
    print(f"hook    PostToolUse  {adapter} post: {'would register' if dry else 'registered'}")
    print(f"hook    Stop         {adapter} stop: {'would register' if dry else 'registered'}")
    if not dry:
        if hfile.is_file():
            bak = hfile.with_name(hfile.name + ".aodd-bak")
            if not bak.exists():
                bak.write_text(hfile.read_text())
                print(f"backup  {bak}")
        hfile.parent.mkdir(parents=True, exist_ok=True)
        data["aodd-guardrails"] = want_block
        hfile.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
PY
}
register_hooks

echo "state   reports, plans and hook state live under \${AODD_HOME:-~/.aodd} (override: AODD_REPORTS, AODD_STATE, AODD_PLANS)"
echo "done"
