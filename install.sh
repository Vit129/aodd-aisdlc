#!/usr/bin/env bash
# Install aodd-aisdlc into a Claude Code home (default ~/.claude, override with CLAUDE_HOME).
#   ./install.sh [--dry-run] [--claude-md] [--codex] [--with agent-memory,schedules | --all | --core-only] [--yes]
# Core (always): skills, agents, rules, hooks, scripts, docs; hooks registered in settings.json (additive,
# idempotent, fail-open). Optional modules (optional/<name>/): agent-memory, schedules. Asked one by one
# when run in a terminal; --with / --all / --core-only answer for you, --yes asks nothing (default: core only,
# default schedule times). Add a module later by re-running with --with <name>.
# --codex also installs into ${CODEX_HOME:-~/.codex}: the same files, the two rules inlined in AGENTS.md
# between aodd:begin/aodd:end markers (Codex has no @import), hooks in hooks.json.
# An existing file that differs is printed as UPDATE and its old content is kept next to it as
# <file>.aodd-bak. Nothing is ever deleted, host files are never chmod'ed, repo git-hooks are not installed.
# Paths: AODD_* variables you have set in the environment are written to settings.json "env" (unset ones
# stay at their defaults, see hooks/_aodd_paths.py).
set -euo pipefail

DRY=0; CLAUDE_MD=0; CODEX_ON=0; AGY_ON=0; YES=0; MODS_SET=0; MODS=""
ALL_MODULES="agent-memory schedules"
add_mod() { case " $MODS " in *" $1 "*) ;; *) MODS="${MODS:+$MODS }$1" ;; esac; }
while [ $# -gt 0 ]; do
  a="$1"; shift
  case "$a" in
    --dry-run) DRY=1 ;;
    --claude-md) CLAUDE_MD=1 ;;
    --codex) CODEX_ON=1 ;;
    --agy) AGY_ON=1 ;;
    --yes|-y) YES=1 ;;
    --all) MODS_SET=1; for m in $ALL_MODULES; do add_mod "$m"; done ;;
    --core-only) MODS_SET=1 ;;
    --with) [ $# -gt 0 ] || { echo "--with needs a list" >&2; exit 2; }; MODS_SET=1
      for m in $(echo "$1" | tr ',' ' '); do
        case " $ALL_MODULES " in *" $m "*) add_mod "$m" ;; *) echo "unknown module: $m (modules: $ALL_MODULES)" >&2; exit 2 ;; esac
      done; shift ;;
    -h|--help) sed -n '2,15p' "$0"; exit 0 ;;
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

copy_tree() {  # copy_tree <relative dir> [dest root] [source root]: every file except tests and caches
  local rel="$1" f DEST="${2:-$DEST}" SRC="${3:-$SRC}"
  [ -d "$SRC/$rel" ] || return 0
  while IFS= read -r f; do
    copy_file "$SRC/$f" "$DEST/$f"
  done < <(cd "$SRC" && find "$rel" -type f ! -name 'test_*.py' ! -name '*.pyc' ! -path '*/__pycache__/*' ! -path '*/git-hooks/*' | sort)
}

copy_module() {  # copy_module <module> <dest root>: optional/<module>/{skills,agents,rules,hooks,scripts,schedules,docs}
  local d
  for d in skills agents rules hooks scripts schedules docs; do copy_tree "$d" "$2" "$SRC/optional/$1"; done
}

# ---- module choice -------------------------------------------------------------------------------
ask() {  # ask <question>: y/N, default no; --yes never asks
  local r; [ "$YES" = 1 ] && return 1
  read -r -p "$1 [y/N] " r || return 1
  case "$r" in y|Y|yes|YES) return 0 ;; *) return 1 ;; esac
}
if [ "$MODS_SET" = 0 ] && [ "$YES" = 0 ] && [ -t 0 ]; then
  echo "Core installs always. Optional modules (add later with ./install.sh --with <name>):"
  ask "  agent-memory: agents recall past decisions and lessons across sessions and projects. Install?" && add_mod agent-memory
  ask "  schedules: weekly team review, cleanup report and backups run by themselves at times you pick. Install?" && add_mod schedules
elif [ "$MODS_SET" = 0 ] && [ "$YES" = 0 ]; then
  echo "note    not a terminal: installing core only (use --with agent-memory,schedules or --all for modules)"
fi
has_mod() { case " $MODS " in *" $1 "*) return 0 ;; *) return 1 ;; esac; }
echo "modules core${MODS:+ $MODS}"

# schedule times: asked in a terminal, defaults otherwise
SCHED_ARGS=()
if has_mod schedules; then
  SCHED_PY="$SRC/optional/schedules/scripts/install-schedules.py"
  if [ "$YES" = 0 ] && [ "$MODS_SET" = 0 ] && [ -t 0 ]; then
    echo "Schedule times (24h HH:MM, optionally preceded by daily|mon..sun; Enter keeps the default; 'off' skips a job):"
    while IFS=$'\t' read -r -u 3 job def what; do
      [ "$job" = memory-backup ] && ! has_mod agent-memory && continue
      read -r -p "  $job (${what%%:*}) [$def]: " t || t=""
      SCHED_ARGS+=(--set "$job=${t:-$def}")
    done 3< <(python3 "$SRC/optional/schedules/scripts/install-schedules.py" --list)
    printf '  schedule these? [Y/n] '; read -r t || t=""
    case "$t" in n|N|no) SCHED_ARGS=(--only none) ;; esac
  fi
fi

for d in skills agents rules hooks scripts docs; do copy_tree "$d"; done
for m in $MODS; do copy_module "$m" "$DEST"; done

# Register hooks in settings.json / hooks.json (python3 stdlib; refuses to touch an unparsable file)
register_hooks() {  # register_hooks <dest> <settings file name> [write env: 1]
DRY="$DRY" DEST="$1" HFILE="$2" WRITE_ENV="${3:-0}" MODS="$MODS" python3 - <<'PY'
import json, os, sys
from pathlib import Path

dest = Path(os.environ["DEST"])
dry = os.environ["DRY"] == "1"
settings = dest / os.environ["HFILE"]
mods = os.environ["MODS"].split()


def cmd(script, *args):
    f = dest / "hooks" / script
    tail = f" {' '.join(args)}" if args else ""
    return f'f="{f}"; [ -f "$f" ] || exit 0; exec python3 "$f"{tail}'


EDIT = "Edit|Write|MultiEdit|NotebookEdit"
CORE = [  # (event, matcher, script, args)
    ("PreToolUse", "Bash|" + EDIT + "|apply_patch", "auditor-readonly.py", ()),
    ("PreToolUse", "Read|Bash|Edit|Write|MultiEdit", "secret-read-guard.py", ()),
    ("PreToolUse", EDIT + "|Bash", "coding-rules-gate.py", ("pre",)),
    ("PostToolUse", "Read|Bash", "coding-rules-gate.py", ("post",)),
    ("PreToolUse", "Bash", "dirty-branch-switch-guard.py", ()),
    ("PreToolUse", "Bash|Grep|Read|Glob", "graphify-guard.py", ("pre",)),
    ("PostToolUse", "Bash|mcp__graphify__.*", "graphify-guard.py", ("post",)),
    ("Stop", "*", "graphify-guard.py", ("stop",)),
    ("Stop", "*", "skill-capture-nudge.py", ()),
    ("Stop", "*", "done-gate.py", ()),
    ("Stop", "*", "work-log.py", ()),
    ("PostToolUse", "Bash", "skill-capture-nudge.py", ("post",)),
]
MODULE = {
    "agent-memory": [
        ("UserPromptSubmit", "*", "memory-recall.py", ()),
        ("PreToolUse", "Write|Edit", "memory-write-scan.py", ()),
        ("SessionStart", "startup|resume|clear", "session-start-recent.py", ()),
    ],
}
WANT = CORE + [w for m in mods for w in MODULE.get(m, [])]

try:
    data = json.loads(settings.read_text()) if settings.is_file() else {}
except json.JSONDecodeError as e:
    sys.exit(f"{settings.name} is not valid JSON ({e}); fix it and re-run. Hooks NOT registered.")
if not isinstance(data, dict):
    sys.exit(f"{settings.name} is not a JSON object; hooks NOT registered.")


def registered_args(c, script):
    """The arguments a registered command passes to `script`, or None if it is not that script."""
    if script not in c:
        return None
    rest = c.rstrip().rsplit('"$f"', 1)[1] if '"$f"' in c else c.rsplit(script, 1)[1]
    return tuple(rest.replace('"', " ").split())


hooks = data.setdefault("hooks", {})
changed = 0
for event, matcher, script, args in WANT:
    groups = hooks.setdefault(event, [])
    label = f"{script} {' '.join(args)}".strip()
    if any(registered_args(h.get("command", ""), script) == args for g in groups for h in g.get("hooks", [])):
        print(f"hook    {event:<16} {label}: already registered")
        continue
    groups.append({"matcher": matcher, "hooks": [{"type": "command", "command": cmd(script, *args)}]})
    changed += 1
    print(f"hook    {event:<16} {label}: {'would register' if dry else 'registered'}")

# AODD_* paths: written only for variables the user has set; an existing different value is kept
if os.environ["WRITE_ENV"] == "1":
    PATHVARS = ("AODD_HOME", "AODD_REPORTS", "AODD_STATE", "AODD_PLANS", "AODD_WORKLOG", "AODD_MEMORY",
                "AODD_WORKSPACE", "AODD_WORKLOG_SKIP", "AODD_REPOS", "AODD_RECALL_EXTRA", "AODD_DIGEST",
                "AODD_PROJECT_ALIASES", "AODD_REPORT_KINDS", "AODD_AGY_TRANSCRIPTS")
    want = {k: os.environ[k] for k in PATHVARS if os.environ.get(k)}
    env = data.setdefault("env", {}) if want else {}
    for k, v in sorted(want.items()):
        if env.get(k) == v:
            continue
        if k in env:
            print(f"env     {k}: kept {env[k]!r} (you have {v!r} in your shell; edit {settings.name} to change)")
            continue
        env[k] = v
        changed += 1
        print(f"env     {k}={v}: {'would write' if dry else 'written'}")

if changed and not dry:
    if settings.is_file():
        bak = settings.with_name(settings.name + ".aodd-bak")
        if not bak.exists():
            bak.write_text(settings.read_text())
            print(f"backup  {bak}")
    settings.parent.mkdir(parents=True, exist_ok=True)
    settings.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
PY
}
register_hooks "$DEST" settings.json 1

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
  for m in $MODS; do copy_module "$m" "$CDEST"; done
  register_hooks "$CDEST" hooks.json
  # AGENTS.md: replace the aodd block in place (or append it), so a re-run never duplicates it
  AG="$CDEST/AGENTS.md"
  BLOCK="$(printf '<!-- aodd:begin -->\n'; cat "$SRC/rules/aodd.md"; printf '\n'; cat "$SRC/rules/ai-sdlc-workflow.md"; printf '\n<!-- aodd:end -->\n')"
  if [ "$DRY" = 1 ]; then echo "AGENTS  $AG <- aodd block (would write)"; else
    mkdir -p "$CDEST"
    [ -f "$AG" ] && [ ! -e "$AG.aodd-bak" ] && ! grep -q "aodd:begin" "$AG" && cp "$AG" "$AG.aodd-bak" && echo "backup  $AG.aodd-bak"
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
if has_mod schedules; then
  # real install runs the copy in the destination; a dry run (or AODD_SCHEDULES_DRY_RUN=1, for tests) only previews
  SP="$DEST/scripts/install-schedules.py"; SDRY=()
  if [ "$DRY" = 1 ] || [ "${AODD_SCHEDULES_DRY_RUN:-0}" = 1 ]; then SP="$SRC/optional/schedules/scripts/install-schedules.py"; SDRY=(--dry-run); fi
  python3 "$SP" ${SDRY[@]+"${SDRY[@]}"} --modules "${MODS// /,}" ${SCHED_ARGS[@]+"${SCHED_ARGS[@]}"} || echo "warn    schedules were not installed (see above); re-run ./install.sh --with schedules"
fi
if [ "$AGY_ON" = 1 ]; then  # Antigravity: its own installer (skills, agents, AGENTS.md block, hook adapter)
  if [ "$DRY" = 1 ]; then bash "$SRC/install-agy.sh" --dry-run; else bash "$SRC/install-agy.sh"; fi
fi
echo "state   reports, plans and hook state live under \${AODD_HOME:-~/.aodd} (override: AODD_REPORTS, AODD_STATE, AODD_PLANS, AODD_WORKLOG, AODD_MEMORY; see README)"
echo "done"
