#!/usr/bin/env python3
"""Measure whether a model opens a model-invoked skill on its own.

Each case is a request phrased the way a user really types it, never copied from the skill's
description (tuning a description against the same sentences it is tested on overfits: it scores
well on those and still misses new phrasings). Every case runs in a fresh, one-turn session, so no
earlier pick is remembered. A skill opened in under half of its runs should become user-invoked
(`disable-model-invocation: true`) or get a description rewritten from new, unseen cases.

Usage: skill_trigger_eval.py cases.json [--rounds N] [--model haiku]
cases.json: {"<skill-name>": ["request 1", "request 2", ...], ...}  (5 or more per skill)
AODD_TRIGGER_CMD overrides the CLI (tests point it at a stub); the prompt is appended as the last argument.
"""
import argparse, json, os, re, shlex, subprocess, sys

THRESHOLD = 0.5


def cli(model):
    if os.environ.get("AODD_TRIGGER_CMD"):
        return shlex.split(os.environ["AODD_TRIGGER_CMD"])
    return ["claude", "-p", "--model", model, "--output-format", "stream-json", "--verbose", "--max-turns", "1"]


def skills_opened(stream):
    """Skill names the session called through the Skill tool, from stream-json output."""
    found = set()
    for line in stream.splitlines():
        try:
            ev = json.loads(line)
        except ValueError:
            continue
        content = (ev.get("message") or {}).get("content") if isinstance(ev, dict) else None
        for item in content if isinstance(content, list) else []:
            if isinstance(item, dict) and item.get("type") == "tool_use" and item.get("name") == "Skill":
                found.add(str((item.get("input") or {}).get("skill", "")))
    return found


def opened(skill, names):
    # Plugin skills come back as "<plugin>:<skill>".
    return any(n == skill or n.endswith(":" + skill) for n in names)


def leaks(skill, prompt):
    return re.search(re.escape(skill), prompt, re.I) is not None


def run(cases, rounds=1, model="haiku"):
    cmd, res = cli(model), {}
    for skill, prompts in cases.items():
        r = res[skill] = {"hits": 0, "runs": 0, "missed": [], "leaked": [p for p in prompts if leaks(skill, p)]}
        for _ in range(rounds):
            for p in prompts:
                try:
                    out = subprocess.run([*cmd, p], capture_output=True, text=True, stdin=subprocess.DEVNULL, timeout=300).stdout
                except (OSError, subprocess.TimeoutExpired) as exc:
                    out = ""
                    print(f"warning: {skill}: {exc}", file=sys.stderr)
                r["runs"] += 1
                if opened(skill, skills_opened(out)):
                    r["hits"] += 1
                elif p not in r["missed"]:
                    r["missed"].append(p)
    return res


def report(res):
    lines = ["| Skill | Opened | Verdict |", "|---|---|---|"]
    for skill, r in sorted(res.items()):
        rate = r["hits"] / r["runs"] if r["runs"] else 0
        verdict = "ok" if rate >= THRESHOLD else "under half: make it user-invoked, or rewrite the description and re-test on new cases"
        lines.append(f"| {skill} | {r['hits']}/{r['runs']} | {verdict} |")
    for skill, r in sorted(res.items()):
        if r["leaked"]:
            lines.append(f"\n{skill}: cases that name the skill do not measure the description: {r['leaked']}")
        if r["missed"]:
            lines.append(f"\n{skill} missed: " + "; ".join(r["missed"]))
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cases")
    ap.add_argument("--rounds", type=int, default=1)
    ap.add_argument("--model", default="haiku")
    a = ap.parse_args()
    with open(a.cases, encoding="utf-8") as f:
        print(report(run(json.load(f), a.rounds, a.model)))


if __name__ == "__main__":
    main()
