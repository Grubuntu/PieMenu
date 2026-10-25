"""FreeCAD selection observer for the PieMenu workbench.

Watches the selection changes to trigger the contextual PieMenu.
"""

from piemenu import context


class SelObserver:
    """Trigger the contextual PieMenu when the selection changes."""

    def addSelection(self, doc, obj, sub, pnt):
        # Block list_topo while CTRL is pressed to allow multi-selection
        # for the context.
        from PySide import QtCore, QtGui

        modifiers = QtGui.QApplication.keyboardModifiers()
        if not (modifiers & QtCore.Qt.ControlModifier):
            context.list_topo()

    def removeSelection(self, doc, obj, sub):
        # Block list_topo while CTRL is pressed to allow multiple deselection
        # for the context.
        from PySide import QtCore, QtGui

        modifiers = QtGui.QApplication.keyboardModifiers()
        if not (modifiers & QtCore.Qt.ControlModifier):
            context.list_topo()
