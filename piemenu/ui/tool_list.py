"""Tool-list and selected-tools tables of the preferences dialog.

`button_list()` fills the "selected tools" table (the pie content) and
`tool_list()` fills the "all commands" table. The remaining helpers keep both
tables in sync (checkboxes, search, reordering, separators).

The widgets and a few callbacks below are created by `pieMenuStart()` after
this module is imported, so they are declared as module attributes here and
published by `pieMenuStart()` through `publish()`.
"""

import FreeCAD as App
import FreeCADGui as Gui
from PySide import QtCore, QtGui, QtWidgets

from piemenu import config, constants, log, state
from piemenu.config import get_index_list, get_param_index
from piemenu.workbench import extract_workbench, get_gui_action_map_all, resolve_workbench_name


def translate(context, text):
    """Translate a string with the FreeCAD Qt translator."""
    return App.Qt.translate(context, text)


# Widgets and callbacks created by `pieMenuStart()` and injected via `publish()`.
button_list_widget = None
c_box = None
get_group = None
pie_menu_instance = None
reload_workbench = None
show_piemenu = None
tool_list_widget = None


def publish(**references):
    """Publish the runtime references used by the tool-list helpers."""
    globals().update(references)


def button_list():
    indexList = get_index_list()

    for i in indexList:
        pie = get_param_index(str(i))
        if pie == c_box.currentText():
            group = config.get_params()["index"].GetGroup(str(i))
            tool_list = group.GetString(constants.PARAM_TOOL_LIST)
        else:
            pass

    if tool_list:
        tool_list = tool_list.split(".,.")
    else:
        tool_list = []

    actionMapAll = get_gui_action_map_all()
    lastWorkbench = Gui.activeWorkbench()

    for i in tool_list:
        if i not in actionMapAll:
            # rule out special case: there has to be an entry
            if i == "":
                pass
            else:
                workbench = extract_workbench(i)
                if workbench not in state.app_state.loaded_workbenches and "Workbench" not in workbench:
                    # rule out special case: unknown Std action
                    if workbench == "Std":
                        pass
                    else:
                        wbName = resolve_workbench_name(workbench)
                        try:
                            Gui.activateWorkbench(wbName)
                            state.app_state.loaded_workbenches.append(workbench)
                        except KeyError:
                            # The command belongs to a workbench that is not
                            # installed (e.g. a macro prefixed with "Custom_"):
                            # nothing to activate, skip silently.
                            pass
                        except Exception as exc:
                            log.log_warning_once(
                                "wb:" + wbName,
                                "cannot activate workbench %s" % wbName, exc)
                else:
                    pass
        else:
            pass
    Gui.activateWorkbench(lastWorkbench.__class__.__name__)

    button_list_widget.blockSignals(True)
    button_list_widget.clearContents()
    button_list_widget.setRowCount(0)

    shortcutCode = 48
    for i in tool_list:
        if i in actionMapAll:

            rowPosition = button_list_widget.rowCount()
            button_list_widget.insertRow(rowPosition)

            actionItem = QtWidgets.QTableWidgetItem(
                actionMapAll[i].text().replace("&", ""))
            actionItem.setData(QtCore.Qt.UserRole, i)
            actionItem.setIcon(actionMapAll[i].icon())
            actionItem.setToolTip(actionMapAll[i].toolTip())
            shortcutItem = QtWidgets.QTableWidgetItem()
            # prevent user to select shortcut in list
            shortcutItem.setFlags(QtCore.Qt.ItemIsEnabled)
            shortcutItem.setTextAlignment(QtCore.Qt.AlignCenter)

            if (actionMapAll[i].text()) == translate('PieMenuTab', 'Separator'):
                shortcutItem.setText("")
            else:
                # we add shortcut till we are not beyond the letter Z
                if shortcutCode <= 90:
                    shortcutItem.setText(chr(shortcutCode))
                    button_list_widget.setItem(rowPosition, 0, shortcutItem)

                # trick to jump form key 9 to key A in ascii list
                if shortcutCode == 57:
                    shortcutCode = 64
                shortcutCode += 1
                # trick to avoid X key, which bug !
                if shortcutCode == 88:
                    shortcutCode = 89

            button_list_widget.setItem(rowPosition, 1, actionItem)

    button_list_widget.blockSignals(False)

    show_piemenu.hide()
    pie_menu_instance.showPiemenuPreview(keyValue=c_box.currentText())
    show_piemenu.show()

def tool_list():
    """ Handle list of tools and checkboxes """
    actionMapAll = get_gui_action_map_all()
    tool_list_widget.blockSignals(True)
    tool_list_widget.clearContents()
    tool_list_widget.setRowCount(0)
    row = 0

    # Remplissage du QTableWidget avec les actions
    for i in actionMapAll:
        tool_list_widget.insertRow(row)

        # Colonne 0 : Sélectionné (Checkbox)
        checkbox_item = QtGui.QTableWidgetItem()
        checkbox_item.setCheckState(QtCore.Qt.Unchecked)
        checkbox_item.setFlags(
            QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled)
        checkbox_item.setTextAlignment(QtCore.Qt.AlignCenter)
        tool_list_widget.setItem(row, 0, checkbox_item)

        # Colonne 1 : Icône et Nom
        actionItem = QtWidgets.QTableWidgetItem(
            actionMapAll[i].text().replace("&", ""))
        actionItem.setData(QtCore.Qt.UserRole, i)
        actionItem.setIcon(actionMapAll[i].icon())
        actionItem.setFlags(QtCore.Qt.ItemIsEnabled)
        actionItem.setToolTip(actionMapAll[i].toolTip())
        tool_list_widget.setItem(row, 1, actionItem)

        # Colonne 2 : Workbench
        workbench = extract_workbench(i)
        if workbench:
            if workbench == "Std":
                workbench = "FreeCAD"
            wb_item = QtGui.QTableWidgetItem(workbench)
            wb_item.setFlags(QtCore.Qt.ItemIsEnabled)
            tool_list_widget.setItem(row, 2, wb_item)
        else:
            wb_item = QtGui.QTableWidgetItem(i)
            wb_item.setFlags(QtCore.Qt.ItemIsEnabled)
            tool_list_widget.setItem(row, 2, wb_item)

        row += 1

    # Gestion de la liste des outils sélectionnés
    toolListOn = None
    indexList = get_index_list()
    for i in indexList:
        pie = get_param_index(str(i))
        if pie == c_box.currentText():
            group = config.get_params()["index"].GetGroup(str(i))
            toolListOn = group.GetString(constants.PARAM_TOOL_LIST)
        else:
            pass

    if toolListOn:
        toolListOn = toolListOn.split(".,.")
    else:
        toolListOn = []

    # Mise à jour des checkboxes selon la liste enregistrée
    for row in range(tool_list_widget.rowCount()):
        item_name = tool_list_widget.item(row, 1)
        checkbox_item = tool_list_widget.item(row, 0)
        if item_name.data(QtCore.Qt.UserRole) in toolListOn:
            checkbox_item.setCheckState(QtCore.Qt.Checked)
        else:
            checkbox_item.setCheckState(QtCore.Qt.Unchecked)

    tool_list_widget.blockSignals(False)

def sort_tool_list_by_column(index):
    """ Tri alterné des colonnes avec indicateur """

    if index == 0:
        tool_list_widget.horizontalHeader().setSortIndicatorShown(False)
        return
    else:
        tool_list_widget.horizontalHeader().setSortIndicatorShown(True)
        tool_list_widget.sortItems(index, state.app_state.sort_order)
        tool_list_widget.horizontalHeader().setSortIndicator(index, state.app_state.sort_order)
        # Alterner le tri pour le prochain clic
        state.app_state.sort_order = (
            QtCore.Qt.DescendingOrder
            if state.app_state.sort_order == QtCore.Qt.AscendingOrder
            else QtCore.Qt.AscendingOrder
        )

def on_tool_list_widget():
    """ Handle list of tool selections in the QTableWidget """
    checkListOn = []
    checkListOff = []

    for row in range(tool_list_widget.rowCount()):
        checkbox_item = tool_list_widget.item(row, 0)
        if checkbox_item:
            item_name = tool_list_widget.item(row, 1)
            # if checkbox_item.checkState(): !!! incompatible avec Qt6, utiliser à la place : if checkbox_item.checkState() == QtCore.Qt.Checked:
            if checkbox_item.checkState() == QtCore.Qt.Checked:
                checkListOn.append(item_name.data(QtCore.Qt.UserRole))
            else:
                checkListOff.append(item_name.data(QtCore.Qt.UserRole))

    tool_list = None
    indexList = get_index_list()
    for i in indexList:
        pie = get_param_index(str(i))
        if pie == c_box.currentText():
            group = config.get_params()["index"].GetGroup(str(i))
            tool_list = group.GetString(constants.PARAM_TOOL_LIST)

    if tool_list:
        tool_list = tool_list.split(".,.")
    else:
        tool_list = []

    for i in checkListOn:
        if i not in tool_list:
            tool_list.append(i)

    for i in checkListOff:
        if i in tool_list:
            tool_list.remove(i)

    for i in indexList:
        pie = get_param_index(str(i))
        if pie == c_box.currentText():
            group = config.get_params()["index"].GetGroup(str(i))
            group.SetString(constants.PARAM_TOOL_LIST, ".,.".join(tool_list))

    button_list()

def search_in_tool_list(search_text):
    """ Rechercher un outil dans la liste des outils """
    search_text = search_text.lower()
    actionMapAll = get_gui_action_map_all()

    tool_list_widget.blockSignals(True)
    tool_list_widget.clearContents()
    tool_list_widget.setRowCount(0)
    row = 0

    # Remplir le QTableWidget avec uniquement les résultats de la recherche
    for i in actionMapAll:
        action_text = actionMapAll[i].text().replace("&", "")
        workbench = extract_workbench(i)
        if search_text in action_text.lower() or search_text in workbench.lower():
            tool_list_widget.insertRow(row)

            # Colonne 0 : Checkbox
            checkbox_item = QtGui.QTableWidgetItem()
            checkbox_item.setCheckState(QtCore.Qt.Unchecked)
            checkbox_item.setFlags(
                QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled)
            tool_list_widget.setItem(row, 0, checkbox_item)

            # Colonne 1 : Icône et Nom
            actionItem = QtWidgets.QTableWidgetItem(action_text)
            actionItem.setData(QtCore.Qt.UserRole, i)
            actionItem.setIcon(actionMapAll[i].icon())
            actionItem.setFlags(QtCore.Qt.ItemIsEnabled)
            actionItem.setToolTip(actionMapAll[i].toolTip())
            tool_list_widget.setItem(row, 1, actionItem)

            # Colonne 2 : Workbench
            if workbench:
                if workbench == "Std":
                    workbench = "FreeCAD"
                wb_item = QtGui.QTableWidgetItem(workbench)
                wb_item.setFlags(QtCore.Qt.ItemIsEnabled)
                tool_list_widget.setItem(row, 2, wb_item)
            else:
                wb_item = QtGui.QTableWidgetItem(i)
                wb_item.setFlags(QtCore.Qt.ItemIsEnabled)
                tool_list_widget.setItem(row, 2, wb_item)

                row += 1

    toolListOn = None
    indexList = get_index_list()
    for i in indexList:
        pie = get_param_index(str(i))
        if pie == c_box.currentText():
            group = config.get_params()["index"].GetGroup(str(i))
            toolListOn = group.GetString(constants.PARAM_TOOL_LIST)

    if toolListOn:
        toolListOn = toolListOn.split(".,.")
    else:
        toolListOn = []

    for row in range(tool_list_widget.rowCount()):
        item_name = tool_list_widget.item(row, 1)
        checkbox_item = tool_list_widget.item(row, 0)
        if item_name.data(QtCore.Qt.UserRole) in toolListOn:
            checkbox_item.setCheckState(QtCore.Qt.Checked)
        else:
            checkbox_item.setCheckState(QtCore.Qt.Unchecked)

    tool_list_widget.blockSignals(False)

def button_list_2_tool_list(button_list_widget):
    """ add tool to list on button click """
    toolData = []
    rowCount = button_list_widget.rowCount()

    for row in range(rowCount):
        item = button_list_widget.item(row, 1)
        if (item.data(QtCore.Qt.UserRole)) is not None:
            toolData.append(item.data(QtCore.Qt.UserRole))
    group = get_group()
    group.SetString(constants.PARAM_TOOL_LIST, ".,.".join(toolData))

def on_button_up():
    """ Move up the selected tools in the list """
    selected_ranges = button_list_widget.selectedRanges()
    if not selected_ranges:
        return

    selected_rows = set()
    for selection in selected_ranges:
        for row in range(selection.topRow(), selection.bottomRow() + 1):
            selected_rows.add(row)

    selected_rows = sorted(selected_rows)

    if 0 in selected_rows:
        return

    for row in selected_rows:
        item_first_column = button_list_widget.takeItem(row, 0)
        item_second_column = button_list_widget.takeItem(row, 1)

        button_list_widget.removeRow(row)
        button_list_widget.insertRow(row - 1)
        button_list_widget.setItem(row - 1, 0, item_first_column)
        button_list_widget.setItem(row - 1, 1, item_second_column)

    button_list_2_tool_list(button_list_widget)
    button_list()

    for row in selected_rows:
        button_list_widget.setRangeSelected(
            QtGui.QTableWidgetSelectionRange(row - 1, 0, row - 1, 1), True)

def on_button_down():
    """ Move down the selected tools in the list """
    selected_ranges = button_list_widget.selectedRanges()

    if not selected_ranges:
        return

    selected_rows = set()
    for selection in selected_ranges:
        for row in range(selection.topRow(), selection.bottomRow() + 1):
            selected_rows.add(row)

    selected_rows = sorted(selected_rows, reverse=True)
    rowCount = button_list_widget.rowCount()

    if rowCount - 1 in selected_rows:
        return

    for row in selected_rows:
        item_first_column = button_list_widget.takeItem(row, 0)
        item_second_column = button_list_widget.takeItem(row, 1)

        button_list_widget.removeRow(row)
        button_list_widget.insertRow(row + 1)
        button_list_widget.setItem(row + 1, 0, item_first_column)
        button_list_widget.setItem(row + 1, 1, item_second_column)

    button_list_2_tool_list(button_list_widget)
    button_list()

    for row in selected_rows:
        button_list_widget.setRangeSelected(
            QtGui.QTableWidgetSelectionRange(row + 1, 0, row + 1, 1), True)

def on_button_remove_command():
    """ Remove selected tools from the list """
    selected_ranges = button_list_widget.selectedRanges()
    if not selected_ranges:
        return

    rows_to_remove = set()
    for selection in selected_ranges:
        for row in range(selection.topRow(), selection.bottomRow() + 1):
            rows_to_remove.add(row)

    for row in sorted(rows_to_remove, reverse=True):
        items = []
        for column in range(button_list_widget.columnCount()):
            item = button_list_widget.takeItem(row, column)
            items.append(item)

        button_list_widget.removeRow(row)

    button_list_widget.setFocus()
    button_list_2_tool_list(button_list_widget)
    button_list()
    tool_list()

    if rows_to_remove:
        last_removed_row = max(rows_to_remove)
        new_index = last_removed_row - len(rows_to_remove)
        if new_index >= 0:
            button_list_widget.setCurrentCell(new_index, 1)

def on_button_add_separator():
    """ Handle separator for PieMenus """
    # we must create a custom toolbar "PieMenuTB" to 'activate' the command 'PieMenu_Separator' otherwise the separators are not correctly handled
    globaltoolbar = App.ParamGet(
        'User parameter:BaseApp/Workbench/Global/Toolbar/Custom_PieMenu')

    pieMenuTB = globaltoolbar.GetString('Name')
    if pieMenuTB == "PieMenuTB":
        pass
    else:
        globaltoolbar.SetString('Name', 'PieMenuTB')
        App.saveParameter()

    globaltoolbar.SetString('PieMenu_Separator', 'FreeCAD')

    reload_workbench()

    # we hide the custom toolbar
    mw = Gui.getMainWindow()
    for i in mw.findChildren(QtGui.QToolBar):
        if i.windowTitle() == 'PieMenuTB':
            i.setVisible(False)

    items = []
    for row in range(tool_list_widget.rowCount()):
        items.append(tool_list_widget.item(row, 0))

    tool_list = None
    indexList = get_index_list()
    for i in indexList:
        pie = get_param_index(str(i))

        if pie == c_box.currentText():
            group = config.get_params()["index"].GetGroup(str(i))
            tool_list = group.GetString(constants.PARAM_TOOL_LIST)
        else:
            pass

    if tool_list:
        tool_list = tool_list.split(".,.")
    else:
        tool_list = []

    i = "PieMenu_Separator"
    tool_list.append(i)

    for i in indexList:
        pie = get_param_index(str(i))
        if pie == c_box.currentText():
            group = config.get_params()["index"].GetGroup(str(i))
            tool_list = group.SetString(constants.PARAM_TOOL_LIST, ".,.".join(tool_list))
        else:
            pass
    button_list()

