import importlib.util
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

spec = importlib.util.spec_from_file_location(
    "antigravity_hook_adapter",
    ROOT / "adapters" / "antigravity-hook-adapter.py"
)
adapter = importlib.util.module_from_spec(spec)
spec.loader.exec_module(adapter)

T = Path(tempfile.mkdtemp())
os.environ["AODD_HOME"] = str(T / "aodd")
for _k in ("AODD_REPORTS", "AODD_STATE", "AODD_PLANS", "CLAUDE_SKILL_CAPTURE", "AODD_AUDITOR", "DONE_GATE_AUDIT", "DONE_GATE_ITEMS"):
    os.environ.pop(_k, None)


# 1. Fails open when hooks are missing
def test_fails_open_when_missing():
    empty_dir = T / "empty_hooks"
    empty_dir.mkdir(parents=True, exist_ok=True)
    os.environ["AODD_HOOKS_DIR"] = str(empty_dir)

    # PreToolUse allows
    res_pre = adapter.handle_pre({
        "toolCall": {"name": "run_command", "args": {"CommandLine": "rm -rf foo"}}
    })
    assert res_pre == {"decision": "allow"}, f"expected allow, got {res_pre}"

    # PostToolUse returns empty
    res_post = adapter.handle_post({
        "toolCall": {"name": "run_command", "args": {"CommandLine": "echo 1"}}
    })
    assert res_post == {}, f"expected empty dict, got {res_post}"

    # Stop allows
    res_stop = adapter.handle_stop({
        "session_id": "missing-hook-session",
        "transcript_path": str(T / "nonexistent.jsonl"),
    })
    assert res_stop == {"decision": "allow"}, f"expected allow, got {res_stop}"


# 2. Calls done-gate on Antigravity transcript
def test_done_gate_integration():
    os.environ["AODD_HOOKS_DIR"] = str(ROOT / "hooks")

    work_dir = T / "proj"
    work_dir.mkdir(parents=True, exist_ok=True)
    prog_file = work_dir / "ai-sdlc-task-progress.md"
    prog_file.write_text("- [x] task one\n- [ ] task two\n")

    tr_file = T / "transcript_dg.jsonl"
    r1 = {"type": "USER_INPUT", "content": "implement feature"}
    r2 = {
        "type": "PLANNER_RESPONSE",
        "tool_calls": [
            {
                "name": "write_to_file",
                "args": {"TargetFile": str(prog_file), "CodeContent": "- [x] task one\n- [ ] task two\n"}
            }
        ]
    }
    tr_file.write_text(json.dumps(r1) + "\n" + json.dumps(r2) + "\n")

    payload = {
        "conversationId": "dg-sess-1",
        "transcriptPath": str(tr_file),
        "workspacePaths": [str(work_dir)],
    }
    res = adapter.handle_stop(payload)
    assert res.get("decision") == "allow", f"a Stop is never blocked, got {res}"
    assert "- [ ] task two" in res.get("systemMessage", ""), res
    assert "reason" not in res

    # When all progress items checked but not audited -> allowed, audit is on demand
    prog_file.write_text("- [x] task one\n- [x] task two\n")
    res_aud = adapter.handle_stop(payload)
    assert res_aud == {"decision": "allow"}, f"expected a plain allow, got {res_aud}"


# 3. Calls skill-capture-nudge on Antigravity transcript
def test_skill_capture_integration():
    os.environ["AODD_HOOKS_DIR"] = str(ROOT / "hooks")

    tr_file = T / "transcript_sc.jsonl"
    records = []
    # User correction signal
    records.append(json.dumps({"type": "USER_INPUT", "content": "that is wrong, do not do it that way"}))
    # 21 tool calls
    for i in range(21):
        records.append(json.dumps({
            "type": "PLANNER_RESPONSE",
            "tool_calls": [
                {
                    "name": "run_command",
                    "args": {"CommandLine": f"echo step {i}"}
                }
            ]
        }))
    tr_file.write_text("\n".join(records) + "\n")

    payload = {
        "conversationId": "sc-sess-1",
        "transcriptPath": str(tr_file),
        "workspacePaths": [str(T / "proj")],
    }
    res = adapter.handle_stop(payload)
    assert res.get("decision") == "allow", f"a Stop is never blocked, got {res}"
    assert "[skill-capture]" in res.get("systemMessage", "")
    assert "user correction" in res.get("systemMessage", "")
    assert adapter.handle_stop(payload) == {"decision": "allow"}, "said once per session"


# 4. Calls auditor-readonly on PreToolUse
def test_auditor_readonly_integration():
    os.environ["AODD_HOOKS_DIR"] = str(ROOT / "hooks")
    os.environ["AODD_AUDITOR"] = "1"

    # write_to_file denied
    res_write = adapter.handle_pre({
        "toolCall": {
            "name": "write_to_file",
            "args": {"TargetFile": str(T / "out.txt"), "CodeContent": "content"}
        }
    })
    assert res_write.get("decision") == "deny", f"expected deny, got {res_write}"
    assert "auditor is read-only" in res_write.get("reason", "")

    # Bash write denied
    res_bash = adapter.handle_pre({
        "toolCall": {
            "name": "run_command",
            "args": {"CommandLine": "rm -rf foo"}
        }
    })
    assert res_bash.get("decision") == "deny", f"expected deny, got {res_bash}"

    # Read-only Bash allowed
    res_read = adapter.handle_pre({
        "toolCall": {
            "name": "run_command",
            "args": {"CommandLine": "git status"}
        }
    })
    assert res_read.get("decision") == "allow", f"expected allow, got {res_read}"

    os.environ.pop("AODD_AUDITOR", None)


# 5. install-agy.sh: --dry-run, real run, and idempotent second run
def test_install_agy():
    temp_agy = T / "gemini" / "antigravity-cli"
    temp_claude = T / "claude"
    temp_gemini = T / "gemini"

    install_env = {
        **{k: v for k, v in os.environ.items() if k != "AODD_NO_BACKUP"},  # a caller's switch must not skip the backup this test checks
        "AGY_HOME": str(temp_agy),
        "CLAUDE_HOME": str(temp_claude),
    }

    # 5a. --dry-run writes nothing
    p_dry = subprocess.run(
        ["bash", str(ROOT / "install-agy.sh"), "--dry-run"],
        capture_output=True,
        text=True,
        env=install_env,
    )
    assert p_dry.returncode == 0, p_dry.stderr
    assert "[dry-run]" in p_dry.stdout
    assert not temp_agy.exists(), "dry-run must not create AGY_HOME"
    assert not (temp_gemini / "AGENTS.md").exists(), "dry-run must not create AGENTS.md"

    # 5b. Pre-create host files to check backup and non-destructive updates
    temp_gemini.mkdir(parents=True, exist_ok=True)
    (temp_gemini / "AGENTS.md").write_text("# Existing Host Instructions\n")
    (temp_gemini / "GEMINI.md").write_text("# Keep\n<!-- aodd:begin -->\nstale\n<!-- aodd:end -->\n# Keep too\n")
    (temp_gemini / "config").mkdir(parents=True, exist_ok=True)
    (temp_gemini / "config" / "hooks.json").write_text(json.dumps({"existing_suite": {"Stop": []}}))
    host_file = temp_gemini / "custom-script.sh"
    host_file.write_text("echo host")
    host_file.chmod(0o644)

    # Real run
    p_real = subprocess.run(
        ["bash", str(ROOT / "install-agy.sh")],
        capture_output=True,
        text=True,
        env=install_env,
    )
    assert p_real.returncode == 0, p_real.stderr

    assert (temp_gemini / "GEMINI.md").read_text() == "# Keep\n# Keep too\n"
    assert "stale" in (temp_gemini / "GEMINI.md.aodd-bak").read_text()

    # Check installed artifacts
    assert (temp_agy / "skills" / "chief-of-staff" / "SKILL.md").is_file()
    for ref in ("bug-hunt.md", "incident-record.md", "course-check.md"):
        assert (temp_agy / "skills" / "ai-sdlc" / "references" / ref).is_file()
    assert (temp_agy / "agents" / "auditor.md").is_file()
    assert (temp_agy / "adapters" / "antigravity-hook-adapter.py").is_file()
    assert os.access(temp_agy / "adapters" / "antigravity-hook-adapter.py", os.X_OK)

    # Check instruction file
    ag_text = (temp_gemini / "AGENTS.md").read_text()
    assert ag_text.startswith("# Existing Host Instructions\n")
    assert ag_text.count("<!-- aodd:begin -->") == 1
    assert ag_text.count("<!-- aodd:end -->") == 1
    assert (temp_gemini / "AGENTS.md.aodd-bak").read_text() == "# Existing Host Instructions\n"

    # Check hooks.json
    hooks_cfg = json.loads((temp_gemini / "config" / "hooks.json").read_text())
    assert "existing_suite" in hooks_cfg
    assert "aodd-guardrails" in hooks_cfg
    assert set(hooks_cfg["aodd-guardrails"].keys()) == {"PreToolUse", "PostToolUse", "Stop"}
    assert (temp_gemini / "config" / "hooks.json.aodd-bak").is_file()

    # Host file untouched and not chmodded
    assert (host_file.stat().st_mode & 0o777) == 0o644, "must not chmod host files"

    # 5c. Second run changes nothing
    ag_before = (temp_gemini / "AGENTS.md").read_text()
    hooks_before = (temp_gemini / "config" / "hooks.json").read_text()
    stat_adapter = (temp_agy / "adapters" / "antigravity-hook-adapter.py").stat()

    p_second = subprocess.run(
        ["bash", str(ROOT / "install-agy.sh")],
        capture_output=True,
        text=True,
        env=install_env,
    )
    assert p_second.returncode == 0, p_second.stderr
    assert (temp_gemini / "AGENTS.md").read_text() == ag_before
    assert (temp_gemini / "config" / "hooks.json").read_text() == hooks_before
    assert (temp_agy / "adapters" / "antigravity-hook-adapter.py").stat().st_mtime == stat_adapter.st_mtime


def test_advice_hooks_never_deny():
    """coding-rules-gate, dirty-branch-switch-guard and search-guard give advice, never a deny."""
    os.environ["AODD_HOOKS_DIR"] = str(ROOT / "hooks")
    os.environ["AODD_STATE"] = str(T / "state-advice")
    os.environ["CODING_RULES_GATE_STATE"] = str(T / "crg-state")
    rules_home = T / "claude-advice"
    (rules_home / "rules").mkdir(parents=True, exist_ok=True)
    (rules_home / "rules" / "coding.md").write_text("rules")
    os.environ["AODD_CODING_RULES"] = str(rules_home / "rules" / "coding.md")
    try:
        # coding-rules-gate: first code edit without the rules read
        res = adapter.handle_pre({"conversationId": "adv-1", "workspacePaths": [str(T / "gproj")],
                                  "toolCall": {"name": "write_to_file", "args": {"TargetFile": str(T / "gproj" / "a.py"), "CodeContent": "x"}}})
        assert res["decision"] == "allow" and "coding.md" in res.get("additionalContext", ""), res
        # dirty-branch-switch-guard: a dirty tree and a branch switch
        repo = T / "dirty-repo"
        repo.mkdir(parents=True, exist_ok=True)
        g = lambda *a: subprocess.run(["git", *a], cwd=repo, check=True, capture_output=True)
        g("init", "-q"); (repo / "f").write_text("a"); g("add", "f")
        g("-c", "user.email=t@t", "-c", "user.name=t", "commit", "-q", "-m", "f")
        (repo / "f").write_text("b")
        pre = {"conversationId": "adv-2", "workspacePaths": [str(repo)],
               "toolCall": {"name": "run_command", "args": {"CommandLine": "git checkout -b other"}}}
        res = adapter.handle_pre(pre)
        assert res["decision"] == "allow" and "uncommitted" in res.get("additionalContext", ""), res
        assert adapter.handle_pre(pre) == {"decision": "allow"}, "same advice once per session"
    finally:
        for k in ("AODD_STATE", "CODING_RULES_GATE_STATE", "AODD_CODING_RULES"):
            os.environ.pop(k, None)


def test_secret_deny_only_for_hard_secrets():
    os.environ["AODD_HOOKS_DIR"] = str(ROOT / "hooks")
    os.environ["AODD_STATE"] = str(T / "state-secret")
    try:
        env = T / ".env"
        env.write_text("KEY=abc\n")
        read = {"conversationId": "sec-1", "toolCall": {"name": "view_file", "args": {"AbsolutePath": str(env)}}}
        assert adapter.handle_pre(read)["decision"] == "deny"                      # printing a secret file: kept
        edit = {"conversationId": "sec-2", "toolCall": {"name": "replace_file_content", "args": {"TargetFile": str(env)}}}
        res = adapter.handle_pre(edit)
        assert res["decision"] == "allow" and "additionalContext" in res, res      # editing one: advice only
    finally:
        os.environ.pop("AODD_STATE", None)


def test_search_guard_integration():
    os.environ["AODD_HOOKS_DIR"] = str(ROOT / "hooks")
    gproj = T / "gproj"
    gproj.mkdir(parents=True, exist_ok=True)
    subprocess.run(["git", "init", "-q"], cwd=gproj, check=True, capture_output=True)
    os.environ["AODD_INDEX_CMD"] = "python3 -c pass {root}"   # a configured search backend
    os.environ["AODD_SEARCH_GUARD_STATE"] = str(T / "sg-state")

    res_deny = adapter.handle_pre({
        "conversationId": "gg-sess-1",
        "workspacePaths": [str(gproj)],
        "toolCall": {"name": "run_command", "args": {"CommandLine": "grep -rn foo ."}}
    })
    assert res_deny.get("decision") == "allow" and "project_search" in res_deny.get("additionalContext", ""), res_deny

    adapter.handle_post({
        "conversationId": "gg-sess-1",
        "workspacePaths": [str(gproj)],
        "toolCall": {"name": "run_command", "args": {"CommandLine": "python3 project_search.py query foo"}}
    })
    res_allow = adapter.handle_pre({
        "conversationId": "gg-sess-1",
        "workspacePaths": [str(gproj)],
        "toolCall": {"name": "run_command", "args": {"CommandLine": "grep -rn foo ."}}
    })
    assert res_allow == {"decision": "allow"}, res_allow
    os.environ.pop("AODD_INDEX_CMD", None); os.environ.pop("AODD_SEARCH_GUARD_STATE", None)


if __name__ == "__main__":
    test_fails_open_when_missing()
    test_done_gate_integration()
    test_skill_capture_integration()
    test_auditor_readonly_integration()
    test_search_guard_integration()
    test_advice_hooks_never_deny()
    test_secret_deny_only_for_hard_secrets()
    test_install_agy()
    print("ok")
