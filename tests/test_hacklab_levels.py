"""Part 2: level loading and validation.

Like the Part 1 lesson tests, this checks every shipped level, so a new level
is covered automatically just by adding its folder.
"""

import copy
import os
import sys
import unittest

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

from terminal_academy.hacklab import levels  # noqa: E402

# A minimal valid level, used as a base for "what makes it invalid" tests.
GOOD = {
    "format_version": 1,
    "id": "09-demo",
    "title": "Demo",
    "number": 9,
    "summary": "A demo level.",
    "story": "A story.",
    "objective": "Do the thing.",
    "diagram": "filesystem",
    "hints": ["one hint"],
    "containers": [{"name": "player", "role": "player", "dockerfile": "Dockerfile.player"}],
    "flag_placements": [{"container": "player", "path": "/home/player/.flag"}],
    "diagram_watch": {"root": "/home/player"},
}


class ShippedLevelsTest(unittest.TestCase):
    def test_levels_load_without_problems(self):
        loaded, problems = levels.load_levels()
        self.assertEqual(problems, [])
        self.assertTrue(loaded, "no levels found")

    def test_at_least_three_levels(self):
        loaded, _ = levels.load_levels()
        numbers = sorted(l.number for l in loaded)
        self.assertEqual(numbers[:3], [1, 2, 3])

    def test_every_level_has_files(self):
        loaded, _ = levels.load_levels()
        for level in loaded:
            with self.subTest(level=level.id):
                self.assertTrue(os.path.isfile(level.learn_path), "missing LEARN.md")
                for container in level.containers:
                    path = os.path.join(level.directory, container.dockerfile)
                    self.assertTrue(os.path.isfile(path),
                                    "missing %s" % container.dockerfile)

    def test_flag_placement_containers_exist(self):
        loaded, _ = levels.load_levels()
        for level in loaded:
            names = {c.name for c in level.containers}
            for placement in level.flag_placements:
                self.assertIn(placement["container"], names)

    def test_network_level_has_target(self):
        loaded, _ = levels.load_levels()
        for level in loaded:
            if level.diagram == "network":
                self.assertIsNotNone(level.target,
                                     "a network level needs a target container")


class FindLevelTest(unittest.TestCase):
    def test_find_by_number_and_id(self):
        loaded, _ = levels.load_levels()
        first = loaded[0]
        self.assertIs(levels.find_level(loaded, str(first.number)), first)
        self.assertIs(levels.find_level(loaded, first.id), first)
        self.assertIsNone(levels.find_level(loaded, "999"))


class ValidationTest(unittest.TestCase):
    def _errors(self, mutate):
        data = copy.deepcopy(GOOD)
        mutate(data)
        return levels.validate_level(data, "levels/09-demo/level.json")

    def test_good_is_valid(self):
        self.assertEqual(levels.validate_level(GOOD, "x/09-demo/level.json"), [])

    def test_unknown_field_rejected(self):
        self.assertTrue(self._errors(lambda d: d.update(extra=1)))

    def test_bad_diagram_rejected(self):
        self.assertTrue(self._errors(lambda d: d.update(diagram="sparkles")))

    def test_two_players_rejected(self):
        def mutate(d):
            d["containers"].append(
                {"name": "player2", "role": "player", "dockerfile": "D"})
        self.assertTrue(self._errors(mutate))

    def test_relative_flag_path_rejected(self):
        def mutate(d):
            d["flag_placements"][0]["path"] = "home/player/.flag"  # not absolute
        self.assertTrue(self._errors(mutate))

    def test_flag_path_with_dotdot_rejected(self):
        def mutate(d):
            d["flag_placements"][0]["path"] = "/home/../etc/.flag"
        self.assertTrue(self._errors(mutate))

    def test_bad_mode_rejected(self):
        def mutate(d):
            d["flag_placements"][0]["mode"] = "999"
        self.assertTrue(self._errors(mutate))

    def test_empty_hints_rejected(self):
        self.assertTrue(self._errors(lambda d: d.update(hints=[])))

    def test_placement_unknown_container_rejected(self):
        def mutate(d):
            d["flag_placements"][0]["container"] = "ghost"
        self.assertTrue(self._errors(mutate))


if __name__ == "__main__":
    unittest.main()
