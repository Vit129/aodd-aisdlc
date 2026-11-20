#!/usr/bin/env python3
"""Version, changelog, tag, push, and publish a release."""

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path

def find_repo_root(start: Path) -> Path:
    for directory in (start, *start.parents):
        if (directory / ".git").exists() and (directory / "cliff.toml").is_file():
            return directory
    raise RuntimeError("Run the release command from inside a checkout with cliff.toml.")


ROOT = find_repo_root(Path.cwd())
VERSION_FILE = ROOT / "VERSION"
CHANGELOG_FILE = ROOT / "CHANGELOG.md"
VERSION_RE = re.compile(r"^(\d+)\.(\d+)\.(\d+)$")


def next_version(version: str, bump: str) -> str:
    match = VERSION_RE.fullmatch(version.strip())
    if not match:
        raise ValueError(f"Invalid semver in VERSION: {version!r}")
    major, minor, patch = map(int, match.groups())
    if bump == "major":
        return f"{major + 1}.0.0"
    if bump == "minor":
        return f"{major}.{minor + 1}.0"
    return f"{major}.{minor}.{patch + 1}"


def version_tuple(version: str) -> tuple[int, int, int]:
    match = VERSION_RE.fullmatch(version.strip())
    if not match:
        raise ValueError(f"Invalid semver: {version!r}")
    return tuple(map(int, match.groups()))


def run(args: list[str], *, capture: bool = False, check: bool = True, env: dict[str, str] | None = None) -> subprocess.CompletedProcess:
    result = subprocess.run(args, cwd=ROOT, text=True, capture_output=capture, env=env)
    if check and result.returncode:
        detail = (result.stderr or result.stdout or "").strip()
        raise RuntimeError(f"Command failed ({' '.join(args)}): {detail}")
    return result


def output(*args: str) -> str:
    return run(list(args), capture=True).stdout.strip()


def release_exists(tag: str) -> bool:
    releases = json.loads(output("gh", "release", "list", "--limit", "1000", "--json", "tagName"))
    return any(release.get("tagName") == tag for release in releases)


def publish(tag: str, *, push_main: bool = True) -> None:
    if output("git", "status", "--porcelain"):
        raise RuntimeError("Release publishing requires a clean working tree.")
    if push_main:
        run(["git", "merge-base", "--is-ancestor", "origin/main", "HEAD"])
        run(["git", "push", "origin", "main", tag])
    else:
        run(["git", "push", "origin", tag])
    if release_exists(tag):
        print(f"GitHub Release {tag} already exists; release is complete.")
        return
    notes = output("git", "cliff", "--latest", "--strip", "header")
    if len(notes) > 125_000:
        raise RuntimeError("Generated release notes exceed GitHub's 125000-character limit.")
    run(["gh", "release", "create", tag, "--title", tag, "--notes", notes])


def release_gate() -> None:
    """Run the repository's documented checks before any release publication."""
    env = os.environ.copy()
    env["GIT_CONFIG_GLOBAL"] = os.devnull
    run(["make", "check"], env=env)


def release_feature(branch: str, bump: str, dry_run: bool) -> int:
    """Verify and merge a committed feature before releasing the merged main."""
    if output("git", "status", "--porcelain"):
        raise RuntimeError("Commit or explicitly stage and commit the intended changes before starting the feature release.")
    if dry_run:
        print(f"Would check {branch}, push it, create or reuse a PR to main, merge it, then release {bump} from main.")
        return 0
    run(["git", "fetch", "origin", "main", "--tags"])
    remote = output("git", "rev-parse", "origin/main")
    tags = output("git", "tag", "--list", "v*").splitlines()
    versions = [tag[1:] for tag in tags if VERSION_RE.fullmatch(tag.removeprefix("v"))]
    latest = max(versions, key=version_tuple) if versions else "0.0.0"
    version_at_main = run(["git", "show", "origin/main:VERSION"], capture=True, check=False)
    if version_at_main.returncode == 0:
        current = version_at_main.stdout.strip()
    else:
        changelog = output("git", "show", "origin/main:CHANGELOG.md")
        match = re.search(r"^## \[?(\d+\.\d+\.\d+)\]?", changelog, re.MULTILINE)
        current = match.group(1) if match else latest
    if version_tuple(current) > version_tuple(latest) and next_version(latest, bump) != current:
        raise RuntimeError(f"Version v{current} is pending on main; finish it before merging a different bump.")
    common = Path(output("git", "rev-parse", "--path-format=absolute", "--git-common-dir"))
    main_root = common.parent
    main_branch = run(["git", "-C", str(main_root), "branch", "--show-current"], capture=True).stdout.strip()
    local_main = output("git", "rev-parse", "refs/heads/main")
    if local_main != remote:
        raise RuntimeError("Local main differs from origin/main; synchronize it before merging.")
    if main_root != ROOT and (main_branch != "main" or run(["git", "-C", str(main_root), "status", "--porcelain"], capture=True).stdout.strip()):
        raise RuntimeError("The main checkout must be clean and on main before merging.")
    run(["git", "merge-base", "--is-ancestor", "origin/main", "HEAD"])
    release_gate()
    feature_head = output("git", "rev-parse", "HEAD")
    run(["git", "push", "origin", f"HEAD:refs/heads/{branch}"])
    prs = json.loads(output("gh", "pr", "list", "--base", "main", "--head", branch, "--state", "open", "--json", "url"))
    if prs:
        pr = prs[0]["url"]
    else:
        pr = output("gh", "pr", "create", "--base", "main", "--head", branch, "--fill")
    run(["gh", "pr", "merge", pr, "--merge", "--match-head-commit", feature_head])
    run(["git", "fetch", "origin", "main", "--tags"])
    run(["git", "merge-base", "--is-ancestor", "HEAD", "origin/main"])
    if main_root == ROOT:
        run(["git", "switch", "main"])
    run(["git", "-C", str(main_root), "merge", "--ff-only", "origin/main"])
    result = subprocess.run([sys.executable, "scripts/release.py", bump], cwd=main_root)
    if result.returncode:
        raise RuntimeError(f"PR was merged, but release from {main_root} failed; resume from main.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("bump", nargs="?", choices=("patch", "minor", "major"))
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--resume", action="store_true", help="complete the current tagged release without bumping")
    parser.add_argument("-m", "--message", default=os.environ.get("COMMIT_MESSAGE"), help="commit message for explicitly staged changes")
    args = parser.parse_args()
    if not args.bump and not args.resume:
        parser.error("choose patch, minor, or major (or --resume)")

    staged = output("git", "diff", "--cached", "--name-only")
    if staged:
        if not args.message:
            raise RuntimeError("Staged changes need --message; stage only the files intended for this release.")
        if output("git", "diff", "--name-only") or output("git", "ls-files", "--others", "--exclude-standard"):
            raise RuntimeError("Unstaged or untracked files remain; preserve and resolve them before release.")
        if args.dry_run:
            print(f"Would commit staged files with message: {args.message}")
        else:
            run(["git", "commit", "-m", args.message])

    branch = output("git", "branch", "--show-current")
    if not branch:
        raise RuntimeError("Release requires a named branch, not a detached HEAD.")
    if branch != "main":
        if args.resume:
            raise RuntimeError("Resume the pending release from main.")
        return release_feature(branch, args.bump, args.dry_run)
    if staged and not args.dry_run:
        run(["git", "fetch", "origin", "main", "--tags"])
        run(["git", "merge-base", "--is-ancestor", "origin/main", "HEAD"])
        release_gate()
        run(["git", "push", "origin", "main"])
    if not args.dry_run:
        run(["git", "fetch", "origin", "main", "--tags"])
    else:
        print("Dry run uses locally available remote refs and tags.")

    tags = output("git", "tag", "--list", "v*").splitlines()
    valid_tags = [value[1:] for value in tags if VERSION_RE.fullmatch(value.removeprefix("v"))]
    latest_tag_version = max(valid_tags, key=version_tuple) if valid_tags else "0.0.0"
    if VERSION_FILE.is_file():
        version = VERSION_FILE.read_text().strip()
    else:
        match = re.search(r"^## \[?(\d+\.\d+\.\d+)\]?", CHANGELOG_FILE.read_text(), re.MULTILINE)
        version = match.group(1) if match else latest_tag_version
    tag = f"v{version}"
    head = output("git", "rev-parse", "HEAD")
    remote = output("git", "rev-parse", "origin/main")
    tag_result = run(["git", "rev-parse", "--verify", f"refs/tags/{tag}^{{commit}}"], capture=True, check=False)
    tag_commit = tag_result.stdout.strip() if tag_result.returncode == 0 else ""
    subject = output("git", "log", "-1", "--format=%s")

    dirty = bool(output("git", "status", "--porcelain"))
    if dirty:
        if not args.dry_run:
            raise RuntimeError("Release requires a clean working tree; preserve and resolve all edits first.")
        print("BLOCKED: working tree has edits; preserve and resolve them before release.")

    pending_version = version_tuple(version) > version_tuple(latest_tag_version)
    if pending_version and args.bump and next_version(latest_tag_version, args.bump) != version:
        raise RuntimeError(
            f"Version v{version} is already pending after v{latest_tag_version}; "
            "finish it with --resume before selecting another bump."
        )

    # Finish a release commit that was created before its tag/push/release step failed.
    if subject == f"chore(release): {tag}":
        if tag_commit and tag_commit != head:
            raise RuntimeError(f"Tag {tag} points to {tag_commit}, but its release commit is {head}; resolve the tag mismatch manually.")
        if tag_commit != head:
            run(["git", "merge-base", "--is-ancestor", "origin/main", "HEAD"])
            if args.dry_run:
                print(f"Would tag and publish the pending release {tag} from {head}.")
                return 0
            release_gate()
            run(["git", "tag", tag])
            publish(tag)
            return 0

    # A release tag at HEAD is either already done or needs its hosted release completed.
    if tag_commit == head:
        if args.dry_run:
            action = "resume" if args.resume else "start the next version after"
            print(f"Would {action} {tag}.")
            return 0
        if args.resume:
            release_gate()
            publish(tag)
            return 0
        if not release_exists(tag):
            release_gate()
            publish(tag)
            return 0

    if args.resume:
        if tag_commit and tag_commit != head:
            raise RuntimeError(f"Cannot verify {tag}: tag points to {tag_commit}, but checkout is {head}.")
        if tag_commit:
            tagged_version = output("git", "show", f"{tag}:VERSION") if VERSION_FILE.is_file() else version
            if tagged_version != version:
                raise RuntimeError(f"Tag {tag} contains VERSION {tagged_version}, expected {version}; resolve the tag mismatch manually.")
            if args.dry_run:
                print(f"Would resume the existing {tag} release.")
                return 0
            release_gate()
            publish(tag, push_main=False)
            return 0
        if version_tuple(version) <= version_tuple(latest_tag_version):
            raise RuntimeError(f"No pending release for VERSION {version}; latest tag is v{latest_tag_version}.")

    if head != remote:
        raise RuntimeError("Local main differs from origin/main; synchronize before release.")
    run(["gh", "auth", "status"])
    run(["git", "cliff", "--version"])

    # A committed VERSION bump ahead of the latest tag is a pending release, not a request to skip it.
    new_version = version if pending_version else next_version(version, args.bump)
    new_tag = f"v{new_version}"
    changelog = output("git", "cliff", "--tag", new_tag)
    if args.dry_run:
        action = "complete" if pending_version else "create"
        print(f"Would {action} {new_tag}, update VERSION/CHANGELOG.md if needed, commit the metadata, push, and create a GitHub Release.")
        return 0

    if not pending_version and VERSION_FILE.is_file():
        VERSION_FILE.write_text(f"{new_version}\n")
    CHANGELOG_FILE.write_text(changelog.rstrip() + "\n")
    metadata = ["CHANGELOG.md"]
    if VERSION_FILE.is_file():
        metadata.append("VERSION")
    run(["git", "add", *metadata])
    if output("git", "diff", "--cached", "--name-only"):
        run(["git", "commit", "-m", f"chore(release): {new_tag}"])
    release_gate()
    run(["git", "tag", new_tag])
    publish(new_tag)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, RuntimeError, ValueError) as exc:
        print(f"release failed: {exc}", file=sys.stderr)
        raise SystemExit(1)
