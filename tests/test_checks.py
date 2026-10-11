"""The 9 check types (LESSONS_PLAN.md, section 2.5)."""

import os
import shutil
import sys
import tempfile
import unittest

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

from terminal_academy import checks  # noqa: E402
from terminal_academy.checks import Context, evaluate  # noqa: E402


class ChecksTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="ta-checks-")
        self.sandbox = os.path.join(self.tmp, "sandbox")
        os.makedirs(os.path.join(self.sandbox, "school", "math"))
        with open(os.path.join(self.sandbox, "notes.txt"), "w", encoding="utf-8") as fh:
            fh.write("first line\nsecret: 42\n")
        os.chmod(os.path.join(self.sandbox, "notes.txt"), 0o644)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def ctx(self, **kw):
        kw.setdefault("cwd", self.sandbox)
        return Context(sandbox=self.sandbox, **kw)

    def test_all_types_are_known(self):
        self.assertEqual(len(checks.CHECK_TYPES), 9)
        self.assertEqual(set(checks.CHECK_TYPES), set(checks.REQUIRED_PARAMS))

    # ----- command_matches ------------------------------------------------

    def test_command_matches(self):
        check = {"type": "command_matches", "pattern": "^ls\\b"}
        self.assertTrue(evaluate(check, self.ctx(command="ls -la")))
        self.assertTrue(evaluate(check, self.ctx(command="   ls   ")))  # stripped
        self.assertFalse(evaluate(check, self.ctx(command="echo ls")))
        self.assertFalse(evaluate(check, self.ctx(command="lsblk")))
        self.assertFalse(evaluate(check, self.ctx(command="")))

    # ----- output_contains ------------------------------------------------

    def test_output_contains_default_stdout(self):
        check = {"type": "output_contains", "text": "hello"}
        self.assertTrue(evaluate(check, self.ctx(stdout="say hello\n")))
        self.assertFalse(evaluate(check, self.ctx(stderr="hello\n")))
        self.assertFalse(evaluate(check, self.ctx(stdout="Hello\n")))  # case-sensitive

    def test_output_contains_stderr(self):
        check = {"type": "output_contains", "text": "No such file", "stream": "stderr"}
        self.assertTrue(evaluate(check, self.ctx(stderr="ls: x: No such file or directory")))
        self.assertFalse(evaluate(check, self.ctx(stdout="No such file")))

    def test_output_contains_both(self):
        check = {"type": "output_contains", "text": "boom", "stream": "both"}
        self.assertTrue(evaluate(check, self.ctx(stdout="boom")))
        self.assertTrue(evaluate(check, self.ctx(stderr="boom")))
        self.assertFalse(evaluate(check, self.ctx(stdout="bo", stderr="om")))

    def test_output_contains_multiline(self):
        check = {"type": "output_contains", "text": "a\nb"}
        self.assertTrue(evaluate(check, self.ctx(stdout="a\nb\n")))
        self.assertFalse(evaluate(check, self.ctx(stdout="a b\n")))

    # ----- file and folder checks -----------------------------------------

    def test_file_exists(self):
        self.assertTrue(evaluate({"type": "file_exists", "path": "notes.txt"}, self.ctx()))
        self.assertFalse(evaluate({"type": "file_exists", "path": "nope.txt"}, self.ctx()))
        self.assertFalse(evaluate({"type": "file_exists", "path": "school"}, self.ctx()))

    def test_dir_exists(self):
        self.assertTrue(evaluate({"type": "dir_exists", "path": "school/math"}, self.ctx()))
        self.assertFalse(evaluate({"type": "dir_exists", "path": "notes.txt"}, self.ctx()))
        self.assertFalse(evaluate({"type": "dir_exists", "path": "art"}, self.ctx()))

    def test_path_missing(self):
        self.assertTrue(evaluate({"type": "path_missing", "path": "gone"}, self.ctx()))
        self.assertFalse(evaluate({"type": "path_missing", "path": "notes.txt"}, self.ctx()))
        self.assertFalse(evaluate({"type": "path_missing", "path": "school"}, self.ctx()))

    def test_path_missing_sees_broken_symlink(self):
        os.symlink("does-not-exist", os.path.join(self.sandbox, "dangling"))
        self.assertFalse(evaluate({"type": "path_missing", "path": "dangling"}, self.ctx()))

    def test_file_contains(self):
        check = {"type": "file_contains", "path": "notes.txt", "text": "secret: 42"}
        self.assertTrue(evaluate(check, self.ctx()))
        check = {"type": "file_contains", "path": "notes.txt", "text": "secret: 43"}
        self.assertFalse(evaluate(check, self.ctx()))
        check = {"type": "file_contains", "path": "school", "text": ""}
        self.assertFalse(evaluate(check, self.ctx()))  # a folder is not a file
        check = {"type": "file_contains", "path": "missing.txt", "text": ""}
        self.assertFalse(evaluate(check, self.ctx()))

    def test_file_contains_binary_does_not_crash(self):
        with open(os.path.join(self.sandbox, "blob"), "wb") as fh:
            fh.write(b"\xff\xfe abc \x00")
        check = {"type": "file_contains", "path": "blob", "text": "abc"}
        self.assertTrue(evaluate(check, self.ctx()))

    def test_file_mode(self):
        path = os.path.join(self.sandbox, "notes.txt")
        check = {"type": "file_mode", "path": "notes.txt", "mode": "600"}
        self.assertFalse(evaluate(check, self.ctx()))
        os.chmod(path, 0o600)
        self.assertTrue(evaluate(check, self.ctx()))

    def test_file_mode_ignores_special_bits(self):
        # The sticky bit on a folder is allowed for normal users everywhere.
        school = os.path.join(self.sandbox, "school")
        os.chmod(school, 0o1755)
        self.assertTrue(evaluate({"type": "file_mode", "path": "school", "mode": "755"},
                                 self.ctx()))
        os.chmod(school, 0o755)

    def test_file_mode_folder_and_missing(self):
        os.chmod(os.path.join(self.sandbox, "school"), 0o700)
        self.assertTrue(evaluate({"type": "file_mode", "path": "school", "mode": "700"},
                                 self.ctx()))
        self.assertFalse(evaluate({"type": "file_mode", "path": "nope", "mode": "644"},
                                  self.ctx()))

    # ----- cwd_is ---------------------------------------------------------

    def test_cwd_is(self):
        math = os.path.join(self.sandbox, "school", "math")
        self.assertTrue(evaluate({"type": "cwd_is", "path": "school/math"}, self.ctx(cwd=math)))
        self.assertFalse(evaluate({"type": "cwd_is", "path": "school"}, self.ctx(cwd=math)))
        self.assertTrue(evaluate({"type": "cwd_is", "path": "."}, self.ctx()))
        self.assertFalse(evaluate({"type": "cwd_is", "path": "."}, self.ctx(cwd=math)))

    def test_cwd_is_uses_realpath(self):
        # Like macOS, where /tmp is a symlink to /private/tmp.
        link = os.path.join(self.tmp, "link")
        os.symlink(self.sandbox, link)
        ctx = Context(sandbox=link, cwd=os.path.join(self.sandbox, "school"))
        self.assertTrue(evaluate({"type": "cwd_is", "path": "school"}, ctx))
        ctx = Context(sandbox=self.sandbox, cwd=os.path.join(link, "school", "math"))
        self.assertTrue(evaluate({"type": "cwd_is", "path": "school/math"}, ctx))

    # ----- all ------------------------------------------------------------

    def test_all(self):
        check = {"type": "all", "checks": [
            {"type": "command_matches", "pattern": "^cat\\b"},
            {"type": "output_contains", "text": "42"},
        ]}
        self.assertTrue(evaluate(check, self.ctx(command="cat notes.txt", stdout="secret: 42")))
        self.assertFalse(evaluate(check, self.ctx(command="cat notes.txt", stdout="nothing")))
        self.assertFalse(evaluate(check, self.ctx(command="echo 42", stdout="42")))

    def test_all_nested(self):
        check = {"type": "all", "checks": [
            {"type": "file_exists", "path": "notes.txt"},
            {"type": "all", "checks": [
                {"type": "dir_exists", "path": "school"},
                {"type": "all", "checks": [{"type": "path_missing", "path": "x"}]},
            ]},
        ]}
        self.assertTrue(evaluate(check, self.ctx()))
        os.makedirs(os.path.join(self.sandbox, "x"))
        self.assertFalse(evaluate(check, self.ctx()))

    def test_unknown_type_raises(self):
        with self.assertRaises(ValueError):
            evaluate({"type": "magic"}, self.ctx())


if __name__ == "__main__":
    unittest.main()
