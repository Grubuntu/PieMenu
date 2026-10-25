"""Generic UI helpers for the PieMenu preferences dialog.

Miscellaneous helpers that do not belong to a specific tab: the dimension and
style helpers of the pie buttons (`radius_size()`, `icon_size()`,
`close_button()`), the accessories-menu entry (`add_accessories_menu()`,
`accessories_menu()`), the workbench reload and selection helpers
(`reload_workbench()`, `get_wb_already_set()`, `set_wb_for_pie_menu()`,
`on_context_workbench()`), the about box (`info_popup()`), the documentation
link (`documentation_link()`), the shortcut-update wrappers
(`update_shortcut_key()`, `update_global_shortcut_key()`,
`compare_and_display_warning()`) and `on_display_spin_box()`.

The widgets and callbacks below are created by `pieMenuStart()` after this
module is imported, so they are declared as module attributes here and
published by `pieMenuStart()` through `publish()`.
"""

import math

import FreeCAD as App
import FreeCADGui as Gui
from PySide import QtCore, QtGui

from piemenu import config, constants, log, shortcuts
from piemenu.config import get_index_list, get_parameter_group
from piemenu.theme import get_style
from piemenu.workbench import get_list_workbenches


def translate(context, text):
    """Translate a string with the FreeCAD Qt translator."""
    return App.Qt.translate(context, text)


# Widgets and callbacks created by `pieMenuStart()` and injected via `publish()`.
c_box = None
combo_context_workbench = None
combo_wb_for_pie_menu = None
get_group = None
global_shortcut_line_edit = None
info_shortcut = None
label_global_shortcut = None
label_shortcut = None
mw = None
on_control = None
pie_menu_dialog = None
pie_menu_instance = None
pie_menu_version = None
shortcut_line_edit = None
timer = None
wizard_timer = None
update_piemenu_preview = None


def publish(**references):
    """Publish the runtime references used by the generic UI helpers."""
    globals().update(references)


def compare_and_display_warning(shortcutsAssigned, currentShortcut):
    return shortcuts.compare_and_display_warning(
        info_shortcut, shortcutsAssigned, currentShortcut)


def update_shortcut_key(newShortcut):
    return shortcuts.update_shortcut_key(
        newShortcut, c_box, label_shortcut, shortcut_line_edit)


def update_global_shortcut_key(newShortcut):
    """Validate and store the global shortcut."""
    return shortcuts.update_global_shortcut_key(
        newShortcut, label_global_shortcut, global_shortcut_line_edit)


def add_accessories_menu():
    """Add the PieMenu entry to the global toolbar (idempotent)."""
    if mw.property("eventLoop"):
        startAM = False
        try:
            mw.mainWindowClosed
            mw.workbenchActivated
            startAM = True
        except AttributeError:
            pass
        if startAM:
            timer.stop()
            timer.deleteLater()
            accessories_menu()


def accessories_menu():
    """Add pie menu preferences to accessories menu."""
    pref = QtGui.QAction(mw)
    pref.setText(translate("AccesoriesMenu", "Pie menu settings"))
    pref.setObjectName("PieMenu")
    pref.triggered.connect(on_control)

    try:
        import AccessoriesMenu
        AccessoriesMenu.addItem("PieMenu")
    except ImportError:
        a = mw.findChild(QtGui.QAction, "AccessoriesMenu")
        if a:
            a.menu().addAction(pref)
        else:
            mb = mw.menuBar()
            action = QtGui.QAction(mw)
            action.setObjectName("AccessoriesMenu")
            action.setIconText(translate("FreeCAD Menu", "Accessories"))
            menu = QtGui.QMenu()
            action.setMenu(menu)
            menu.addAction(pref)

            def addMenu():
                """Add accessories menu to the menu bar."""
                mb.addAction(action)
                action.setVisible(True)

            addMenu()
            mw.workbenchActivated.connect(addMenu)


def reload_workbench():
    try:
        wb = Gui.activeWorkbench()
        # needed to change WB and reload it : do only Gui.reloadWorkbench() is not enough
        Gui.activateWorkbench('PartDesignWorkbench')
        Gui.activateWorkbench('PartWorkbench')
        Gui.activateWorkbench(wb.name())
        Gui.updateGui()
    except Exception as exc:
        log.log_error("cannot reload active workbench", exc)


def radius_size(buttonSize):
    """Calculates border radius for QToolButton based on the given buttonSize."""
    radius = str(math.trunc(buttonSize / 2))
    return "QToolButton {border-radius: " + radius + "px}"


def icon_size(buttonSize):
    """Calculates the size of an icon based on the given buttonSize."""
    icon = buttonSize / 3 * 2
    return icon


def close_button(buttonSize=32):
    """Style the close button."""
    icon = icon_size(buttonSize)
    radius = radius_size(buttonSize)
    button = QtGui.QToolButton()
    button.setObjectName("styleMenuClose")
    button.setProperty("ButtonX", 0)  # +, right
    button.setProperty("ButtonY", 0)  # +, down
    button.setGeometry(0, 0, buttonSize, buttonSize)
    button.setIconSize(QtCore.QSize(icon, icon))
    styleCurrentTheme = get_style()
    button.setStyleSheet(styleCurrentTheme + radius)
    button.setAttribute(QtCore.Qt.WA_TranslucentBackground)

    def onButton():
        pie_menu_instance.hide()

    button.clicked.connect(onButton)

    return button


def info_popup():
    msg = """
        <h2>Pie menu</h2>
        <p style='font-weight:normal;font-style:italic;'>version """ + pie_menu_version + """</p>
        <p style='font-weight:normal;'>This macro adds pie menu to FreeCAD GUI</p>
        <hr>
        <h2>Licence</h2>
        <p style='font-weight:normal;'>Copyright (C) 2024 Grubuntu, Pgilfernandez, Hasecilu @ FreeCAD</p>
        <p style='font-weight:normal;'>Copyright (C) 2022, 2023 mdkus @ FreeCAD</p>
        <p style='font-weight:normal;'>Copyright (C) 2016, 2017 triplus @ FreeCAD</p>
        <p style='font-weight:normal;'>Copyright (C) 2015,2016 looo @ FreeCAD</p>
        <p style='font-weight:normal;'>Copyright (C) 2015 microelly <microelly2@freecadbuch.de></p>
        <p style='font-weight:normal;'>This library is free software; you can redistribute it and/or modify it under the terms of the GNU Lesser General Public License as published by the Free Software Foundation; either version 2.1 of the License, or (at your option) any later version.</p>
        <p style='font-weight:normal;'>This library is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more details.</p>
        <p style='font-weight:normal;'>You should have received a copy of the GNU Lesser General Public License along with this library; if not, write to the Free Software Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301 USA</p>
    """
    QtGui.QMessageBox.question(None, "Help", msg, QtGui.QMessageBox.Ok)


def documentation_link():
    """Open PieMenu documentation using the Help settings."""
    from Help import show
    pie_menu_dialog.close()
    # Open a wiki page
    show("PieMenu Workbench")


def get_wb_already_set():
    """ Check if a workbench is already set for a PieMenu """
    indexList = get_index_list()
    wbAlreadySet = []
    for i in indexList:
        group = config.get_params()["index"].GetGroup(str(i))
        defWb = group.GetString(constants.PARAM_DEFAULT_WORKBENCH)
        if defWb != 'None':
            wbAlreadySet.append(defWb)

    return wbAlreadySet


def set_wb_for_pie_menu():
    """ Set workbench to a dedicate PieMenu """
    combo_wb_for_pie_menu.blockSignals(True)
    wbList = get_list_workbenches()
    wbAlreadySet = get_wb_already_set()

    for item in wbList[:]:
        if item in wbAlreadySet:
            wbList.remove(item)
            wbAlreadySet.remove(item)

    group = get_group(mode=0)
    defWorkbench = group.GetString(constants.PARAM_DEFAULT_WORKBENCH)
    wbList.append(defWorkbench)
    if 'None' not in wbList:
        wbList.insert(0, 'None')

    combo_wb_for_pie_menu.clear()
    combo_wb_for_pie_menu.addItems(wbList)
    index = combo_wb_for_pie_menu.findText(defWorkbench)
    if index != -1:
        combo_wb_for_pie_menu.setCurrentIndex(index)
    combo_wb_for_pie_menu.blockSignals(False)


def on_context_workbench():
    """ Handle when a workbench is set to a PieMenu in context tab """
    combo_context_workbench.blockSignals(True)
    wbList = get_list_workbenches()

    contextWorkbench = get_parameter_group(
        c_box.currentText(), "String", constants.PARAM_CONTEXT_WORKBENCH)
    wbList.append(contextWorkbench)
    if "None" in wbList:
        wbList.remove("None")

    if translate('ContextTab', 'None (Disable)') not in wbList:
        wbList.insert(0, translate('ContextTab', 'None (Disable)'))

    if translate('ContextTab', 'All Workbenches') not in wbList:
        wbList.insert(0,  translate('ContextTab', 'All Workbenches'))

    notDuplicate = []
    for i in wbList:
        if i not in notDuplicate:
            notDuplicate.append(i)

    combo_context_workbench.clear()
    combo_context_workbench.addItems(notDuplicate)
    index = combo_context_workbench.findText(contextWorkbench)
    if index != -1:
        combo_context_workbench.setCurrentIndex(index)
    combo_context_workbench.blockSignals(False)


def on_display_spin_box(state):
    """ Set parameter to show or not fast SpinBox """
    if state == 2 or state == 1:
        config.get_params()["main"].SetBool(constants.PARAM_DISPLAY_SPIN_BOX, True)
    else:
        config.get_params()["main"].SetBool(constants.PARAM_DISPLAY_SPIN_BOX, False)
    update_piemenu_preview()
