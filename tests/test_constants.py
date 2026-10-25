"""Tests for piemenu.constants (pure, no FreeCAD GUI needed)."""
import math
import unittest


class TestConstants(unittest.TestCase):
    def test_available_shape_is_list(self):
        from piemenu import constants
        self.assertIsInstance(constants.available_shape, list)
        self.assertIn("Pie", constants.available_shape)
        self.assertIn("LeftRight", constants.available_shape)

    def test_get_signs(self):
        from piemenu import constants
        signs = constants.get_signs()
        self.assertIn("<", signs)
        self.assertTrue(signs["<"](1, 2))
        self.assertFalse(signs["<"](2, 1))

    def test_compute_shape_angle_pie(self):
        from piemenu import constants
        angle, start = constants.compute_shape_angle("Pie", 5, 5)
        self.assertAlmostEqual(angle, 2 * math.pi / 5)
        self.assertAlmostEqual(start, 3 * math.pi / 2 - angle)

    def test_compute_shape_angle_single_command(self):
        from piemenu import constants
        angle, start = constants.compute_shape_angle("Pie", 1, 5)
        self.assertEqual(angle, 0)

    def test_compute_shape_angle_concentric(self):
        from piemenu import constants
        angle, start = constants.compute_shape_angle("Concentric", 8, 4)
        self.assertAlmostEqual(angle, 2 * math.pi / 4)

    def test_compute_shape_angle_unknown_shape_falls_back(self):
        from piemenu import constants
        angle, start = constants.compute_shape_angle("UnknownShape", 4, 4)
        self.assertAlmostEqual(angle, 2 * math.pi / 4)


class TestSpinboxFeatureMaps(unittest.TestCase):
    def test_size_attr_covers_all_spinbox_features(self):
        from piemenu import constants
        for feature in constants.listSpinboxFeatures:
            self.assertIn(feature, constants.SPINBOX_SIZE_ATTR,
                          "missing size attr for %s" % feature)

    def test_midplane_features_are_subset(self):
        from piemenu import constants
        self.assertTrue(constants.SPINBOX_MIDPLANE_FEATURES.issubset(
            set(constants.SPINBOX_SIZE_ATTR)))

    def test_hole_is_not_a_size_feature(self):
        from piemenu import constants
        self.assertNotIn("<PartDesign::Hole>", constants.SPINBOX_SIZE_ATTR)


if __name__ == "__main__":
    unittest.main()