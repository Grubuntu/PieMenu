"""Smoke tests: every module must import without error."""
import unittest


MODULES = [
    "piemenu",
    "piemenu.config",
    "piemenu.constants",
    "piemenu.state",
    "piemenu.log",
    "piemenu.context",
    "piemenu.defaults",
    "piemenu.observers",
    "piemenu.parameters",
    "piemenu.resources",
    "piemenu.shortcuts",
    "piemenu.theme",
    "piemenu.workbench",
    "piemenu.commands",
    "piemenu.widgets",
    "piemenu.ui.context",
    "piemenu.ui.icons",
    "piemenu.ui.menus",
    "piemenu.ui.misc",
    "piemenu.ui.options",
    "piemenu.ui.preferences",
    "piemenu.ui.quick_menu",
    "piemenu.ui.settings",
    "piemenu.ui.toolbar",
    "piemenu.ui.tool_list",
    "piemenu.ui.tab_piemenu",
    "piemenu.ui.tab_assistant",
    "piemenu.ui.tab_context",
    "piemenu.ui.tab_toolbar",
    "piemenu.ui.tab_settings",
    "piemenu.ui.wizard",
    "piemenu.bootstrap",
]


class TestImports(unittest.TestCase):
    def test_import_all(self):
        import importlib
        for name in MODULES:
            mod = importlib.import_module(name)
            self.assertIsNotNone(mod)


if __name__ == "__main__":
    unittest.main()