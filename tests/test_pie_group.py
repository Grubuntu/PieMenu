"""Tests for piemenu.pie_menu.resolve_pie_group (group lookup of add_commands)."""

import unittest

from piemenu import pie_menu


class FakeIndexParams:
    def __init__(self, groups):
        self._groups = groups

    def GetGroup(self, index):
        return self._groups[index]


class FakeConfig:
    """Stub of piemenu.config: only get_params()["index"].GetGroup() is used."""

    def __init__(self, groups):
        self._groups = groups

    def get_params(self):
        return {"index": FakeIndexParams(self._groups)}


class TestResolvePieGroup(unittest.TestCase):
    """resolve_pie_group must return the same group as the inline code did."""

    def setUp(self):
        names = ("get_group", "get_index_list", "get_param_index", "config")
        self.saved = {name: getattr(pie_menu, name) for name in names}
        self.mode_calls = []

        def fake_get_group(mode=1):
            self.mode_calls.append(mode)
            return "group-mode-%s" % mode

        pie_menu.get_group = fake_get_group

    def tearDown(self):
        for name, value in self.saved.items():
            setattr(pie_menu, name, value)

    def test_current_pie_group_by_default(self):
        self.assertEqual(pie_menu.resolve_pie_group(), "group-mode-1")
        self.assertEqual(self.mode_calls, [1])

    def test_context_uses_the_context_group(self):
        self.assertEqual(pie_menu.resolve_pie_group(context=True), "group-mode-2")
        self.assertEqual(self.mode_calls, [2])

    def test_named_pie_is_looked_up_in_the_index(self):
        pie_menu.get_index_list = lambda: ["0", "1"]
        pie_menu.get_param_index = lambda index: {"0": "Conception", "1": "Files"}[index]
        pie_menu.config = FakeConfig({"0": "grp-conception", "1": "grp-files"})
        self.assertEqual(pie_menu.resolve_pie_group("Files"), "grp-files")
        # an explicit key never falls back to the current/context group
        self.assertEqual(self.mode_calls, [])

    def test_unknown_pie_returns_empty_group(self):
        pie_menu.get_index_list = lambda: ["0"]
        pie_menu.get_param_index = lambda index: "Conception"
        pie_menu.config = FakeConfig({"0": "grp-conception"})
        self.assertEqual(pie_menu.resolve_pie_group("Missing"), "")
        self.assertEqual(self.mode_calls, [])


if __name__ == "__main__":
    unittest.main()
