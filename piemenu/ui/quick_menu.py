"""QuickMenu button builder.

`quick_menu()` builds the small button that opens the PieMenu quick popup
(global context toggle, PieMenu selection, toolbar menu and a shortcut to the
preferences dialog).

Some of the callbacks it wires are created by the `pieMenuStart()` bootstrap
*after* this module is imported. They are declared as module attributes here
and published by `pieMenuStart()` through `publish()`.
"""

from PySide import QtCore, QtGui

import FreeCADGui as Gui

from piemenu import config, constants
from piemenu.config import get_index_list, get_param, get_param_index
from piemenu.theme import get_style
from piemenu.workbench import get_gui_tool_button_data


def translate(context, text):
    """Translate a string with the FreeCAD Qt translator."""
    import FreeCAD as App
    return App.Qt.translate(context, text)


# Callbacks created by `pieMenuStart()` and injected through `publish()`.
create_pie = None
icon_default = None
icon_size = None
on_context = None
on_control = None
on_display_spin_box = None
pie_menu_instance = None
radius_size = None


def publish(**references):
    """Publish the runtime references used by `quick_menu`."""
    globals().update(references)


def quick_menu(button_size=20):
    """Build and style the QuickMenu button."""

    def pieList():
        """Populate the menuPieMenu with actions based on user parameters."""
        indexList = get_index_list()
        menuPieMenu.clear()

        pieList = []
        shortlist = []
        for i in indexList:
            pieName = get_param_index(str(i))
            pieList.append(pieName)
            param = config.get_params()["index"].GetGroup(str(i))
            shortcut = param.GetString(constants.PARAM_SHORTCUT_KEY)
            shortlist.append(shortcut)
        if not config.get_params()["main"].GetBool(constants.PARAM_TOOL_BAR):
            text = get_param(constants.PARAM_CURRENT_PIE)
        else:
            text = None

        for i, pieName in enumerate(pieList):
            action = QtGui.QAction(pieGroup)
            if i < len(shortlist):
                shortcut = shortlist[i]
                action.setText(f"{pieName}")
                action.setShortcut(QtGui.QKeySequence(shortcut))
                action.setCheckable(True)
                if pieName == text:
                    action.setChecked(True)
                    # Add icon in front of default PieMenu in Quickmenu list
                    action.setIcon(icon_default)
            else:
                pass
            menuPieMenu.addAction(action)

    def onPieGroup():
        """Handle the default pieMenu selection event in quick_menu."""
        config.get_params()["main"].SetBool(constants.PARAM_TOOL_BAR, False)
        config.get_params()["main"].RemString(constants.PARAM_TOOL_BAR)
        try:
            text = pieGroup.checkedAction().text()
            config.get_params()["main"].SetString(constants.PARAM_CURRENT_PIE, text)
        except TypeError:
            text = pieGroup.checkedAction().text()
            config.get_params()["main"].SetString(constants.PARAM_CURRENT_PIE, text)
        pie_menu_instance.hide()
        pie_menu_instance.showAtMouseInstance()

    def onMenuToolBar():
        """Handle the toolbar menu setup event."""
        menuToolBar.clear()
        if config.get_params()["main"].GetBool(constants.PARAM_TOOL_BAR):
            text = config.get_params()["main"].GetString(constants.PARAM_TOOL_BAR)
            if ": " in text:
                toolbar_desc = text.split(": ")
                text = toolbar_desc[1]
            else:
                pass
        else:
            text = None
        for i in mw.findChildren(QtGui.QToolBar):
            commands = []
            for a in i.findChildren(QtGui.QToolButton):
                try:
                    if not a.defaultAction().isSeparator():
                        commands.append(a.defaultAction())
                    else:
                        pass
                except AttributeError:
                    pass
            if len(commands) != 0:
                menu = QtGui.QMenu(i.windowTitle())
                menu.aboutToShow.connect(lambda sender=menu:
                                         onMenuToolbarGroup(sender))
                menuToolBar.addMenu(menu)
            else:
                pass

    def isActualPie(text):
        """Check if the given text corresponds to the current toolbar (or menu)."""
        if config.get_params()["main"].GetBool(constants.PARAM_TOOL_BAR):
            entry = config.get_params()["main"].GetString(constants.PARAM_TOOL_BAR)
            if ": " in entry:
                toolbar_desc = entry.split(": ")
                idMenu = toolbar_desc[1]
            else:
                idMenu = entry
            if idMenu == text:
                return True
        return False

    def onMenuToolbarGroup(sender):
        """Handle the toolbar menu group setup event."""
        if not sender.actions():
            action = QtGui.QAction(sender)
            action.setText("Show")
            action.setData(sender.title())
            action.setCheckable(True)
            if isActualPie(sender.title()):
                action.setChecked(True)
            sender.addAction(action)
            action = QtGui.QAction(sender)
            action.setText("Save")
            action.setData(sender.title())
            sender.addAction(action)
            sender.triggered.connect(lambda sender: onToolbarGroup(sender))

    def onToolbarGroup(sender):
        """Handle actions triggered in response to a toolbar menu."""
        if sender.text() == "Show":
            config.get_params()["main"].SetBool(constants.PARAM_TOOL_BAR, True)
        elif sender.text() == "Save":
            newPieGroup = create_pie(sender.data())
        else:
            return
        workbenches = []
        commands = []
        if sender.text() == "Save":
            # write persistent commands
            get_gui_tool_button_data(sender.data(), None, commands, None)
            newPieGroup.SetString(constants.PARAM_TOOL_LIST, ".,.".join(commands))
            newPieGroup.SetString(constants.PARAM_SHAPE, "Pie")
        elif sender.text() == "Show":
            # write persistent toolbar and its workbenches
            get_gui_tool_button_data(sender.data(), None, None, workbenches)
            toolbar_desc = ", ".join(workbenches)
            toolbar_desc = toolbar_desc + ': ' + sender.data()
            config.get_params()["main"].SetString(constants.PARAM_TOOL_BAR, toolbar_desc)
            pie_menu_instance.hide()
            pie_menu_instance.showAtMouseInstance()

    def onPrefButton():
        """Handle the preferences button event."""
        pie_menu_instance.hide()
        on_control()

    #### QuickMenu ####
    mw = Gui.getMainWindow()
    styleCurrentTheme = get_style()

    menu = QtGui.QMenu(mw)
    menu.setObjectName("styleQuickMenu")
    menu.setStyleSheet(styleCurrentTheme)

    actionContext = QtGui.QAction(menu)
    actionContext.setText(translate("QuickMenu", "Global context"))
    actionContext.setCheckable(True)
    actionContext.setChecked(config.get_params()["main"].GetBool(constants.PARAM_ENABLE_CONTEXT))
    actionContext.triggered.connect(lambda checked: on_context(checked))

    actionDisplaySpinBox = QtGui.QAction(menu)
    actionDisplaySpinBox.setText(translate("QuickMenu", "Direct SpinBox display"))
    actionDisplaySpinBox.setCheckable(True)
    actionDisplaySpinBox.setChecked(config.get_params()["main"].GetBool(constants.PARAM_DISPLAY_SPIN_BOX))
    actionDisplaySpinBox.triggered.connect(lambda checked: on_display_spin_box(checked))

    menuPieMenu = QtGui.QMenu()
    menuPieMenu.setTitle(translate("QuickMenu", "PieMenu"))
    menuPieMenu.aboutToShow.connect(pieList)

    pieGroup = QtGui.QActionGroup(menu)
    pieGroup.setExclusive(True)
    pieGroup.triggered.connect(onPieGroup)

    menuToolBar = QtGui.QMenu()
    menuToolBar.setObjectName("styleQuickMenuItem")
    menuToolBar.setTitle(translate("QuickMenu", constants.PARAM_TOOL_BAR))
    menuToolBar.setStyleSheet(styleCurrentTheme)
    menuToolBar.aboutToShow.connect(onMenuToolBar)

    toolbarGroup = QtGui.QMenu()
    toolbarGroupOps = QtGui.QActionGroup(toolbarGroup)
    toolbarGroupOps.setExclusive(True)
    toolbarGroup.triggered.connect(onToolbarGroup)

    prefAction = QtGui.QAction(menu)
    prefAction.setText(translate("QuickMenu", "Preferences"))
    prefAction.triggered.connect(onPrefButton)

    menu.addAction(actionContext)
    menu.addAction(actionDisplaySpinBox)
    menu.addSeparator()
    menu.addMenu(menuPieMenu)
    menu.addMenu(menuToolBar)
    menu.addSeparator()
    menu.addAction(prefAction)

    icon = icon_size(button_size)
    radius = radius_size(button_size)

    button = QtGui.QToolButton()
    button.setObjectName("styleButtonMenu")
    button.setMenu(menu)
    button.setProperty("ButtonX", 0)  # +, right
    button.setProperty("ButtonY", 32)  # +, down
    button.setGeometry(0, 0, button_size, button_size)
    button.setIconSize(QtCore.QSize(icon, icon))
    button.setStyleSheet(styleCurrentTheme + radius)
    button.setPopupMode(QtGui.QToolButton.ToolButtonPopupMode.InstantPopup)
    return button

