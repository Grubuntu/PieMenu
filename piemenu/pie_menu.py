"""Main PieMenu widget.

`PieMenu` draws the radial menu at the mouse position. It is triggered either
by the global shortcut (see `piemenu.shortcuts`) or by a contextual selection
(see `piemenu.context`).

FreeCAD and Qt are imported at module level because the widget subclasses
`QWidget` and resolves the main window while the class body is executed.

Some of the widgets and callbacks used by the methods below are created by the
`pieMenuStart()` bootstrap *after* this module has been imported. They are
declared as module attributes here and published by `pieMenuStart()` through
`publish()`.
"""

import math
from types import SimpleNamespace

import FreeCAD as App
import FreeCADGui as Gui
from FreeCAD import Units
from PySide import QtCore, QtGui, QtWidgets
from PySide.QtCore import Qt
from PySide.QtGui import QFontMetrics, QShortcut, QTransform
from PySide.QtWidgets import QCheckBox, QHBoxLayout, QWidget

from piemenu import config, constants, log, resources, state
from piemenu.config import (
    get_index_list,
    get_param,
    get_param_index,
    get_parameter_global,
    get_parameter_group,
)
from piemenu.context import list_topo
from piemenu.theme import get_css_color, get_style
from piemenu.widgets import HoverButton, PreselectButton
from piemenu.workbench import (
    actualize_workbench_actions,
    get_gui_action_map_all,
    get_gui_tool_button_data,
    get_pie_name,
    resolve_workbench_name,
)


def translate(context, text):
    """Translate a string with the FreeCAD Qt translator."""
    return App.Qt.translate(context, text)


# Widgets and callbacks created by `pieMenuStart()`. They only exist once the
# bootstrap has run, so they are published there through `publish()`.
pie_menu_instance = None
action_key = None
pie_menu_dialog = None
button_list_widget = None
c_box = None
checkbox_global_key_toggle = None
checkbox_quick_menu = None
checkbox_right_click = None
close_button = None
get_group = None
get_shape = None
icon_size = None
list_tool_bar = None
on_button_down = None
on_button_remove_command = None
on_button_up = None
quick_menu = None
radius_size = None
show_piemenu = None
show_preview_widget = None
spin_delay_right_click = None
tabs = None
update_icons_pie_menus = None


def publish(**references):
    """Publish the runtime references used by the PieMenu methods."""
    globals().update(references)


def _update_toolbar_preview():
    """Build and display the toolbar preview pie menu.

    Extracted from ``update_commands`` (the ``toolBarTab`` branch).
    """
    context = False
    text = False
    items = []
    commands = []

    for index in range(list_tool_bar.count()):
        items.append(list_tool_bar.item(index))
        if items[index].isSelected():
            sender = list_tool_bar.item(index)
            get_gui_tool_button_data(sender.text(), None, commands, None)

    actions = []
    action_map_all = get_gui_action_map_all()
    while actualize_workbench_actions(actions, commands, action_map_all):
        action_map_all = get_gui_action_map_all()
    else:
        pass
    pie_menu_instance.add_commands(actions, False, "toolBarTab")


def update_commands(key_value=None, context=False):
    """ Refresh the commands of the current PieMenu. """
    # key_value = None > Global shortcut
    # key_value != None > Custom shortcut
    # `text` stays None for the toolbar preview, which has no pie menu.
    text = None
    if not key_value or key_value is None:
        # context
        if context:
            text = get_param(constants.PARAM_CONTEXT_PIE)

        # workbench
        elif not config.get_params()["main"].GetBool(constants.PARAM_TOOL_BAR):
            wb = Gui.activeWorkbench()
            wb_name = wb.name()
            wb_name = wb_name.replace("Workbench", "")
            # workbench
            text = get_pie_name(wb_name)

            # current Pie
            if text is None:
                text = get_param(constants.PARAM_CURRENT_PIE)
        # else:
            # text = key_value
            context = False

        # toolbar
        elif config.get_params()["main"].GetBool(constants.PARAM_TOOL_BAR):
            toolbar = config.get_params()["main"].GetString(constants.PARAM_TOOL_BAR)
            text = None
            context = False
            if ": " in toolbar:
                toolbar_desc = toolbar.split(": ")
                toolbar = toolbar_desc[1]
                workbenches = toolbar_desc[0]
                workbenches = workbenches.split(", ")
                last_workbench = Gui.activeWorkbench()
                for i in workbenches:
                    # rule out special cases
                    if i is None or i == "Std":
                        pass
                    else:
                        wb_name = resolve_workbench_name(i)
                    if (i + "Workbench") not in state.app_state.loaded_workbenches:
                        try:
                            Gui.activateWorkbench(wb_name)
                        except KeyError:
                            # The command belongs to a workbench that is not
                            # installed (e.g. a macro prefixed with "Custom_"):
                            # nothing to activate, skip silently.
                            pass
                        except Exception as exc:
                            log.log_warning_once(
                                "wb:" + wb_name,
                                "cannot activate workbench %s" % wb_name, exc)
                        state.app_state.loaded_workbenches.append(wb_name)
                Gui.activateWorkbench(last_workbench.__class__.__name__)
            else:
                pass
            context = False
            actions = []
            get_gui_tool_button_data(toolbar, actions, None, None)

    # for toolbar preview in preferences settings
    elif key_value == "toolBarTab":
        _update_toolbar_preview()

    else:
        # custom shortcut
        text = key_value
        context = False

    if text:
        tool_list = None
        index_list = get_index_list()
        for i in index_list:
            pie = get_param_index(str(i))
            if pie == text:
                group = config.get_params()["index"].GetGroup(str(i))
                tool_list = group.GetString(constants.PARAM_TOOL_LIST)
            else:
                pass

        if tool_list:
            tool_list = tool_list.split(".,.")
        else:
            tool_list = []

        actions = []

        action_map_all = get_gui_action_map_all()
        last_workbench = Gui.activeWorkbench()
        while actualize_workbench_actions(actions, tool_list, action_map_all):
            action_map_all = get_gui_action_map_all()
        else:
            pass
        Gui.activateWorkbench(last_workbench.__class__.__name__)

        state.app_state.trigger_mode = get_parameter_group(text, "String", constants.PARAM_TRIGGER_MODE)
        state.app_state.hover_delay = get_parameter_group(text, "Int", constants.PARAM_HOVER_DELAY)

    else:
        pass

    if not key_value == "toolBarTab":
        pie_menu_instance.add_commands(actions, context, text)


def read_pie_settings(group, keyValue, commandNumber):
    """Read and normalise the parameters of one pie menu.

    Extracted from ``PieMenu.add_commands``: returns a namespace holding
    every value the layout code needs, without touching the widget itself.
    Missing or invalid parameters fall back to the historical defaults (the
    minimum shortcut label size comes from issue #124).

    ``group`` is the FreeCAD parameter group of the pie menu, ``keyValue``
    its name and ``commandNumber`` the number of buttons about to be laid
    out (it drives the computed angles).
    """
    # defaults values
    valueRadius = 100
    valueButton = 32
    shape = "Pie"
    num_of_column = 4
    icon_spacing = 8
    command_per_circle = 5
    shortcutLabelSize = 8

    # The group is empty for the toolbar preview and for a pie menu that does
    # not exist yet: there is nothing to read, the layout keeps the defaults.
    if group:
        try:
            valueRadius = group.GetInt(constants.PARAM_RADIUS)
            valueButton = group.GetInt(constants.PARAM_BUTTON)
            shape = get_shape(keyValue)
            num_of_column = get_parameter_group(keyValue, "Int", constants.PARAM_NUM_COLUMN)
            icon_spacing = get_parameter_group(
                keyValue, "Int", constants.PARAM_ICON_SPACING)
            command_per_circle = get_parameter_group(
                keyValue, "Int", constants.PARAM_COMMAND_PER_CIRCLE)
            shortcutLabelSize = get_parameter_group(
                keyValue, "Int", constants.PARAM_SHORTCUT_LABEL_SIZE)
            ### Fix https://github.com/Grubuntu/PieMenu/issues/124
            if shortcutLabelSize < 6:
                shortcutLabelSize = 6
        except Exception as exc:
            log.log_error("add_commands: failed to read parameters", exc)

    # toolbar mode and the toolbar tab override the geometry
    if config.get_params()["main"].GetBool(constants.PARAM_TOOL_BAR) or keyValue == "toolBarTab":
        valueRadius = 100
        valueButton = 32
        shape = "Pie"

    # a falsy radius/button means "not configured": use the defaults
    radius = valueRadius if valueRadius else 100
    buttonSize = valueButton if valueButton else 32

    if num_of_column == 0:
        num_of_column = 1

    if icon_spacing < 0:
        icon_spacing = 0

    angle, angleStart = constants.compute_shape_angle(
        shape, commandNumber, command_per_circle)

    radius_css = radius_size(buttonSize)
    icon = icon_size(buttonSize)

    displayCommandName = False
    displayPreselect = False
    enableShortcut = False
    displayShortcut = False
    if shape in ["Pie", "LeftRight"]:
        try:  # get displayCommandName to display or not command name only for Pie shape
            displayCommandName = get_parameter_group(
                keyValue, "Bool", constants.PARAM_DISPLAY_COMMAND)
        except Exception as exc:
            log.log_warning("cannot read %s for %s" % (constants.PARAM_DISPLAY_COMMAND, keyValue), exc)
    if shape in ["Pie", "RainbowUp", "RainbowDown"]:
        try:  # get displayPreselect to display or not command name only for Pie shape
            displayPreselect = get_parameter_group(
                keyValue, "Bool", constants.PARAM_DISPLAY_PRESELECT)
        except Exception as exc:
            log.log_warning("cannot read %s for %s" % (constants.PARAM_DISPLAY_PRESELECT, keyValue), exc)

    try:  # get enableShortcut to enable or not shortcut
        enableShortcut = get_parameter_group(
            keyValue, "Bool", constants.PARAM_ENABLE_SHORTCUT)
    except Exception as exc:
        log.log_warning("cannot read %s for %s" % (constants.PARAM_ENABLE_SHORTCUT, keyValue), exc)
    try:  # get displayShortcut to display or not shortcut
        displayShortcut = get_parameter_group(
            keyValue, "Bool", constants.PARAM_DISPLAY_SHORTCUT)
    except Exception as exc:
        log.log_warning("cannot read %s for %s" % (constants.PARAM_DISPLAY_SHORTCUT, keyValue), exc)

    return SimpleNamespace(
        value_radius=valueRadius,
        radius=radius,
        button_size=buttonSize,
        shape=shape,
        num_of_column=num_of_column,
        icon_spacing=icon_spacing,
        command_per_circle=command_per_circle,
        shortcut_label_size=shortcutLabelSize,
        angle=angle,
        angle_start=angleStart,
        radius_css=radius_css,
        icon=icon,
        display_command_name=displayCommandName,
        display_preselect=displayPreselect,
        enable_shortcut=enableShortcut,
        display_shortcut=displayShortcut,
    )


def should_show_pie(module):
    """Tell whether the pie menu must be drawn for the current edit context.

    Extracted from ``PieMenu.add_commands``: the pie is shown when nothing is
    being edited (or the sketcher/assembly module is active) and when no
    document is open at all. A missing GUI/document state is a normal state,
    not an error: the historical probing code (and its exact behaviour) is
    kept as is.
    """
    showPie = False

    # handle case when not in edit mode or if  Sketcher is open
    try:
        if (Gui.ActiveDocument.getInEdit() is None) or (module == 'SketcherGui') or (module == 'AssemblyGui'):
            showPie = True
    except Exception:
        # no active GUI document (probe): showPie keeps its value; the
        # "no document open" probe below decides
        None

    # handle case when there is any document open
    try:
        # if there is any open document we throw exception, to set showPie to True to show PieMenu
        App.ActiveDocument.Name
    except Exception:
        showPie = True

    return showPie


def resolve_pie_group(keyValue=None, context=False):
    """Return the FreeCAD parameter group of the pie menu to build.

    Extracted from ``PieMenu.add_commands``: an explicit ``keyValue`` selects
    the named pie (its group is looked up through the index list), otherwise
    the context group or the current pie group is used. Returns ``""`` when
    the named pie has no group, so the parameter reads fall back to their
    defaults (same behaviour as before the extraction).
    """
    group = ""

    if keyValue is not None:
        indexList = get_index_list()
        for i in indexList:
            pie = get_param_index(str(i))
            if pie == keyValue:
                group = config.get_params()["index"].GetGroup(str(i))
    elif context:
        group = get_group(mode=2)
    else:
        group = get_group(mode=1)

    return group


class PieMenu(QWidget):
    """ Main widget for PieMenu """
    try:
        mw = Gui.getMainWindow()
    except AttributeError:
        # FreeCADGui is not fully initialised (headless/console mode); the
        # instance resolves it lazily on first use in the GUI.
        mw = None
    event_filter_installed = False
    offset_x = 0
    offset_y = 0

    def __init__(self, parent=mw):
        """Build the radial menu widget, its timers and the event filter."""
        super().__init__()
        self.double_spinbox = None
        styleCurrentTheme = get_style()

        # timer for right click delay
        self.timer = QtCore.QTimer(self)
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.show_menu)

        self.debounceTimer = QtCore.QTimer(self)
        self.debounceTimer.setSingleShot(True)
        self.debounceTimer.timeout.connect(self.install_filter)

        if not PieMenu.event_filter_installed:
            app = QtGui.QGuiApplication.instance() or QtGui.QApplication([])
            app.installEventFilter(self)
            PieMenu.event_filter_installed = True

        self.radius = 100
        self.buttons = []
        self.buttonSize = 32

        self.menu = QtWidgets.QWidget(None)
        self.menu.setObjectName("styleContainer")
        self.menu.setStyleSheet(styleCurrentTheme)

        flags = QtCore.Qt.FramelessWindowHint | QtCore.Qt.Popup | QtCore.Qt.NoDropShadowWindowHint
        # flags = QtCore.Qt.FramelessWindowHint | QtCore.Qt.Popup

        self.menu.setWindowFlags(flags)
        self.menu.setAttribute(QtCore.Qt.WA_TranslucentBackground)

        self.menuSize = self.radius * 2 + self.buttonSize

        if state.app_state.compositing_manager:
            pass
        else:
            self.menu.setAttribute(QtCore.Qt.WA_PaintOnScreen)

    def stop_filter(self):
        app = QtGui.QGuiApplication.instance() or QtGui.QApplication([])
        app.removeEventFilter(self)

    def install_filter(self):
        app = QtGui.QGuiApplication.instance() or QtGui.QApplication([])
        app.installEventFilter(self)

    def show_menu(self):
        """Toggle the menu: hide it when visible, otherwise trigger the global shortcut."""
        if self.menu.isVisible():
            self.menu.hide()
        else:
            action_key.trigger()

    def validation(self):
        """Confirm the current spinbox value and close the dialog."""
        # fix https://github.com/Grubuntu/PieMenu/issues/130
        # quit current sketcher operation:
        Gui.runCommand("Sketcher_StopOperation")
        # to avoid that 'Sketcher_CompDimensionTools' being activated before resetEdit()
        Gui.ActiveDocument.resetEdit()
        App.ActiveDocument.recompute()
        pie_menu_instance.hide()

    def cancel(self):
        """Cancel the current feature and close the spinbox dialog."""
        docName = App.ActiveDocument.Name
        # quit current sketcher operation:
        Gui.runCommand("Sketcher_StopOperation")
        App.closeActiveTransaction(True)
        Gui.Control.closeDialog()
        App.getDocument(docName).recompute()
        Gui.getDocument(docName).resetEdit()
        pie_menu_instance.hide()

    def validButton(self, buttonSize=32):
        icon = icon_size(buttonSize)
        button = QtGui.QToolButton()
        button.setObjectName("styleComboValid")
        button.setProperty("ButtonX", -25)
        button.setProperty("ButtonY", 8)
        button.setGeometry(0, 0, buttonSize, buttonSize)
        button.setIconSize(QtCore.QSize(icon, icon))
        return button

    def cancelButton(self, buttonSize=32):
        icon = icon_size(buttonSize)
        button = QtGui.QToolButton()
        button.setObjectName("styleComboCancel")
        button.setProperty("ButtonX", 25)
        button.setProperty("ButtonY", 8)
        button.setGeometry(0, 0, buttonSize, buttonSize)
        button.setIconSize(QtCore.QSize(icon, icon))
        return button

    def doubleSpinbox(self, buttonSize=32, step=1.0):
        """ https://github.com/FreeCAD/FreeCAD/blob/main/src/Gui/QuantitySpinBox.h """
        ui = Gui.UiLoader()
        button = ui.createWidget("Gui::QuantitySpinBox")
        button.setProperty("minimum", 0.0)
        button.setFixedWidth(110)
        button.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        button.setProperty("ButtonX", 0)
        button.setProperty("ButtonY", -30)
        button.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        button.setStyleSheet(" QWidget { border-radius: 5px; }")
        button.setProperty("setSingleStep", step)
        button.valueChanged.connect(self.spin_interactif)
        return button

    def checkboxThroughAll(self):
        checkboxThroughAll = QCheckBox(
            translate("Fast Spinbox", "Through all"))
        checkboxThroughAll.setCheckable(True)
        checkboxThroughAll.setProperty("ButtonX", 50)
        checkboxThroughAll.setProperty("ButtonY", -105)
        checkboxThroughAll.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        return checkboxThroughAll

    def checkboxReversed(self):
        checkboxReversed = QCheckBox(translate("Fast Spinbox", "Reversed"))
        checkboxReversed.setCheckable(True)
        checkboxReversed.setProperty("ButtonX", 50)
        checkboxReversed.setProperty("ButtonY", -55)
        checkboxReversed.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        return checkboxReversed

    def checkboxSymToPlane(self):
        checkboxSymToPlane = QCheckBox(
            translate("Fast Spinbox", "Symmetric to plane"))
        checkboxSymToPlane.setCheckable(True)
        checkboxSymToPlane.setProperty("ButtonX", 50)
        checkboxSymToPlane.setProperty("ButtonY", -80)
        checkboxSymToPlane.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        return checkboxSymToPlane

    def eventFilter(self, obj, event):
        """Handle mouse and keyboard events """
        _lr = self._handle_left_button_release(event)
        if _lr is not None:
            return _lr

        _rc = self._handle_right_click(event)
        if _rc is not None:
            return _rc

        # Special case when shortcut is assigned to tool PieMenu AND also other there
        if event.type() == QtCore.QEvent.ShortcutOverride and self.menu.isVisible():
            _so = self._handle_shortcut_override(event)
            if _so is not None:
                return _so

        """ Handle keys Return and Enter for spinbox """
        if event.type() == QtCore.QEvent.KeyPress:
            _kp = self._handle_key_press(event)
            if _kp is not None:
                return _kp

        if event.type() == QtCore.QEvent.KeyRelease:
            _kr = self._handle_key_release(event)
            if _kr is not None:
                return _kr

        elif event.type() == QtCore.QEvent.Wheel:
            self._handle_wheel_event(event)
        self._handle_window_state(obj, event)
        return False

    def _handle_wheel_event(self, event):
        """Adjust the fast spinbox step on Ctrl/Shift + wheel.

        Extracted from ``PieMenu.eventFilter``. The spinbox only exists once a
        pie menu has been built; a missing one is a normal state.
        """
        """ Press CTRL + rotate Wheel = X10, Press SHIFT + rotate Wheel = X0.1, Press CTRL+SHIFT + rotate Wheel= X0.01 """
        modifiers = event.modifiers()
        if modifiers & QtCore.Qt.ControlModifier and modifiers & QtCore.Qt.ShiftModifier:
            # NOTE: weird behavior, you have to set 0.001 to modify the hundredths...
            step = 0.001
        elif modifiers & QtCore.Qt.ShiftModifier:
            step = 0.1
        else:
            step = 1.0
        # the fast spinbox only exists once a pie menu has been built
        if self.double_spinbox is not None:
            try:
                self.double_spinbox.setProperty("singleStep", step)
            except Exception as exc:
                log.log_warning("cannot set spinbox step", exc)


    def _handle_right_click(self, event):
        """Handle right-click timer/debounce for the spin-delay feature.

        Extracted from ``PieMenu.eventFilter``. Returns ``True``/``False``
        when the event is consumed, or ``None`` to let the caller continue.
        """
        try:
            # the checkbox is published by the preferences UI: None before that
            if checkbox_right_click is not None and checkbox_right_click.isChecked():
                if event.type() == QtCore.QEvent.MouseButtonPress:
                    if event.button() == QtCore.Qt.RightButton:
                        self.timer.start(spin_delay_right_click.value())
                        return False

                if event.type() == QtCore.QEvent.MouseButtonRelease:
                    if event.button() == QtCore.Qt.RightButton:
                        if self.timer.isActive():
                            self.timer.stop()
                            self.debounceTimer.start(100)
                            self.stop_filter()
                            return False
                        else:
                            return True
        except Exception as exc:
            log.log_error("eventFilter failed (right click handling)", exc)
        return None


    def _handle_key_press(self, event):
        """Handle KeyPress events (Enter/Return validation, tool-list keys).

        Extracted from ``PieMenu.eventFilter``. Returns ``True``/``False``
        when the event is consumed, or ``None`` to let the caller continue.
        """
        key = event.key()
        #### Confirm with 'Enter' or 'Return' key ####
        if key == QtCore.Qt.Key_Enter or key == QtCore.Qt.Key_Return:
            # spinbox / pie menu may not exist: only validate when they do
            try:
                if self.double_spinbox.isVisible():
                    self.validation()
            except Exception:
                None
            try:
                if self.menu.isVisible():
                    self.validation()
            except Exception:
                None
                return True

        #### Keys SUPPR, DEL, UP and DOWN in Toollist ####
        """ Handle Keys SUPPR, DEL, UP and DOWN in Toollist """
        # move/delete only when 'tabs' is visible (not in ToolbarTab's settings)
        if tabs.isVisible():
            if key == Qt.Key_Backspace or key == Qt.Key_Delete:
                if button_list_widget.hasFocus():
                    on_button_remove_command()
                    return True
            if key == Qt.Key_Up:
                if button_list_widget.hasFocus():
                    on_button_up()
                    return True
            if key == Qt.Key_Down:
                if button_list_widget.hasFocus():
                    on_button_down()
                    return True
        return None


    def _handle_left_button_release(self, event):
        """Hide the menu on a left click outside the menu/dialog.

        Extracted from ``PieMenu.eventFilter``. Returns ``False`` when the
        event is consumed (menu hidden), or ``None`` to let the caller
        continue.
        """
        if event.type() == QtCore.QEvent.MouseButtonRelease:
            if event.button() == QtCore.Qt.LeftButton:
                if self.menu.isActiveWindow() or pie_menu_dialog.isVisible():
                    pass
                else:
                    self.menu.hide()
                    for i in self.buttons:
                        i.hide()
                    return False
        return None


    def _handle_window_state(self, obj, event):
        """Hide the menu when the main window is minimised.

        Extracted from ``PieMenu.eventFilter``.
        """
        """ Filtrer les événements pour détecter la minimisation """
        if obj == self.mw and event.type() == QtCore.QEvent.WindowStateChange:
            # Vérifier si la fenêtre principale est minimisée
            if self.mw.isMinimized():
                self.menu.hide()
        return None


    def _handle_shortcut_override(self, event):
        """Handle ShortcutOverride events (tool shortcuts, toggle mode).

        Extracted from ``PieMenu.eventFilter``. Returns ``True``/``False``
        when the event is consumed, or ``None`` to let the caller continue.
        """
        # we need to set "state.app_state.flag_shortcut_override" to advertise that we go through Event.ShortcutOverride for this tool shortcut for the step "KeyRelease" below
        state.app_state.flag_shortcut_override = False
        key = event.key()
        event.accept()
        try:
            # if fast spinbox is open, we do nothing with shortcuts
            if self.double_spinbox.isVisible():
                pass
        except Exception:
            # spinbox not show
            try:
                charKey = chr(key)
            except Exception:
                charKey = ''
            if charKey in state.app_state.list_shortcut_code:
                self.menu.hide()
                j = 0
                for i in state.app_state.list_shortcut_code:
                    if i == charKey:
                        # set flag here
                        state.app_state.flag_shortcut_override = True
                    j += 1
                return True
            # Handle toggle mode for global shortcut###
            elif checkbox_global_key_toggle.isChecked():
                if event.key() == QtGui.QKeySequence(state.app_state.global_shortcut_key):
                    if self.menu.isVisible():
                        self.menu.hide()
                        return True
                    else:
                        return False

                for shortcut in self.mw.findChildren(QShortcut):
                    if event.key() == QtGui.QKeySequence(shortcut.key()):
                        if self.menu.isVisible():
                            self.menu.hide()
                            event.accept()
                            return True
                        else:
                            return False
        return None


    def _trigger_tool_shortcut(self, event, charKey):
        """Trigger the tool bound to ``charKey`` if it is a known shortcut.

        Extracted from ``PieMenu._handle_key_release`` (the body was
        duplicated for the two shortcut-override branches). Returns ``True``
        when a shortcut was handled, ``False`` otherwise. Always resets
        ``flag_shortcut_override`` once a shortcut has been triggered.
        """
        if charKey not in state.app_state.list_shortcut_code:
            return False
        self.menu.hide()
        event.accept()
        j = 0
        for i in state.app_state.list_shortcut_code:
            if i == charKey:
                # trigger tool shortcut action
                state.app_state.list_commands[j].trigger()
                state.app_state.flag_shortcut_override = False
                module = None
                event.accept()
                try:
                    g = Gui.ActiveDocument.getInEdit()
                    module = g.Module
                    displaySpinBox = get_parameter_global("Bool", constants.PARAM_DISPLAY_SPIN_BOX)
                    if (module is not None and module != 'SketcherGui') and displaySpinBox:
                        pie_menu_instance.showAtMouseInstance()
                except Exception:
                    # not in edit mode: do not open the spinbox
                    pass
            j += 1
        return True


    def _handle_key_release(self, event):
        """Handle KeyRelease events (tool shortcuts, context list_topo).

        Extracted from ``PieMenu.eventFilter``. Returns ``True`` when a
        shortcut was triggered, or ``None`` to let the caller continue.
        """
        """ Handle tool shortcut in PieMenu """
        if state.app_state.flag_shortcut_override:
            key = event.key()
            try:
                # if fast spinbox is open, we do nothing with shortcuts
                if self.double_spinbox.isVisible():
                    pass
            except Exception:
                # spinbox not show
                try:
                    charKey = chr(key)
                except Exception:
                    charKey = ''

                if self._trigger_tool_shortcut(event, charKey):
                    return True

        if self.menu.isVisible() and state.app_state.flag_shortcut_override:
            key = event.key()
            try:
                # if fast spinbox is open, we do nothing with shortcuts
                if self.double_spinbox.isVisible():
                    pass
            except Exception:
                # spinbox not show
                try:
                    charKey = chr(key)
                except Exception:
                    charKey = ''

                if self._trigger_tool_shortcut(event, charKey):
                    return True
        # run listTopo (context) when CTRL is release: allow multiple selection
        if event.type() == QtCore.QEvent.KeyRelease and event.key() == QtCore.Qt.Key_Control:
            enableContext = config.get_params()["main"].GetBool(constants.PARAM_ENABLE_CONTEXT)
            if enableContext:
                self.debounceTimer.start(100)
                self.stop_filter()
                list_topo()
        return None




    def add_commands(self, commands, context=False, keyValue=None):
        """ Add commands to mieMenus """
        if state.app_state.first_load:
            # Load the needed workbenches at the first launch
            update_icons_pie_menus()
            state.app_state.first_load = False

        styleCurrentTheme = get_style()
        # initialise so the values are always bound, even when the try below
        # fails (the edit-mode helper is only allowed to touch them inside
        # its own guard, but evaluating them as call arguments must not raise)
        g = None
        wbName = None
        module = None
        try:
            g = Gui.ActiveDocument.getInEdit()
            module = g.Module
            wb = Gui.activeWorkbench()
            wbName = wb.name()
        except Exception:
            module = None

        for i in self.buttons:
            i.deleteLater()
        self.buttons = []
        group = resolve_pie_group(keyValue, context)

        if len(commands) == 0:
            commandNumber = 1
        else:
            commandNumber = len(commands)

        self.offset_x = 0
        self.offset_y = 0
        # per-button icon label, created only in some layout branches
        iconLabel = None

        # read the pie menu parameters (radius, shape, display flags...)
        settings = read_pie_settings(group, keyValue, commandNumber)
        valueRadius = settings.value_radius
        self.radius = settings.radius
        self.buttonSize = settings.button_size
        buttonSize = settings.button_size
        shape = settings.shape
        num_of_column = settings.num_of_column
        icon_spacing = settings.icon_spacing
        command_per_circle = settings.command_per_circle
        shortcutLabelSize = settings.shortcut_label_size
        angle, angleStart = settings.angle, settings.angle_start
        radius = settings.radius_css
        icon = settings.icon
        displayCommandName = settings.display_command_name
        displayPreselect = settings.display_preselect
        enableShortcut = settings.enable_shortcut
        displayShortcut = settings.display_shortcut
        number_of_circle = 1

        showPie = should_show_pie(module)

        if showPie:
            _layout = self._init_pie_layout(commandNumber)
            num = _layout.num
            ecart = _layout.ecart
            Y = _layout.Y
            X = _layout.X
            X_shortcut = _layout.X_shortcut
            Y_shortcut = _layout.Y_shortcut
            shortcutCode = _layout.shortcutCode
            maxTextLength = _layout.maxTextLength
            ctx = SimpleNamespace(
                commands=commands, styleCurrentTheme=styleCurrentTheme,
                shape=shape, displayCommandName=displayCommandName,
                displayPreselect=displayPreselect, enableShortcut=enableShortcut,
                displayShortcut=displayShortcut, valueRadius=valueRadius,
                buttonSize=buttonSize, icon=icon, radius=radius,
                angle=angle, angleStart=angleStart, X=X, Y=Y,
                X_shortcut=X_shortcut, Y_shortcut=Y_shortcut,
                maxTextLength=maxTextLength, iconLabel=iconLabel, num=num,
                ecart=ecart, num_of_column=num_of_column,
                icon_spacing=icon_spacing, command_per_circle=command_per_circle,
                number_of_circle=number_of_circle,
                shortcutLabelSize=shortcutLabelSize, shortcutCode=shortcutCode,
                commandNumber=commandNumber)
            self._build_pie_buttons(ctx)
            buttonSize = ctx.buttonSize
            icon = ctx.icon
            radius = ctx.radius
            angle = ctx.angle
            X = ctx.X
            Y = ctx.Y
            X_shortcut = ctx.X_shortcut
            Y_shortcut = ctx.Y_shortcut
            maxTextLength = ctx.maxTextLength
            iconLabel = ctx.iconLabel
            num = ctx.num
            num_of_column = ctx.num_of_column
            command_per_circle = ctx.command_per_circle
            number_of_circle = ctx.number_of_circle
            shortcutCode = ctx.shortcutCode

        self._add_quick_menu_and_close_button(module)

        try:
            self._setup_edit_mode_buttons(module, g, wbName, styleCurrentTheme)
        except Exception as exc:
            log.log_error("spinbox setup failed in add_commands", exc)

        if state.app_state.compositing_manager:
            pass
        else:
            for i in self.buttons:
                i.setAttribute(QtCore.Qt.WA_PaintOnScreen)

    def _setup_edit_mode_buttons(self, module, g, wbName, styleCurrentTheme):
        """Build the Valid/Cancel buttons and the fast PartDesign spinbox.

        Extracted from ``PieMenu.add_commands``. The block is only entered
        when a document is being edited (see the guard at the top). It mutates
        ``self`` (spinbox, checkboxes, offset) and appends its buttons to
        ``self.buttons``. Missing attributes (e.g. ``checkbox_throughAll``)
        are expected for some PartDesign features and are left at their
        default value.
        """
        # without an active document there is nothing to validate: skip the block
        if (Gui.ActiveDocument is not None and Gui.ActiveDocument.getInEdit() is not None and not (module == 'AssemblyGui')):
            """ or show Valid and Cancel buttons in Edit Feature Only """
            buttonValid = self.validButton()
            buttonValid.setStyleSheet(styleCurrentTheme)
            buttonValid.setParent(self.menu)
            buttonValid.clicked.connect(self.validation)
            self.buttons.append(buttonValid)

            buttonCancel = self.cancelButton()
            buttonCancel.setStyleSheet(styleCurrentTheme)
            buttonCancel.setParent(self.menu)
            buttonCancel.clicked.connect(self.cancel)
            self.buttons.append(buttonCancel)

            if (module is not None and module != 'SketcherGui' and wbName == 'PartDesignWorkbench'):
                """ Show Spinbox in Edit Feature in Part Design WB only """
                layoutOptions = QtGui.QVBoxLayout()
                fonctionActive = g.Object

                self.double_spinbox = self.doubleSpinbox()
                self.double_spinbox.setParent(self.menu)
                self.double_spinbox.valueChanged.connect(
                    self.spin_interactif)
                self.buttons.append(self.double_spinbox)
                self.double_spinbox.setVisible(True)

                def checkbox_layout(checkbox_func, ObjectAttribute="Type", ObjectType=True):
                    checkbox = checkbox_func()
                    checkbox.setParent(self.menu)
                    checkbox.setObjectName("styleCheckbox")
                    checkbox.setStyleSheet(styleCurrentTheme)
                    checkbox.setMinimumWidth(220)
                    checkbox.stateChanged.connect(self.spin_interactif)

                    self.buttons.append(checkbox)

                    if getattr(g.Object, ObjectAttribute) == ObjectType:
                        checkbox.setChecked(True)
                    else:
                        checkbox.setChecked(False)
                    self.checkbox = checkbox
                    return self.checkbox

                layoutMidPlane = QHBoxLayout()
                layoutReversed = QHBoxLayout()
                layoutThroughAll = QHBoxLayout()

                if (str(fonctionActive) == '<PartDesign::Fillet>'):
                    Gui.ExpressionBinding(self.double_spinbox).bind(
                        g.Object, constants.PARAM_RADIUS)
                    quantity = Units.Quantity(Units.Quantity(
                        g.Object.Radius).getUserPreferred()[0])

                elif (str(fonctionActive) == '<PartDesign::Chamfer>'):
                    Gui.ExpressionBinding(
                        self.double_spinbox).bind(g.Object, "Size")
                    quantity = Units.Quantity(Units.Quantity(
                        g.Object.Size).getUserPreferred()[0])

                elif (str(fonctionActive) == '<PartDesign::Thickness>'):
                    Gui.ExpressionBinding(
                        self.double_spinbox).bind(g.Object, "Value")
                    quantity = Units.Quantity(Units.Quantity(
                        g.Object.Value).getUserPreferred()[0])

                elif (str(fonctionActive) == '<PartDesign::Pad>') or (str(fonctionActive) == '<PartDesign::Pocket>'):
                    Gui.ExpressionBinding(self.double_spinbox).bind(
                        g.Object, "Length")
                    quantity = Units.Quantity(Units.Quantity(
                        g.Object.Length).getUserPreferred()[0])

                    self.checkbox_midPlane = checkbox_layout(
                        self.checkboxSymToPlane, "Midplane", True)
                    layoutMidPlane.addWidget(self.checkbox_midPlane)
                    layoutOptions.addLayout(layoutMidPlane)

                    self.checkbox_reversed = checkbox_layout(
                        self.checkboxReversed, "Reversed", True)
                    layoutReversed.addWidget(self.checkbox_reversed)
                    layoutOptions.addLayout(layoutReversed)

                    if (str(fonctionActive) == '<PartDesign::Pocket>'):
                        self.checkbox_throughAll = checkbox_layout(
                            self.checkboxThroughAll, "Type", "ThroughAll")

                        layoutThroughAll.addWidget(
                            self.checkbox_throughAll)
                        layoutOptions.addLayout(layoutThroughAll)

                elif (str(fonctionActive) == '<PartDesign::Revolution>') or (str(fonctionActive) == '<PartDesign::Groove>'):
                    Gui.ExpressionBinding(
                        self.double_spinbox).bind(g.Object, "Angle")
                    quantity = Units.Quantity(Units.Quantity(
                        g.Object.Angle).getUserPreferred()[0])

                    self.checkbox_midPlane = checkbox_layout(
                        self.checkboxSymToPlane, "Midplane", True)
                    layoutMidPlane.addWidget(self.checkbox_midPlane)
                    layoutOptions.addLayout(layoutMidPlane)

                    self.checkbox_reversed = checkbox_layout(
                        self.checkboxReversed, "Reversed", True)
                    layoutReversed.addWidget(self.checkbox_reversed)
                    layoutOptions.addLayout(layoutReversed)

                self.double_spinbox.setProperty('value', quantity)

                self.double_spinbox.setFocus()
                self.double_spinbox.selectAll()

                self.offset_x = 10
                self.offset_y = 28


    def _add_quick_menu_and_close_button(self, module):
        """Add the quick-menu button and the close button (when applicable).

        Extracted from ``PieMenu.add_commands``. The close button is only
        added when no object is being edited (or the assembly module is
        active); a missing GUI document is a normal state and is swallowed.
        """
        buttonQuickMenu = quick_menu()
        if checkbox_quick_menu.isChecked():
            buttonQuickMenu.setParent(self.menu)
            self.buttons.append(buttonQuickMenu)
        else:
            buttonQuickMenu.hide()

        try:
            # only add the close button when no object is being edited
            if (Gui.ActiveDocument.getInEdit() is None or (module == 'AssemblyGui')):
                buttonClose = close_button()
                buttonClose.setParent(self.menu)
                self.buttons.append(buttonClose)
        except Exception:
            # no active document (or assembly module): skip the close button
            None


    def _handle_separator(self, button, buttonPreselect, iconLabel, icon):
        """Style a button that is a Separator tool.

        Extracted from ``PieMenu.add_commands`` (called inside the per-button
        loop). ``iconLabel`` may be ``None`` for shapes without command
        names; the missing-icon case is swallowed.
        """
        button.setObjectName("styleSeparator")
        button.setIcon(QtGui.QIcon(resources.iconSeparator))
        iconButton = QtGui.QIcon(resources.iconSeparator)
        buttonPreselect.setVisible(False)
        if iconLabel is not None:
            try:
                iconLabel.setPixmap(
                    iconButton.pixmap(QtCore.QSize(icon, icon)))
            except Exception as exc:
                log.log_warning("cannot set separator icon", exc)


    def _create_pie_button(self, commands, i, buttonSize, icon, radius, styleCurrentTheme):
        """Create the HoverButton and its PreselectButton arrow.

        Extracted from ``PieMenu.add_commands`` (called inside the per-button
        loop). Returns ``(button, buttonPreselect)``.
        """
        button = HoverButton()
        button.setParent(self.menu)
        button.setObjectName("pieMenu")
        button.setAttribute(QtCore.Qt.WA_Hover)
        button.setStyleSheet(styleCurrentTheme + radius)
        button.setDefaultAction(commands[commands.index(i)])
        button.setIconSize(QtCore.QSize(icon, icon))
        button.setGeometry(0, 0, buttonSize, buttonSize)

        # Preselection Arrow
        buttonPreselect = PreselectButton()
        return button, buttonPreselect


    def _init_pie_layout(self, commandNumber):
        """Initialise the shared layout variables for a Pie-shaped menu.

        Extracted from ``PieMenu.add_commands`` (only entered when
        ``showPie``). Returns a namespace with the starting values of
        ``num``, ``ecart``, ``Y``, ``X``, ``X_shortcut``, ``Y_shortcut``,
        ``shortcutCode`` and ``maxTextLength``.
        """
        num = 1

        ### for Pie shape with commands names ###
        ecart = (2 * self.radius) / ((commandNumber)/2)
        Y = -self.radius - ecart
        X = 0
        X_shortcut = 0
        Y_shortcut = 0

        ### 48 = code ascii pour le chiffre 0 ###
        shortcutCode = 48
        state.app_state.list_commands = []
        state.app_state.list_shortcut_code = []
        maxTextLength = 0
        return SimpleNamespace(
            num=num, ecart=ecart, Y=Y, X=X,
            X_shortcut=X_shortcut, Y_shortcut=Y_shortcut,
            shortcutCode=shortcutCode, maxTextLength=maxTextLength)


    def _setup_preselect_button(self, button, buttonPreselect, commands, i, angle, num, angleStart, buttonSize, icon, styleCurrentTheme):
        """Build the preselection-arrow button for one pie button.

        Extracted from ``PieMenu.add_commands`` (called inside the per-button
        loop, only when ``displayPreselect`` is set). Mutates
        ``buttonPreselect`` and appends it to ``self.buttons``.
        """
        buttonPreselect.setParent(self.menu)
        buttonPreselect.setObjectName("stylebuttonPreselect")
        buttonPreselect.setAttribute(QtCore.Qt.WA_Hover)
        buttonPreselect.setStyleSheet(styleCurrentTheme)
        buttonPreselect.setDefaultAction(
            commands[commands.index(i)])
        buttonPreselect.setToolTip(None)

        angle_total = angle * num + angleStart + math.pi*3/2
        sizeRound = buttonSize * \
            (abs(math.sin(angle_total)) +
             abs(math.cos(angle_total)))

        buttonPreselect.setIconSize(
            QtCore.QSize(sizeRound, sizeRound))
        rotation_angle = math.degrees(
            angle * num + angleStart) + 270
        buttonPreselect.originalPixmap = QtGui.QPixmap(
            resources.iconArrowDown)
        buttonPreselect.setGeometry(0, 0, sizeRound, sizeRound)

        trans = QTransform()
        trans.rotate(rotation_angle)
        transformed_pixmap = buttonPreselect.originalPixmap.transformed(
            trans)

        blankIcon = QtGui.QPixmap(resources.iconBlank)
        buttonPreselect.setIcon(QtGui.QIcon(blankIcon))
        buttonPreselect.setBaseIcon(QtGui.QIcon(blankIcon))
        buttonPreselect.setHoverIcon(
            QtGui.QIcon(transformed_pixmap))

        self.buttons.append(buttonPreselect)


    def _create_shortcut_label(self, commands, i, shortcutLabelSize, styleCurrentTheme, icon, X_shortcut, Y_shortcut, shortcutCode, displayShortcut):
        """Create a shortcut-key label for one pie button.

        Extracted from ``PieMenu.add_commands`` (called inside the per-button
        loop, only when ``enableShortcut`` is set). Mutates ``shortcutCode``
        (skipping 57/88) and appends to ``self.buttons`` when
        ``displayShortcut``. Returns the updated ``shortcutCode``.
        """
        if shortcutCode > 90:
            return shortcutCode
        # Add button label for Shortcuts Tools on PieMenu
        shortcutLabel = HoverButton()
        shortcutLabel.setParent(self.menu)
        shortcutLabel.setObjectName(
            "pieMenuShortcutTool")

        fontSize = ("QToolButton#pieMenuShortcutTool {font-size: " + str(
            shortcutLabelSize) + "px; padding: 0px; margin: 0px;}")

        shortcutLabel.setStyleSheet(
            styleCurrentTheme + fontSize)
        shortcutLabel.setDefaultAction(
            commands[commands.index(i)])
        shortcutLabel.setToolButtonStyle(
            Qt.ToolButtonTextOnly)
        shortcutLabel.setText(chr(shortcutCode))
        shortcutLabel.setToolTip(None)
        shortcutLabel.setFixedSize(
            shortcutLabelSize + 6, shortcutLabelSize + 6)

        state.app_state.list_commands.append(
            commands[commands.index(i)])
        state.app_state.list_shortcut_code.append(chr(shortcutCode))

        if shortcutCode == 57:
            shortcutCode = 64
        shortcutCode += 1
        # trick to avoid X key which bug !
        if shortcutCode == 88:
            shortcutCode = 89

        shortcutLabel.setProperty(
            "ButtonX", X_shortcut)
        shortcutLabel.setProperty(
            "ButtonY", Y_shortcut)

        if displayShortcut:
            self.buttons.append(shortcutLabel)
        return shortcutCode


    def _layout_concentric(self, button, num, angle, angleStart, command_per_circle, number_of_circle, buttonSize, icon_spacing, icon):
        """Lay out one button for the Concentric shape.

        Extracted from ``PieMenu.add_commands``. Mutates ``self.radius`` and
        ``self.menu``; returns the updated layout variables.
        """
        ### Concentric ###
        button.setProperty("ButtonX", self.radius *
                           (math.cos(angle * num + angleStart)))
        button.setProperty("ButtonY", self.radius *
                           (math.sin(angle * num + angleStart)))

        X_shortcut = (self.radius) * \
            (math.cos(angle * num + angleStart)) + icon/2
        Y_shortcut = (self.radius) * \
            (math.sin(angle * num + angleStart)) + icon/2

        if ((num % command_per_circle) == 0):
            num = 0
            self.radius = self.radius + buttonSize + icon_spacing
            number_of_circle = number_of_circle + 1
            command_per_circle = command_per_circle + command_per_circle
            angle = 2 * math.pi / command_per_circle
            angleStart = angleStart + angle/2

        # self.menu size Concentric
        width =  self.radius * 2 + buttonSize + 4
        height = self.radius * 2 + buttonSize + 4
        self.menu.setFixedSize(width, height)
        return num, angle, angleStart, command_per_circle, number_of_circle, X_shortcut, Y_shortcut


    def _layout_star(self, button, num, angle, angleStart, command_per_circle, buttonSize, icon_spacing, icon):
        """Lay out one button for the Star shape.

        Extracted from ``PieMenu.add_commands``. Mutates ``self.radius`` and
        ``self.menu``; returns the updated ``X_shortcut``/``Y_shortcut``.
        """
        ### Star ###
        button.setProperty("ButtonX", self.radius *
                           (math.cos(angle * num + angleStart)))
        button.setProperty("ButtonY", self.radius *
                           (math.sin(angle * num + angleStart)))

        X_shortcut = (self.radius) * \
            (math.cos(angle * num + angleStart)) + icon/2
        Y_shortcut = (self.radius) * \
            (math.sin(angle * num + angleStart)) + icon/2

        if ((num % command_per_circle) == 0):
            self.radius = self.radius + buttonSize + icon_spacing

        # self.menu size Star
        width =  self.radius * 2 + icon_spacing + buttonSize
        height = self.radius * 2 + icon_spacing + buttonSize
        self.menu.setFixedSize(width, height)
        return X_shortcut, Y_shortcut


    def _layout_updown(self, button, commandNumber, num, num_of_column, buttonSize, icon_spacing, icon, valueRadius):
        """Lay out one button for the UpDown shape.

        Extracted from ``PieMenu.add_commands``. Mutates ``self.menu``;
        returns the updated ``num_of_column`` and shortcut offsets.
        ``self.radius`` is read (not mutated) by this branch.
        """
        ### Table Up and Down  ###
        num_of_column = math.ceil(commandNumber / 2)
        X = ((num - 1) % num_of_column) * \
            (buttonSize + icon_spacing)
        if ((num - 1) < num_of_column):
            offset = 0
            side = -1
        else:
            offset = 2 * self.radius
            side = 1
        Y = (self.radius - offset)

        button.setProperty(
            "ButtonX", X - ((num_of_column - 1) * (buttonSize + icon_spacing)) / 2)
        button.setProperty("ButtonY", -Y)

        X_shortcut = X - \
            ((num_of_column - 1) *
             (buttonSize + icon_spacing)) / 2 + icon/2
        Y_shortcut = -Y - (side * icon/2)

        # self.menu size Table Up and Down
        width = num_of_column * (buttonSize + 4 + icon_spacing)
        height = valueRadius * 2 + buttonSize + 4
        self.menu.setFixedSize(width, height)
        return num_of_column, X_shortcut, Y_shortcut


    def _layout_table_top(self, button, num, commandNumber, num_of_column, buttonSize, icon_spacing, icon, valueRadius):
        """Lay out one button for the TableTop shape.

        Extracted from ``PieMenu.add_commands``. Mutates ``self.menu``;
        returns the updated ``X_shortcut``/``Y_shortcut``.
        ``self.radius`` is read (not mutated) by this branch.
        """
        ### Table  Top ###
        num_of_line = math.ceil(commandNumber/num_of_column)
        offset = num_of_line * (buttonSize + icon_spacing)
        X = ((num-1) % num_of_column) * \
            (buttonSize + icon_spacing)
        Y = self.radius / 2 + \
            ((num-1) // num_of_column) * \
            (buttonSize + icon_spacing)
        button.setProperty(
            "ButtonX", X - ((num_of_column-1) * (buttonSize + icon_spacing)) / 2)
        button.setProperty("ButtonY", -Y)

        X_shortcut = (
            X - ((num_of_column-1) * (buttonSize + icon_spacing)) / 2) + icon/2
        Y_shortcut = -Y + icon/2

        # self.menu size Table Top
        width = num_of_column * (buttonSize + icon_spacing)
        height = valueRadius + offset + (buttonSize + icon_spacing) * (num_of_line - 1)
        self.menu.setFixedSize(width, height)
        return X_shortcut, Y_shortcut


    def _layout_table_down(self, button, num, commandNumber, num_of_column, buttonSize, icon_spacing, icon, valueRadius):
        """Lay out one button for the TableDown shape.

        Extracted from ``PieMenu.add_commands``. Mutates ``self.menu``;
        returns the updated ``X_shortcut``/``Y_shortcut``.
        ``self.radius`` is read (not mutated) by this branch.
        """
        ### Table Down  ###
        num_of_line = math.ceil(commandNumber/num_of_column)
        offset = num_of_line * (buttonSize + icon_spacing)
        X = ((num-1) % num_of_column) * \
            (buttonSize + icon_spacing)
        Y = - buttonSize - self.radius / 4 - \
            ((num-1) // num_of_column) * \
            (buttonSize + icon_spacing)
        button.setProperty(
            "ButtonX", X - ((num_of_column-1) * (buttonSize + icon_spacing)) / 2)
        button.setProperty("ButtonY", -Y)

        X_shortcut = (
            X - ((num_of_column-1) * (buttonSize + icon_spacing)) / 2) + icon/2
        Y_shortcut = -Y - icon/2

        # self.menu size Table Down
        width = num_of_column * (buttonSize + icon_spacing)
        height = valueRadius + offset + (buttonSize + icon_spacing) * (num_of_line - 1)
        self.menu.setFixedSize(width, height)
        return X_shortcut, Y_shortcut


    def _layout_table_left(self, button, num, commandNumber, num_of_column, buttonSize, icon_spacing, icon, valueRadius):
        """Lay out one button for the TableLeft shape.

        Extracted from ``PieMenu.add_commands``. Mutates ``self.menu``;
        returns the updated ``X_shortcut``/``Y_shortcut``.
        ``self.radius`` is read (not mutated) by this branch.
        """
        ### Table Left  ###
        num_of_line = math.ceil(commandNumber/num_of_column)
        X = - buttonSize - self.radius / 2 - \
            ((num-1) // num_of_column) * \
            (buttonSize + icon_spacing)
        Y = ((num-1) % num_of_column) * \
            (buttonSize + icon_spacing)
        button.setProperty("ButtonX", X)
        button.setProperty(
            "ButtonY", Y - ((num_of_column-1) * (buttonSize + icon_spacing)) / 2)

        X_shortcut = X + icon/2
        Y_shortcut = Y - \
            ((num_of_column-1) * (buttonSize + icon_spacing)) / 2 + icon/2

        # self.menu size Table Left
        width = 2 * (valueRadius + num_of_line * (buttonSize + 4 + icon_spacing))
        height = num_of_column * (icon_spacing + buttonSize + 4)
        self.menu.setFixedSize(width, height)
        return X_shortcut, Y_shortcut


    def _layout_table_right(self, button, num, commandNumber, num_of_column, buttonSize, icon_spacing, icon, valueRadius):
        """Lay out one button for the TableRight shape.

        Extracted from ``PieMenu.add_commands``. Mutates ``self.menu``;
        returns the updated ``X_shortcut``/``Y_shortcut``.
        ``self.radius`` is read (not mutated) by this branch.
        """
        ### Table Right  ###
        num_of_line = math.ceil(commandNumber/num_of_column)
        X = buttonSize + self.radius / 2 + \
            ((num-1) // num_of_column) * \
            (buttonSize + icon_spacing)
        Y = ((num-1) % num_of_column) * \
            (buttonSize + icon_spacing)
        button.setProperty("ButtonX", X)
        button.setProperty(
            "ButtonY", Y - ((num_of_column-1) * (buttonSize + icon_spacing)) / 2)

        X_shortcut = X - icon/2
        Y_shortcut = Y - \
            ((num_of_column-1) * (buttonSize + icon_spacing)) / 2 + icon/2

        # self.menu size Table Right
        width = 2 * (valueRadius + num_of_line * (buttonSize + 4 + icon_spacing))
        height = num_of_column * (icon_spacing + buttonSize + 4)
        self.menu.setFixedSize(width, height)
        return X_shortcut, Y_shortcut


    def _layout_pie_simple(self, button, buttonPreselect, num, angle, angleStart, buttonSize, icon, valueRadius):
        """Lay out one button for Pie-without-names / RainbowUp / RainbowDown.

        Extracted from ``PieMenu.add_commands``. Mutates ``button``,
        ``buttonPreselect`` and ``self.menu``; returns the updated
        ``X_shortcut``/``Y_shortcut``. ``self.radius`` is read (not
        mutated) by this branch.
        """
        ### Pie without commands names / RainbowUp / RainbowDown   ###
        button.setProperty("ButtonX", self.radius *
                           (math.cos(angle * num + angleStart)))
        button.setProperty("ButtonY", self.radius *
                           (math.sin(angle * num + angleStart)))

        X_shortcut = (self.radius) * \
            (math.cos(angle * num + angleStart)) + icon/2
        Y_shortcut = (self.radius) * \
            (math.sin(angle * num + angleStart)) + icon/2

        buttonPreselect.setProperty(
            "ButtonX", (self.radius - 1.2 * buttonSize) * (math.cos(angle * num + angleStart)))
        buttonPreselect.setProperty(
            "ButtonY", (self.radius - 1.2 * buttonSize) * (math.sin(angle * num + angleStart)))

        # self.menu size Pie without commands names / RainbowUp / RainbowDown
        width =  valueRadius * 2 + buttonSize + 4
        height = valueRadius * 2 + buttonSize + 4
        self.menu.setFixedSize(width, height)
        return X_shortcut, Y_shortcut


    def _layout_leftright(self, button, commands, i, num, commandNumber, num_of_column, buttonSize, icon_spacing, icon, valueRadius, styleCurrentTheme, radius, maxTextLength, displayCommandName, iconLabel):
        """Lay out one button for the LeftRight shape.

        Extracted from ``PieMenu.add_commands``. Mutates ``button``,
        ``iconLabel`` (may be created here) and ``self.menu``; returns the
        updated ``num_of_column``, ``maxTextLength``, ``X_shortcut``,
        ``Y_shortcut`` and ``iconLabel``.
        """
        ### Left and Right with command names ###
        if displayCommandName:
            num_of_column = math.ceil(commandNumber/2)
            button.setIcon(QtGui.QIcon())
            # set padding and font size dependind on icon size
            font_size = round(icon/2)
            if ((num-1) < (num_of_column)):
                # Left side icons
                padding = "QToolButton#pieMenu {padding-right: " + str(icon) \
                    + "px; font-size: " + \
                    str(font_size) + "px;}"
            else:
                # Right side icons
                padding = "QToolButton#pieMenu {padding-left: " + str(icon) \
                    + "px; font-size: " + \
                    str(font_size) + "px;}"
            button.setStyleSheet(
                styleCurrentTheme + radius + padding)
            # get length of the string
            text_length = QFontMetrics(button.font()).horizontalAdvance(
                commands[commands.index(i)].text())

            button.setGeometry(
                buttonSize, 0,  2 * buttonSize + text_length, buttonSize)
            # layout for icon and command string
            layout = QtGui.QHBoxLayout(button)
            layout.setContentsMargins((icon/4), 0, 0, 0)
            if ((num-1) < (num_of_column)):
                # Left side icons: align icon to the right and add some margin
                layout.addStretch(1)
                iconMarging = "#iconLabel {margin-right: " + \
                    str(icon/4) + "px;}"

            iconButton = QtGui.QIcon(
                commands[commands.index(i)].icon())
            iconLabel = QtGui.QLabel()
            iconLabel.setObjectName("iconLabel")
            iconLabel.setPixmap(
                iconButton.pixmap(QtCore.QSize(icon, icon)))
            if ((num-1) < (num_of_column)):
                # Left side icons
                iconLabel.setStyleSheet(
                    styleCurrentTheme + iconMarging)
            else:
                # Right side icons
                iconLabel.setStyleSheet(styleCurrentTheme)
            layout.addWidget(iconLabel)
            Y = ((num - 1) % num_of_column) * \
                (buttonSize + icon_spacing)
            if ((num-1) < (num_of_column)):
                # Left side icons
                offset = - text_length
                side = -1
            else:
                # Right side icons
                offset = 2 * self.radius
                side = 1
            # TODO: align them to the left
            X = (self.radius - offset - text_length/2)

            button.setProperty("ButtonX", -X)
            button.setProperty(
                "ButtonY", Y - ((num_of_column - 1) * (buttonSize + icon_spacing)) / 2)

            X_shortcut = side * (self.radius - buttonSize)
            Y_shortcut = Y - \
                ((num_of_column - 1) *
                 (buttonSize + icon_spacing)) / 2 + icon/2
            # self.menu size Left and Right with command names
            if text_length > maxTextLength:
                maxTextLength = text_length
            width = valueRadius * 2 + buttonSize + 4 + maxTextLength * 2 
            height = valueRadius * 2 + buttonSize + 4 + icon_spacing * (commandNumber/2)
            self.menu.setFixedSize(width, height)

        else:
            ### Left and Right  ###
            num_of_column = math.ceil(commandNumber/2)
            Y = ((num - 1) % num_of_column) * \
                (buttonSize + icon_spacing)
            if ((num-1) < (num_of_column)):
                offset = 0
                side = -1
            else:
                offset = 2*self.radius
                side = 1
            X = (self.radius - offset)

            button.setProperty("ButtonX", -X)
            button.setProperty(
                "ButtonY", Y - ((num_of_column - 1) * (buttonSize + icon_spacing)) / 2)

            X_shortcut = -X - (side * icon/2)
            Y_shortcut = Y - \
                ((num_of_column - 1) *
                 (buttonSize + icon_spacing)) / 2 + icon/2

            # self.menu size Left and Right without command names
            width = valueRadius * 2 + buttonSize + 4 
            height = valueRadius * 2 + buttonSize + 4 + icon_spacing * (commandNumber/2)
            self.menu.setFixedSize(width, height)
        return num_of_column, maxTextLength, X_shortcut, Y_shortcut, iconLabel


    def _layout_pie_with_names(self, button, buttonPreselect, commands, i, num, commandNumber, ecart, buttonSize, radius, icon, styleCurrentTheme, valueRadius, angle, angleStart, X, Y, X_shortcut, Y_shortcut, maxTextLength, iconLabel):
        """Lay out one Pie button that displays its command name.

        Extracted from ``PieMenu.add_commands`` (only entered when
        ``displayCommandName and shape == 'Pie'``). Mutates ``button``,
        ``buttonSize``, ``radius`` (CSS), ``icon``, ``angle``, ``X``, ``Y``,
        ``X_shortcut``, ``Y_shortcut``, ``maxTextLength`` and ``iconLabel``
        (created here); sets ``self.menu`` size. Returns the updated values.
        """
        # set minimum Y spacing at 1.2 * buttonSize
        if ecart < (1.2 * buttonSize):
            buttonSize = (ecart / 1.2)
            radius = radius_size(buttonSize)
            icon = icon_size(buttonSize)

        angle = (2 * math.pi) / (commandNumber)
        button.setIcon(QtGui.QIcon())
        # set padding and font size dependind on icon size
        font_size = round(icon/2)

        # get length of the string
        text_length = QFontMetrics(button.font()).horizontalAdvance(
            commands[commands.index(i)].text())

        button.setGeometry(
            buttonSize, 0,  2 * buttonSize + text_length, buttonSize)
        # layout for icon and command string
        layout = QtGui.QHBoxLayout(button)
        layout.setContentsMargins((icon/4), 0, 0, 0)

        iconButton = QtGui.QIcon(
            commands[commands.index(i)].icon())
        iconLabel = QtGui.QLabel()
        iconLabel.setObjectName("iconLabel")
        iconLabel.setPixmap(
            iconButton.pixmap(QtCore.QSize(icon, icon)))
        iconMarging = ""
        # right side
        if (num) <= (commandNumber/2):
            padding = "QToolButton#pieMenu {padding-left: " + str(
                icon) + "px; font-size: " + str(font_size) + "px;}"
            Y += ecart
            Y_shortcut = Y
            if Y > self.radius:
                Y = self.radius
                Y_shortcut = Y
            if num == 1:
                X = 0
                X_shortcut = 0
                Y_shortcut = Y + icon
            else:
                X = self.radius * \
                    (math.cos(angle * num + angleStart)) + \
                    (buttonSize + text_length/2)
                padding = "QToolButton#pieMenu {padding-left: " + str(
                    icon) + "px; font-size: " + str(font_size) + "px;}"
                X_shortcut = ((self.radius) * (math.cos(angle * num + angleStart)) + (
                    buttonSize + text_length/2)) - (text_length/2 + 1.8*icon)
                Y_shortcut = Y

        # handle bottom right for odd commandNumber
        elif (commandNumber % 2) == 1 and (num) == ((commandNumber+1)/2):
            X = self.radius * \
                (math.cos(angle * num + angleStart)) + \
                (buttonSize + text_length/2)
            Y = self.radius - ecart/2
            X_shortcut = (self.radius * (math.cos(angle * num + angleStart)) + (
                buttonSize + text_length/2)) - (text_length/2 + 1.8*icon)
            Y_shortcut = Y

        # handle bottom left for odd commandNumber
        elif (commandNumber % 2) == 1 and (num) == (((commandNumber+1)/2)+1):
            X = self.radius * \
                (math.cos(angle * num + angleStart)) - \
                (buttonSize + text_length/2)
            Y = self.radius - ecart/2
            layout.addStretch(1)
            padding = "QToolButton#pieMenu {padding-right: " + str(icon) \
                + "px; font-size: " + str(font_size) + "px;}"
            iconMarging = "#iconLabel {margin-right: " + \
                str(icon/4) + "px;}"
            X_shortcut = (self.radius * (math.cos(angle * num + angleStart)) - (
                buttonSize + text_length/2)) + (text_length/2 + 1.8*icon)
            Y_shortcut = Y

        # even commandNumber case, set the button on the middle bottom
        elif (commandNumber % 2) == 0 and (num) == ((commandNumber/2)+1):
            X = 0
            Y = self.radius
            X_shortcut = X
            Y_shortcut = Y - icon

        # left side
        else:
            Y -= ecart
            if Y < -self.radius:
                Y = -self.radius
            X = self.radius * \
                (math.cos(angle * num + angleStart)) - \
                (buttonSize + text_length/2)
            layout.addStretch(1)
            padding = "QToolButton#pieMenu {padding-right: " + str(icon) \
                + "px; font-size: " + str(font_size) + "px;}"
            iconMarging = "#iconLabel {margin-right: " + \
                str(icon/4) + "px;}"
            X_shortcut = (self.radius * (math.cos(angle * num + angleStart)) - (
                buttonSize + text_length/2)) + (text_length/2 + 1.8*icon)
            Y_shortcut = Y

        button.setProperty("ButtonX", X)
        button.setProperty("ButtonY", Y)

        buttonPreselect.setProperty("ButtonX", (self.radius - 1.2 * buttonSize) *
                                    (math.cos(angle * num + angleStart)))
        buttonPreselect.setProperty("ButtonY", (self.radius - 1.2 * buttonSize) *
                                    (math.sin(angle * num + angleStart)))

        iconLabel.setStyleSheet(
            styleCurrentTheme + iconMarging)
        button.setStyleSheet(
            styleCurrentTheme + radius + padding)
        layout.addWidget(iconLabel)

        # self.menu size Pie shape + command name 
        if text_length > maxTextLength:
            maxTextLength = text_length
        width =  valueRadius * 2 + buttonSize + 4 + 2 * maxTextLength + 3 * buttonSize
        height = valueRadius * 2 + buttonSize + 4
        self.menu.setFixedSize(width, height)
        return buttonSize, radius, icon, angle, X, Y, X_shortcut, Y_shortcut, maxTextLength, iconLabel


    def _build_pie_buttons(self, ctx):
        """Run the per-button layout loop for a Pie-shaped menu.

        Extracted from ``PieMenu.add_commands``. Reads and writes the shared
        layout state through ``ctx`` (a ``SimpleNamespace``). Mutates
        ``self.buttons`` and ``self.menu``.
        """
        commands = ctx.commands
        styleCurrentTheme = ctx.styleCurrentTheme
        shape = ctx.shape
        displayCommandName = ctx.displayCommandName
        displayPreselect = ctx.displayPreselect
        enableShortcut = ctx.enableShortcut
        displayShortcut = ctx.displayShortcut
        valueRadius = ctx.valueRadius
        buttonSize = ctx.buttonSize
        icon = ctx.icon
        radius = ctx.radius
        angle = ctx.angle
        angleStart = ctx.angleStart
        X = ctx.X
        Y = ctx.Y
        X_shortcut = ctx.X_shortcut
        Y_shortcut = ctx.Y_shortcut
        maxTextLength = ctx.maxTextLength
        iconLabel = ctx.iconLabel
        num = ctx.num
        ecart = ctx.ecart
        num_of_column = ctx.num_of_column
        icon_spacing = ctx.icon_spacing
        command_per_circle = ctx.command_per_circle
        number_of_circle = ctx.number_of_circle
        shortcutLabelSize = ctx.shortcutLabelSize
        shortcutCode = ctx.shortcutCode
        commandNumber = ctx.commandNumber

        for i in commands:
            """ show PieMenu in Edit Feature and in Sketcher """
            button, buttonPreselect = self._create_pie_button(commands, i, buttonSize, icon, radius, styleCurrentTheme)


            # modify style for display command name (only with Pie shape)
            if displayCommandName and shape == "Pie":
                buttonSize, radius, icon, angle, X, Y, X_shortcut, Y_shortcut, maxTextLength, iconLabel = self._layout_pie_with_names(button, buttonPreselect, commands, i, num, commandNumber, ecart, buttonSize, radius, icon, styleCurrentTheme, valueRadius, angle, angleStart, X, Y, X_shortcut, Y_shortcut, maxTextLength, iconLabel)

            elif shape == "TableTop":
                X_shortcut, Y_shortcut = self._layout_table_top(button, num, commandNumber, num_of_column, buttonSize, icon_spacing, icon, valueRadius)

            elif shape == "TableDown":
                X_shortcut, Y_shortcut = self._layout_table_down(button, num, commandNumber, num_of_column, buttonSize, icon_spacing, icon, valueRadius)

            elif shape == "TableLeft":
                X_shortcut, Y_shortcut = self._layout_table_left(button, num, commandNumber, num_of_column, buttonSize, icon_spacing, icon, valueRadius)

            elif shape == "TableRight":
                X_shortcut, Y_shortcut = self._layout_table_right(button, num, commandNumber, num_of_column, buttonSize, icon_spacing, icon, valueRadius)

            elif shape == "UpDown":
                num_of_column, X_shortcut, Y_shortcut = self._layout_updown(button, commandNumber, num, num_of_column, buttonSize, icon_spacing, icon, valueRadius)

            elif shape == "Concentric":
                num, angle, angleStart, command_per_circle, number_of_circle, X_shortcut, Y_shortcut = self._layout_concentric(button, num, angle, angleStart, command_per_circle, number_of_circle, buttonSize, icon_spacing, icon)

            elif shape == "Star":
                X_shortcut, Y_shortcut = self._layout_star(button, num, angle, angleStart, command_per_circle, buttonSize, icon_spacing, icon)

            elif shape == "LeftRight":
                num_of_column, maxTextLength, X_shortcut, Y_shortcut, iconLabel = self._layout_leftright(button, commands, i, num, commandNumber, num_of_column, buttonSize, icon_spacing, icon, valueRadius, styleCurrentTheme, radius, maxTextLength, displayCommandName, iconLabel)

            else:
                X_shortcut, Y_shortcut = self._layout_pie_simple(button, buttonPreselect, num, angle, angleStart, buttonSize, icon, valueRadius)

            if displayPreselect:
                self._setup_preselect_button(button, buttonPreselect, commands, i, angle, num, angleStart, buttonSize, icon, styleCurrentTheme)

            self.buttons.append(button)

            #### Manage Separator ###
            if (commands[commands.index(i)].text()) == translate('PieMenuTab', 'Separator'):
                self._handle_separator(button, buttonPreselect, iconLabel, icon)
            else:
                if enableShortcut:
                    shortcutCode = self._create_shortcut_label(commands, i, shortcutLabelSize, styleCurrentTheme, icon, X_shortcut, Y_shortcut, shortcutCode, displayShortcut)
            num = num + 1

        ctx.buttonSize = buttonSize
        ctx.icon = icon
        ctx.radius = radius
        ctx.angle = angle
        ctx.X = X
        ctx.Y = Y
        ctx.X_shortcut = X_shortcut
        ctx.Y_shortcut = Y_shortcut
        ctx.maxTextLength = maxTextLength
        ctx.iconLabel = iconLabel
        ctx.num = num
        ctx.num_of_column = num_of_column
        ctx.command_per_circle = command_per_circle
        ctx.number_of_circle = number_of_circle
        ctx.shortcutCode = shortcutCode


    def hide(self):
        for i in self.buttons:
            i.hide()
        self.menu.hide()

    def showAtMouseInstance(self, keyValue=None):
        enableContext = config.get_params()["main"].GetBool(constants.PARAM_ENABLE_CONTEXT)

        if state.app_state.context_phase:
            if not keyValue:
                sel = Gui.Selection.getSelectionEx()
                if not sel:
                    self.hide()
                    state.app_state.context_phase = False
                    update_commands()
                elif not enableContext:
                    self.hide()
                    update_commands()
                else:
                    keyValue = get_param(constants.PARAM_CONTEXT_PIE)
                    update_commands(keyValue, context=True)
            else:
                update_commands(keyValue)
        else:
            update_commands(keyValue)

        height = self.menu.height()
        width = self.menu.width()
        posX = width / 2
        posY = height / 2

        if state.app_state.window_shadow:
            pos = self.mw.mapFromGlobal(QtGui.QCursor.pos())
            cursor_pos = QtGui.QCursor.pos()
            self.menu.move(cursor_pos.x() - self.menu.width() // 2,
                           cursor_pos.y() - self.menu.height() // 2)

            self.menu.show()
            for i in self.buttons:
                i.move(i.property("ButtonX") + posX - i.width() / 2 + self.offset_x,
                       i.property("ButtonY") + posY - i.height() / 2 + self.offset_y)
                i.setVisible(True)
                i.setParent(self.menu)
                i.repaint()
        else:
            #### a vérifier ####
            pos = QtGui.QCursor.pos()
            x = int(pos.x() - self.menuSize / 2)
            y = int(pos.y() - self.menuSize / 2)
            self.menu.show()

            for i in self.buttons:
                i.move(int(i.property("ButtonX") + (self.menuSize - i.size().width()) / 2 + self.offset_x),
                       int(i.property("ButtonY") + (self.menuSize - i.size().height()) / 2 + self.offset_y))
                i.setVisible(True)


    def showPiemenuPreview(self, keyValue=None):
        """ Preview of PieMenu in widgetTable on Preferences Tab """
        # get BackgroundColor value in parameters, if 0 then we have a fresh install
        backgroundColorConfig = config.get_params()["color"].GetUnsigned(
            "BackgroundColor")
        cssColorTop = get_css_color(config.get_params()["color"], "BackgroundColor2")
        cssColorBottom = get_css_color(config.get_params()["color"], "BackgroundColor3")
        gradient = True
        useBackgroundColorMid = False

        if backgroundColorConfig != 0:
            gradient = config.get_params()["color"].GetBool("Gradient")
            radialGradient = config.get_params()["color"].GetBool("RadialGradient")
            useBackgroundColorMid = config.get_params()["color"].GetBool(
                "UseBackgroundColorMid")
            cssColorSimple = get_css_color(config.get_params()["color"], "BackgroundColor")
            cssColorMiddle = get_css_color(config.get_params()["color"], "BackgroundColor4")

        if gradient:
            if useBackgroundColorMid:
                show_preview_widget.setStyleSheet(
                    f"background-color: qlineargradient(y1: 0, y2: 1, stop: 0 {cssColorTop}, stop: 0.5 {cssColorMiddle}, stop: 1 {cssColorBottom});")
            else:
                show_preview_widget.setStyleSheet(
                    f"background-color: qlineargradient(y1: 0, y2: 1, stop: 0 {cssColorTop}, stop: 1 {cssColorBottom})")

        elif radialGradient:
            if useBackgroundColorMid:
                show_preview_widget.setStyleSheet(
                    f"background-color: qradialgradient(cx: 0.5, cy: 0.5, radius: 0.5, fx: 0.5, fy: 0.5, stop: 0 {cssColorTop}, stop: 0.5 {cssColorMiddle}, stop: 1 {cssColorBottom});")
            else:
                show_preview_widget.setStyleSheet(
                    f"background-color: qradialgradient(cx: 0.5, cy: 0.5, radius: 0.5, fx: 0.5, fy: 0.5, stop: 0 {cssColorTop}, stop: 1 {cssColorBottom});")
        else:
            # color simple :
            show_preview_widget.setStyleSheet(
                f"background-color: {cssColorSimple};")

        shape = get_parameter_group(c_box.currentText(), "String", constants.PARAM_SHAPE)

        # positions of PieMenu in widget
        height = show_piemenu.height()
        width = show_piemenu.width()
        posX = width / 2
        posY = height / 2

        if shape == "TableLeft":
            posX = width * 4 / 5

        if shape == "TableRight":
            posX = width / 5

        update_commands(keyValue)

        if state.app_state.window_shadow:
            # needed for tools shortcut
            # To avoid flickering in PieMenuDialog window
            if pie_menu_dialog.isVisible():
                self.menu.setParent(pie_menu_dialog)
                self.menu.show()
                self.menu.hide()
                self.menu.setParent(None)

            for i in self.buttons:
                i.move(i.property("ButtonX") + posX - i.width() / 2 + self.offset_x,
                       i.property("ButtonY") + posY - i.height() / 2 + self.offset_y)
                i.setVisible(True)
                i.setAttribute(Qt.WA_Disabled, True)
                i.setParent(show_piemenu)
                # disable quickMenu and (central) 
                if i.objectName() == "styleButtonMenu" or i.objectName() == "styleMenuClose":
                    i.setEnabled(False)

        else:
            for i in self.buttons:
                i.move(i.property("ButtonX")
                       + (self.menuSize - i.size().width()) /
                       2 + self.offset_x,
                       i.property("ButtonY")
                       + (self.menuSize - i.size().height()) / 2 + self.offset_y)
                i.setVisible(True)
                i.setAttribute(Qt.WA_Disabled, True)
                i.setParent(show_piemenu)

                # disable quickMenu and (central) 
                if i.objectName() == "styleButtonMenu" or i.objectName() == "styleMenuClose":
                    i.setEnabled(False)


    def spin_interactif(self):
        """ Handle spinbox in fast edit mode """
        docName = App.ActiveDocument.Name
        g = Gui.ActiveDocument.getInEdit()
        fonctionActive = g.Object
        featureName = g.Object.Name
        size = self.double_spinbox.property('value')

        # These checkboxes only exist for some PartDesign features,
        # so a missing attribute here is expected: keep the default value.
        featureThroughAll = 0
        featureReversed = 0
        featureSymToPlane = 0
        try:
            featureThroughAll = self.checkbox_throughAll.isChecked()
        except Exception:
            None
        try:
            featureReversed = self.checkbox_reversed.isChecked()
        except Exception:
            None
        try:
            featureSymToPlane = self.checkbox_midPlane.isChecked()
        except Exception:
            None

        obj = App.getDocument(docName).getObject(featureName)

        # Write the feature's main value (Fillet->Radius, Chamfer->Size, ...).
        # Pocket in "through all" mode has no Length to write.
        attr = constants.SPINBOX_SIZE_ATTR.get(str(fonctionActive))
        is_pocket = (str(fonctionActive) == '<PartDesign::Pocket>')
        if attr is not None and not (is_pocket and featureThroughAll):
            setattr(obj, attr, size)

        # MidPlane / Reversed apply to Pad, Pocket, Revolution and Groove.
        if str(fonctionActive) in constants.SPINBOX_MIDPLANE_FEATURES:
            obj.Reversed = 1 if featureReversed else 0
            fc_version = App.Version()[0:3]
            major = int(fc_version[0])
            minor = int(fc_version[1])
            patch = int(fc_version[2])

            if featureSymToPlane:
                if (major, minor, patch) <= (1, 0, 2):
                    obj.Midplane = 1
                else:
                    obj.SideType = 2
            else:
                if (major, minor, patch) <= (1, 0, 2):
                    obj.Midplane = 0
                else:
                    obj.SideType = 0

        # ThroughAll handling is specific to Pocket.
        if is_pocket:
            if featureThroughAll:
                self.double_spinbox.setEnabled(False)
                obj.Type = 1
            else:
                self.double_spinbox.setEnabled(True)
                obj.Type = 0

        # Hole and unknown features have no spinbox value: hide it.
        if attr is None:
            self.double_spinbox.setVisible(False)

        App.ActiveDocument.recompute()
