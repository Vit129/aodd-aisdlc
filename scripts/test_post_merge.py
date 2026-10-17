"""post-merge hook: runs install.sh then AODD_POST_INSTALL on main, debounced, logs, never fails git, skips other branches."""
import os, shutil, subprocess, tempfile, time
from pathlib import Path

hook = Path(__file__).resolve().parent / "git-hooks" / "post-merge"
t = Path(tempfile.mkdtemp())
repo, state = t / "repo", t / "state"
repo.mkdir(); (repo / "hooks").mkdir()
shutil.copy(hook.parent.parent.parent / "hooks" / "_aodd_paths.py", repo / "hooks")
git = lambda *a: subprocess.run(["git", "-C", str(repo), *a], check=True, capture_output=True)
git("init", "-q", "-b", "main")
(repo / "install.sh").write_text(f'#!/bin/bash\necho installed >> "{t}/trace"\n'); (repo / "install.sh").chmod(0o755)
env = {**os.environ, "AODD_STATE": str(state), "AODD_POST_INSTALL": f'echo post >> "{t}/trace"', "AODD_AUTO_INSTALL": "0"}


def run():
    return subprocess.run(["bash", str(hook)], cwd=repo, env=env, capture_output=True).returncode


assert run() == 0; time.sleep(1.5); assert not (t / "trace").exists()   # opt-in: no AODD_AUTO_INSTALL=1, no install
env["AODD_AUTO_INSTALL"] = "1"


def wait(pred):
    for _ in range(50):
        if pred(): return True
        time.sleep(0.1)
    return False


assert run() == 0
assert wait(lambda: (t / "trace").is_file() and "post" in (t / "trace").read_text() and not (state / "post-merge.lock").exists())
assert (t / "trace").read_text().split() == ["installed", "post"]
assert "post-merge" in (state / "post-merge.log").read_text()
assert run() == 0 and run() == 0; time.sleep(0.5)                       # inside 30 s: debounced
assert (t / "trace").read_text().split() == ["installed", "post"]
(state / "post-merge.stamp").unlink(); git("symbolic-ref", "HEAD", "refs/heads/feature")  # not main: nothing runs
assert run() == 0; time.sleep(0.5)
assert (t / "trace").read_text().split() == ["installed", "post"]
(repo / "install.sh").write_text("#!/bin/bash\nexit 3\n"); git("symbolic-ref", "HEAD", "refs/heads/main")  # failing install never fails git
assert run() == 0
assert wait(lambda: "failed" in (state / "post-merge.log").read_text())
# a literal "$HOME/..." AODD_STATE (unexpanded settings env) must land under the real HOME, not in the repo
fake_home = Path(tempfile.mkdtemp())
r = subprocess.run(["bash", str(hook)], cwd=repo, capture_output=True,
                   env={**env, "HOME": str(fake_home), "AODD_STATE": "$HOME/st", "AODD_AUTO_INSTALL": "1", "AUTO_INSTALL_DELAY": "0"})
assert r.returncode == 0
time.sleep(1.5)
assert not (repo / "$HOME").exists(), "literal $HOME dir created in the repo"
assert (fake_home / "st").exists(), list(fake_home.iterdir())
# ${HOME} braces expand the same way as in Python (_aodd_paths)
r = subprocess.run(["bash", str(hook)], cwd=repo, capture_output=True,
                   env={**env, "HOME": str(fake_home), "AODD_STATE": "${HOME}/st2", "AODD_AUTO_INSTALL": "1", "AUTO_INSTALL_DELAY": "0"})
assert r.returncode == 0 and (fake_home / "st2").exists(), list(fake_home.iterdir())
print("ok")
