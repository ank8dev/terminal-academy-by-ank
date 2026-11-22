"""Turn raw log text into small, typed events the diagram can draw.

Three event sources feed the live diagram:

1. **The shell hook** in the player container. After every command, a tiny
   bash hook appends one line ``EPOCH<TAB>CWD<TAB>COMMAND`` to a file we share
   with the host (see ``rc.sh`` and ``session.py``). :func:`parse_shell_log`
   turns that file into :class:`ShellEvent` objects.

2. **tcpdump** in the target container (network levels). It prints one line
   per packet; :func:`parse_tcpdump` extracts the TCP handshake flags
   (SYN, SYN-ACK, ACK) and who talked to whom.

3. **The SSH server log** in the target container. :func:`parse_auth_log`
   finds each password attempt and whether it failed or succeeded.

Every function here is PURE: text in, list of events out. No files, no
network, no Docker. That is what makes them easy to unit-test.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import List, Optional


# ----- 1. the player's shell hook -------------------------------------------

@dataclass
class ShellEvent:
    """One command the player ran, and where they were when it finished."""

    time: float
    cwd: str
    command: str


def parse_shell_log(text: str) -> List[ShellEvent]:
    """Parse the ``EPOCH<TAB>CWD<TAB>COMMAND`` lines written by the hook.

    Lines that do not have the three tab-separated fields are skipped, so a
    half-written last line (the hook is appending while we read) never crashes
    the diagram.
    """
    events: List[ShellEvent] = []
    for line in text.splitlines():
        if not line.strip():
            continue
        parts = line.split("\t", 2)
        if len(parts) != 3:
            continue
        stamp, cwd, command = parts
        try:
            when = float(stamp)
        except ValueError:
            continue
        events.append(ShellEvent(time=when, cwd=cwd, command=command))
    return events


# ----- 2. tcpdump (the TCP handshake) ---------------------------------------

@dataclass
class Packet:
    """One TCP packet seen by tcpdump, reduced to what the diagram needs."""

    src_ip: str
    src_port: int
    dst_ip: str
    dst_port: int
    kind: str  # "SYN", "SYN-ACK", "ACK", "DATA", "FIN", "RST" or "OTHER"


# tcpdump's text format, for a line such as:
#   10.89.0.2.40000 > 10.89.0.3.22: Flags [S], seq 1, win 64240, ...
# IPs are "a.b.c.d.port" (the port is the last dotted number), so we match the
# four address octets, then the port, on each side.
_TCPDUMP_RE = re.compile(
    r"(?P<src>\d+\.\d+\.\d+\.\d+)\.(?P<sport>\d+)\s*>\s*"
    r"(?P<dst>\d+\.\d+\.\d+\.\d+)\.(?P<dport>\d+):\s*Flags\s*\[(?P<flags>[^\]]*)\]"
)

# TCP flag letters -> the handshake stage we show. tcpdump writes "S" for SYN,
# "S." for SYN+ACK, "." for a bare ACK, "P." for data (push), "F"/"F." for
# FIN, "R"/"R." for reset.
_FLAG_KIND = {
    "S": "SYN",
    "S.": "SYN-ACK",
    ".": "ACK",
    "P.": "DATA",
    "F": "FIN",
    "F.": "FIN",
    "R": "RST",
    "R.": "RST",
}


def _flags_to_kind(flags: str) -> str:
    return _FLAG_KIND.get(flags, "DATA" if "P" in flags else "OTHER")


def parse_tcpdump(text: str) -> List[Packet]:
    """Pull the TCP packets out of tcpdump's text output."""
    packets: List[Packet] = []
    for line in text.splitlines():
        match = _TCPDUMP_RE.search(line)
        if not match:
            continue
        packets.append(
            Packet(
                src_ip=match.group("src"),
                src_port=int(match.group("sport")),
                dst_ip=match.group("dst"),
                dst_port=int(match.group("dport")),
                kind=_flags_to_kind(match.group("flags")),
            )
        )
    return packets


def handshake_stage(packets: List[Packet], dst_port: int = 22) -> str:
    """How far the TCP handshake to ``dst_port`` has got: the diagram's state.

    Returns one of "none", "syn", "syn-ack", "established". We look only at
    packets to/from ``dst_port`` so other traffic does not confuse it.
    """
    saw_syn = saw_synack = saw_ack = False
    for pkt in packets:
        to_target = pkt.dst_port == dst_port
        from_target = pkt.src_port == dst_port
        if to_target and pkt.kind == "SYN":
            saw_syn = True
        elif from_target and pkt.kind == "SYN-ACK":
            saw_synack = True
        elif to_target and pkt.kind in ("ACK", "DATA") and saw_synack:
            saw_ack = True
    if saw_ack:
        return "established"
    if saw_synack:
        return "syn-ack"
    if saw_syn:
        return "syn"
    return "none"


# ----- 3. the SSH server log (password attempts) ----------------------------

@dataclass
class AuthEvent:
    """One password attempt against the SSH server."""

    user: str
    success: bool
    source: Optional[str] = None  # the client IP, if the log shows it


# sshd log lines look like:
#   Failed password for player from 10.89.0.2 port 40000 ssh2
#   Failed password for invalid user root from 10.89.0.2 port 40001 ssh2
#   Accepted password for player from 10.89.0.2 port 40002 ssh2
_AUTH_RE = re.compile(
    r"(?P<result>Accepted|Failed)\s+password\s+for\s+"
    r"(?:invalid user\s+)?(?P<user>\S+)\s+from\s+(?P<source>\d+\.\d+\.\d+\.\d+)"
)


def parse_auth_log(text: str) -> List[AuthEvent]:
    """Find each SSH password attempt in the server log."""
    events: List[AuthEvent] = []
    for line in text.splitlines():
        match = _AUTH_RE.search(line)
        if not match:
            continue
        events.append(
            AuthEvent(
                user=match.group("user"),
                success=match.group("result") == "Accepted",
                source=match.group("source"),
            )
        )
    return events
