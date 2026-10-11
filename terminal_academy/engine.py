"""One lesson, played step by step (LESSONS_PLAN 2.7 and 2.9).

``LessonSession`` keeps its input and output injectable (``input_func`` and a
``UI`` object), so tests can drive a whole lesson without a terminal.
"""

from __future__ import annotations

import os
from typing import Any, Callable, Dict, List, Optional

from terminal_academy import checks, explain, safety
from terminal_academy.lessons import (
    Lesson,
    missing_tools,
    setup_sandbox,
)
from terminal_academy.progress import Progress
from terminal_academy.shell import DEFAULT_TIMEOUT, Shell
from terminal_academy.ui import UI

DONE = "done"
MENU = "menu"
QUIT = "quit"

IN_APP = ("hint", "skip", "reset", "lessons", "menu", "help", "quit", "exit")

HELP_TEXT = """Commands you can type at any time:
  hint              get a clue (type it again for the next one)
  skip              skip this step (I'll do it for you)
  reset             start this lesson again with a fresh sandbox
  explain <cmd>     a short note about a command, e.g. explain ls
  lessons           show all lessons
  menu              back to the main menu (your progress is saved)
  help              show the task again and this list
  quit              save and exit (Ctrl+D works too)
Everything else is a real command and runs in your sandbox."""


class _Quit(Exception):
    """Raised when the student presses Ctrl+D."""


class LessonSession:
    def __init__(
        self,
        lesson: Lesson,
        home: str,
        progress: Progress,
        ui: UI,
        input_func: Callable[[str], str] = input,
        timeout: float = DEFAULT_TIMEOUT,
        use_tty: Optional[bool] = None,
        show_lessons: Optional[Callable[[], None]] = None,
    ) -> None:
        self.lesson = lesson
        self.lid = lesson["id"]
        self.steps: List[Dict[str, Any]] = lesson["steps"]
        self.progress = progress
        self.ui = ui
        self.input_func = input_func
        self.show_lessons = show_lessons
        self.sandbox = os.path.join(home, "sandbox", self.lid)
        self.state_dir = os.path.join(home, "state", self.lid)
        os.makedirs(os.path.dirname(self.sandbox), exist_ok=True)
        os.makedirs(self.state_dir, exist_ok=True)
        self.shell = Shell(self.sandbox, self.state_dir, timeout=timeout, use_tty=use_tty)
        self.step = 0
        self.hint_index = 0
        self.attempts = 0
        self.ctx = checks.Context(sandbox=self.shell.sandbox, cwd=self.shell.cwd)

    # ----- input helpers --------------------------------------------------

    def _read(self, prompt: str) -> str:
        try:
            return self.input_func(prompt)
        except EOFError:
            self.ui.print("")
            raise _Quit()

    def confirm(self, question: str) -> bool:
        try:
            answer = self._read(question + " (y/n) ")
        except KeyboardInterrupt:
            self.ui.print("")
            return False
        return answer.strip().lower() in ("y", "yes")

    # ----- lesson lifecycle -----------------------------------------------

    def _fresh_start(self) -> None:
        self.shell.cleanup()
        setup_sandbox(self.lesson, self.shell.sandbox)
        self.shell.reset_state()
        self.progress.start(self.lid)
        self.step = 0
        self._new_step()

    def _new_step(self) -> None:
        self.hint_index = 0
        self.attempts = 0
        self.ctx = checks.Context(sandbox=self.shell.sandbox, cwd=self.shell.cwd)

    def _choose_start(self) -> None:
        entry = self.progress.entry(self.lid)
        status = entry["status"]
        saved_step = int(entry.get("step", 0))
        can_continue = (
            status == "in_progress"
            and os.path.isdir(self.sandbox)
            and 0 <= saved_step < len(self.steps)
        )
        if status == "done":
            self.ui.say("You already finished this lesson. Let's play it again "
                        "with a fresh sandbox!")
            self._fresh_start()
            return
        if can_continue:
            self.ui.say("Welcome back! You stopped at step %d of %d."
                        % (saved_step + 1, len(self.steps)))
            try:
                answer = self._read("Continue where you stopped (c), or start again (s)? [c/s] ")
            except KeyboardInterrupt:
                answer = "c"
                self.ui.print("")
            if answer.strip().lower() in ("s", "start", "start again", "r", "restart"):
                self._fresh_start()
            else:
                self.step = saved_step
                self._new_step()
            return
        self._fresh_start()

    def run(self) -> str:
        """Play the lesson. Returns "done", "menu" or "quit"."""
        try:
            self.ui.header("Lesson %s · %s" % (self.lid[:2].lstrip("0") or "0",
                                               self.lesson["title"]))
            self._choose_start()
            self._intro()
            return self._loop()
        except _Quit:
            return self._leave(QUIT)

    def _intro(self) -> None:
        self.ui.info(self.lesson["intro"])
        missing = missing_tools(self.lesson.get("requires"))
        if missing:
            self.ui.warn("Heads up: this lesson uses %s, which I can't find on "
                         "your computer. Some steps may not work."
                         % ", ".join(missing))
        self.ui.dim("Type help to see what you can do, or hint if you get stuck.")

    def _leave(self, outcome: str) -> str:
        self.shell.cleanup()
        return outcome

    def _show_step(self) -> None:
        step = self.steps[self.step]
        self.ui.print("")
        label = "Step %d of %d" % (self.step + 1, len(self.steps))
        if step.get("optional"):
            label += " (bonus)"
        self.ui.print(self.ui.style(label, "cyan", "bold"))
        self.ui.say(step["instruction"])

    def _advance(self, skipped: bool = False) -> None:
        step = self.steps[self.step]
        if skipped and not step.get("optional"):
            self.progress.add_skipped(self.lid, self.step)
        self.step += 1
        if self.step < len(self.steps):
            self.progress.set_step(self.lid, self.step)
        self._new_step()

    def _finish(self) -> str:
        self.progress.finish(self.lid, len(self.steps))
        self.ui.print("")
        self.ui.success("Lesson complete: %s" % self.lesson["title"])
        if self.lesson.get("outro"):
            self.ui.say(self.lesson["outro"])
        return self._leave(DONE)

    def prompt(self) -> str:
        # The text stays "academy:~/folder $ " (the README shows it);
        # only the colors are the brand ones.
        return (self.ui.prompt_style("academy", "lime", "bold")
                + self.ui.prompt_style(":", "yellow", "bold")
                + self.ui.prompt_style(self.shell.relative_cwd(), "cyan", "bold")
                + " $ ")

    # ----- main loop ------------------------------------------------------

    def _loop(self) -> str:
        shown = -1
        while self.step < len(self.steps):
            step = self.steps[self.step]
            if shown != self.step:
                self._show_step()
                shown = self.step
                missing = missing_tools(step.get("requires"))
                if missing:
                    self.ui.say("This step needs %s, which is not installed on your "
                                "computer. No problem, we'll skip it."
                                % ", ".join(missing))
                    self._advance(skipped=False)
                    continue
            try:
                line = self._read(self.prompt())
            except KeyboardInterrupt:
                self.ui.print("")
                self.ui.dim("Type quit to exit.")
                continue
            try:
                outcome = self._handle(line)
            except KeyboardInterrupt:
                self.ui.print("")
                self.ui.dim("Type quit to exit.")
                continue
            if outcome in (MENU, QUIT):
                return self._leave(outcome)
            if outcome == "reset":
                shown = -1
        return self._finish()

    def _handle(self, line: str) -> Optional[str]:
        """Handle one input line. May return MENU, QUIT or "reset"."""
        text = line.strip()
        if not text:
            return None
        word = text.lower()
        if word in IN_APP:
            return self._in_app(word)
        if word == "explain" or word.startswith("explain "):
            self._explain(text[len("explain"):].strip())
            return None
        self.run_command(text)
        return None

    def _in_app(self, word: str) -> Optional[str]:
        step = self.steps[self.step]
        if word == "hint":
            hints = step["hints"]
            hint = hints[min(self.hint_index, len(hints) - 1)]
            if self.hint_index < len(hints):
                self.progress.add_hint(self.lid)
            self.hint_index += 1
            prefix = "Hint %d/%d: " % (min(self.hint_index, len(hints)), len(hints))
            self.ui.say(prefix + hint)
            return None
        if word == "skip":
            if not self.confirm("Skip this step? I'll do it for you."):
                self.ui.say("OK, keep going. You've got this.")
                return None
            self._skip()
            return None
        if word == "reset":
            if not self.confirm("Start this lesson again? Your sandbox will be "
                                "rebuilt from scratch."):
                return None
            self._fresh_start()
            self.ui.say("Fresh sandbox, back to step 1.")
            return "reset"
        if word == "lessons":
            if self.show_lessons:
                self.show_lessons()
            return None
        if word == "menu":
            self.ui.say("Progress saved. See you in the menu!")
            return MENU
        if word == "help":
            self.ui.say(step["instruction"])
            self.ui.dim(HELP_TEXT)
            return None
        if word in ("quit", "exit"):
            self.ui.say("Progress saved. See you next time!")
            return QUIT
        return None

    def _explain(self, query: str) -> None:
        if not query:
            self.ui.say("I have notes about these commands: "
                        + ", ".join(explain.topics())
                        + ". Example: explain grep")
            return
        note = explain.lookup(query)
        if note:
            self.ui.say(note)
        else:
            self.ui.say("I don't have a note about %r yet. Try: man %s"
                        % (query, query.split()[0]))

    def _skip(self) -> None:
        step = self.steps[self.step]
        solution = (step.get("solution") or "").strip()
        if solution:
            self.ui.say("Here is one way to do it:")
            for line in solution.split("\n"):
                self.ui.print("    " + self.ui.style(line, "bold"))
            for line in solution.split("\n"):
                if line.strip():
                    result = self.shell.run(line, interactive=False)
                    if result.stdout.strip() or result.stderr.strip():
                        self.ui.dim((result.stdout + result.stderr).rstrip("\n"))
            self.ui.dim("(I ran it for you, so your sandbox is ready for the next step.)")
        self.ui.say("Step skipped. " + step["explain"])
        self._advance(skipped=True)

    # ----- real commands --------------------------------------------------

    def run_command(self, command: str) -> bool:
        """Run a shell command, show the output, check the step.

        Returns True if the current step's check passed.
        """
        reason = safety.check_command(command, sandbox=self.shell.sandbox,
                                      cwd=self.shell.cwd)
        if reason:
            self.ui.warn("Blocked: " + reason)
            return False
        result = self.shell.run(command)
        self.ui.raw(result.stdout)
        if result.stderr:
            self.ui.raw(self.ui.style(result.stderr.rstrip("\n"), "red"))
        if result.truncated:
            self.ui.dim("(That was a lot of output, so I only showed the beginning.)")
        if result.timed_out:
            self.ui.warn("That took too long, so I stopped it. "
                         "Tip: add & to run it in the background.")
        if result.interrupted:
            self.ui.dim("Stopped.")
        if result.moved_back:
            self.ui.warn("That folder is outside your sandbox, so I moved you back.")

        self.ctx = checks.Context(
            sandbox=self.shell.sandbox,
            cwd=result.cwd,
            command=command,
            stdout=result.stdout,
            stderr=result.stderr,
        )
        step = self.steps[self.step]
        if checks.evaluate(step["check"], self.ctx):
            self.ui.success()
            self.ui.say(step["explain"])
            self._advance()
            return True
        self.attempts += 1
        if self.attempts % 3 == 0:
            self.ui.stuck()
        return False
