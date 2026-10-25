from PySide import QtCore, QtGui
from PySide.QtCore import Qt
from PySide.QtGui import QKeySequence
from PySide.QtWidgets import QLineEdit

from piemenu import config, constants, state


class CustomLineEdit(QLineEdit):
    """Capture key events from shortcut fields in settings."""

    shortcutChanged = QtCore.Signal(str)

    def __init__(self):
        super(CustomLineEdit, self).__init__()

    def keyPressEvent(self, event):
        key_text = QKeySequence(event.key()).toString()
        modifier_text = self.get_modifier_text(event.modifiers())

        if event.key() == Qt.Key_Tab:
            self.setText("TAB")
            return

        elif event.key() in [Qt.Key_Backspace, Qt.Key_Delete]:
            if len(self.text()) > 0:
                current_text = self.text()
                if current_text and current_text[-1] == ',':
                    self.setText(current_text[:-1])
                else:
                    self.setText(current_text[:-1])
            else:
                self.setText('')

        elif modifier_text:
            if key_text and modifier_text:
                shortcut_text = f"{modifier_text}+{key_text}"
                self.setText(shortcut_text)

        elif key_text:
            if len(self.selectedText()) > 0:
                self.setText(key_text)
            else:
                if len(key_text) == 1 and len(self.text()) > 0:
                    last_char = self.text()[-1]
                    if last_char.isalpha():
                        self.setText(self.text() + ',' + key_text)
                    else:
                        self.setText(self.text() + key_text)
                else:
                    self.setText(key_text)
        else:
            super().keyPressEvent(event)

        self.shortcutChanged.emit(self.text())

    def get_modifier_text(self, modifiers):
        modifier_names = {
            Qt.ControlModifier: 'CTRL',
            Qt.AltModifier: 'ALT',
            Qt.ShiftModifier: 'SHIFT',
            Qt.MetaModifier: 'META'
        }

        if modifiers == Qt.KeyboardModifier.NoModifier:
            return ""

        modifier_text = '+'.join(
            modifier_names[modifier]
            for modifier in modifier_names
            if modifiers & modifier
        )

        if modifiers == Qt.Key_Tab:
            modifier_text += '+TAB' if modifier_text else 'TAB'

        return modifier_text


class HoverButton(QtGui.QToolButton):
    """Hover timer to avoid too fast triggering on hover mode."""

    def __init__(self, parent=None):
        super(HoverButton, self).__init__()
        self.hoverTimer = QtCore.QTimer(self)
        self.hoverTimer.setSingleShot(True)
        self.hoverTimer.timeout.connect(self.onHoverTimeout)
        self.enterEventConnected = False
        self.isMouseOver = False
        self.leaveEvent = self.onLeaveEvent

    def onHoverTimeout(self):
        """Handle hover timeout event."""
        import FreeCADGui as Gui

        mode = state.app_state.trigger_mode
        if self.isMouseOver and self.defaultAction().isEnabled() and mode == "Hover":
            dialog = state.app_state.pie_menu_dialog
            instance = state.app_state.pie_menu_instance
            if not dialog.isVisible():
                instance.hide()
                self.defaultAction().trigger()
                module = None
                try:
                    g = Gui.ActiveDocument.getInEdit()
                    module = g.Module
                except Exception:
                    # not in edit mode: keep module = None
                    pass
                displaySpinBox = config.get_parameter_global("Bool", constants.PARAM_DISPLAY_SPIN_BOX)
                if (module is not None and module != 'SketcherGui') and displaySpinBox:
                    instance.showAtMouseInstance()
        else:
            pass

    def onLeaveEvent(self, event):
        self.isMouseOver = False

    def enterEvent(self, event):
        if not self.enterEventConnected:
            self.hoverTimer.start(state.app_state.hover_delay)
            self.enterEventConnected = True
        self.hoverTimer.stop()
        self.hoverTimer.start(state.app_state.hover_delay)
        self.isMouseOver = True

    def mouseReleaseEvent(self, event):
        import FreeCADGui as Gui

        if self.isMouseOver and self.defaultAction().isEnabled():
            dialog = state.app_state.pie_menu_dialog
            instance = state.app_state.pie_menu_instance
            if not dialog.isVisible():
                instance.hide()
                Gui.getMainWindow().setFocus()
                self.defaultAction().trigger()
                module = None
                try:
                    g = Gui.ActiveDocument.getInEdit()
                    module = g.Module
                    fonctionActive = g.Object
                    displaySpinBox = config.get_parameter_global("Bool", constants.PARAM_DISPLAY_SPIN_BOX)

                    if (module is not None and module != 'SketcherGui' and str(fonctionActive) in constants.listSpinboxFeatures) and displaySpinBox:
                        instance.showAtMouseInstance()
                except Exception:
                    # not in edit mode or feature without spinbox: do nothing
                    pass
        else:
            pass


class PreselectButton(QtGui.QToolButton):
    """Custom class for preselect button."""

    def __init__(self, parent=None):
        super(PreselectButton, self).__init__()
        self.baseIcon = None
        self.hoverIcon = None
        self.leaveEvent = self.onLeaveEvent

    def onLeaveEvent(self, event):
        self.setIcon(self.baseIcon)
        self.update()

    def enterEvent(self, event):
        self.setIcon(self.hoverIcon)
        self.update()

    def mouseReleaseEvent(self, event):
        import FreeCADGui as Gui

        if self.defaultAction().isEnabled():
            dialog = state.app_state.pie_menu_dialog
            instance = state.app_state.pie_menu_instance
            if not dialog.isVisible():
                instance.hide()
                Gui.getMainWindow().setFocus()
                self.defaultAction().trigger()
                module = None
                try:
                    g = Gui.ActiveDocument.getInEdit()
                    module = g.Module
                    fonctionActive = g.Object
                    displaySpinBox = config.get_parameter_global("Bool", constants.PARAM_DISPLAY_SPIN_BOX)
                    if (module is not None and module != 'SketcherGui' and str(fonctionActive) in constants.listSpinboxFeatures) and displaySpinBox:
                        instance.showAtMouseInstance()
                except Exception:
                    # not in edit mode or feature without spinbox: do nothing
                    pass
        else:
            pass

    def setBaseIcon(self, icon=QtGui.QIcon()):
        self.baseIcon = icon
        self.setIcon(self.baseIcon)

    def setHoverIcon(self, icon=QtGui.QIcon()):
        self.hoverIcon = icon
