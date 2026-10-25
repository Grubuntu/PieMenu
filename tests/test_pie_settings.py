"""Tests for piemenu.pie_menu.read_pie_settings (settings block of add_commands)."""

import math
import unittest

from piemenu import constants, pie_menu


class FakeGroup:
    """Minimal FreeCAD parameter group: read_pie_settings only calls GetInt."""

    def __init__(self, radius=0, button=0):
        self.radius = radius
        self.button = button

    def GetInt(self, name):
        if name == constants.PARAM_RADIUS:
            return self.radius
        if name == constants.PARAM_BUTTON:
            return self.button
        raise KeyError(name)


class FakeMainParams:
    """Stub of the 'main' parameter group: only the toolbar flag is read."""

    def __init__(self, is_toolbar):
        self._is_toolbar = is_toolbar  # callable, so tests can toggle it later

    def GetBool(self, name):
        return self._is_toolbar()


class FakeConfig:
    def __init__(self, is_toolbar):
        self._is_toolbar = is_toolbar

    def get_params(self):
        return {"main": FakeMainParams(self._is_toolbar)}


class FakeLog:
    """Records log calls instead of writing to the console/file."""

    def __init__(self):
        self.errors = []
        self.warnings = []

    def log_error(self, context, exc=None):
        self.errors.append((context, exc))

    def log_warning(self, context, exc=None):
        self.warnings.append((context, exc))


# Values returned for each parameter when a test does not override them.
# command_per_circle must stay > 0: the angle computation would divide by it.
PARAM_VALUES = {
    constants.PARAM_NUM_COLUMN: 4,
    constants.PARAM_ICON_SPACING: 8,
    constants.PARAM_COMMAND_PER_CIRCLE: 5,
    constants.PARAM_SHORTCUT_LABEL_SIZE: 8,
    constants.PARAM_DISPLAY_COMMAND: True,
    constants.PARAM_DISPLAY_PRESELECT: True,
    constants.PARAM_ENABLE_SHORTCUT: True,
    constants.PARAM_DISPLAY_SHORTCUT: True,
}


class TestReadPieSettings(unittest.TestCase):
    """read_pie_settings must return what the old inline block computed."""

    def setUp(self):
        # The helpers it uses are published by the bootstrap: they are None in
        # a headless test run, so replace them with deterministic stubs.
        names = ("get_shape", "radius_size", "icon_size",
                 "get_parameter_group", "config", "log")
        self.saved = {name: getattr(pie_menu, name) for name in names}
        self.shape = "Pie"
        self.toolbar = False
        self.values = dict(PARAM_VALUES)
        self.log = FakeLog()

        pie_menu.get_shape = lambda key: self.shape
        pie_menu.radius_size = lambda size: "radius-css-%s" % size
        pie_menu.icon_size = lambda size: size / 3 * 2
        pie_menu.get_parameter_group = \
            lambda key, kind, param: self.values.get(param, 0)
        pie_menu.config = FakeConfig(lambda: self.toolbar)
        pie_menu.log = self.log

    def tearDown(self):
        for name, value in self.saved.items():
            setattr(pie_menu, name, value)

    def test_defaults_when_parameters_are_missing(self):
        # GetInt returns 0 = "not configured" -> historical defaults
        settings = pie_menu.read_pie_settings(
            FakeGroup(radius=0, button=0), "Conception", 4)
        self.assertEqual(settings.radius, 100)
        self.assertEqual(settings.button_size, 32)
        self.assertEqual(settings.value_radius, 0)
        self.assertEqual(settings.shape, "Pie")
        self.assertEqual(settings.num_of_column, 4)
        self.assertEqual(settings.icon_spacing, 8)
        self.assertEqual(settings.command_per_circle, 5)
        self.assertEqual(settings.radius_css, "radius-css-32")
        self.assertAlmostEqual(settings.icon, 32 / 3 * 2)

    def test_raw_radius_is_kept_for_layout(self):
        settings = pie_menu.read_pie_settings(
            FakeGroup(radius=777, button=48), "Conception", 4)
        self.assertEqual(settings.value_radius, 777)  # used for widget sizes
        self.assertEqual(settings.radius, 777)        # stored on the widget
        self.assertEqual(settings.button_size, 48)
        self.assertEqual(settings.radius_css, "radius-css-48")

    def test_clamps_invalid_layout_values(self):
        self.values[constants.PARAM_NUM_COLUMN] = 0
        self.values[constants.PARAM_ICON_SPACING] = -3
        self.values[constants.PARAM_SHORTCUT_LABEL_SIZE] = 2
        settings = pie_menu.read_pie_settings(FakeGroup(), "Conception", 4)
        self.assertEqual(settings.num_of_column, 1)
        self.assertEqual(settings.icon_spacing, 0)
        self.assertEqual(settings.shortcut_label_size, 6)  # issue #124 minimum

    def test_toolbar_overrides_geometry(self):
        self.toolbar = True
        self.shape = "Concentric"
        settings = pie_menu.read_pie_settings(
            FakeGroup(radius=777, button=48), "toolBarTab", 6)
        self.assertEqual(settings.value_radius, 100)
        self.assertEqual(settings.radius, 100)
        self.assertEqual(settings.button_size, 32)
        self.assertEqual(settings.shape, "Pie")

    def test_display_flags_follow_the_shape(self):
        self.shape = "Concentric"
        settings = pie_menu.read_pie_settings(FakeGroup(), "Conception", 4)
        # command name and preselect only exist for Pie-like shapes
        self.assertFalse(settings.display_command_name)
        self.assertFalse(settings.display_preselect)
        self.assertTrue(settings.enable_shortcut)
        self.assertTrue(settings.display_shortcut)

        self.shape = "Pie"
        settings = pie_menu.read_pie_settings(FakeGroup(), "Conception", 4)
        self.assertTrue(settings.display_command_name)
        self.assertTrue(settings.display_preselect)

    def test_read_failure_falls_back_and_logs(self):
        class BrokenGroup:
            def GetInt(self, name):
                raise ValueError("no parameter group")

        settings = pie_menu.read_pie_settings(BrokenGroup(), "Conception", 4)
        self.assertEqual(settings.radius, 100)
        self.assertEqual(settings.button_size, 32)
        self.assertEqual(settings.shape, "Pie")  # get_shape never reached
        self.assertEqual(len(self.log.errors), 1)

    def test_angles_are_computed(self):
        settings = pie_menu.read_pie_settings(FakeGroup(), "Conception", 4)
        self.assertAlmostEqual(settings.angle, 2 * math.pi / 4)
        self.assertIsInstance(settings.angle_start, float)


if __name__ == "__main__":
    unittest.main()
