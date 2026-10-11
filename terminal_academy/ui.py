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
import time
from typing import Callable, List, Optional, TextIO

from terminal_academy import __version__

# ----- brand -----------------------------------------------------------------
#
# The big wordmark uses a block font in the style of figlet's "ANSI Shadow".
# Every glyph is 6 rows high; all rows of one glyph have the same width.
# "█" is the letter itself, the box-drawing characters are its shadow.

_FONT = {
    "T": ["████████╗", "╚══██╔══╝", "   ██║   ", "   ██║   ", "   ██║   ", "   ╚═╝   "],
    "E": ["███████╗", "██╔════╝", "█████╗  ", "██╔══╝  ", "███████╗", "╚══════╝"],
    "R": ["██████╗ ", "██╔══██╗", "██████╔╝", "██╔══██╗", "██║  ██║", "╚═╝  ╚═╝"],
    "M": ["███╗   ███╗", "████╗ ████║", "██╔████╔██║", "██║╚██╔╝██║",
          "██║ ╚═╝ ██║", "╚═╝     ╚═╝"],
    "I": ["██╗", "██║", "██║", "██║", "██║", "╚═╝"],
    "N": ["███╗   ██╗", "████╗  ██║", "██╔██╗ ██║", "██║╚██╗██║", "██║ ╚████║",
          "╚═╝  ╚═══╝"],
    "A": [" █████╗ ", "██╔══██╗", "███████║", "██╔══██║", "██║  ██║", "╚═╝  ╚═╝"],
    "L": ["██╗     ", "██║     ", "██║     ", "██║     ", "███████╗", "╚══════╝"],
    "C": [" ██████╗", "██╔════╝", "██║     ", "██║     ", "╚██████╗", " ╚═════╝"],
    "D": ["██████╗ ", "██╔══██╗", "██║  ██║", "██║  ██║", "██████╔╝", "╚═════╝ "],
    "Y": ["██╗   ██╗", "╚██╗ ██╔╝", " ╚████╔╝ ", "  ╚██╔╝  ", "   ██║   ", "   ╚═╝   "],
}

_SHADOW = "╗╔╝╚║═"


def _render_word(word: str) -> List[str]:
    rows = []
    for row in range(6):
        rows.append("".join(_FONT[ch][row] for ch in word).rstrip())
    return rows


# Two lines, so each one fits in 80 columns (65 and 60 characters wide).
BIG_LOGO = _render_word("TERMINAL") + _render_word("ACADEMY")

# The same letters for terminals that cannot show block characters:
# the letters become "#" and the shadow is dropped (so is the shadow-only row
# under each word, except for one blank line between the two words).
BIG_LOGO_ASCII = [
    "".join("#" if ch == "█" else " " if ch in _SHADOW else ch for ch in line).rstrip()
    for line in BIG_LOGO[0:5] + [""] + BIG_LOGO[6:11]
]

# The compact mark for narrow terminals (plain ASCII, works everywhere).
LOGO = [
    r"  _    //   //    __ _ ",
    r" | |_ //   //    / _` |",
    r" | __//   //    | (_| |",
    r"  \__//   //     \__,_|",
]

TAGLINE = "Learn the terminal by doing."

LOGO_INDENT = "  "
BIG_LOGO_WIDTH = max(len(line) for line in BIG_LOGO) + len(LOGO_INDENT)

# A vertical gradient over the 12 logo rows, Yellow (221) to Pink (204),
# in the 256-color palette.
_GRADIENT = [221, 221, 221, 215, 215, 215, 209, 209, 209, 204, 204, 204]

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
    # Brand names, with plain 8-color fallbacks.
    "lime": "32",
    "pink": "35",
    "ink": "2",
    "paper": "97",
}

# On 256-color terminals, the basic colors become the brand colors
# (see the brand spec: Yellow 221, Pink 204, Cyan 80, Lime 149, dim 61).
_CODES_256 = dict(_CODES)
_CODES_256.update({
    "green": "38;5;149",
    "lime": "38;5;149",
    "yellow": "38;5;221",
    "magenta": "38;5;204",
    "pink": "38;5;204",
    "cyan": "38;5;80",
    "blue": "38;5;80",
    "ink": "38;5;61",
    "paper": "38;5;230",
})

# Typographic symbols and what to print instead when the terminal has no UTF-8.
_ASCII_FALLBACK = str.maketrans({"·": "-", "…": "...", "─": "-", "—": "-", "–": "-",
                                 "’": "'", "‘": "'", "“": '"', "”": '"'})

BOOT_STEPS = [
    "preparing your sandbox",
    "loading {n} lessons",
    "checking your progress",
    "waking up Ank",
]

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


def supports_256_colors() -> bool:
    """Best guess whether the terminal knows the 256-color palette."""
    term = os.environ.get("TERM", "")
    if "256" in term or os.environ.get("COLORTERM") in ("truecolor", "24bit"):
        return True
    # macOS Terminal, iTerm2, VS Code and friends all do 256 colors.
    return bool(os.environ.get("TERM_PROGRAM"))


def animation_wanted(stream: TextIO, color: bool) -> bool:
    """The boot animation only runs in a real, colorful, interactive terminal.

    It is off when colors are off (NO_COLOR, --no-color, TERM=dumb, not a
    terminal), on CI, and with TERMINAL_ACADEMY_NO_ANIMATION set.
    """
    if not color:
        return False
    for name in ("TERMINAL_ACADEMY_NO_ANIMATION", "NO_COLOR", "CI"):
        if os.environ.get(name):
            return False
    try:
        return stream.isatty()
    except (AttributeError, ValueError):
        return False


def terminal_columns() -> int:
    try:
        return shutil.get_terminal_size((80, 24)).columns
    except (OSError, ValueError):
        return 80


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
        self.unicode = _supports_unicode(self.out)
        self.codes = _CODES_256 if supports_256_colors() else _CODES
        if self.unicode:
            self.sym = {"done": "✓", "progress": "▶", "new": "·", "missing": "!",
                        "ok": "✓", "arrow": "›"}
        else:
            self.sym = {"done": "+", "progress": ">", "new": ".", "missing": "!",
                        "ok": "+", "arrow": ">"}

    # ----- basics ---------------------------------------------------------

    def _sgr(self, names) -> str:
        return ";".join(self.codes[n] if n in self.codes else "38;5;%s" % n
                        for n in names)

    def style(self, text: str, *names) -> str:
        """Color ``text``. Names come from _CODES; a number is a 256-color index."""
        if not self.color or not names or not text:
            return text
        return "\033[%sm%s\033[0m" % (self._sgr(names), text)

    def prompt_style(self, text: str, *names: str) -> str:
        """Like style(), but safe for input() prompts when readline is active.

        readline needs to know which bytes are invisible, or line editing
        breaks; \\001 and \\002 mark them.
        """
        if not self.color or not names:
            return text
        codes = self._sgr(names)
        if self.readline_active:
            return "\001\033[%sm\002%s\001\033[0m\002" % (codes, text)
        return "\033[%sm%s\033[0m" % (codes, text)

    def mark(self) -> str:
        """The short brand mark: t//a, with the slashes in Yellow."""
        return (self.style("t", "paper", "bold") + self.style("//", "yellow", "bold")
                + self.style("a", "paper", "bold"))

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
        if not self.unicode:
            text = text.translate(_ASCII_FALLBACK)
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
        name = self.style("ank " + self.sym["arrow"], "pink", "bold")
        wrapped = self.wrap(text, indent="      ")
        self.print(name + " " + wrapped.lstrip(" "))

    def info(self, text: str) -> None:
        self.print(self.wrap(text))

    def dim(self, text: str) -> None:
        self.print(self.style(self.wrap(text), "dim"))

    def success(self, text: Optional[str] = None) -> None:
        line = text or random.choice(SUCCESS_LINES)
        self.print(self.style(self.sym["ok"] + " " + line, "lime", "bold"))

    def warn(self, text: str) -> None:
        self.print(self.style(self.wrap(text), "yellow"))

    def error(self, text: str) -> None:
        self.print(self.style(self.wrap(text), "red"))

    def header(self, text: str) -> None:
        """A lesson title, with the t//a mark in front."""
        rule = "─" if self.unicode else "-"
        self.print("")
        self.print(self.mark() + "  " + self.style(text, "cyan", "bold"))
        self.print(self.style(rule * min(len(text) + 6, self.width()), "ink"))

    def stuck(self) -> None:
        self.say(random.choice(STUCK_LINES))

    # ----- logo, welcome screen and boot animation -------------------------

    def logo_lines(self, columns: Optional[int] = None) -> List[str]:
        """The logo, ready to print: big if it fits, the compact mark if not.

        Without UTF-8 the big logo is drawn with "#" instead of blocks.
        """
        cols = terminal_columns() if columns is None else columns
        if cols < BIG_LOGO_WIDTH:
            return [LOGO_INDENT + self._color_mark_line(line) for line in LOGO]
        source = BIG_LOGO if self.unicode else BIG_LOGO_ASCII
        return [LOGO_INDENT + self._color_logo_line(line, _GRADIENT[i])
                for i, line in enumerate(source)]

    def _color_logo_line(self, line: str, color: int) -> str:
        """Blocks in the gradient color, the shadow in dim Ink."""
        if not self.color:
            return line
        out = []
        run, kind = "", None
        for ch in line:
            k = "shadow" if ch in _SHADOW else "space" if ch == " " else "block"
            if k != kind and run:
                out.append(self._logo_run(run, kind, color))
                run = ""
            run += ch
            kind = k
        if run:
            out.append(self._logo_run(run, kind, color))
        return "".join(out)

    def _logo_run(self, run: str, kind: Optional[str], color: int) -> str:
        if kind == "space":
            return run
        if kind == "shadow":
            return self.style(run, "ink")
        if self.codes is _CODES_256:
            return self.style(run, str(color), "bold")
        return self.style(run, "yellow", "bold")

    def _color_mark_line(self, line: str) -> str:
        if not self.color:
            return line
        return "".join(self.style(ch, "yellow", "bold") if ch == "/"
                       else self.style(ch, "paper", "bold") if ch != " " else ch
                       for ch in line)

    def splash(self) -> None:
        """The welcome screen at the top of the main menu."""
        self.print("")
        for line in self.logo_lines():
            self.print(line)
        self.print("")
        dot = " · " if self.unicode else " - "
        self.print(LOGO_INDENT + self.mark() + "  "
                   + self.style("Welcome to Terminal Academy", "bold")
                   + self.style("  v" + __version__, "ink"))
        more = dot + "Real commands. Safe practice folder. Instant feedback."
        if len(LOGO_INDENT + TAGLINE + more) > terminal_columns():
            more = ""
        self.print(LOGO_INDENT + self.style(TAGLINE, "yellow") + self.style(more, "dim"))
        self.print("")
        self.say("Hi, I'm Ank, your terminal mentor. You type real commands, "
                 "I check them. Everything happens in a practice folder that "
                 "protects you from accidents, so go ahead and experiment.")
        self.print(self.style(self.wrap(
            "Commands are real and run on your computer. Terminal Academy "
            "comes with NO WARRANTY; you use it at your own risk "
            "(see LICENSE).", indent="      "), "dim"))
        self.print("")
        self.print(LOGO_INDENT + self.style(self.sym["arrow"], "cyan", "bold") + " "
                   + self.style("pick a lesson number" + dot + "help inside a lesson"
                                + dot + "q to quit", "dim"))

    def boot(self, lesson_count: int,
             sleep: Callable[[float], None] = time.sleep,
             enabled: Optional[bool] = None) -> bool:
        """A short boot animation (~0.8 s). Returns True if it was shown.

        It only runs in an interactive, colorful terminal (see
        animation_wanted). Ctrl+C skips it.
        """
        if enabled is None:
            enabled = animation_wanted(self.out, self.color)
        if not enabled:
            return False
        if self.unicode:
            frames, full, empty, ell = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏", "━", "─", "…"
        else:
            frames, full, empty, ell = "|/-\\", "=", "-", "..."
        steps = [text.format(n=lesson_count) for text in BOOT_STEPS]
        per_step, delay, bar_len = 6, 0.03, 16
        total = len(steps) * per_step
        write = self.out.write
        tick = 0
        try:
            write("\033[?25l")  # hide the cursor
            for text in steps:
                for _ in range(per_step):
                    tick += 1
                    filled = bar_len * tick // total
                    bar = (self.style(full * filled, "yellow")
                           + self.style(empty * (bar_len - filled), "ink"))
                    write("\r\033[K  " + self.style(frames[tick % len(frames)], "cyan", "bold")
                          + " " + bar + "  " + self.style(text + ell, "dim"))
                    self.out.flush()
                    sleep(delay)
            write("\r\033[K  " + self.style(self.sym["ok"], "lime", "bold") + " "
                  + self.style(full * bar_len, "lime") + "  "
                  + self.style("ready", "lime", "bold"))
            self.out.flush()
            sleep(0.18)
        except KeyboardInterrupt:
            pass
        finally:
            try:
                write("\r\033[K\033[?25h")  # clean line, show the cursor again
                self.out.flush()
            except KeyboardInterrupt:
                pass
        return True
