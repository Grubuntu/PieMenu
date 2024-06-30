# PieMenu widget for FreeCAD

# Copyright (C) 2024 Grubuntu, Pgilfernandez, hasecilu @ FreeCAD
# Copyright (C) 2022, 2023 mdkus @ FreeCAD
# Copyright (C) 2016, 2017 triplus @ FreeCAD
# Copyright (C) 2015,2016 looo @ FreeCAD
# Copyright (C) 2015 microelly <microelly2@freecadbuch.de>
#
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301 USA

# Attribution:
# http://forum.freecadweb.org/
# http://www.freecadweb.org/wiki/index.php?title=Code_snippets
#

global PIE_MENU_VERSION
PIE_MENU_VERSION = "1.7.3"

def pieMenuStart():
    """Main function that starts the Pie Menu."""
    import os
    import math
    import operator
    import platform
    import FreeCAD as App
    import FreeCADGui as Gui
    import PieMenuLocator as locator
    from TranslateUtils import translate
    from FreeCAD import Units
    from PySide import QtCore, QtGui, QtWidgets
    from PySide.QtWidgets import QApplication, QCheckBox, QComboBox, QDialog, QFileDialog, \
                QGroupBox, QHBoxLayout, QLabel, QLineEdit, QListWidget, QListWidgetItem, \
                QMessageBox, QPushButton, QVBoxLayout, QWidget
    from PySide.QtGui import QKeyEvent, QFontMetrics, QKeySequence, QAction, QShortcut, QTransform
    from PySide.QtCore import QPoint, QSize, Qt


    # global variables
    path = locator.path()
    respath = path + "/Resources/icons/"
    respath = respath.replace("\\", "/")
    stylepath = path + "/Resources/Stylesheets/"
    stylepath = stylepath.replace("\\", "/")
    transpath = path + "/Resources/translation/"
    transpath = transpath.replace("\\", "/")

    # Add translations path
    Gui.addLanguagePath(transpath)
    Gui.updateLocale()

    global shortcutKey
    global globalShortcutKey
    global shortcutList
    global flagVisi
    global triggerMode
    global hoverDelay
    global listCommands
    global listShortcutCode
    global flagShortcutOverride

    shortcutKey = ""
    globalShortcutKey = "TAB"
    shortcutList = []
    flagVisi = False
    triggerMode = "Press"
    hoverDelay = 100
    listCommands = []
    listShortcutCode = []
    flagShortcutOverride = False

    selectionTriggered = False
    contextPhase = False

    paramPath = "User parameter:BaseApp/PieMenu"
    paramIndexPath = "User parameter:BaseApp/PieMenu/Index"
    paramAccents = "User parameter:BaseApp/Preferences/Themes"
    paramColor = "User parameter:BaseApp/Preferences/View"
    paramGet = App.ParamGet(paramPath)
    paramIndexGet = App.ParamGet(paramIndexPath)
    paramAccentsGet = App.ParamGet(paramAccents)
    paramColorGet = App.ParamGet(paramColor)

    ## HACK: workaround to avoid ghosting : we find wbs already loaded,
    ## so as not to reload them again in the function 'updateCommands'
    global loadedWorkbenches
    paramLoadedWb = "User parameter:BaseApp/Preferences/General"
    paramWb = App.ParamGet(paramLoadedWb)
    loadedWorkbenches = paramWb.GetString("BackgroundAutoloadModules")
    loadedWorkbenches = loadedWorkbenches.split(",")

    iconMenu = respath + "PieMenuQuickMenu.svg"
    iconUp = respath + "PieMenuUp.svg"
    iconDown = respath + "PieMenuDown.svg"
    iconAdd = respath + "PieMenuAdd.svg"
    iconRemove = respath + "PieMenuRemove.svg"
    iconRename = respath + "PieMenuRename.svg"
    iconReset = respath + "PieMenuReload.svg"
    iconCopy = respath + "PieMenuCopy.svg"
    iconRemoveCommand = respath + "PieMenuRemoveCommand.svg"
    iconBackspace =  respath + "PieMenuBackspace.svg"
    iconInfo =  respath + "PieMenuInfo.svg"
    iconAddSeparator =  respath + "PieMenuAddSeparator.svg"
    iconSeparator =  respath + "PieMenuSeparator.svg"
    iconDocumentation = respath + "PieMenuDocumentation.svg"
    iconPieMenuLogo = respath + "PieMenu_Logo.svg"
    iconDefault = QtGui.QApplication.style().standardIcon(QtGui.QStyle.StandardPixmap.SP_DialogApplyButton)
    iconLeft = respath + "PieMenuLeft.svg"
    iconRight = respath + "PieMenuRight.svg"
    iconArrowDown = respath + "PieMenuArrowDown.svg"
    iconBlank = respath + "PieMenuBlank.svg"

    sign = {
        "<": operator.lt,
        "<=": operator.le,
        "==": operator.eq,
        "!=": operator.ne,
        ">": operator.gt,
        ">=": operator.ge,
        }

    touches_speciales = {'CTRL', 'ALT', 'SHIFT', 'META', 'TAB'}

    available_shape = [ "Pie", "RainbowUp", "RainbowDown", "Concentric", "Star", "UpDown", "LeftRight", \
                           "TableTop", "TableDown", "TableLeft", "TableRight" ]

    listSpinboxFeatures = [ '<PartDesign::Fillet>', '<PartDesign::Chamfer>', '<PartDesign::Thickness>', '<PartDesign::Pad>', '<PartDesign::Pocket>', '<PartDesign::Revolution>' ]

    # 3 defaults PieMenus on a fresh install
    defaultTools = ["Std_ViewTop",
                    "Std_New",
                    "Std_ViewRight",
                    "Std_BoxSelection",
                    "Std_ViewBottom",
                    "Std_ViewIsometric",
                    "Std_ViewLeft",
                    "Std_ViewScreenShot"]

    defaultToolsPartDesign = ["PartDesign_NewSketch",
                              "PartDesign_Pad",
                              "PartDesign_Pocket",
                              "PartDesign_Chamfer",
                              "PartDesign_Fillet"]

    defaultToolsSketcher =["Sketcher_CreatePolyline",
                           "Sketcher_CompCreateCircle",
                           "Sketcher_CreateRectangle",
                           "Sketcher_ToggleConstruction"]

    #### Classes definition ####
    class SelObserver:
        def addSelection(self, doc, obj, sub, pnt):
            # block listTopo as CTRL is press to allow multiple selection for context
            modifiers = QtGui.QApplication.keyboardModifiers()
            if not (modifiers & QtCore.Qt.ControlModifier):
                listTopo()

        def removeSelection(self, doc, obj, sub):
            # block listTopo as CTRL is press to allow multiple deselection for context
            modifiers = QtGui.QApplication.keyboardModifiers()
            if not (modifiers & QtCore.Qt.ControlModifier):
                listTopo()


    class CustomLineEdit(QLineEdit):
        """ get key event from box shortcut in settings """
        def __init__(self):
            super(CustomLineEdit, self).__init__()

        def keyPressEvent(self, event):
            key_text = QKeySequence(event.key()).toString()
            modifier_text = self.get_modifier_text(event.modifiers())

            # Tab key
            if event.key() == Qt.Key_Tab:
                self.setText("TAB")
                return

            elif event.key() in [Qt.Key_Backspace, Qt.Key_Delete]:
                if len(self.text()) > 0:
                    current_text = self.text()
                    if current_text and current_text[-1] == ',':
                        self.setText(current_text[:-1])
                    else:
                        self.setText(current_text[:-1])
                else:
                    self.setText('')

            elif modifier_text:
                if key_text and modifier_text:

                    shortcut_text = f"{modifier_text}+{key_text}"
                    self.setText(shortcut_text)

            elif key_text:
                if len(self.selectedText()) > 0:
                    self.setText(key_text)
                else:
                    if len(key_text) == 1 and len(self.text()) > 0:
                        last_char = self.text()[-1]
                        if last_char.isalpha():
                            self.setText(self.text() + ',' + key_text)
                        else:
                            self.setText(self.text() + key_text)
                    else:
                        self.setText(key_text)
            else:
                super().keyPressEvent(event)

            currentShortcut = self.text()
            shortcutsAssigned = getAssignedShortcut()
            compareAndDisplayWarning(shortcutsAssigned, currentShortcut)

        def get_modifier_text(self, modifiers):
            modifier_names = {
                Qt.ControlModifier: 'CTRL',
                Qt.AltModifier: 'ALT',
                Qt.ShiftModifier: 'SHIFT',
                Qt.MetaModifier: 'META',
                Qt.Key_Tab: 'TAB'
            }
            modifier_text = '+'.join([modifier_names[modifier] \
                for modifier in modifier_names if modifiers & modifier])
            return modifier_text


    class HoverButton(QtGui.QToolButton):
        """ Custom class : hover timer to avoid too fast triggering on hover mode """

        def __init__(self, parent=None):
            super(HoverButton, self).__init__()
            self.hoverTimer = QtCore.QTimer(self)
            self.hoverTimer.setSingleShot(True)
            self.hoverTimer.timeout.connect(self.onHoverTimeout)
            self.enterEventConnected = False
            self.isMouseOver = False
            self.leaveEvent = self.onLeaveEvent
            self.baseIcon = None
            self.hoverIcon = None

        def onHoverTimeout(self):
            """Handle hover timeout event."""
            global triggerMode
            mode = triggerMode
            if self.isMouseOver and self.defaultAction().isEnabled() and mode == "Hover":
                if not pieMenuDialog.isVisible():
                    PieMenuInstance.hide()
                    self.defaultAction().trigger()
                    module = None
                    try:
                        docName = App.ActiveDocument.Name
                        g = Gui.ActiveDocument.getInEdit()
                        module = g.Module
                    except:
                        pass
                    if (module is not None and module != 'SketcherGui'):
                        PieMenuInstance.showAtMouse()
            else:
                pass


        def onLeaveEvent(self, event):
            self.isMouseOver = False
            # set invisible icon for Preselect button on leave
            if self.baseIcon:
                self.setIcon(self.baseIcon)
                self.update()

        def enterEvent(self, event):
            global hoverDelay

            if not self.enterEventConnected:
                self.hoverTimer.start(hoverDelay)
                self.enterEventConnected = True
            self.hoverTimer.stop()
            self.hoverTimer.start(hoverDelay)
            self.isMouseOver = True

            # set a visible icon for Preselect button on hover
            if self.hoverIcon:
                self.setIcon(self.hoverIcon)
                self.update()

        def mouseReleaseEvent(self, event):
            if self.isMouseOver and self.defaultAction().isEnabled():
                if not pieMenuDialog.isVisible():
                    PieMenuInstance.hide()
                    mw.setFocus()
                    self.defaultAction().trigger()
                    module = None
                    try:
                        docName = App.ActiveDocument.Name
                        g = Gui.ActiveDocument.getInEdit()
                        module = g.Module
                        fonctionActive = g.Object

                        if (module is not None and module != 'SketcherGui' and str(fonctionActive) in listSpinboxFeatures):
                            PieMenuInstance.showAtMouse()
                    except:
                        pass
            else:
                pass

        def setBaseIcon(self, icon: QtGui.QIcon):
            self.baseIcon = icon
            self.setIcon(self.baseIcon)

        def setHoverIcon(self, icon: QtGui.QIcon):
            self.hoverIcon = icon
            # self.setIcon(self.hoverIcon)


    class PieMenuSeparator():
        """Class PieMenuSeparator"""
        def __init__(self):
            pass

        def GetResources(self):
            """Return a dictionary with data that will be used by the button or menu item."""
            return {'Pixmap' : iconAddSeparator, 'MenuText': translate('PieMenuTab', 'Separator'), 'ToolTip': translate('PieMenuTab', 'Separator for PieMenu ')}

        def Activated(self):
            """Run the following code when the command is activated (button press)."""
            pass

        def IsActive(self):
            """Return True when the command should be active or False when it should be disabled (greyed)."""
            return False


    class NestedPieMenu():
        """Class nested PieMenu """
        def __init__(self, keyValue, iconPath=None):
            self.keyValue = keyValue
            if iconPath == None:
                self.iconPath = getParameterGroup(self.keyValue, "String", "IconPath")
                if self.iconPath == "":
                    # default icon when noone
                    self.iconPath = iconPieMenuLogo
                else :
                    self.iconPath = getParameterGroup(self.keyValue, "String", "IconPath")
            else:
                self.iconPath = iconPath

        def GetResources(self):
            """Return a dictionary with data that will be used by the button or menu item."""
            return {'Pixmap' : self.iconPath, 'MenuText':'PieMenu '+ self.keyValue, 'ToolTip': 'Piemenu '+ self.keyValue}

        def Activated(self):
            """Run the following code when the command is activated (button press)."""
            PieMenuInstance.showAtMouse(self.keyValue, notKeyTriggered=False)

        def IsActive(self):
            """Return True when the command should be active or False when it should be disabled (greyed)."""
            return True

        def setIconPath(self, icon_path):
            """Set the icon path for the NestedPieMenu instance."""
            self.iconPath = icon_path


    #### Class PieMenu ####
    class PieMenu(QWidget):
        """ Main widget for PieMenu """
        mw = Gui.getMainWindow()
        event_filter_installed = False
        offset_x = 0
        offset_y = 0


        def __init__(self, parent=mw):
            super().__init__()
            self.double_spinbox = None
            styleCurrentTheme = getStyle()

            # timer for right click delay
            self.timer = QtCore.QTimer(self)
            self.timer.setSingleShot(True)
            self.timer.timeout.connect(self.show_menu)

            self.debounceTimer = QtCore.QTimer(self)
            self.debounceTimer.setSingleShot(True)
            self.debounceTimer.timeout.connect(self.install_filter)

            if not PieMenu.event_filter_installed:
                app = QtGui.QGuiApplication.instance() or QtGui.QApplication([])
                app.installEventFilter(self)
                PieMenu.event_filter_installed = True

            self.radius = 100
            self.buttons = []
            self.buttonSize = 32
            self.menu = QtGui.QMenu()

            self.menuSize = 0
            self.menu.setObjectName("styleContainer")
            self.menu.setStyleSheet(styleCurrentTheme)
            
            self.menu.setWindowFlags(QtCore.Qt.FramelessWindowHint | Qt.NoDropShadowWindowHint)
            self.menu.setAttribute(QtCore.Qt.WA_TranslucentBackground)

            if compositingManager:
                pass
            else:
                self.menu.setAttribute(QtCore.Qt.WA_PaintOnScreen)

        def stop_filter(self):
            app = QtGui.QGuiApplication.instance() or QtGui.QApplication([])
            app.removeEventFilter(self)

        def install_filter(self):
            app = QtGui.QGuiApplication.instance() or QtGui.QApplication([])
            app.installEventFilter(self)

        def show_menu(self):
            if self.menu.isVisible():
                self.menu.hide()
                for i in self.buttons:
                    i.hide()
            else:
                actionKey.trigger()

        def validation(self):
            docName = App.ActiveDocument.Name
            Gui.getDocument(docName).resetEdit()
            App.ActiveDocument.recompute()
            PieMenuInstance.hide()

        def cancel(self):
            docName = App.ActiveDocument.Name
            App.closeActiveTransaction(True)
            Gui.Control.closeDialog()
            App.getDocument(docName).recompute()
            Gui.getDocument(docName).resetEdit()
            PieMenuInstance.hide()

        def validButton(self, buttonSize=32):
            icon = iconSize(buttonSize)
            button = QtGui.QToolButton()
            button.setObjectName("styleComboValid")
            button.setProperty("ButtonX", -25)
            button.setProperty("ButtonY", 8)
            button.setGeometry(0, 0, buttonSize, buttonSize)
            button.setIconSize(QtCore.QSize(icon, icon))
            return button

        def cancelButton(self, buttonSize=32):
            icon = iconSize(buttonSize)
            button = QtGui.QToolButton()
            button.setObjectName("styleComboCancel")
            button.setProperty("ButtonX", 25)
            button.setProperty("ButtonY", 8)
            button.setGeometry(0, 0, buttonSize, buttonSize)
            button.setIconSize(QtCore.QSize(icon, icon))
            return button

        def doubleSpinbox(self, buttonSize=32, step=1.0):
            """ https://github.com/FreeCAD/FreeCAD/blob/main/src/Gui/QuantitySpinBox.h """
            ui = FreeCADGui.UiLoader()
            button = ui.createWidget("Gui::QuantitySpinBox")
            button.setProperty("minimum", 0.0)
            button.setFixedWidth(95)
            button.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
            button.setProperty("ButtonX", 0)
            button.setProperty("ButtonY", -30)
            button.setAttribute(QtCore.Qt.WA_TranslucentBackground)
            button.setStyleSheet(" QWidget { border-radius: 5px; }")
            button.setProperty("setSingleStep" , step)
            button.valueChanged.connect(self.spin_interactif)
            return button

        def checkboxThroughAll(self):
            checkboxThroughAll = QCheckBox(translate("Fast Spinbox", "Through all"))
            checkboxThroughAll.setCheckable(True)
            checkboxThroughAll.setProperty("ButtonX", 50)
            checkboxThroughAll.setProperty("ButtonY", -95)
            checkboxThroughAll.setAttribute(QtCore.Qt.WA_TranslucentBackground)
            return checkboxThroughAll

        def checkboxReversed(self):
            checkboxReversed = QCheckBox(translate("Fast Spinbox", "Reversed"))
            checkboxReversed.setCheckable(True)
            checkboxReversed.setProperty("ButtonX", 50)
            checkboxReversed.setProperty("ButtonY", -55)
            checkboxReversed.setAttribute(QtCore.Qt.WA_TranslucentBackground)
            return checkboxReversed

        def checkboxSymToPlane(self):
            checkboxSymToPlane = QCheckBox(translate("Fast Spinbox", "Symmetric to plane"))
            checkboxSymToPlane.setCheckable(True)
            checkboxSymToPlane.setProperty("ButtonX", 50)
            checkboxSymToPlane.setProperty("ButtonY", -75)
            checkboxSymToPlane.setAttribute(QtCore.Qt.WA_TranslucentBackground)
            return checkboxSymToPlane


        def eventFilter(self, obj, event):
            """Handle mouse and keyboard events """
            if event.type() == QtCore.QEvent.MouseButtonRelease:
                if event.button() == QtCore.Qt.LeftButton:
                    if self.menu.isActiveWindow():
                        pass
                    else:
                        self.menu.hide()
                        return False

            try:
                if checkboxRightClick.isChecked():
                    if event.type() == QtCore.QEvent.MouseButtonPress:
                        if event.button() == QtCore.Qt.RightButton:
                            self.timer.start(spinDelayRightClick.value())
                            return False

                    if event.type() == QtCore.QEvent.MouseButtonRelease:
                        if event.button() == QtCore.Qt.RightButton:
                            if self.timer.isActive():
                                self.timer.stop()
                                self.debounceTimer.start(100)
                                self.stop_filter()
                                return False
                            else:
                                return True
            except:
                None

            # Special case when shortcut is assigned to tool PieMenu AND also other there
            if event.type() == QtCore.QEvent.ShortcutOverride and self.menu.isVisible():
                # we need to set "flagShortcutOverride" to advertise that we go through Event.ShortcutOverride for this tool shortcut for the step "KeyRelease" below
                global flagShortcutOverride
                flagShortcutOverride = False

                key = event.key()
                event.accept()
                try:
                    # if fast spinbox is open, we do nothing with shortcuts
                    if self.double_spinbox.isVisible():
                        pass
                except:
                    # spinbox not show
                    try:
                        charKey = chr(key)
                    except:
                        charKey = ''

                    if charKey in listShortcutCode:
                        self.menu.hide()
                        for i in self.buttons:
                            i.hide()
                        j = 0
                        for i in listShortcutCode:
                            if i == charKey:
                                # set flag here
                                flagShortcutOverride = True
                            j+=1
                        return True

                    # Handle toggle mode for global shortcut###
                    elif checkboxGlobalKeyToggle.isChecked():
                        if event.key() == QtGui.QKeySequence(globalShortcutKey):
                            if self.menu.isVisible():
                                self.menu.hide()
                                for i in self.buttons:
                                    i.hide()
                                flagVisi = True
                                return True
                            else:
                                flagVisi = False
                                return False

                        for shortcut in mw.findChildren(QShortcut):
                            if event.key() == QtGui.QKeySequence(shortcut.key()):
                                if self.menu.isVisible():
                                    self.menu.hide()
                                    for i in self.buttons:
                                        i.hide()
                                    event.accept()
                                    flagVisi = True
                                    return True
                                else:
                                    flagVisi = False
                                    return False

            """ Handle keys Return and Enter for spinbox """
            if event.type() == QtCore.QEvent.KeyPress:
                key = event.key()
                #### Confirm with 'Enter' or 'Return' key ####
                if key == QtCore.Qt.Key_Enter or key == QtCore.Qt.Key_Return:
                    try:
                        if self.double_spinbox.isVisible():
                            self.validation()
                    except:
                        None
                    try:
                        if self.menu.isVisible():
                            self.validation()
                    except:
                        None
                        flagVisi = True
                        return True

                #### Keys SUPPR, DEL, UP and DOWN in Toollist ####
                """ Handle Keys SUPPR, DEL, UP and DOWN in Toollist """
                # move/delete only when 'tabs' is visible (not in ToolbarTab's settings)
                if tabs.isVisible():
                    if key == Qt.Key_Backspace or key == Qt.Key_Delete:
                        if buttonListWidget.hasFocus() == True:
                            onButtonRemoveCommand()
                            return True
                    if key == Qt.Key_Up:
                        if buttonListWidget.hasFocus() == True:
                            onButtonUp()
                            return True
                    if key == Qt.Key_Down:
                        if buttonListWidget.hasFocus() == True:
                            onButtonDown()
                            return True

            if event.type() == QtCore.QEvent.KeyRelease:
                """ Handle tool shortcut in PieMenu """
                if flagShortcutOverride :
                    key = event.key()
                    try:
                        # if fast spinbox is open, we do nothing with shortcuts
                        if self.double_spinbox.isVisible():
                            pass
                    except:
                        # spinbox not show
                        try:
                            charKey = chr(key)
                        except:
                            charKey = ''

                        if charKey in listShortcutCode:
                            self.menu.hide()
                            for i in self.buttons:
                                i.hide()
                            event.accept()
                            j = 0
                            for i in listShortcutCode:
                                if i == charKey:
                                    # trigger tool shortcut action
                                    listCommands[j].trigger()
                                    flagShortcutOverride = False
                                    module = None
                                    event.accept()
                                    try:
                                        docName = App.ActiveDocument.Name
                                        g = Gui.ActiveDocument.getInEdit()
                                        module = g.Module
                                        if (module is not None and module != 'SketcherGui'):
                                            PieMenuInstance.showAtMouse()
                                    except:
                                        pass
                                j+=1
                            return True

                if self.menu.isVisible() and flagShortcutOverride:
                    key = event.key()
                    try:
                        # if fast spinbox is open, we do nothing with shortcuts
                        if self.double_spinbox.isVisible():
                            pass
                    except:
                        # spinbox not show
                        try:
                            charKey = chr(key)
                        except:
                            charKey = ''

                        if charKey in listShortcutCode:
                            self.menu.hide()
                            for i in self.buttons:
                                i.hide()
                            event.accept()
                            j = 0
                            for i in listShortcutCode:
                                if i == charKey:
                                    # trigger tool shortcut action
                                    listCommands[j].trigger()
                                    module = None
                                    event.accept()
                                    try:
                                        docName = App.ActiveDocument.Name
                                        g = Gui.ActiveDocument.getInEdit()
                                        module = g.Module
                                        if (module is not None and module != 'SketcherGui'):
                                            PieMenuInstance.showAtMouse()
                                    except:
                                        pass
                                j+=1
                            return True
                # run listTopo (context) when CTRL is release: allow multiple selection
                if event.type() == QtCore.QEvent.KeyRelease and event.key() == QtCore.Qt.Key_Control:
                    enableContext = paramGet.GetBool("EnableContext")
                    if enableContext:
                        listTopo()

            elif event.type() == QtCore.QEvent.Wheel:
                """ Press CTRL + rotate Wheel = X10, Press SHIFT + rotate Wheel = X0.1, Press CTRL+SHIFT + rotate Wheel= X0.01 """
                modifiers = event.modifiers()
                if modifiers & QtCore.Qt.ControlModifier and modifiers & QtCore.Qt.ShiftModifier:
                    step = 0.001 # NOTE: weird behavior, you have to set 0.001 to modify the hundredths...
                elif modifiers & QtCore.Qt.ShiftModifier:
                    step = 0.1
                else:
                    step = 1.0
                try:
                    self.double_spinbox.setProperty("singleStep", step)
                except:
                    None
            return False


        def add_commands(self, commands, context=False, keyValue=None):
            """ Add commands to mieMenus """
            styleCurrentTheme = getStyle()
            try:
                docName = App.ActiveDocument.Name
                g = Gui.ActiveDocument.getInEdit()
                module = g.Module
                wb = Gui.activeWorkbench()
                wbName = wb.name()
            except:
                module = None

            for i in self.buttons:
                i.deleteLater()
            self.buttons = []
            group = ""

            if keyValue != None:
                indexList = getIndexList()
                for i in indexList:
                    a = str(i)
                    try:
                        pie = paramIndexGet.GetString(a).decode("UTF-8")
                    except AttributeError:
                        pie = paramIndexGet.GetString(a)

                    if pie == keyValue:
                        group = paramIndexGet.GetGroup(a)
                    else:
                        pass
            elif context:
                group = getGroup(mode=2)
            else:
                group = getGroup(mode=1)

            if len(commands) == 0:
                commandNumber = 1
            else:
                commandNumber = len(commands)

            self.offset_x = 0
            self.offset_y = 0

            # defaults values
            valueRadius = 100
            valueButton = 32
            shape = "Pie"
            num_per_row = 4
            icon_spacing = 8
            command_per_circle = 5
            shortcutLabelSize = "8"

            try:
                valueRadius = group.GetInt("Radius")
                valueButton = group.GetInt("Button")
                shape = getShape(keyValue)
                num_per_row = getParameterGroup(keyValue, "Int", "NumColumn")
                icon_spacing = getParameterGroup(keyValue, "Int", "IconSpacing")
                command_per_circle = getParameterGroup(keyValue, "Int", "CommandPerCircle")
                shortcutLabelSize = getParameterGroup(keyValue, "Int", "ShortcutLabelSize")
            except:
                None

            number_of_circle = 1
            buttonSize = valueButton

            if paramGet.GetBool("ToolBar") or keyValue == "toolBarTab":
                valueRadius = 100
                valueButton = 32
                shape = "Pie"

            if valueRadius:
                self.radius = valueRadius
            else:
                self.radius = 100

            if valueButton:
                self.buttonSize = valueButton
            else:
                self.buttonSize = 32

            buttonSize = self.buttonSize

            if num_per_row == 0:
                num_per_row = 1

            if icon_spacing < 0:
                icon_spacing = 0

            if shape == "Pie":
                if commandNumber == 1:
                    angle = 0
                    # buttonSize = self.buttonSize
                else:
                    angle = 2 * math.pi / commandNumber
                angleStart = 3 * math.pi / 2 - angle

            elif shape == "RainbowUp":
                if commandNumber == 1:
                    angle = 0
                    buttonSize = self.buttonSize
                else:
                    angle =  math.pi / (commandNumber-1)
                angleStart = 3 * math.pi / 2 - (angle*(commandNumber+1))/2

            elif shape == "RainbowDown":
                if commandNumber == 1:
                    angle = 0
                    buttonSize = self.buttonSize
                else:
                    angle =  math.pi / (commandNumber-1)
                angleStart =  math.pi / 2 - (angle*(commandNumber+1))/2

            elif shape == "Concentric" or shape == "Star" :
                angle = 2 * math.pi / (command_per_circle)
                angleStart = 3 * math.pi / 2 - angle

            else:
                angle = 2 * math.pi / commandNumber
                angleStart = 3 * math.pi / 2 - angle

            radius = radiusSize(buttonSize)
            icon = iconSize(buttonSize)

            if windowShadow:
                pass
            else:
                self.menuSize = valueRadius * 2 + buttonSize + 4
                if self.menuSize < 90:
                    self.menuSize = 90
                else:
                    pass
                self.menu.setMinimumWidth(self.menuSize)
                self.menu.setMinimumHeight(self.menuSize)

            displayCommandName = False
            displayPreselect = False
            enableShortcut = False
            displayShortcut = False
            if shape in ["Pie", "LeftRight"]:
                try: # get displayCommandName to display or not command name only for Pie shape
                    displayCommandName = getParameterGroup(keyValue, "Bool", "DisplayCommand")
                except:
                    None
            if shape in ["Pie", "RainbowUp", "RainbowDown"]:
                try: # get displayPreselect to display or not command name only for Pie shape
                    displayPreselect = getParameterGroup(keyValue, "Bool", "DisplayPreselect")
                except:
                    None

            try: # get enableShortcut to enable or not shortcut
                enableShortcut = getParameterGroup(keyValue, "Bool", "EnableShorcut")
            except:
                None
            try: # get displayShortcut to display or not shortcut
                displayShortcut = getParameterGroup(keyValue, "Bool", "DisplayShorcut")
            except:
                None

            showPie = False
            # handle case when not in edit mode or if  Sketcher is open
            try:
                if (Gui.ActiveDocument.getInEdit() is None) or (module == 'SketcherGui'):
                    showPie = True
            except:
                None

            # handle case when there is any document open
            try:
                # if there is any open document we throw exception, to set showPie to True to show PieMenu
                App.ActiveDocument.Name
            except:
                showPie = True

            if showPie:
                num = 1

                ### for Pie shape with commands names ###
                ecart = (2 * self.radius) / ((commandNumber)/2)
                Y = -self.radius - ecart
                X = 0
                X_shortcut = 0
                Y_shortcut = 0

                ### 48 = code ascii pour le chiffre 0 ###
                shortcutCode = 48
                global listCommands
                listCommands = []
                global listShortcutCode
                listShortcutCode = []

                def rotate_pixmap(pixmap, angle):
                    transform = QtGui.QTransform().rotate(angle)
                    return pixmap.transformed(transform, Qt.SmoothTransformation)

                for i in commands:
                    """ show PieMenu in Edit Feature and in Sketcher """
                    button = HoverButton()
                    button.setParent(self.menu)
                    button.setObjectName("pieMenu")
                    button.setAttribute(QtCore.Qt.WA_Hover)
                    button.setStyleSheet(styleCurrentTheme + radius)
                    button.setDefaultAction(commands[commands.index(i)])
                    button.setIconSize(QtCore.QSize(icon, icon))
                    button.setGeometry(0, 0, buttonSize, buttonSize)

                    # Preselection Arrow
                    buttonPreselect = HoverButton()

                    # modify style for display command name (only with Pie shape)
                    if displayCommandName and shape == "Pie":
                        # set minimum Y spacing at 1.2 * buttonSize
                        if ecart < (1.2 * buttonSize):
                            buttonSize = (ecart / 1.2)
                            radius = radiusSize(buttonSize)
                            icon = iconSize(buttonSize)

                        angle = (2 * math.pi) / (commandNumber)
                        button.setIcon(QtGui.QIcon())
                        # set padding and font size dependind on icon size
                        font_size = round(icon/2)

                        # get length of the string
                        text_length = QFontMetrics(button.font()).horizontalAdvance(
                            commands[commands.index(i)].text())

                        button.setGeometry(buttonSize, 0,  2 * buttonSize + text_length, buttonSize)
                        # layout for icon and command string
                        layout = QtGui.QHBoxLayout(button)
                        layout.setContentsMargins((icon/4), 0, 0, 0)

                        iconButton = QtGui.QIcon(commands[commands.index(i)].icon())
                        iconLabel = QtGui.QLabel()
                        iconLabel.setObjectName("iconLabel")
                        iconLabel.setPixmap(iconButton.pixmap(QtCore.QSize(icon, icon)))
                        iconMarging = ""
                        # right side
                        if (num) <= (commandNumber/2):
                            padding = "QToolButton#pieMenu {padding-left: " + str(icon) + "px; font-size: " + str(font_size) + "px;}"
                            Y += ecart
                            Y_shortcut = Y
                            if Y > self.radius:
                                Y = self.radius
                                Y_shortcut = Y
                            if num == 1:
                                X = 0
                                X_shortcut = 0
                                Y_shortcut = Y + icon
                            else:
                                X = self.radius * (math.cos(angle * num + angleStart)) + ( buttonSize + text_length/2)
                                padding = "QToolButton#pieMenu {padding-left: " + str(icon) + "px; font-size: " + str(font_size) + "px;}"
                                X_shortcut = ((self.radius) * (math.cos(angle * num + angleStart)) + ( buttonSize + text_length/2)) - (text_length/2 + 1.8*icon)
                                Y_shortcut = Y

                        # handle bottom right for odd commandNumber
                        elif (commandNumber % 2) == 1 and (num) == ((commandNumber+1)/2):
                            X = self.radius * (math.cos(angle * num + angleStart)) + ( buttonSize + text_length/2)
                            Y = self.radius - ecart/2
                            X_shortcut = (self.radius * (math.cos(angle * num + angleStart)) + ( buttonSize + text_length/2)) - (text_length/2 + 1.8*icon)
                            Y_shortcut = Y

                        # handle bottom left for odd commandNumber
                        elif (commandNumber % 2) == 1 and (num) == (((commandNumber+1)/2)+1):
                            X = self.radius * (math.cos(angle * num + angleStart)) - ( buttonSize + text_length/2)
                            Y = self.radius - ecart/2
                            layout.addStretch(1)
                            padding = "QToolButton#pieMenu {padding-right: " + str(icon) \
                            + "px; font-size: " + str(font_size) + "px;}"
                            iconMarging = "#iconLabel {margin-right: " + str(icon/4) + "px;}"
                            X_shortcut = (self.radius * (math.cos(angle * num + angleStart)) - ( buttonSize + text_length/2)) + (text_length/2 + 1.8*icon)
                            Y_shortcut = Y

                        # even commandNumber case, set the button on the middle bottom
                        elif (commandNumber % 2) == 0 and (num) == ((commandNumber/2)+1):
                            X = 0
                            Y = self.radius
                            X_shortcut = X
                            Y_shortcut = Y - icon

                        # left side
                        else:
                            Y -= ecart
                            if Y < -self.radius:
                                Y = -self.radius
                            X = self.radius * (math.cos(angle * num + angleStart)) - ( buttonSize + text_length/2)
                            layout.addStretch(1)
                            padding = "QToolButton#pieMenu {padding-right: " + str(icon) \
                            + "px; font-size: " + str(font_size) + "px;}"
                            iconMarging = "#iconLabel {margin-right: " + str(icon/4) + "px;}"
                            X_shortcut = (self.radius * (math.cos(angle * num + angleStart)) - (buttonSize + text_length/2)) + (text_length/2 + 1.8*icon)
                            Y_shortcut = Y

                        button.setProperty("ButtonX", X)
                        button.setProperty("ButtonY", Y)
                        
                        buttonPreselect.setProperty("ButtonX", (self.radius - 1 * buttonSize) *
                                           (math.cos(angle * num + angleStart)))
                        buttonPreselect.setProperty("ButtonY", (self.radius - 1 * buttonSize) *
                                           (math.sin(angle * num + angleStart)))

                        iconLabel.setStyleSheet(styleCurrentTheme + iconMarging)
                        button.setStyleSheet(styleCurrentTheme + radius + padding)
                        layout.addWidget(iconLabel)

                    elif shape == "TableTop":
                        ### Table  Top ###
                        num_of_line = math.ceil(commandNumber/num_per_row)
                        offset = num_of_line * (buttonSize + icon_spacing)
                        X = ((num-1) % num_per_row) * (buttonSize + icon_spacing)
                        Y = self.radius / 2 + ((num-1) // num_per_row) * (buttonSize + icon_spacing)
                        button.setProperty("ButtonX", X - ((num_per_row-1) * (buttonSize + icon_spacing)) / 2)
                        button.setProperty("ButtonY", -Y )

                        X_shortcut = (X - ((num_per_row-1) * (buttonSize + icon_spacing)) / 2) + icon/2
                        Y_shortcut = -Y + icon/2

                    elif shape == "TableDown":
                        ### Table Down  ###
                        num_of_line = math.ceil(commandNumber/num_per_row)
                        X = ((num-1) % num_per_row) * (buttonSize + icon_spacing)
                        Y = - buttonSize - self.radius / 4 - ((num-1) // num_per_row) * (buttonSize + icon_spacing)
                        button.setProperty("ButtonX", X - ((num_per_row-1) * (buttonSize + icon_spacing)) / 2)
                        button.setProperty("ButtonY", -Y )

                        X_shortcut = (X - ((num_per_row-1) * (buttonSize + icon_spacing)) / 2) + icon/2
                        Y_shortcut = -Y - icon/2

                    elif shape == "TableLeft":
                        ### Table Left  ###
                        num_of_line = math.ceil(commandNumber/num_per_row)
                        X = - buttonSize - self.radius / 2 -((num-1) // num_per_row) * (buttonSize + icon_spacing)
                        Y = ((num-1) % num_per_row) * (buttonSize + icon_spacing)
                        button.setProperty("ButtonX", X )
                        button.setProperty("ButtonY", Y - ((num_per_row-1) * (buttonSize + icon_spacing)) / 2)

                        X_shortcut = X + icon/2
                        Y_shortcut = Y - ((num_per_row-1) * (buttonSize + icon_spacing)) / 2 + icon/2

                    elif shape == "TableRight":
                        ### Table Right  ###
                        num_of_line = math.ceil(commandNumber/num_per_row)
                        X = buttonSize + self.radius / 2 + ((num-1) // num_per_row) * (buttonSize + icon_spacing)
                        Y = ((num-1) % num_per_row) * (buttonSize + icon_spacing)
                        button.setProperty("ButtonX", X )
                        button.setProperty("ButtonY", Y - ((num_per_row-1) * (buttonSize + icon_spacing)) / 2)

                        X_shortcut = X - icon/2
                        Y_shortcut = Y - ((num_per_row-1) * (buttonSize + icon_spacing)) / 2 + icon/2

                    elif shape == "UpDown":
                        ### Table Up and Down  ###
                        num_per_row = math.ceil(commandNumber / 2)
                        X = ((num - 1) % num_per_row) * (buttonSize + icon_spacing)
                        if ((num - 1) < num_per_row):
                            offset = 0
                            side = -1
                        else:
                            offset = 2 * self.radius
                            side = 1
                        Y = (self.radius - offset)

                        button.setProperty("ButtonX", X - ((num_per_row - 1) * (buttonSize + icon_spacing)) / 2)
                        button.setProperty("ButtonY", -Y)

                        X_shortcut = X - ((num_per_row - 1) * (buttonSize + icon_spacing)) / 2 + icon/2
                        Y_shortcut = -Y - (side * icon/2)

                    elif shape == "Concentric":
                        ### Concentric ###
                        button.setProperty("ButtonX", self.radius *
                                           (math.cos(angle * num + angleStart)))
                        button.setProperty("ButtonY", self.radius *
                                           (math.sin(angle * num + angleStart)))

                        X_shortcut = (self.radius) * (math.cos(angle * num + angleStart)) + icon/2
                        Y_shortcut = (self.radius) * (math.sin(angle * num + angleStart)) + icon/2

                        if ((num % command_per_circle) == 0) :
                            num = 0
                            self.radius = self.radius + buttonSize + icon_spacing
                            number_of_circle = number_of_circle + 1
                            command_per_circle = command_per_circle + command_per_circle
                            angle = 2 * math.pi / command_per_circle
                            angleStart = angleStart + angle/2

                    elif shape == "Star":
                        ### Star ###
                        button.setProperty("ButtonX", self.radius *
                                           (math.cos(angle * num + angleStart)))
                        button.setProperty("ButtonY", self.radius *
                                           (math.sin(angle * num + angleStart)))

                        X_shortcut = (self.radius) * (math.cos(angle * num + angleStart)) + icon/2
                        Y_shortcut = (self.radius) * (math.sin(angle * num + angleStart)) + icon/2

                        if ((num % command_per_circle) == 0) :
                            self.radius = self.radius + buttonSize + icon_spacing

                    elif shape == "LeftRight":
                        ### Left and Right with command names ###
                        if displayCommandName:
                            num_per_row = math.ceil(commandNumber/2)
                            button.setIcon(QtGui.QIcon())
                            # set padding and font size dependind on icon size
                            font_size = round(icon/2)
                            if ((num-1) < (num_per_row)):
                                # Left side icons
                                padding = "QToolButton#pieMenu {padding-right: " + str(icon) \
                                + "px; font-size: " + str(font_size) + "px;}"
                            else:
                                # Right side icons
                                padding = "QToolButton#pieMenu {padding-left: " + str(icon) \
                                + "px; font-size: " + str(font_size) + "px;}"
                            button.setStyleSheet(styleCurrentTheme + radius + padding)
                            # get length of the string
                            text_length = QFontMetrics(button.font()).horizontalAdvance(
                                commands[commands.index(i)].text())

                            button.setGeometry(buttonSize, 0,  2 * buttonSize + text_length, buttonSize)
                            # layout for icon and command string
                            layout = QtGui.QHBoxLayout(button)
                            layout.setContentsMargins((icon/4), 0, 0, 0)
                            if ((num-1) < (num_per_row)):
                                # Left side icons: align icon to the right and add some margin
                                layout.addStretch(1)
                                iconMarging = "#iconLabel {margin-right: " + str(icon/4) + "px;}"

                            iconButton = QtGui.QIcon(commands[commands.index(i)].icon())
                            iconLabel = QtGui.QLabel()
                            iconLabel.setObjectName("iconLabel")
                            iconLabel.setPixmap(iconButton.pixmap(QtCore.QSize(icon, icon)))
                            if ((num-1) < (num_per_row)):
                                # Left side icons
                                iconLabel.setStyleSheet(styleCurrentTheme + iconMarging)
                            else:
                                # Right side icons
                                iconLabel.setStyleSheet(styleCurrentTheme)
                            layout.addWidget(iconLabel)
                            Y = ((num -1) % num_per_row) * (buttonSize + icon_spacing)
                            if ((num-1) < (num_per_row)) :
                                # Left side icons
                                offset = - text_length
                                side = -1
                            else :
                                # Right side icons
                                offset = 2 * self.radius
                                side = 1
                            X = ( self.radius - offset - text_length/2  ) # TODO: align them to the left

                            button.setProperty("ButtonX", -X )
                            button.setProperty("ButtonY", Y - ((num_per_row - 1) * (buttonSize + icon_spacing)  ) / 2)

                            X_shortcut = side * (self.radius - buttonSize)
                            Y_shortcut = Y - ((num_per_row - 1) * (buttonSize + icon_spacing)  ) / 2 + icon/2

                        else:
                            ### Left and Right  ###
                            num_per_row = math.ceil(commandNumber/2)
                            Y = ((num -1) % num_per_row) * (buttonSize + icon_spacing)
                            if ((num-1) < (num_per_row)) :
                                offset = 0
                                side = -1
                            else :
                                offset = 2*self.radius
                                side = 1
                            X = (self.radius - offset )

                            button.setProperty("ButtonX", -X)
                            button.setProperty("ButtonY", Y - ((num_per_row - 1) * (buttonSize + icon_spacing)  ) / 2)

                            X_shortcut = -X - (side * icon/2)
                            Y_shortcut = Y - ((num_per_row - 1) * (buttonSize + icon_spacing)  ) / 2 + icon/2
                    else :
                        ### Pie without commands names / RainbowUp / RainbowDown   ###
                        button.setProperty("ButtonX", self.radius *
                                           (math.cos(angle * num + angleStart)))
                        button.setProperty("ButtonY", self.radius *
                                           (math.sin(angle * num + angleStart)))

                        X_shortcut = (self.radius) * (math.cos(angle * num + angleStart)) + icon/2
                        Y_shortcut = (self.radius) * (math.sin(angle * num + angleStart)) + icon/2

                        buttonPreselect.setProperty("ButtonX", (self.radius - 1 * buttonSize) * (math.cos(angle * num + angleStart)))
                        buttonPreselect.setProperty("ButtonY", (self.radius - 1 * buttonSize) * (math.sin(angle * num + angleStart)))

                    if displayPreselect:
                        buttonPreselect.setParent(self.menu)
                        buttonPreselect.setObjectName("stylebuttonPreselect")
                        buttonPreselect.setAttribute(QtCore.Qt.WA_Hover)
                        buttonPreselect.setStyleSheet(styleCurrentTheme)
                        buttonPreselect.setDefaultAction(commands[commands.index(i)])
                        buttonPreselect.setToolTip("")

                        angle_total = angle * num + angleStart + math.pi*3/2
                        sizeRound = buttonSize * (abs(math.sin(angle_total)) + abs(math.cos(angle_total)))

                        buttonPreselect.setIconSize(QtCore.QSize(sizeRound, sizeRound))
                        rotation_angle = math.degrees(angle * num + angleStart) + 270
                        buttonPreselect.originalPixmap = QtGui.QPixmap(iconArrowDown)
                        buttonPreselect.setGeometry(0, 0, sizeRound, sizeRound)

                        trans = QTransform()
                        trans.rotate(rotation_angle)
                        transformed_pixmap = buttonPreselect.originalPixmap.transformed(trans)

                        blankIcon = QtGui.QPixmap(iconBlank)
                        buttonPreselect.setBaseIcon(QtGui.QIcon(blankIcon))
                        buttonPreselect.setHoverIcon(QtGui.QIcon(transformed_pixmap))

                        self.buttons.append(buttonPreselect)

                    self.buttons.append(button)

                    #### Manage Separator ###
                    if (commands[commands.index(i)].text()) == translate('PieMenuTab', 'Separator'):
                        button.setObjectName("styleSeparator")
                        button.setIcon(QtGui.QIcon(iconSeparator))
                        iconButton = QtGui.QIcon(iconSeparator)
                        try:
                            iconLabel.setPixmap(iconButton.pixmap(QtCore.QSize(icon, icon)))
                        except:
                            None
                    else:
                        if enableShortcut:
                            if shortcutCode <= 90 :
                                # Add button label for Shortcuts Tools on PieMenu
                                shortcutLabel = HoverButton()
                                shortcutLabel.setParent(self.menu)
                                shortcutLabel.setObjectName("pieMenuShortcutTool")

                                fontSize = "QToolButton#pieMenuShortcutTool {font-size: " + str(shortcutLabelSize) + "px;}"

                                shortcutLabel.setStyleSheet(styleCurrentTheme + fontSize)
                                shortcutLabel.setDefaultAction(commands[commands.index(i)])
                                shortcutLabel.setToolButtonStyle(Qt.ToolButtonTextOnly)
                                shortcutLabel.setText(chr(shortcutCode))

                                listCommands.append(commands[commands.index(i)])
                                listShortcutCode.append(chr(shortcutCode))

                                if shortcutCode == 57:
                                    shortcutCode = 64
                                shortcutCode += 1
                                # trick to avoid X key which bug !
                                if shortcutCode == 88:
                                    shortcutCode = 89

                                shortcutLabel.setProperty("ButtonX", X_shortcut )
                                shortcutLabel.setProperty("ButtonY", Y_shortcut )

                                if displayShortcut:
                                    self.buttons.append(shortcutLabel)

                    num = num + 1

            buttonQuickMenu = quickMenu()
            if checkboxQuickMenu.checkState():
                buttonQuickMenu.setParent(self.menu)
                self.buttons.append(buttonQuickMenu)
            else:
                buttonQuickMenu.hide()

            try:
                if (Gui.ActiveDocument.getInEdit() == None):
                    buttonClose = closeButton()
                    buttonClose.setParent(self.menu)
                    self.buttons.append(buttonClose)
            except:
                None

            try:
                if (Gui.ActiveDocument.getInEdit() != None):
                    """ or show Valid and Cancel buttons in Edit Feature Only """
                    buttonValid = self.validButton()
                    buttonValid.setStyleSheet(styleCurrentTheme)
                    buttonValid.setParent(self.menu)
                    buttonValid.clicked.connect(self.validation)
                    self.buttons.append(buttonValid)

                    buttonCancel = self.cancelButton()
                    buttonCancel.setStyleSheet(styleCurrentTheme)
                    buttonCancel.setParent(self.menu)
                    buttonCancel.clicked.connect(self.cancel)
                    self.buttons.append(buttonCancel)

                    self.offset_x = 28
                    self.offset_y = 0

                    if (module != None and module != 'SketcherGui' and wbName == 'PartDesignWorkbench'):
                        """ Show Spinbox in Edit Feature in Part Design WB only """
                        layoutOptions = QtGui.QVBoxLayout()
                        fonctionActive = g.Object
                        featureName = g.Object.Name

                        self.double_spinbox = self.doubleSpinbox()
                        self.double_spinbox.setParent(self.menu)
                        self.double_spinbox.valueChanged.connect(self.spin_interactif)
                        self.buttons.append(self.double_spinbox)
                        self.double_spinbox.setVisible(True)

                        def checkbox_layout(checkbox_func, ObjectAttribute="Type", ObjectType=True):
                            checkbox = checkbox_func()
                            checkbox.setParent(self.menu)
                            checkbox.setObjectName("styleCheckbox")
                            checkbox.setStyleSheet(styleCurrentTheme)
                            checkbox.setMinimumWidth(220)
                            checkbox.stateChanged.connect(self.spin_interactif)

                            self.buttons.append(checkbox)

                            if getattr(g.Object, ObjectAttribute) == ObjectType:
                                checkbox.setChecked(True)
                            else:
                                checkbox.setChecked(False)
                            self.checkbox = checkbox
                            return self.checkbox

                        layoutMidPlane = QHBoxLayout()
                        layoutReversed = QHBoxLayout()
                        layoutThroughAll = QHBoxLayout()

                        if (str(fonctionActive) == '<PartDesign::Fillet>'):
                            FreeCADGui.ExpressionBinding(self.double_spinbox).bind(g.Object,"Radius")
                            quantity = Units.Quantity(Units.Quantity(g.Object.Radius).getUserPreferred()[0])

                        elif (str(fonctionActive) == '<PartDesign::Chamfer>'):
                            FreeCADGui.ExpressionBinding(self.double_spinbox).bind(g.Object,"Size")
                            quantity = Units.Quantity(Units.Quantity(g.Object.Size).getUserPreferred()[0])

                        elif (str(fonctionActive) == '<PartDesign::Thickness>'):
                            FreeCADGui.ExpressionBinding(self.double_spinbox).bind(g.Object,"Value")
                            quantity = Units.Quantity(Units.Quantity(g.Object.Value).getUserPreferred()[0])

                        elif (str(fonctionActive) == '<PartDesign::Pad>') or (str(fonctionActive) == '<PartDesign::Pocket>'):
                            FreeCADGui.ExpressionBinding(self.double_spinbox).bind(g.Object,"Length")
                            quantity = Units.Quantity(Units.Quantity(g.Object.Length).getUserPreferred()[0])

                            self.checkbox_midPlane = checkbox_layout(self.checkboxSymToPlane, "Midplane", True)
                            layoutMidPlane.addWidget(self.checkbox_midPlane)
                            layoutOptions.addLayout(layoutMidPlane)

                            self.checkbox_reversed = checkbox_layout(self.checkboxReversed, "Reversed", True)
                            layoutReversed.addWidget(self.checkbox_reversed)
                            layoutOptions.addLayout(layoutReversed)

                            if (str(fonctionActive) == '<PartDesign::Pocket>'):
                                self.checkbox_throughAll = checkbox_layout(self.checkboxThroughAll, "Type", "ThroughAll")

                                layoutThroughAll.addWidget(self.checkbox_throughAll)
                                layoutOptions.addLayout(layoutThroughAll)

                        elif (str(fonctionActive) == '<PartDesign::Revolution>') or (str(fonctionActive) == '<PartDesign::Groove>'):
                            FreeCADGui.ExpressionBinding(self.double_spinbox).bind(g.Object,"Angle")
                            quantity = Units.Quantity(Units.Quantity(g.Object.Angle).getUserPreferred()[0])

                            self.checkbox_midPlane = checkbox_layout(self.checkboxSymToPlane, "Midplane", True)
                            layoutMidPlane.addWidget(self.checkbox_midPlane)
                            layoutOptions.addLayout(layoutMidPlane)

                            self.checkbox_reversed = checkbox_layout(self.checkboxReversed, "Reversed", True)
                            layoutReversed.addWidget(self.checkbox_reversed)
                            layoutOptions.addLayout(layoutReversed)

                        else:
                            self.buttons.remove(double_spinbox)
                            # self.double_spinbox.setVisible(False)

                        self.double_spinbox.setProperty('value', quantity)

                        self.double_spinbox.setFocus()
                        self.double_spinbox.selectAll()

                        self.offset_x = 10
                        self.offset_y = 28
            except :
                None


            if compositingManager:
                pass
            else:
                for i in self.buttons:
                    i.setAttribute(QtCore.Qt.WA_PaintOnScreen)


        def hide(self):
            for i in self.buttons:
                i.hide()
            self.menu.hide()


        def showAtMouseInstance(self, keyValue=None, notKeyTriggered=False):
            nonlocal selectionTriggered
            nonlocal contextPhase

            enableContext = paramGet.GetBool("EnableContext")

            if contextPhase and keyValue==None:
                sel = Gui.Selection.getSelectionEx()
                if not sel:
                    self.hide()
                    contextPhase = False
                    updateCommands()
                elif not enableContext:
                    self.hide()
                    updateCommands()
                else:
                    updateCommands(keyValue, context=True)
            else:
                updateCommands(keyValue)

            if windowShadow:
                pos = mw.mapFromGlobal(QtGui.QCursor.pos())
                ## voir utilité du code suivant ?
                # if notKeyTriggered:
                    # if contextPhase:
                        # # special case treatment
                        # if selectionTriggered:
                            # selectionTriggered = False
                        # else:
                            # pos.setX(lastPosX)
                            # pos.setY(lastPosY)
                        # lastPosX = pos.x()
                        # lastPosY = pos.y()
                    # else:
                        # pos.setX(lastPosX)
                        # pos.setY(lastPosY)
                # else:
                    # lastPosX = pos.x()
                    # lastPosY = pos.y()

                self.menu.popup(QtCore.QPoint(mw.pos()))
                self.menu.setGeometry(mw.geometry())


                for i in self.buttons:
                    i.move(i.property("ButtonX") + pos.x() - i.width() / 2 + self.offset_x ,
                           i.property("ButtonY") + pos.y() - i.height() / 2 + self.offset_y)

                    i.setVisible(True)

                for i in self.buttons:
                    i.repaint()
            else:
                pos = QtGui.QCursor.pos()

                ## voir utilité du code suivant ?

                # if notKeyTriggered:
                    # if contextPhase:
                        # # special case treatment
                        # if selectionTriggered:
                            # selectionTriggered = False
                        # else:
                            # pos.setX(lastPosX)
                            # pos.setY(lastPosY)
                        # lastPosX = pos.x()
                        # lastPosY = pos.y()
                    # else:
                        # pos.setX(lastPosX)
                        # pos.setY(lastPosY)
                # else:
                    # lastPosX = pos.x()
                    # lastPosY = pos.y()

                for i in self.buttons:
                    i.move(i.property("ButtonX")
                          + (self.menuSize - i.size().width()) / 2 + self.offset_x,
                          i.property("ButtonY")
                          + (self.menuSize - i.size().height()) / 2 + self.offset_y)

                    i.setVisible(True)

                self.menu.popup(QtCore.QPoint(pos.x() - self.menuSize / 2, pos.y() - self.menuSize / 2))


        def showPiemenuPreview(self, keyValue=None, notKeyTriggered=False):
            """ Preview of PieMenu in widgetTable on Preferences Tab """
            # get BackgroundColor value in parameters, if 0 then we have a fresh install
            backgroundColorConfig = paramColorGet.GetUnsigned("BackgroundColor")
            cssColorTop = getCssColor(paramColorGet, "BackgroundColor2")
            cssColorBottom = getCssColor(paramColorGet, "BackgroundColor3")
            gradient = True
            useBackgroundColorMid = False

            if backgroundColorConfig != 0:
                gradient = paramColorGet.GetBool("Gradient")
                radialGradient = paramColorGet.GetBool("RadialGradient")
                useBackgroundColorMid = paramColorGet.GetBool("UseBackgroundColorMid")
                cssColorSimple = getCssColor(paramColorGet, "BackgroundColor")
                cssColorMiddle = getCssColor(paramColorGet, "BackgroundColor4")

            if gradient:
                if useBackgroundColorMid:
                    showPreviewWidget.setStyleSheet(f"background-color: qlineargradient(y1: 0, y2: 1, stop: 0 {cssColorTop}, stop: 0.5 {cssColorMiddle}, stop: 1 {cssColorBottom});")
                else:
                    showPreviewWidget.setStyleSheet(f"background-color: qlineargradient(y1: 0, y2: 1, stop: 0 {cssColorTop}, stop: 1 {cssColorBottom})")

            elif radialGradient:
                if useBackgroundColorMid:
                    showPreviewWidget.setStyleSheet(f"background-color: qradialgradient(cx: 0.5, cy: 0.5, radius: 0.5, fx: 0.5, fy: 0.5, stop: 0 {cssColorTop}, stop: 0.5 {cssColorMiddle}, stop: 1 {cssColorBottom});")
                else:
                    showPreviewWidget.setStyleSheet(f"background-color: qradialgradient(cx: 0.5, cy: 0.5, radius: 0.5, fx: 0.5, fy: 0.5, stop: 0 {cssColorTop}, stop: 1 {cssColorBottom});")
            else:
                # color simple :
                showPreviewWidget.setStyleSheet(f"background-color: {cssColorSimple};")

            group = getGroup(mode=1)
            valueRadius = group.GetInt("Radius")
            valueButton = group.GetInt("Button")
            iconSpacing = group.GetInt("IconSpacing")
            shape = getParameterGroup(cBox.currentText(), "String", "Shape")

            # positions of PieMenu in widget
            height = showPiemenu.height()
            width = showPiemenu.width()
            posX = width / 2
            posY = height / 2

            if shape == "TableLeft":
                posX = width * 4 / 5

            if shape == "TableRight":
                posX = width / 5

            updateCommands(keyValue)

            if windowShadow:
                ## needed for tools shortcut
                self.menu.popup(QtCore.QPoint(mw.pos()))
                self.menu.hide()
                for i in self.buttons:
                    i.hide()

                for i in self.buttons:
                    i.move(i.property("ButtonX") + posX - i.width() / 2 + self.offset_x ,
                           i.property("ButtonY") + posY - i.height() / 2 + self.offset_y)
                    i.setVisible(True)
                    i.setAttribute(Qt.WA_Disabled, True)
                    i.setParent(showPiemenu)
                    # i.repaint()

                    # disable quickMenu and (central) closebutton
                    if i.objectName() == "styleButtonMenu" or i.objectName() == "styleMenuClose":
                        i.setEnabled(False)

            else:
                # a tester !
                for i in self.buttons:
                    i.move(i.property("ButtonX")
                          + (self.menuSize - i.size().width()) / 2 + self.offset_x,
                          i.property("ButtonY")
                          + (self.menuSize - i.size().height()) / 2 + self.offset_y)
                    i.setVisible(True)
                    i.setAttribute(Qt.WA_Disabled, True)
                    i.setParent(showPiemenu)

                    # disable quickMenu and (central) closebutton
                    if i.objectName() == "styleButtonMenu" or i.objectName() == "styleMenuClose":
                        i.setEnabled(False)

                self.menu.popup(QtCore.QPoint(posX - self.menuSize / 2, posY - self.menuSize / 2))


        def showAtMouse(self, keyValue=None, notKeyTriggered=False):
            global flagVisi

            if not flagVisi:
                self.showAtMouseInstance(keyValue, notKeyTriggered)
                flagVisi = False
            else:
                self.menu.hide()
                for i in self.buttons:
                    i.hide()
                flagVisi = False


        def spin_interactif(self):
            """ Handle spinbox in fast edit mode """
            docName = App.ActiveDocument.Name
            g = Gui.ActiveDocument.getInEdit()
            fonctionActive = g.Object
            featureName = g.Object.Name

            size = self.double_spinbox.property('value')

            featureThroughAll = 0
            featureReversed = 0
            featureSymToPlane = 0

            try:
                featureThroughAll = self.checkbox_throughAll.isChecked()
            except:
                None

            try:
                featureReversed = self.checkbox_reversed.isChecked()
            except:
                None

            try:
                featureSymToPlane = self.checkbox_midPlane.isChecked()
            except:
                None

            if (str(fonctionActive) == '<PartDesign::Fillet>'):
                App.getDocument(docName).getObject(featureName).Radius = size
            elif (str(fonctionActive) == '<PartDesign::Chamfer>'):
                App.getDocument(docName).getObject(featureName).Size = size

            elif (str(fonctionActive) == '<PartDesign::Pocket>') or (str(fonctionActive) == '<PartDesign::Pad>')\
            or (str(fonctionActive) == '<PartDesign::Revolution>') or (str(fonctionActive) == '<PartDesign::Groove>'):

                # reversed
                if featureReversed:
                    App.getDocument(docName).getObject(featureName).Reversed = 1
                else:
                    App.getDocument(docName).getObject(featureName).Reversed = 0

                # midplane
                if featureSymToPlane:
                    App.getDocument(docName).getObject(featureName).Midplane = 1
                else:
                    App.getDocument(docName).getObject(featureName).Midplane = 0

                if (str(fonctionActive) == '<PartDesign::Pocket>'):
                    # through all
                    if featureThroughAll:
                        self.double_spinbox.setEnabled(False)
                        App.getDocument(docName).getObject(featureName).Type = 1
                    else :
                        self.double_spinbox.setEnabled(True)
                        App.getDocument(docName).getObject(featureName).Type = 0
                        App.getDocument(docName).getObject(featureName).Length = size

                elif (str(fonctionActive) == '<PartDesign::Revolution>') or (str(fonctionActive) == '<PartDesign::Groove>'):
                    App.getDocument(docName).getObject(featureName).Angle = size
                else:
                    App.getDocument(docName).getObject(featureName).Length = size

            elif (str(fonctionActive) == '<PartDesign::Thickness>'):
                App.getDocument(docName).getObject(featureName).Value = size

            elif (str(fonctionActive) == '<PartDesign::Hole>'):
                self.double_spinbox.setVisible(False)
            else:
                self.double_spinbox.setVisible(False)

            App.ActiveDocument.recompute()
    #### END Class PieMenu ####


    class PieMenuDialog(QDialog):
        mw = Gui.getMainWindow()
        """ Class to handle PieMenuDialog events """
        def __init__(self, parent=None):

            super(PieMenuDialog, self).__init__(parent)

            self.setObjectName("PieMenuPreferences")
            self.setWindowTitle("PieMenu " + PIE_MENU_VERSION)
            self.closeEvent = self.customCloseEvent
            self.setWindowIcon(QtGui.QIcon(iconPieMenuLogo))
            self.setMinimumSize(1000, 680)
            self.setModal(True)


        def customCloseEvent(self, event):
            # Caught close event to save parameters on disk
            App.saveParameter()
            super(PieMenuDialog, self).closeEvent(event)
            onBackToSettings()

    #### END Classes definitions ####


    ### BEGIN Functions Def ####
    def addAccessoriesMenu():
        if mw.property("eventLoop"):
            startAM = False
            try:
                mw.mainWindowClosed
                mw.workbenchActivated
                startAM = True
            except AttributeError:
                pass
            if startAM:
                t.stop()
                t.deleteLater()
                accessoriesMenu()


    def accessoriesMenu():
        """Add pie menu preferences to accessories menu."""
        pref = QtGui.QAction(mw)
        pref.setText(translate("AccesoriesMenu", "Pie menu settings"))
        pref.setObjectName("PieMenu")
        pref.triggered.connect(onControl)

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


    def getCssColor(user_parameter, key):
            color = user_parameter.GetUnsigned(key)
            hex_color = hex(color)[2:].zfill(8)
            rgb_hex_color = hex_color[:6]
            return f"#{rgb_hex_color}"


    def getStyle():
        theme = paramGet.GetString("Theme")
        if theme == "":
            theme = "Legacy" # default theme if new installation
        stylesheet_path = f"{stylepath}{theme}.qss"
        if not os.path.exists(stylesheet_path):
            stylesheet_path = f"{stylepath}Legacy.qss"
            paramGet.SetString("Theme", "Legacy")
        with open(stylesheet_path, "r") as f:
            styleCurrentTheme = f.read()
        styleCurrentTheme = styleCurrentTheme.replace("pieMenuQss:", stylepath)
        # Get FreeCAD ThemeAccentColors
        ThemeAccentColor1_hex = getCssColor(paramAccentsGet, "ThemeAccentColor1")
        ThemeAccentColor2_hex = getCssColor(paramAccentsGet, "ThemeAccentColor2")
        ThemeAccentColor3_hex = getCssColor(paramAccentsGet, "ThemeAccentColor3")
        styleCurrentTheme = styleCurrentTheme.replace("@ThemeAccentColor1", str(ThemeAccentColor1_hex))
        styleCurrentTheme = styleCurrentTheme.replace("@ThemeAccentColor2", str(ThemeAccentColor2_hex))
        styleCurrentTheme = styleCurrentTheme.replace("@ThemeAccentColor3", str(ThemeAccentColor3_hex))
        return styleCurrentTheme


    def getParameterGlobal(paramType="String", paramName=""):
        """Get parameter from user parameters."""
        if paramType == "String":
            parameter = paramGet.GetString(paramName)
        elif paramType == "Int":
            parameter = paramGet.GetInt(paramName)
        elif paramType == "Bool":
            parameter = paramGet.GetBool(paramName)
        else:
            pass
        return parameter


    def getParameterGroup(keyValue=None, paramType="String", paramName=""):
        """ paramType = "String", "Int", "Bool" """
        parameter = ""
        # group = getGroup()
        if keyValue == None:
            try:
                keyValue = paramGet.GetString("CurrentPie").decode("UTF-8")
            except AttributeError:
                keyValue = paramGet.GetString("CurrentPie")
        indexList = getIndexList()
        for i in indexList:
            try:
                pieName = paramIndexGet.GetString(str(i)).decode("UTF-8")
            except AttributeError:
                pieName = paramIndexGet.GetString(str(i))
            if pieName == keyValue:
                param = paramIndexGet.GetGroup(str(i))
                if paramType=="String":
                    parameter = param.GetString(paramName)
                elif paramType=="Int":
                    parameter = param.GetInt(paramName)
                elif paramType=="Bool":
                    parameter = param.GetBool(paramName)
                else:
                    pass
        return parameter


    def setParameterGroup(keyValue=None, paramType="String", paramName="", paramValue=None):
        """ set parameter """
        indexList = getIndexList()
        for i in indexList:
            a = str(i)
            try:
                pieName = paramIndexGet.GetString(a).decode("UTF-8")
            except AttributeError:
                pieName = paramIndexGet.GetString(a)
            if pieName == keyValue:
                param = paramIndexGet.GetGroup(str(i))
                if paramType=="String":
                    param.SetString(paramName, paramValue)
                elif paramType=="Int":
                    param.SetInt(paramName, paramValue)
                elif paramType=="Bool":
                    param.SetBool(paramName, paramValue)
                else:
                    pass


    def getIndexList():
        """Get current pieMenus using available index."""
        indexList = paramIndexGet.GetString("IndexList")
        if indexList:
            indexList = list(map(int, indexList.split(".,.")))
        else:
            indexList = []
        return indexList


    def getShortcutList():
        """Get keyboard shortcut and  namePie from user parameters"""
        global globalShortcutKey
        for shortcut in mw.findChildren(QShortcut):
            if shortcut.activated is not None:
                shortcut.activated.disconnect()
            shortcut.setParent(None)
            shortcut.deleteLater()
        shortcutList =[]

        indexList = getIndexList()
        for i in indexList:
            param = paramIndexGet.GetGroup(str(i))
            namePie = paramIndexGet.GetString(str(i))
            shortcutKey = param.GetString("ShortcutKey")
            if shortcutKey != "":
                shortcutList.append(f"PieMenu_{namePie} => {shortcutKey}")

        for result in shortcutList:
            namePie, shortcutKey = result.split(" => ")
            shortcut = QShortcut(QKeySequence(shortcutKey), mw)
            namePie = namePie.split("PieMenu_")[1]
            shortcut.activated.connect(lambda keyValue=namePie: \
                PieMenuInstance.showAtMouse(keyValue=keyValue, notKeyTriggered=False))
            shortcut.setEnabled(True)
        return shortcutList


    def setTriggerMode(triggerMode):
        """ Set TriggerMode in parameter """
        if triggerMode == "Press":
            spinHoverDelay.setEnabled(False)
        else:
            spinHoverDelay.setEnabled(True)
        indexList = getIndexList()
        for i in indexList:
            a = str(i)
            try:
                pieName = paramIndexGet.GetString(a).decode("UTF-8")
            except AttributeError:
                pieName = paramIndexGet.GetString(a)
            if pieName == cBox.currentText():
                param = paramIndexGet.GetGroup(str(i))
                param.SetString("TriggerMode", triggerMode)


    def setGlobalKeyToggle():
        """ Set globlal key toggle mode in parameters """
        globalKeyToggle = checkboxGlobalKeyToggle.isChecked()
        paramGet.SetBool("GlobalKeyToggle", globalKeyToggle)
        flagVisi = False
        actionKey.setEnabled(True)


    def reloadWorkbench():
        try:
            wb = Gui.activeWorkbench()
            # needed to change WB and reload it : do only Gui.reloadWorkbench() is not enough
            Gui.activateWorkbench('PartDesignWorkbench')
            Gui.activateWorkbench('PartWorkbench')
            Gui.activateWorkbench(wb.name())
            Gui.updateGui()
        except:
            pass


    def updateNestedPieMenus():
        indexList = getIndexList()
        for i in indexList:
            a = str(i)
            try:
                pie = paramIndexGet.GetString(a).decode("UTF-8")
            except AttributeError:
                pie = paramIndexGet.GetString(a)

            iconPath = getParameterGroup(pie, "String", "IconPath")
            if iconPath == "":
                iconPath = iconPieMenuLogo

            FreeCADGui.addCommand('Std_PieMenu_' + pie, NestedPieMenu(pie, iconPath))

            globaltoolbar = FreeCAD.ParamGet('User parameter:BaseApp/Workbench/Global/Toolbar/Custom_PieMenu')

            pieMenuTB = globaltoolbar.GetString('Name')
            if pieMenuTB == 'PieMenuTB':
                pass
            else:
                globaltoolbar.SetString('Name','PieMenuTB')

            globaltoolbar.SetString('Std_PieMenu_' + pie,'FreeCAD')


    def onListToolBar():
        """Handle the toolbar list."""
        listToolBar.clear()
        listToolBar.blockSignals(True)
        if paramGet.GetBool("ToolBar"):
            text = paramGet.GetString("ToolBar")
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
                getGuiToolButtonData(command.text(), None, commands, None)
                if len(commands) != 0:
                    listToolBar.addItem(item)

        listToolBar.blockSignals(False)
        return listToolBar


    def radiusSize(buttonSize):
        """Calculates border radius for QToolButton based on the given buttonSize."""
        radius = str(math.trunc(buttonSize / 2))
        return "QToolButton {border-radius: " + radius + "px}"


    def iconSize(buttonSize):
        """Calculates the size of an icon based on the given buttonSize."""
        icon = buttonSize / 3 * 2
        return icon


    def closeButton(buttonSize=32):
        """Style the close button."""
        icon = iconSize(buttonSize)
        radius = radiusSize(buttonSize)
        button = QtGui.QToolButton()
        button.setObjectName("styleMenuClose")
        button.setProperty("ButtonX", 0) # +, right
        button.setProperty("ButtonY", 0) # +, down
        button.setGeometry(0, 0, buttonSize, buttonSize)
        button.setIconSize(QtCore.QSize(icon, icon))
        styleCurrentTheme = getStyle()
        button.setStyleSheet(styleCurrentTheme + radius)
        button.setAttribute(QtCore.Qt.WA_TranslucentBackground)

        def onButton():
            PieMenuInstance.hide()

        button.clicked.connect(onButton)

        return button


    def contextList():
        contextAll.clear()
        indexList = getIndexList()
        for i in indexList:
            a = str(i)
            group = paramIndexGet.GetGroup(a)
            groupContext = group.GetGroup("Context")
            if groupContext.GetBool("Enabled"):
                current = {}
                current["Index"] = a
                current["VertexSign"] = groupContext.GetString("VertexSign")
                current["VertexValue"] = groupContext.GetInt("VertexValue")

                current["EdgeSign"] = groupContext.GetString("EdgeSign")
                current["EdgeValue"] = groupContext.GetInt("EdgeValue")

                current["FaceSign"] = groupContext.GetString("FaceSign")
                current["FaceValue"] = groupContext.GetInt("FaceValue")

                current["ObjectSign"] = groupContext.GetString("ObjectSign")
                current["ObjectValue"] = groupContext.GetInt("ObjectValue")
                contextAll[i] = current
            else:
                pass


    def getContextPie(v, e, f, o):
        global globalContextPie
        global globalIndexPie
        global indexPie
        globalContextPie = False
        globalIndexPie = None
        indexPie = None
        for i in contextAll:
            current = contextAll[i]
            def vertex():
                if sign[current["VertexSign"]](v, current["VertexValue"]):
                    edge()
                else:
                    pass
            def edge():
                if sign[current["EdgeSign"]](e, current["EdgeValue"]):
                    face()
                else:
                    pass
            def face():
                if sign[current["FaceSign"]](f, current["FaceValue"]):
                    obj()
                else:
                    pass
            def obj():
                if sign[current["ObjectSign"]](o, current["ObjectValue"]):
                    global globalContextPie
                    global globalIndexPie
                    global indexPie
                    # globalContextPie = "True"
                    globalIndexPie = current["Index"]

                    if globalIndexPie:
                        try:
                            pieName = paramIndexGet.GetString(globalIndexPie).decode("UTF-8")
                        except AttributeError:
                            pieName = paramIndexGet.GetString(globalIndexPie)
                        contextWorkbench = None
                        contextWorkbench = getParameterGroup(pieName, "String", "ContextWorkbench")
                        activeWB = Gui.activeWorkbench().name()
                        activeWB = activeWB.split("Workbench")

                        if contextWorkbench == activeWB[0] or contextWorkbench == translate("ContextTab", "All Workbenches"):
                            globalContextPie = "True"
                            indexPie = current["Index"]
                else:
                    pass
            vertex()

        if globalContextPie == "True":
            return indexPie
        else:
            return None


    def listTopo():
        """ Handle conditions to trigger context mode """
        enableContext = paramGet.GetBool("EnableContext")
        if enableContext:
            module = None
            try:
                docName = App.ActiveDocument.Name
                g = Gui.ActiveDocument.getInEdit()
                module = g.Module
            except:
                pass

            if module == None or module == "SketcherGui":
                nonlocal selectionTriggered
                nonlocal contextPhase
                sel = Gui.Selection.getSelectionEx()
                vertexes = 0
                edges = 0
                faces = 0
                objects = 0
                allList = []
                for i in sel:
                    if not i.SubElementNames:
                        objects = objects + 1
                    else:
                        for a in i.SubElementNames:
                            allList.append(a)
                for i in allList:
                    if i.startswith('Vertex') or i.startswith('RootPoint'):
                        vertexes = vertexes + 1
                    elif i.startswith('Edge'):
                        edges = edges + 1
                    elif i.startswith('Face'):
                        faces = faces + 1
                    else:
                        pass
                pieIndex = getContextPie(vertexes,
                                         edges,
                                         faces,
                                         objects)

                if pieIndex:
                    try:
                        pieName = paramIndexGet.GetString(pieIndex).decode("UTF-8")
                    except AttributeError:
                        pieName = paramIndexGet.GetString(pieIndex)
                    try:
                        paramGet.SetString("ContextPie", pieName.encode("UTF-8"))
                    except TypeError:
                        paramGet.SetString("ContextPie", pieName)
                    contextPhase = True

                    # updateCommands(keyValue=None, context=True)
                    PieMenuInstance.hide()

                    activeWB = Gui.activeWorkbench().name()
                    activeWB = activeWB.split("Workbench")
                    contextWorkbench = None
                    contextWorkbench = getParameterGroup(pieName, "String", "ContextWorkbench")

                    if contextWorkbench == activeWB[0] or contextWorkbench == None or contextWorkbench == translate("ContextTab", "All Workbenches"):
                        immediateTrigger = getParameterGroup(pieName, "Bool", "ImmediateTriggerContext")
                        if immediateTrigger:
                            selectionTriggered = True
                            PieMenuInstance.showAtMouse(notKeyTriggered=True)
                else:
                    pass


    def addObserver():
        if paramGet.GetBool("EnableContext"):
            Gui.Selection.addObserver(selObserver)
        else:
            Gui.Selection.removeObserver(selObserver)


    def getGuiActionMapAll():
        # WBs workaround 0.22.37436
        availableActions = {}
        duplicates = []

        wbContainer = mw.findChild(QtGui.QAction, "Std_Workbench")
        parentWbContainer = wbContainer.parent()
        wbGroup = parentWbContainer.findChild(QtGui.QActionGroup)
        for i in wbGroup.actions():
            if i.objectName() != "" and i.icon():
                availableActions[i.objectName()] = i
            else:
                pass

        for i in mw.findChildren(QtGui.QAction):
            if i.objectName() is not None:
                if i.objectName() != "" and i.icon():
                    if i.objectName() in availableActions:
                        pass
                    else:
                        availableActions[i.objectName()] = i
                else:
                    pass
            else:
                pass

        for d in duplicates:
            del availableActions[d]

        return availableActions


    def extractWorkbench(command):
        cmd_parts = command.split("_")
        if cmd_parts[0] == "":
            workbench = "None"
        else:
            workbench = cmd_parts[0]
        return workbench


    def getActionData(action, actions, commands, workbenches):
        if not action.icon():
            return
        if actions is not None:
            if action in actions:
                pass
            else:
                actions.append(action)
        if commands is None and workbenches is None:
            return
        command = action.objectName()
        if len(command) == 0:
            workbench = "None"
        else:
            if commands is not None:
                if command in commands:
                    pass
                else:
                    commands.append(command)
            workbench = extractWorkbench(command)
        if workbenches is not None:
            if workbench not in workbenches:
                workbenches.append(workbench)


    def getGuiToolButtonData(idToolBar, actions, commands, workbenches):
        actionMapAll = getGuiActionMapAll()
        for i in actionMapAll:
            action = actionMapAll[i]
            for widgets in action.associatedWidgets():
                if widgets.windowTitle() == idToolBar:
                    getActionData(action, actions, commands, workbenches)


    def actualizeWorkbenchActions(actions, toolList, actionMap):
        for i in toolList:
            # rule out special case: there has to be an entry
            if i == "":
                pass
            elif i in actionMap:
                # if actionMap[i] not in actions:
                actions.append(actionMap[i])
            else:
                cmd_parts = i.split("_")
                # rule out special case: unknown Std action
                if cmd_parts[0] == "Std":
                    pass
                else:
                    # treatment of special cases
                    # Fem workbench
                    if cmd_parts[0] == "FEM":
                        cmd_parts[0] = "Fem"
                    # Sheet Metal workbench
                    # Sheet Metal has changed its command name?
                    # if cmd_parts[0][:2] == "SM":
                    if cmd_parts[0] == "SheetMetal":
                        cmd_parts[0] = "SM"
                    # Assembly4 workbench
                    if cmd_parts[0][:4] == "Asm4":
                        cmd_parts[0] = "Assembly4"
                    try:
                        Gui.activateWorkbench(cmd_parts[0] + "Workbench")
                    except:
                        None
        return False


    def updateCommands(keyValue=None, context=False):
        indexList = getIndexList()
        # keyValue = None > Global shortcut
        # keyValue != None > Custom shortcut
        global triggerMode
        global hoverDelay

        if keyValue == None:
            # context
            if context:
                try:
                    text = paramGet.GetString("ContextPie").decode("UTF-8")
                except AttributeError:
                    text = paramGet.GetString("ContextPie")

            # workbench
            elif not paramGet.GetBool("ToolBar"):
                wb = Gui.activeWorkbench()
                wbName = wb.name()
                wbName = wbName.replace("Workbench", "")
                # workbench
                text =  getPieName(wbName)

                # current Pie
                if text == None:
                    try:
                        text = paramGet.GetString("CurrentPie").decode("UTF-8")
                    except AttributeError:
                        text = paramGet.GetString("CurrentPie")
            # else:
                # text = keyValue
                context = False

            # toolbar
            elif paramGet.GetBool("ToolBar"):
                toolbar = paramGet.GetString("ToolBar")
                text = None
                context = False
                if ": " in toolbar:
                    toolbar_desc = toolbar.split(": ")
                    toolbar = toolbar_desc[1]
                    workbenches = toolbar_desc[0]
                    workbenches = workbenches.split(", ")
                    lastWorkbench = Gui.activeWorkbench()
                    for i in workbenches:
                        # rule out special cases
                        if i == None or i == "Std":
                            # wb = Gui.activeWorkbench()
                            # workbenches = wb.name()
                            pass
                        else:
                            # match special cases
                            # Fem workbench
                            if i == "FEM":
                                i = "Fem"
                            # Sheet Metal workbench
                            # if i[:2] == "SM":
                            if i == "SheetMetal":
                                # i = i[:2]
                                i = "SM"
                            # Assembly4 workbench
                            if i == "Asm4":
                                i = "Assembly4"
                        if (i + "Workbench") not in loadedWorkbenches:
                            try:
                                Gui.activateWorkbench(i + "Workbench")
                            except:
                                None
                            loadedWorkbenches.append(i + "Workbench")
                    Gui.activateWorkbench(lastWorkbench.__class__.__name__)
                else:
                    pass
                context = False
                actions = []
                getGuiToolButtonData(toolbar, actions, None, None)

        # for toolbar preview in preferences settings
        elif keyValue == "toolBarTab":
            context = False
            text = False
            items = []
            commands = []

            for index in range(listToolBar.count()):
                items.append(listToolBar.item(index))
                if items[index].isSelected():
                    sender = listToolBar.item(index)
                    getGuiToolButtonData(sender.text(), None, commands, None)

            actions = []
            actionMapAll = getGuiActionMapAll()
            while actualizeWorkbenchActions(actions, commands, actionMapAll):
                actionMapAll = getGuiActionMapAll()
            else:
                pass
            PieMenuInstance.add_commands(actions, False, "toolBarTab")

        else:
            # custom shortcut
            text = keyValue
            context = False

        if text:
            toolList = None

            for i in indexList:
                a = str(i)
                try:
                    pie = paramIndexGet.GetString(a).decode("UTF-8")
                except AttributeError:
                    pie = paramIndexGet.GetString(a)
                if pie == text:
                    group = paramIndexGet.GetGroup(a)
                    toolList = group.GetString("ToolList")
                else:
                    pass

            if toolList:
                toolList = toolList.split(".,.")
            else:
                toolList = []

            actions = []

            actionMapAll = getGuiActionMapAll()
            lastWorkbench = Gui.activeWorkbench()
            while actualizeWorkbenchActions(actions, toolList, actionMapAll):
                actionMapAll = getGuiActionMapAll()
            else:
                pass
            Gui.activateWorkbench(lastWorkbench.__class__.__name__)

        else:
            pass

        triggerMode = getParameterGroup(text, "String", "TriggerMode")
        hoverDelay = getParameterGroup(text, "Int", "HoverDelay")

        if not keyValue == "toolBarTab":
            PieMenuInstance.add_commands(actions, context, text)


    def getGroup(mode=0):
        """
        Obtain the parameter group.
        When:
        mode = 0: read from comboBox at GUI
        mode = 1: read from CurrentPie parameter
        mode = 2: read from ContextPie parameter
        If it doesn't exists return default PieMenu group
        """
        indexList = getIndexList()
        if mode == 2:
            try:
                text = paramGet.GetString("ContextPie").decode("UTF-8")
            except AttributeError:
                text = paramGet.GetString("ContextPie")
        elif mode == 1:
            try:
                text = paramGet.GetString("CurrentPie").decode("UTF-8")
            except AttributeError:
                text = paramGet.GetString("CurrentPie")
        else:
            text = cBox.currentText()
        group = None

        # Iterate over the available groups on indexList
        # to find the group stored on `text` var
        for i in indexList:
            a = str(i)
            try:
                pie = paramIndexGet.GetString(a).decode("UTF-8")
            except AttributeError:
                pie = paramIndexGet.GetString(a)

            if pie == text:
                group = paramIndexGet.GetGroup(a)
            else:
                pass
        if group:
            # group was found, good
            pass
        else:
            # return the default PieMenu group
            if 0 in indexList:
                group = paramIndexGet.GetGroup("0")
            else:
                setDefaultPie()
                try:
                    updateCommands()
                except:
                    None
                group = paramIndexGet.GetGroup("0")

        return group


    def setTheme():
        comboBoxTheme.blockSignals(True)
        theme = comboBoxTheme.currentText()
        paramGet.SetString("Theme", theme)
        comboBoxTheme.blockSignals(False)
        try:
            if pieMenuDialog.isVisible():
                updatePiemenuPreview()
        except:
            None


    def getTheme():
        """ list all QSS files themes available """
        all_files = os.listdir(stylepath)
        qss_files = [file for file in all_files if file.endswith(".qss")]
        available_styles = [file[:-4] for file in qss_files]
        comboBoxTheme.blockSignals(True)
        comboBoxTheme.clear()
        comboBoxTheme.addItems(available_styles)

        theme = paramGet.GetString("Theme")
        index = comboBoxTheme.findText(theme)
        if index != -1:
            comboBoxTheme.setCurrentIndex(index)
        comboBoxTheme.blockSignals(False)


    def buttonList():
        group = getGroup()
        toolList = group.GetString("ToolList")
        if toolList:
            toolList = toolList.split(".,.")
        else:
            toolList = []
        actionMapAll = getGuiActionMapAll()

        workbenches = []
        lastWorkbench = Gui.activeWorkbench()
        for i in toolList:
            if i not in actionMapAll:
                # rule out special case: there has to be an entry
                if i == "":
                    pass
                else:
                    cmd_parts = i.split("_")
                    if cmd_parts[0] not in workbenches:
                        # rule out special case: unknown Std action
                        if cmd_parts[0] == "Std":
                            pass
                        else:
                            # treatment of special cases
                            # Fem workbench
                            if cmd_parts[0] == "FEM":
                                cmd_parts[0] = "Fem"
                            # Sheet Metal workbench
                            # if cmd_parts[0][:2] == "SM":
                            if cmd_parts[0] == "SheetMetal":
                                # cmd_parts[0] = cmd_parts[0][:2]
                                cmd_parts[0] = "SM"
                            # Assembly4 workbench
                            if cmd_parts[0][:4] == "Asm4":
                                cmd_parts[0] = "Assembly4"
                            try:
                                Gui.activateWorkbench(cmd_parts[0] + "Workbench")
                                workbenches.append(cmd_parts[0])
                            except:
                                None
                    else:
                        pass
            else:
                pass
        Gui.activateWorkbench(lastWorkbench.__class__.__name__)
        actionMapAll = getGuiActionMapAll()
        buttonListWidget.blockSignals(True)
        buttonListWidget.clearContents()
        buttonListWidget.setRowCount(0)

        shortcutCode = 48
        for i in toolList:
            if i in actionMapAll:

                rowPosition = buttonListWidget.rowCount()
                buttonListWidget.insertRow(rowPosition)

                actionItem = QtWidgets.QTableWidgetItem(actionMapAll[i].text().replace("&", ""))
                actionItem.setData(QtCore.Qt.UserRole, i)
                actionItem.setIcon(actionMapAll[i].icon())
                actionItem.setToolTip(actionMapAll[i].toolTip())
                # prevent user to write something in list
                actionItem.setFlags(QtCore.Qt.ItemIsEnabled)
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
                        buttonListWidget.setItem(rowPosition, 0, shortcutItem)

                    # trick to jump form key 9 to key A in ascii list
                    if shortcutCode == 57:
                        shortcutCode = 64
                    shortcutCode += 1
                    # trick to avoid X key, which bug !
                    if shortcutCode == 88:
                        shortcutCode = 89

                buttonListWidget.setItem(rowPosition, 1, actionItem)

        buttonListWidget.blockSignals(False)

        showPiemenu.hide()
        PieMenuInstance.showPiemenuPreview(keyValue=cBox.currentText(), notKeyTriggered=False)
        showPiemenu.show()


    def cBoxUpdate(index=None):
        try:
            currentPie = paramGet.GetString("CurrentPie").decode("UTF-8")
        except AttributeError:
            currentPie = paramGet.GetString("CurrentPie")

        pieList = []
        indexList = getIndexList()
        for i in indexList:
            a = str(i)
            try:
                pieList.append(paramIndexGet.GetString(a).decode("UTF-8"))
            except AttributeError:
                pieList.append(paramIndexGet.GetString(a))
        duplicates = []
        for i in pieList:
            if i == currentPie:
                pass
            else:
                duplicates.append(i)
        duplicates.append(currentPie)

        pieList = sorted(duplicates)
        pieList.reverse()

        cBox.blockSignals(True)
        cBox.clear()

        for i in pieList:
            cBox.insertItem(0, i)
        cBox.blockSignals(False)

        if index == None:
            index = 0
        else:
            index = cBox.findText(index)

        cBox.setCurrentIndex(index)
        onPieChange()


    def getAssignedShortcut():
        shortcutsAssigned = [f"{act.whatsThis()} => {act.shortcut().toString()}" \
            for act in Gui.getMainWindow().findChildren(QtGui.QAction) \
            if not act.shortcut().isEmpty() and act.whatsThis()]
        shortcutList = getShortcutList()
        shortcutsAssigned.extend(shortcutList)
        return shortcutsAssigned


    def compareAndDisplayWarning(shortcutsAssigned, currentShortcut):
        infoShortcut.setText('')
        for assignedShortcut in shortcutsAssigned:
            command, shortcut = assignedShortcut.split(" => ")
            if shortcut.replace(" ", "").lower() == currentShortcut.lower():
                infoShortcut.setText(f' Warning: {currentShortcut} is already assigned for {command}')
                break


    def updateShortcutKey(newShortcut):
        global shortcutKey
        if not newShortcut:
            shortcutKey = newShortcut
            setParameterGroup(cBox.currentText(), "String", "ShortcutKey", shortcutKey)
            labelShortcut.setText(translate("PieMenuTab", "Shortcut deleted! No shortcut assigned ") + shortcutKey)

        else:
            parties = set(newShortcut.replace(',', '+').split('+'))
            for partie in parties:
                if partie not in touches_speciales and len(partie) > 1:
                    labelShortcut.setText(
                        translate("PieMenuTab", "Invalid shortcut! Current shortcut: ") + shortcutKey)
                else :
                    shortcutKey = newShortcut
                    setParameterGroup(cBox.currentText(), "String", "ShortcutKey", shortcutKey)
                    labelShortcut.setText(translate("PieMenuTab", "New shortcut assigned: ") + shortcutKey)
        shortcutLineEdit.setText(shortcutKey)
        getShortcutList()


    def updateGlobalShortcutKey(newShortcut):
        global globalShortcutKey
        if not newShortcut:
            globalShortcutKey = newShortcut
            paramGet.SetString("GlobalShortcutKey", globalShortcutKey)
            labelGlobalShortcut.setText(translate("GlobalSettingsTab", \
                "Shortcut deleted ! No shortcut assigned ")\
                + globalShortcutKey)

        else:
            parties = set(newShortcut.replace(',', '+').split('+'))
            for partie in parties:
                if partie not in touches_speciales and len(partie) > 1:
                    labelGlobalShortcut.setText(translate("GlobalSettingsTab", \
                        "Invalid shortcut ! Current global shortcut : ") \
                        + globalShortcutKey)
                else :
                    globalShortcutKey = newShortcut
                    paramGet.SetString("GlobalShortcutKey", globalShortcutKey)
                    labelGlobalShortcut.setText(translate("GlobalSettingsTab", \
                        "New global shortcut assigned: ") \
                        + globalShortcutKey)
        actionKey.setShortcut(QtGui.QKeySequence(globalShortcutKey))
        globalShortcutLineEdit.setText(globalShortcutKey)


    def infoPopup():
        msg = """
            <h2>Pie menu</h2>
            <p style='font-weight:normal;font-style:italic;'>version """ + PIE_MENU_VERSION + """</p>
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
        res = QtGui.QMessageBox.question(None,"Help",msg,QtGui.QMessageBox.Ok)


    def documentationLink():
        """Open PieMenu documentation using the Help settings."""
        from Help import show
        pieMenuDialog.close()
        # Open a wiki page
        show("PieMenu Workbench")


    def onPieChange():
        """ Update values for all settings """
        global triggerMode

        buttonList()
        toolList()
        setDefaults()
        getCheckContext()
        shortcutKey = getParameterGroup(cBox.currentText(), "String", "ShortcutKey")
        getShortcutList()
        shortcutLineEdit.setText(shortcutKey)

        defaultPie = getParameterGlobal("String", "CurrentPie")
        checkboxDefaultPie.blockSignals(True)
        if defaultPie == cBox.currentText():
            checkboxDefaultPie.setChecked(True)
        else:
            checkboxDefaultPie.setChecked(False)
        checkboxDefaultPie.blockSignals(False)

        index = cBox.findText(defaultPie)
        cBox.setItemIcon(index, iconDefault)

        globalShortcutLineEdit.setText(globalShortcutKey)
        labelShortcut.setText(translate("PieMenuTab", "Current shortcut: ") + shortcutKey)
        labelGlobalShortcut.setText(translate("GlobalSettingsTab", "Global shortcut: ") \
            + globalShortcutKey)

        displayCommandName = getParameterGroup(cBox.currentText(), "Bool", "DisplayCommand")
        checkboxDisplayCommandName.blockSignals(True)
        checkboxDisplayCommandName.setChecked(displayCommandName)
        checkboxDisplayCommandName.blockSignals(False)

        displayPreselect = getParameterGroup(cBox.currentText(), "Bool", "DisplayPreselect")
        checkboxDisplayPreselect.blockSignals(True)
        checkboxDisplayPreselect.setChecked(displayPreselect)
        checkboxDisplayPreselect.blockSignals(False)

        enableShortcut = getParameterGroup(cBox.currentText(), "Bool", "EnableShorcut")
        toolShortcutGroup.setChecked(enableShortcut)
        buttonListWidget.setColumnHidden(0, not enableShortcut)

        contextPieMenu = getCheckContext()
        settingContextGroup.setChecked(contextPieMenu)
        displayShortcut = getParameterGroup(cBox.currentText(), "Bool", "DisplayShorcut")
        checkboxDisplayShortcut.setChecked(displayShortcut)

        shape = getShape(cBox.currentText())
        onShape(shape)

        spinNumColumn.setValue(getParameterGroup(cBox.currentText(), "Int", "NumColumn"))
        spinIconSpacing.setValue(getParameterGroup(cBox.currentText(), "Int", "IconSpacing"))

        setWbForPieMenu()
        checkboxGlobalKeyToggle.setChecked(getParameterGlobal("Bool", "GlobalKeyToggle"))

        spinCommandPerCircle.setValue(getParameterGroup(cBox.currentText(), "Int", "CommandPerCircle"))
        triggerMode = getParameterGroup(cBox.currentText(), "String", "TriggerMode")
        setTriggerMode(triggerMode)

        radioButtonPress.setChecked(triggerMode == "Press")
        radioButtonHover.setChecked(triggerMode == "Hover")

        spinHoverDelay.setValue(getParameterGroup(cBox.currentText(), "Int", "HoverDelay"))
        spinShortcutLabelSize.setValue(getParameterGroup(cBox.currentText(), "Int", "ShortcutLabelSize"))

        iconPath = getParameterGroup(cBox.currentText(), "String", "IconPath")
        if iconPath != "":
            buttonIconPieMenu.setIcon(QtGui.QIcon(iconPath))
        else:
            buttonIconPieMenu.setIcon(QtGui.QIcon(iconPieMenuLogo))

        checkboxTriggerContext.blockSignals(True)
        checkboxTriggerContext.setChecked(getParameterGroup(cBox.currentText(), "Bool", "ImmediateTriggerContext"))
        checkboxTriggerContext.blockSignals(False)

        infoShortcut.setText('')
        onContextWorkbench()


    def inputTextDialog(title):
        info1 = translate("PieMenuTab", "Please insert menu name")
        info2 = translate("PieMenuTab", "Menu already exists")
        d = QtGui.QInputDialog(pieMenuDialog)
        d.setModal(True)
        d.setInputMode(QtGui.QInputDialog.InputMode.TextInput)
        text, ok = QtGui.QInputDialog.getText(pieMenuDialog, title, info1)
        if not ok:
            return text, ok
        while not text:
            text, ok = QtGui.QInputDialog.getText(pieMenuDialog, title, info1)
            if not ok:
                return text, ok
            else:
                pass
        index = cBox.findText(text)
        info = info2
        while index != -1:
            d = QtGui.QInputDialog(pieMenuDialog)
            d.setModal(True)
            d.setInputMode(QtGui.QInputDialog.InputMode.TextInput)
            text, ok = QtGui.QInputDialog.getText(pieMenuDialog, title, info)
            if ok:
                if text:
                    index = cBox.findText(text)
                    info = info2
                else:
                    info = info1
            else:
                return text, ok
        return text, ok


    def createPie(text):
        pieList = []
        indexList = getIndexList()
        for i in indexList:
            a = str(i)
            pieList.append(paramIndexGet.GetString(a))
        if text.encode('UTF-8') in pieList:
            pass
        elif not text:
            pass
        else:
            if text == "restore_default_pie" and text.lower():
                setDefaultPie(restore=True)
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
                paramIndexGet.SetString("IndexList", ".,.".join(indexList))
                indexNumber = str(indexNumber)
                try:
                    paramIndexGet.SetString(indexNumber, text.encode('UTF-8'))
                except TypeError:
                    paramIndexGet.SetString(indexNumber, text)
            cBoxUpdate(text)

            updateNestedPieMenus()
            reloadWorkbench()

        return paramIndexGet.GetGroup(indexNumber)


    def onButtonAddPieMenu():
        text, ok = inputTextDialog(translate("PieMenuTab", "New menu"))
        if not ok:
            return
        createPie(text)


    def onButtonRemovePieMenu():
        try:
            currentPie = paramGet.GetString("CurrentPie").decode("UTF-8")
        except AttributeError:
            currentPie = paramGet.GetString("CurrentPie")
        try:
            contextPie = paramGet.GetString("ContextPie").decode("UTF-8")
        except AttributeError:
            contextPie = paramGet.GetString("ContextPie")

        indexList = getIndexList()
        for i in indexList:
            a = str(i)
            try:
                pie = paramIndexGet.GetString(a).decode("UTF-8")
            except AttributeError:
                pie = paramIndexGet.GetString(a)
            if pie == cBox.currentText():
                indexList.remove(i)

                temp = []

                for i in indexList:
                    temp.append(str(i))

                indexList = temp

                paramIndexGet.SetString("IndexList", ".,.".join(indexList))

                paramIndexGet.RemGroup(a)
                paramIndexGet.RemString(a)

                globaltoolbar = FreeCAD.ParamGet('User parameter:BaseApp/Workbench/Global/Toolbar/Custom_PieMenu')
                globaltoolbar.RemString('Std_PieMenu_' + pie)

                # special case treatment
                if pie == currentPie:
                    currentPie = "View"
                    try:
                        paramGet.SetString("CurrentPie", currentPie.encode('UTF-8'))
                    except TypeError:
                        paramGet.SetString("CurrentPie", currentPie)
                if pie == contextPie:
                    paramGet.RemString("ContextPie")

                # remove nested_menu in toollist
                for i in indexList:
                    a = str(i)
                    toolListe = None

                    group = paramIndexGet.GetGroup(a)
                    toolListe = group.GetString("ToolList")

                    if toolListe:
                        toolListe = toolListe.split(".,.")
                    else:
                        toolListe = []

                    stringToFind = 'Std_PieMenu_' + pie

                    if (stringToFind) in toolListe:
                        toolListe.remove(stringToFind)
                        toolListe = group.SetString("ToolList", ".,.".join(toolListe))

            else:
                pass

        cBoxUpdate()

        if cBox.currentIndex() == -1:
            setDefaultPie()
            cBoxUpdate()
        else:
            pass


    def onButtonRenamePieMenu():
        text, ok = inputTextDialog(translate("PieMenuTab", "Rename menu"))
        if not ok:
            return
        indexList = getIndexList()
        try:
            currentPie = paramGet.GetString("CurrentPie").decode("UTF-8")
        except AttributeError:
            currentPie = paramGet.GetString("CurrentPie")
        for i in indexList:
            a = str(i)
            try:
                pie = paramIndexGet.GetString(a).decode("UTF-8")
            except AttributeError:
                pie = paramIndexGet.GetString(a)
            if pie == cBox.currentText():
                try:
                    paramIndexGet.SetString(a, text.encode('UTF-8'))
                except TypeError:
                    paramIndexGet.SetString(a, text)
                if pie == currentPie:
                    try:
                        paramGet.SetString("CurrentPie", text.encode('UTF-8'))
                    except TypeError:
                        paramGet.SetString("CurrentPie", text)
                else:
                    pass

                # rename nested_menu in toollist
                for i in indexList:
                    a = str(i)
                    toolListe = None

                    group = paramIndexGet.GetGroup(a)
                    toolListe = group.GetString("ToolList")

                    if toolListe:
                        toolListe = toolListe.split(".,.")
                    else:
                        toolListe = []

                    stringToFind = 'Std_PieMenu_' + pie

                    if (stringToFind) in toolListe:
                        index = toolListe.index(stringToFind)
                        toolListe[index] = 'Std_PieMenu_' + text
                        toolListe = group.SetString("ToolList", ".,.".join(toolListe))

        globaltoolbar = FreeCAD.ParamGet('User parameter:BaseApp/Workbench/Global/Toolbar/Custom_PieMenu')
        globaltoolbar.RemString('Std_PieMenu_' + pie)
        FreeCADGui.addCommand('Std_PieMenu_' + text, NestedPieMenu(text))
        globaltoolbar.SetString('Std_PieMenu_' + text, 'FreeCAD')

        reloadWorkbench()
        toolList()
        cBoxUpdate(text)


    def getCurrentMenuIndex(currentMenuName):
        indexList = getIndexList()
        for i in indexList:
            a = str(i)
            indexName = paramIndexGet.GetString(a)
            if indexName == currentMenuName:
                return a
        return "-1"


    def copyIndexParams(grpOrg, grpCopy):
        valButOrg = grpOrg.GetInt("Button")
        valRadOrg = grpOrg.GetInt("Radius")
        tbOrg = grpOrg.GetString("ToolList")
        grpCopy.SetInt("Button", valButOrg)
        grpCopy.SetInt("Radius", valRadOrg)
        grpCopy.SetString("ToolList", tbOrg)


    def copyContextParams(grpOrg, grpCopy):
        grpCntOrg = grpOrg.GetGroup("Context")
        grpCntCopy = grpCopy.GetGroup("Context")
        enabledOrg = grpCntOrg.GetBool("Enabled")
        vtxSgnOrg = grpCntOrg.GetString("VertexSign")
        vtxValOrg = grpCntOrg.GetInt("VertexValue")
        edgSgnOrg = grpCntOrg.GetString("EdgeSign")
        edgValOrg = grpCntOrg.GetInt("EdgeValue")
        fceSgnOrg = grpCntOrg.GetString("FaceSign")
        fceValOrg = grpCntOrg.GetInt("FaceValue")
        objSgnOrg = grpCntOrg.GetString("ObjectSign")
        objValOrg = grpCntOrg.GetInt("ObjectValue")
        grpCntCopy.SetBool("Enabled", enabledOrg)
        grpCntCopy.SetString("VertexSign", vtxSgnOrg)
        grpCntCopy.SetInt("VertexValue", vtxValOrg)
        grpCntCopy.SetString("EdgeSign", edgSgnOrg)
        grpCntCopy.SetInt("EdgeValue", edgValOrg)
        grpCntCopy.SetString("FaceSign", fceSgnOrg)
        grpCntCopy.SetInt("FaceValue", fceValOrg)
        grpCntCopy.SetString("ObjectSign", objSgnOrg)
        grpCntCopy.SetInt("ObjectValue", objValOrg)


    def onButtonCopyPieMenu():
        text, ok = inputTextDialog(translate("PieMenuTab", "Copy menu"))
        if not ok:
            return

        indexOrg = getCurrentMenuIndex(cBox.currentText())

        pieList = []
        indexList = getIndexList()
        for i in indexList:
            a = str(i)
            pieList.append(paramIndexGet.GetString(a))

        if text.encode('UTF-8') in pieList:
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

            paramIndexGet.SetString("IndexList", ".,.".join(indexList))

            indexCopy = str(indexCopy)
            grpOrg = paramIndexGet.GetGroup(indexOrg)
            grpCopy = paramIndexGet.GetGroup(indexCopy)
            copyIndexParams(grpOrg, grpCopy)
            copyContextParams(grpOrg, grpCopy)

            try:
                paramIndexGet.SetString(indexCopy, text.encode('UTF-8'))
            except TypeError:
                paramIndexGet.SetString(indexCopy, text)

        cBoxUpdate(text)


    def onDefaultPie(state):
        if state == 2:
            paramGet.SetString("CurrentPie", cBox.currentText())
        currentPie = paramGet.GetString("CurrentPie")
        index = cBox.findText(currentPie)
        cBox.setItemIcon(index, iconDefault)
        cBoxUpdate(cBox.currentText())


    def getListWorkbenches():
        workenchList = Gui.listWorkbenches()
        wbList = []
        for i in workenchList:
            wbName = i.replace("Workbench", "")
            wbList.append(wbName)
        wbList.sort()
        if 'None' in wbList:
            wbList.remove('None')
            wbList.insert(0, 'None')

        return wbList


    def getWbAlreadySet():
        indexList = getIndexList()
        wbAlreadySet = []
        for i in indexList:
            a = str(i)
            try:
                pie = paramIndexGet.GetString(a).decode("UTF-8")
            except AttributeError:
                pie = paramIndexGet.GetString(a)

            group = paramIndexGet.GetGroup(a)
            defWb  = group.GetString("DefaultWorkbench")
            if defWb != 'None':
                wbAlreadySet.append(defWb)

        return wbAlreadySet


    def setWbForPieMenu():
        group = getGroup()

        comboWbForPieMenu.blockSignals(True)
        wbList = getListWorkbenches()
        wbAlreadySet = getWbAlreadySet()

        for item in wbList[:]:
            if item in wbAlreadySet:
                wbList.remove(item)
                wbAlreadySet.remove(item)

        defWorkbench = getWbForPieMenu()
        wbList.append(defWorkbench)
        if 'None' not in wbList:
            wbList.insert(0, 'None')

        comboWbForPieMenu.clear()
        comboWbForPieMenu.addItems(wbList)
        index = comboWbForPieMenu.findText(defWorkbench)
        if index != -1:
            comboWbForPieMenu.setCurrentIndex(index)
        comboWbForPieMenu.blockSignals(False)


    def getWbForPieMenu():
        group = getGroup(mode=0)
        defWorkbench = group.GetString("DefaultWorkbench")
        return defWorkbench


    def getContextWorkbench():
        group = getGroup(mode=2)
        contextWorkbench = group.GetString("ContextWorkbench")
        return contextWorkbench


    def onContextWorkbench():
        group = getGroup()

        comboContextWorkbench.blockSignals(True)
        wbList = getListWorkbenches()

        contextWorkbench = getParameterGroup(cBox.currentText(), "String", "ContextWorkbench")
        wbList.append(contextWorkbench)
        if "None" in wbList:
            wbList.remove("None")

        if translate('ContextTab', 'None (Disable)') not in wbList:
            wbList.insert(0, translate('ContextTab', 'None (Disable)'))

        if translate('ContextTab','All Workbenches') not in wbList:
            wbList.insert(0,  translate('ContextTab','All Workbenches'))

        notDuplicate = []
        for i in wbList:
            if i not in notDuplicate:
                notDuplicate.append(i)

        comboContextWorkbench.clear()
        comboContextWorkbench.addItems(notDuplicate)
        index = comboContextWorkbench.findText(contextWorkbench)
        if index != -1:
            comboContextWorkbench.setCurrentIndex(index)
        comboContextWorkbench.blockSignals(False)


    def onWbForPieMenu():
        group = getGroup()
        defWorkbench = comboWbForPieMenu.currentText()
        group.SetString("DefaultWorkbench", defWorkbench)

    def setContextWorkbench():
        group = getGroup()
        contextWorkbench = comboContextWorkbench.currentText()
        group.SetString("ContextWorkbench", contextWorkbench)



    def getPieName(wbName):
        text = None
        indexList = getIndexList()
        for i in indexList:
            a = str(i)
            try:
                pie = paramIndexGet.GetString(a).decode("UTF-8")
            except AttributeError:
                pie = paramIndexGet.GetString(a)
            group = paramIndexGet.GetGroup(a)
            defWb  = group.GetString("DefaultWorkbench")
            if defWb == wbName:
                text = pie
        return text


    def updatePiemenuPreview(key=None):
        try:
            showPiemenu.hide()
            if key == "toolBarTab":
                PieMenuInstance.showPiemenuPreview("toolBarTab")
            else:
                PieMenuInstance.showPiemenuPreview(keyValue=cBox.currentText(), notKeyTriggered=False)
            showPiemenu.show()
        except:
            None


    def onSpinShortcutLabelSize():
        group = getGroup()
        value = spinShortcutLabelSize.value()
        group.SetInt("ShortcutLabelSize", value)
        try:
            if pieMenuDialog.isVisible():
                updatePiemenuPreview()
        except:
            None


    def setShape():
        group = getGroup(mode=0)
        comboShape.blockSignals(True)
        shape = comboShape.currentText()
        group.SetString("Shape", shape)
        comboShape.blockSignals(False)
        onShape(shape)
        try:
            if pieMenuDialog.isVisible():
                updatePiemenuPreview()
        except:
            None


    def onShape(shape):
        try:
            if pieMenuDialog.isVisible():

                if shape in ["TableTop", "TableDown", "TableLeft", "TableRight"]:
                    spinNumColumn.setEnabled(True)
                    labelNumColumn.setVisible(True)
                    spinNumColumn.setVisible(True)
                else:
                    spinNumColumn.setEnabled(False)
                    labelNumColumn.setVisible(False)
                    spinNumColumn.setVisible(False)

                if shape in ["UpDown", "LeftRight", "TableTop", "TableDown", "TableLeft", "TableRight", "Concentric", "Star"]:
                    labelIconSpacing.setVisible(True)
                    spinIconSpacing.setEnabled(True)
                    spinIconSpacing.setVisible(True)
                else:
                    labelIconSpacing.setVisible(False)
                    spinIconSpacing.setEnabled(False)
                    spinIconSpacing.setVisible(False)

                if shape in ["TableTop", "TableDown"]:
                    labelNumColumn.setText(translate("PieMenuTab", "Number of columns:"))
                else:
                    labelNumColumn.setText(translate("PieMenuTab", "Number of rows:"))

                if shape in ["Pie", "LeftRight"]:
                    labeldisplayCommandName.setVisible(True)
                    checkboxDisplayCommandName.setVisible(True)
                    checkboxDisplayCommandName.setEnabled(True)

                else:
                    labeldisplayCommandName.setVisible(False)
                    checkboxDisplayCommandName.setVisible(False)
                    checkboxDisplayCommandName.setEnabled(False)

                if shape in ["Concentric", "Star"]:
                    labelCommandPerCircle.setVisible(True)
                    spinCommandPerCircle.setEnabled(True)
                    spinCommandPerCircle.setVisible(True)
                else:
                    labelCommandPerCircle.setVisible(False)
                    spinCommandPerCircle.setEnabled(False)
                    spinCommandPerCircle.setVisible(False)

                if shape in ["Pie", "RainbowUp", "RainbowDown"]:
                    labelDisplayPreselect.setVisible(True)
                    checkboxDisplayPreselect.setVisible(True)
                    checkboxDisplayPreselect.setEnabled(True)
                else:
                    labelDisplayPreselect.setVisible(False)
                    checkboxDisplayPreselect.setVisible(False)
                    checkboxDisplayPreselect.setEnabled(False)

            # Available for all shapes
            labelShortcutSize.setVisible(True)
            spinShortcutLabelSize.setVisible(True)
            spinShortcutLabelSize.setEnabled(True)

        except:
            None


    def getShape(keyValue=None):
        """ Get value of shape of current PieMenu """
        if keyValue == None:
            try:
                keyValue = paramGet.GetString("CurrentPie").decode("UTF-8")
            except AttributeError:
                keyValue = paramGet.GetString("CurrentPie")

        group = getGroup()
        shape = group.GetString("Shape")

        indexList = getIndexList()
        for i in indexList:
            try:
                pieName = paramIndexGet.GetString(str(i)).decode("UTF-8")
            except AttributeError:
                pieName = paramIndexGet.GetString(str(i))
            if pieName == keyValue:
                param = paramIndexGet.GetGroup(str(i))
                shape = param.GetString("Shape")

        comboShape.blockSignals(True)
        comboShape.clear()
        comboShape.addItems(available_shape)
        index = comboShape.findText(shape)
        if index != -1:
            comboShape.setCurrentIndex(index)
        comboShape.blockSignals(False)

        return shape


    def onDisplayCommandName(state):
        """ Set parameter to show or not 'Command names' """
        indexList = getIndexList()
        for i in indexList:
            a = str(i)
            try:
                pieName = paramIndexGet.GetString(a).decode("UTF-8")
            except AttributeError:
                pieName = paramIndexGet.GetString(a)
            if pieName == cBox.currentText():
                param = paramIndexGet.GetGroup(str(i))
                param.SetBool("DisplayCommand", state)
        try:
            if pieMenuDialog.isVisible():
                updatePiemenuPreview()
        except:
            None


    def onDisplayPreselect(state):
        """ Set parameter to show or not 'Preselect button' """
        indexList = getIndexList()
        for i in indexList:
            a = str(i)
            try:
                pieName = paramIndexGet.GetString(a).decode("UTF-8")
            except AttributeError:
                pieName = paramIndexGet.GetString(a)
            if pieName == cBox.currentText():
                param = paramIndexGet.GetGroup(str(i))
                param.SetBool("DisplayPreselect", state)
        try:
            if pieMenuDialog.isVisible():
                updatePiemenuPreview()
        except:
            None


    def onEnableShortcut(state):
        """ Set parameter for enable or not 'Shortcut Tool' """
        if state:
            spinShortcutLabelSize.setEnabled(True)
            buttonListWidget.setColumnHidden(0, False)
            checkboxDisplayShortcut.setEnabled(True)

        else:
            spinShortcutLabelSize.setEnabled(False)
            buttonListWidget.setColumnHidden(0, True)
            checkboxDisplayShortcut.setEnabled(False)

        indexList = getIndexList()
        for i in indexList:
            a = str(i)
            try:
                pieName = paramIndexGet.GetString(a).decode("UTF-8")
            except AttributeError:
                pieName = paramIndexGet.GetString(a)
            if pieName == cBox.currentText():
                param = paramIndexGet.GetGroup(str(i))
                param.SetBool("EnableShorcut", state)
        try:
            if pieMenuDialog.isVisible():
                updatePiemenuPreview()
        except:
            None


    def onDisplayShortcut(state):
        """ Set parameter for display or not 'Shortcut Tool' """
        if state == 2:
            spinShortcutLabelSize.setEnabled(True)
        else:
            spinShortcutLabelSize.setEnabled(False)

        indexList = getIndexList()
        for i in indexList:
            a = str(i)
            try:
                pieName = paramIndexGet.GetString(a).decode("UTF-8")
            except AttributeError:
                pieName = paramIndexGet.GetString(a)
            if pieName == cBox.currentText():
                param = paramIndexGet.GetGroup(str(i))
                param.SetBool("DisplayShorcut", state)
        updatePiemenuPreview()


    def onTriggerContext(state):
        """ Set parameter for immediate trigger context mode """
        indexList = getIndexList()
        for i in indexList:
            a = str(i)
            try:
                pieName = paramIndexGet.GetString(a).decode("UTF-8")
            except AttributeError:
                pieName = paramIndexGet.GetString(a)
            if pieName == cBox.currentText():
                param = paramIndexGet.GetGroup(str(i))
                param.SetBool("ImmediateTriggerContext", state)


    def onNumColumn():
        group = getGroup()
        value = spinNumColumn.value()
        group.SetInt("NumColumn", value)
        updatePiemenuPreview()


    def onIconSpacing():
        group = getGroup()
        value = spinIconSpacing.value()
        group.SetInt("IconSpacing", value)
        updatePiemenuPreview()


    def onCommandPerCircle():
        group = getGroup()
        value = spinCommandPerCircle.value()
        group.SetInt("CommandPerCircle", value)
        updatePiemenuPreview()


    def onSpinHoverDelay():
        """ Set TriggerMode in parameter """
        value = spinHoverDelay.value()
        indexList = getIndexList()
        for i in indexList:
            a = str(i)
            try:
                pieName = paramIndexGet.GetString(a).decode("UTF-8")
            except AttributeError:
                pieName = paramIndexGet.GetString(a)
            if pieName == cBox.currentText():
                param = paramIndexGet.GetGroup(str(i))
                param.SetInt("HoverDelay", value)


    def onSpinRadius():
        group = getGroup()
        value = spinRadius.value()
        group.SetInt("Radius", value)
        updatePiemenuPreview()


    def onSpinButton():
        group = getGroup()
        value = spinButton.value()
        group.SetInt("Button", value)
        updatePiemenuPreview()


    def onSpinDelayRightClick():
        value = spinDelayRightClick.value()
        paramGet.SetInt("DelayRightClick", value)


    def onShowQuickMenu(state):
        if state == Qt.Checked:
            paramGet.SetBool("ShowQuickMenu", True)
        else:
            paramGet.SetBool("ShowQuickMenu", False)
        updatePiemenuPreview()


    def onRightClickTrigger(state):
        if state == Qt.Checked:
            paramGet.SetBool("RightClickTrigger", True)
            spinDelayRightClick.setEnabled(True)
        else:
            paramGet.SetBool("RightClickTrigger", False)
            spinDelayRightClick.setEnabled(False)


    def onButtonIconPieMenu():
        """ Set path for icon's PieMenu """
        file_dialog = QFileDialog()
        file_path, _ = QFileDialog.getOpenFileName(None, translate("PieMenuTab", "Choose Icon"), "", translate("PieMenuTab", "SVG Files (*.svg);;ICO Files (*.ico);;All files (*.*)"))

        if file_path:
            indexList = getIndexList()
            for i in indexList:
                a = str(i)
                try:
                    pieName = paramIndexGet.GetString(a).decode("UTF-8")
                except AttributeError:
                    pieName = paramIndexGet.GetString(a)
                if pieName == cBox.currentText():
                    param = paramIndexGet.GetGroup(str(i))
                    param.SetString("IconPath", file_path)
                    buttonIconPieMenu.setIcon(QtGui.QIcon(file_path))

            globaltoolbar = FreeCAD.ParamGet('User parameter:BaseApp/Workbench/Global/Toolbar/Custom_PieMenu')
            globaltoolbar.SetString('Std_PieMenu_' + pieName, 'FreeCAD')

            updateNestedPieMenus()
            reloadWorkbench()
            toolList()


    def onContext(state):
        if state == Qt.Checked:
            paramGet.SetBool("EnableContext", True)
        else:
            paramGet.SetBool("EnableContext", False)


    def toolList():
        text = cBox.currentText()
        actionMapAll = getGuiActionMapAll()
        toolListWidget.blockSignals(True)
        toolListWidget.clear()
        for i in actionMapAll:
            item = QtGui.QListWidgetItem(toolListWidget)
            item.setText(actionMapAll[i].text().replace("&", ""))
            item.setIcon(actionMapAll[i].icon())
            item.setCheckState(QtCore.Qt.CheckState(0))
            item.setData(QtCore.Qt.UserRole, actionMapAll[i].objectName())
            item.setToolTip(actionMapAll[i].toolTip())

        toolListOn = None
        indexList = getIndexList()
        for i in indexList:
            a = str(i)
            try:
                pie = paramIndexGet.GetString(a).decode("UTF-8")
            except AttributeError:
                pie = paramIndexGet.GetString(a)
            if pie == text:
                group = paramIndexGet.GetGroup(a)
                toolListOn = group.GetString("ToolList")
            else:
                pass
        if toolListOn:
            toolListOn = toolListOn.split(".,.")
        else:
            toolListOn = []
        items = []
        for index in range(toolListWidget.count()):
            items.append(toolListWidget.item(index))
        for i in items:
            if i.data(QtCore.Qt.UserRole) in toolListOn:
                i.setCheckState(QtCore.Qt.CheckState(2))
            else:
                pass
        toolListWidget.blockSignals(False)


    def onAddToolBar():
        """ create a menu from an existing toolbar  """
        items = []
        commands = []
        for index in range(listToolBar.count()):
            items.append(listToolBar.item(index))
        text, ok = inputTextDialog(translate("PieMenuTab", "New menu"))
        if not ok:
            return text, ok
        else:
            newPieGroup = createPie(text)
            toolbar = listToolBar.currentItem()
            getGuiToolButtonData(toolbar.text(), None, commands, None)
            newPieGroup.SetString("ToolList", ".,.".join(commands))
            newPieGroup.SetString("Shape", "Pie")
            tabs.setCurrentIndex(0)
        onBackToSettings()
        updatePiemenuPreview()


    def showListToolBar():
        """ show list of tools of an existing toolbar  """
        items = []
        commands = []

        for index in range(listToolBar.count()):
            items.append(listToolBar.item(index))
            if items[index].isSelected():
                sender = listToolBar.item(index)
                getGuiToolButtonData(sender.text(), None, commands, None)

        buttonListWidget.blockSignals(True)
        buttonListWidget.clearContents()
        buttonListWidget.setRowCount(0)

        actionMapAll = getGuiActionMapAll()
        for i in commands:
            if i in actionMapAll:
                rowPosition = buttonListWidget.rowCount()
                buttonListWidget.insertRow(rowPosition)
                actionItem = QtWidgets.QTableWidgetItem(actionMapAll[i].text().replace("&", ""))
                actionItem.setData(QtCore.Qt.UserRole, i)
                actionItem.setIcon(actionMapAll[i].icon())
                actionItem.setFlags(QtCore.Qt.ItemIsEnabled)
                buttonListWidget.setItem(rowPosition, 1, actionItem)
                actionItem.setToolTip(actionMapAll[i].toolTip())

        buttonListWidget.blockSignals(False)
        updatePiemenuPreview("toolBarTab")


    def onToolListWidget():
        text = cBox.currentText()
        items = []

        for index in range(toolListWidget.count()):
            items.append(toolListWidget.item(index))

        checkListOn = []
        checkListOff = []

        for i in items:
            if i.checkState():
                checkListOn.append(i.data(QtCore.Qt.UserRole))
            else:
                checkListOff.append(i.data(QtCore.Qt.UserRole))

        toolList = None
        indexList = getIndexList()
        for i in indexList:
            a = str(i)
            try:
                pie = paramIndexGet.GetString(a).decode("UTF-8")
            except AttributeError:
                pie = paramIndexGet.GetString(a)
            if pie == text:
                group = paramIndexGet.GetGroup(a)
                toolList = group.GetString("ToolList")
            else:
                pass

        if toolList:
            toolList = toolList.split(".,.")
        else:
            toolList = []

        for i in checkListOn:
            if i not in toolList:
                toolList.append(i)

            else:
                pass

        for i in checkListOff:
            if i in toolList:
                toolList.remove(i)
            else:
                pass
        for i in indexList:
            a = str(i)
            try:
                pie = paramIndexGet.GetString(a).decode("UTF-8")
            except AttributeError:
                pie = paramIndexGet.GetString(a)
            if pie == text:
                group = paramIndexGet.GetGroup(a)
                toolList = group.SetString("ToolList", ".,.".join(toolList))
            else:
                pass
        buttonList()


    def searchInToolList(search_text):
        search_text = search_text.lower()
        toolListWidget.clear()

        text = cBox.currentText()
        actionMapAll = getGuiActionMapAll()
        toolListWidget.blockSignals(True)
        toolListWidget.clear()
        for i in actionMapAll:
            action_text = actionMapAll[i].text().replace("&", "")
            if search_text in action_text.lower():
                item = QListWidgetItem(toolListWidget)
                item.setText(action_text)
                item.setIcon(actionMapAll[i].icon())
                item.setCheckState(QtCore.Qt.CheckState(0))
                item.setData(QtCore.Qt.UserRole, actionMapAll[i].objectName())
                item.setToolTip(actionMapAll[i].toolTip())

        toolListOn = None
        indexList = getIndexList()
        for i in indexList:
            a = str(i)
            try:
                pie = paramIndexGet.GetString(a).decode("UTF-8")
            except AttributeError:
                pie = paramIndexGet.GetString(a)
            if pie == text:
                group = paramIndexGet.GetGroup(a)
                toolListOn = group.GetString("ToolList")
            else:
                pass
        if toolListOn:
            toolListOn = toolListOn.split(".,.")
        else:
            toolListOn = []
        items = []
        for index in range(toolListWidget.count()):
            items.append(toolListWidget.item(index))
        for i in items:
            if i.data(QtCore.Qt.UserRole) in toolListOn:
                i.setCheckState(QtCore.Qt.CheckState(2))
            else:
                pass
        toolListWidget.blockSignals(False)


    def buttonList2ToolList(buttonListWidget):
        toolData = []
        rowCount = buttonListWidget.rowCount()

        for row in range(rowCount):
            item = buttonListWidget.item(row, 1)
            if (item.data(QtCore.Qt.UserRole)) is not None:
                toolData.append(item.data(QtCore.Qt.UserRole))
        group = getGroup()
        group.SetString("ToolList", ".,.".join(toolData))


    def onButtonUp():
        currentIndex = buttonListWidget.currentRow()
        if currentIndex != 0:
            item_first_column = buttonListWidget.takeItem(currentIndex, 0)
            item_second_column = buttonListWidget.takeItem(currentIndex, 1)

            buttonListWidget.removeRow(currentIndex)
            buttonListWidget.insertRow(currentIndex - 1)

            buttonListWidget.setItem(currentIndex, 0, item_first_column)
            buttonListWidget.setItem(currentIndex - 1, 1, item_second_column)

            buttonList2ToolList(buttonListWidget)
            buttonList()
            buttonListWidget.setCurrentCell(currentIndex - 1, 1)


    def onButtonDown():
        currentIndex = buttonListWidget.currentRow()
        rowCount = buttonListWidget.rowCount()
        if currentIndex < rowCount - 1:
            item_first_column = buttonListWidget.takeItem(currentIndex, 0)
            item_second_column = buttonListWidget.takeItem(currentIndex, 1)

            buttonListWidget.removeRow(currentIndex)
            buttonListWidget.insertRow(currentIndex + 1)

            buttonListWidget.setItem(currentIndex, 0, item_first_column)
            buttonListWidget.setItem(currentIndex + 1, 1, item_second_column)

            buttonList2ToolList(buttonListWidget)
            buttonList()
            buttonListWidget.setCurrentCell(currentIndex + 1, 1)


    def onButtonRemoveCommand():
        currentIndex = buttonListWidget.currentRow()
        rowCount = buttonListWidget.rowCount()

        if rowCount > 0 and 0 <= currentIndex < rowCount:
            items = []
            for column in range(buttonListWidget.columnCount()):
                item = buttonListWidget.takeItem(currentIndex, column)
                items.append(item)

            buttonListWidget.removeRow(currentIndex)

            buttonListWidget.setFocus()
            buttonList2ToolList(buttonListWidget)
            buttonList()
            toolList()
            if currentIndex != 0:
                buttonListWidget.setCurrentCell(currentIndex - 1, 1)


    def onButtonAddSeparator():
        """ Handle separator for PieMenus """
        # we must create a custom toolbar "PieMenuTB" to 'activate' the command 'Std_PieMenuSeparator' otherwise the separators are not correctly handled
        globaltoolbar = FreeCAD.ParamGet('User parameter:BaseApp/Workbench/Global/Toolbar/Custom_PieMenu')

        pieMenuTB = globaltoolbar.GetString('Name')
        if pieMenuTB == "PieMenuTB":
            pass
        else:
            globaltoolbar.SetString('Name','PieMenuTB')
            App.saveParameter()
        globaltoolbar.SetString('Std_PieMenuSeparator','FreeCAD')

        reloadWorkbench()

        # we hide the custom toolbar
        mw = Gui.getMainWindow()
        for i in mw.findChildren(QtGui.QToolBar):
            if i.windowTitle() == 'PieMenuTB':
                i.setVisible(False)

        text = cBox.currentText()

        items = []
        for index in range(toolListWidget.count()):
            items.append(toolListWidget.item(index))

        toolList = None
        indexList = getIndexList()
        for i in indexList:
            a = str(i)
            try:
                pie = paramIndexGet.GetString(a).decode("UTF-8")
            except AttributeError:
                pie = paramIndexGet.GetString(a)
            if pie == text:
                group = paramIndexGet.GetGroup(a)
                toolList = group.GetString("ToolList")
            else:
                pass

        if toolList:
            toolList = toolList.split(".,.")
        else:
            toolList = []

        i = "Std_PieMenuSeparator"
        toolList.append(i)

        for i in indexList:
            a = str(i)
            try:
                pie = paramIndexGet.GetString(a).decode("UTF-8")
            except AttributeError:
                pie = paramIndexGet.GetString(a)
            if pie == text:
                group = paramIndexGet.GetGroup(a)
                toolList = group.SetString("ToolList", ".,.".join(toolList))
            else:
                pass
        buttonList()


    def onButtonToolBar():
        """ Show interface to add existing Freecad's Toolbars """
        infoShortcut.setText('')
        piemenuBoxGroup.setVisible(False)

        tabs.setVisible(False)
        toolBarTab.setVisible(True)
        buttonBackToSettings.setVisible(True)
        buttonExistingToolBar.setVisible(False)

        for i in reversed(range(buttonsLayout.count())):
            try:
                buttonsLayout.itemAt(i).widget().hide()
            except:
                None
            # hide shortcuts in buttonListWidget
            buttonListWidget.setColumnHidden(0, True)

        # generate list of existing toolBars
        listToolBar = onListToolBar()

        # set first element of listToolBar
        index = listToolBar.model().index(0, 0)
        if index.isValid():
            listToolBar.setCurrentIndex(index)
        showListToolBar()

        updatePiemenuPreview("toolBarTab")


    def onBackToSettings():
        """ Return to general settings interface """
        toolBarTab.setVisible(False)
        piemenuBoxGroup.setVisible(True)
        buttonExistingToolBar.setVisible(True)
        for i in reversed(range(buttonsLayout.count())):
            try:
                buttonsLayout.itemAt(i).widget().show()
            except:
                None
        tabs.setVisible(True)

        vSplitter.refresh()
        buttonBackToSettings.setVisible(False)
        onPieChange()
        updatePiemenuPreview()


    def comboBox(TopoType):
        signList = ["<", "<=", "==", "!=", ">", ">="]
        model = QtGui.QStandardItemModel()
        for i in signList:
            item = QtGui.QStandardItem()
            item.setText(i)
            item.setData(TopoType, QtCore.Qt.UserRole)
            model.setItem(signList.index(i), 0, item)
        comboBoxSign = QtGui.QComboBox()
        comboBoxSign.setObjectName("styleCombo")
        comboBoxSign.setModel(model)
        styleCurrentTheme = getStyle()
        comboBoxSign.setStyleSheet(styleCurrentTheme)


        def onCurrentIndexChanged():
            group = getGroup()
            groupContext = group.GetGroup("Context")
            text = comboBoxSign.currentText()
            topo = comboBoxSign.itemData(comboBoxSign.currentIndex(),
                                         QtCore.Qt.UserRole)
            groupContext.SetString(topo, text)
            contextList()
        comboBoxSign.currentIndexChanged.connect(onCurrentIndexChanged)
        return comboBoxSign


    def spinBox(TopoValue):
        spinBox = QtGui.QSpinBox()
        spinBox.setFrame(False)

        def onSpinBox():
            group = getGroup()
            groupContext = group.GetGroup("Context")
            value = spinBox.value()
            groupContext.SetInt(TopoValue, value)
            contextList()
        spinBox.valueChanged.connect(onSpinBox)

        return spinBox


    def getCheckContext():
        """ Get parameter 'Context' """
        group = getGroup()
        groupContext = group.GetGroup("Context")
        contextPieMenu = True
        contextPieMenu = groupContext.GetBool("Enabled")
        if contextPieMenu:
            settingContextGroup.setChecked(True)
            contextTable.setEnabled(True)
            resetContextButton.setEnabled(True)
        else:
            settingContextGroup.setChecked(False)
            contextTable.setEnabled(False)
            resetContextButton.setEnabled(False)
        contextList()

        return contextPieMenu


    def onCheckContext(state):
        """ Set parameter for enable or not 'Context' """
        setDefaults()
        group = getGroup()
        groupContext = group.GetGroup("Context")
        if state:
            contextTable.setEnabled(True)
            resetContextButton.setEnabled(True)
            groupContext.SetBool("Enabled", 1)
        else:
            contextTable.setEnabled(False)
            resetContextButton.setEnabled(False)
            groupContext.SetBool("Enabled", 0)
        contextList()


    def onResetContextButton():
        group = getGroup()
        group.RemGroup("Context")
        setDefaults()
        getCheckContext()


    def setDefaults():
        group = getGroup()
        groupContext = group.GetGroup("Context")
        vertexSign = groupContext.GetString("VertexSign")
        # Make sure vertexSign has a valid value
        if vertexSign in sign:
            pass
        else:
            groupContext.SetString("VertexSign", "==")
            vertexSign = "=="
        for i in range(vertexComboBox.count()):
            if vertexComboBox.itemText(i) == vertexSign:
                vertexComboBox.setCurrentIndex(i)
            else:
                pass
        vertexValue = groupContext.GetInt("VertexValue")
        if vertexValue:
            pass
        else:
            a = groupContext.GetInt("VertexValue", True)
            b = groupContext.GetInt("VertexValue", False)

            if a == b:
                groupContext.SetInt("VertexValue", 0)
                vertexValue = 0
            else:
                groupContext.SetInt("VertexValue", 10)
                vertexValue = 10
        vertexSpin.setValue(vertexValue)
        edgeSign = groupContext.GetString("EdgeSign")
        if edgeSign in sign:
            pass
        else:
            groupContext.SetString("EdgeSign", "==")
            edgeSign = "=="
        for i in range(edgeComboBox.count()):
            if edgeComboBox.itemText(i) == edgeSign:
                edgeComboBox.setCurrentIndex(i)
            else:
                pass
        edgeValue = groupContext.GetInt("EdgeValue")
        if edgeValue:
            pass
        else:
            a = groupContext.GetInt("EdgeValue", True)
            b = groupContext.GetInt("EdgeValue", False)

            if a == b:
                groupContext.SetInt("EdgeValue", 0)
                edgeValue = 0
            else:
                groupContext.SetInt("EdgeValue", 10)
                edgeValue = 10
        edgeSpin.setValue(edgeValue)
        faceSign = groupContext.GetString("FaceSign")
        if faceSign in sign:
            pass
        else:
            groupContext.SetString("FaceSign", "==")
            faceSign = "=="
        for i in range(faceComboBox.count()):
            if faceComboBox.itemText(i) == faceSign:
                faceComboBox.setCurrentIndex(i)
            else:
                pass
        faceValue = groupContext.GetInt("FaceValue")
        if faceValue:
            pass
        else:
            a = groupContext.GetInt("FaceValue", True)
            b = groupContext.GetInt("FaceValue", False)

            if a == b:
                groupContext.SetInt("FaceValue", 0)
                faceValue = 0
            else:
                groupContext.SetInt("FaceValue", 10)
                faceValue = 10
        faceSpin.setValue(faceValue)
        objectSign = groupContext.GetString("ObjectSign")
        if objectSign in sign:
            pass
        else:
            groupContext.SetString("ObjectSign", "==")
            objectSign = "=="
        for i in range(objectComboBox.count()):
            if objectComboBox.itemText(i) == objectSign:
                objectComboBox.setCurrentIndex(i)
            else:
                pass
        objectValue = groupContext.GetInt("ObjectValue")
        if objectValue:
            pass
        else:
            a = groupContext.GetInt("ObjectValue", True)
            b = groupContext.GetInt("ObjectValue", False)
            if a == b:
                groupContext.SetInt("ObjectValue", 0)
                objectValue = 0
            else:
                groupContext.SetInt("ObjectValue", 10)
                objectValue = 10
        objectSpin.setValue(objectValue)

        defaultWorkbench = group.GetString("DefaultWorkbench")
        if defaultWorkbench:
            pass
        else:
            defaultWorkbench = "None"
            group.SetString("DefaultWorkbench", defaultWorkbench)

        valueRadius = group.GetInt("Radius")
        if valueRadius:
            pass
        else:
            valueRadius = 100
            group.SetInt("Radius", valueRadius)
        spinRadius.setValue(valueRadius)

        valueButton = group.GetInt("Button")
        if valueButton:
            pass
        else:
            valueButton = 32
            group.SetInt("Button", valueButton)
        spinButton.setValue(valueButton)

        shape = group.GetString("Shape")
        if shape:
            pass
        else:
            shape = "Pie"
            group.SetString("Shape", shape)

        triggerMode = group.GetString("TriggerMode")
        if triggerMode:
            pass
        else:
            triggerMode = "Press"
            group.SetString("TriggerMode", triggerMode)

        hoverDelay = group.GetInt("HoverDelay")
        if hoverDelay:
            pass
        else:
            hoverDelay = 100
            group.SetInt("HoverDelay", hoverDelay)

        displayCommand = group.GetBool("DisplayCommand")
        if displayCommand:
            pass
        else:
            displayCommand = False
            group.SetBool("DisplayCommand", displayCommand)

        displayPreselect = group.GetBool("DisplayPreselect")
        if displayPreselect:
            pass
        else:
            displayPreselect = False
            group.SetBool("DisplayPreselect", displayPreselect)
        contextList()


    def setDefaultPie(restore=False):
        indexList = getIndexList()
        if 0 in indexList:
            if restore:
                group = paramIndexGet.GetGroup("0")
                group.SetString("ToolList", ".,.".join(defaultTools))
            else:
                pass
        else:
            indexList.append(0)
            indexList.append(1)
            indexList.append(2)

            temp = []

            for i in indexList:
                temp.append(str(i))

            indexList = temp

            paramIndexGet.SetString("0", "View")
            paramIndexGet.SetString("IndexList", ".,.".join(indexList))

            group = paramIndexGet.GetGroup("0")
            group.SetString("ToolList", ".,.".join(defaultTools))
            group.SetInt("Radius", 80)
            group.SetInt("Button", 32)
            group.SetString("Shape", "Pie")
            group.SetString("TriggerMode", "Press")
            group.SetInt("HoverDelay", 100)
            group.SetBool("EnableShorcut", False)
            group.SetBool("DisplayPreselect", False)

            paramIndexGet.SetString("1", "PartDesign")
            group = paramIndexGet.GetGroup("1")
            group.SetString("ToolList", ".,.".join(defaultToolsPartDesign))
            group.SetInt("Radius", 80)
            group.SetInt("Button", 32)
            group.SetString("Shape", "Pie")
            group.SetString("TriggerMode", "Press")
            group.SetInt("HoverDelay", 100)
            group.SetBool("EnableShorcut", False)
            group.SetBool("DisplayPreselect", False)

            paramIndexGet.SetString("2", "Sketcher")
            group = paramIndexGet.GetGroup("2")
            group.SetString("ToolList", ".,.".join(defaultToolsSketcher))
            group.SetInt("Radius", 80)
            group.SetInt("Button", 32)
            group.SetString("Shape", "Pie")
            group.SetString("TriggerMode", "Press")
            group.SetInt("HoverDelay", 100)
            group.SetString("DefaultWorkbench", "Sketcher")
            group.SetBool("EnableShorcut", False)
            group.SetBool("DisplayPreselect", False)

        paramGet.SetBool("ToolBar", False)
        paramGet.RemString("ToolBar")
        paramGet.SetString("CurrentPie", "View")
        paramGet.SetString("Theme", "Legacy")
        paramGet.SetString("GlobalShortcutKey", "TAB")
        paramGet.SetBool("ShowQuickMenu", True)
        paramGet.SetBool("EnableContext", False)
        paramGet.SetBool("GlobalKeyToggle", True)
        paramGet.SetInt("DelayRightClick", 100)
        App.saveParameter()


    ### Begin QuickMenu  Def ###
    def quickMenu(buttonSize=20):
        """Build and style the QuickMenu button."""


        def onActionContext():
            """ Set state of Context mode"""
            if actionContext.isChecked():
                paramGet.SetBool("EnableContext", True)
                checkboxGlobalContext.setChecked(True)
                contextList()
            else:
                paramGet.SetBool("EnableContext", False)
                checkboxGlobalContext.setChecked(False)
            addObserver()


        def pieList():
            """Populate the menuPieMenu with actions based on user parameters."""
            indexList = getIndexList()
            menuPieMenu.clear()

            pieList = []
            shortlist = []
            for i in indexList:
                a = str(i)
                try:
                    pieName = paramIndexGet.GetString(a).decode("UTF-8")
                except AttributeError:
                    pieName = paramIndexGet.GetString(a)
                pieList.append(pieName)
                param = paramIndexGet.GetGroup(str(i))
                shortcut = param.GetString("ShortcutKey")
                shortlist.append(shortcut)
            if not paramGet.GetBool("ToolBar"):
                try:
                    text = paramGet.GetString("CurrentPie").decode("UTF-8")
                except AttributeError:
                    text = paramGet.GetString("CurrentPie")
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
                        action.setIcon(iconDefault)
                else:
                    pass
                menuPieMenu.addAction(action)


        def onPieGroup():
            """Handle the default pieMenu selection event in quickMenu."""
            paramGet.SetBool("ToolBar", False)
            paramGet.RemString("ToolBar")
            try:
                text = pieGroup.checkedAction().text().encode("UTF-8")
                paramGet.SetString("CurrentPie", text)
            except TypeError:
                text = pieGroup.checkedAction().text()
                paramGet.SetString("CurrentPie", text)
            PieMenuInstance.hide()
            PieMenuInstance.showAtMouse(notKeyTriggered=True)


        def onMenuToolBar():
            """Handle the toolbar menu setup event."""
            menuToolBar.clear()
            if paramGet.GetBool("ToolBar"):
                text = paramGet.GetString("ToolBar")
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
                    menu.aboutToShow.connect(lambda sender=menu: \
                        onMenuToolbarGroup(sender))
                    menuToolBar.addMenu(menu)
                else:
                    pass


        def isActualPie(text):
            """Check if the given text corresponds to the current toolbar (or menu)."""
            if paramGet.GetBool("ToolBar"):
                entry = paramGet.GetString("ToolBar")
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
                paramGet.SetBool("ToolBar", True)
            elif sender.text() == "Save":
                newPieGroup = createPie(sender.data())
            else:
                return
            workbenches = []
            commands = []
            if sender.text() == "Save":
                # write persistent commands
                getGuiToolButtonData(sender.data(), None, commands, None)
                newPieGroup.SetString("ToolList", ".,.".join(commands))
                newPieGroup.SetString("Shape", "Pie")
            elif sender.text() == "Show":
                # write persistent toolbar and its workbenches
                getGuiToolButtonData(sender.data(), None, None, workbenches)
                toolbar_desc = ", ".join(workbenches)
                toolbar_desc = toolbar_desc + ': ' + sender.data()
                paramGet.SetString("ToolBar", toolbar_desc)
                PieMenuInstance.hide()
                PieMenuInstance.showAtMouse(notKeyTriggered=True)


        def onPrefButton():
            """Handle the preferences button event."""
            PieMenuInstance.hide()
            onControl()

        #### QuickMenu ####
        mw = Gui.getMainWindow()
        styleCurrentTheme = getStyle()

        menu = QtGui.QMenu(mw)
        menu.setObjectName("styleQuickMenu")
        menu.setStyleSheet(styleCurrentTheme)

        actionContext = QtGui.QAction(menu)
        actionContext.setText(translate("QuickMenu", "Global context"))
        actionContext.setCheckable(True)
        actionContext.setChecked(paramGet.GetBool("EnableContext"))
        actionContext.triggered.connect(onActionContext)

        menuPieMenu = QtGui.QMenu()
        menuPieMenu.setTitle(translate("QuickMenu", "PieMenu"))
        menuPieMenu.aboutToShow.connect(pieList)

        pieGroup = QtGui.QActionGroup(menu)
        pieGroup.setExclusive(True)
        pieGroup.triggered.connect(onPieGroup)

        menuToolBar = QtGui.QMenu()
        menuToolBar.setObjectName("styleQuickMenuItem")
        menuToolBar.setTitle(translate("QuickMenu", "ToolBar"))
        menuToolBar.setStyleSheet(styleCurrentTheme)
        menuToolBar.aboutToShow.connect(onMenuToolBar)

        toolbarGroup = QtGui.QMenu()
        toolbarGroupOps = QtGui.QActionGroup(toolbarGroup)
        toolbarGroupOps.setExclusive(True)
        toolbarGroup.triggered.connect(onToolbarGroup)

        prefAction = QtGui.QAction(menu)
        prefAction.setIconText(translate("QuickMenu", "Preferences"))

        prefButton = QtGui.QToolButton()
        prefButton.setDefaultAction(prefAction)
        prefButton.clicked.connect(onPrefButton)

        prefButtonWidgetAction = QtGui.QWidgetAction(menu)
        prefButtonWidgetAction.setDefaultWidget(prefButton)

        menu.addAction(actionContext)
        menu.addSeparator()
        menu.addMenu(menuPieMenu)
        menu.addMenu(menuToolBar)
        menu.addSeparator()
        menu.addAction(prefButtonWidgetAction)

        icon = iconSize(buttonSize)
        radius = radiusSize(buttonSize)

        button = QtGui.QToolButton()
        button.setObjectName("styleButtonMenu")
        button.setMenu(menu)
        button.setProperty("ButtonX", 0) # +, right
        button.setProperty("ButtonY", 32) # +, down
        button.setGeometry(0, 0, buttonSize, buttonSize)
        button.setIconSize(QtCore.QSize(icon, icon))
        button.setStyleSheet(styleCurrentTheme + radius)
        button.setPopupMode(QtGui.QToolButton.ToolButtonPopupMode.InstantPopup)
        return button

    ### END QuickMenu   Def ###

    #### Preferences dialog ####
    def onControl():
        """Initializes the preferences dialog."""
        keyValue = None
        try:
            keyValue = paramGet.GetString("CurrentPie").decode("UTF-8")
        except AttributeError:
            keyValue = paramGet.GetString("CurrentPie")
        cBoxUpdate(keyValue)

        buttonList()
        tabs.setCurrentIndex(0)

        for i in mw.findChildren(QtGui.QDialog):
            if i.objectName() == "PieMenuPreferences":
                i.deleteLater()
            else:
                pass

        contextPieMenu = getCheckContext()
        settingContextGroup.setChecked(contextPieMenu)

        pieMenuDialog.show()
        shape = getShape(cBox.currentText())
        onShape(shape)
        updatePiemenuPreview()

        #### END Preferences dialog ####

    ####END Functions Def ####

    #### Main code ####

    #### MainWindow Preferences Dialog ####
    #### group PieMenu ####
    tabs = QtGui.QTabWidget()
    tabToolBar = QtGui.QTabWidget()

    #### layout PieMenu Settings ####
    buttonIconPieMenu = QtGui.QToolButton()
    buttonIconPieMenu.setToolTip(translate("PieMenuTab", "Set icon to current PieMenu, FreeCAD restart needed"))
    buttonIconPieMenu.setMinimumHeight(30)
    buttonIconPieMenu.setMinimumWidth(30)
    buttonIconPieMenu.clicked.connect(onButtonIconPieMenu)

    cBox = QtGui.QComboBox()
    cBox.setMinimumHeight(28)
    cBox.currentIndexChanged.connect(onPieChange)
    cBox.setMinimumWidth(140)

    buttonAddPieMenu = QtGui.QToolButton()
    buttonAddPieMenu.setIcon(QtGui.QIcon(iconAdd))
    buttonAddPieMenu.setToolTip(translate("PieMenuTab", "Add new pie menu"))
    buttonAddPieMenu.setMinimumHeight(30)
    buttonAddPieMenu.setMinimumWidth(30)
    buttonAddPieMenu.clicked.connect(onButtonAddPieMenu)

    buttonRemovePieMenu = QtGui.QToolButton()
    buttonRemovePieMenu.setIcon(QtGui.QIcon(iconRemove))
    buttonRemovePieMenu.setToolTip(translate("PieMenuTab", "Remove current pie menu"))
    buttonRemovePieMenu.setMinimumHeight(30)
    buttonRemovePieMenu.setMinimumWidth(30)
    buttonRemovePieMenu.clicked.connect(onButtonRemovePieMenu)

    buttonRenamePieMenu = QtGui.QToolButton()
    buttonRenamePieMenu.setToolTip(translate("PieMenuTab", "Rename current pie menu"))
    buttonRenamePieMenu.setIcon(QtGui.QIcon(iconRename))
    buttonRenamePieMenu.setMinimumHeight(30)
    buttonRenamePieMenu.setMinimumWidth(30)
    buttonRenamePieMenu.clicked.connect(onButtonRenamePieMenu)

    buttonCopyPieMenu = QtGui.QToolButton()
    buttonCopyPieMenu.setToolTip(translate("PieMenuTab", "Copy current pie menu"))
    buttonCopyPieMenu.setIcon(QtGui.QIcon(iconCopy))
    buttonCopyPieMenu.setMinimumHeight(30)
    buttonCopyPieMenu.setMinimumWidth(30)
    buttonCopyPieMenu.clicked.connect(onButtonCopyPieMenu)

    buttonExistingToolBar = QtGui.QPushButton(translate("PieMenuTab", "Workbenches toolbars..."))
    buttonExistingToolBar.setToolTip(translate("PieMenuTab", "Add one of the existing workbenches toolbars"))
    buttonExistingToolBar.setIcon(QtGui.QIcon(iconRight))
    buttonExistingToolBar.setMinimumHeight(30)
    buttonExistingToolBar.setMinimumWidth(60)
    buttonExistingToolBar.clicked.connect(onButtonToolBar)

    layoutAddRemove = QtGui.QHBoxLayout()
    layoutAddRemove.addWidget(buttonIconPieMenu)
    layoutAddRemove.addWidget(cBox)
    layoutAddRemove.addWidget(buttonAddPieMenu)
    layoutAddRemove.addWidget(buttonRemovePieMenu)
    layoutAddRemove.addWidget(buttonRenamePieMenu)
    layoutAddRemove.addWidget(buttonCopyPieMenu)

    piemenuBoxGroup = QGroupBox()
    piemenuBoxGroup.setLayout(QtGui.QHBoxLayout())
    piemenuBoxGroup.layout().addLayout(layoutAddRemove)
    piemenuBoxGroup.layout().addWidget(buttonExistingToolBar)

    pieMenuTab = QtGui.QWidget()
    pieMenuTabLayout = QtGui.QVBoxLayout()
    pieMenuTab.setLayout(pieMenuTabLayout)

    checkboxDefaultPie = QCheckBox()
    checkboxDefaultPie.setCheckable(True)
    checkboxDefaultPie.stateChanged.connect(lambda state: onDefaultPie(state))

    labelDefaultPie = QtGui.QLabel(translate("GlobalSettingsTab", "Set this PieMenu as default"))
    labelDefaultPie.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)

    layoutDefaultPieLeft = QtGui.QHBoxLayout()
    layoutDefaultPieLeft.addWidget(checkboxDefaultPie)
    layoutDefaultPieLeft.addWidget(labelDefaultPie)
    layoutDefaultPieLeft.addStretch(1)
    layoutDefaultPie = QtGui.QHBoxLayout()
    layoutDefaultPie.addLayout(layoutDefaultPieLeft, 1)

    labelWbForPieMenu = QtGui.QLabel(translate("PieMenuTab", "Workbench associated to this PieMenu:"))
    labelWbForPieMenu.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)

    comboWbForPieMenu = QtGui.QComboBox()
    comboWbForPieMenu.setMinimumWidth(160)
    comboWbForPieMenu.currentIndexChanged.connect(onWbForPieMenu)

    layoutWbForPieMenuLeft = QtGui.QHBoxLayout()
    layoutWbForPieMenuLeft.addWidget(labelWbForPieMenu)
    layoutWbForPieMenuRight = QtGui.QHBoxLayout()
    layoutWbForPieMenuRight.addWidget(comboWbForPieMenu)
    layoutWbForPieMenu = QtGui.QHBoxLayout()
    layoutWbForPieMenu.addLayout(layoutWbForPieMenuLeft, 1)
    layoutWbForPieMenu.addLayout(layoutWbForPieMenuRight, 1)

    piemenuSettingGroup = QGroupBox(translate("PieMenuTab", "Assignment"))
    piemenuSettingGroup.setLayout(QtGui.QVBoxLayout())
    piemenuSettingGroup.layout().addLayout(layoutDefaultPie)
    piemenuSettingGroup.layout().addLayout(layoutWbForPieMenu)

    ## group Shape ####
    labelShape = QtGui.QLabel(translate("PieMenuTab", "Shape:"))
    labelShape.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)

    comboShape = QtGui.QComboBox()
    comboShape.setMinimumWidth(100)
    comboShape.currentIndexChanged.connect(setShape)

    layoutShapeLeft = QtGui.QHBoxLayout()
    layoutShapeLeft.addWidget(labelShape)
    layoutShapeRight = QtGui.QHBoxLayout()
    layoutShapeRight.addWidget(comboShape)
    layoutShape = QtGui.QHBoxLayout()
    layoutShape.addLayout(layoutShapeLeft, 1)
    layoutShape.addLayout(layoutShapeRight, 1)

    labelRadius = QtGui.QLabel(translate("PieMenuTab", "Pie size:"))
    labelRadius.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)

    spinRadius = QtGui.QSpinBox()
    spinRadius.setMaximum(9999)
    spinRadius.setMinimumWidth(160)
    spinRadius.valueChanged.connect(onSpinRadius)

    layoutRadiusLeft = QtGui.QHBoxLayout()
    layoutRadiusLeft.addWidget(labelRadius)
    layoutRadiusRight = QtGui.QHBoxLayout()
    layoutRadiusRight.addWidget(spinRadius)
    layoutRadius = QtGui.QHBoxLayout()
    layoutRadius.addLayout(layoutRadiusLeft, 1)
    layoutRadius.addLayout(layoutRadiusRight, 1)

    labelButton = QtGui.QLabel(translate("PieMenuTab", "Button size:"))
    labelButton.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)

    spinButton = QtGui.QSpinBox()
    spinButton.setMaximum(120)
    spinButton.setMinimum(16)
    spinButton.setMinimumWidth(160)
    spinButton.valueChanged.connect(onSpinButton)

    layoutButtonLeft = QtGui.QHBoxLayout()
    layoutButtonLeft.addWidget(labelButton)
    layoutButtonRight = QtGui.QHBoxLayout()
    layoutButtonRight.addWidget(spinButton)
    layoutButton = QtGui.QHBoxLayout()
    layoutButton.addLayout(layoutButtonLeft, 1)
    layoutButton.addLayout(layoutButtonRight, 1)

    labelIconSpacing = QtGui.QLabel(translate("PieMenuTab", "Icon spacing:"))
    labelIconSpacing.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)

    spinIconSpacing = QtGui.QSpinBox()
    spinIconSpacing.setMaximum(200)
    spinIconSpacing.setMinimumWidth(0)
    spinIconSpacing.valueChanged.connect(onIconSpacing)

    layoutIconSpacingLeft = QtGui.QHBoxLayout()
    layoutIconSpacingLeft.addWidget(labelIconSpacing)
    layoutIconSpacingRight = QtGui.QHBoxLayout()
    layoutIconSpacingRight.addWidget(spinIconSpacing)
    layoutIconSpacing = QtGui.QHBoxLayout()
    layoutIconSpacing.addLayout(layoutIconSpacingLeft, 1)
    layoutIconSpacing.addLayout(layoutIconSpacingRight, 1)

    labelNumColumn = QtGui.QLabel(translate("PieMenuTab", "Number of columns:"))
    labelNumColumn.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)

    spinNumColumn = QtGui.QSpinBox()
    spinNumColumn.setMaximum(12)
    spinNumColumn.setMinimumWidth(120)
    spinNumColumn.valueChanged.connect(onNumColumn)

    layoutColumnLeft = QtGui.QHBoxLayout()
    layoutColumnLeft.addWidget(labelNumColumn)
    layoutColumnRight = QtGui.QHBoxLayout()
    layoutColumnRight.addWidget(spinNumColumn)
    layoutColumn = QtGui.QHBoxLayout()
    layoutColumn.addLayout(layoutColumnLeft, 1)
    layoutColumn.addLayout(layoutColumnRight, 1)

    labelCommandPerCircle = QtGui.QLabel(translate("PieMenuTab", "Command for first circle:"))
    labelCommandPerCircle.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)

    spinCommandPerCircle = QtGui.QSpinBox()
    spinCommandPerCircle.setMaximum(20)
    spinCommandPerCircle.setMinimum(2)
    spinCommandPerCircle.setMinimumWidth(0)
    spinCommandPerCircle.valueChanged.connect(onCommandPerCircle)

    layoutCommandPerCircleLeft = QtGui.QHBoxLayout()
    layoutCommandPerCircleLeft.addWidget(labelCommandPerCircle)
    layoutCommandPerCircleRight = QtGui.QHBoxLayout()
    layoutCommandPerCircleRight.addWidget(spinCommandPerCircle)
    layoutCommandPerCircle = QtGui.QHBoxLayout()
    layoutCommandPerCircle.addLayout(layoutCommandPerCircleLeft, 1)
    layoutCommandPerCircle.addLayout(layoutCommandPerCircleRight, 1)

    checkboxDisplayCommandName = QCheckBox()
    checkboxDisplayCommandName.setCheckable(True)
    checkboxDisplayCommandName.stateChanged.connect(lambda state: onDisplayCommandName(state))

    labeldisplayCommandName = QtGui.QLabel(translate("PieMenuTab", "Show command names"))
    labeldisplayCommandName.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)

    layoutDisplayCommandNameLeft = QtGui.QHBoxLayout()
    layoutDisplayCommandNameLeft.addWidget(checkboxDisplayCommandName)
    layoutDisplayCommandNameLeft.addWidget(labeldisplayCommandName)
    layoutDisplayCommandNameLeft.addStretch(1)
    layoutDisplayCommandName = QtGui.QHBoxLayout()
    layoutDisplayCommandName.addLayout(layoutDisplayCommandNameLeft, 1)

    checkboxDisplayPreselect = QCheckBox()
    checkboxDisplayPreselect.setCheckable(True)
    checkboxDisplayPreselect.stateChanged.connect(lambda state: onDisplayPreselect(state))

    labelDisplayPreselect = QtGui.QLabel(translate("PieMenuTab", "Show preselect button"))
    labelDisplayPreselect.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)

    layoutDisplayPreselectLeft = QtGui.QHBoxLayout()
    layoutDisplayPreselectLeft.addWidget(checkboxDisplayPreselect)
    layoutDisplayPreselectLeft.addWidget(labelDisplayPreselect)
    layoutDisplayPreselectLeft.addStretch(1)
    layoutDisplayPreselect = QtGui.QHBoxLayout()
    layoutDisplayPreselect.addLayout(layoutDisplayPreselectLeft, 1)

    shapeGroup = QGroupBox(translate("PieMenuTab", "Shape"))
    shapeGroup.setLayout(QtGui.QVBoxLayout())
    shapeGroup.layout().addLayout(layoutShape)
    shapeGroup.layout().addLayout(layoutRadius)
    shapeGroup.layout().addLayout(layoutButton)
    shapeGroup.layout().addLayout(layoutIconSpacing)
    shapeGroup.layout().addLayout(layoutColumn)
    shapeGroup.layout().addLayout(layoutCommandPerCircle)
    shapeGroup.layout().addLayout(layoutDisplayCommandName)
    shapeGroup.layout().addLayout(layoutDisplayPreselect)

    ### group Trigger Mode ####
    radioButtonPress = QtGui.QRadioButton(translate("GlobalSettingsTab", "Press"))
    radioButtonPress.toggled.connect(lambda checked, data="Press": setTriggerMode(data))

    radioButtonHover = QtGui.QRadioButton(translate("GlobalSettingsTab", "Hover"))
    radioButtonHover.toggled.connect(lambda checked, data="Hover":  setTriggerMode(data))

    radioGroup = QtGui.QButtonGroup()
    radioGroup.addButton(radioButtonPress)
    radioGroup.addButton(radioButtonHover)

    layoutActionHoverButton = QtGui.QVBoxLayout()
    layoutActionHoverButton.addWidget(radioButtonPress)
    layoutActionHoverButton.addWidget(radioButtonHover)

    labelHoverDelay = QtGui.QLabel(translate("GlobalSettingsTab", "Hover delay (ms):"))
    labelHoverDelay.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)

    spinHoverDelay = QtGui.QSpinBox()
    spinHoverDelay.setMaximum(999)
    spinHoverDelay.setMinimumWidth(90)
    spinHoverDelay.valueChanged.connect(onSpinHoverDelay)

    layoutTriggerButtonLeft = QtGui.QHBoxLayout()
    layoutTriggerButtonLeft.addLayout(layoutActionHoverButton)
    layoutTriggerButtonLeft.addStretch(1)
    layoutTriggerButtonRight = QtGui.QHBoxLayout()
    layoutTriggerButtonRight.addWidget(labelHoverDelay)
    layoutTriggerButtonRight.addStretch(1)
    layoutTriggerButtonRight.addWidget(spinHoverDelay)
    layoutTriggerButton = QtGui.QHBoxLayout()
    layoutTriggerButton.addLayout(layoutTriggerButtonLeft, 1)
    layoutTriggerButton.addLayout(layoutTriggerButtonRight, 1)

    triggerModeGroup = QGroupBox(translate("PieMenuTab", "Trigger mode"))
    triggerModeGroup.setLayout(QtGui.QVBoxLayout())
    triggerModeGroup.layout().addLayout(layoutTriggerButton)

    ### group Tools Shortcuts ####
    toolShortcutGroup = QGroupBox()
    toolShortcutGroup.setCheckable(True)
    toolShortcutGroup.toggled.connect(lambda state: onEnableShortcut(state))

    checkboxDisplayShortcut = QCheckBox()
    checkboxDisplayShortcut.setCheckable(True)
    checkboxDisplayShortcut.stateChanged.connect(lambda state: onDisplayShortcut(state))

    labelDisplayShortcut = QtGui.QLabel(translate("PieMenuTab", "Display tools shortcut"))
    labelDisplayShortcut.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)

    labelShortcutSize = QtGui.QLabel(translate("PieMenuTab", "Font size:"))
    labelShortcutSize.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)

    spinShortcutLabelSize = QtGui.QSpinBox()
    spinShortcutLabelSize.setMinimum(6)
    spinShortcutLabelSize.setMaximum(50)
    spinShortcutLabelSize.setMinimumWidth(90)
    spinShortcutLabelSize.valueChanged.connect(onSpinShortcutLabelSize)

    layoutDisplayShortcutLeft = QtGui.QHBoxLayout()
    layoutDisplayShortcutLeft.addWidget(checkboxDisplayShortcut)
    layoutDisplayShortcutLeft.addWidget(labelDisplayShortcut)
    layoutDisplayShortcutLeft.addStretch(1)
    layoutDisplayShortcutRight = QtGui.QHBoxLayout()
    layoutDisplayShortcutRight.addWidget(labelShortcutSize)
    layoutDisplayShortcutRight.addWidget(spinShortcutLabelSize)
    layoutDisplayShortcut = QtGui.QHBoxLayout()
    layoutDisplayShortcut.addLayout(layoutDisplayShortcutLeft, 1)
    layoutDisplayShortcut.addLayout(layoutDisplayShortcutRight, 1)

    enableShortcut = getParameterGroup(cBox.currentText(), "Bool", "EnableShorcut")
    if enableShortcut == "":
        enableShortcut = False

    # keep this line here
    buttonListWidget = QtGui.QTableWidget()

    toolShortcutGroup.setTitle(translate("PieMenuTab", "Tools shortcuts"))
    toolShortcutGroup.setCheckable(True)
    toolShortcutGroup.setChecked(enableShortcut)
    toolShortcutGroup.setLayout(QtGui.QVBoxLayout())
    toolShortcutGroup.layout().addLayout(layoutDisplayShortcut)

    #### group Individual Shortcut ####
    shortcutKey = getParameterGroup(cBox.currentText(), "String", "ShortcutKey")

    labelShortcut = QLabel()
    labelShortcut.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
    labelShortcut.setText(translate("PieMenuTab", "Current shortcut: ") + shortcutKey)

    shortcutLineEdit = CustomLineEdit()
    shortcutLineEdit.setText(shortcutKey)

    assignShortcutButton = QtGui.QPushButton(translate("GlobalSettingsTab", "Assign"))
    assignShortcutButton.clicked.connect(lambda: updateShortcutKey(shortcutLineEdit.text()))

    deleteShortcutButton = QtGui.QPushButton()
    deleteShortcutButton.setMaximumWidth(40)
    deleteShortcutButton.setIcon(QtGui.QIcon.fromTheme(iconBackspace))
    deleteShortcutButton.clicked.connect(lambda: updateShortcutKey(""))

    layoutShortcut = QtGui.QHBoxLayout()
    layoutShortcut.addWidget(labelShortcut)
    layoutShortcut.addStretch(1)
    layoutShortcut.addWidget(shortcutLineEdit)
    layoutShortcut.addWidget(assignShortcutButton)
    layoutShortcut.addWidget(deleteShortcutButton)

    infoShortcut = QLabel()
    infoShortcut.setText('')

    layoutInfoShortcut = QtGui.QHBoxLayout()
    layoutInfoShortcut.addWidget(infoShortcut)
    layoutInfoShortcut.addStretch(1)

    pieMenuTabLayout.insertWidget(0, piemenuSettingGroup)
    pieMenuTabLayout.insertWidget(1, shapeGroup)
    pieMenuTabLayout.insertWidget(2, triggerModeGroup)
    pieMenuTabLayout.insertWidget(3, toolShortcutGroup)
    pieMenuTabLayout.insertSpacing(4, 10)
    pieMenuTabLayout.insertLayout(5, layoutShortcut)

    #### Tool list container ####
    searchLayout = QHBoxLayout()
    searchLineEdit = QLineEdit()
    searchLineEdit.setPlaceholderText(translate("ToolsTab", "Search"))
    searchLineEdit.textChanged.connect(searchInToolList)

    clearButton = QtGui.QToolButton()
    clearButton.setToolTip(translate("ToolsTab", "Clear search"))
    clearButton.setMaximumWidth(40)
    clearButton.setIcon(QtGui.QIcon.fromTheme(iconBackspace))
    clearButton.clicked.connect(searchLineEdit.clear)

    searchLayout.addWidget(searchLineEdit)
    searchLayout.addWidget(clearButton)

    toolListWidget = QtGui.QListWidget()
    toolListWidget.setSortingEnabled(True)
    toolListWidget.sortItems(QtCore.Qt.AscendingOrder)
    toolListWidget.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)

    toolListWidget.itemChanged.connect(onToolListWidget)

    toolListLayout = QVBoxLayout()
    toolListLayout.addLayout(searchLayout)
    toolListLayout.addWidget(toolListWidget)

    widgetContainer = QWidget()
    widgetContainer.setLayout(toolListLayout)
    widgetContainer.setMinimumHeight(380)

    #### Tab ContextTab ####
    contextTab = QtGui.QWidget()
    contextTabLayout = QtGui.QVBoxLayout()
    contextTab.setLayout(contextTabLayout)

    vertexItem = QtGui.QTableWidgetItem()
    vertexItem.setText(translate("ContextTab", "Vertex"))
    vertexItem.setToolTip(translate("ContextTab", "Set desired operator and vertex number"))
    vertexItem.setFlags(QtCore.Qt.ItemIsEnabled)

    edgeItem = QtGui.QTableWidgetItem()
    edgeItem.setText(translate("ContextTab", "Edge"))
    edgeItem.setToolTip(translate("ContextTab", "Set desired operator and edge number"))
    edgeItem.setFlags(QtCore.Qt.ItemIsEnabled)

    faceItem = QtGui.QTableWidgetItem()
    faceItem.setText(translate("ContextTab", "Face"))
    faceItem.setToolTip(translate("ContextTab", "Set desired operator and face number"))
    faceItem.setFlags(QtCore.Qt.ItemIsEnabled)

    objectItem = QtGui.QTableWidgetItem()
    objectItem.setText(translate("ContextTab", "Object"))
    objectItem.setToolTip(translate("ContextTab", "Set desired operator and object number"))
    objectItem.setFlags(QtCore.Qt.ItemIsEnabled)

    vertexComboBox = comboBox("VertexSign")
    edgeComboBox = comboBox("EdgeSign")
    faceComboBox = comboBox("FaceSign")
    objectComboBox = comboBox("ObjectSign")

    vertexSpin = spinBox("VertexValue")
    edgeSpin = spinBox("EdgeValue")
    faceSpin = spinBox("FaceValue")
    objectSpin = spinBox("ObjectValue")

    contextTable = QtGui.QTableWidget(4, 3)
    contextTable.setMaximumHeight(120)
    contextTable.setFrameStyle(QtGui.QFrame.NoFrame)
    contextTable.verticalHeader().setVisible(False)
    contextTable.horizontalHeader().setVisible(False)

    try:
        contextTable.verticalHeader().setResizeMode(QtGui.QHeaderView.Stretch)
        contextTable.horizontalHeader().setResizeMode(QtGui.QHeaderView.Stretch)
    except AttributeError:
        contextTable.verticalHeader().setSectionResizeMode(QtGui.QHeaderView.Stretch)
        contextTable.horizontalHeader().setSectionResizeMode(QtGui.QHeaderView.Stretch)

    contextTable.setItem(0, 0, vertexItem)
    contextTable.setCellWidget(0, 1, vertexComboBox)
    contextTable.setCellWidget(0, 2, vertexSpin)

    contextTable.setItem(1, 0, edgeItem)
    contextTable.setCellWidget(1, 1, edgeComboBox)
    contextTable.setCellWidget(1, 2, edgeSpin)

    contextTable.setItem(2, 0, faceItem)
    contextTable.setCellWidget(2, 1, faceComboBox)
    contextTable.setCellWidget(2, 2, faceSpin)

    contextTable.setItem(3, 0, objectItem)
    contextTable.setCellWidget(3, 1, objectComboBox)
    contextTable.setCellWidget(3, 2, objectSpin)

    resetContextButton = QtGui.QToolButton()
    resetContextButton.setIcon(QtGui.QIcon(iconReset))
    resetContextButton.setToolTip(translate("ContextTab", "Reset to defaults"))
    resetContextButton.setMinimumHeight(30)
    resetContextButton.setMinimumWidth(30)
    resetContextButton.setEnabled(False)
    resetContextButton.clicked.connect(onResetContextButton)

    resetLayout = QtGui.QHBoxLayout()
    resetLayout.addStretch(1)
    resetLayout.addWidget(resetContextButton)

    checkboxTriggerContext = QCheckBox()
    checkboxTriggerContext.setCheckable(True)
    checkboxTriggerContext.stateChanged.connect(lambda state: onTriggerContext(state))

    labelTriggerContext = QtGui.QLabel(translate("ContextTab", "Immediate triggering when conditions are met"))
    labelTriggerContext.setToolTip(translate("ContextTab", "The PieMenu will open immediately once the contextual selection conditions are met."))
    labelTriggerContext.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)

    triggerContextLayout = QtGui.QHBoxLayout()
    triggerContextLayout.addWidget(checkboxTriggerContext)
    triggerContextLayout.addWidget(labelTriggerContext)
    triggerContextLayout.addStretch(1)

    settingContextGroup = QGroupBox(translate("GlobalSettingsTab", "Context"))
    settingContextGroup.setCheckable(True)

    labelContextWorkbench = QtGui.QLabel(translate("ContextTab", "Set workbench for these contextual selection conditions"))

    comboContextWorkbench = QtGui.QComboBox()
    comboContextWorkbench.setMinimumWidth(160)
    comboContextWorkbench.currentIndexChanged.connect(setContextWorkbench)

    contextWorkbenchLayout = QtGui.QHBoxLayout()
    contextWorkbenchLayout.addWidget(labelContextWorkbench)
    contextWorkbenchLayout.addStretch(1)
    contextWorkbenchLayout.addWidget(comboContextWorkbench)

    settingContextGroup.setLayout(QtGui.QVBoxLayout())
    settingContextGroup.layout().addLayout(contextWorkbenchLayout)
    settingContextGroup.layout().addWidget(contextTable)
    settingContextGroup.layout().addLayout(resetLayout)
    settingContextGroup.layout().addLayout(triggerContextLayout)
    settingContextGroup.toggled.connect(lambda state: onCheckContext(state))

    contextTabLayout.insertWidget(1, settingContextGroup)
    contextTabLayout.addStretch(1)

    #### Tab ToolBar ####
    buttonBackToSettings = QtGui.QPushButton(translate("ToolBarTab", "Return to settings..."))
    buttonBackToSettings.setToolTip(translate("ToolBarTab", "Return to general settings"))
    buttonBackToSettings.setIcon(QtGui.QIcon(iconLeft))
    buttonBackToSettings.setMinimumHeight(30)
    buttonBackToSettings.setMinimumWidth(60)
    buttonBackToSettings.clicked.connect(onBackToSettings)
    buttonBackToSettings.setVisible(False)

    listToolBar = QtGui.QListWidget()
    listToolBar.setSortingEnabled(True)
    listToolBar.sortItems(QtCore.Qt.AscendingOrder)
    listToolBar.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
    listToolBar.setMinimumSize(QSize(385, 460))
    listToolBar.itemSelectionChanged.connect(showListToolBar)

    listToolBarLayout = QtGui.QVBoxLayout()
    listToolBarLayout.addWidget(listToolBar)
    labelAddToolBar = QLabel(translate("ToolBarTab", "Add the selected toolbar as a new PieMenu"))

    buttonAddToolBar = QtGui.QToolButton()
    buttonAddToolBar.setToolTip(translate("ToolBarTab", "Add selected ToolBar as PieMenu"))
    buttonAddToolBar.setIcon(QtGui.QIcon(iconAdd))
    buttonAddToolBar.setMinimumHeight(30)
    buttonAddToolBar.setMinimumWidth(30)
    buttonAddToolBar.clicked.connect(onAddToolBar)

    labelAddToolBarLayout = QtGui.QHBoxLayout()
    labelAddToolBarLayout.addWidget(labelAddToolBar)
    labelAddToolBarLayout.addStretch(1)
    labelAddToolBarLayout.addWidget(buttonAddToolBar)

    addToolBarGroup = QGroupBox(translate("ToolBarTab", "ToolBars "))
    addToolBarGroup.setLayout(QtGui.QVBoxLayout())
    addToolBarGroup.layout().addLayout(listToolBarLayout)
    addToolBarGroup.layout().addStretch(1)
    addToolBarGroup.layout().addLayout(labelAddToolBarLayout)

    toolBarTabLayout = QtGui.QVBoxLayout()
    toolBarTabLayout.addWidget(addToolBarGroup)

    toolBarTab = QtGui.QWidget()
    toolBarTab.setLayout(toolBarTabLayout)

    #### Tab Global Settings ####
    settingsTab = QtGui.QWidget()
    settingsTabLayout = QtGui.QVBoxLayout()
    settingsTab.setLayout(settingsTabLayout)

    tabs.addTab(pieMenuTab, translate("PieMenuTab", "PieMenu"))
    tabs.addTab(widgetContainer, translate("ToolsTab", "Tools"))
    tabs.addTab(contextTab, translate("ContextTab", "Context"))
    tabs.addTab(settingsTab, translate("GlobalSettingsTab", "Global settings"))

    tabToolBar.addTab(toolBarTab, translate("ToolBarsTab", "ToolBars"))

    #### buttons actions list ####
    buttonAddSeparator = QtGui.QToolButton()
    buttonAddSeparator.setIcon(QtGui.QIcon(iconAddSeparator))
    buttonAddSeparator.setToolTip(translate("Commands", "Add separator"))
    buttonAddSeparator.setMinimumHeight(30)
    buttonAddSeparator.setMinimumWidth(30)
    buttonAddSeparator.clicked.connect(onButtonAddSeparator)

    buttonRemoveCommand = QtGui.QToolButton()
    buttonRemoveCommand.setIcon(QtGui.QIcon(iconRemoveCommand))
    buttonRemoveCommand.setToolTip(translate("Commands", "Remove selected command"))
    buttonRemoveCommand.setMinimumHeight(30)
    buttonRemoveCommand.setMinimumWidth(30)
    buttonRemoveCommand.clicked.connect(onButtonRemoveCommand)

    buttonUp = QtGui.QToolButton()
    buttonUp.setIcon(QtGui.QIcon(iconUp))
    buttonUp.setToolTip(translate("Commands", "Move selected command up"))
    buttonUp.setMinimumHeight(30)
    buttonUp.setMinimumWidth(30)
    buttonUp.clicked.connect(onButtonUp)

    buttonDown = QtGui.QToolButton()
    buttonDown.setIcon(QtGui.QIcon(iconDown))
    buttonDown.setToolTip(translate("Commands", "Move selected command down"))
    buttonDown.setMinimumHeight(30)
    buttonDown.setMinimumWidth(30)
    buttonDown.clicked.connect(onButtonDown)

    buttonsLayout = QtGui.QHBoxLayout()
    buttonsLayout.addStretch(1)
    buttonsLayout.addWidget(buttonAddSeparator)
    buttonsLayout.addWidget(buttonRemoveCommand)
    buttonsLayout.addWidget(buttonDown)
    buttonsLayout.addWidget(buttonUp)

    piemenuWidget = QtGui.QWidget()
    piemenuLayout = QtGui.QHBoxLayout()
    piemenuLayout.addWidget(piemenuBoxGroup)
    piemenuLayout.addWidget(buttonBackToSettings)
    piemenuLayout.addStretch(1)
    piemenuWidget.setLayout(piemenuLayout)

    buttonListWidget.setColumnCount(2)
    buttonListWidget.setHorizontalHeaderLabels([translate("PieMenuTab", "Shortcut"), translate("PieMenuTab", "Action")])
    buttonListWidget.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
    buttonListWidget.verticalHeader().setVisible(False)
    buttonListWidget.horizontalHeaderItem(0).setTextAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter)
    buttonListWidget.horizontalHeaderItem(1).setTextAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
    buttonListWidget.horizontalHeader().setSectionResizeMode(QtGui.QHeaderView.Interactive)
    buttonListWidget.setColumnWidth(0, 60)
    buttonListWidget.horizontalHeader().setMinimumSectionSize(60)
    buttonListWidget.horizontalHeader().setStretchLastSection(True)

    pieButtons = QtGui.QWidget()
    pieButtonsLayout = QtGui.QVBoxLayout()
    pieButtons.setLayout(pieButtonsLayout)
    pieButtonsLayout.setContentsMargins(0, 0, 0, 0)
    pieButtonsLayout.addWidget(buttonListWidget)
    pieButtonsLayout.insertLayout(1, buttonsLayout)

    showPreviewWidget = QtGui.QTableWidget()
    showPreviewWidget.setColumnCount(1)
    showPreviewWidget.setHorizontalHeaderLabels([translate("PieMenuTab", "Preview")])
    showPreviewWidget.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
    showPreviewWidget.verticalHeader().setVisible(False)
    showPreviewWidget.horizontalHeader().setSectionResizeMode(QtGui.QHeaderView.Interactive)
    showPreviewWidget.horizontalHeader().setMinimumSectionSize(100)
    showPreviewWidget.horizontalHeader().setStretchLastSection(True)

    showPiemenu = QtGui.QWidget()
    showPiemenuLayout = QtGui.QVBoxLayout()
    showPiemenu.setLayout(showPiemenuLayout)
    showPiemenuLayout.setContentsMargins(0, 0, 0, 0)
    showPiemenuLayout.addWidget(showPreviewWidget)

    #### Main Layout####
    vSplitter = QtGui.QSplitter()
    vSplitter.insertWidget(1, tabs)
    vSplitter.insertWidget(2, toolBarTab)
    vSplitter.insertWidget(3, pieButtons)
    vSplitter.insertWidget(4, showPiemenu)

    preferencesWidget = QtGui.QWidget()
    preferencesLayout = QtGui.QVBoxLayout()
    preferencesLayout.setContentsMargins(0, 0, 0, 0)
    preferencesWidget.setLayout(preferencesLayout)
    preferencesLayout.addWidget(piemenuWidget)
    preferencesLayout.addWidget(vSplitter)

    info_button = QtGui.QPushButton()
    info_button.setToolTip(translate("MainWindow", "About"))
    info_button.setMaximumWidth(80)
    info_button.setIcon(QtGui.QIcon.fromTheme(iconInfo))
    info_button.clicked.connect(infoPopup)

    doc_button = QtGui.QPushButton(translate("MainWindow", "Documentation"))
    doc_button.setToolTip(translate("MainWindow", "Documentation"))
    doc_button.setIcon(QtGui.QIcon.fromTheme(iconDocumentation))
    doc_button.clicked.connect(documentationLink)

    close_button = QtGui.QPushButton(translate("MainWindow", "Close"))
    close_button.setMaximumWidth(120)

    button_row_layout = QtGui.QHBoxLayout()
    button_row_layout.addWidget(info_button)
    button_row_layout.addStretch(1)
    button_row_layout.addWidget(close_button, 0, alignment=QtCore.Qt.AlignCenter)
    button_row_layout.addStretch(1)
    button_row_layout.addWidget(doc_button, 0, alignment=QtCore.Qt.AlignRight)

    button_layout = QtGui.QVBoxLayout()
    button_layout.addLayout(layoutInfoShortcut)
    button_layout.addLayout(button_row_layout)

    global pieMenuDialog
    pieMenuDialog = PieMenuDialog()

    pieMenuDialogLayout = QtGui.QVBoxLayout()
    pieMenuDialog.setLayout(pieMenuDialogLayout)
    pieMenuDialogLayout.addWidget(preferencesWidget)
    pieMenuDialogLayout.addLayout(button_layout)

    close_button.clicked.connect(pieMenuDialog.close)

    #### Global Settings ####
    labelTheme = QLabel(translate("GlobalSettingsTab", "Theme style:"))
    labelTheme.setMinimumWidth(160)
    labelTheme.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)

    comboBoxTheme = QtGui.QComboBox()
    comboBoxTheme.setMinimumWidth(120)
    comboBoxTheme.currentIndexChanged.connect(setTheme)

    getTheme()

    layoutThemeLeft = QtGui.QHBoxLayout()
    layoutThemeLeft.addWidget(labelTheme)
    layoutThemeRight = QtGui.QHBoxLayout()
    layoutThemeRight.addWidget(comboBoxTheme)
    layoutTheme = QtGui.QHBoxLayout()
    layoutTheme.addLayout(layoutThemeLeft, 1)
    layoutTheme.addLayout(layoutThemeRight, 1)

    checkboxQuickMenu = QCheckBox()
    checkboxQuickMenu.setCheckable(True)
    checkboxQuickMenu.setChecked(paramGet.GetBool("ShowQuickMenu"))

    checkboxQuickMenu.stateChanged.connect(lambda state: onShowQuickMenu(state))

    labelShowQuickMenu = QLabel(translate("GlobalSettingsTab", "Show QuickMenu"))
    labelShowQuickMenu.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)

    layoutShowQuickMenuLeft = QtGui.QHBoxLayout()
    layoutShowQuickMenuLeft.addWidget(checkboxQuickMenu)
    layoutShowQuickMenuLeft.addWidget(labelShowQuickMenu)
    layoutShowQuickMenuLeft.addStretch(1)
    layoutShowQuickMenu = QtGui.QHBoxLayout()
    layoutShowQuickMenu.addLayout(layoutShowQuickMenuLeft, 1)

    checkboxGlobalContext = QCheckBox()
    checkboxGlobalContext.setCheckable(True)
    enableContext = paramGet.GetBool("EnableContext")
    checkboxGlobalContext.setChecked(enableContext)
    checkboxGlobalContext.stateChanged.connect(lambda state: onContext(state))

    labelGlobalContext = QLabel(translate("GlobalSettingsTab", "Global context"))
    labelGlobalContext.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)

    layoutGlobalContextLeft = QtGui.QHBoxLayout()
    layoutGlobalContextLeft.addWidget(checkboxGlobalContext)
    layoutGlobalContextLeft.addWidget(labelGlobalContext)
    layoutGlobalContextLeft.addStretch(1)
    layoutGlobalContext = QtGui.QHBoxLayout()
    layoutGlobalContext.addLayout(layoutGlobalContextLeft, 1)

    checkboxGlobalKeyToggle = QCheckBox()
    checkboxGlobalKeyToggle.setCheckable(True)

    checkboxGlobalKeyToggle.setChecked(getParameterGlobal("Bool", "GlobalKeyToggle"))
    checkboxGlobalKeyToggle.stateChanged.connect(setGlobalKeyToggle)

    labelGlobalKeyToggle = QLabel(translate("GlobalSettingsTab","Shortcuts behavior: Toggle show/hide PieMenu"))
    labelGlobalKeyToggle.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
    layoutGlobalToggle = QtGui.QHBoxLayout()
    layoutGlobalToggle.addWidget(checkboxGlobalKeyToggle)
    layoutGlobalToggle.addWidget(labelGlobalKeyToggle)
    layoutGlobalToggle.addStretch(1)

    checkboxRightClick = QCheckBox()
    checkboxRightClick.setCheckable(True)

    checkboxRightClick.setChecked(getParameterGlobal("Bool", "RightClickTrigger"))
    checkboxRightClick.stateChanged.connect(lambda state: onRightClickTrigger(state))

    labelDelayRightClick= QLabel(translate("GlobalSettingsTab","Delay (ms):"))

    spinDelayRightClick = QtGui.QSpinBox()
    spinDelayRightClick.setMaximum(1000)
    spinDelayRightClick.setMinimum(50)
    spinDelayRightClick.setValue(getParameterGlobal("Int", "DelayRightClick"))
    spinDelayRightClick.valueChanged.connect(onSpinDelayRightClick)

    labelRightClick = QLabel(translate("GlobalSettingsTab","Long right-click to open default PieMenu"))
    labelRightClick.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
    layoutRightClick = QtGui.QHBoxLayout()
    layoutRightClick.addWidget(checkboxRightClick)
    layoutRightClick.addWidget(labelRightClick)
    layoutRightClick.addStretch(1)
    layoutRightClick.addWidget(labelDelayRightClick)
    layoutRightClick.addWidget(spinDelayRightClick)

    globalSettingsGroup = QGroupBox(translate("GlobalSettingsTab", "Global settings"))
    globalSettingsGroup.setLayout(QtGui.QVBoxLayout())
    globalSettingsGroup.layout().addLayout(layoutTheme)
    globalSettingsGroup.layout().addLayout(layoutShowQuickMenu)
    globalSettingsGroup.layout().addLayout(layoutGlobalContext)
    globalSettingsGroup.layout().addLayout(layoutGlobalToggle)

    experimentalGroup = QGroupBox(translate("GlobalSettingsTab", "Experimental"))
    experimentalGroup.setLayout(QtGui.QVBoxLayout())
    experimentalGroup.layout().addLayout(layoutRightClick)

    labelGlobalShortcut = QLabel()
    labelGlobalShortcut.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
    labelGlobalShortcut.setText(translate("GlobalSettingsTab", "Global shortcut : ") + globalShortcutKey)

    globalShortcutKey = paramGet.GetString("GlobalShortcutKey")

    globalShortcutLineEdit = CustomLineEdit()
    globalShortcutLineEdit.setText(globalShortcutKey)
    globalShortcutLineEdit.setToolTip(translate("GlobalSettingsTab", "For TAB press CTRL+TAB"))

    assignGlobalShortcutButton = QtGui.QPushButton(translate("PieMenuTab", "Assign"))
    assignGlobalShortcutButton.clicked.connect(lambda: updateGlobalShortcutKey(globalShortcutLineEdit.text()))

    deleteGlobalShortcutButton = QtGui.QPushButton()
    deleteGlobalShortcutButton.setMaximumWidth(40)
    deleteGlobalShortcutButton.setIcon(QtGui.QIcon.fromTheme(iconBackspace))
    deleteGlobalShortcutButton.clicked.connect(lambda: updateGlobalShortcutKey(""))

    layoutGlobalShortcut = QtGui.QHBoxLayout()
    layoutGlobalShortcut.addWidget(labelGlobalShortcut)
    layoutGlobalShortcut.addStretch(1)
    layoutGlobalShortcut.addWidget(globalShortcutLineEdit)
    layoutGlobalShortcut.addWidget(assignGlobalShortcutButton)
    layoutGlobalShortcut.addWidget(deleteGlobalShortcutButton)

    settingsTabLayout.insertWidget(1, globalSettingsGroup)
    settingsTabLayout.insertWidget(2, experimentalGroup)
    settingsTabLayout.addStretch(1)
    settingsTabLayout.insertSpacing(3, 42)
    settingsTabLayout.insertLayout(4, layoutGlobalShortcut)

    # Create a fake command in FreeCAD to handle the PieMenu Separator
    FreeCADGui.addCommand('Std_PieMenuSeparator', PieMenuSeparator())
    updateNestedPieMenus()

    mw = Gui.getMainWindow()
    start = True
    for action in mw.findChildren(QtGui.QAction):
        if action.objectName() == "PieMenuShortCut":
            start = False
        else:
            pass

    if start:
        compositingManager = True
        if QtCore.qVersion() < "5":
            windowShadow = False
        else:
            windowShadow = True
        if platform.system() == "Linux":
            try:
                if QtGui.QX11Info.isCompositingManagerRunning():
                    windowShadow = True
                else:
                    compositingManager = False
            except AttributeError:
                windowShadow = True
        else:
            pass
        if platform.system() == "Windows":
            windowShadow = True
        else:
            pass

        contextAll = {}
        contextList()
        selObserver = SelObserver()
        addObserver()
        setDefaults()
        PieMenuInstance = PieMenu()
        actionKey = QtGui.QAction(mw)
        actionKey.setText("Invoke pie menu")
        actionKey.setObjectName("PieMenuShortCut")
        # fix shortcut not trigger on fresh install
        globalShortcutKey = paramGet.GetString("GlobalShortcutKey")
        actionKey.setShortcut(QtGui.QKeySequence(globalShortcutKey))
        actionKey.triggered.connect(PieMenuInstance.showAtMouse)
        mw.addAction(actionKey)
        getShortcutList()
        # let the addition of the accessoriesMenu wait until FC is ready for it
        t = QtCore.QTimer()
        t.timeout.connect(addAccessoriesMenu)
        t.start(500)

    else:
        pass

pieMenuStart()
