"""PieMenu settings handlers for the preferences dialog.

These callbacks react to the widgets of the PieMenu settings tab (theme, shape,
sizes, trigger options, default and context workbench) and write the values
back to the PieMenu parameters.

The widgets and callbacks below are created by `pieMenuStart()` after this
module is imported, so they are declared as module attributes here and
published by `pieMenuStart()` through `publish()`.
"""

import FreeCAD as App
import FreeCADGui as Gui
from PySide import QtGui

from piemenu import config, constants, log, resources, state
from piemenu.config import get_index_list, get_param_index, get_parameter_group
from piemenu.ui.icons import get_icon_pie_menu
from piemenu.workbench import extract_workbench, resolve_workbench_name


def translate(context, text):
    """Translate a string with the FreeCAD Qt translator."""
    return App.Qt.translate(context, text)


# Widgets and callbacks created by `pieMenuStart()` and injected via `publish()`.
action_key = None
c_box = None
checkbox_global_key_toggle = None
combo_box_theme = None
combo_context_workbench = None
combo_shape = None
combo_wb_for_pie_menu = None
get_group = None
on_shape = None
pie_menu_dialog = None
spin_button = None
spin_command_per_circle = None
spin_delay_right_click = None
spin_hover_delay = None
spin_icon_spacing = None
spin_num_column = None
spin_radius = None
spin_shortcut_label_size = None
update_piemenu_preview = None


def publish(**references):
    """Publish the runtime references used by the settings handlers."""
    globals().update(references)


def set_global_key_toggle():
    """ Set globlal key toggle mode in parameters """
    globalKeyToggle = checkbox_global_key_toggle.isChecked()
    config.get_params()["main"].SetBool(constants.PARAM_GLOBAL_KEY_TOGGLE, globalKeyToggle)
    action_key.setEnabled(True)

def update_icons_pie_menus():
    """ Update PieMenu icon after change it """
    indexList = get_index_list()
    lastWorkbench = Gui.activeWorkbench()
    workbenches = Gui.listWorkbenches()

    for i in indexList:
        pie = get_param_index(str(i))
        iconPath = get_parameter_group(pie, "String", constants.PARAM_ICON_PATH)
        if iconPath == "":
            iconPath = resources.iconPieMenuLogo
        icon = get_icon_pie_menu(iconPath)
        namePie = 'PieMenu_' + pie

        try:
            # iconPath is either a command name ("Part_Fillet") or a file path
            workbench = extract_workbench(iconPath)
            wbName = resolve_workbench_name(workbench)
            if wbName in workbenches and wbName not in state.app_state.loaded_workbenches:
                message = translate(
                    "MainWindow",
                    "PieMenu needs to load {} to access icon resources. To avoid this message, please consider enabling auto-load for this workbench in FreeCAD's settings.",
                ).format(wbName)
                QtGui.QMessageBox.information(
                    None,
                    translate("MainWindow", "Workbench Loading"),
                    message,
                    QtGui.QMessageBox.Ok,
                )

                Gui.activateWorkbench(wbName)
                state.app_state.loaded_workbenches.append(wbName)
                Gui.activateWorkbench(lastWorkbench.__class__.__name__)
        except Exception as exc:
            log.log_warning_once(
                "icons:" + namePie,
                "cannot load workbench to refresh icons of %s" % namePie, exc)

        all_actions = Gui.getMainWindow().findChildren(QtGui.QAction)

        for action in all_actions:
            if action.data() == iconPath:
                icon = action.icon()
        for action in all_actions:
            if action.data() == namePie:
                action.setIcon(QtGui.QIcon(icon))

def set_theme():
    """Apply the selected theme and refresh the preview when the dialog is visible."""
    combo_box_theme.blockSignals(True)
    theme = combo_box_theme.currentText()
    config.get_params()["main"].SetString(constants.PARAM_THEME, theme)
    combo_box_theme.blockSignals(False)
    try:
        # the pie menu preview may not exist yet: skip the refresh in that case
        if pie_menu_dialog.isVisible():
            update_piemenu_preview()
    except Exception:
        None

def on_wb_for_pie_menu():
    """ Set Default Workbench in parameters """
    group = get_group()
    defWorkbench = combo_wb_for_pie_menu.currentText()
    group.SetString(constants.PARAM_DEFAULT_WORKBENCH, defWorkbench)

def set_context_workbench():
    """ Set Context Workbench in parameters """
    group = get_group()
    contextWorkbench = combo_context_workbench.currentText()
    group.SetString(constants.PARAM_CONTEXT_WORKBENCH, contextWorkbench)

def on_spin_shortcut_label_size():
    """ Set shortcut label size """
    group = get_group()
    value = spin_shortcut_label_size.value()
    group.SetInt(constants.PARAM_SHORTCUT_LABEL_SIZE, value)
    try:
        # the pie menu preview may not exist yet: skip the refresh in that case
        if pie_menu_dialog.isVisible():
            update_piemenu_preview()
    except Exception:
        None

def set_shape():
    """ Set shape of the PieMenu """
    group = get_group(mode=0)
    combo_shape.blockSignals(True)
    shape = combo_shape.currentText()
    group.SetString(constants.PARAM_SHAPE, shape)
    combo_shape.blockSignals(False)
    on_shape(shape)
    try:
        # the pie menu preview may not exist yet: skip the refresh in that case
        if pie_menu_dialog.isVisible():
            update_piemenu_preview()
    except Exception:
        None

def on_num_column():
    """ Set NUmber of column """
    group = get_group()
    value = spin_num_column.value()
    group.SetInt(constants.PARAM_NUM_COLUMN, value)
    update_piemenu_preview()

def on_icon_spacing():
    """ Set Icon spacing """
    group = get_group()
    value = spin_icon_spacing.value()
    group.SetInt(constants.PARAM_ICON_SPACING, value)
    update_piemenu_preview()

def on_command_per_circle():
    """ Set number of command per circle """
    group = get_group()
    value = spin_command_per_circle.value()
    group.SetInt(constants.PARAM_COMMAND_PER_CIRCLE, value)
    update_piemenu_preview()

def on_spin_hover_delay():
    """ Set TriggerMode in parameter """
    value = spin_hover_delay.value()
    indexList = get_index_list()
    for i in indexList:
        pieName = get_param_index(str(i))
        if pieName == c_box.currentText():
            param = config.get_params()["index"].GetGroup(str(i))
            param.SetInt(constants.PARAM_HOVER_DELAY, value)

def on_spin_radius():
    """ Set radius """
    group = get_group()
    value = spin_radius.value()
    group.SetInt(constants.PARAM_RADIUS, value)
    update_piemenu_preview()

def on_spin_button():
    """ Set button size """
    group = get_group()
    value = spin_button.value()
    group.SetInt(constants.PARAM_BUTTON, value)
    update_piemenu_preview()

def on_spin_delay_right_click():
    """ Set delay for right click to trigger """
    value = spin_delay_right_click.value()
    config.get_params()["main"].SetInt(constants.PARAM_DELAY_RIGHT_CLICK, value)

