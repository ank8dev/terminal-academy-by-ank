"""Part 2: parsing the three event sources (shell hook, tcpdump, SSH log)."""

import os
import sys
import unittest

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

from terminal_academy.hacklab import events  # noqa: E402


class ShellLogTest(unittest.TestCase):
    def test_parse_valid_lines(self):
        text = "1700000000\t/home/player\tls -a\n1700000005\t/home/player/.config\tcat x\n"
        parsed = events.parse_shell_log(text)
        self.assertEqual(len(parsed), 2)
        self.assertEqual(parsed[0].cwd, "/home/player")
        self.assertEqual(parsed[0].command, "ls -a")
        self.assertEqual(parsed[1].time, 1700000005.0)

    def test_command_with_tabs_is_kept_whole(self):
        parsed = events.parse_shell_log("1\t/home\tgrep -P a\tb\n")
        self.assertEqual(parsed[0].command, "grep -P a\tb")

    def test_skips_half_written_and_blank_lines(self):
        text = "1700000000\t/home\tls\n\nhalf-written-line\n1700000001\t/home"
        parsed = events.parse_shell_log(text)
        self.assertEqual(len(parsed), 1)  # only the first complete line

    def test_bad_timestamp_skipped(self):
        self.assertEqual(events.parse_shell_log("notime\t/home\tls\n"), [])


class TcpdumpTest(unittest.TestCase):
    SYN = "1700000000.1 IP 10.89.0.2.40000 > 10.89.0.3.22: Flags [S], seq 1, win 64240"
    SYNACK = "1700000000.2 IP 10.89.0.3.22 > 10.89.0.2.40000: Flags [S.], seq 9, ack 2"
    ACK = "1700000000.3 IP 10.89.0.2.40000 > 10.89.0.3.22: Flags [.], ack 10, win 502"

    def test_parse_syn(self):
        pkts = events.parse_tcpdump(self.SYN)
        self.assertEqual(len(pkts), 1)
        p = pkts[0]
        self.assertEqual((p.src_ip, p.src_port), ("10.89.0.2", 40000))
        self.assertEqual((p.dst_ip, p.dst_port), ("10.89.0.3", 22))
        self.assertEqual(p.kind, "SYN")

    def test_parse_syn_ack_and_ack(self):
        self.assertEqual(events.parse_tcpdump(self.SYNACK)[0].kind, "SYN-ACK")
        self.assertEqual(events.parse_tcpdump(self.ACK)[0].kind, "ACK")

    def test_non_packet_lines_ignored(self):
        self.assertEqual(events.parse_tcpdump("tcpdump: listening on any\n\n"), [])

    def test_handshake_stage_progression(self):
        self.assertEqual(events.handshake_stage([]), "none")
        syn = events.parse_tcpdump(self.SYN)
        self.assertEqual(events.handshake_stage(syn), "syn")
        synack = events.parse_tcpdump(self.SYN + "\n" + self.SYNACK)
        self.assertEqual(events.handshake_stage(synack), "syn-ack")
        full = events.parse_tcpdump("\n".join([self.SYN, self.SYNACK, self.ACK]))
        self.assertEqual(events.handshake_stage(full), "established")

    def test_handshake_ignores_other_ports(self):
        other = "1700000000.1 IP 10.89.0.2.40000 > 10.89.0.3.80: Flags [S], seq 1"
        self.assertEqual(events.handshake_stage(events.parse_tcpdump(other), 22), "none")


class AuthLogTest(unittest.TestCase):
    def test_parse_failed_and_accepted(self):
        text = (
            "Nov 22 10:00:00 target sshd[12]: Failed password for operator "
            "from 10.89.0.2 port 40000 ssh2\n"
            "Nov 22 10:00:03 target sshd[12]: Accepted password for operator "
            "from 10.89.0.2 port 40005 ssh2\n"
        )
        parsed = events.parse_auth_log(text)
        self.assertEqual(len(parsed), 2)
        self.assertFalse(parsed[0].success)
        self.assertEqual(parsed[0].user, "operator")
        self.assertEqual(parsed[0].source, "10.89.0.2")
        self.assertTrue(parsed[1].success)

    def test_invalid_user_line(self):
        text = "sshd[9]: Failed password for invalid user root from 10.0.0.9 port 1 ssh2\n"
        parsed = events.parse_auth_log(text)
        self.assertEqual(parsed[0].user, "root")
        self.assertFalse(parsed[0].success)

    def test_unrelated_lines_ignored(self):
        self.assertEqual(events.parse_auth_log("sshd started\nconnection closed\n"), [])


if __name__ == "__main__":
    unittest.main()
