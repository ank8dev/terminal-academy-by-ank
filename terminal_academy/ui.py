"""Output helpers: colors, wrapping, the splash logo and Ank's voice.

Colors are plain ANSI codes. They are switched off when the output is not a
terminal, when the NO_COLOR environment variable is set (https://no-color.org),
when TERM is "dumb", or with --no-color.
"""

from __future__ import annotations

import os
import random
import shutil
import sys
import textwrap
from typing import Optional, TextIO

from terminal_academy import __version__

LOGO = [
    r"  _    //   //    __ _ ",
    r" | |_ //   //    / _` |",
    r" | __//   //    | (_| |",
    r"  \__//   //     \__,_|",
]

_CODES = {
    "reset": "0",
    "bold": "1",
    "dim": "2",
    "red": "31",
    "green": "32",
    "yellow": "33",
    "blue": "34",
    "magenta": "35",
    "cyan": "36",
}

# Short, kind lines in Ank's voice. Every success line starts with a check mark,
# so it is easy to spot (and easy to test).
SUCCESS_LINES = [
    "Nice!",
    "You got it!",
    "Clean work.",
    "Exactly right.",
    "That's the one!",
    "Smooth.",
]

STUCK_LINES = [
    "Stuck? Type hint and I'll give you a clue.",
    "Stuck? Type hint. Asking for help is a pro move.",
]


def colors_wanted(stream: TextIO, no_color_flag: bool = False) -> bool:
    """Return True if ANSI colors should be used on ``stream``."""
    if no_color_flag:
        return False
    if os.environ.get("NO_COLOR"):
        return False
    if os.environ.get("TERM") == "dumb":
        return False
    try:
        return stream.isatty()
    except (AttributeError, ValueError):
        return False


def _supports_unicode(stream: TextIO) -> bool:
    encoding = (getattr(stream, "encoding", None) or "").lower()
    return "utf" in encoding


class UI:
    """All printing goes through this class, so tests can capture it."""

    def __init__(
        self,
        out: Optional[TextIO] = None,
        color: Optional[bool] = None,
        readline_active: bool = False,
    ) -> None:
        self.out = out if out is not None else sys.stdout
        self.color = colors_wanted(self.out) if color is None else color
        self.readline_active = readline_active
        if _supports_unicode(self.out):
            self.sym = {"done": "✓", "progress": "▶", "new": "·", "missing": "!",
                        "ok": "✓", "arrow": "›"}
        else:
            self.sym = {"done": "+", "progress": ">", "new": ".", "missing": "!",
                        "ok": "+", "arrow": ">"}

    # ----- basics ---------------------------------------------------------

    def style(self, text: str, *names: str) -> str:
        if not self.color or not names:
            return text
        codes = ";".join(_CODES[n] for n in names)
        return "\033[%sm%s\033[0m" % (codes, text)

    def prompt_style(self, text: str, *names: str) -> str:
        """Like style(), but safe for input() prompts when readline is active.

        readline needs to know which bytes are invisible, or line editing
        breaks; \\001 and \\002 mark them.
        """
        if not self.color or not names:
            return text
        codes = ";".join(_CODES[n] for n in names)
        if self.readline_active:
            return "\001\033[%sm\002%s\001\033[0m\002" % (codes, text)
        return "\033[%sm%s\033[0m" % (codes, text)

    def width(self) -> int:
        try:
            cols = shutil.get_terminal_size((80, 24)).columns
        except (OSError, ValueError):
            cols = 80
        return max(40, min(cols, 88))

    def wrap(self, text: str, indent: str = "") -> str:
        """Wrap every line of ``text`` on its own (keeps blank lines)."""
        width = self.width()
        lines = []
        for line in text.split("\n"):
            if not line.strip():
                lines.append("")
                continue
            # Keep the line's own leading spaces (used for examples).
            lead = line[: len(line) - len(line.lstrip(" "))]
            lines.append(
                textwrap.fill(
                    line.strip(),
                    width=width,
                    initial_indent=indent + lead,
                    subsequent_indent=indent + lead,
                    break_long_words=False,
                    break_on_hyphens=False,
                )
            )
        return "\n".join(lines)

    def print(self, text: str = "") -> None:
        self.out.write(text + "\n")
        self.out.flush()

    def raw(self, text: str) -> None:
        """Print command output exactly as it is."""
        if not text:
            return
        self.out.write(text if text.endswith("\n") else text + "\n")
        self.out.flush()

    # ----- message kinds --------------------------------------------------

    def say(self, text: str) -> None:
        """A message from Ank, the mentor."""
        name = self.style("ank " + self.sym["arrow"], "magenta", "bold")
        wrapped = self.wrap(text, indent="      ")
        self.print(name + " " + wrapped.lstrip(" "))

    def info(self, text: str) -> None:
        self.print(self.wrap(text))

    def dim(self, text: str) -> None:
        self.print(self.style(self.wrap(text), "dim"))

    def success(self, text: Optional[str] = None) -> None:
        line = text or random.choice(SUCCESS_LINES)
        self.print(self.style(self.sym["ok"] + " " + line, "green", "bold"))

    def warn(self, text: str) -> None:
        self.print(self.style(self.wrap(text), "yellow"))

    def error(self, text: str) -> None:
        self.print(self.style(self.wrap(text), "red"))

    def header(self, text: str) -> None:
        self.print("")
        self.print(self.style(text, "cyan", "bold"))
        self.print(self.style("─" * min(len(text), self.width())
                              if _supports_unicode(self.out) else "-" * len(text), "cyan"))

    def stuck(self) -> None:
        self.say(random.choice(STUCK_LINES))

    def splash(self) -> None:
        self.print("")
        for line in LOGO:
            self.print("   " + self.style(line, "green", "bold"))
        self.print("")
        self.print("   " + self.style("Welcome to Terminal Academy", "bold")
                   + self.style("  v" + __version__, "dim"))
        self.print("")
        self.say("Hi, I'm Ank, your terminal mentor. You type real commands, "
                 "I check them. Everything happens in a practice folder that "
                 "protects you from accidents, so go ahead and experiment.")
        self.print(self.style("   Commands are real and run on your computer. Terminal Academy "
                              "comes with NO WARRANTY; you use it at your own risk "
                              "(see LICENSE).", "dim"))
