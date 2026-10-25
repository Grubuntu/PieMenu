"""Keyboard shortcut handling for the PieMenu workbench.

Manages the per-PieMenu shortcuts and the global shortcut, updating the
FreeCAD parameters and warning the user when a shortcut is already assigned
to another command.
"""

from piemenu import config, constants, state


def get_shortcut_list():
    """(Re)create the QShortcut objects for each PieMenu and return them as displayable text."""
    import FreeCADGui as Gui
    from PySide.QtGui import QKeySequence, QShortcut

    mw = Gui.getMainWindow()
    pie_menu_instance = state.app_state.pie_menu_instance

    # Remove the previous QShortcut objects.
    for shortcut in mw.findChildren(QShortcut):
        try:
            shortcut.activated.disconnect()
        except Exception:
            # no slot connected to this shortcut: nothing to remove
            pass
        shortcut.setParent(None)
        shortcut.deleteLater()

    shortcut_list = []

    index_list = config.get_index_list()
    for i in index_list:
        param = config.get_params()["index"].GetGroup(str(i))
        name_pie = config.get_params()["index"].GetString(str(i))
        shortcut_key = param.GetString(constants.PARAM_SHORTCUT_KEY)
        if shortcut_key:
            shortcut_list.append((name_pie, shortcut_key))

    def create_shortcut_handler(name):
        return lambda: pie_menu_instance.showAtMouseInstance(keyValue=name)

    for name_pie, shortcut_key in shortcut_list:
        shortcut = QShortcut(QKeySequence(shortcut_key), mw)
        shortcut.activated.connect(create_shortcut_handler(name_pie))
        shortcut.setEnabled(True)

    # Return the displayable list for debug or display.
    return [f"PieMenu_{name} => {key}" for name, key in shortcut_list]


def get_assigned_shortcut():
    """Return the shortcuts already assigned by FreeCAD actions and by PieMenu."""
    import FreeCADGui as Gui
    from PySide import QtGui

    shortcuts_assigned = [
        f"{act.whatsThis()} => {act.shortcut().toString()}"
        for act in Gui.getMainWindow().findChildren(QtGui.QAction)
        if not act.shortcut().isEmpty() and act.whatsThis()
    ]
    shortcuts_assigned.extend(get_shortcut_list())
    return shortcuts_assigned


def compare_and_display_warning(info_shortcut, shortcuts_assigned, current_shortcut):
    """Display a warning on the info label when the shortcut is already assigned."""
    info_shortcut.setText('')
    for assigned_shortcut in shortcuts_assigned:
        command, shortcut = assigned_shortcut.split(" => ")
        if shortcut.replace(" ", "").lower() == current_shortcut.lower():
            info_shortcut.setText(
                f' Warning: {current_shortcut} is already assigned for {command}')
            break


def update_shortcut_key(new_shortcut, combo_pie, label_shortcut, line_shortcut):
    """Validate and store the individual shortcut of the currently selected PieMenu."""
    import FreeCAD as App

    translate = App.Qt.translate

    if not new_shortcut:
        state.app_state.shortcut_key = new_shortcut
        config.set_parameter_group(combo_pie.currentText(), "String",
                                   constants.PARAM_SHORTCUT_KEY, state.app_state.shortcut_key)
        label_shortcut.setText(translate(
            "PieMenuTab", "Shortcut deleted! No shortcut assigned ")
            + state.app_state.shortcut_key)

    else:
        parts = set(new_shortcut.replace(',', '+').split('+'))
        for part in parts:
            if part not in constants.touches_speciales and len(part) > 1:
                label_shortcut.setText(
                    translate("PieMenuTab", "Invalid shortcut! Current shortcut: ")
                    + state.app_state.shortcut_key)
            else:
                state.app_state.shortcut_key = new_shortcut
                config.set_parameter_group(combo_pie.currentText(),
                                           "String", constants.PARAM_SHORTCUT_KEY,
                                           state.app_state.shortcut_key)
                label_shortcut.setText(
                    translate("PieMenuTab", "New shortcut assigned: ")
                    + state.app_state.shortcut_key)
    line_shortcut.setText(state.app_state.shortcut_key)
    get_shortcut_list()


def update_global_shortcut_key(new_shortcut, label_global_shortcut,
                               line_global_shortcut):
    """Validate and store the global shortcut used to open the default PieMenu."""
    import FreeCAD as App
    from PySide import QtGui

    translate = App.Qt.translate
    action_key = state.app_state.action_key

    if not new_shortcut:
        state.app_state.global_shortcut_key = new_shortcut
        config.get_params()["main"].SetString(constants.PARAM_GLOBAL_SHORTCUT_KEY,
                                              state.app_state.global_shortcut_key)
        label_global_shortcut.setText(translate("GlobalSettingsTab",
                                                "Shortcut deleted ! No shortcut assigned ")
                                      + state.app_state.global_shortcut_key)

    else:
        parts = set(new_shortcut.replace(',', '+').split('+'))
        for part in parts:
            if part not in constants.touches_speciales and len(part) > 1:
                label_global_shortcut.setText(translate("GlobalSettingsTab",
                                                        "Invalid shortcut ! Current global shortcut : ")
                                              + state.app_state.global_shortcut_key)
            else:
                state.app_state.global_shortcut_key = new_shortcut
                config.get_params()["main"].SetString(constants.PARAM_GLOBAL_SHORTCUT_KEY,
                                                      state.app_state.global_shortcut_key)
                label_global_shortcut.setText(translate("GlobalSettingsTab",
                                                        "New global shortcut assigned: ")
                                              + state.app_state.global_shortcut_key)
    action_key.setShortcut(QtGui.QKeySequence(state.app_state.global_shortcut_key))
    line_global_shortcut.setText(state.app_state.global_shortcut_key)
