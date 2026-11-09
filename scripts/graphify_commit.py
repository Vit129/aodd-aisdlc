#!/usr/bin/env python3
"""Refresh tracked Graphify artifacts synchronously, then commit the prepared index."""

import argparse
import os
import subprocess
from pathlib import Path


def prepare_graph(root: Path) -> None:
    if not (root / "graphify-out").is_dir():
        raise RuntimeError("Graphify setup missing; stop before commit and configure the repository graph.")
    env = {**os.environ, "PYTHONHASHSEED": "0"}
    subprocess.run(["graphify", "update", "."], cwd=root, env=env, check=True)
    tracked = subprocess.check_output(["git", "ls-files", "-z", "--", "graphify-out/"], cwd=root)
    paths = [os.fsdecode(path) for path in tracked.split(b"\0") if path]
    if paths:
        subprocess.run(["git", "add", "--update", "--", *paths], cwd=root, check=True)


def commit(root: Path, message: str) -> None:
    prepare_graph(root)
    subprocess.run(["git", "commit", "-m", message], cwd=root, check=True,
                   env={**os.environ, "GRAPHIFY_SKIP_HOOK": "1"})


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("-m", "--message", required=True)
    args = parser.parse_args()
    root = Path(subprocess.check_output(["git", "rev-parse", "--show-toplevel"], text=True).strip())
    commit(root, args.message)


if __name__ == "__main__":
    try:
        main()
    except (OSError, RuntimeError, subprocess.CalledProcessError) as exc:
        raise SystemExit(f"Graphify commit stopped: {exc}") from exc
