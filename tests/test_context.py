"""Tests for piemenu.context (needs FreeCAD, runs in freecadcmd)."""
import unittest


class TestContext(unittest.TestCase):
    def test_context_list_runs_and_fills_state(self):
        from piemenu import context, state
        context.context_list()
        self.assertIsInstance(state.app_state.context_all, dict)

    def test_context_list_clears_previous(self):
        from piemenu import context, state
        state.app_state.context_all["dummy"] = {"x": 1}
        context.context_list()
        self.assertNotIn("dummy", state.app_state.context_all)

    def test_get_context_pie_returns_int_or_none(self):
        from piemenu import context, constants, state
        # get_context_pie relies on the operator table populated at startup.
        state.app_state.signs = constants.get_signs()
        result = context.get_context_pie(1, 1, 1, 1, 1, 1)
        self.assertTrue(result is None or isinstance(result, int))


if __name__ == "__main__":
    unittest.main()