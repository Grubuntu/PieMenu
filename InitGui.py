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
PIE_MENU_VERSION = "1.5"

def pieMenuStart():
    """Main function that starts the Pie Menu."""
    import os
    import math
    import operator
    import platform
    import FreeCAD as App
    import FreeCADGui as Gui
    from PySide import QtCore
    from PySide import QtGui, QtWidgets
    import PieMenuLocator as locator
    from PySide2.QtGui import QKeyEvent, QFontMetrics
    from PySide.QtWidgets import QApplication, QLineEdit, QWidget, QAction, \
        QPushButton, QLabel, QVBoxLayout, QHBoxLayout, QDoubleSpinBox, QCheckBox, \
        QMessageBox, QShortcut, QListWidgetItem, QListWidget, QComboBox, QDialog
    from PySide2.QtGui import QKeySequence
    from PySide2.QtCore import Qt
    from TranslateUtils import translate
    from FreeCAD import Units
    
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

    selectionTriggered = False
    contextPhase = False
    global shortcutKey
    global globalShortcutKey
    global shortcutList
    global flagVisi
    global triggerMode
    global hoverDelay
    global listCommands
    global listShortcutCode

    shortcutKey = ""
    globalShortcutKey = "TAB"
    shortcutList =[]
    flagVisi = False
    triggerMode = "Press"
    hoverDelay  = 100
    listCommands = []
    listShortcutCode = []

    paramPath = "User parameter:BaseApp/PieMenu"
    paramIndexPath = "User parameter:BaseApp/PieMenu/Index"
    paramAccents = "User parameter:BaseApp/Preferences/Themes"
    paramGet = App.ParamGet(paramPath)
    paramIndexGet = App.ParamGet(paramIndexPath)
    paramAccentsGet = App.ParamGet(paramAccents)

    ## HACK: workaround to avoid ghosting : we find wbs already loaded,
    ## so as not to reload them again in the function 'updateCommands'
    global loadedWorkbenches
    paramLoadedWb = "User parameter:BaseApp/Preferences/General"
    paramWb = App.ParamGet(paramLoadedWb)
    loadedWorkbenches = paramWb.GetString("BackgroundAutoloadModules")
    loadedWorkbenches = loadedWorkbenches.split(",")

    #### Classes definition ####
    class SelObserver:
        def addSelection(self, doc, obj, sub, pnt):
            listTopo()

        def removeSelection(self, doc, obj, sub):
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

        def onHoverTimeout(self):
            """Handle hover timeout event."""
            global triggerMode
            mode = triggerMode
            if self.isMouseOver and self.defaultAction().isEnabled() and mode == "Hover":
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

        def enterEvent(self, event):
            global hoverDelay
           
            if not self.enterEventConnected:
                self.hoverTimer.start(hoverDelay)
                self.enterEventConnected = True
            self.hoverTimer.stop()
            self.hoverTimer.start(hoverDelay)
            self.isMouseOver = True

        def mouseReleaseEvent(self, event):
            if self.isMouseOver and self.defaultAction().isEnabled():
                PieMenuInstance.hide()
                mw.setFocus()
                self.defaultAction().trigger()
                module = None
                try:
                    docName = App.ActiveDocument.Name
                    g = Gui.ActiveDocument.getInEdit()
                    module = g.Module
                    if (module is not None and module != 'SketcherGui'):
                        PieMenuInstance.showAtMouse()
                except:
                    pass
            else:
                pass


    class PieMenuSeparator:
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

            if not PieMenu.event_filter_installed:
                app = QtGui.QGuiApplication.instance() or QtGui.QApplication([])
                app.installEventFilter(self)
                PieMenu.event_filter_installed = True

            self.radius = 100
            self.buttons = []
            self.buttonSize = 32
            self.menu = QtGui.QMenu(mw)
            self.menuSize = 0
            self.menu.setObjectName("styleContainer")
            self.menu.setStyleSheet(styleCurrentTheme)
            self.menu.setWindowFlags(self.menu.windowFlags() |
                QtCore.Qt.FramelessWindowHint | Qt.NoDropShadowWindowHint)
            self.menu.setAttribute(QtCore.Qt.WA_TranslucentBackground)
            if compositingManager:
                pass
            else:
                self.menu.setAttribute(QtCore.Qt.WA_PaintOnScreen)
            self.setFocus()

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

        def validButton(self, buttonSize=38):
            icon = iconSize(buttonSize)
            button = QtGui.QToolButton()
            button.setObjectName("styleComboValid")
            button.setProperty("ButtonX", -25)
            button.setProperty("ButtonY", 8)
            button.setGeometry(0, 0, buttonSize, buttonSize)
            button.setIconSize(QtCore.QSize(icon, icon))
            return button

        def cancelButton(self, buttonSize=38):
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
            button.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
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
            """ Handle tool shortcut in PieMenus """
            if event.type() == QtCore.QEvent.KeyRelease:
                if self.menu.isVisible():
                    global flagVisi
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
                        # if chr(event.key()) in listShortcutCode:
                        if charKey in listShortcutCode:
                            self.menu.hide()
                            event.accept()
                            j = 0
                            for i in listShortcutCode:
                                # if i == event.text():
                                if i == charKey:
                                    listCommands[j].trigger()
                                    module = None
                                    try:
                                        docName = App.ActiveDocument.Name
                                        g = Gui.ActiveDocument.getInEdit()
                                        module = g.Module
                                        # global flagVisi
                                        if (module is not None and module != 'SketcherGui'):
                                            PieMenuInstance.showAtMouse()
                                    except:
                                        pass
                                j+=1
                            return True

            """ Handle toggle mode for global shortcut """
            if event.type() == QtCore.QEvent.ShortcutOverride:
                if checkboxGlobalKeyToggle.isChecked():
                    if event.key() == QtGui.QKeySequence(globalShortcutKey):
                        if self.menu.isVisible():
                            self.menu.hide()
                            flagVisi = True
                            return True
                        else:
                            flagVisi = False
                            return False

                    ###### Handle individuals shortcuts toggle show/hide ####    
                    else:
                        for shortcut in mw.findChildren(QShortcut):
                            if event.key() == QtGui.QKeySequence(shortcut.key()):
                                if self.menu.isVisible():
                                    self.menu.hide()
                                    flagVisi = True
                                    return True
                                else:
                                    flagVisi = False
                                    return False

            """ Handle keys Return and Enter for spinbox """
            if event.type() == QtCore.QEvent.KeyPress:
                key = event.key()
                if key == QtCore.Qt.Key_Enter or key == QtCore.Qt.Key_Return:
                    try:
                        if self.double_spinbox.isVisible():
                            self.validation()
                    except:
                        None
                    ###### Confirm with 'Enter' or 'Return' key ######
                    try:
                        if self.menu.isVisible():
                            self.validation()
                    except:
                        None

                        flagVisi = True
                        return True

                ######### Delete with keys SUPPR and DEL in Toollist #######################
                """ Handle delete in Toollist """ 
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

            valueRadius = group.GetInt("Radius")
            self.radius = valueRadius
            valueButton = group.GetInt("Button")
            buttonSize = valueButton
            self.offset_x = 0
            self.offset_y = 0

            shape = getShape(keyValue)

            num_per_row = getParameterGroup(keyValue, "Int", "NumColumn")
            icon_spacing = getParameterGroup(keyValue, "Int", "IconSpacing")
            command_per_circle = getParameterGroup(keyValue, "Int", "CommandPerCircle")
            shortcutLabelSize = getParameterGroup(keyValue, "Int", "ShortcutLabelSize")
            number_of_circle = 1

            if paramGet.GetBool("ToolBar") and keyValue == None:
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

            if num_per_row == 0:
                num_per_row = 1

            if icon_spacing < 0:
                icon_spacing = 0

            if shape == "Pie":
                if commandNumber == 1:
                    angle = 0
                    buttonSize = self.buttonSize
                else:
                    angle = 2 * math.pi / commandNumber
                    buttonRadius = math.sin(angle / 2) * self.radius
                    buttonSize = math.trunc(2 * buttonRadius / math.sqrt(2))
                angleStart = 3 * math.pi / 2 - angle

            elif shape == "RainbowUp":
                if commandNumber == 1:
                    angle = 0
                    buttonSize = self.buttonSize
                else:
                    angle =  math.pi / (commandNumber-1)
                buttonRadius = math.sin(angle / 2) * self.radius
                buttonSize = math.trunc(2 * buttonRadius / math.sqrt(2))
                angleStart = 3 * math.pi / 2 - (angle*(commandNumber+1))/2

            elif shape == "RainbowDown":
                if commandNumber == 1:
                    angle = 0
                    buttonSize = self.buttonSize
                else:
                    angle =  math.pi / (commandNumber-1)
                buttonRadius = math.sin(angle / 2) * self.radius
                buttonSize = math.trunc(2 * buttonRadius / math.sqrt(2))
                angleStart =  math.pi / 2 - (angle*(commandNumber+1))/2

            elif shape == "Concentric" or shape == "Star" :
                angle = 2 * math.pi / (command_per_circle)
                buttonRadius = math.sin(angle / 2) * self.radius
                buttonSize = math.trunc(2 * buttonRadius / math.sqrt(2))
                angleStart = 3 * math.pi / 2 - angle

            else:
                angle = 2 * math.pi / commandNumber
                angleStart = 3 * math.pi / 2 - angle

            if buttonSize > self.buttonSize:
                buttonSize = self.buttonSize
            else:
                pass
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
            displayShortcut = False
            if shape in ["Pie", "LeftRight"]:
                try: # get displayCommandName to display or not command name only for Pie shape
                    displayCommandName = getParameterGroup(keyValue, "Bool", "DisplayCommand")
                except:
                    None

            # Test not needed in this version, as all shapes accept the shortcuts Tools
            # if shape in ["Pie", "RainbowUp", "RainbowDown", "Concentric", "Star", "LeftRight", "UpDown", "TableTop", "TableDown", "TableLeft", "TableRight"]:
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
                            angleStart = angleStart + angle

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

                    self.buttons.append(button)

                    #### Manage Separator ###
                    if (commands[commands.index(i)].text()) == translate('PieMenuTab', 'Separator'):
                        button.setObjectName("styleSeparator")
                        button.setIcon(QtGui.QIcon(iconSeparator))
                        iconButton =  QtGui.QIcon(iconSeparator)
                        try:
                            iconLabel.setPixmap(iconButton.pixmap(QtCore.QSize(icon, icon)))
                        except:
                            None
                    else:
                        if displayShortcut:
                            # Add button label for Shortcuts Tools on PieMenu
                            shortcutLabel = HoverButton()
                            shortcutLabel.setParent(self.menu)
                            shortcutLabel.setObjectName("pieMenuShortcutTool")

                            fontSize = "QToolButton#pieMenuShortcut {font-size: " + str(shortcutLabelSize) + "px;}"

                            shortcutLabel.setStyleSheet(styleCurrentTheme + fontSize)
                            shortcutLabel.setDefaultAction(commands[commands.index(i)])
                            shortcutLabel.setToolButtonStyle(Qt.ToolButtonTextOnly)
                            shortcutLabel.setText(chr(shortcutCode))

                            listCommands.append(commands[commands.index(i)])
                            listShortcutCode.append(chr(shortcutCode))
                            # print(shortcutCode)
                            if shortcutCode == 57:
                                shortcutCode = 64
                            shortcutCode += 1

                            shortcutLabel.setProperty("ButtonX", X_shortcut )
                            shortcutLabel.setProperty("ButtonY", Y_shortcut )

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
                            unit = " °" # degres
                            quantity = Units.Quantity(Units.Quantity(g.Object.Angle).getUserPreferred()[0])

                            self.checkbox_midPlane = checkbox_layout(self.checkboxSymToPlane, "Midplane", True)
                            layoutMidPlane.addWidget(self.checkbox_midPlane)
                            layoutOptions.addLayout(layoutMidPlane)

                            self.checkbox_reversed = checkbox_layout(self.checkboxReversed, "Reversed", True)
                            layoutReversed.addWidget(self.checkbox_reversed)
                            layoutOptions.addLayout(layoutReversed)

                        elif (str(fonctionActive) == '<PartDesign::Hole>'):
                            self.buttons.remove(double_spinbox)
                        else:
                            self.buttons.remove(double_spinbox)

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
            global lastPosX
            global lastPosY

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
                if notKeyTriggered:
                    if contextPhase:
                        # special case treatment
                        if selectionTriggered:
                            selectionTriggered = False
                        else:
                            pos.setX(lastPosX)
                            pos.setY(lastPosY)
                        lastPosX = pos.x()
                        lastPosY = pos.y()
                    else:
                        pos.setX(lastPosX)
                        pos.setY(lastPosY)
                else:
                    lastPosX = pos.x()
                    lastPosY = pos.y()

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
                if notKeyTriggered:
                    if contextPhase:
                        # special case treatment
                        if selectionTriggered:
                            selectionTriggered = False
                        else:
                            pos.setX(lastPosX)
                            pos.setY(lastPosY)
                        lastPosX = pos.x()
                        lastPosY = pos.y()
                    else:
                        pos.setX(lastPosX)
                        pos.setY(lastPosY)
                else:
                    lastPosX = pos.x()
                    lastPosY = pos.y()

                for i in self.buttons:
                    i.move(i.property("ButtonX")
                          + (self.menuSize - i.size().width()) / 2 + self.offset_x,
                          i.property("ButtonY")
                          + (self.menuSize - i.size().height()) / 2 + self.offset_y)

                    i.setVisible(True)

                self.menu.popup(QtCore.QPoint(pos.x() - self.menuSize / 2, pos.y() - self.menuSize / 2))

        def showAtMouse(self, keyValue=None, notKeyTriggered=False):
            global flagVisi
            
            if not flagVisi:
                self.showAtMouseInstance(keyValue, notKeyTriggered)
                flagVisi = False
            else:
                self.menu.hide()
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
            # Connect close event 

            self.resize(800, 450)
            self.setObjectName("PieMenuPreferences")
            self.setWindowTitle("PieMenu " + PIE_MENU_VERSION)
            self.closeEvent = self.customCloseEvent
            self.setWindowIcon(QtGui.QIcon(iconPieMenuLogo))

        def customCloseEvent(self, event):
            # Caught close event to save parameters on disk
            App.saveParameter()
            super(PieMenuDialog, self).closeEvent(event)

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
        ThemeAccentColor1 = paramAccentsGet.GetUnsigned("ThemeAccentColor1")
        ThemeAccentColor2 = paramAccentsGet.GetUnsigned("ThemeAccentColor2")
        ThemeAccentColor3 = paramAccentsGet.GetUnsigned("ThemeAccentColor3")
        ThemeAccentColor1_hex_full = format(ThemeAccentColor1, '06x')
        ThemeAccentColor2_hex_full = format(ThemeAccentColor2, '06x')
        ThemeAccentColor3_hex_full = format(ThemeAccentColor3, '06x')
        ThemeAccentColor1_hex = ThemeAccentColor1_hex_full[:-2]
        ThemeAccentColor2_hex = ThemeAccentColor2_hex_full[:-2]
        ThemeAccentColor3_hex = ThemeAccentColor3_hex_full[:-2]
        styleCurrentTheme = styleCurrentTheme.replace("@ThemeAccentColor1", "#" + str(ThemeAccentColor1_hex))
        styleCurrentTheme = styleCurrentTheme.replace("@ThemeAccentColor2", "#" + str(ThemeAccentColor2_hex))
        styleCurrentTheme = styleCurrentTheme.replace("@ThemeAccentColor3", "#" + str(ThemeAccentColor3_hex))
        return styleCurrentTheme


    ###################################
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

    ################################

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


    def remObsoleteParams():
        """Remove obsolete parameters from older versions."""
        paramGet.RemBool("ContextPhase")


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
        globalContextPie = False
        globalIndexPie = None
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
                    globalContextPie = "True"
                    globalIndexPie = current["Index"]
                else:
                    pass
            vertex()
        if globalContextPie == "True":
            return globalIndexPie
        else:
            return None


    def listTopo():
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
            if i.startswith('Vertex'):
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
            # selectionTriggered = True
            #PieMenuInstance.showAtMouse(notKeyTriggered=True)
        else:
            pass


    def addObserver():
        if paramGet.GetBool("EnableContext"):
            Gui.Selection.addObserver(selObserver)
        else:
            Gui.Selection.removeObserver(selObserver)


    def getGuiActionMapAll():
        actions = {}
        duplicates = []
        for i in mw.findChildren(QtGui.QAction):
            if i.objectName() is not None:
                if i.objectName() != "" and i.icon():
                    if i.objectName() in actions:
                        if i.objectName() not in duplicates:
                            duplicates.append(i.objectName())
                        else:
                            pass
                    else:
                        actions[i.objectName()] = i
                else:
                    pass
            else:
                pass
        for d in duplicates:
            del actions[d]
        return actions


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
                    if cmd_parts[0][:2] == "SM":
                        cmd_parts[0] = cmd_parts[0][:2]
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
                            if i[:2] == "SM":
                                i = i[:2]
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


    def getTheme():
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
        buttonListWidget.blockSignals(True)
        buttonListWidget.clear()
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
                            if cmd_parts[0][:2] == "SM":
                                cmd_parts[0] = cmd_parts[0][:2]
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
        for i in toolList:
            if i in actionMapAll:
                item = QtGui.QListWidgetItem(buttonListWidget)
                item.setData(QtCore.Qt.UserRole, i)
                item.setText(actionMapAll[i].text().replace("&", ""))
                item.setIcon(actionMapAll[i].icon())
            else:
                pass
        buttonListWidget.blockSignals(False)


    def cBoxUpdate():
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
        pieList = duplicates
        pieList.reverse()
        cBox.blockSignals(True)
        cBox.clear()
        for i in pieList:
            cBox.insertItem(0, i)
        cBox.blockSignals(False)
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
        touches_speciales = {'CTRL', 'ALT', 'SHIFT', 'META', 'TAB'}

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

        getShortcutList()


    def updateGlobalShortcutKey(newShortcut):
        global globalShortcutKey
        touches_speciales = {'CTRL', 'ALT', 'SHIFT', 'META', 'TAB'}

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
        setCheckContext()
        shortcutKey = getParameterGroup(cBox.currentText(), "String", "ShortcutKey")
        getShortcutList()
        shortcutLineEdit.setText(shortcutKey)

        globalShortcutLineEdit.setText(globalShortcutKey)
        labelShortcut.setText(translate("PieMenuTab", "Current shortcut: ") + shortcutKey)
        labelGlobalShortcut.setText(translate("GlobalSettingsTab", "Global shortcut: ") \
            + globalShortcutKey)

        displayCommandName = getParameterGroup(cBox.currentText(), "Bool", "DisplayCommand")
        cboxDisplayCommandName.blockSignals(True)
        cboxDisplayCommandName.setChecked(displayCommandName)
        cboxDisplayCommandName.blockSignals(False)

        displayShortcut = getParameterGroup(cBox.currentText(), "Bool", "DisplayShorcut")
        cboxDisplayShortcut.blockSignals(True)
        cboxDisplayShortcut.setChecked(displayShortcut)
        cboxDisplayShortcut.blockSignals(False)

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
            cBoxUpdate()
            # select the new piemenu in the cBox
            index = cBox.findText(text)
            if index != -1:
                cBox.setCurrentIndex(index)

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
                # special case treatment
                if pie == currentPie:
                    currentPie = "View"
                    try:
                        paramGet.SetString("CurrentPie", currentPie.encode('UTF-8'))
                    except TypeError:
                        paramGet.SetString("CurrentPie", currentPie)
                if pie == contextPie:
                    paramGet.RemString("ContextPie")
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
        cBoxUpdate()


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

        cBoxUpdate()


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


    def onWbForPieMenu():
        group = getGroup()
        defWorkbench = comboWbForPieMenu.currentText()
        group.SetString("DefaultWorkbench", defWorkbench)


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


    def onSpinShortcutLabelSize():
        group = getGroup()
        value = spinShortcutLabelSize.value()
        group.SetInt("ShortcutLabelSize", value)


    def setShape():
        group = getGroup(mode=0)
        comboShape.blockSignals(True)
        shape = comboShape.currentText()
        group.SetString("Shape", shape)
        comboShape.blockSignals(False)
        onShape(shape)


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
                    cboxDisplayCommandName.setVisible(True)
                    cboxDisplayCommandName.setEnabled(True)
                else:
                    labeldisplayCommandName.setVisible(False)
                    cboxDisplayCommandName.setVisible(False)
                    cboxDisplayCommandName.setEnabled(False)

                if shape in ["Concentric", "Star"]:
                    labelCommandPerCircle.setVisible(True)
                    spinCommandPerCircle.setEnabled(True)
                    spinCommandPerCircle.setVisible(True)
                else:
                    labelCommandPerCircle.setVisible(False)
                    spinCommandPerCircle.setEnabled(False)
                    spinCommandPerCircle.setVisible(False)

            ### Available for all shapes
            labeldisplayShortcut.setVisible(True)
            cboxDisplayShortcut.setVisible(True)
            cboxDisplayShortcut.setEnabled(True)

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
        available_shape = [ "Pie", "RainbowUp", "RainbowDown", "Concentric", "Star", "UpDown", "LeftRight", \
                           "TableTop", "TableDown", "TableLeft", "TableRight" ]
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


    def onDisplayShortcut(state):
        """ Set parameter for show or not 'Shortcut Tool' """
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


    def onNumColumn():
        group = getGroup()
        value = spinNumColumn.value()
        group.SetInt("NumColumn", value)


    def onIconSpacing():
        group = getGroup()
        value = spinIconSpacing.value()
        group.SetInt("IconSpacing", value)


    def onCommandPerCircle():
        group = getGroup()
        value = spinCommandPerCircle.value()
        group.SetInt("CommandPerCircle", value)


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


    def onSpinButton():
        group = getGroup()
        value = spinButton.value()
        group.SetInt("Button", value)


    def onShowQuickMenu(state):
        if state == Qt.Checked:
            paramGet.SetBool("ShowQuickMenu", True)
        else:
            paramGet.SetBool("ShowQuickMenu", False)


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
        items = []
        for index in range(buttonListWidget.count()):
            items.append(buttonListWidget.item(index))
        toolData = []
        for i in items:
            toolData.append(i.data(QtCore.Qt.UserRole))
        group = getGroup()
        group.SetString("ToolList", ".,.".join(toolData))


    def onButtonUp():
        currentIndex = buttonListWidget.currentRow()
        if currentIndex != 0:
            currentItem = buttonListWidget.takeItem(currentIndex)
            buttonListWidget.insertItem(currentIndex - 1, currentItem)
            buttonListWidget.setCurrentRow(currentIndex - 1)
            buttonList2ToolList(buttonListWidget)


    def onButtonAddSeparator():
        """ Handle separator for PieMenus """
        # we must create a custom toolbar "PieMenuTB" to 'activate' the command 'Std_PieMenuSeparator' otherwise the separators are not correctly handled
        globaltoolbar = FreeCAD.ParamGet('User parameter:BaseApp/Workbench/Global/Toolbar/Custom_PieMenu')
        piemenuSeparator = globaltoolbar.GetString('Name')
        if piemenuSeparator == "PieMenuTB":
            pass
        else:
            globaltoolbar.SetString('Name','PieMenuTB')
            globaltoolbar.SetString('Std_PieMenuSeparator','FreeCAD')
            globaltoolbar.SetString('Value','1')
            App.saveParameter()
            wb = Gui.activeWorkbench()
            wb.reloadActive()

            # we hide the custom toolbar
            mw = FreeCADGui.getMainWindow()
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


    def onButtonDown():
        currentIndex = buttonListWidget.currentRow()
        if currentIndex != buttonListWidget.count() - 1 and currentIndex != -1:
            currentItem = buttonListWidget.takeItem(currentIndex)
            buttonListWidget.insertItem(currentIndex + 1, currentItem)
            buttonListWidget.setCurrentRow(currentIndex + 1)
            buttonList2ToolList(buttonListWidget)


    def onButtonRemoveCommand():
        currentIndex = buttonListWidget.currentRow()
        buttonListWidget.takeItem(currentIndex)
        if currentIndex != 0:
            buttonListWidget.setCurrentRow(currentIndex - 1)
        buttonListWidget.setFocus()
        buttonList2ToolList(buttonListWidget)
        toolList()


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


    def setCheckContext():
        group = getGroup()
        groupContext = group.GetGroup("Context")
        if groupContext.GetBool("Enabled"):
            checkContext.setChecked(True)
            contextTable.setEnabled(True)
            resetContextButton.setEnabled(True)
        else:
            checkContext.setChecked(False)
            contextTable.setEnabled(False)
            resetContextButton.setEnabled(False)
        contextList()


    def onCheckContext():
        setDefaults()
        group = getGroup()
        groupContext = group.GetGroup("Context")
        if checkContext.isChecked():
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
        setCheckContext()


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

        contextList()


    def setDefaultPie(restore=False):
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
            group.SetBool("DisplayShorcut", False)

            paramIndexGet.SetString("1", "PartDesign")
            group = paramIndexGet.GetGroup("1")
            group.SetString("ToolList", ".,.".join(defaultToolsPartDesign))
            group.SetInt("Radius", 80)
            group.SetInt("Button", 32)
            group.SetString("Shape", "Pie")
            group.SetString("TriggerMode", "Press")
            group.SetInt("HoverDelay", 100)
            group.SetBool("DisplayShorcut", False)

            paramIndexGet.SetString("2", "Sketcher")
            group = paramIndexGet.GetGroup("2")
            group.SetString("ToolList", ".,.".join(defaultToolsSketcher))
            group.SetInt("Radius", 80)
            group.SetInt("Button", 32)
            group.SetString("Shape", "Pie")
            group.SetString("TriggerMode", "Press")
            group.SetInt("HoverDelay", 100)
            group.SetString("DefaultWorkbench", "Sketcher")
            group.SetBool("DisplayShorcut", False)

        paramGet.SetBool("ToolBar", False)
        paramGet.RemString("ToolBar")
        paramGet.SetString("CurrentPie", "View")
        paramGet.SetString("Theme", "Legacy")
        paramGet.SetString("GlobalShortcutKey", "TAB")
        paramGet.SetBool("ShowQuickMenu", True)
        paramGet.SetBool("EnableContext", False)
        paramGet.SetBool("GlobalKeyToggle", True)
        App.saveParameter() 


    ### Begin QuickMenu  Def ###
    def quickMenu(buttonSize=20):
        """Build and style the QuickMenu button."""


        def setChecked():
            if paramGet.GetBool("EnableContext"):
                actionContext.setChecked(True)
            else:
                pass


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

        icon = iconSize(buttonSize)
        radius = radiusSize(buttonSize)

        menu = QtGui.QMenu(mw)
        menu.setObjectName("styleQuickMenu")
        menu.setStyleSheet(styleCurrentTheme)

        button = QtGui.QToolButton()
        button.setObjectName("styleButtonMenu")
        button.setMenu(menu)
        button.setProperty("ButtonX", 0) # +, right
        button.setProperty("ButtonY", 32) # +, down
        button.setGeometry(0, 0, buttonSize, buttonSize)
        button.setIconSize(QtCore.QSize(icon, icon))

        button.setStyleSheet(styleCurrentTheme + radius)
        button.setPopupMode(QtGui.QToolButton
                            .ToolButtonPopupMode.InstantPopup)

        actionContext = QtGui.QAction(menu)
        actionContext.setText(translate("QuickMenu", "Context"))
        actionContext.setCheckable(True)

        menuPieMenu = QtGui.QMenu()
        menuPieMenu.setTitle(translate("QuickMenu", "PieMenu"))

        pieGroup = QtGui.QActionGroup(menu)
        pieGroup.setExclusive(True)

        menuToolBar = QtGui.QMenu()
        menuToolBar.setObjectName("styleQuickMenuItem")
        menuToolBar.setTitle(translate("QuickMenu", "ToolBar"))
        menuToolBar.setStyleSheet(styleCurrentTheme)

        toolbarGroup = QtGui.QMenu()

        toolbarGroupOps = QtGui.QActionGroup(toolbarGroup)
        toolbarGroupOps.setExclusive(True)

        prefAction = QtGui.QAction(menu)
        prefAction.setIconText(translate("QuickMenu", "Preferences"))

        prefButton = QtGui.QToolButton()
        prefButton.setDefaultAction(prefAction)

        prefButtonWidgetAction = QtGui.QWidgetAction(menu)
        prefButtonWidgetAction.setDefaultWidget(prefButton)

        setChecked()
        actionContext.triggered.connect(onActionContext)
        menuPieMenu.aboutToShow.connect(pieList)
        pieGroup.triggered.connect(onPieGroup)
        menuToolBar.aboutToShow.connect(onMenuToolBar)
        toolbarGroup.triggered.connect(onToolbarGroup)
        prefButton.clicked.connect(onPrefButton)
        menu.addAction(actionContext)
        menu.addSeparator()
        menu.addMenu(menuPieMenu)
        menu.addMenu(menuToolBar)
        menu.addSeparator()
        menu.addAction(prefButtonWidgetAction)

        return button

    ### END QuickMenu   Def ###


    def onControl():
        """Initializes the preferences dialog."""
        shape = getShape(cBox.currentText())
        onShape(shape)

        global pieMenuDialog
        global shortcutKey
        global globalShortcutKey

        for i in mw.findChildren(QtGui.QDialog):
            if i.objectName() == "PieMenuPreferences":
                i.deleteLater()
            else:
                pass

        shortcutKey = getParameterGroup(cBox.currentText(), "String", "ShortcutKey")
        globalShortcutKey = paramGet.GetString("GlobalShortcutKey")

        #### Preferences  dialog ####
        tabs = QtGui.QTabWidget()

        pieMenuTab = QtGui.QWidget()
        pieMenuTabLayout = QtGui.QVBoxLayout()
        pieMenuTab.setLayout(pieMenuTabLayout)

        layoutAddRemove = QtGui.QHBoxLayout()
        layoutAddRemove.addWidget(cBox)
        layoutAddRemove.addWidget(buttonAddPieMenu)
        layoutAddRemove.addWidget(buttonRemovePieMenu)
        layoutAddRemove.addWidget(buttonRenamePieMenu)
        layoutAddRemove.addWidget(buttonCopyPieMenu)

        layoutWbForPieMenuLeft = QtGui.QHBoxLayout()
        layoutWbForPieMenuLeft.addWidget(labelWbForPieMenu)
        layoutWbForPieMenuRight = QtGui.QHBoxLayout()
        layoutWbForPieMenuRight.addWidget(comboWbForPieMenu)
        layoutWbForPieMenu = QtGui.QHBoxLayout()
        layoutWbForPieMenu.addLayout(layoutWbForPieMenuLeft, 1)
        layoutWbForPieMenu.addLayout(layoutWbForPieMenuRight, 1)

        layoutRadiusLeft = QtGui.QHBoxLayout()
        layoutRadiusLeft.addWidget(labelRadius)
        layoutRadiusRight = QtGui.QHBoxLayout()
        layoutRadiusRight.addWidget(spinRadius)
        layoutRadius = QtGui.QHBoxLayout()
        layoutRadius.addLayout(layoutRadiusLeft, 1)
        layoutRadius.addLayout(layoutRadiusRight, 1)

        layoutButtonLeft = QtGui.QHBoxLayout()
        layoutButtonLeft.addWidget(labelButton)
        layoutButtonRight = QtGui.QHBoxLayout()
        layoutButtonRight.addWidget(spinButton)
        layoutButton = QtGui.QHBoxLayout()
        layoutButton.addLayout(layoutButtonLeft, 1)
        layoutButton.addLayout(layoutButtonRight, 1)

        labelShortcut.setText(translate("PieMenuTab", "Current shortcut: ") + shortcutKey)

        layoutShortcut = QtGui.QHBoxLayout()
        layoutShortcut.addWidget(labelShortcut)
        layoutShortcut.addStretch(1)
        layoutShortcut.addWidget(shortcutLineEdit)
        layoutShortcut.addWidget(assignShortcutButton)

        layoutShapeLeft = QtGui.QHBoxLayout()
        layoutShapeLeft.addWidget(labelShape)
        layoutShapeRight = QtGui.QHBoxLayout()
        layoutShapeRight.addWidget(comboShape)
        layoutShape = QtGui.QHBoxLayout()
        layoutShape.addLayout(layoutShapeLeft, 1)
        layoutShape.addLayout(layoutShapeRight, 1)

        layoutColumnLeft = QtGui.QHBoxLayout()
        layoutColumnLeft.addWidget(labelNumColumn)
        layoutColumnRight = QtGui.QHBoxLayout()
        layoutColumnRight.addWidget(spinNumColumn)
        layoutColumnRight.addStretch(1)
        layoutColumn = QtGui.QHBoxLayout()
        layoutColumn.addLayout(layoutColumnLeft, 1)
        layoutColumn.addLayout(layoutColumnRight, 1)

        layoutIconSpacingLeft = QtGui.QHBoxLayout()
        layoutIconSpacingLeft.addWidget(labelIconSpacing)
        layoutIconSpacingRight = QtGui.QHBoxLayout()
        layoutIconSpacingRight.addWidget(spinIconSpacing)
        layoutIconSpacingRight.addStretch(1)
        layoutIconSpacing = QtGui.QHBoxLayout()
        layoutIconSpacing.addLayout(layoutIconSpacingLeft, 1)
        layoutIconSpacing.addLayout(layoutIconSpacingRight, 1)

        layoutCommandPerCircleLeft = QtGui.QHBoxLayout()
        layoutCommandPerCircleLeft.addStretch(1)
        layoutCommandPerCircleLeft.addWidget(labelCommandPerCircle)
        layoutCommandPerCircleRight = QtGui.QHBoxLayout()
        layoutCommandPerCircleRight.addWidget(spinCommandPerCircle)
        layoutCommandPerCircleRight.addStretch(1)
        layoutCommandPerCircle = QtGui.QHBoxLayout()
        layoutCommandPerCircle.addLayout(layoutCommandPerCircleLeft, 1)
        layoutCommandPerCircle.addLayout(layoutCommandPerCircleRight, 1)

        layoutDisplayCommandNameLeft = QtGui.QHBoxLayout()
        layoutDisplayCommandNameLeft.addStretch(1)
        layoutDisplayCommandNameLeft.addWidget(labeldisplayCommandName)
        layoutDisplayCommandNameRight = QtGui.QHBoxLayout()
        layoutDisplayCommandNameRight.addWidget(cboxDisplayCommandName)
        layoutDisplayCommandNameRight.addStretch(1)
        layoutDisplayCommandName = QtGui.QHBoxLayout()
        layoutDisplayCommandName.addLayout(layoutDisplayCommandNameLeft, 1)
        layoutDisplayCommandName.addLayout(layoutDisplayCommandNameRight, 1)

        layoutDisplayShortcutLeft = QtGui.QHBoxLayout()
        layoutDisplayShortcutLeft.addStretch(1)
        layoutDisplayShortcutLeft.addWidget(labeldisplayShortcut)
        layoutDisplayShortcutLeft.addWidget(cboxDisplayShortcut)
        layoutDisplayShortcutRight = QtGui.QHBoxLayout()
        layoutDisplayShortcutRight.addWidget(labelShortcutSize)
        layoutDisplayShortcutRight.addWidget(spinShortcutLabelSize)
        layoutDisplayShortcutRight.addStretch(1)

        layoutDisplayShortcut = QtGui.QHBoxLayout()
        layoutDisplayShortcut.addLayout(layoutDisplayShortcutLeft, 1)
        layoutDisplayShortcut.addLayout(layoutDisplayShortcutRight, 1)

        layoutInfoShortcut = QtGui.QHBoxLayout()
        layoutInfoShortcut.addWidget(infoShortcut)
        layoutInfoShortcut.addStretch(1)
        infoShortcut.setText('')

        labelShowQuickMenu = QLabel(translate("GlobalSettingsTab", "Show QuickMenu:"))
        labelShowQuickMenu.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)

        layoutShowQuickMenuLeft = QtGui.QHBoxLayout()
        layoutShowQuickMenuLeft.addStretch(1)
        layoutShowQuickMenuLeft.addWidget(labelShowQuickMenu)
        layoutShowQuickMenuRight = QtGui.QHBoxLayout()
        layoutShowQuickMenuRight.addWidget(checkboxQuickMenu)
        layoutShowQuickMenuRight.addStretch(1)
        layoutShowQuickMenu = QtGui.QHBoxLayout()
        layoutShowQuickMenu.addLayout(layoutShowQuickMenuLeft, 1)
        layoutShowQuickMenu.addLayout(layoutShowQuickMenuRight, 1)

        checkboxQuickMenu.stateChanged.connect(lambda state: onShowQuickMenu(state))

        labelTheme = QLabel(translate("GlobalSettingsTab", "Theme style:"))
        labelTheme.setMinimumWidth(160)
        labelTheme.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)

        layoutThemeLeft = QtGui.QHBoxLayout()
        layoutThemeLeft.addStretch(1)
        layoutThemeLeft.addWidget(labelTheme)
        layoutThemeRight = QtGui.QHBoxLayout()
        layoutThemeRight.addWidget(comboBoxTheme)
        layoutTheme = QtGui.QHBoxLayout()
        layoutTheme.addLayout(layoutThemeLeft, 1)
        layoutTheme.addLayout(layoutThemeRight, 1)
        comboBoxTheme.currentIndexChanged.connect(setTheme)

        labelTriggerButton = QLabel(translate("GlobalSettingsTab", "Trigger mode:"))
        labelTriggerButton.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)

        radioGroup = QtGui.QButtonGroup()
        radioGroup.addButton(radioButtonPress)
        radioGroup.addButton(radioButtonHover)

        layoutActionHoverButton = QtGui.QVBoxLayout()
        layoutActionHoverButton.addWidget(radioButtonPress)
        layoutActionHoverButton.addWidget(radioButtonHover)

        layoutTriggerButtonLeft = QtGui.QHBoxLayout()
        layoutTriggerButtonLeft.addStretch(1)
        layoutTriggerButtonLeft.addWidget(labelTriggerButton)
        layoutTriggerButtonRight = QtGui.QHBoxLayout()
        layoutTriggerButtonRight.addLayout(layoutActionHoverButton)
        layoutTriggerButtonRight.addStretch(1)
        layoutTriggerButton = QtGui.QHBoxLayout()
        layoutTriggerButton.addLayout(layoutTriggerButtonLeft, 1)
        layoutTriggerButton.addLayout(layoutTriggerButtonRight, 1)

        layoutHoverDelayLeft = QtGui.QHBoxLayout()
        layoutHoverDelayLeft.addStretch(1)
        layoutHoverDelayLeft.addWidget(labelHoverDelay)
        layoutHoverDelayRight = QtGui.QHBoxLayout()
        layoutHoverDelayRight.addWidget(spinHoverDelay)
        layoutHoverDelayRight.addStretch(1)
        layoutHoverDelay = QtGui.QHBoxLayout()
        layoutHoverDelay.addLayout(layoutHoverDelayLeft, 1)
        layoutHoverDelay.addLayout(layoutHoverDelayRight, 1)

        labelGlobalShortcut.setText(translate("GlobalSettingsTab",\
            "Global shortcut : ") + globalShortcutKey)
        layoutGlobalShortcut = QtGui.QHBoxLayout()
        layoutGlobalShortcut.addWidget(labelGlobalShortcut)
        layoutGlobalShortcut.addStretch(1)
        layoutGlobalShortcut.addWidget(globalShortcutLineEdit)
        
        layoutGlobalToggle = QtGui.QHBoxLayout()
        layoutGlobalToggle.addWidget(labelGlobalKeyToggle)
        layoutGlobalToggle.addWidget(checkboxGlobalKeyToggle)

        layoutGlobalShortcut.addWidget(assignGlobalShortcutButton)

        pieMenuTabLayout.insertLayout(0, layoutAddRemove)
        pieMenuTabLayout.insertSpacing(1, 12)
        pieMenuTabLayout.insertLayout(2, layoutWbForPieMenu)
        pieMenuTabLayout.insertLayout(3, layoutRadius)
        pieMenuTabLayout.insertLayout(4, layoutButton)
        pieMenuTabLayout.insertLayout(5, layoutShape)
        pieMenuTabLayout.insertLayout(6, layoutTriggerButton)
        pieMenuTabLayout.insertLayout(7, layoutHoverDelay)
        pieMenuTabLayout.insertLayout(8, layoutColumn)
        pieMenuTabLayout.insertLayout(9, layoutIconSpacing)
        pieMenuTabLayout.insertLayout(10, layoutCommandPerCircle)
        pieMenuTabLayout.insertLayout(11, layoutDisplayCommandName)
        pieMenuTabLayout.insertLayout(12, layoutDisplayShortcut)
        # pieMenuTabLayout.insertLayout(13, layoutShortcutSize)
        pieMenuTabLayout.insertSpacing(14, 42)
        pieMenuTabLayout.insertWidget(15, separatorPieMenu)
        pieMenuTabLayout.insertLayout(16, layoutShortcut)

        pieMenuTabLayout.addStretch(0)

        contextTab = QtGui.QWidget()
        contextTabLayout = QtGui.QVBoxLayout()
        contextTab.setLayout(contextTabLayout)

        settingsTab = QtGui.QWidget()
        settingsTabLayout = QtGui.QVBoxLayout()
        settingsTab.setLayout(settingsTabLayout)

        labelGlobalContext = QLabel(translate("GlobalSettingsTab", "Global context:"))
        labelGlobalContext.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)

        layoutGlobalContextLeft = QtGui.QHBoxLayout()
        layoutGlobalContextLeft.addStretch(1)
        layoutGlobalContextLeft.addWidget(labelGlobalContext)
        layoutGlobalContextRight = QtGui.QHBoxLayout()
        layoutGlobalContextRight.addWidget(checkboxGlobalContext)
        layoutGlobalContextRight.addStretch(1)
        layoutGlobalContext = QtGui.QHBoxLayout()
        layoutGlobalContext.addLayout(layoutGlobalContextLeft, 1)
        layoutGlobalContext.addLayout(layoutGlobalContextRight, 1)

        layoutCheckContextLeft = QtGui.QHBoxLayout()
        layoutCheckContextLeft.addStretch(1)
        layoutCheckContextLeft.addWidget(labelContext)
        layoutCheckContextRight = QtGui.QHBoxLayout()
        layoutCheckContextRight.addWidget(checkContext)
        layoutCheckContextRight.addStretch(1)
        layoutCheckContext = QtGui.QHBoxLayout()
        layoutCheckContext.addLayout(layoutCheckContextLeft, 1)
        layoutCheckContext.addLayout(layoutCheckContextRight, 1)

        settingsTabLayout.insertLayout(1, layoutTheme)
        settingsTabLayout.insertLayout(2, layoutShowQuickMenu)
        settingsTabLayout.insertLayout(3, layoutGlobalContext)
        settingsTabLayout.insertLayout(4, layoutGlobalToggle)
        settingsTabLayout.insertSpacing(5, 42)
        settingsTabLayout.insertWidget(6, separatorSettings)
        settingsTabLayout.insertLayout(7, layoutGlobalShortcut)

        resetLayout = QtGui.QHBoxLayout()
        resetLayout.addStretch(1)
        resetLayout.addWidget(resetContextButton)

        contextTabLayout.insertLayout(0, layoutCheckContext)
        contextTabLayout.addWidget(contextTable)
        contextTabLayout.insertLayout(2, resetLayout)
        contextTabLayout.addStretch(1)

        tabs.addTab(pieMenuTab, translate("PieMenuTab", "PieMenu"))
        tabs.addTab(widgetContainer, translate("ToolsTab", "Tools"))
        tabs.addTab(contextTab, translate("ContextTab", "Context"))
        tabs.addTab(settingsTab, translate("GlobalSettingsTab", "Global settings"))

        pieButtons = QtGui.QWidget()
        pieButtonsLayout = QtGui.QVBoxLayout()
        pieButtons.setLayout(pieButtonsLayout)
        pieButtonsLayout.setContentsMargins(0, 0, 0, 0)
        pieButtonsLayout.addWidget(buttonListWidget)

        buttonsLayout = QtGui.QHBoxLayout()
        buttonsLayout.addStretch(1)
        
        buttonsLayout.addWidget(buttonAddSeparator)
        buttonsLayout.addWidget(buttonRemoveCommand)
        buttonsLayout.addWidget(buttonDown)
        buttonsLayout.addWidget(buttonUp)

        pieButtonsLayout.insertLayout(1, buttonsLayout)

        vSplitter = QtGui.QSplitter()
        vSplitter.insertWidget(0, pieButtons)
        vSplitter.insertWidget(0, tabs)

        preferencesWidget = QtGui.QWidget()
        preferencesLayout = QtGui.QHBoxLayout()
        preferencesLayout.setContentsMargins(0, 0, 0, 0)
        preferencesWidget.setLayout(preferencesLayout)
        preferencesLayout.addWidget(vSplitter)

        pieMenuDialog = PieMenuDialog()

        pieMenuDialogLayout = QtGui.QVBoxLayout()
        pieMenuDialog.setLayout(pieMenuDialogLayout)
        pieMenuDialog.show()

        info_button = QtGui.QPushButton()
        info_button.setToolTip(translate("MainWindow", "About"))
        info_button.setMaximumWidth(80)
        info_button.setIcon(QtGui.QIcon.fromTheme(iconInfo))
        info_button.clicked.connect(infoPopup)

        doc_button = QtGui.QPushButton(translate("MainWindow", "Documentation"))
        doc_button.setToolTip(translate("MainWindow", "Documentation"))
        doc_button.setIcon(QtGui.QIcon.fromTheme(iconDocumentation))
        doc_button.clicked.connect(documentationLink)

        close_button = QtGui.QPushButton(translate("MainWindow", "Close"), \
                                         pieMenuDialog)
        close_button.setMaximumWidth(120)
        close_button.clicked.connect(pieMenuDialog.close)

        # Create a horizontal layout for the buttons
        button_row_layout = QtGui.QHBoxLayout()
        button_row_layout.addWidget(info_button)
        button_row_layout.addStretch(1)
        button_row_layout.addWidget(close_button, 0, alignment=QtCore.Qt.AlignCenter)
        button_row_layout.addStretch(1)
        button_row_layout.addWidget(doc_button, 0, alignment=QtCore.Qt.AlignRight)

        button_layout = QtGui.QVBoxLayout()
        button_layout.addLayout(layoutInfoShortcut)

        button_layout.addLayout(button_row_layout)

        pieMenuDialogLayout.addWidget(preferencesWidget)
        pieMenuDialogLayout.addLayout(button_layout)

        cBoxUpdate()
        #### END Preferences dialog ####

    ####END Functions Def ####
    
    #### Main code ####
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

    sign = {
        "<": operator.lt,
        "<=": operator.le,
        "==": operator.eq,
        "!=": operator.ne,
        ">": operator.gt,
        ">=": operator.ge,
        }

    styleCurrentTheme = getStyle()
    globalShortcutKey = paramGet.GetString("GlobalShortcutKey")

    checkboxGlobalKeyToggle = QCheckBox()
    checkboxGlobalKeyToggle.setCheckable(True)

    checkboxGlobalKeyToggle.setChecked(getParameterGlobal("Bool", "GlobalKeyToggle"))
    checkboxGlobalKeyToggle.stateChanged.connect(setGlobalKeyToggle)


    buttonListWidget = QtGui.QListWidget()
    buttonListWidget.setHorizontalScrollBarPolicy(QtCore
                                                  .Qt.ScrollBarAlwaysOff)

    comboBoxTheme = QComboBox()
    comboBoxTheme.setMinimumWidth(120)

    getTheme()

    cBox = QtGui.QComboBox()
    cBox.setMinimumHeight(30)
    cBox.currentIndexChanged.connect(onPieChange)

    infoShortcut = QLabel()

    shortcutLineEdit = CustomLineEdit()
    shortcutLineEdit.setText(shortcutKey)

    globalShortcutLineEdit = CustomLineEdit()
    globalShortcutLineEdit.setText(globalShortcutKey)
    globalShortcutLineEdit.setToolTip(translate("GlobalSettingsTab", "For TAB press CTRL+TAB"))

    labelGlobalKeyToggle = QLabel(translate("GlobalSettingsTab","Shortcuts behavior: Toggle show/hide PieMenu:"))
    labelGlobalKeyToggle.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)

    labelShortcut = QLabel()
    labelShortcut.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
    labelGlobalShortcut = QLabel()
    labelGlobalShortcut.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)

    assignShortcutButton = QtGui.QPushButton(translate("GlobalSettingsTab", "Assign"))
    assignShortcutButton.clicked.connect(lambda: updateShortcutKey(shortcutLineEdit.text()))

    assignGlobalShortcutButton = QtGui.QPushButton(translate("PieMenuTab", \
                                                                 "Assign"))
    assignGlobalShortcutButton.clicked.connect(lambda: updateGlobalShortcutKey(globalShortcutLineEdit.text()))

    separatorPieMenu = QtGui.QFrame()
    separatorPieMenu.setObjectName("separatorPieMenu")
    separatorPieMenu.setFrameShape(QtGui.QFrame.HLine)
    separatorPieMenu.setFrameShadow(QtGui.QFrame.Sunken)
    separatorPieMenu.setStyleSheet(styleCurrentTheme)

    separatorSettings = QtGui.QFrame()
    separatorSettings.setObjectName("separatorSettings")
    separatorSettings.setFrameShape(QtGui.QFrame.HLine)
    separatorSettings.setFrameShadow(QtGui.QFrame.Sunken)
    separatorSettings.setStyleSheet(styleCurrentTheme)

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

    labelWbForPieMenu = QtGui.QLabel(translate("PieMenuTab", "Workbench associated to this PieMenu:"))
    labelWbForPieMenu.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)

    comboWbForPieMenu = QComboBox()
    comboWbForPieMenu.setMinimumWidth(160)
    comboWbForPieMenu.currentIndexChanged.connect(onWbForPieMenu)

    labelRadius = QtGui.QLabel(translate("PieMenuTab", "Pie size:"))
    labelRadius.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)

    spinRadius = QtGui.QSpinBox()
    spinRadius.setMaximum(9999)
    spinRadius.setMinimumWidth(160)
    spinRadius.valueChanged.connect(onSpinRadius)

    labelHoverDelay = QtGui.QLabel(translate("GlobalSettingsTab", "Hover delay (ms):"))
    labelHoverDelay.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)

    spinHoverDelay = QtGui.QSpinBox()
    spinHoverDelay.setMaximum(999)
    spinHoverDelay.setMinimumWidth(90)
    spinHoverDelay.valueChanged.connect(onSpinHoverDelay)

    labelShape = QtGui.QLabel(translate("PieMenuTab", "Shape:"))
    labelShape.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)

    labeldisplayCommandName = QtGui.QLabel(translate("PieMenuTab", "Show command names:"))
    labeldisplayCommandName.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)

    labeldisplayShortcut = QtGui.QLabel(translate("PieMenuTab", "Enable tools shortcuts:"))
    labeldisplayShortcut.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)

    labelShortcutSize = QtGui.QLabel(translate("PieMenuTab", "Size:"))
    labelShortcutSize.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)

    spinShortcutLabelSize = QtGui.QSpinBox()
    spinShortcutLabelSize.setMinimum(6)
    spinShortcutLabelSize.setMaximum(50)
    spinShortcutLabelSize.setMinimumWidth(90)
    spinShortcutLabelSize.valueChanged.connect(onSpinShortcutLabelSize)
    ########### TO DO set default value to spinShortcutLabelSize

    spinNumColumn = QtGui.QSpinBox()
    spinNumColumn.setMaximum(12)
    spinNumColumn.setMinimumWidth(120)
    spinNumColumn.valueChanged.connect(onNumColumn)

    spinIconSpacing = QtGui.QSpinBox()
    spinIconSpacing.setMaximum(200)
    spinIconSpacing.setMinimumWidth(0)
    spinIconSpacing.valueChanged.connect(onIconSpacing)

    spinCommandPerCircle = QtGui.QSpinBox()
    spinCommandPerCircle.setMaximum(20)
    spinCommandPerCircle.setMinimum(2)
    spinCommandPerCircle.setMinimumWidth(0)
    spinCommandPerCircle.valueChanged.connect(onCommandPerCircle)

    radioButtonPress = QtGui.QRadioButton(translate("GlobalSettingsTab", "Press"))
    radioButtonPress.toggled.connect(lambda checked, data="Press": setTriggerMode(data))

    radioButtonHover = QtGui.QRadioButton(translate("GlobalSettingsTab", "Hover"))
    radioButtonHover.toggled.connect(lambda checked, data="Hover":  setTriggerMode(data))

    comboShape = QComboBox()
    comboShape.setMinimumWidth(100)
    comboShape.currentIndexChanged.connect(setShape)

    labelNumColumn = QtGui.QLabel(translate("PieMenuTab", "Number of columns:"))
    labelNumColumn.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)

    labelIconSpacing = QtGui.QLabel(translate("PieMenuTab", "Icon spacing:"))
    labelIconSpacing.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)

    labelCommandPerCircle = QtGui.QLabel(translate("PieMenuTab", "Command per circle:"))
    labelCommandPerCircle.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)

    cboxDisplayCommandName = QCheckBox()
    cboxDisplayCommandName.setCheckable(True)
    cboxDisplayCommandName.stateChanged.connect(lambda state: onDisplayCommandName(state))

    cboxDisplayShortcut = QCheckBox()
    cboxDisplayShortcut.setCheckable(True)
    cboxDisplayShortcut.stateChanged.connect(lambda state: onDisplayShortcut(state))

    labelButton = QtGui.QLabel(translate("PieMenuTab", "Button size:"))
    labelButton.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)

    spinButton = QtGui.QSpinBox()
    spinButton.setMaximum(999)
    spinButton.setMinimumWidth(160)
    spinButton.valueChanged.connect(onSpinButton)

    toolListWidget = QtGui.QListWidget()
    toolListWidget.setSortingEnabled(True)
    toolListWidget.sortItems(QtCore.Qt.AscendingOrder)
    toolListWidget.setHorizontalScrollBarPolicy(QtCore
                                                .Qt.ScrollBarAlwaysOff)

    toolListLayout = QVBoxLayout()

    searchLayout = QHBoxLayout()

    searchLineEdit = QLineEdit()
    searchLineEdit.setPlaceholderText(translate("ToolsTab", "Search"))

    searchResultLabel = QLabel()

    clearButton = QtGui.QToolButton()
    clearButton.setToolTip(translate("ToolsTab", "Clear search"))
    clearButton.setMaximumWidth(40)
    clearButton.setIcon(QtGui.QIcon.fromTheme(iconBackspace))
    clearButton.clicked.connect(searchLineEdit.clear)

    searchLayout.addWidget(searchLineEdit)
    searchLayout.addWidget(clearButton)

    toolListLayout.addLayout(searchLayout)
    toolListLayout.addWidget(toolListWidget)

    widgetContainer = QWidget()
    widgetContainer.setLayout(toolListLayout)
    widgetContainer.setMinimumHeight(380)

    checkboxQuickMenu = QCheckBox()
    checkboxQuickMenu.setCheckable(True)
    checkboxQuickMenu.setChecked(paramGet.GetBool("ShowQuickMenu"))

    checkboxGlobalContext = QCheckBox()
    checkboxGlobalContext.setCheckable(True)
    enableContext = paramGet.GetBool("EnableContext")
    checkboxGlobalContext.setChecked(enableContext)

    checkboxGlobalContext.stateChanged.connect(lambda state: onContext(state))

    toolListWidget.itemChanged.connect(onToolListWidget)

    searchLineEdit.textChanged.connect(searchInToolList)

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

    labelContext = QtGui.QLabel(translate("ContextTab", "Enable"))
    
    checkContext = QtGui.QCheckBox()
    checkContext.stateChanged.connect(onCheckContext)

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

    # Create a fake command in FreeCAD to handle the PieMenu Separator
    FreeCADGui.addCommand('Std_PieMenuSeparator', PieMenuSeparator())

    mw = Gui.getMainWindow()
    start = True
    for action in mw.findChildren(QtGui.QAction):
        if action.objectName() == "PieMenuShortCut":
            start = False
        else:
            pass

    if start:
        remObsoleteParams()
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
