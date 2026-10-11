"""Command line interface: ``./academy`` or ``python3 -m terminal_academy``.

  academy                 main menu
  academy list            list lessons and progress
  academy start 3         start lesson 3 (number or id)
  academy reset [3]       reset progress (all lessons, or one)
"""

from __future__ import annotations

import argparse
import os
import sys
from typing import Callable, List, Optional

from terminal_academy import __version__
from terminal_academy.engine import DONE, QUIT, LessonSession
from terminal_academy.lessons import (
    Lesson,
    find_lesson,
    force_rmtree,
    lesson_missing_tools,
    lesson_number,
    load_lessons,
)
from terminal_academy.progress import Progress
from terminal_academy.shell import DEFAULT_TIMEOUT
from terminal_academy.ui import UI, colors_wanted

LEVEL_NAMES = {
    1: "First steps",
    2: "Working with text",
    3: "Scripts and settings",
    4: "Processes and networks",
    5: "SSH and beyond",
}


class App:
    def __init__(
        self,
        home: str,
        ui: UI,
        input_func: Callable[[str], str] = input,
        timeout: float = DEFAULT_TIMEOUT,
        lessons_dir: Optional[str] = None,
    ) -> None:
        self.home = home
        self.ui = ui
        self.input_func = input_func
        self.timeout = timeout
        os.makedirs(home, exist_ok=True)
        self.progress = Progress(os.path.join(home, "progress.json"))
        if self.progress.recovered_from_broken:
            ui.warn("Your progress file was broken, so I started fresh. "
                    "A copy of the old file is in progress.json.bak.")
        self.lessons, problems = load_lessons(lessons_dir)
        for problem in problems:
            ui.warn("Skipping a broken lesson file: " + problem)

    # ----- lessons list ---------------------------------------------------

    def status_symbol(self, lesson: Lesson) -> str:
        status = self.progress.status(lesson["id"])
        if status == "done":
            return self.ui.style(self.ui.sym["done"], "green", "bold")
        if status == "in_progress":
            return self.ui.style(self.ui.sym["progress"], "yellow", "bold")
        return self.ui.style(self.ui.sym["new"], "dim")

    def print_lessons(self) -> None:
        level = None
        for lesson in self.lessons:
            if lesson["level"] != level:
                level = lesson["level"]
                self.ui.print("")
                self.ui.print(self.ui.style(
                    "Level %d · %s" % (level, LEVEL_NAMES.get(level, "")), "cyan", "bold"))
            number = "%2d" % lesson_number(lesson)
            minutes = " (~%d min)" % lesson["minutes"] if lesson.get("minutes") else ""
            line = "  %s %s  %s%s" % (
                self.status_symbol(lesson),
                self.ui.style(number, "bold"),
                lesson["title"],
                self.ui.style(minutes, "dim"),
            )
            missing = lesson_missing_tools(lesson)
            if missing:
                line += "  " + self.ui.style(
                    "%s needs %s" % (self.ui.sym["missing"], ", ".join(missing)), "yellow")
            self.ui.print(line)
            self.ui.print(self.ui.style(self.ui.wrap(lesson["summary"], indent="       "),
                                        "dim"))
        self.ui.print("")
        self.ui.dim("%s done   %s in progress   %s not started   %s missing tool"
                    % (self.ui.sym["done"], self.ui.sym["progress"],
                       self.ui.sym["new"], self.ui.sym["missing"]))

    def next_lesson(self, lesson: Lesson) -> Optional[Lesson]:
        idx = self.lessons.index(lesson)
        return self.lessons[idx + 1] if idx + 1 < len(self.lessons) else None

    # ----- playing --------------------------------------------------------

    def play(self, lesson: Lesson) -> str:
        """Play ``lesson`` and then offer the next ones. Returns "quit" or "menu"."""
        current: Optional[Lesson] = lesson
        while current is not None:
            session = LessonSession(
                current, self.home, self.progress, self.ui,
                input_func=self.input_func, timeout=self.timeout,
                show_lessons=self.print_lessons,
            )
            outcome = session.run()
            if outcome != DONE:
                return outcome
            nxt = self.next_lesson(current)
            if nxt is None:
                self.ui.say("That was the last lesson for now. You're amazing!")
                return "menu"
            try:
                answer = self.input_func(
                    "Next up: Lesson %d · %s. Start it now? (y/n) "
                    % (lesson_number(nxt), nxt["title"]))
            except (EOFError, KeyboardInterrupt):
                self.ui.print("")
                return QUIT
            if answer.strip().lower() not in ("y", "yes", ""):
                return "menu"
            current = nxt
        return "menu"

    def menu(self) -> int:
        self.ui.splash()
        while True:
            self.print_lessons()
            try:
                answer = self.input_func("Pick a lesson number (q to quit): ")
            except (EOFError, KeyboardInterrupt):
                self.ui.print("")
                break
            answer = answer.strip()
            if answer.lower() in ("q", "quit", "exit"):
                break
            if not answer:
                continue
            lesson = find_lesson(self.lessons, answer)
            if lesson is None:
                self.ui.say("Hmm, I don't know lesson %r. Type one of the numbers "
                            "from the list." % answer)
                continue
            if self.play(lesson) == QUIT:
                break
        self.ui.say("Bye! Come back soon, the terminal misses you already.")
        return 0

    def reset(self, key: Optional[str], yes: bool) -> int:
        if key:
            lesson = find_lesson(self.lessons, key)
            if lesson is None:
                self.ui.error("Unknown lesson %r. Try: academy list" % key)
                return 2
            targets = [lesson["id"]]
            question = "Reset your progress in lesson %s?" % lesson["id"]
        else:
            targets = [l["id"] for l in self.lessons]
            question = "Reset ALL your progress?"
        if not yes:
            try:
                answer = self.input_func(question + " (y/n) ")
            except (EOFError, KeyboardInterrupt):
                answer = ""
            if answer.strip().lower() not in ("y", "yes"):
                self.ui.say("OK, nothing changed.")
                return 0
        self.progress.reset(key and targets[0] or None)
        for lid in targets:
            for folder in ("sandbox", "state"):
                path = os.path.join(self.home, folder, lid)
                if os.path.lexists(path):
                    force_rmtree(path)
        self.ui.say("Done. Fresh start!")
        return 0


# ----- argument parsing ----------------------------------------------------

def _common_options(parser: argparse.ArgumentParser, default) -> None:
    parser.add_argument("--no-color", action="store_true", default=default,
                        help="do not use colors (the NO_COLOR variable works too)")
    parser.add_argument("--home", metavar="DIR", default=default,
                        help="where progress and sandboxes live "
                             "(default: ~/.terminal-academy, or $TERMINAL_ACADEMY_HOME)")
    parser.add_argument("--allow-root", action="store_true", default=default,
                        help="run even as root (not recommended)")
    parser.add_argument("--timeout", type=float, default=default, help=argparse.SUPPRESS)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="academy",
        description="Terminal Academy: learn the terminal by doing.",
    )
    parser.add_argument("--version", action="version",
                        version="Terminal Academy " + __version__)
    _common_options(parser, argparse.SUPPRESS)
    sub = parser.add_subparsers(dest="command")
    common = argparse.ArgumentParser(add_help=False)
    _common_options(common, argparse.SUPPRESS)
    sub.add_parser("list", parents=[common], help="list lessons and your progress")
    p_start = sub.add_parser("start", parents=[common], help="start a lesson")
    p_start.add_argument("lesson", help="lesson number or id, e.g. 1 or 01-first-steps")
    p_reset = sub.add_parser("reset", parents=[common], help="reset progress")
    p_reset.add_argument("lesson", nargs="?", help="only this lesson (default: all)")
    p_reset.add_argument("-y", "--yes", action="store_true", help="do not ask")
    return parser


def resolve_home(arg: Optional[str]) -> str:
    home = arg or os.environ.get("TERMINAL_ACADEMY_HOME") or "~/.terminal-academy"
    return os.path.abspath(os.path.expanduser(home))


def resolve_timeout(arg: Optional[float]) -> float:
    if arg is not None:
        return max(0.1, arg)
    env = os.environ.get("TERMINAL_ACADEMY_TIMEOUT")
    if env:
        try:
            return max(0.1, float(env))
        except ValueError:
            pass
    return DEFAULT_TIMEOUT


def make_input(ui: UI) -> Callable[[str], str]:
    """input(), plus echo of the typed line when stdin is not a terminal."""
    interactive = sys.stdin.isatty()

    def read(prompt: str) -> str:
        line = input(prompt)
        if not interactive:
            ui.print(line)
        return line

    return read


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    readline_active = False
    if sys.stdin.isatty():
        try:
            import readline  # noqa: F401  (arrow keys and history for input())

            readline_active = True
        except ImportError:
            pass

    # On a terminal without UTF-8 (e.g. LANG=C), print "?" for symbols it
    # cannot show instead of crashing with UnicodeEncodeError.
    try:
        sys.stdout.reconfigure(errors="replace")  # type: ignore[attr-defined]
    except (AttributeError, ValueError):
        pass

    no_color = bool(getattr(args, "no_color", False))
    ui = UI(color=colors_wanted(sys.stdout, no_color), readline_active=readline_active)

    if hasattr(os, "geteuid") and os.geteuid() == 0 and not (
        getattr(args, "allow_root", False) or os.environ.get("TERMINAL_ACADEMY_ALLOW_ROOT")
    ):
        ui.error("You are running Terminal Academy as root (the admin user). "
                 "Please run it as your normal user: it is safer, and the lessons "
                 "about permissions only work that way. "
                 "(If you really must, use --allow-root.)")
        return 1

    app = App(
        resolve_home(getattr(args, "home", None)),
        ui,
        input_func=make_input(ui),
        timeout=resolve_timeout(getattr(args, "timeout", None)),
    )
    if not app.lessons:
        ui.error("I could not find any lessons. Is the terminal_academy/lessons folder there?")
        return 1

    try:
        if args.command in (None, "start"):
            # Interactive use only: the boot animation checks for a real
            # terminal itself, and Ctrl+C just skips it.
            ui.boot(len(app.lessons))
        if args.command == "list":
            app.print_lessons()
            return 0
        if args.command == "start":
            lesson = find_lesson(app.lessons, args.lesson)
            if lesson is None:
                ui.error("Unknown lesson %r. Try: academy list" % args.lesson)
                return 2
            if app.play(lesson) != QUIT:
                return app.menu()
            ui.say("Bye! Come back soon.")
            return 0
        if args.command == "reset":
            return app.reset(args.lesson, args.yes)
        return app.menu()
    except KeyboardInterrupt:
        ui.print("")
        return 130
    except BrokenPipeError:
        # Output went to a program that stopped reading (e.g. `| head`).
        try:
            devnull = os.open(os.devnull, os.O_WRONLY)
            os.dup2(devnull, sys.stdout.fileno())
        except OSError:
            pass
        return 1
