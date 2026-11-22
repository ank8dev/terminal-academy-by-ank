"""The ``academy hack`` command: play Part 2 (ethical hacking) levels.

This reuses the Part 1 building blocks where it can: the same ``UI`` for all
output, the same ``Progress`` file for "done / in progress" and hint counting,
and the same friendly, hint-first teaching style. What is new is the Docker
lab (``session``) and the live diagram (``diagram_server``).

Commands:

    academy hack                 list Part 2 levels and your progress
    academy hack list            the same list
    academy hack start <n>       build, start and play level <n>
    academy hack hint <n>        show the next hint for level <n>
    academy hack learn <n>       show LEARN.md (concept + how to defend)
    academy hack submit <n> F    submit a flag you found
    academy hack stop <n>        stop a level's containers
"""

from __future__ import annotations

import os
import subprocess
from typing import List, Optional

from terminal_academy.hacklab import docker_lab, flags
from terminal_academy.hacklab.diagram_server import DiagramServer
from terminal_academy.hacklab.levels import Level, find_level, load_levels
from terminal_academy.hacklab.session import LabSession
from terminal_academy.progress import Progress
from terminal_academy.ui import UI

ETHICS = (
    "Ethics first: everything in Part 2 happens inside this lab, on containers "
    "that cannot reach the internet or your real network. Never use these "
    "techniques on any system you do not own or do not have written permission "
    "to test. Learning to attack is how you learn to defend."
)


class HackApp:
    """Runs the ``hack`` subcommands."""

    def __init__(self, home: str, ui: UI,
                 input_func=input, levels_dir: Optional[str] = None) -> None:
        self.home = home
        self.ui = ui
        self.input_func = input_func
        os.makedirs(home, exist_ok=True)
        self.progress = Progress(os.path.join(home, "progress.json"))
        self.flag_store = flags.FlagStore(os.path.join(home, "hacklab", "flags.json"))
        self.levels, problems = load_levels(levels_dir)
        for problem in problems:
            ui.warn("Skipping a broken level: " + problem)

    # ----- helpers --------------------------------------------------------

    def _session(self, level: Level) -> LabSession:
        return LabSession(level, self.home, self.flag_store)

    def _status_symbol(self, level: Level) -> str:
        status = self.progress.status(level.id)
        if status == "done":
            return self.ui.style(self.ui.sym["done"], "green", "bold")
        if status == "in_progress":
            return self.ui.style(self.ui.sym["progress"], "yellow", "bold")
        return self.ui.style(self.ui.sym["new"], "dim")

    def _find(self, key: str) -> Optional[Level]:
        return find_level(self.levels, key)

    def _docker_ok(self) -> bool:
        reason = docker_lab.check_docker()
        if reason:
            self.ui.error(reason)
            return False
        return True

    # ----- list -----------------------------------------------------------

    def list(self) -> int:
        self.ui.header("Part 2 · Ethical Hacking")
        self.ui.dim(ETHICS)
        reason = docker_lab.check_docker()
        if reason:
            self.ui.print("")
            self.ui.warn("Docker is not ready, so levels cannot start yet:")
            self.ui.dim(reason)
        self.ui.print("")
        for level in self.levels:
            line = "  %s %s  %s" % (
                self._status_symbol(level),
                self.ui.style("%2d" % level.number, "bold"),
                level.title,
            )
            self.ui.print(line)
            self.ui.print(self.ui.style(self.ui.wrap(level.summary, indent="       "),
                                        "dim"))
        self.ui.print("")
        self.ui.dim("Start one with:  academy hack start %d"
                    % (self.levels[0].number if self.levels else 1))
        return 0

    # ----- hints / learn --------------------------------------------------

    def hint(self, key: str) -> int:
        level = self._find(key)
        if level is None:
            self.ui.error("Unknown level %r. Try: academy hack list" % key)
            return 2
        # We reuse the progress "step" field to remember how many hints the
        # player has already seen for this level.
        entry = self.progress.entry(level.id)
        index = int(entry.get("step", 0))
        if index >= len(level.hints):
            index = len(level.hints) - 1
        self.ui.say("Hint %d/%d: %s" % (index + 1, len(level.hints), level.hints[index]))
        if index + 1 < len(level.hints):
            self.progress.set_step(level.id, index + 1)
        self.progress.add_hint(level.id)
        return 0

    def learn(self, key: str) -> int:
        level = self._find(key)
        if level is None:
            self.ui.error("Unknown level %r. Try: academy hack list" % key)
            return 2
        try:
            with open(level.learn_path, encoding="utf-8") as fh:
                self.ui.print(fh.read().rstrip("\n"))
        except OSError:
            self.ui.error("This level has no LEARN.md yet.")
            return 1
        return 0

    # ----- start ----------------------------------------------------------

    def start(self, key: str, attach: bool = True) -> int:
        level = self._find(key)
        if level is None:
            self.ui.error("Unknown level %r. Try: academy hack list" % key)
            return 2
        if not self._docker_ok():
            return 1

        self.ui.header("Level %d · %s" % (level.number, level.title))
        self.ui.dim(ETHICS)
        self.ui.print("")
        self.ui.info(level.story)
        self.ui.print("")
        self.ui.say("Objective: " + level.objective)

        session = self._session(level)
        self.progress.start(level.id)
        try:
            self.ui.print("")
            self.ui.dim("Preparing the lab (this builds Docker images the first time)…")
            session.start()
        except docker_lab.DockerError as exc:
            self.ui.error("Could not start the lab: %s" % exc)
            session.stop()
            return 1

        server = DiagramServer(session.snapshot)
        url = server.start()
        self.ui.success("Lab is up.")
        self.ui.say("Open the live diagram in your browser:  " + url)
        self.ui.dim("Tip: in another command, a hint is 'academy hack hint %d', "
                    "and 'academy hack learn %d' explains the idea."
                    % (level.number, level.number))

        try:
            if attach:
                self.ui.print("")
                self.ui.dim("Entering the lab shell. Type 'exit' to come back.")
                subprocess.call(["docker", *session.attach_argv()])
                self._after_shell(level, session)
        finally:
            server.stop()
        return 0

    def _after_shell(self, level: Level, session: LabSession) -> None:
        """Back from the lab shell: offer to submit the flag, then clean up."""
        self.ui.print("")
        try:
            answer = self.input_func(
                "Found the flag? Paste it to check (or press Enter to skip): ")
        except (EOFError, KeyboardInterrupt):
            answer = ""
            self.ui.print("")
        answer = answer.strip()
        if answer:
            if session.submit(answer):
                self.ui.success("Correct! That is the flag. Level solved.")
                self.progress.finish(level.id, 1)
            else:
                self.ui.warn("That is not the flag for this run. Flags are random "
                             "each time you start a level, so keep looking.")
        try:
            stop = self.input_func("Stop the lab now and remove its containers? (y/n) ")
        except (EOFError, KeyboardInterrupt):
            stop = "y"
            self.ui.print("")
        if stop.strip().lower() in ("y", "yes", ""):
            session.stop()
            self.ui.say("Lab stopped. Your progress is saved.")
        else:
            self.ui.dim("Lab left running. Stop it later with: academy hack stop %d"
                        % level.number)

    # ----- submit / stop --------------------------------------------------

    def submit(self, key: str, candidate: str) -> int:
        level = self._find(key)
        if level is None:
            self.ui.error("Unknown level %r. Try: academy hack list" % key)
            return 2
        if self.flag_store.check(level.id, candidate):
            self.ui.success("Correct! Level %d solved." % level.number)
            self.progress.finish(level.id, 1)
            return 0
        self.ui.warn("That is not the flag for the current run of level %d."
                     % level.number)
        return 1

    def stop(self, key: str) -> int:
        level = self._find(key)
        if level is None:
            self.ui.error("Unknown level %r. Try: academy hack list" % key)
            return 2
        self._session(level).stop()
        self.flag_store.clear(level.id)
        self.ui.say("Level %d stopped. Containers and network removed." % level.number)
        return 0


def run(args, home: str, ui: UI, input_func=input) -> int:
    """Dispatch one ``academy hack ...`` invocation."""
    app = HackApp(home, ui, input_func=input_func)
    if not app.levels:
        ui.error("I could not find any Part 2 levels.")
        return 1
    action = getattr(args, "hack_action", None) or "list"
    if action == "list":
        return app.list()
    if action == "start":
        return app.start(args.level)
    if action == "hint":
        return app.hint(args.level)
    if action == "learn":
        return app.learn(args.level)
    if action == "submit":
        return app.submit(args.level, args.flag)
    if action == "stop":
        return app.stop(args.level)
    return app.list()
