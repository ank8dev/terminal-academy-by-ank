"""A very small wrapper around the ``docker`` command line.

Part 2 (ethical hacking) runs each level inside Docker containers. We do NOT
use a Docker SDK: that would be an extra dependency, and the project rule is
"standard library only". Instead we shell out to the ``docker`` binary and
read its output. Every function here is a thin, readable shell-out so you can
see exactly which ``docker`` command runs.

WHY a wrapper at all: so the rest of Part 2 never builds ``docker`` command
lines by hand. One place knows how to talk to Docker; everything else asks
this module. That also gives us one clear spot to fail with a friendly
message when Docker is missing.
"""

from __future__ import annotations

import os
import shutil
import subprocess
from dataclasses import dataclass
from typing import List, Optional, Sequence

# How long we wait for a single docker command before giving up. Builds can be
# slow (apt-get installs packages), so this is generous.
BUILD_TIMEOUT = 600.0
RUN_TIMEOUT = 120.0


@dataclass
class DockerResult:
    """What one ``docker ...`` command returned."""

    returncode: int
    stdout: str
    stderr: str

    @property
    def ok(self) -> bool:
        return self.returncode == 0


class DockerError(Exception):
    """A docker command failed. The message is meant to be shown to the user."""


def docker_path() -> Optional[str]:
    """Where the ``docker`` binary is, or None if it is not installed."""
    return shutil.which("docker")


def check_docker() -> Optional[str]:
    """Return a friendly error string if Docker is unusable, else ``None``.

    Part 2 needs a working Docker engine. This checks two things that fail
    for different reasons:

    1. the ``docker`` command exists (the client is installed), and
    2. the daemon answers (``docker info`` succeeds).

    On macOS 12 (our target) Docker Desktop may be unsupported; Colima is the
    usual replacement. The message points there.
    """
    if docker_path() is None:
        return (
            "I need Docker for Part 2, but I can't find the 'docker' command.\n"
            "Install Docker Engine (Linux) or, on macOS, Colima + the docker CLI:\n"
            "    brew install colima docker && colima start\n"
            "Then try again. Part 1 (the terminal lessons) needs no Docker."
        )
    try:
        proc = subprocess.run(
            ["docker", "info"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
            timeout=RUN_TIMEOUT,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return "I found the docker command but could not run it: %s" % exc
    if proc.returncode != 0:
        detail = proc.stderr.decode("utf-8", "replace").strip()
        return (
            "Docker is installed but the engine is not running.\n"
            "Start it first:\n"
            "    Linux:  sudo systemctl start docker   (or: sudo dockerd)\n"
            "    macOS:  colima start\n"
            "Docker said:\n    %s" % (detail or "(no details)")
        )
    return None


def run(args: Sequence[str], timeout: float = RUN_TIMEOUT,
        check: bool = False) -> DockerResult:
    """Run ``docker <args>`` and capture its output.

    ``check=True`` raises :class:`DockerError` on a non-zero exit, with the
    stderr as the message. ``check=False`` (the default) returns the result so
    the caller can decide what a failure means.
    """
    try:
        proc = subprocess.run(
            ["docker", *args],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        raise DockerError("docker %s took too long and was stopped." % args[0])
    except OSError as exc:
        raise DockerError("could not run docker: %s" % exc)
    result = DockerResult(
        returncode=proc.returncode,
        stdout=proc.stdout.decode("utf-8", "replace"),
        stderr=proc.stderr.decode("utf-8", "replace"),
    )
    if check and not result.ok:
        raise DockerError(result.stderr.strip() or "docker %s failed" % " ".join(args))
    return result


# ----- images ----------------------------------------------------------------

def image_exists(tag: str) -> bool:
    return run(["image", "inspect", tag]).ok


def build_image(tag: str, context_dir: str, dockerfile: str) -> DockerResult:
    """Build ``dockerfile`` in ``context_dir`` and tag it ``tag``.

    ``TERMINAL_ACADEMY_BUILD_NETWORK`` (optional) sets the build network, e.g.
    ``host``. Normal users leave it unset. It exists for sandboxes where the
    Docker build step must reach the package mirror through the host's network
    (such as a CI/cloud box behind an HTTPS proxy).
    """
    args = ["build", "-t", tag, "-f", dockerfile]
    build_net = os.environ.get("TERMINAL_ACADEMY_BUILD_NETWORK")
    if build_net:
        args += ["--network", build_net]
    args.append(context_dir)
    return run(args, timeout=BUILD_TIMEOUT)


# ----- networks --------------------------------------------------------------

def network_exists(name: str) -> bool:
    return run(["network", "inspect", name]).ok


def create_network(name: str) -> None:
    """Create an *internal* bridge network (no route to the outside world).

    ``--internal`` is the key safety setting: containers on this network can
    talk to each other but NOT to the internet or your real LAN. A scanning
    lesson must never be able to reach a real machine.
    """
    if not network_exists(name):
        run(["network", "create", "--internal", name], check=True)


def remove_network(name: str) -> None:
    run(["network", "rm", name])  # ignore errors: it may already be gone


# ----- containers ------------------------------------------------------------

def run_detached(name: str, image: str, network: str,
                 binds: Optional[List[str]] = None,
                 hostname: Optional[str] = None,
                 aliases: Optional[List[str]] = None,
                 extra: Optional[List[str]] = None) -> None:
    """Start a background container, attached to ``network``.

    ``binds`` are ``host:container`` bind mounts (used to share the event
    files with the host). ``aliases`` are short DNS names other containers on
    the network can use (so the player can reach ``target`` by that name). The
    container keeps running (its image's command is a long sleep) so we can
    ``exec`` into it.
    """
    args = ["run", "-d", "--name", name, "--network", network,
            "--hostname", hostname or name]
    for alias in aliases or []:
        args += ["--network-alias", alias]
    for bind in binds or []:
        args += ["-v", bind]
    args += extra or []
    args.append(image)
    run(args, check=True)


def exec_in(name: str, command: Sequence[str], user: Optional[str] = None,
            timeout: float = RUN_TIMEOUT) -> DockerResult:
    """Run a command inside a running container (not interactive)."""
    args = ["exec"]
    if user:
        args += ["-u", user]
    args += [name, *command]
    return run(args, timeout=timeout)


def exec_shell(name: str, command: str, user: Optional[str] = None,
               timeout: float = RUN_TIMEOUT) -> DockerResult:
    """Run a shell snippet inside a container (``sh -c '<command>'``)."""
    return exec_in(name, ["sh", "-c", command], user=user, timeout=timeout)


def copy_in(name: str, host_path: str, container_path: str) -> None:
    """Copy a file from the host into the container with ``docker cp``.

    We use this for the flag: it is copied into the container at run time, so
    the secret is never baked into the image layers and never passed as an
    environment variable.
    """
    run(["cp", host_path, "%s:%s" % (name, container_path)], check=True)


def container_running(name: str) -> bool:
    result = run(["inspect", "-f", "{{.State.Running}}", name])
    return result.ok and result.stdout.strip() == "true"


def stop_and_remove(name: str) -> None:
    """Stop and delete a container. Safe to call even if it does not exist."""
    run(["rm", "-f", name])
