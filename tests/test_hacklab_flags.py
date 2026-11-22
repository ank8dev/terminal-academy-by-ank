"""Part 2: flag generation, hashing and the hash-only flag store."""

import os
import sys
import tempfile
import unittest

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

from terminal_academy.hacklab import flags  # noqa: E402


class FlagShapeTest(unittest.TestCase):
    def test_new_flag_shape(self):
        flag = flags.new_flag()
        self.assertTrue(flag.startswith("FLAG{"))
        self.assertTrue(flag.endswith("}"))
        self.assertTrue(flags.looks_like_flag(flag))

    def test_flags_are_random(self):
        many = {flags.new_flag() for _ in range(50)}
        self.assertEqual(len(many), 50, "flags should be unique per call")

    def test_looks_like_flag_rejects_junk(self):
        self.assertFalse(flags.looks_like_flag("hello"))
        self.assertFalse(flags.looks_like_flag("FLAG{}"))
        self.assertFalse(flags.looks_like_flag(""))

    def test_normalize_trims_whitespace(self):
        self.assertEqual(flags.normalize("  FLAG{x}\n"), "FLAG{x}")

    def test_sha256_is_stable_and_trimmed(self):
        flag = "FLAG{abcdef}"
        self.assertEqual(flags.sha256_hex(flag), flags.sha256_hex("  " + flag + "\n"))
        self.assertEqual(len(flags.sha256_hex(flag)), 64)

    def test_different_flags_hash_differently(self):
        self.assertNotEqual(flags.sha256_hex("FLAG{a}"), flags.sha256_hex("FLAG{b}"))


class FlagStoreTest(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.mkdtemp(prefix="ta-flags-")
        self.store = flags.FlagStore(os.path.join(self.dir, "flags.json"))

    def tearDown(self):
        import shutil
        shutil.rmtree(self.dir, ignore_errors=True)

    def test_store_keeps_only_hash_not_flag(self):
        flag = flags.new_flag()
        self.store.set_flag("01-demo", flag)
        with open(self.store.path, encoding="utf-8") as fh:
            text = fh.read()
        # The clear-text flag must never be written to disk.
        self.assertNotIn(flag, text)
        self.assertIn(flags.sha256_hex(flag), text)

    def test_check_accepts_correct_flag(self):
        flag = flags.new_flag()
        self.store.set_flag("01-demo", flag)
        self.assertTrue(self.store.check("01-demo", flag))
        self.assertTrue(self.store.check("01-demo", " " + flag + "\n"))

    def test_check_rejects_wrong_flag(self):
        self.store.set_flag("01-demo", flags.new_flag())
        self.assertFalse(self.store.check("01-demo", "FLAG{wrong}"))

    def test_check_unknown_level_is_false(self):
        self.assertFalse(self.store.check("nope", "FLAG{x}"))

    def test_clear_forgets_a_level(self):
        flag = flags.new_flag()
        self.store.set_flag("01-demo", flag)
        self.store.clear("01-demo")
        self.assertFalse(self.store.check("01-demo", flag))

    def test_store_survives_reload(self):
        flag = flags.new_flag()
        self.store.set_flag("01-demo", flag)
        reopened = flags.FlagStore(self.store.path)
        self.assertTrue(reopened.check("01-demo", flag))

    def test_broken_file_does_not_crash(self):
        with open(self.store.path, "w", encoding="utf-8") as fh:
            fh.write("not json {{{")
        store = flags.FlagStore(self.store.path)  # should not raise
        self.assertIsNone(store.expected_hash("anything"))


if __name__ == "__main__":
    unittest.main()
