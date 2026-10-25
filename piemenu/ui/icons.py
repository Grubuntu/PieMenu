"""Icon-picker helpers for the preferences dialog.

`get_all_actions()` collects every FreeCAD action that carries an icon and
`get_icon_pie_menu()` turns a stored icon path back into an icon object. The
`on_button_icon_pie_menu()` / `on_button_browse_icon()` handlers open the
"Choose Icon" popup, `on_icon_clicked()` applies the chosen icon and
`window_icons_close()` tears the popup down.

The widgets and callbacks below are created by `pieMenuStart()` after this
module is imported, so they are declared as module attributes here and
published by `pieMenuStart()` through `publish()`.
"""

from functools import partial

import FreeCAD as App
import FreeCADGui as Gui
from PySide import QtCore, QtGui
from PySide.QtWidgets import QFileDialog

from piemenu import config, constants, resources
from piemenu.config import get_index_list, get_param_index
from piemenu.ui.tool_list import tool_list


def translate(context, text):
    """Translate a string with the FreeCAD Qt translator."""
    return App.Qt.translate(context, text)


# Widgets and callbacks created by `pieMenuStart()` and injected via `publish()`.
button_icon_pie_menu = None
c_box = None
grid_layout = None
on_pie_change = None
pie_menu_dialog = None
update_icons_pie_menus = None
window_icons = None


def publish(**references):
    """Publish the runtime references used by the icon helpers."""
    globals().update(references)


def get_all_actions():
    """ Return the list of all Freecad's action with an icon """
    all_actions = Gui.getMainWindow().findChildren(QtGui.QAction)
    action_list = []

    for action in all_actions:
        icon = action.icon()
        if not icon.isNull() and action.data() is not None and action not in action_list:
            action_list.append(action)
    return action_list

def get_icon_pie_menu(iconPath=""):
    """ Return icon object corresponding to iconPath  through all actions """
    iconAction = iconPath
    action_list = get_all_actions()

    if iconPath == "":
        iconAction = resources.iconPieMenuLogo
    else:
        for action in action_list:
            if action.data() == iconPath:
                iconAction = action.icon()
    return iconAction

def on_icon_clicked(objIcon):
    """ Set icon to the PieMenu """
    indexList = get_index_list()
    for i in indexList:
        pieName = get_param_index(str(i))
        if pieName == c_box.currentText():
            param = config.get_params()["index"].GetGroup(str(i))
            param.SetString(constants.PARAM_ICON_PATH, objIcon)

    commandName = 'PieMenu_' + c_box.currentText()
    all_actions = Gui.getMainWindow().findChildren(QtGui.QAction)

    for action in all_actions:
        if action.data() == commandName:
            icon = get_icon_pie_menu(objIcon)
            action.setIcon(QtGui.QIcon(icon))

    window_icons.close()
    update_icons_pie_menus()
    tool_list()
    on_pie_change()

def on_button_browse_icon():
    """ Open dialog to browse files to choose an icon """
    window_icons.close()
    file_path, _ = QFileDialog.getOpenFileName(
        None, "Choose Icon", "", "SVG Files (*.svg);;ICO Files (*.ico);;All files (*.*)")

    if file_path:
        indexList = get_index_list()
        for i in indexList:
            pieName = get_param_index(str(i))
            if pieName == c_box.currentText():
                param = config.get_params()["index"].GetGroup(str(i))
                param.SetString(constants.PARAM_ICON_PATH, file_path)
                button_icon_pie_menu.setIcon(QtGui.QIcon(file_path))

        globaltoolbar = App.ParamGet(
            'User parameter:BaseApp/Workbench/Global/Toolbar/Custom_PieMenu')
        globaltoolbar.SetString('PieMenu_' + pieName, 'FreeCAD')

        update_icons_pie_menus()
        tool_list()
        on_pie_change()
        pie_menu_dialog.show()

def on_button_icon_pie_menu():
    """ Create and show the list of available icons for PieMenu icon """
    row, col = 0, 0
    icons_list = get_all_actions()

    # add default icon PieMenuLogo at beginning of the list
    buttonIcon = QtGui.QToolButton()
    buttonIcon.setIcon(QtGui.QIcon(resources.iconPieMenuLogo))
    buttonIcon.setIconSize(QtCore.QSize(24, 24))
    buttonIcon.setObjectName("styleButtonMenu")
    buttonIcon.setToolTip("Default PieMenuLogo")
    grid_layout.addWidget(buttonIcon, row, col)
    buttonIcon.clicked.connect(partial(on_icon_clicked, resources.iconPieMenuLogo))
    col += 1

    for action in icons_list:
        if action.data() is not None and isinstance(action.data(), str):
            buttonIcon = QtGui.QToolButton()
            buttonIcon.setIcon(QtGui.QIcon(action.icon()))
            buttonIcon.setIconSize(QtCore.QSize(24, 24))
            buttonIcon.setObjectName("styleButtonMenu")
            buttonIcon.setToolTip(action.data())
            grid_layout.addWidget(buttonIcon, row, col)
            buttonIcon.clicked.connect(
                partial(on_icon_clicked, action.data()))
            col += 1
            if col >= 8:
                col = 0
                row += 1

    window_icons.setParent(pie_menu_dialog)
    window_icons.setWindowTitle(translate("PieMenuTab", "Choose Icon"))
    window_icons.setWindowFlags(
        QtCore.Qt.Window | QtCore.Qt.WindowStaysOnTopHint | QtCore.Qt.X11BypassWindowManagerHint)

    window_icons.setWindowModality(QtCore.Qt.ApplicationModal)

    pieMenuDialogPos = pie_menu_dialog.pos()
    posX = pieMenuDialogPos.x() + pie_menu_dialog.width()/2 - pie_menu_dialog.width()/4
    posY = pieMenuDialogPos.y() + pie_menu_dialog.height()/3
    window_icons.setGeometry(
        posX, posY, pie_menu_dialog.width()/2, pie_menu_dialog.height()/2)
    window_icons.show()

def window_icons_close():
    """ Close the window and purge the grid """
    # grid purge is needed
    while grid_layout.count() > 0:
        item = grid_layout.takeAt(0)
        widget = item.widget()
        if widget is not None:
            widget.deleteLater()

    window_icons.close()
    pie_menu_dialog.show()

