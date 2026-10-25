"""Display-option handlers for the preferences dialog.

These callbacks react to the checkboxes and spinboxes that control how the
PieMenu commands are displayed and triggered: command names, preselection,
shortcuts, context trigger, quick menu and right-click delay.

The widgets and callbacks below are created by `pieMenuStart()` after this
module is imported, so they are declared as module attributes here and
published by `pieMenuStart()` through `publish()`.
"""

from piemenu import config, constants
from piemenu.config import get_index_list, get_param_index
from piemenu.context import add_observer, context_list


# Widgets and callbacks created by `pieMenuStart()` and injected via `publish()`.
button_list_widget = None
c_box = None
checkbox_display_shortcut = None
pie_menu_dialog = None
spin_delay_right_click = None
spin_hover_delay = None
spin_shortcut_label_size = None
update_piemenu_preview = None


def publish(**references):
    """Publish the runtime references used by the option handlers."""
    globals().update(references)


def set_trigger_mode(triggerMode):
    """ Set TriggerMode in parameter """
    if triggerMode == "Press":
        spin_hover_delay.setEnabled(False)
    else:
        spin_hover_delay.setEnabled(True)
    indexList = get_index_list()
    for i in indexList:
        pieName = get_param_index(str(i))
        if pieName == c_box.currentText():
            param = config.get_params()["index"].GetGroup(str(i))
            param.SetString(constants.PARAM_TRIGGER_MODE, triggerMode)

def on_display_command_name(state):
    """ Set parameter to show or not 'Command names' """
    indexList = get_index_list()
    for i in indexList:
        pieName = get_param_index(str(i))
        if pieName == c_box.currentText():
            param = config.get_params()["index"].GetGroup(str(i))
            param.SetBool(constants.PARAM_DISPLAY_COMMAND, state)
    try:
        # the pie menu preview may not exist yet: skip the refresh in that case
        if pie_menu_dialog.isVisible():
            update_piemenu_preview()
    except Exception:
        None

def on_display_preselect(state):
    """ Set parameter to show or not 'Preselect button' """
    indexList = get_index_list()
    for i in indexList:
        pieName = get_param_index(str(i))
        if pieName == c_box.currentText():
            param = config.get_params()["index"].GetGroup(str(i))
            param.SetBool(constants.PARAM_DISPLAY_PRESELECT, state)
    try:
        # the pie menu preview may not exist yet: skip the refresh in that case
        if pie_menu_dialog.isVisible():
            update_piemenu_preview()
    except Exception:
        None

def on_enable_shortcut(state):
    """ Set parameter for enable or not 'Shortcut Tool' """
    if state:
        spin_shortcut_label_size.setEnabled(True)
        button_list_widget.setColumnHidden(0, False)
        checkbox_display_shortcut.setEnabled(True)

    else:
        spin_shortcut_label_size.setEnabled(False)
        button_list_widget.setColumnHidden(0, True)
        checkbox_display_shortcut.setEnabled(False)

    indexList = get_index_list()
    for i in indexList:
        pieName = get_param_index(str(i))
        if pieName == c_box.currentText():
            param = config.get_params()["index"].GetGroup(str(i))
            param.SetBool(constants.PARAM_ENABLE_SHORTCUT, state)
    try:
        # the pie menu preview may not exist yet: skip the refresh in that case
        if pie_menu_dialog.isVisible():
            update_piemenu_preview()
    except Exception:
        None

def on_display_shortcut(state):
    """ Set parameter for display or not 'Shortcut Tool' """
    if state == 2:
        spin_shortcut_label_size.setEnabled(True)
    else:
        spin_shortcut_label_size.setEnabled(False)

    indexList = get_index_list()
    for i in indexList:
        pieName = get_param_index(str(i))
        if pieName == c_box.currentText():
            param = config.get_params()["index"].GetGroup(str(i))
            param.SetBool(constants.PARAM_DISPLAY_SHORTCUT, state)
    update_piemenu_preview()

def on_trigger_context(state):
    """ Set parameter for immediate trigger context mode """
    indexList = get_index_list()
    for i in indexList:
        pieName = get_param_index(str(i))
        if pieName == c_box.currentText():
            param = config.get_params()["index"].GetGroup(str(i))
            param.SetBool("ImmediateTriggerContext", state)

def on_show_quick_menu(state):
    """ Set visibility of Quickmenu """
    if state == 2:
        config.get_params()["main"].SetBool(constants.PARAM_SHOW_QUICK_MENU, True)
        context_list()
        add_observer()
    else:
        config.get_params()["main"].SetBool(constants.PARAM_SHOW_QUICK_MENU, False)
    update_piemenu_preview()

def on_right_click_trigger(state):
    """ Set right click trigger """
    if state == 2:
        config.get_params()["main"].SetBool(constants.PARAM_RIGHT_CLICK_TRIGGER, True)
        spin_delay_right_click.setEnabled(True)
    else:
        config.get_params()["main"].SetBool(constants.PARAM_RIGHT_CLICK_TRIGGER, False)
        spin_delay_right_click.setEnabled(False)
