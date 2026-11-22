"""Run one Part 2 level: build images, start containers, place the flag,
and feed the live diagram.

This is the orchestrator. It ties together the small pieces:

- ``docker_lab``  — talk to Docker
- ``flags``       — make a random flag and remember only its hash
- ``events``      — read the shell hook, tcpdump and the SSH log
- ``diagram_server`` — the browser page that draws the live diagram

The design keeps the dangerous parts contained: every container sits on an
``--internal`` Docker network (no route to the internet or your real machine),
the flag is copied in at run time (never baked into an image), and stopping a
level removes every container and network it made.
"""

from __future__ import annotations

import os
import shutil
import tempfile
from typing import Any, Dict, List, Optional

from terminal_academy.hacklab import docker_lab, events, flags
from terminal_academy.hacklab.levels import Container, Level

# Where this module's static files live (the shell hook and the diagram page).
PACKAGE_DIR = os.path.dirname(os.path.abspath(__file__))
RC_SH = os.path.join(PACKAGE_DIR, "rc.sh")

# How deep the filesystem-tree diagram looks.
TREE_DEPTH = 4


class LabSession:
    """A running (or startable) level."""

    def __init__(self, level: Level, home: str, flag_store: flags.FlagStore) -> None:
        self.level = level
        self.home = home
        self.flag_store = flag_store
        # Names are prefixed so we never touch a container that is not ours.
        self.prefix = "ta-" + level.id
        self.network = self.prefix + "-net"
        # Host folder shared with the containers at /lab (hook, events, logs).
        self.lab_dir = os.path.join(home, "hacklab", level.id, "lab")
        self.events_dir = os.path.join(self.lab_dir, "events")
        self.solved = False

    # ----- names ----------------------------------------------------------

    def container_name(self, container: Container) -> str:
        return "%s-%s" % (self.prefix, container.name)

    def image_tag(self, container: Container) -> str:
        return "terminal-academy/%s-%s" % (self.level.id, container.name)

    # ----- build ----------------------------------------------------------

    def build(self, log=print) -> None:
        """Build every container image for this level."""
        for container in self.level.containers:
            tag = self.image_tag(container)
            dockerfile = os.path.join(self.level.directory, container.dockerfile)
            log("Building image %s ..." % tag)
            result = docker_lab.build_image(tag, self.level.directory, dockerfile)
            if not result.ok:
                raise docker_lab.DockerError(
                    "Building %s failed:\n%s" % (tag, result.stderr.strip())
                )

    def images_ready(self) -> bool:
        return all(docker_lab.image_exists(self.image_tag(c))
                   for c in self.level.containers)

    # ----- start / stop ---------------------------------------------------

    def _prepare_lab_dir(self) -> None:
        """Make the shared /lab folder and copy the shell hook into it."""
        os.makedirs(self.events_dir, exist_ok=True)
        # The player runs as a non-root user and must be able to append to the
        # event files, so the shared folder is world-writable. It only ever
        # holds our own log files.
        os.chmod(self.lab_dir, 0o777)
        os.chmod(self.events_dir, 0o777)
        shutil.copyfile(RC_SH, os.path.join(self.lab_dir, "rc.sh"))
        # Start every run with empty logs, so the diagram reflects THIS run.
        for name in ("shell.log", "tcpdump.log", "auth.log"):
            open(os.path.join(self.events_dir, name), "w").close()
            os.chmod(os.path.join(self.events_dir, name), 0o666)

    def start(self) -> str:
        """Build (if needed), start the containers, place the flag.

        Returns the fresh flag string (shown to no one; used only so the
        caller can, for example, verify in a test). The host keeps only the
        SHA-256.
        """
        if not self.images_ready():
            self.build()
        self.stop()  # clean any leftovers from a previous run
        self._prepare_lab_dir()
        docker_lab.create_network(self.network)

        bind = "%s:/lab" % self.lab_dir
        for container in self.level.containers:
            extra: List[str] = []
            # The target of a network level runs tcpdump, which needs the raw
            # and admin network capabilities. We grant them only there.
            if self.level.diagram == "network" and container.role == "target":
                extra = ["--cap-add", "NET_ADMIN", "--cap-add", "NET_RAW"]
            docker_lab.run_detached(
                name=self.container_name(container),
                image=self.image_tag(container),
                network=self.network,
                binds=[bind],
                hostname=container.name,
                # So other containers can reach this one by its short name,
                # e.g. the player runs `ssh operator@target`.
                aliases=[container.name],
                extra=extra,
            )

        flag = flags.new_flag()
        self._place_flag(flag)
        self.flag_store.set_flag(self.level.id, flag)

        if self.level.diagram == "network":
            self._start_capture()
        return flag

    def _place_flag(self, flag: str) -> None:
        """Write the flag to each placement, with the right owner and mode.

        The flag is written to a temporary file on the host, copied in with
        ``docker cp``, then the host copy is deleted right away.
        """
        fd, tmp = tempfile.mkstemp(prefix="ta-flag-")
        try:
            with os.fdopen(fd, "w") as fh:
                fh.write(flag + "\n")
            for placement in self.level.flag_placements:
                container = next(c for c in self.level.containers
                                 if c.name == placement["container"])
                name = self.container_name(container)
                path = placement["path"]
                # Make sure the parent folder exists inside the container.
                parent = os.path.dirname(path)
                docker_lab.exec_shell(name, "mkdir -p '%s'" % parent, user="root")
                docker_lab.copy_in(name, tmp, path)
                if placement.get("owner"):
                    owner = placement["owner"]
                    docker_lab.exec_in(name, ["chown", "%s:%s" % (owner, owner), path],
                                       user="root")
                mode = placement.get("mode", "644")
                docker_lab.exec_in(name, ["chmod", mode, path], user="root")
        finally:
            os.remove(tmp)  # the host never keeps the flag in clear text

    def _start_capture(self) -> None:
        """For network levels: capture packets on the target with tcpdump.

        tcpdump writes to the shared /lab so the diagram can read it. We run it
        detached; it stops when the container stops.
        """
        target = self.level.target
        if target is None:
            return
        name = self.container_name(target)
        # -l line-buffered, -n no name lookups, -tt epoch time, tcp only.
        docker_lab.exec_in(
            name,
            ["sh", "-c",
             "tcpdump -l -n -tt -i any tcp >> /lab/events/tcpdump.log 2>/dev/null &"],
            user="root",
        )

    def running(self) -> bool:
        return docker_lab.container_running(self.container_name(self.level.player))

    def stop(self) -> None:
        """Stop and remove every container and the network for this level."""
        for container in self.level.containers:
            docker_lab.stop_and_remove(self.container_name(container))
        docker_lab.remove_network(self.network)

    # ----- playing --------------------------------------------------------

    def attach_argv(self) -> List[str]:
        """The ``docker`` argv that drops the player into an interactive shell."""
        name = self.container_name(self.level.player)
        return ["exec", "-it", name, "bash", "--rcfile", "/lab/rc.sh", "-i"]

    def run_in_player(self, command: str, user: Optional[str] = None):
        """Run a shell command inside the player container (non-interactive).

        Used by tests and the end-to-end self-check. Real players use the
        interactive shell instead.
        """
        return docker_lab.exec_shell(self.container_name(self.level.player),
                                     command, user=user)

    def submit(self, candidate: str) -> bool:
        ok = self.flag_store.check(self.level.id, candidate)
        if ok:
            self.solved = True
        return ok

    # ----- the live diagram state ----------------------------------------

    def _read_event_file(self, name: str) -> str:
        try:
            with open(os.path.join(self.events_dir, name), encoding="utf-8",
                      errors="replace") as fh:
                return fh.read()
        except OSError:
            return ""

    def snapshot(self) -> Dict[str, Any]:
        """Build the current diagram state (what the browser draws).

        This is the function the diagram server polls. It reads the event
        files and, for the filesystem/permission views, asks the container for
        a fresh picture of the relevant files.
        """
        shell_events = events.parse_shell_log(self._read_event_file("shell.log"))
        cwd = shell_events[-1].cwd if shell_events else None
        commands = [e.command for e in shell_events][-12:]
        state: Dict[str, Any] = {
            "diagram": self.level.diagram,
            "level": {"id": self.level.id, "title": self.level.title,
                      "number": self.level.number},
            "objective": self.level.objective,
            "cwd": cwd,
            "commands": commands,
            "solved": self.solved,
            "running": self.running(),
        }
        if self.level.diagram == "filesystem":
            state["tree"] = self._filesystem_tree(cwd)
        elif self.level.diagram == "permissions":
            state["files"] = self._permission_rows()
        elif self.level.diagram == "network":
            state.update(self._network_state())
        return state

    def _filesystem_tree(self, cwd: Optional[str]) -> List[Dict[str, Any]]:
        root = self.level.diagram_watch.get("root", "/home/player")
        # find writes one "<type>\t<path>" line per entry; we sort by path in
        # Python so the shell never has to quote a tab character.
        result = self.run_in_player(
            "find '%s' -maxdepth %d -printf '%%y\\t%%p\\n' 2>/dev/null"
            % (root, TREE_DEPTH),
            user="root",
        )
        rows: List[Dict[str, Any]] = []
        lines = sorted(result.stdout.splitlines(),
                       key=lambda ln: ln.split("\t", 1)[-1])
        for line in lines:
            parts = line.split("\t", 1)
            if len(parts) != 2:
                continue
            kind, path = parts
            name = os.path.basename(path) or path
            depth = 0 if path == root else path[len(root):].strip("/").count("/") + 1
            rows.append({
                "path": path,
                "name": name,
                "depth": depth,
                "is_dir": kind == "d",
                "hidden": name.startswith("."),
                "is_cwd": cwd is not None and os.path.realpath(path) == os.path.realpath(cwd),
            })
        return rows

    def _permission_rows(self) -> List[Dict[str, Any]]:
        rows: List[Dict[str, Any]] = []
        for path in self.level.diagram_watch.get("paths", []):
            result = self.run_in_player(
                "stat -c '%%A|%%a|%%U|%%G|%%n' '%s' 2>/dev/null" % path, user="root")
            line = result.stdout.strip()
            if not line or "|" not in line:
                rows.append({"path": path, "name": os.path.basename(path),
                             "exists": False})
                continue
            bits, octal, owner, group, name = line.split("|", 4)
            rows.append({
                "path": path,
                "name": os.path.basename(name),
                "exists": True,
                "bits": bits,         # e.g. "-rw-r--r--"
                "perm": octal,        # e.g. "644"
                "owner": owner,
                "group": group,
            })
        return rows

    def _network_state(self) -> Dict[str, Any]:
        packets = events.parse_tcpdump(self._read_event_file("tcpdump.log"))
        auth = events.parse_auth_log(self._read_event_file("auth.log"))
        port = int(self.level.diagram_watch.get("port", 22))
        return {
            "handshake": events.handshake_stage(packets, dst_port=port),
            "packet_count": len(packets),
            "port": port,
            "auth": [{"user": a.user, "success": a.success, "source": a.source}
                     for a in auth],
        }
