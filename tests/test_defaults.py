"""Tests for piemenu.defaults (needs FreeCAD, runs in freecadcmd).

Uses a throwaway parameter group so the real PieMenu user settings are
never modified by the tests.
"""
import unittest


class TestDefaults(unittest.TestCase):
    def test_set_default_values_writes_expected_params(self):
        import FreeCAD as App
        from piemenu import defaults

        params = App.ParamGet("User parameter:BaseApp/PieMenuTest")
        group = params.GetGroup("DefaultsTest")

        defaults.set_default_values(group)

        self.assertEqual(group.GetInt("Radius"), 80)
        self.assertEqual(group.GetInt("Button"), 32)
        self.assertEqual(group.GetString("Shape"), "Pie")
        self.assertEqual(group.GetString("TriggerMode"), "Press")
        self.assertEqual(group.GetInt("HoverDelay"), 100)
        self.assertFalse(group.GetBool("EnableShorcut"))
        self.assertFalse(group.GetBool("DisplayPreselect"))
        self.assertEqual(group.GetInt("ShortcutLabelSize"), 8)

        params.RemGroup("DefaultsTest")

    def test_set_default_values_idempotent(self):
        import FreeCAD as App
        from piemenu import defaults

        params = App.ParamGet("User parameter:BaseApp/PieMenuTest")
        group = params.GetGroup("Idem")

        defaults.set_default_values(group)
        defaults.set_default_values(group)

        self.assertEqual(group.GetString("Shape"), "Pie")
        params.RemGroup("Idem")


if __name__ == "__main__":
    unittest.main()