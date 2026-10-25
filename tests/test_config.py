"""Tests for piemenu.config (needs FreeCAD, runs in freecadcmd)."""
import unittest


class TestConfig(unittest.TestCase):
    def test_get_index_list_returns_list(self):
        from piemenu import config
        index_list = config.get_index_list()
        self.assertIsInstance(index_list, list)
        self.assertTrue(all(isinstance(i, int) for i in index_list))

    def test_get_param_index_returns_str(self):
        from piemenu import config
        pie = config.get_param_index("1")
        self.assertIsInstance(pie, str)
        self.assertTrue(len(pie) > 0)

    def test_get_param_returns_str(self):
        from piemenu import config
        value = config.get_param("CurrentPie")
        self.assertIsInstance(value, str)

    def test_get_parameter_group_string(self):
        from piemenu import config
        pie = config.get_param("CurrentPie")
        value = config.get_parameter_group(pie, "String", "ToolList")
        self.assertIsInstance(value, str)

    def test_get_parameter_group_int(self):
        from piemenu import config
        pie = config.get_param("CurrentPie")
        value = config.get_parameter_group(pie, "Int", "Radius")
        self.assertIsInstance(value, int)

    def test_get_parameter_group_bool(self):
        from piemenu import config
        pie = config.get_param("CurrentPie")
        value = config.get_parameter_group(pie, "Bool", "EnableShorcut")
        self.assertIsInstance(value, bool)


if __name__ == "__main__":
    unittest.main()