#!/usr/bin/env python3
"""rea_check.py with a stub launcher: no network, no real rea."""
import importlib.util, io, os, stat, tempfile
from contextlib import redirect_stdout
from pathlib import Path

spec = importlib.util.spec_from_file_location("rea_check", Path(__file__).with_name("rea_check.py"))
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)

T = Path(tempfile.mkdtemp(prefix="reacheck-", dir=Path(__file__).resolve().parents[1]))
log = T / "log"
stub = T / "rea"
stub.write_text(f'#!/bin/sh\necho "$@" >> "{log}"\n[ "$1" = "--version" ] && echo "rea 6.4.0"\n[ "$1" = doctor ] && [ "$3" = codex ] && exit 3\nexit 0\n')
stub.chmod(stub.stat().st_mode | stat.S_IXUSR)
os.environ["AODD_REA_CMD"] = str(stub)


def go(*args, latest):
    os.environ["AODD_REA_LATEST"] = latest
    buf = io.StringIO()
    with redirect_stdout(buf):
        rc = m.main(list(args))
    return rc, buf.getvalue()


try:
    rc, out = go(latest="6.4.0", )                       # current, codex unregistered: report only, exit 1
    assert rc == 1 and "ok      claude_code" in out and "FIX     codex" in out and "STALE" not in out, out
    assert "setup" not in log.read_text(), "read-only run must not run setup"
    rc, out = go("--client", "claude_code", latest="6.4.0")
    assert rc == 0, out
    rc, out = go("--client", "claude_code", latest="6.5.0")  # stale: flagged, still read-only
    assert rc == 1 and "STALE" in out, out
    log.write_text("")
    rc, out = go("--update", latest="6.4.0")             # no newer version: only the failing client is re-set-up
    assert rc == 0 and log.read_text().count("setup --client codex --yes") == 1 and "setup --client claude_code" not in log.read_text(), log.read_text()
    assert m.semver("rea 6.8.0") == (6, 8, 0) and m.semver("x") is None
    print("ok")
finally:
    for f in T.iterdir(): f.unlink()
    T.rmdir()
