#!/usr/bin/env python3
"""Real local Git fixtures; no release, network, or installed configuration writes."""
import os
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from graphify_commit import commit
import release


class GraphCommitTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="graph commit ")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.git("init", "-b", "main")
        self.git("config", "user.name", "Fixture")
        self.git("config", "user.email", "fixture@example.invalid")
        self.git("config", "core.hooksPath", str(self.root / ".git/hooks"))
        (self.root / "graphify-out").mkdir()
        (self.root / "graphify-out/graph.json").write_text("old")
        (self.root / "product").write_text("old")
        self.git("add", "product", "graphify-out/graph.json")
        self.git("-c", "core.hooksPath=/dev/null", "commit", "-m", "fixture")
        (self.root / "product").write_text("new")
        self.git("add", "product")
        self.bin = self.root / "bin"
        self.bin.mkdir()
        (self.root / ".git/info/exclude").write_text("bin/\ngraphify-out/cache.tmp\n")
        self.stub('test "$PYTHONHASHSEED" = 0 || exit 8\necho fresh > graphify-out/graph.json\necho local > graphify-out/cache.tmp\n')
        self.hook("post-commit", '[ "$GRAPHIFY_SKIP_HOOK" = 1 ] || echo dirty >> graphify-out/graph.json\n')
        self.hook("pre-commit", 'echo checked > .git/pre-commit-ran\n')
        self.env = patch.dict(os.environ, {"PATH": str(self.bin) + os.pathsep + os.environ["PATH"]})
        self.env.start()
        self.addCleanup(self.env.stop)

    def git(self, *args):
        return subprocess.check_output(["git", *args], cwd=self.root, text=True).strip()

    def stub(self, body):
        path = self.bin / "graphify"
        path.write_text("#!/bin/sh\n" + body)
        path.chmod(0o755)

    def hook(self, name, body):
        path = self.root / ".git/hooks" / name
        path.write_text("#!/bin/sh\n" + body)
        path.chmod(0o755)

    def test_same_commit_and_unrelated_hooks_remain_active(self):
        commit(self.root, "fix: fixture")
        self.assertEqual(self.git("show", "HEAD:product"), "new")
        self.assertEqual(self.git("show", "HEAD:graphify-out/graph.json"), "fresh")
        self.assertEqual(self.git("diff", "--name-only"), "")
        self.assertEqual(self.git("rev-list", "--count", "HEAD"), "2")
        self.assertNotIn("cache.tmp", self.git("ls-tree", "-r", "--name-only", "HEAD"))
        self.assertTrue((self.root / ".git/pre-commit-ran").exists())

    def test_failure_preserves_staged_product_and_stops_commit(self):
        self.stub("exit 9\n")
        with self.assertRaises(subprocess.CalledProcessError):
            commit(self.root, "fix: fixture")
        self.assertEqual(self.git("rev-list", "--count", "HEAD"), "1")
        self.assertEqual(self.git("diff", "--cached", "--name-only"), "product")
        self.assertEqual((self.root / "product").read_text(), "new")

    def test_commit_hook_failure_is_not_suppressed(self):
        self.hook("pre-commit", "exit 7\n")
        with self.assertRaises(subprocess.CalledProcessError):
            commit(self.root, "fix: fixture")
        self.assertEqual(self.git("rev-list", "--count", "HEAD"), "1")


class ReleaseGraphTests(GraphCommitTests):
    def release_fixture(self):
        self.git("-c", "core.hooksPath=/dev/null", "commit", "-m", "fixture product")
        (self.root / "VERSION").write_text("1.0.0\n")
        (self.root / "CHANGELOG.md").write_text("old changelog\n")
        self.git("add", "VERSION", "CHANGELOG.md")
        self.git("-c", "core.hooksPath=/dev/null", "commit", "-m", "fixture metadata")
        self.git("tag", "v1.0.0")
        self.git("remote", "add", "origin", str(self.root))
        for name, body in [("gh", 'echo \'[{"tagName":"v1.0.0"}]\'\n'), ("git-cliff", "echo changelog\n")]:
            path = self.bin / name
            path.write_text("#!/bin/sh\n" + body)
            path.chmod(0o755)
        # The release runner validates the origin name. All Git I/O stays in this fixture.
        actual_output = release.output
        def output(*args):
            if args == ("git", "remote", "get-url", "origin"):
                return "fixture/aodd-aisdlc"
            return actual_output(*args)
        patches = [patch.object(release, "ROOT", self.root),
                   patch.object(release, "VERSION_FILE", self.root / "VERSION"),
                   patch.object(release, "CHANGELOG_FILE", self.root / "CHANGELOG.md"),
                   patch.object(release, "output", side_effect=output),
                   patch("sys.argv", ["release.py", "patch"])]
        for item in patches:
            item.start()
            self.addCleanup(item.stop)

    def test_release_metadata_and_graph_share_candidate_commit(self):
        self.release_fixture()
        with patch.object(release, "publish") as publish, patch.object(release, "release_gate") as gate:
            self.assertEqual(release.main(), 0)
        self.assertEqual(self.git("show", "HEAD:VERSION"), "1.0.1")
        self.assertEqual(self.git("show", "HEAD:graphify-out/graph.json"), "fresh")
        self.assertEqual(self.git("diff", "--name-only"), "")
        self.assertEqual(self.git("rev-parse", "v1.0.1"), self.git("rev-parse", "HEAD"))
        publish.assert_called_once_with("v1.0.1")
        gate.assert_called_once()

    def test_release_graph_failure_stops_before_commit_tag_and_publish(self):
        self.release_fixture()
        before = self.git("rev-parse", "HEAD")
        self.stub("exit 9\n")
        with patch.object(release, "publish") as publish, patch.object(release, "release_gate"), self.assertRaises(subprocess.CalledProcessError):
            release.main()
        self.assertEqual(self.git("rev-parse", "HEAD"), before)
        self.assertEqual(self.git("tag", "--list", "v1.0.1"), "")
        publish.assert_not_called()


if __name__ == "__main__":
    unittest.main()
