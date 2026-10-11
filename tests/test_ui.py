"""The look of the app: logo, welcome screen, colors and the boot animation."""

import io
import os
import sys
import unittest
from unittest import mock

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

from terminal_academy import ui as ui_module  # noqa: E402
from terminal_academy.ui import (  # noqa: E402
    BIG_LOGO,
    BIG_LOGO_ASCII,
    LOGO,
    UI,
    animation_wanted,
)


class FakeStream(io.StringIO):
    """A StringIO with a chosen encoding, that can pretend to be a terminal."""

    def __init__(self, encoding="utf-8", tty=False):
        super().__init__()
        self._encoding = encoding
        self._tty = tty

    @property
    def encoding(self):
        return self._encoding

    def isatty(self):
        return self._tty


def no_sleep(_seconds):
    raise AssertionError("must not sleep")


class LogoTest(unittest.TestCase):
    def test_logo_lines_fit_80_columns(self):
        for logo in (BIG_LOGO, BIG_LOGO_ASCII, LOGO):
            for line in logo:
                self.assertLessEqual(len(ui_module.LOGO_INDENT + line), 80, line)
        self.assertLessEqual(ui_module.BIG_LOGO_WIDTH, 80)

    def test_logo_rows_line_up(self):
        for glyph in ui_module._FONT.values():
            self.assertEqual(len(glyph), 6)
            self.assertEqual(len(set(len(row) for row in glyph)), 1, glyph)

    def test_big_logo_with_utf8(self):
        lines = UI(out=FakeStream("utf-8"), color=False).logo_lines(columns=100)
        self.assertEqual(lines, [ui_module.LOGO_INDENT + l for l in BIG_LOGO])
        self.assertIn("█", "".join(lines))

    def test_ascii_fallback_without_utf8(self):
        for encoding in ("ascii", "ANSI_X3.4-1968", "latin-1"):
            lines = UI(out=FakeStream(encoding), color=True).logo_lines(columns=100)
            text = "".join(lines)
            text.encode("ascii")  # would raise if a block character slipped through
            self.assertIn("#", text)

    def test_compact_mark_on_narrow_terminals(self):
        lines = UI(out=FakeStream("utf-8"), color=False).logo_lines(columns=60)
        self.assertEqual(lines, [ui_module.LOGO_INDENT + l for l in LOGO])

    def test_no_escape_codes_when_colors_are_off(self):
        out = FakeStream("utf-8")
        screen = UI(out=out, color=False)
        screen.splash()
        screen.header("Lesson 1 · First Steps")
        screen.success()
        self.assertNotIn("\033", out.getvalue())
        self.assertNotIn("\033", screen.mark())

    def test_colors_on_use_brand_palette(self):
        with mock.patch.dict(os.environ, {"TERM": "xterm-256color"}):
            screen = UI(out=FakeStream("utf-8"), color=True)
        self.assertIn("38;5;221", screen.mark())  # the Yellow slashes
        logo = "".join(screen.logo_lines(columns=100))
        self.assertIn("38;5;221", logo)
        self.assertIn("38;5;204", logo)


class SplashTest(unittest.TestCase):
    def splash_text(self, encoding="utf-8"):
        out = FakeStream(encoding)
        UI(out=out, color=False).splash()
        return out.getvalue()

    def test_splash_keeps_welcome_and_warranty(self):
        text = " ".join(self.splash_text().split())  # undo the line wrapping
        self.assertIn("Welcome to Terminal Academy", text)
        self.assertIn("NO WARRANTY", text)
        self.assertIn("Commands are real and run on your computer.", text)
        self.assertIn("Learn the terminal by doing.", text)
        self.assertIn("t//a", text)

    def test_splash_is_ascii_without_utf8(self):
        self.splash_text("ascii").encode("ascii")


class AnimationTest(unittest.TestCase):
    def clean_env(self, **extra):
        env = {k: v for k, v in os.environ.items()
               if k not in ("NO_COLOR", "CI", "TERMINAL_ACADEMY_NO_ANIMATION")}
        env.update(extra)
        return mock.patch.dict(os.environ, env, clear=True)

    def test_no_animation_when_not_a_terminal(self):
        out = FakeStream(tty=False)
        with self.clean_env():
            self.assertFalse(animation_wanted(out, True))
            self.assertFalse(UI(out=out, color=True).boot(15, sleep=no_sleep))
        self.assertEqual(out.getvalue(), "")

    def test_no_animation_with_env_switches(self):
        for name in ("TERMINAL_ACADEMY_NO_ANIMATION", "NO_COLOR", "CI"):
            out = FakeStream(tty=True)
            with self.clean_env(**{name: "1"}):
                self.assertFalse(UI(out=out, color=True).boot(15, sleep=no_sleep), name)
            self.assertEqual(out.getvalue(), "", name)

    def test_no_animation_without_colors(self):
        out = FakeStream(tty=True)
        with self.clean_env():
            self.assertFalse(UI(out=out, color=False).boot(15, sleep=no_sleep))
        self.assertEqual(out.getvalue(), "")

    def test_animation_in_a_terminal(self):
        out = FakeStream(tty=True)
        naps = []
        with self.clean_env():
            self.assertTrue(UI(out=out, color=True).boot(15, sleep=naps.append))
        text = out.getvalue()
        self.assertIn("loading 15 lessons", text)
        self.assertIn("ready", text)
        self.assertTrue(text.endswith("\r\033[K\033[?25h"))  # line cleaned, cursor back
        self.assertLessEqual(sum(naps), 1.2)

    def test_ctrl_c_skips_the_animation(self):
        out = FakeStream(tty=True)

        def interrupt(_seconds):
            raise KeyboardInterrupt

        with self.clean_env():
            self.assertTrue(UI(out=out, color=True).boot(15, sleep=interrupt))
        self.assertTrue(out.getvalue().endswith("\033[?25h"))


if __name__ == "__main__":
    unittest.main()
