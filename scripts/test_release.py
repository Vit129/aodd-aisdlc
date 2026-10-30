#!/usr/bin/env python3
"""Unit tests for release version calculation."""

import importlib.util
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).with_name("release.py")
SPEC = importlib.util.spec_from_file_location("release", MODULE_PATH)
release = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(release)


class ReleaseVersionTests(unittest.TestCase):
    def test_patch_bump(self):
        self.assertEqual(release.next_version("0.6.1", "patch"), "0.6.2")

    def test_minor_bump(self):
        self.assertEqual(release.next_version("0.6.1", "minor"), "0.7.0")

    def test_major_bump(self):
        self.assertEqual(release.next_version("0.6.1", "major"), "1.0.0")

    def test_rejects_invalid_version(self):
        with self.assertRaises(ValueError):
            release.next_version("v0.6.1", "patch")

    def test_version_order(self):
        self.assertGreater(release.version_tuple("0.7.0"), release.version_tuple("0.6.9"))


if __name__ == "__main__":
    unittest.main()
