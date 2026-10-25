"""Tests for piemenu.pie_menu.should_show_pie (the showPie decision)."""

import unittest

from piemenu import pie_menu


class FakeGuiDoc:
    """Stub of Gui.ActiveDocument: only getInEdit() is used."""

    def __init__(self, in_edit):
        self._in_edit = in_edit

    def getInEdit(self):
        return object() if self._in_edit else None


class FakeAppDoc:
    """Stub of App.ActiveDocument: only the .Name probe is used."""

    Name = "Unnamed"


class TestShouldShowPie(unittest.TestCase):
    """should_show_pie must keep the historical decision table."""

    def setUp(self):
        self.saved = {"Gui": pie_menu.Gui, "App": pie_menu.App}

    def tearDown(self):
        for name, value in self.saved.items():
            setattr(pie_menu, name, value)

    def set_context(self, gui_doc, app_doc):
        pie_menu.Gui = type("FakeGui", (), {"ActiveDocument": gui_doc})()
        pie_menu.App = type("FakeApp", (), {"ActiveDocument": app_doc})()

    def test_no_gui_document_shows_the_pie(self):
        # Gui.ActiveDocument is None -> probe raises, then no document open
        self.set_context(gui_doc=None, app_doc=None)
        self.assertTrue(pie_menu.should_show_pie("PartDesignGui"))

    def test_editing_a_part_shows_no_pie(self):
        self.set_context(gui_doc=FakeGuiDoc(in_edit=True), app_doc=FakeAppDoc())
        self.assertFalse(pie_menu.should_show_pie("PartDesignGui"))

    def test_sketcher_shows_the_pie(self):
        self.set_context(gui_doc=FakeGuiDoc(in_edit=True), app_doc=FakeAppDoc())
        self.assertTrue(pie_menu.should_show_pie("SketcherGui"))

    def test_assembly_shows_the_pie(self):
        self.set_context(gui_doc=FakeGuiDoc(in_edit=True), app_doc=FakeAppDoc())
        self.assertTrue(pie_menu.should_show_pie("AssemblyGui"))

    def test_no_document_open_shows_the_pie(self):
        # editing in the GUI but no document in App: second probe raises
        self.set_context(gui_doc=FakeGuiDoc(in_edit=True), app_doc=None)
        self.assertTrue(pie_menu.should_show_pie("PartDesignGui"))


if __name__ == "__main__":
    unittest.main()
