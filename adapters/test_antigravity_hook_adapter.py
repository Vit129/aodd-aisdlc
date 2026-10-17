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
os.environ.pop("AODD_REPORTS", None)
os.environ.pop("AODD_STATE", None)
os.environ.pop("AODD_PLANS", None)


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
    assert res.get("decision") == "continue", f"expected continue, got {res}"
    assert "- [ ] task two" in res.get("reason", "")

    # When all progress items checked but not audited -> still blocks for audit
    prog_file.write_text("- [x] task one\n- [x] task two\n")
    res_aud = adapter.handle_stop(payload)
    assert res_aud.get("decision") == "continue", f"expected continue, got {res_aud}"
    assert "audit.py" in res_aud.get("reason", "")


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
    assert res.get("decision") == "continue", f"expected continue, got {res}"
    assert "[skill-capture]" in res.get("reason", "")
    assert "user correction" in res.get("reason", "")


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
        **os.environ,
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

    # Check installed artifacts
    assert (temp_agy / "skills" / "chief-of-staff" / "SKILL.md").is_file()
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


if __name__ == "__main__":
    test_fails_open_when_missing()
    test_done_gate_integration()
    test_skill_capture_integration()
    test_auditor_readonly_integration()
    test_install_agy()
    print("ok")
