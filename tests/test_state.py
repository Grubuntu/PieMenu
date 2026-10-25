"""Tests for piemenu.state (pure dataclass)."""
import unittest


class TestState(unittest.TestCase):
    def test_app_state_defaults(self):
        from piemenu.state import AppState
        s = AppState()
        self.assertEqual(s.global_shortcut_key, "TAB")
        self.assertEqual(s.hover_delay, 100)
        self.assertTrue(s.first_load)
        self.assertEqual(s.list_commands, [])

    def test_app_state_mutable_lists_independent(self):
        from piemenu.state import AppState
        a = AppState()
        b = AppState()
        a.list_commands.append("x")
        self.assertEqual(b.list_commands, [])


if __name__ == "__main__":
    unittest.main()