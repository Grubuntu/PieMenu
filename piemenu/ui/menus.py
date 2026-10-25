"""PieMenu (menu) management for the preferences dialog.

`input_text_dialog()` prompts for a menu name, `create_pie()` creates a new
PieMenu, `create_nested_pie_menus()` registers one FreeCAD command per PieMenu
and the `on_button_*_pie_menu()` handlers add, remove, rename and copy the
menus stored in the PieMenu parameters.

The widgets and callbacks below are created by `pieMenuStart()` after this
module is imported, so they are declared as module attributes here and
published by `pieMenuStart()` through `publish()`.
"""

import FreeCAD as App
import FreeCADGui as Gui
from PySide import QtGui

from piemenu import config, constants, resources, state
from piemenu.commands import NestedPieMenu
from piemenu.config import get_index_list, get_param, get_param_index, get_parameter_group
from piemenu.defaults import set_default_pie, set_default_values
from piemenu.ui.tool_list import tool_list


def translate(context, text):
    """Translate a string with the FreeCAD Qt translator."""
    return App.Qt.translate(context, text)


# Widgets and callbacks created by `pieMenuStart()` and injected via `publish()`.
c_box = None
c_box_update = None
get_group = None
on_pie_change = None
pie_menu_dialog = None
reload_workbench = None


def publish(**references):
    """Publish the runtime references used by the menu helpers."""
    globals().update(references)


def input_text_dialog(title):
    """ Dialog box for PieMenu name """
    info1 = translate("PieMenuTab", "Please insert menu name")
    info2 = translate("PieMenuTab", "Menu already exists")
    d = QtGui.QInputDialog(pie_menu_dialog)
    d.setModal(True)
    d.setInputMode(QtGui.QInputDialog.InputMode.TextInput)
    text, ok = QtGui.QInputDialog.getText(pie_menu_dialog, title, info1)
    if not ok:
        return text, ok
    while not text:
        text, ok = QtGui.QInputDialog.getText(pie_menu_dialog, title, info1)
        if not ok:
            return text, ok
        else:
            pass
    index = c_box.findText(text)
    info = info2
    while index != -1:
        d = QtGui.QInputDialog(pie_menu_dialog)
        d.setModal(True)
        d.setInputMode(QtGui.QInputDialog.InputMode.TextInput)
        text, ok = QtGui.QInputDialog.getText(pie_menu_dialog, title, info)
        if ok:
            if text:
                index = c_box.findText(text)
                info = info2
            else:
                info = info1
        else:
            return text, ok
    return text, ok

def create_nested_pie_menus():
    """ Create a freeCAD command in order to use it as PieMenu """
    index_list = get_index_list()
    for i in index_list:
        pie = get_param_index(str(i))
        icon_path = get_parameter_group(pie, "String", constants.PARAM_ICON_PATH)
        if icon_path == "":
            icon_path = resources.iconPieMenuLogo

        Gui.addCommand('PieMenu_' + pie, NestedPieMenu(pie, icon_path))

        globaltoolbar = App.ParamGet(
            'User parameter:BaseApp/Workbench/Global/Toolbar/Custom_PieMenu')

        pie_menu_tb = globaltoolbar.GetString('Name')
        if pie_menu_tb == 'PieMenuTB':
            pass
        else:
            globaltoolbar.SetString('Name', 'PieMenuTB')

        globaltoolbar.SetString('PieMenu_' + pie, 'FreeCAD')

def create_pie(text):
    """ Create new PieMenu """
    pieList = []
    indexList = get_index_list()
    for i in indexList:
        pieList.append(config.get_params()["index"].GetString(str(i)))
    if text in pieList:
        pass
    elif not text:
        pass
    else:
        if text == "restore_default_pie" and text.lower():
            set_default_pie(restore=True)
        else:
            x = 1
            while x in indexList and x < 999:
                x = x + 1
            else:
                indexNumber = x
            indexList.append(indexNumber)
            temp = []
            for i in indexList:
                temp.append(str(i))
            indexList = temp
            config.get_params()["index"].SetString(constants.PARAM_INDEX_LIST, ".,.".join(indexList))
            indexNumber = str(indexNumber)
            config.get_params()["index"].SetString(indexNumber, text)

        c_box_update(text)
        # set defaults values
        if state.app_state.wizard_running:
            group = config.get_params()["index"].GetGroup(indexNumber)
        else:
            group = get_group()
            set_default_values(group)
        create_nested_pie_menus()
        reload_workbench()
        on_pie_change()

    return config.get_params()["index"].GetGroup(indexNumber)

def on_button_add_pie_menu():
    """ Dialog to add PieMenu """
    text, ok = input_text_dialog(translate("PieMenuTab", "New menu"))
    if not ok:
        return
    create_pie(text)

def on_button_remove_pie_menu():
    """ Remove PieMenu """
    currentPie = get_param(constants.PARAM_CURRENT_PIE)
    contextPie = get_param(constants.PARAM_CONTEXT_PIE)

    indexList = get_index_list()
    for i in indexList:
        pie = get_param_index(str(i))
        if pie == c_box.currentText():
            config.get_params()["index"].RemGroup(str(i))
            config.get_params()["index"].RemString(str(i))

            indexList.remove(i)
            temp = []
            for n in indexList:
                temp.append(str(n))
            indexList = temp
            config.get_params()["index"].SetString(constants.PARAM_INDEX_LIST, ".,.".join(indexList))

            globaltoolbar = App.ParamGet(
                'User parameter:BaseApp/Workbench/Global/Toolbar/Custom_PieMenu')
            globaltoolbar.RemString('PieMenu_' + pie)

            # special case treatment
            if pie == currentPie:
                currentPie = "View"
                config.get_params()["main"].SetString(constants.PARAM_CURRENT_PIE, currentPie)
            if pie == contextPie:
                config.get_params()["main"].RemString(constants.PARAM_CONTEXT_PIE)

            # remove nested_menu in toollist
            for i in indexList:
                toolListe = None
                group = config.get_params()["index"].GetGroup(str(i))
                toolListe = group.GetString(constants.PARAM_TOOL_LIST)

                if toolListe:
                    toolListe = toolListe.split(".,.")
                else:
                    toolListe = []

                stringToFind = 'PieMenu_' + pie

                if (stringToFind) in toolListe:
                    toolListe.remove(stringToFind)
                    toolListe = group.SetString(
                        constants.PARAM_TOOL_LIST, ".,.".join(toolListe))
            break
        else:
            pass

    c_box_update()

    if c_box.currentIndex() == -1:
        set_default_pie()
        c_box_update()
    else:
        pass

def on_button_rename_pie_menu():
    """ Rename PieMenu """
    text, ok = input_text_dialog(translate("PieMenuTab", "Rename menu"))
    if not ok:
        return
    indexList = get_index_list()
    currentPie = get_param(constants.PARAM_CURRENT_PIE)
    for i in indexList:
        pie = get_param_index(str(i))
        if pie == c_box.currentText():
            config.get_params()["index"].SetString(str(i), text)
            if pie == currentPie:
                config.get_params()["main"].SetString(constants.PARAM_CURRENT_PIE, text)
            else:
                pass

            # rename nested_menu in toollist
            for i in indexList:
                toolListe = None

                group = config.get_params()["index"].GetGroup(str(i))
                toolListe = group.GetString(constants.PARAM_TOOL_LIST)

                if toolListe:
                    toolListe = toolListe.split(".,.")
                else:
                    toolListe = []

                stringToFind = 'PieMenu_' + pie

                if (stringToFind) in toolListe:
                    index = toolListe.index(stringToFind)
                    toolListe[index] = 'PieMenu_' + text
                    toolListe = group.SetString(
                        constants.PARAM_TOOL_LIST, ".,.".join(toolListe))

    globaltoolbar = App.ParamGet(
        'User parameter:BaseApp/Workbench/Global/Toolbar/Custom_PieMenu')
    globaltoolbar.RemString('PieMenu_' + pie)
    Gui.addCommand('PieMenu_' + text, NestedPieMenu(text))
    globaltoolbar.SetString('PieMenu_' + text, 'FreeCAD')

    reload_workbench()
    tool_list()
    c_box_update(text)

def get_current_menu_index(currentMenuName):
    """ Get the index through list of PieMenus in parameter """
    indexList = get_index_list()
    for i in indexList:
        indexName = config.get_params()["index"].GetString(str(i))
        if indexName == currentMenuName:
            return str(i)
    return "-1"

def on_button_copy_pie_menu():
    """ Dialog for copy PieMenu """
    text, ok = input_text_dialog(translate("PieMenuTab", "Copy menu"))
    if not ok:
        return

    indexOrg = get_current_menu_index(c_box.currentText())

    pieList = []
    indexList = get_index_list()
    for i in indexList:
        pieList.append(config.get_params()["index"].GetString(str(i)))

    if text in pieList:
        pass
    elif not text:
        pass
    else:
        x = 1

        while x in indexList and x < 999:
            x = x + 1
        else:
            indexCopy = x

        indexList.append(indexCopy)

        temp = []

        for i in indexList:
            temp.append(str(i))

        indexList = temp

        config.get_params()["index"].SetString(constants.PARAM_INDEX_LIST, ".,.".join(indexList))

        indexCopy = str(indexCopy)
        grpOrg = config.get_params()["index"].GetGroup(indexOrg)
        grpCopy = config.get_params()["index"].GetGroup(indexCopy)
        grpOrg.CopyTo(grpCopy)
        grpCopy.SetString(constants.PARAM_SHORTCUT_KEY, "")  # clear shortcutkey

        grpCntOrg = grpOrg.GetGroup("Context")
        grpCntCopy = grpCopy.GetGroup("Context")
        grpCntOrg.CopyTo(grpCntCopy)

        config.get_params()["index"].SetString(indexCopy, text)

    c_box_update(text)

