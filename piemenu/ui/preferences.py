"""Preferences dialog for the PieMenu settings window.

`PieMenuDialog` is the modal window itself; it saves the parameters and returns
to the general settings when it is closed. `get_group()`, `get_shape()` and
`get_theme()` read the values stored in the parameters, `c_box_update()` and
`on_pie_change()` refresh the whole window when the selected PieMenu changes,
`on_shape()` toggles the visibility of the shape-dependent widgets,
`update_piemenu_preview()` refreshes the preview and `on_control()` /
`on_back_to_settings()` open and leave the dialog.

The widgets and callbacks below are created by `pieMenuStart()` after this
module is imported, so they are declared as module attributes here and
published by `pieMenuStart()` through `publish()`.
"""

import os

import FreeCAD as App
import FreeCADGui as Gui
from PySide import QtGui
from PySide.QtWidgets import QDialog

from piemenu import config, constants, defaults, resources, shortcuts, state
from piemenu.config import get_index_list, get_param, get_param_index, get_parameter_global, get_parameter_group
from piemenu.context import add_observer, context_list
from piemenu.ui import context as context_ui
from piemenu.ui import icons as icons_ui
from piemenu.ui import misc as misc_ui
from piemenu.ui import options as options_ui
from piemenu.ui import settings as settings_ui
from piemenu.ui import tool_list as tool_list_ui
from piemenu.workbench import get_pie_name


def translate(context, text):
    """Translate a string with the FreeCAD Qt translator."""
    return App.Qt.translate(context, text)


# Widgets and callbacks created by `pieMenuStart()` and injected via `publish()`.
button_back_to_settings = None
button_existing_tool_bar = None
button_icon_pie_menu = None
button_list_widget = None
buttons_layout = None
c_box = None
checkbox_default_pie = None
checkbox_display_command_name = None
checkbox_display_preselect = None
checkbox_display_shortcut = None
checkbox_display_spin_box = None
checkbox_global_key_toggle = None
checkbox_trigger_context = None
combo_box_theme = None
combo_shape = None
icon_default = None
info_shortcut = None
label_command_per_circle = None
label_display_preselect = None
label_global_shortcut = None
label_icon_spacing = None
label_num_column = None
label_shortcut = None
label_shortcut_size = None
labeldisplay_command_name = None
mw = None
pie_menu_dialog = None
pie_menu_instance = None
pie_menu_version = None
piemenu_box_group = None
radio_button_hover = None
radio_button_press = None
shortcut_line_edit = None
show_piemenu = None
spin_button = None
spin_command_per_circle = None
spin_hover_delay = None
spin_icon_spacing = None
spin_num_column = None
spin_radius = None
spin_shortcut_label_size = None
tabs = None
tool_bar_tab = None
tool_shortcut_group = None
update_commands = None
v_splitter = None
# Called when the dialog leaves the ToolBars view, so that the assistant
# panel shows the guide of the view that becomes visible again.
on_assistant_refresh = None


def publish(**references):
    """Publish the runtime references used by the preferences handlers."""
    globals().update(references)


class PieMenuDialog(QDialog):
    """ Class to handle PieMenuDialog events """

    def __init__(self, parent=None):
        """Build the preferences dialog (title from the version constant)."""
        super(PieMenuDialog, self).__init__(parent)

        self.setObjectName("PieMenuPreferences")
        self.setWindowTitle("PieMenu " + pie_menu_version)
        self.closeEvent = self.custom_close_event
        self.setWindowIcon(QtGui.QIcon(resources.iconPieMenuLogo))
        self.setMinimumSize(1000, 680)
        self.setModal(True)

    def custom_close_event(self, event):
        """Save parameters and return to settings when the dialog is closed."""
        # Caught close event to save parameters on disk
        App.saveParameter()
        on_back_to_settings()
        icons_ui.window_icons.close()
        super(PieMenuDialog, self).closeEvent(event)


def get_group(mode=0):
    """
    Obtain the parameter group.
    When:
    mode = 0: read from comboBox at GUI
    mode = 1: read from CurrentPie parameter
    mode = 2: read from ContextPie parameter
    If it doesn't exists return default PieMenu group
    """

    if mode == 2:
        text = get_param(constants.PARAM_CONTEXT_PIE)
    elif mode == 1:
        text = get_param(constants.PARAM_CURRENT_PIE)
    else:
        text = c_box.currentText()
    group = None

    # Iterate over the available groups on indexList
    # to find the group stored on `text` var
    indexList = get_index_list()
    for i in indexList:
        pie = get_param_index(str(i))
        if pie == text:
            group = config.get_params()["index"].GetGroup(str(i))
        else:
            pass
    if group:
        # group was found, good
        pass
    else:
        # return the default PieMenu group
        if 0 in indexList:
            group = config.get_params()["index"].GetGroup("0")
        elif state.app_state.wizard_running:
            # wizard is creating the first pie: don't auto-create defaults
            group = None
        else:
            defaults.set_default_pie()
            try:
                update_commands()
            except Exception as exc:
                from piemenu import log
                log.log_error("get_group: update_commands failed", exc)
            group = config.get_params()["index"].GetGroup("0")

    return group

def get_theme():
    """ list all QSS files themes available """
    all_files = os.listdir(resources.stylepath)
    qss_files = [file for file in all_files if file.endswith(".qss")]
    available_styles = [file[:-4] for file in qss_files]
    combo_box_theme.blockSignals(True)
    combo_box_theme.clear()
    combo_box_theme.addItems(available_styles)

    theme = config.get_params()["main"].GetString(constants.PARAM_THEME)
    index = combo_box_theme.findText(theme)
    if index != -1:
        combo_box_theme.setCurrentIndex(index)
    combo_box_theme.blockSignals(False)

def c_box_update(index=None):
    """Rebuild the PieMenu combo list, ordered with the current PieMenu first."""
    currentPie = get_param(constants.PARAM_CURRENT_PIE)

    pieList = []
    indexList = get_index_list()
    for i in indexList:
        try:
            pieList.append(config.get_params()["index"].GetString(str(i)))
        except AttributeError:
            pieList.append(config.get_params()["index"].GetString(str(i)))
    duplicates = []
    for i in pieList:
        if i == currentPie:
            pass
        else:
            duplicates.append(i)
    duplicates.append(currentPie)

    pieList = sorted(duplicates)
    pieList.reverse()

    c_box.blockSignals(True)
    c_box.clear()

    for i in pieList:
        c_box.insertItem(0, i)
    c_box.blockSignals(False)

    if index is None:
        index = 0
    else:
        index = c_box.findText(index)

    c_box.setCurrentIndex(index)
    on_pie_change()
def on_pie_change():
    """ Update values for all settings """
    state.app_state.sub_group_selected = None
    context_ui.on_reset_context_table()
    tool_list_ui.button_list()
    tool_list_ui.tool_list()
    context_ui.set_context_conditions()
    shortcuts.get_shortcut_list()

    iconPath = get_parameter_group(c_box.currentText(), "String", constants.PARAM_ICON_PATH)
    defaultPie = get_parameter_global("String", constants.PARAM_CURRENT_PIE)
    index = c_box.findText(defaultPie)
    shape = get_shape(c_box.currentText())
    radiusSize = get_parameter_group(c_box.currentText(), "Int", constants.PARAM_RADIUS)
    buttonSize = get_parameter_group(c_box.currentText(), "Int", constants.PARAM_BUTTON)
    numColumn = get_parameter_group(c_box.currentText(), "Int", constants.PARAM_NUM_COLUMN)
    iconSpacing = get_parameter_group(
        c_box.currentText(), "Int", constants.PARAM_ICON_SPACING)
    commandPerCircle = get_parameter_group(
        c_box.currentText(), "Int", constants.PARAM_COMMAND_PER_CIRCLE)
    displayCommandName = get_parameter_group(
        c_box.currentText(), "Bool", constants.PARAM_DISPLAY_COMMAND)
    displayPreselect = get_parameter_group(
        c_box.currentText(), "Bool", constants.PARAM_DISPLAY_PRESELECT)
    triggerMode = get_parameter_group(
        c_box.currentText(), "String", constants.PARAM_TRIGGER_MODE)
    triggerContext = get_parameter_group(
        c_box.currentText(), "Bool", "ImmediateTriggerContext")
    hoverDelay = get_parameter_group(c_box.currentText(), "Int", constants.PARAM_HOVER_DELAY)
    enableShortcut = get_parameter_group(
        c_box.currentText(), "Bool", constants.PARAM_ENABLE_SHORTCUT)
    displayShortcut = get_parameter_group(
        c_box.currentText(), "Bool", constants.PARAM_DISPLAY_SHORTCUT)
    shortcutLabelSize = get_parameter_group(
        c_box.currentText(), "Int", constants.PARAM_SHORTCUT_LABEL_SIZE)
    shortcutKey = get_parameter_group(
        c_box.currentText(), "String", constants.PARAM_SHORTCUT_KEY)
    globalKeyToggle = get_parameter_global("Bool", constants.PARAM_GLOBAL_KEY_TOGGLE)
    displaySpinBox = get_parameter_global("Bool", constants.PARAM_DISPLAY_SPIN_BOX)

    icon = icons_ui.get_icon_pie_menu(iconPath)
    button_icon_pie_menu.setIcon(QtGui.QIcon(icon))

    checkbox_default_pie.blockSignals(True)
    if defaultPie == c_box.currentText():
        checkbox_default_pie.setChecked(True)
    else:
        checkbox_default_pie.setChecked(False)
    checkbox_default_pie.blockSignals(False)

    c_box.setItemIcon(index, icon_default)

    misc_ui.on_context_workbench()
    misc_ui.set_wb_for_pie_menu()
    on_shape(shape)
    spin_radius.setValue(radiusSize)
    spin_button.setValue(buttonSize)
    spin_num_column.setValue(numColumn)
    spin_icon_spacing.setValue(iconSpacing)
    spin_command_per_circle.setValue(commandPerCircle)
    checkbox_display_command_name.blockSignals(True)
    checkbox_display_command_name.setChecked(displayCommandName)
    checkbox_display_command_name.blockSignals(False)
    checkbox_display_preselect.blockSignals(True)
    checkbox_display_preselect.setChecked(displayPreselect)
    checkbox_display_preselect.blockSignals(False)
    checkbox_display_spin_box.blockSignals(True)
    checkbox_display_spin_box.setChecked(displaySpinBox)
    checkbox_display_spin_box.blockSignals(False)
    options_ui.set_trigger_mode(triggerMode)
    radio_button_press.setChecked(triggerMode == "Press")
    radio_button_hover.setChecked(triggerMode == "Hover")
    spin_hover_delay.setValue(hoverDelay)
    tool_shortcut_group.setChecked(enableShortcut)
    button_list_widget.setColumnHidden(0, not enableShortcut)
    checkbox_display_shortcut.setChecked(displayShortcut)
    spin_shortcut_label_size.setValue(shortcutLabelSize)
    shortcut_line_edit.setText(shortcutKey)
    label_shortcut.setText(
        translate("PieMenuTab", "Current shortcut: ") + shortcutKey)
    checkbox_trigger_context.setChecked(triggerContext)
    checkbox_global_key_toggle.setChecked(globalKeyToggle)
    info_shortcut.setText('')
    context_ui.update_context_conditions()

def on_default_pie(state):
    """ Set the selected PieMenu as default PieMenu """
    if state == 2:
        config.get_params()["main"].SetString(constants.PARAM_CURRENT_PIE, c_box.currentText())
    currentPie = config.get_params()["main"].GetString(constants.PARAM_CURRENT_PIE)
    index = c_box.findText(currentPie)
    c_box.setItemIcon(index, icon_default)
    c_box_update(c_box.currentText())
def update_piemenu_preview(key=None):
    """ Update the preview of PieMenu in preview Tab """
    try:
        show_piemenu.hide()
        if key == "toolBarTab":
            pie_menu_instance.showPiemenuPreview("toolBarTab")
        else:
            pie_menu_instance.showPiemenuPreview(keyValue=c_box.currentText())
        show_piemenu.show()
    except Exception as exc:
        from piemenu import log
        log.log_error("update_piemenu_preview failed", exc)

def on_shape(shape):
    """ Handle the visibilty of buttons/boxes depending of the shape """
    try:
        if pie_menu_dialog.isVisible():

            if shape in ["TableTop", "TableDown", "TableLeft", "TableRight"]:
                spin_num_column.setEnabled(True)
                label_num_column.setVisible(True)
                spin_num_column.setVisible(True)
            else:
                spin_num_column.setEnabled(False)
                label_num_column.setVisible(False)
                spin_num_column.setVisible(False)

            if shape in ["UpDown", "LeftRight", "TableTop", "TableDown", "TableLeft", "TableRight", "Concentric", "Star"]:
                label_icon_spacing.setVisible(True)
                spin_icon_spacing.setEnabled(True)
                spin_icon_spacing.setVisible(True)
            else:
                label_icon_spacing.setVisible(False)
                spin_icon_spacing.setEnabled(False)
                spin_icon_spacing.setVisible(False)

            if shape in ["TableTop", "TableDown"]:
                label_num_column.setText(
                    translate("PieMenuTab", "Number of columns:"))
            else:
                label_num_column.setText(
                    translate("PieMenuTab", "Number of rows:"))

            if shape in ["Pie", "LeftRight"]:
                labeldisplay_command_name.setVisible(True)
                checkbox_display_command_name.setVisible(True)
                checkbox_display_command_name.setEnabled(True)

            else:
                labeldisplay_command_name.setVisible(False)
                checkbox_display_command_name.setVisible(False)
                checkbox_display_command_name.setEnabled(False)

            if shape in ["Concentric", "Star"]:
                label_command_per_circle.setVisible(True)
                spin_command_per_circle.setEnabled(True)
                spin_command_per_circle.setVisible(True)
            else:
                label_command_per_circle.setVisible(False)
                spin_command_per_circle.setEnabled(False)
                spin_command_per_circle.setVisible(False)

            if shape in ["Pie", "RainbowUp", "RainbowDown"]:
                label_display_preselect.setVisible(True)
                checkbox_display_preselect.setVisible(True)
                checkbox_display_preselect.setEnabled(True)
            else:
                label_display_preselect.setVisible(False)
                checkbox_display_preselect.setVisible(False)
                checkbox_display_preselect.setEnabled(False)

        # Available for all shapes
        label_shortcut_size.setVisible(True)
        spin_shortcut_label_size.setVisible(True)
        spin_shortcut_label_size.setEnabled(True)

    except Exception as exc:
        from piemenu import log
        log.log_error("on_shape: failed to update widget visibility", exc)

def get_shape(keyValue=None):
    """ Get value of shape of current PieMenu """
    if keyValue is None:
        keyValue = get_param(constants.PARAM_CURRENT_PIE)
    group = get_group()
    shape = group.GetString(constants.PARAM_SHAPE)

    indexList = get_index_list()
    for i in indexList:
        try:
            pieName = config.get_params()["index"].GetString(str(i))
        except AttributeError:
            pieName = config.get_params()["index"].GetString(str(i))
        if pieName == keyValue:
            param = config.get_params()["index"].GetGroup(str(i))
            shape = param.GetString(constants.PARAM_SHAPE)

    combo_shape.blockSignals(True)
    combo_shape.clear()
    # TODO only place available_shape is used: inline
    combo_shape.addItems(constants.available_shape)
    index = combo_shape.findText(shape)
    if index != -1:
        combo_shape.setCurrentIndex(index)
    combo_shape.blockSignals(False)

    return shape


def on_context(state):
    """ Set context mode activation """
    if state == 2 or state == 1:
        config.get_params()["main"].SetBool(constants.PARAM_ENABLE_CONTEXT, True)
        context_list()
    else:
        config.get_params()["main"].SetBool(constants.PARAM_ENABLE_CONTEXT, False)
    add_observer()

def on_back_to_settings():
    """ Return to general settings interface """
    tool_bar_tab.setVisible(False)
    piemenu_box_group.setVisible(True)
    button_existing_tool_bar.setVisible(True)
    for i in reversed(range(buttons_layout.count())):
        try:
            buttons_layout.itemAt(i).widget().show()
        except Exception:
            # layout items without a widget (spacers, layouts) are skipped
            None
    tabs.setVisible(True)

    v_splitter.refresh()
    button_back_to_settings.setVisible(False)
    on_pie_change()
    update_piemenu_preview()
    if on_assistant_refresh is not None:
        on_assistant_refresh()

#### Preferences dialog ####
def on_control():
    """Initializes the preferences dialog."""
    wb = Gui.activeWorkbench()
    wbName = wb.name()
    wbName = wbName.replace("Workbench", "")
    keyValue = get_pie_name(wbName)

    if keyValue is None:
        keyValue = get_param(constants.PARAM_CURRENT_PIE)

    c_box_update(keyValue)

    tool_list_ui.button_list()
    tabs.setCurrentIndex(0)

    for i in mw.findChildren(QtGui.QDialog):
        if i.objectName() == "PieMenuPreferences":
            i.deleteLater()
        else:
            pass

    label_global_shortcut.setText(
        translate("GlobalSettingsTab", "Global shortcut: ") + state.app_state.global_shortcut_key)

    pie_menu_dialog.show()
    shape = get_shape(c_box.currentText())
    on_shape(shape)
    settings_ui.update_icons_pie_menus()
    update_piemenu_preview()
    #### END Preferences dialog ####
