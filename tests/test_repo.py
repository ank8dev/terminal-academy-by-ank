"""Repository sanity checks: landing page files, lesson JSON, launcher."""

import json
import os
import stat
import sys
import unittest

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

SITE = os.path.join(REPO, "site")
LESSONS = os.path.join(REPO, "terminal_academy", "lessons")


class RepoTest(unittest.TestCase):
    def test_site_html_files(self):
        pages = []
        for root, _dirs, files in os.walk(SITE):
            pages.extend(os.path.join(root, f) for f in files if f.endswith(".html"))
        self.assertIn(os.path.join(SITE, "index.html"), pages)
        for page in pages:
            with self.subTest(page=os.path.relpath(page, REPO)):
                with open(page, encoding="utf-8") as fh:
                    text = fh.read().lower()
                self.assertIn("<html", text)
                self.assertIn("</html>", text)

    def test_lesson_json_parses(self):
        names = [n for n in os.listdir(LESSONS) if n.endswith(".json")]
        self.assertTrue(names)
        for name in names:
            with self.subTest(lesson=name):
                with open(os.path.join(LESSONS, name), encoding="utf-8") as fh:
                    self.assertIsInstance(json.load(fh), dict)

    def test_launcher_is_executable(self):
        mode = os.stat(os.path.join(REPO, "academy")).st_mode
        self.assertTrue(mode & stat.S_IXUSR)


if __name__ == "__main__":
    unittest.main()
