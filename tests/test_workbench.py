"""Tests for piemenu.workbench (pure helpers, no GUI needed)."""
import unittest


class TestExtractWorkbench(unittest.TestCase):
    def test_standard_command(self):
        from piemenu.workbench import extract_workbench
        self.assertEqual(extract_workbench("Sketcher_CreateLine"), "Sketcher")

    def test_empty_command(self):
        from piemenu.workbench import extract_workbench
        self.assertEqual(extract_workbench(""), "None")

    def test_underscore_only(self):
        from piemenu.workbench import extract_workbench
        self.assertEqual(extract_workbench("_Foo"), "None")


class TestResolveWorkbenchName(unittest.TestCase):
    """resolve_workbench_name: no more "PartDesignWorkbenchWorkbench" ids."""

    def test_short_name_gets_suffix(self):
        from piemenu.workbench import resolve_workbench_name
        self.assertEqual(resolve_workbench_name("Part"), "PartWorkbench")

    def test_mapped_name(self):
        from piemenu.workbench import resolve_workbench_name
        self.assertEqual(resolve_workbench_name("Arch"), "BIMWorkbench")

    def test_full_name_kept_as_is(self):
        from piemenu.workbench import resolve_workbench_name
        self.assertEqual(
            resolve_workbench_name("PartDesignWorkbench"),
            "PartDesignWorkbench")

    def test_unknown_full_name_not_doubled(self):
        # FreeCAD 1.1 has no "StartWorkbench", but the id must stay
        # "StartWorkbench" (never "StartWorkbenchWorkbench").
        from piemenu.workbench import resolve_workbench_name
        self.assertEqual(
            resolve_workbench_name("StartWorkbench"),
            "StartWorkbench")


if __name__ == "__main__":
    unittest.main()