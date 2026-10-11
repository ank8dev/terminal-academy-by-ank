"""Running student commands (LESSONS_PLAN.md, section 2.9)."""

import os
import shutil
import subprocess
import sys
import tempfile
import time
import unittest

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

from terminal_academy.shell import Shell, find_shell, is_interactive  # noqa: E402


def process_gone(pid):
    """True if ``pid`` has ended (a zombie waiting for its parent counts as ended)."""
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return True
    except PermissionError:
        return False
    stat_file = "/proc/%d/stat" % pid
    if os.path.exists(stat_file):
        try:
            with open(stat_file) as fh:
                state = fh.read().rsplit(")", 1)[1].split()[0]
            return state in ("Z", "X")
        except (OSError, IndexError):
            return True
    try:
        out = subprocess.run(["ps", "-o", "stat=", "-p", str(pid)],
                             stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                             universal_newlines=True, timeout=5).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return False
    return out == "" or out.startswith("Z")


def wait_gone(pid, seconds=5.0):
    deadline = time.monotonic() + seconds
    while time.monotonic() < deadline:
        if process_gone(pid):
            return True
        time.sleep(0.05)
    return process_gone(pid)


class ShellTest(unittest.TestCase):
    shell = None  # the default: bash from PATH (or sh)

    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="ta-shell-")
        self.sandbox = os.path.join(self.tmp, "sandbox")
        os.makedirs(os.path.join(self.sandbox, "school", "math"))
        self.sh = Shell(self.sandbox, os.path.join(self.tmp, "state"),
                        timeout=10, use_tty=False, shell=self.shell)

    def tearDown(self):
        self.sh.cleanup()
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_simple_output(self):
        r = self.sh.run("echo hello")
        self.assertEqual(r.stdout, "hello\n")
        self.assertEqual(r.stderr, "")
        self.assertEqual(r.returncode, 0)
        self.assertFalse(r.timed_out)

    def test_starts_in_sandbox(self):
        self.assertEqual(self.sh.cwd, os.path.realpath(self.sandbox))
        r = self.sh.run("pwd -P")
        self.assertEqual(r.stdout.strip(), os.path.realpath(self.sandbox))

    def test_cd_persists(self):
        r = self.sh.run("cd school")
        self.assertEqual(r.cwd, os.path.realpath(os.path.join(self.sandbox, "school")))
        self.sh.run("cd math")
        r = self.sh.run("pwd -P")
        self.assertEqual(r.stdout.strip(),
                         os.path.realpath(os.path.join(self.sandbox, "school", "math")))
        self.assertEqual(self.sh.relative_cwd(), "~/school/math")
        self.sh.run("cd ..")
        self.assertEqual(self.sh.relative_cwd(), "~/school")

    def test_cd_home_goes_to_sandbox(self):
        self.sh.run("cd school/math")
        r = self.sh.run("cd")
        self.assertEqual(r.cwd, os.path.realpath(self.sandbox))
        self.assertEqual(self.sh.relative_cwd(), "~")

    def test_export_persists(self):
        self.sh.run("export PET=cat")
        r = self.sh.run('echo "pet=$PET"')
        self.assertEqual(r.stdout, "pet=cat\n")
        r = self.sh.run("sh -c 'echo child=$PET'")  # really exported
        self.assertEqual(r.stdout, "child=cat\n")

    def test_value_with_spaces_and_quotes(self):
        self.sh.run("export MSG=\"it's a \\\"test\\\" \\$x\"")
        r = self.sh.run('printf "%s\\n" "$MSG"')
        self.assertEqual(r.stdout, "it's a \"test\" $x\n")

    def test_unset_persists(self):
        self.sh.run("export PET=cat")
        self.sh.run("unset PET")
        r = self.sh.run('echo "[${PET-unset}]"')
        self.assertEqual(r.stdout, "[unset]\n")

    def test_path_change_persists(self):
        os.makedirs(os.path.join(self.sandbox, "bin"))
        tool = os.path.join(self.sandbox, "bin", "hello-ta")
        with open(tool, "w") as fh:
            fh.write("#!/bin/sh\necho hi from tool\n")
        os.chmod(tool, 0o755)
        self.sh.run('export PATH="$HOME/bin:$PATH"')
        r = self.sh.run("hello-ta")
        self.assertEqual(r.stdout, "hi from tool\n")

    def test_reset_state_forgets_env_and_cwd(self):
        self.sh.run("export PET=cat")
        self.sh.run("cd school")
        self.sh.reset_state()
        self.assertEqual(self.sh.cwd, os.path.realpath(self.sandbox))
        r = self.sh.run('echo "[${PET-unset}]"')
        self.assertEqual(r.stdout, "[unset]\n")

    def test_ta_variables_do_not_leak(self):
        r = self.sh.run("env")
        self.assertNotIn("TA_STATE=", r.stdout)
        self.assertNotIn("TA_CMD=", r.stdout)
        self.sh.run("true")
        r = self.sh.run("env")
        self.assertNotIn("TA_STATE=", r.stdout)

    def test_cd_outside_is_moved_back(self):
        r = self.sh.run("cd /")
        self.assertTrue(r.moved_back)
        self.assertEqual(r.cwd, os.path.realpath(self.sandbox))
        r = self.sh.run("pwd -P")
        self.assertFalse(r.moved_back)
        self.assertEqual(r.stdout.strip(), os.path.realpath(self.sandbox))

    def test_cd_dotdot_from_root_is_moved_back(self):
        r = self.sh.run("cd ..")
        self.assertTrue(r.moved_back)
        self.assertEqual(self.sh.relative_cwd(), "~")

    def test_home_is_sandbox(self):
        r = self.sh.run('echo "$HOME"')
        self.assertEqual(os.path.realpath(r.stdout.strip()), os.path.realpath(self.sandbox))
        self.sh.run("true")  # later commands too (environment loaded from file)
        r = self.sh.run("cd ~ && pwd -P")
        self.assertEqual(r.stdout.strip(), os.path.realpath(self.sandbox))

    def test_stderr_captured(self):
        r = self.sh.run("echo oops >&2")
        self.assertEqual(r.stdout, "")
        self.assertEqual(r.stderr, "oops\n")
        r = self.sh.run("ls does-not-exist")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("does-not-exist", r.stderr)

    def test_exit_code(self):
        self.assertEqual(self.sh.run("true").returncode, 0)
        self.assertEqual(self.sh.run("false").returncode, 1)
        self.assertEqual(self.sh.run("exit 3").returncode, 3)

    def test_exit_still_saves_state(self):
        self.sh.run("cd school; export PET=dog; exit 4")
        self.assertEqual(self.sh.relative_cwd(), "~/school")
        self.assertEqual(self.sh.run('echo "$PET"').stdout, "dog\n")

    def test_syntax_error_does_not_break_shell(self):
        r = self.sh.run("echo (")
        self.assertNotEqual(r.returncode, 0)
        self.assertEqual(self.sh.run("echo ok").stdout, "ok\n")

    def test_stdin_is_empty(self):
        start = time.monotonic()
        r = self.sh.run("cat")
        self.assertEqual(r.stdout, "")
        self.assertLess(time.monotonic() - start, 5)

    def test_comment_in_command(self):
        r = self.sh.run("echo hi # this is a comment")
        self.assertEqual(r.stdout, "hi\n")
        r = self.sh.run("cd school # go to school")
        self.assertEqual(self.sh.relative_cwd(), "~/school")
        r = self.sh.run("# only a comment")
        self.assertEqual(r.returncode, 0)
        self.assertEqual(self.sh.relative_cwd(), "~/school")

    def test_timeout_stops_command(self):
        sh = Shell(self.sandbox, os.path.join(self.tmp, "state2"), timeout=0.5,
                   use_tty=False, shell=self.shell)
        try:
            start = time.monotonic()
            r = sh.run("sleep 20")
            elapsed = time.monotonic() - start
            self.assertTrue(r.timed_out)
            self.assertLess(elapsed, 5)
            self.assertEqual(sh.run("echo after").stdout, "after\n")
        finally:
            sh.cleanup()

    def test_background_job_does_not_hang_and_is_cleaned_up(self):
        start = time.monotonic()
        r = self.sh.run("sleep 300 & echo $!")
        self.assertLess(time.monotonic() - start, 5)
        self.assertFalse(r.timed_out)
        pid = int(r.stdout.strip())
        self.assertFalse(process_gone(pid), "background sleep should still run")
        self.assertTrue(self.sh.pgids, "the process group should be remembered")
        self.sh.cleanup()
        self.assertTrue(wait_gone(pid), "cleanup() should stop the background sleep")
        self.assertEqual(self.sh.pgids, set())

    def test_is_interactive(self):
        self.assertTrue(is_interactive("less notes.txt"))
        self.assertTrue(is_interactive("cat notes.txt | less"))
        self.assertTrue(is_interactive("/usr/bin/man ls"))
        self.assertFalse(is_interactive("ls -l"))
        self.assertFalse(is_interactive("echo less"))


def _other_shell(path):
    """``path`` if it exists and is not the shell the default tests already use."""
    if not os.path.exists(path):
        return None
    if os.path.realpath(path) == os.path.realpath(find_shell()):
        return None
    return path


@unittest.skipUnless(_other_shell("/bin/bash"), "/bin/bash missing or already tested")
class BinBashShellTest(ShellTest):
    """/bin/bash explicitly: on macOS this is the old bash 3.2."""

    shell = "/bin/bash"


@unittest.skipUnless(_other_shell("/bin/sh"), "/bin/sh missing or already tested")
class BinShShellTest(ShellTest):
    """The fallback when bash is missing (dash on Debian/Ubuntu)."""

    shell = "/bin/sh"


if __name__ == "__main__":
    unittest.main()
