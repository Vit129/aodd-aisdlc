#!/usr/bin/env python3
"""Unit tests for release version calculation."""

import importlib.util
import os
import subprocess
import sys
import unittest
import tempfile
import shutil
from unittest.mock import patch
from pathlib import Path

MODULE_PATH = Path(__file__).with_name("release.py")
SPEC = importlib.util.spec_from_file_location("release", MODULE_PATH)
release = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(release)


class ReleaseVersionTests(unittest.TestCase):
    def test_finds_checkout_root_from_nested_directory(self):
        self.assertEqual(release.find_repo_root(Path(__file__).parent), Path(__file__).resolve().parents[1])

    def test_finds_tag_versioned_checkout_without_version_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / ".git").mkdir()
            (root / "cliff.toml").write_text("")
            nested = root / "nested"
            nested.mkdir()
            self.assertEqual(release.find_repo_root(nested), root)

    def test_resume_does_not_validate_another_commit(self):
        with tempfile.TemporaryDirectory() as tmp:
            version = Path(tmp) / "VERSION"
            version.write_text("1.2.3\n")
            def fake_output(*args):
                values = {
                    ("git", "diff", "--cached", "--name-only"): "",
                    ("git", "branch", "--show-current"): "main",
                    ("git", "tag", "--list", "v*"): "v1.2.3",
                    ("git", "rev-parse", "HEAD"): "new-commit",
                    ("git", "rev-parse", "origin/main"): "new-commit",
                    ("git", "log", "-1", "--format=%s"): "normal commit",
                    ("git", "status", "--porcelain"): "",
                }
                return values[args]
            class Result:
                returncode = 0
                stdout = "old-commit\n"
            with patch.object(release, "VERSION_FILE", version), patch.object(release, "output", side_effect=fake_output), patch.object(release, "run", return_value=Result()), patch("sys.argv", ["release.py", "--resume"]):
                with self.assertRaisesRegex(RuntimeError, "Cannot verify"):
                    release.main()

    def test_patch_bump(self):
        self.assertEqual(release.next_version("0.6.1", "patch"), "0.6.2")

    def test_minor_bump(self):
        self.assertEqual(release.next_version("0.6.1", "minor"), "0.7.0")

    def test_major_bump(self):
        self.assertEqual(release.next_version("0.6.1", "major"), "1.0.0")

    def test_rejects_invalid_version(self):
        with self.assertRaises(ValueError):
            release.next_version("v0.6.1", "patch")

    def test_release_choice_is_required_and_skip_is_rejected(self):
        for args in ([], ["skip"]):
            result = subprocess.run([sys.executable, str(MODULE_PATH), *args], capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)

    def test_multiple_release_choices_are_rejected(self):
        result = subprocess.run(["make", "-n", "start", "patch", "minor"], cwd=MODULE_PATH.parent.parent, capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Choose only one", result.stderr)

    def test_version_order(self):
        self.assertGreater(release.version_tuple("0.7.0"), release.version_tuple("0.6.9"))

    def test_feature_release_checks_and_merges_the_tested_head(self):
        class Result:
            returncode = 0
            stdout = "1.0.0\n"
        def fake_output(*args):
            return {
                ("git", "status", "--porcelain"): "",
                ("git", "rev-parse", "origin/main"): "base",
                ("git", "tag", "--list", "v*"): "v1.0.0",
                ("git", "rev-parse", "--path-format=absolute", "--git-common-dir"): str(release.ROOT / ".git"),
                ("git", "rev-parse", "refs/heads/main"): "base",
                ("git", "rev-parse", "HEAD"): "tested-head",
                ("gh", "pr", "list", "--base", "main", "--head", "feature/test", "--state", "open", "--json", "url"): "[]",
                ("gh", "pr", "create", "--base", "main", "--head", "feature/test", "--fill"): "https://example.invalid/pr/1",
            }[args]
        with patch.object(release, "output", side_effect=fake_output), patch.object(release, "run", return_value=Result()) as run, patch.object(release, "release_gate") as gate, patch.object(release.subprocess, "run", return_value=Result()):
            self.assertEqual(release.release_feature("feature/test", "patch", False), 0)
        gate.assert_called_once()
        commands = [call.args[0] for call in run.call_args_list]
        self.assertIn(["gh", "pr", "merge", "https://example.invalid/pr/1", "--merge", "--match-head-commit", "tested-head"], commands)
        self.assertIn(["git", "merge-base", "--is-ancestor", "HEAD", "origin/main"], commands)
        self.assertFalse(any("--admin" in command or "--force" in command for command in commands))

    def test_feature_release_stops_on_dirty_worktree(self):
        with patch.object(release, "output", return_value=" M private.txt"), patch.object(release, "run") as run:
            with self.assertRaisesRegex(RuntimeError, "Commit or explicitly stage"):
                release.release_feature("feature/test", "patch", False)
        run.assert_not_called()


class ReleaseIntegrationTests(unittest.TestCase):
    def test_feature_branch_to_release_in_both_checkout_types(self):
        for version_file in (True, False):
            with self.subTest(version_file=version_file), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                remote, repo, bins, merge = (root / name for name in ("remote.git", "repo", "bin", "merge"))
                repo.mkdir()
                bins.mkdir()
                env = os.environ.copy()
                env.update({"PATH": str(bins) + os.pathsep + env.get("PATH", ""),
                            "GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_NOSYSTEM": "1",
                            "GIT_AUTHOR_NAME": "Test", "GIT_AUTHOR_EMAIL": "test@example.invalid",
                            "GIT_COMMITTER_NAME": "Test", "GIT_COMMITTER_EMAIL": "test@example.invalid",
                            "TEST_REMOTE": str(remote), "TEST_MERGE": str(merge), "TEST_BRANCH": "feature/test"})
                def git(*args, cwd=repo):
                    return subprocess.run(["git", *args], cwd=cwd, env=env, capture_output=True, text=True, check=True)
                git("init", "--bare", str(remote), cwd=root)
                git("init", "-b", "main")
                git("remote", "add", "origin", str(remote))
                (repo / "scripts").mkdir()
                shutil.copyfile(MODULE_PATH, repo / "scripts/release.py")
                (repo / "cliff.toml").write_text("")
                (repo / "CHANGELOG.md").write_text("# Changelog\n## [1.0.0]\n")
                (repo / "Makefile").write_text("check:\n\t@true\n")
                if version_file:
                    (repo / "VERSION").write_text("1.0.0\n")
                gh = bins / "gh"
                gh.write_text('''#!/bin/sh
set -e
case "$1 $2" in
  'pr list') echo '[]' ;;
  'pr create') echo https://example.invalid/pr/1 ;;
  'pr merge') git clone -q -b main "$TEST_REMOTE" "$TEST_MERGE"; git -C "$TEST_MERGE" merge -q --no-ff "origin/$TEST_BRANCH" -m 'merge feature'; git -C "$TEST_MERGE" push -q origin main ;;
  'release list') echo '[]' ;;
esac
''')
                gh.chmod(0o755)
                cliff = bins / "git-cliff"
                cliff.write_text("#!/bin/sh\nif [ \"$1\" = --version ]; then echo test; elif [ \"$1\" = --latest ]; then echo notes; else printf '# Changelog\\n## [%s]\\n' \"${2#v}\"; fi\n")
                cliff.chmod(0o755)
                git("add", "scripts/release.py", "cliff.toml", "CHANGELOG.md", "Makefile", *(["VERSION"] if version_file else []))
                git("commit", "-m", "initial")
                git("tag", "v1.0.0")
                git("push", "-u", "origin", "main", "v1.0.0")
                git("switch", "-c", "feature/test")
                (repo / "feature.txt").write_text("feature\n")
                git("add", "feature.txt")
                git("commit", "-m", "feat: feature")
                feature_head = git("rev-parse", "HEAD").stdout.strip()
                result = subprocess.run([sys.executable, "scripts/release.py", "patch"], cwd=repo, env=env, capture_output=True, text=True)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertEqual(git("branch", "--show-current").stdout.strip(), "main")
                self.assertEqual(git("rev-parse", "v1.0.1^{}").stdout.strip(), git("rev-parse", "origin/main").stdout.strip())
                git("merge-base", "--is-ancestor", feature_head, "v1.0.1")

    def test_both_version_sources_retry_same_candidate(self):
        for version_file in (True, False):
            with self.subTest(version_file=version_file), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                remote = root / "remote.git"
                repo = root / "repo"
                bin_dir = root / "bin"
                repo.mkdir()
                bin_dir.mkdir()
                env = os.environ.copy()
                env.update({"PATH": str(bin_dir) + os.pathsep + env.get("PATH", ""),
                            "GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_NOSYSTEM": "1",
                            "GIT_AUTHOR_NAME": "Test", "GIT_AUTHOR_EMAIL": "test@example.invalid",
                            "GIT_COMMITTER_NAME": "Test", "GIT_COMMITTER_EMAIL": "test@example.invalid"})
                def git(*args, cwd=repo):
                    return subprocess.run(["git", *args], cwd=cwd, env=env, capture_output=True, text=True, check=True)
                git("init", "--bare", str(remote), cwd=root)
                git("init", "-b", "main")
                git("remote", "add", "origin", str(remote))
                (repo / "cliff.toml").write_text("")
                (repo / "CHANGELOG.md").write_text("# Changelog\n## [1.0.0]\n")
                (repo / "Makefile").write_text("check:\n\t@test \"$$RELEASE_TEST_FAIL\" != 1\n")
                if version_file:
                    (repo / "VERSION").write_text("1.0.0\n")
                gh = bin_dir / "gh"
                gh.write_text("#!/bin/sh\nif [ \"$1 $2\" = 'release list' ]; then echo '[]'; fi\n")
                gh.chmod(0o755)
                cliff = bin_dir / "git-cliff"
                cliff.write_text("#!/bin/sh\nif [ \"$1\" = --version ]; then echo test; elif [ \"$1\" = --latest ]; then echo notes; else printf '# Changelog\\n## [%s]\\n' \"${2#v}\"; fi\n")
                cliff.chmod(0o755)
                git("add", "cliff.toml", "CHANGELOG.md", "Makefile", *(["VERSION"] if version_file else []))
                git("commit", "-m", "initial")
                git("tag", "v1.0.0")
                git("push", "-u", "origin", "main", "v1.0.0")
                (repo / "feature.txt").write_text("feature\n")
                git("add", "feature.txt")
                git("commit", "-m", "feat: feature")
                git("push", "origin", "main")
                before = git("rev-parse", "HEAD").stdout.strip()
                preview = subprocess.run([sys.executable, str(MODULE_PATH), "minor", "--dry-run"], cwd=repo, env=env, capture_output=True, text=True)
                self.assertEqual(preview.returncode, 0, preview.stderr)
                self.assertEqual(git("rev-parse", "HEAD").stdout.strip(), before)
                failed = subprocess.run([sys.executable, str(MODULE_PATH), "minor"], cwd=repo, env={**env, "RELEASE_TEST_FAIL": "1"}, capture_output=True, text=True)
                self.assertNotEqual(failed.returncode, 0)
                self.assertEqual(git("tag", "--list", "v1.1.0").stdout.strip(), "")
                candidate = git("rev-parse", "HEAD").stdout.strip()
                resumed = subprocess.run([sys.executable, str(MODULE_PATH), "--resume"], cwd=repo, env=env, capture_output=True, text=True)
                self.assertEqual(resumed.returncode, 0, resumed.stderr)
                self.assertEqual(git("rev-parse", "v1.1.0^{}" ).stdout.strip(), candidate)
                self.assertEqual(git("rev-parse", "HEAD").stdout.strip(), candidate)
                self.assertEqual(git("status", "--porcelain").stdout.strip(), "")


if __name__ == "__main__":
    unittest.main()
