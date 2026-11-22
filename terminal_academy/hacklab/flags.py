"""Flags: the secret token a player must find in each level.

Design goals (from the project rules):

- **Random per run.** Every time you start a level, a brand-new flag is made.
  You cannot look up the answer from a friend or a past run.
- **The host never keeps the flag in clear text.** We store only its SHA-256
  hash. When the player submits a flag, we hash their answer and compare the
  hashes. This is the same idea a login system uses for passwords.
- **Never in the repo, never in an environment variable.** The flag is written
  to a temporary file and copied into the container with ``docker cp`` (see
  ``session.py``). It is not a build argument (which would bake it into an
  image layer) and not an ``-e NAME=value`` (which ``docker inspect`` would
  reveal).

A flag looks like ``FLAG{3f9a...}`` so it is easy to recognise on screen.
"""

from __future__ import annotations

import hashlib
import json
import os
import secrets
from typing import Optional

FLAG_PREFIX = "FLAG{"
FLAG_SUFFIX = "}"
# 16 random bytes -> 32 hex characters. Far too many to guess.
RANDOM_BYTES = 16


def new_flag() -> str:
    """Return a fresh random flag, e.g. ``FLAG{a1b2...}``.

    ``secrets.token_hex`` uses the operating system's cryptographic random
    source, so flags are unpredictable.
    """
    return FLAG_PREFIX + secrets.token_hex(RANDOM_BYTES) + FLAG_SUFFIX


def normalize(flag: str) -> str:
    """Tidy a submitted flag before checking it.

    Players copy flags by hand, so we forgive leading/trailing spaces and a
    trailing newline. We do NOT change the inside, because the flag is
    case-sensitive on purpose (it teaches that secrets are exact).
    """
    return flag.strip()


def sha256_hex(flag: str) -> str:
    """The SHA-256 hash of a flag, as lowercase hex."""
    return hashlib.sha256(normalize(flag).encode("utf-8")).hexdigest()


def looks_like_flag(text: str) -> bool:
    """A cheap shape check: does this look like ``FLAG{...}``?"""
    text = normalize(text)
    return text.startswith(FLAG_PREFIX) and text.endswith(FLAG_SUFFIX) and len(text) > len(
        FLAG_PREFIX + FLAG_SUFFIX
    )


class FlagStore:
    """Remembers the SHA-256 of the current flag for each level, on the host.

    The file holds only hashes, so reading it does not reveal any flag. It
    lives next to the player's progress (``~/.terminal-academy/``).
    """

    def __init__(self, path: str) -> None:
        self.path = path
        self.data = self._load()

    def _load(self) -> dict:
        try:
            with open(self.path, encoding="utf-8") as fh:
                data = json.load(fh)
            if isinstance(data, dict):
                return data
        except (OSError, ValueError):
            pass
        return {}

    def _save(self) -> None:
        folder = os.path.dirname(os.path.abspath(self.path))
        os.makedirs(folder, exist_ok=True)
        tmp = self.path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as fh:
            json.dump(self.data, fh, indent=2, sort_keys=True)
        os.replace(tmp, self.path)

    def set_flag(self, level_id: str, flag: str) -> None:
        """Store only the hash of ``flag`` for ``level_id``."""
        self.data[level_id] = {"sha256": sha256_hex(flag)}
        self._save()

    def expected_hash(self, level_id: str) -> Optional[str]:
        entry = self.data.get(level_id)
        if isinstance(entry, dict):
            return entry.get("sha256")
        return None

    def check(self, level_id: str, submitted: str) -> bool:
        """True if ``submitted`` hashes to the stored hash for ``level_id``.

        Uses :func:`secrets.compare_digest` so the comparison takes the same
        time whether the first or the last character is wrong (it does not
        leak where the mistake is). That is overkill for a learning game, but
        it is the correct habit, and this project teaches good habits.
        """
        expected = self.expected_hash(level_id)
        if not expected:
            return False
        return secrets.compare_digest(expected, sha256_hex(submitted))

    def clear(self, level_id: str) -> None:
        if level_id in self.data:
            del self.data[level_id]
            self._save()
