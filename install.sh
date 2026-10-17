#!/usr/bin/env bash
# Install aodd-aisdlc into a Claude Code home (default ~/.claude, override with CLAUDE_HOME).
#   ./install.sh [--dry-run] [--claude-md] [--codex]
# --codex also installs into ${CODEX_HOME:-~/.codex}: skills, agents, hooks, scripts, docs, the two rules
# inlined in AGENTS.md between aodd:begin/aodd:end markers (Codex has no @import), hooks in hooks.json.
# Copies skills, agents, rules, hooks, scripts and docs (not tests, and not scripts/git-hooks, which are for working on this repo); registers the three hooks in settings.json
# (additive, idempotent, fail-open). An existing file that differs is printed as UPDATE and its old
# content is kept next to it as <file>.aodd-bak. Nothing is ever deleted.
set -euo pipefail

DRY=0; CLAUDE_MD=0; CODEX_ON=0
for a in "$@"; do
  case "$a" in
    --dry-run) DRY=1 ;;
    --claude-md) CLAUDE_MD=1 ;;
    --codex) CODEX_ON=1 ;;
    -h|--help) sed -n '2,9p' "$0"; exit 0 ;;
    *) echo "unknown option: $a" >&2; exit 2 ;;
  esac
done

SRC="$(cd "$(dirname "$0")" && pwd)"
DEST="${CLAUDE_HOME:-$HOME/.claude}"
[ "$DRY" = 1 ] && echo "[dry-run] nothing will be written"
echo "install into: $DEST"

copy_file() {  # copy_file <src> <dest>
  local s="$1" d="$2"
  if [ -e "$d" ]; then
    if cmp -s "$s" "$d"; then return 0; fi
    echo "UPDATE  $d (old content kept as $d.aodd-bak)"
    [ "$DRY" = 1 ] || cp "$d" "$d.aodd-bak"
  else
    echo "NEW     $d"
  fi
  [ "$DRY" = 1 ] || { mkdir -p "$(dirname "$d")"; cp "$s" "$d"; if [ -x "$s" ]; then chmod +x "$d"; fi; }
}

copy_tree() {  # copy_tree <relative dir> [dest root]: every file except tests and caches
  local rel="$1" f DEST="${2:-$DEST}"
  [ -d "$SRC/$rel" ] || return 0
  while IFS= read -r f; do
    copy_file "$SRC/$f" "$DEST/$f"
  done < <(cd "$SRC" && find "$rel" -type f ! -name 'test_*.py' ! -name '*.pyc' ! -path '*/__pycache__/*' ! -path '*/git-hooks/*' | sort)
}

for d in skills agents rules hooks scripts docs; do copy_tree "$d"; done

# Register hooks in settings.json / hooks.json (python3 stdlib; refuses to touch an unparsable file)
register_hooks() {  # register_hooks <dest> <settings file name>
DRY="$DRY" DEST="$1" HFILE="$2" python3 - <<'PY'
import json, os, sys
from pathlib import Path

dest = Path(os.environ["DEST"])
dry = os.environ["DRY"] == "1"
settings = dest / os.environ["HFILE"]


def cmd(script, *args):
    f = dest / "hooks" / script
    tail = f" {' '.join(args)}" if args else ""
    return f'f="{f}"; [ -f "$f" ] || exit 0; exec python3 "$f"{tail}'


WANT = [  # (event, matcher, script, args)
    ("PreToolUse", "Bash|Edit|Write|MultiEdit|NotebookEdit|apply_patch", "auditor-readonly.py", ()),
    ("Stop", "*", "skill-capture-nudge.py", ()),
    ("Stop", "*", "done-gate.py", ()),
    ("PostToolUse", "Bash", "skill-capture-nudge.py", ("post",)),
]

try:
    data = json.loads(settings.read_text()) if settings.is_file() else {}
except json.JSONDecodeError as e:
    sys.exit(f"{settings.name} is not valid JSON ({e}); fix it and re-run. Hooks NOT registered.")
if not isinstance(data, dict):
    sys.exit(f"{settings.name} is not a JSON object; hooks NOT registered.")

hooks = data.setdefault("hooks", {})
added = 0
for event, matcher, script, args in WANT:
    groups = hooks.setdefault(event, [])
    command = cmd(script, *args)

    def has(c):  # same script (and same post/non-post mode) already registered under this event
        return script in c and ((c.rstrip().endswith(" post")) == (args == ("post",)))

    if any(has(h.get("command", "")) for g in groups for h in g.get("hooks", [])):
        print(f"hook    {event:<12} {script} {' '.join(args)}: already registered")
        continue
    groups.append({"matcher": matcher, "hooks": [{"type": "command", "command": command}]})
    added += 1
    print(f"hook    {event:<12} {script} {' '.join(args)}: {'would register' if dry else 'registered'}")

if added and not dry:
    if settings.is_file():
        bak = settings.with_name(settings.name + ".aodd-bak")
        if not bak.exists():
            bak.write_text(settings.read_text())
            print(f"backup  {bak}")
    settings.parent.mkdir(parents=True, exist_ok=True)
    settings.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
PY
}
register_hooks "$DEST" settings.json

IMPORT='@rules/aodd.md'
if [ "$CLAUDE_MD" = 1 ]; then
  if [ -f "$DEST/CLAUDE.md" ] && grep -qxF "$IMPORT" "$DEST/CLAUDE.md"; then
    echo "CLAUDE.md already imports $IMPORT"
  else
    echo "APPEND  $DEST/CLAUDE.md <- $IMPORT"
    [ "$DRY" = 1 ] || { mkdir -p "$DEST"; printf '\n%s\n' "$IMPORT" >> "$DEST/CLAUDE.md"; }
  fi
else
  echo "next    add the line '$IMPORT' to $DEST/CLAUDE.md (or re-run with --claude-md) so the AODD contract loads every session"
fi
if [ "$CODEX_ON" = 1 ]; then
  CDEST="${CODEX_HOME:-$HOME/.codex}"
  echo "install into: $CDEST (codex)"
  for d in skills agents hooks scripts docs; do copy_tree "$d" "$CDEST"; done
  register_hooks "$CDEST" hooks.json
  # AGENTS.md: replace the aodd block in place (or append it), so a re-run never duplicates it
  AG="$CDEST/AGENTS.md"
  BLOCK="$(printf '<!-- aodd:begin -->\n'; cat "$SRC/rules/aodd.md"; printf '\n'; cat "$SRC/rules/ai-sdlc-workflow.md"; printf '\n<!-- aodd:end -->\n')"
  if [ "$DRY" = 1 ]; then echo "AGENTS  $AG <- aodd block (would write)"; else
    mkdir -p "$CDEST"
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
fi
echo "state   reports, plans and hook state live under \${AODD_HOME:-~/.aodd} (override: AODD_REPORTS, AODD_STATE, AODD_PLANS)"
echo "done"
