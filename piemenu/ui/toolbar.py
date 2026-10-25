"""Toolbar helpers for the ToolBar tab of the preferences dialog.

`on_list_tool_bar()` lists the existing FreeCAD toolbars, `show_list_tool_bar()`
previews the commands of the selected one, `on_add_tool_bar()` creates a new pie
from it and `on_button_tool_bar()` switches the dialog to that tab.

The widgets and callbacks below are created by `pieMenuStart()` after this
module is imported, so they are declared as module attributes here and
published by `pieMenuStart()` through `publish()`.
"""

from PySide import QtCore, QtGui, QtWidgets
from PySide.QtWidgets import QListWidgetItem

from piemenu import config, constants
from piemenu.workbench import get_gui_action_map_all, get_gui_tool_button_data


def translate(context, text):
    """Translate a string with the FreeCAD Qt translator."""
    import FreeCAD as App
    return App.Qt.translate(context, text)


# Widgets and callbacks created by `pieMenuStart()` and injected via `publish()`.
button_back_to_settings = None
button_existing_tool_bar = None
button_list_widget = None
buttons_layout = None
create_pie = None
info_shortcut = None
input_text_dialog = None
list_tool_bar = None
mw = None
on_back_to_settings = None
piemenu_box_group = None
tabs = None
tool_bar_tab = None
update_piemenu_preview = None


def publish(**references):
    """Publish the runtime references used by the toolbar helpers."""
    globals().update(references)


def on_list_tool_bar():
    """Handle the toolbar list."""
    list_tool_bar.clear()
    list_tool_bar.blockSignals(True)
    if config.get_params()["main"].GetBool(constants.PARAM_TOOL_BAR):
        text = config.get_params()["main"].GetString(constants.PARAM_TOOL_BAR)
        if ": " in text:
            toolbar_desc = text.split(": ")
            text = toolbar_desc[1]
    else:
        text = None

    for toolbar in mw.findChildren(QtGui.QToolBar):
        barList = []

        for action in toolbar.findChildren(QtGui.QAction):
            if not action.isSeparator() and action.text() != "":
                barList.append(action)

        for command in barList:
            item = QListWidgetItem()
            item.setText(command.text())

            # filter for empty toolbar
            commands = []
            get_gui_tool_button_data(command.text(), None, commands, None)
            if len(commands) != 0:
                list_tool_bar.addItem(item)

    list_tool_bar.blockSignals(False)
    return list_tool_bar

def on_add_tool_bar():
    """ create a menu from an existing toolbar  """
    items = []
    commands = []
    for index in range(list_tool_bar.count()):
        items.append(list_tool_bar.item(index))
    text, ok = input_text_dialog(translate("PieMenuTab", "New menu"))
    if not ok:
        return text, ok
    else:
        newPieGroup = create_pie(text)
        toolbar = list_tool_bar.currentItem()
        get_gui_tool_button_data(toolbar.text(), None, commands, None)
        newPieGroup.SetString(constants.PARAM_TOOL_LIST, ".,.".join(commands))
        newPieGroup.SetString(constants.PARAM_SHAPE, "Pie")
        tabs.setCurrentIndex(0)
    on_back_to_settings()
    update_piemenu_preview()

def show_list_tool_bar():
    """ show list of tools of an existing toolbar  """
    items = []
    commands = []

    for index in range(list_tool_bar.count()):
        items.append(list_tool_bar.item(index))
        if items[index].isSelected():
            sender = list_tool_bar.item(index)
            get_gui_tool_button_data(sender.text(), None, commands, None)

    button_list_widget.blockSignals(True)
    button_list_widget.clearContents()
    button_list_widget.setRowCount(0)

    actionMapAll = get_gui_action_map_all()
    for i in commands:
        if i in actionMapAll:
            rowPosition = button_list_widget.rowCount()
            button_list_widget.insertRow(rowPosition)
            actionItem = QtWidgets.QTableWidgetItem(
                actionMapAll[i].text().replace("&", ""))
            actionItem.setData(QtCore.Qt.UserRole, i)
            actionItem.setIcon(actionMapAll[i].icon())
            actionItem.setFlags(QtCore.Qt.ItemIsEnabled)
            button_list_widget.setItem(rowPosition, 1, actionItem)
            actionItem.setToolTip(actionMapAll[i].toolTip())

    button_list_widget.blockSignals(False)
    update_piemenu_preview("toolBarTab")

def on_button_tool_bar():
    """ Show interface to add existing Freecad's Toolbars """
    info_shortcut.setText('')
    piemenu_box_group.setVisible(False)

    tabs.setVisible(False)
    tool_bar_tab.setVisible(True)
    button_back_to_settings.setVisible(True)
    button_existing_tool_bar.setVisible(False)

    for i in reversed(range(buttons_layout.count())):
        try:
            buttons_layout.itemAt(i).widget().hide()
        except Exception:
            # layout items without a widget (spacers, layouts) are skipped
            None
        # hide shortcuts in button_list_widget
        button_list_widget.setColumnHidden(0, True)

    # generate list of existing toolBars
    list_tool_bar = on_list_tool_bar()

    # set first element of list_tool_bar
    index = list_tool_bar.model().index(0, 0)
    if index.isValid():
        list_tool_bar.setCurrentIndex(index)
    show_list_tool_bar()

    update_piemenu_preview("toolBarTab")

