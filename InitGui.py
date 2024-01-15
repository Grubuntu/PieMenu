# PieMenu widget for FreeCAD

# Copyright (C) 2024 Grubuntu @ FreeCAD
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

# Changelog :
# 1.2.8 : 
# Added validation/cancel buttons for validate or close features window rapidly
# Added interactive spinbox for editing length/angle/size in features Pad, Pocket, Chamfer, Fillet, Thickness, Revolution
# Added transparent theme : choose via settings menu
# Added Sketcher context menu : show in context SketcherWB
# Added tempo on the hover to avoid too fast triggering
# Added 'PartDesign' and 'Sketcher' menu at first launch 
# Removed close button (useless, we can click outside the widget to close it)
#
# 1.2.9 : 
# Added ability to set global keyboard shortcut in settings menu
#
# 1.2.9.1 : 
# Correction for Theme setting
#
# 1.3.0 :
# Added ability to set a keyboard shortcut for each PieMenu

global PIE_MENU_VERSION
PIE_MENU_VERSION = "1.3.0"

def pieMenuStart():
    import math
    import operator
    import platform
    import FreeCAD as App
    import FreeCADGui as Gui
    from PySide import QtCore
    from PySide import QtGui
    import PieMenuLocator as locator
    from PySide2.QtGui import QKeyEvent
    from PySide.QtWidgets import QApplication, QLineEdit, QWidget, QAction, QPushButton, QLabel, QVBoxLayout, QHBoxLayout, QDoubleSpinBox, QCheckBox, QMessageBox, QShortcut
    from PySide2.QtGui import QKeySequence
    from PySide2.QtCore import Qt

    # global variables
    
    path = locator.path()
    respath = path + "/Resources/icons/"
    
    selectionTriggered = False
    contextPhase = False
    
    styleButton = ""
    theme = ""
    
    global shortcutKey
    global globalShortcutKey
    global shortcutList
    shortcutKey = ''
    globalShortcutKey = 'TAB'
    
    paramPath = "User parameter:BaseApp/PieMenu"
    paramIndexPath= "User parameter:BaseApp/PieMenu/Index"
    paramGet = App.ParamGet(paramPath)
    paramIndexGet = App.ParamGet(paramIndexPath)

    
    def setGlobalShortcutKey(globalShortcutKey):
        """ Set shortcut in user parameters """
        paramGet.SetString("GlobalShortcutKey", globalShortcutKey)

    def getGlobalShortcutKey():
        global globalShortcutKey
        """Get global shortcut key from user parameters."""
        globalShortcutKey = paramGet.GetString("GlobalShortcutKey")
        return globalShortcutKey
        
    globalShortcutKey = getGlobalShortcutKey()
    
    def getShortcutKey():
        global shortcutKey
        """Get shortcut key from user parameters."""
        indexList = paramIndexGet.GetString("IndexList")
        if indexList:
            indexList = list(map(int, indexList.split(".,.")))
        else:
            indexList = []
        try:
            selectedPieName = cBox.currentText()
        except:
            selectedPieName = ''
        for i in indexList:
            try:
                pieName = paramIndexGet.GetString(str(i)).decode("UTF-8")
            except AttributeError:
                pieName = paramIndexGet.GetString(str(i))
            if pieName == selectedPieName:
                param = paramIndexGet.GetGroup(str(i))
                shortcutKey = param.GetString("ShortcutKey")
        return shortcutKey
        
    def getShortcutList():
        global globalShortcutKey
        """Get keyboard shortcut and  namePie from user parameters"""
        indexList = paramIndexGet.GetString("IndexList")
         # Effacer les raccourcis existants
        for shortcut in mw.findChildren(QShortcut):
            if shortcut.activated is not None:
                shortcut.activated.disconnect()
            shortcut.setParent(None)
            shortcut.deleteLater()
        if indexList:
            indexList = list(map(int, indexList.split(".,.")))
        else:
            indexList = []
        resultShortcutList = []
        for i in indexList:
            param = paramIndexGet.GetGroup(str(i))
            namePie = paramIndexGet.GetString(str(i))
            shortcut = param.GetString("ShortcutKey")
            resultShortcutList.append((shortcut, namePie))
        for shortcutKey, key_value in resultShortcutList:
            shortcut = QShortcut(QKeySequence(shortcutKey), mw)
            shortcut.activated.connect(lambda keyValue=key_value: PieMenuInstance.showAtMouse(keyValue=keyValue, notKeyTriggered=False))
            shortcut.setEnabled(True)
        return resultShortcutList
        
    def setShortcutKey(shortcutKey):
        """ set shortcut in parameter """
        indexList = paramIndexGet.GetString("IndexList")
        if indexList:
            indexList = indexList.split(".,.")
            temp = []
            for i in indexList:
                temp.append(int(i))
            indexList = temp
        else:
            indexList = []
        for i in indexList:
            a = str(i)
            try:
                pieName = paramIndexGet.GetString(a).decode("UTF-8")
            except AttributeError:
                pieName = paramIndexGet.GetString(a)
            if pieName == cBox.currentText():
                param = paramIndexGet.GetGroup(str(i))
                param.SetString("ShortcutKey", shortcutKey)
                
    def remObsoleteParams():
        """Remove obsolete parameters from older versions."""
        paramGet.RemBool("ContextPhase")

    def accessoriesMenu():
        """Add pie menu preferences to accessories menu."""
        pref = QtGui.QAction(mw)
        pref.setText("Pie menu")
        pref.setObjectName("PieMenu")
        pref.triggered.connect(onPreferences)
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
                action.setIconText("Accessories")
                menu = QtGui.QMenu()
                action.setMenu(menu)
                menu.addAction(pref)

                def addMenu():
                    """Add accessories menu to the menu bar."""
                    mb.addAction(action)
                    action.setVisible(True)

                addMenu()
                mw.workbenchActivated.connect(addMenu)
                
                
    def onPreferences():
        """Open the preferences dialog."""
        onControl()
        
    def setButtonStyle():
        """ 2 stylesheets : Transparent and Legacy """
        theme = paramGet.GetString("Theme")
        if theme == "Transparent":
            styleButton = ("""
                QToolButton{
                background-color: transparent; border: none;
                }

                QToolButton:hover {
                    background-color: #888888; border: none;
                }

                QToolButton:checked {
                    background-color: lightGreen;
                }

                QToolButton::menu-indicator {
                    subcontrol-origin: padding;
                    subcontrol-position: center center;
                }
                
                """)
        else:
            styleButton = ("""
                QToolButton {
                    background-color: lightGray;
                    border: 1px outset silver;
                }

                QToolButton:disabled {
                    background-color: darkGray;
                }

                QToolButton:hover {
                    background-color: lightBlue;
                }

                QToolButton:checked {
                    background-color: lightGreen;
                }

                QToolButton::menu-indicator {
                    subcontrol-origin: padding;
                    subcontrol-position: center center;
                }

                """)
        
        return styleButton
    
    setButtonStyle()
    

    styleMenuClose = ("""
        QToolButton {
            background-color: rgba(60,60,60,255);
            color: silver;
            border: 1px solid #1e1e1e;
        }

        QToolButton::menu-indicator {
            image: none;
        }

        """)

    styleContainer = ("QMenu{background: transparent}")

    styleCombo = ("""
        QComboBox {
            background: transparent;
            border: 1px solid transparent;
        }

        """)

    styleQuickMenu = ("padding: 5px 10px 5px 10px")

    styleQuickMenuItem = ("""
        QMenu::item {
            padding: 5px 20px 5px 20px;
            text-align: left;
        }
        """)
        
    iconClose = respath + "PieMenuClose.svg"
    iconMenu = respath + "PieMenuQuickMenu.svg"
    iconUp = respath + "PieMenuUp.svg"
    iconDown = respath + "PieMenuDown.svg"
    iconAdd = respath + "PieMenuAdd.svg"
    iconRemove = respath + "PieMenuRemove.svg"
    iconRename = respath + "PieMenuRename.svg"
    iconCopy = respath + "PieMenuCopy.svg"
    iconRemoveCommand = respath + "PieMenuRemoveCommand.svg"
    iconValid = respath + "edit_OK.svg"
    iconCancel = respath + "edit_Cancel.svg"
    
    def radiusSize(buttonSize):
        radius = str(math.trunc(buttonSize / 2))
        return "QToolButton {border-radius: " + radius + "px}"

    def iconSize(buttonSize):
        icon = buttonSize / 3 * 2
        return icon

### Begin QuickMenu  Def ###
    def quickMenu(buttonSize=20):
        mw = Gui.getMainWindow()
        
        icon = iconSize(buttonSize)
        radius = radiusSize(buttonSize)

        menu = QtGui.QMenu(mw)
        menu.setStyleSheet(styleQuickMenu)

        button = QtGui.QToolButton()
        button.setMenu(menu)
        button.setProperty("ButtonX", 0)
        button.setProperty("ButtonY", 32)
        button.setGeometry(0, 0, buttonSize, buttonSize)
        button.setStyleSheet(styleMenuClose + radius)
        button.setIconSize(QtCore.QSize(icon, icon))
        button.setIcon(QtGui.QIcon(iconMenu))
        button.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        button.setPopupMode(QtGui.QToolButton
                            .ToolButtonPopupMode.InstantPopup)

        menuMode = QtGui.QMenu()
        menuMode.setTitle("Trigger")

        modeGroup = QtGui.QActionGroup(menuMode)
        modeGroup.setExclusive(True)

        actionPress = QtGui.QAction(modeGroup)
        actionPress.setText("Press")
        actionPress.setData("Press")
        actionPress.setCheckable(True)

        actionHover = QtGui.QAction(modeGroup)
        actionHover.setText("Hover")
        actionHover.setData("Hover")
        actionHover.setCheckable(True)

        menuMode.addAction(actionPress)
        menuMode.addAction(actionHover)

        actionContext = QtGui.QAction(menu)
        actionContext.setText("Context")
        actionContext.setCheckable(True)

        menuPieMenu = QtGui.QMenu()
        menuPieMenu.setTitle("PieMenu")

        pieGroup = QtGui.QActionGroup(menu)
        pieGroup.setExclusive(True)

        menuToolBar = QtGui.QMenu()
        menuToolBar.setTitle("ToolBar")
        menuToolBar.setStyleSheet(styleQuickMenuItem)

        toolbarGroup = QtGui.QMenu()

        toolbarGroupOps = QtGui.QActionGroup(toolbarGroup)
        toolbarGroupOps.setExclusive(True)

        prefAction = QtGui.QAction(menu)
        prefAction.setIconText("Preferences")

        prefButton = QtGui.QToolButton()
        prefButton.setDefaultAction(prefAction)

        prefButtonWidgetAction = QtGui.QWidgetAction(menu)
        prefButtonWidgetAction.setDefaultWidget(prefButton)
        

        def setChecked():
            if paramGet.GetString("TriggerMode") == "Hover":
                actionHover.setChecked(True)
            else:
                actionPress.setChecked(True)

            if paramGet.GetBool("EnableContext"):
                actionContext.setChecked(True)
            else:
                pass


        setChecked()


        def onModeGroup():
            text = modeGroup.checkedAction().data()
            paramGet.SetString("TriggerMode", text)
            PieMenuInstance.hide()
            PieMenuInstance.showAtMouse(notKeyTriggered=True)


        modeGroup.triggered.connect(onModeGroup)


        def onActionContext():
            if actionContext.isChecked():
                paramGet.SetBool("EnableContext", True)
                contextList()
            else:
                paramGet.SetBool("EnableContext", False)
            addObserver()


        actionContext.triggered.connect(onActionContext)


        def pieList():
            indexList = paramIndexGet.GetString("IndexList")
            menuPieMenu.clear()
            if indexList:
                indexList = indexList.split(".,.")
                temp = []
                for i in indexList:
                    temp.append(int(i))
                indexList = temp
            else:
                indexList = []
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


        menuPieMenu.aboutToShow.connect(pieList)


        def onPieGroup():
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


        pieGroup.triggered.connect(onPieGroup)


        def onMenuToolBar():
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
                    menu.aboutToShow.connect(lambda sender=menu: onMenuToolbarGroup(sender))
                    menuToolBar.addMenu(menu)
                else:
                    pass


        menuToolBar.aboutToShow.connect(onMenuToolBar)


        def isActualPie(text):
            if paramGet.GetBool("ToolBar"):
                entry = paramGet.GetString("ToolBar")
                if ": " in entry:
                    toolbar_desc = entry.split(": ")
                    idMenu = toolbar_desc[1]
                else:
                    idMenu = entry
                if idMenu == text:
                    return True;
            return False


        def onMenuToolbarGroup(sender):
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
            elif sender.text() == "Show":
                #Bug toolbar :  sender.data() est en français (langue locale) et est comparé plus loin à widgets.objectName() en Anglais
                #print('sender.data :', sender.data())
                
                # write persistent toolbar and its workbenches
                getGuiToolButtonData(sender.data(), None, None, workbenches)
                toolbar_desc = ", ".join(workbenches)
                toolbar_desc = toolbar_desc + ': ' + sender.data()
                paramGet.SetString("ToolBar", toolbar_desc)
                PieMenuInstance.hide()
                PieMenuInstance.showAtMouse(notKeyTriggered=True)


        toolbarGroup.triggered.connect(onToolbarGroup)


        def onPrefButton():
            PieMenuInstance.hide()
            onControl()
            
            
        prefButton.clicked.connect(onPrefButton)
        menu.addMenu(menuMode)
        menu.addAction(actionContext)
        menu.addSeparator()
        menu.addMenu(menuPieMenu)
        menu.addMenu(menuToolBar)
        menu.addSeparator()
        menu.addAction(prefButtonWidgetAction)

        return button 

### END QuickMenu   Def ###


    class HoverButton(QtGui.QToolButton):

        def __init__(self, parent=None):
            super(HoverButton, self).__init__()
            self.hoverTimer = QtCore.QTimer(self)
            self.hoverTimer.setSingleShot(True)
            self.hoverTimer.timeout.connect(self.onHoverTimeout)
            self.enterEventConnected = False
            self.isMouseOver = False 
            self.leaveEvent = self.onLeaveEvent

        def onHoverTimeout(self):
            mode = paramGet.GetString("TriggerMode")
            if self.isMouseOver and self.defaultAction().isEnabled() and mode == "Hover":
                PieMenuInstance.hide()
                self.defaultAction().trigger()
                try:
                    docName = App.ActiveDocument.Name
                    g = Gui.ActiveDocument.getInEdit()
                    module = g.Module
                except:
                    module = ''
                if (module is not None and module != 'SketcherGui'):
                    PieMenuInstance.showAtMouse()
            else:
                pass

        def onLeaveEvent(self, event):
            self.isMouseOver = False 

        def enterEvent(self, event):
            if not self.enterEventConnected:
                self.hoverTimer.start(250) # timer to avoid too fast triggering at  hover
                self.enterEventConnected = True
            self.hoverTimer.stop()  
            self.hoverTimer.start(250) # timer to avoid too fast triggering at hover
            self.isMouseOver = True  

        def mouseReleaseEvent(self, event):
            mode = paramGet.GetString("TriggerMode")
            if self.isMouseOver and self.defaultAction().isEnabled():
                PieMenuInstance.hide()
                self.defaultAction().trigger()
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


    class PieMenu(QWidget):
        mw = Gui.getMainWindow()
        event_filter_installed = False
        offset_x = 0
        offset_y = 0
        
        def __init__(self, parent=mw):
            super().__init__()
            self.double_spinbox = None
            
            if not PieMenu.event_filter_installed:
                app = QtGui.QGuiApplication.instance() or QtGui.QApplication([])
                app.installEventFilter(self)
                PieMenu.event_filter_installed = True
            self.radius = 100
            self.buttons = []
            self.buttonSize = 32
            self.menu = QtGui.QMenu(mw)
            self.menuSize = 0
            self.menu.setStyleSheet(styleContainer)
            self.menu.setWindowFlags(self.menu.windowFlags() | QtCore.Qt.FramelessWindowHint)     
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
            button.setProperty("ButtonX", -25)
            button.setProperty("ButtonY", 0)
            button.setGeometry(0, 0, buttonSize, buttonSize)
            button.setIconSize(QtCore.QSize(icon, icon))
            button.setIcon(QtGui.QIcon(iconValid))
            styleButton = setButtonStyle()
            button.setStyleSheet(styleButton + " QWidget { border-radius: 5px; }")
            return button
            
        def cancelButton(self, buttonSize=38):
            icon = iconSize(buttonSize)
            button = QtGui.QToolButton()
            button.setProperty("ButtonX", 25)
            button.setProperty("ButtonY", 0)
            button.setGeometry(0, 0, buttonSize, buttonSize)
            button.setIconSize(QtCore.QSize(icon, icon))
            button.setIcon(QtGui.QIcon(iconCancel))
            styleButton = setButtonStyle()
            button.setStyleSheet(styleButton + " QWidget { border-radius: 5px; }")
            return button
            
        def doubleSpinbox(self, buttonSize=32):
            button = QtGui.QDoubleSpinBox()
            button.setDecimals(3)
            button.setFixedWidth(90)
            button.setMaximum(1000000)
            button.setAlignment(QtCore.Qt.AlignRight)
            button.setProperty("ButtonX", 0)
            button.setProperty("ButtonY", -30)
            button.setAttribute(QtCore.Qt.WA_TranslucentBackground)
            button.setStyleSheet(" QWidget { border-radius: 5px; }")            
            return button                      
                                        
        def eventFilter(self, obj, event):
            if event.type() == QtCore.QEvent.KeyPress:
                key = event.key()
                if key == QtCore.Qt.Key_Enter or key == QtCore.Qt.Key_Return:
                    try:
                        if (self.double_spinbox.isVisible() == True):
                            self.validation()  
                    except:
                        None
            return super(PieMenu, self).eventFilter(obj, event)


        def add_commands(self, commands, context=False):
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
            if context:
                group = getGroup(mode=2)
            else:
                group = getGroup(mode=1)
            if len(commands) == 0:
                commandNumber = 1
            else:
                commandNumber = len(commands)
            valueRadius = group.GetInt("Radius")
            valueButton = group.GetInt("Button")
            if paramGet.GetBool("ToolBar"):
                valueRadius = 100
                valueButton = 32
            if valueRadius:
                self.radius = valueRadius
            else:
                self.radius = 100
            if valueButton:
                self.buttonSize = valueButton
            else:
                self.buttonSize = 32
            if commandNumber == 1:
                angle = 0
                buttonSize = self.buttonSize
            else:
                angle = 2 * math.pi / commandNumber
                buttonRadius = math.sin(angle / 2) * self.radius
                buttonSize = math.trunc(2 * buttonRadius / math.sqrt(2))
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
            num = 1
            for i in commands:
                if (Gui.ActiveDocument.getInEdit() is None) or (module == 'SketcherGui'):
                    """ show PieMenu in Edit Feature and in Sketcher """
                    button = HoverButton()
                    button.setParent(self.menu)
                    button.setAttribute(QtCore.Qt.WA_Hover)
                    styleButton = setButtonStyle()
                    button.setStyleSheet(styleButton + radius)
                    button.setDefaultAction(commands[commands.index(i)])
                    button.setGeometry(0, 0, buttonSize, buttonSize)
                    button.setIconSize(QtCore.QSize(icon, icon))
                    button.setProperty("ButtonX", self.radius *
                                       (math.cos(angle * num + angleStart)))
                    button.setProperty("ButtonY", self.radius *
                                       (math.sin(angle * num + angleStart)))
                    self.buttons.append(button)
                else:
                    None
                num = num + 1 
            buttonQuickMenu = quickMenu()
            buttonQuickMenu.setParent(self.menu)
            if (module != 'SketcherGui'): # TO SOLVE : we hide setting menu in sketcher to prevent user to go in the preferences dialog : there is a bug with settings
                self.buttons.append(buttonQuickMenu)
            buttonQuickMenu.hide()

            """ show Valid and Cancel buttons always """
            # buttonValid = self.validButton()
            # buttonValid.setParent(self.menu)
            # buttonValid.clicked.connect(self.validation)
            # self.buttons.append(buttonValid)
            
            # buttonCancel = self.cancelButton()
            # buttonCancel.setParent(self.menu)
            # buttonCancel.clicked.connect(self.cancel)
            # self.buttons.append(buttonCancel)
            
            self.offset_x = 0
            self.offset_y = 0
            try:
                if (Gui.ActiveDocument.getInEdit() != None):
                    """ or show Valid and Cancel buttons in Edit Feature Only """
                    buttonValid = self.validButton()
                    buttonValid.setParent(self.menu)
                    buttonValid.clicked.connect(self.validation)
                    self.buttons.append(buttonValid)
                    
                    buttonCancel = self.cancelButton()
                    buttonCancel.setParent(self.menu)
                    buttonCancel.clicked.connect(self.cancel)
                    self.buttons.append(buttonCancel)
                
                    self.offset_x = 28
                    self.offset_y = 0
                    if (module != None and module != 'SketcherGui' and wbName == 'PartDesignWorkbench'): 
                        """ Show Spinbox in Edit Feature in Part Design WB only """
                        fonctionActive = g.Object
                        featureName = g.Object.Name
                        
                        double_spinbox = self.doubleSpinbox()
                        double_spinbox.setParent(self.menu)
                        double_spinbox.valueChanged.connect(self.spin_interactif)
                        self.buttons.append(double_spinbox)
                        double_spinbox.setVisible(True)
                        self.double_spinbox = double_spinbox
                        
                        if (str(fonctionActive) == '<PartDesign::Fillet>'):
                            self.double_spinbox.setValue(g.Object.Radius)
                        elif (str(fonctionActive) == '<PartDesign::Chamfer>'):
                            self.double_spinbox.setValue(g.Object.Size)
                        elif (str(fonctionActive) == '<PartDesign::Pad>'):
                            self.double_spinbox.setValue(g.Object.Length)
                        elif (str(fonctionActive) == '<PartDesign::Pocket>'):
                            self.double_spinbox.setValue(g.Object.Length)
                        elif (str(fonctionActive) == '<PartDesign::Thickness>'):
                            self.double_spinbox.setValue(g.Object.Value)
                        elif (str(fonctionActive) == '<PartDesign::Revolution>'):
                            self.double_spinbox.setValue(g.Object.Angle)
                        elif (str(fonctionActive) == '<PartDesign::Hole>'): # TODO :  à developper pour gérer la fonction Hole
                            self.buttons.remove(double_spinbox)
                        else:
                            self.buttons.remove(double_spinbox)
                            
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

        def showAtMouse(self, keyValue=None, notKeyTriggered=False):
            nonlocal selectionTriggered
            nonlocal contextPhase
            global lastPosX
            global lastPosY

            enableContext = paramGet.GetBool("EnableContext")

            if contextPhase:
                sel = Gui.Selection.getSelectionEx()
                if not sel:
                    self.hide()
                    contextPhase = False
                    updateCommands()
                elif not enableContext:
                    self.hide()
                    updateCommands()
                else:
                    updateCommands(context=True)
            else:
                updateCommands(keyValue)

            if self.menu.isVisible():
                self.hide()
            else:
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
                        i.move(i.property("ButtonX") + (self.menuSize - i.size().width()) / 2 + self.offset_x,
                               i.property("ButtonY") + (self.menuSize - i.size().height()) / 2 + self.offset_y)
                        i.setVisible(True)

                    self.menu.popup(QtCore.QPoint(pos.x() - self.menuSize / 2, pos.y() - self.menuSize / 2))


        def spin_interactif(self):
            docName = App.ActiveDocument.Name 
            g = Gui.ActiveDocument.getInEdit()
            fonctionActive = g.Object
            featureName = g.Object.Name
            size = self.double_spinbox.value()
            if (str(fonctionActive) == '<PartDesign::Fillet>'):
                App.getDocument(docName).getObject(featureName).Radius = size
            elif (str(fonctionActive) == '<PartDesign::Chamfer>'):
                App.getDocument(docName).getObject(featureName).Size = size
            elif (str(fonctionActive) == '<PartDesign::Pad>'):
                App.getDocument(docName).getObject(featureName).Length = size
            elif (str(fonctionActive) == '<PartDesign::Pocket>'):
                App.getDocument(docName).getObject(featureName).Length = size
            elif (str(fonctionActive) == '<PartDesign::Thickness>'):
                App.getDocument(docName).getObject(featureName).Value = size
            elif (str(fonctionActive) == '<PartDesign::Revolution>'):
                App.getDocument(docName).getObject(featureName).Angle = size
            elif (str(fonctionActive) == '<PartDesign::Hole>'):
                self.double_spinbox.setVisible(False)
            else:
                self.double_spinbox.setVisible(False)
            App.ActiveDocument.recompute()
           
    sign = {
        "<": operator.lt,
        "<=": operator.le,
        "==": operator.eq,
        "!=": operator.ne,
        ">": operator.gt,
        ">=": operator.ge,
        }
        

    def contextList():
        indexList = paramIndexGet.GetString("IndexList")
        contextAll.clear()
        if indexList:
            indexList = indexList.split(".,.")
            temp = []
            for i in indexList:
                temp.append(int(i))
            indexList = temp
        else:
            indexList = []
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

            updateCommands(context=True)
            PieMenuInstance.hide()
            selectionTriggered = True
            #PieMenuInstance.showAtMouse(notKeyTriggered=True) 
        else:
            pass


    class SelObserver:
        def addSelection(self, doc, obj, sub, pnt):
            listTopo()

        def removeSelection(self, doc, obj, sub):
            listTopo()


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
            if not workbench in workbenches:
                workbenches.append(workbench)

    def getGuiToolButtonData(idToolBar, actions, commands, workbenches):
        #idToolBar is in the locale language setting, but need to be in english
        actionMapAll = getGuiActionMapAll()
        for i in actionMapAll:
            action = actionMapAll[i]
            for widgets in action.associatedWidgets():
                if widgets.objectName() == idToolBar:
                    getActionData(action, actions, commands, workbenches)
                    

    def actualizeWorkbenchActions(actions, toolList, actionMap):
        for i in toolList:
            # rule out special case: there has to be an entry
            if i == "":
                pass
            elif i in actionMap:
                if not actionMap[i] in actions:
                    actions.append(actionMap[i])
            else:
                cmd_parts = i.split("_")
                # rule out special case: unknown Std action
                if cmd_parts[0] == "Std":
                    pass
                else:
                    # match special cases
                    # Fem workbench
                    if cmd_parts[0] == "FEM":
                        cmd_parts[0] = "Fem"
                    # Sheet Metal workbench
                    if cmd_parts[0][:2] == "SM":
                        cmd_parts[0] = cmd_parts[0][:2]
                    cmdWb = cmd_parts[0] + "Workbench"
                    # after workbench activation actionMap has to be actualized
                    Gui.activateWorkbench(cmdWb)
                    return True
        return False


    def updateCommands(keyValue=None, context=False):
        indexList = paramIndexGet.GetString("IndexList")
        if paramGet.GetBool("ToolBar") and context is False:

            toolbar = paramGet.GetString("ToolBar")

            if ": " in toolbar:
                toolbar_desc = toolbar.split(": ")
                toolbar = toolbar_desc[1]
                workbenches = toolbar_desc[0]
                workbenches = workbenches.split(", ")
                lastWorkbench = Gui.activeWorkbench()
                for i in workbenches:
                    # rule out special cases
                    if i == None or i == "Std":
                        #wb = Gui.activeWorkbench()
                        #workbenches = wb.name()
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
                        try:
                            Gui.activateWorkbench(i + "Workbench")
                        except:
                            None

                Gui.activateWorkbench(lastWorkbench.__class__.__name__)
            else:
                pass
            actions = []
            getGuiToolButtonData(toolbar, actions, None, None)

        else:

            if indexList:
                indexList = indexList.split(".,.")

                temp = []

                for i in indexList:
                    temp.append(int(i))

                indexList = temp
            else:
                indexList = []
            
            #print('keyValue', keyValue)
            # keyValue != de None when a shortcutkey is pressed
            if keyValue == None:
                try:
                    docName = App.ActiveDocument.Name
                    g = Gui.ActiveDocument.getInEdit()
                    module = g.Module
                except:
                    module = None
                if (module != None and module == 'SketcherGui'): 
                    """ In Sketcher WB we load the Sketcher PieMenu """
                    text = 'Sketcher'
                else :    
                    if context:
                        try:
                            text = paramGet.GetString("ContextPie").decode("UTF-8")
                        except AttributeError:
                            text = paramGet.GetString("ContextPie")
                    else:
                        if keyValue == 'CurrentPie':
                            try:
                                text = paramGet.GetString("CurrentPie").decode("UTF-8")
                            except AttributeError:
                                text = paramGet.GetString("CurrentPie")
                        else:
                            if keyValue == None:
                                try:
                                    text = paramGet.GetString("CurrentPie").decode("UTF-8")
                                except AttributeError:
                                    text = paramGet.GetString("CurrentPie")
                            else :
                                """ get text send in shortcutkey sender """
                                text = keyValue
            else:
                """ get text send in shortcutkey sender"""
                text = keyValue
                
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
            #lastWorkbench = Gui.activeWorkbench()
            while actualizeWorkbenchActions(actions, toolList, actionMapAll):
                actionMapAll = getGuiActionMapAll()
            else:
                pass
            #Gui.activateWorkbench(lastWorkbench.__class__.__name__)
           
        PieMenuInstance.add_commands(actions, context)


    def getGroup(mode=0):
        indexList = paramIndexGet.GetString("IndexList")
        #### For Sketcher Mod ####
        try:
            docName = App.ActiveDocument.Name
            g = Gui.ActiveDocument.getInEdit()
            module = g.Module
        except:
            module = None
            
        if (module != None and module == 'SketcherGui'): 
            text = 'Sketcher'
        else :    
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
        #### End Sketcher Mod ####

        if indexList:
            indexList = indexList.split(".,.")

            temp = []

            for i in indexList:
                temp.append(int(i))

            indexList = temp
        else:
            indexList = []

        group = None

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
            pass
        else:
            if 0 in indexList:
                group = paramIndexGet.GetGroup("0")
            else:
                setDefaultPie()
                updateCommands()
                group = paramIndexGet.GetGroup("0")

        return group

    buttonListWidget = QtGui.QListWidget()
    buttonListWidget.setHorizontalScrollBarPolicy(QtCore
                                                  .Qt.ScrollBarAlwaysOff)

    def setTheme(state):
        if state == Qt.Checked:
            paramGet.SetString("Theme", "Transparent")
        else:
            paramGet.SetString("Theme", "Legacy")

    def getTheme():
        theme = paramGet.GetString("Theme")
        actionTheme.setChecked(theme == "Transparent")


    actionTheme = QCheckBox()
    actionTheme.setCheckable(True)
    getTheme()
    
    
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
                            workbenches.append(cmd_parts[0])
                            Gui.activateWorkbench(cmd_parts[0] + "Workbench")
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


    cBox = QtGui.QComboBox()
    cBox.setMinimumHeight(30)


    def cBoxUpdate():
        indexList = paramIndexGet.GetString("IndexList")
        try:
            currentPie = paramGet.GetString("CurrentPie").decode("UTF-8")
        except AttributeError:
            currentPie = paramGet.GetString("CurrentPie")
        if indexList:
            indexList = indexList.split(".,.")
            temp = []
            for i in indexList:
                temp.append(int(i))
            indexList = temp
        else:
            indexList = []
        pieList = []
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


    class CustomLineEdit(QLineEdit):
        """ get key event from box shortcut in settings """
        def __init__(self):
            super(CustomLineEdit, self).__init__()

        def keyPressEvent(self, event):
            key_text = QKeySequence(event.key()).toString()
            modifier_text = self.get_modifier_text(event.modifiers())
            if key_text and modifier_text:
                shortcut_text = f"{modifier_text}+{key_text}"
                self.setText(shortcut_text)
            else:
                super().keyPressEvent(event)

        def get_modifier_text(self, modifiers):
            modifier_names = {
                Qt.ControlModifier: 'CTRL',
                Qt.AltModifier: 'ALT',
                Qt.ShiftModifier: 'SHIFT',
                Qt.MetaModifier: 'META'
            }
            modifier_text = '+'.join([modifier_names[modifier] for modifier in modifier_names if modifiers & modifier])
            return modifier_text
            
            
    shortcutLineEdit = CustomLineEdit()
    shortcutLineEdit.setText(shortcutKey)
    
    globalShortcutLineEdit = CustomLineEdit()
    globalShortcutLineEdit.setText(globalShortcutKey)
    
    labelShortcut = QLabel()
    labelGlobalShortcut = QLabel()


    def onPieChange():
        buttonList()
        toolList()
        setDefaults()
        setCheckContext()
        getShortcutKey()
        getShortcutList()
        shortcutLineEdit.setText(shortcutKey)
        globalShortcutLineEdit.setText(globalShortcutKey)
        labelShortcut.setText('Current shortcut : ' + shortcutKey)
        labelGlobalShortcut.setText('Global shortcut : ' + globalShortcutKey)
        
        
    cBox.currentIndexChanged.connect(onPieChange)

    buttonAddPieMenu = QtGui.QToolButton()
    buttonAddPieMenu.setIcon(QtGui.QIcon(iconAdd))
    buttonAddPieMenu.setToolTip("Add new pie menu")
    buttonAddPieMenu.setMinimumHeight(30)
    buttonAddPieMenu.setMinimumWidth(30)


    def inputTextDialog(title):
        info1 = "Please insert menu name"
        info2 = "Menu already exists"
        d = QtGui.QInputDialog(pieMenuDialog)
        d.setModal(True)
        d.setInputMode(QtGui.QInputDialog.InputMode.TextInput)
        text, ok = QtGui.QInputDialog.getText(pieMenuDialog,
                                              title,
                                              info1)
        if not ok:
            return text, ok
        while not text:
            text, ok = QtGui.QInputDialog.getText(pieMenuDialog,
                                              title,
                                              info1)
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
            text, ok = QtGui.QInputDialog.getText(pieMenuDialog,
                                                  title,
                                                  info)
            if ok:
                if text:
                    index = cBox.findText(text)
                    info = info2
                else:
                    info = info1
            else:
                return text, ok
        return text, ok


    def splitIndexList(indexList):
        if indexList:
            indexList = indexList.split(".,.")
            temp = []
            for i in indexList:
                temp.append(int(i))
            indexList = temp
        else:
            indexList = []
        return indexList


    def createPie(text):
        indexList = paramIndexGet.GetString("IndexList")
        indexList = splitIndexList(indexList)
        pieList = []
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
        return paramIndexGet.GetGroup(indexNumber)


    def onButtonAddPieMenu():
        text, ok = inputTextDialog("New menu")
        if not ok:
            return
        createPie(text)
                
                
    buttonAddPieMenu.clicked.connect(onButtonAddPieMenu)

    buttonRemovePieMenu = QtGui.QToolButton()
    buttonRemovePieMenu.setIcon(QtGui.QIcon(iconRemove))
    buttonRemovePieMenu.setToolTip("Remove current pie menu")
    buttonRemovePieMenu.setMinimumHeight(30)
    buttonRemovePieMenu.setMinimumWidth(30)


    def onButtonRemovePieMenu():
        indexList = paramIndexGet.GetString("IndexList")
        indexList = splitIndexList(indexList)
        try:
            currentPie = paramGet.GetString("CurrentPie").decode("UTF-8")
        except AttributeError:
            currentPie = paramGet.GetString("CurrentPie")
        try:
            contextPie = paramGet.GetString("ContextPie").decode("UTF-8")
        except AttributeError:
            contextPie = paramGet.GetString("ContextPie")

        text = cBox.currentText()

        for i in indexList:
            a = str(i)
            try:
                pie = paramIndexGet.GetString(a).decode("UTF-8")
            except AttributeError:
                pie = paramIndexGet.GetString(a)
            if pie == text:
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

    buttonRemovePieMenu.clicked.connect(onButtonRemovePieMenu)

    buttonRenamePieMenu = QtGui.QToolButton()
    buttonRenamePieMenu.setToolTip("Rename current pie menu")
    buttonRenamePieMenu.setIcon(QtGui.QIcon(iconRename))
    buttonRenamePieMenu.setMinimumHeight(30)
    buttonRenamePieMenu.setMinimumWidth(30)
    
    
    def onButtonRenamePieMenu():
        text, ok = inputTextDialog("Rename menu")
        if not ok:
            return
        indexList = paramIndexGet.GetString("IndexList")
        indexList = splitIndexList(indexList)
        try:
            currentPie = paramGet.GetString("CurrentPie").decode("UTF-8")
        except AttributeError:
            currentPie = paramGet.GetString("CurrentPie")
        currentText = cBox.currentText()
        for i in indexList:
            a = str(i)
            try:
                pie = paramIndexGet.GetString(a).decode("UTF-8")
            except AttributeError:
                pie = paramIndexGet.GetString(a)
            if pie == currentText:
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


    buttonRenamePieMenu.clicked.connect(onButtonRenamePieMenu)    
    
    buttonCopyPieMenu = QtGui.QToolButton()
    buttonCopyPieMenu.setToolTip("Copy current pie menu")
    buttonCopyPieMenu.setIcon(QtGui.QIcon(iconCopy))
    buttonCopyPieMenu.setMinimumHeight(30)
    buttonCopyPieMenu.setMinimumWidth(30)


    def getCurrentMenuIndex(currentMenuName):
        indexList = paramIndexGet.GetString("IndexList")
        indexList = splitIndexList(indexList)
        for i in indexList:
            a = str(i)
            indexName = paramIndexGet.GetString(a)
            if indexName == currentMenuName:
                return a;
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
        text, ok = inputTextDialog("Copy menu")
        if not ok:
            return
        indexList = paramIndexGet.GetString("IndexList")
        indexList = splitIndexList(indexList)

        currentMenuName = cBox.currentText()
        indexOrg = getCurrentMenuIndex(currentMenuName)

        pieList = []

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
    
    buttonCopyPieMenu.clicked.connect(onButtonCopyPieMenu)

    labelRadius = QtGui.QLabel("Pie size")
    spinRadius = QtGui.QSpinBox()
    spinRadius.setMaximum(9999)
    spinRadius.setMinimumWidth(70)


    def onSpinRadius():
        group = getGroup()
        value = spinRadius.value()
        group.SetInt("Radius", value)


    spinRadius.valueChanged.connect(onSpinRadius)

    labelButton = QtGui.QLabel("Button size")
    spinButton = QtGui.QSpinBox()
    spinButton.setMaximum(999)
    spinButton.setMinimumWidth(70)
    
    
    def onSpinButton():
        group = getGroup()
        value = spinButton.value()
        group.SetInt("Button", value)


    spinButton.valueChanged.connect(onSpinButton)

    toolListWidget = QtGui.QListWidget()
    toolListWidget.setSortingEnabled(True)
    toolListWidget.sortItems(QtCore.Qt.AscendingOrder)
    toolListWidget.setHorizontalScrollBarPolicy(QtCore
                                                .Qt.ScrollBarAlwaysOff)



    def toolList():
        indexList = paramIndexGet.GetString("IndexList")
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
        if indexList:
            indexList = indexList.split(".,.")
            temp = []
            for i in indexList:
                temp.append(int(i))
            indexList = temp
        else:
            indexList = []
        toolListOn = None
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

        indexList = paramIndexGet.GetString("IndexList")

        if indexList:
            indexList = indexList.split(".,.")

            temp = []

            for i in indexList:
                temp.append(int(i))

            indexList = temp
        else:
            indexList = []

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


    toolListWidget.itemChanged.connect(onToolListWidget)


    def buttonList2ToolList(buttonListWidget):
        items = []
        for index in range(buttonListWidget.count()):
            items.append(buttonListWidget.item(index))
        toolData = []
        for i in items:
            toolData.append(i.data(QtCore.Qt.UserRole))
        group = getGroup()
        group.SetString("ToolList", ".,.".join(toolData))


    buttonUp = QtGui.QToolButton()
    buttonUp.setIcon(QtGui.QIcon(iconUp))
    buttonUp.setToolTip("Move selected command up")
    buttonUp.setMinimumHeight(30)
    buttonUp.setMinimumWidth(30)


    def onButtonUp():
        currentIndex = buttonListWidget.currentRow()
        if currentIndex != 0:
            currentItem = buttonListWidget.takeItem(currentIndex)
            buttonListWidget.insertItem(currentIndex - 1, currentItem)
            buttonListWidget.setCurrentRow(currentIndex - 1)
            buttonList2ToolList(buttonListWidget)


    buttonUp.clicked.connect(onButtonUp)

    buttonDown = QtGui.QToolButton()
    buttonDown.setIcon(QtGui.QIcon(iconDown))
    buttonDown.setToolTip("Move selected command down")
    buttonDown.setMinimumHeight(30)
    buttonDown.setMinimumWidth(30)


    def onButtonDown():
        currentIndex = buttonListWidget.currentRow()
        if currentIndex != buttonListWidget.count() - 1 and currentIndex != -1:
            currentItem = buttonListWidget.takeItem(currentIndex)
            buttonListWidget.insertItem(currentIndex + 1, currentItem)
            buttonListWidget.setCurrentRow(currentIndex + 1)
            buttonList2ToolList(buttonListWidget)


    buttonDown.clicked.connect(onButtonDown)

    buttonRemoveCommand = QtGui.QToolButton()
    buttonRemoveCommand.setIcon(QtGui.QIcon(iconRemoveCommand))
    buttonRemoveCommand.setToolTip("Remove selected command")
    buttonRemoveCommand.setMinimumHeight(30)
    buttonRemoveCommand.setMinimumWidth(30)


    def onButtonRemoveCommand():
        currentIndex = buttonListWidget.currentRow()
        buttonListWidget.takeItem(currentIndex)
        if currentIndex != 0:
            buttonListWidget.setCurrentRow(currentIndex - 1)
        buttonListWidget.setFocus()
        buttonList2ToolList(buttonListWidget)
        toolList()


    buttonRemoveCommand.clicked.connect(onButtonRemoveCommand)

    vertexItem = QtGui.QTableWidgetItem()
    vertexItem.setText("Vertex")
    vertexItem.setToolTip("Set desired operator and vertex number")
    vertexItem.setFlags(QtCore.Qt.ItemIsEnabled)

    edgeItem = QtGui.QTableWidgetItem()
    edgeItem.setText("Edge")
    edgeItem.setToolTip("Set desired operator and edge number")
    edgeItem.setFlags(QtCore.Qt.ItemIsEnabled)

    faceItem = QtGui.QTableWidgetItem()
    faceItem.setText("Face")
    faceItem.setToolTip("Set desired operator and face number")
    faceItem.setFlags(QtCore.Qt.ItemIsEnabled)

    objectItem = QtGui.QTableWidgetItem()
    objectItem.setText("Object")
    objectItem.setToolTip("Set desired operator and object number")
    objectItem.setFlags(QtCore.Qt.ItemIsEnabled)


    def comboBox(TopoType):
        signList = ["<", "<=", "==", "!=", ">", ">="]
        model = QtGui.QStandardItemModel()
        for i in signList:
            item = QtGui.QStandardItem()
            item.setText(i)
            item.setData(TopoType, QtCore.Qt.UserRole)
            model.setItem(signList.index(i), 0, item)
        comboBoxSign = QtGui.QComboBox()
        comboBoxSign.setModel(model)
        comboBoxSign.setStyleSheet(styleCombo)


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


    vertexComboBox = comboBox("VertexSign")
    edgeComboBox = comboBox("EdgeSign")
    faceComboBox = comboBox("FaceSign")
    objectComboBox = comboBox("ObjectSign")


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


    vertexSpin = spinBox("VertexValue")
    edgeSpin = spinBox("EdgeValue")
    faceSpin = spinBox("FaceValue")
    objectSpin = spinBox("ObjectValue")

    labelContext = QtGui.QLabel("Enable")
    checkContext = QtGui.QCheckBox()


    def setCheckContext():
        group = getGroup()
        groupContext = group.GetGroup("Context")
        if groupContext.GetBool("Enabled"):
            checkContext.setChecked(True)
            contextTable.setEnabled(True)
            resetButton.setEnabled(True)
        else:
            checkContext.setChecked(False)
            contextTable.setEnabled(False)
            resetButton.setEnabled(False)
        contextList()


    def onCheckContext():
        setDefaults()
        group = getGroup()
        groupContext = group.GetGroup("Context")
        if checkContext.isChecked():
            contextTable.setEnabled(True)
            resetButton.setEnabled(True)
            groupContext.SetBool("Enabled", 1)
        else:
            contextTable.setEnabled(False)
            resetButton.setEnabled(False)
            groupContext.SetBool("Enabled", 0)
        contextList()
        
        
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

    resetButton = QtGui.QToolButton()
    resetButton.setMinimumHeight(30)
    resetButton.setMinimumWidth(30)
    resetButton.setText(u'\u27F3')

    resetButton.setEnabled(False)


    def onResetButton():
        group = getGroup()
        group.RemGroup("Context")
        setDefaults()
        setCheckContext()


    resetButton.clicked.connect(onResetButton)


    def setDefaults():
        group = getGroup()
        groupContext = group.GetGroup("Context")
        vertexSign = groupContext.GetString("VertexSign")
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
        contextList()


    def setDefaultPie(restore=False):
        indexList = paramIndexGet.GetString("IndexList")

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
                               #"Sketcher_CompCurveEdition",  #removed for compatibility with 0.21
                               "Sketcher_ToggleConstruction"]

        if indexList:
            indexList = indexList.split(".,.")

            temp = []

            for i in indexList:
                temp.append(int(i))

            indexList = temp
        else:
            indexList = []

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
            
            paramIndexGet.SetString("1", "PartDesign")
            group = paramIndexGet.GetGroup("1")
            group.SetString("ToolList", ".,.".join(defaultToolsPartDesign))
            
            paramIndexGet.SetString("2", "Sketcher")
            group = paramIndexGet.GetGroup("2")
            group.SetString("ToolList", ".,.".join(defaultToolsSketcher))
            
        paramGet.SetBool("ToolBar", False)
        paramGet.RemString("ToolBar")
        paramGet.SetString("CurrentPie", "View")
        paramGet.SetString("Theme", "Legacy")
        paramGet.SetString("GlobalShortcutKey", "TAB")

        group = getGroup(mode=1)

        group.SetInt("Radius", 80)
        group.SetInt("Button", 32)
        
    def onControl():
        getTheme()
        global pieMenuDialog
        global shortcutKey
        global globalShortcutKey
        
        for i in mw.findChildren(QtGui.QDialog):
            if i.objectName() == "PieMenuPreferences":
                i.deleteLater()
            else:
                pass

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


        layoutRadius = QtGui.QHBoxLayout()
        layoutRadius.addWidget(labelRadius)
        layoutRadius.addStretch(1)
        layoutRadius.addWidget(spinRadius)

        layoutButton = QtGui.QHBoxLayout()
        layoutButton.addWidget(labelButton)
        layoutButton.addStretch(1)
        layoutButton.addWidget(spinButton)

        def updateShortcutKey(newShortcut):
            global shortcutKey
            touches_speciales = {'CTRL', 'ALT', 'SHIFT', 'META', 'TAB'}
            ##### voir pour suppression du raccourci
            if not newShortcut:
                shortcutKey = newShortcut
                setShortcutKey(shortcutKey)
                labelShortcut.setText('Shortcut deleted ! No shortcut assigned ' + shortcutKey)

            else:
                parties = set(newShortcut.split('+'))
                for partie in parties:
                    if partie not in touches_speciales and len(partie) > 1:
                        labelShortcut.setText('Invalid shortcut ! Current shortcut : ' + shortcutKey)
                    else :
                        shortcutKey = newShortcut
                        setShortcutKey(shortcutKey)
                        #actionKey.setShortcut(QtGui.QKeySequence(shortcutKey))  
                        labelShortcut.setText('New shortcut assigned: ' + shortcutKey)
                        setShortcutKey(shortcutKey)
            getShortcutList()
                
        getShortcutKey()
        
        labelShortcut.setText('Current shortcut : ' + shortcutKey)
        layoutShortcut = QtGui.QHBoxLayout()
        layoutShortcut.addWidget(labelShortcut)
        layoutShortcut.addStretch(1)
        layoutShortcut.addWidget(shortcutLineEdit)
        assignShortcutButton = QtGui.QPushButton("Assign")
        layoutShortcut.addWidget(assignShortcutButton)
        assignShortcutButton.clicked.connect(lambda: updateShortcutKey(shortcutLineEdit.text()))
      
        labelTheme = QLabel("Transparent theme")
        layoutTheme = QtGui.QHBoxLayout()
        layoutTheme.addWidget(labelTheme)
        layoutTheme.addStretch(1)
        layoutTheme.addWidget(actionTheme)
        actionTheme.stateChanged.connect(lambda state: setTheme(state))
      
        def updateGlobalShortcutKey(newShortcut):
            global globalShortcutKey
            touches_speciales = {'CTRL', 'ALT', 'SHIFT', 'META', 'TAB'}
            
            if not newShortcut:
                globalShortcutKey = newShortcut
                setGlobalShortcutKey(globalShortcutKey)
                labelGlobalShortcut.setText('Shortcut deleted ! No shortcut assigned ' + globalShortcutKey)
                
            else:
                parties = set(newShortcut.split('+'))
                for partie in parties:
                    if partie not in touches_speciales and len(partie) > 1:
                        labelGlobalShortcut.setText('Invalid shortcut  ! Current global shortcut : ' + globalShortcutKey)
                    else :
                        globalShortcutKey = newShortcut
                        setGlobalShortcutKey(globalShortcutKey)
                        labelGlobalShortcut.setText('New global shortcut assigned: ' + globalShortcutKey)
            actionKey.setShortcut(QtGui.QKeySequence(globalShortcutKey))

        getGlobalShortcutKey()

        labelGlobalShortcut.setText('Global shortcut : ' + globalShortcutKey)
        layoutGlobalShortcut = QtGui.QHBoxLayout()
        layoutGlobalShortcut.addWidget(labelGlobalShortcut)
        layoutGlobalShortcut.addStretch(1)
        layoutGlobalShortcut.addWidget(globalShortcutLineEdit)

        assignGlobalShortcutButton = QtGui.QPushButton("Assign")
        layoutGlobalShortcut.addWidget(assignGlobalShortcutButton)
        assignGlobalShortcutButton.clicked.connect(lambda: updateGlobalShortcutKey(globalShortcutLineEdit.text()))
        
        pieMenuTabLayout.insertLayout(0, layoutAddRemove)
        pieMenuTabLayout.insertSpacing(1, 18)
        pieMenuTabLayout.insertLayout(2, layoutShortcut)
        pieMenuTabLayout.insertLayout(3, layoutRadius)
        pieMenuTabLayout.insertLayout(4, layoutButton)
        pieMenuTabLayout.insertSpacing(5, 40)
        pieMenuTabLayout.insertLayout(6, layoutTheme)
        pieMenuTabLayout.insertLayout(7, layoutGlobalShortcut)
        pieMenuTabLayout.addStretch(0)
        
        contextTab = QtGui.QWidget()
        contextTabLayout = QtGui.QVBoxLayout()
        contextTab.setLayout(contextTabLayout)

        layoutCheckContext = QtGui.QHBoxLayout()
        layoutCheckContext.addWidget(labelContext)
        layoutCheckContext.addStretch(1)
        layoutCheckContext.addWidget(checkContext)

        resetLayout = QtGui.QHBoxLayout()
        resetLayout.addStretch(1)
        resetLayout.addWidget(resetButton)

        contextTabLayout.insertLayout(0, layoutCheckContext)
        contextTabLayout.addWidget(contextTable)
        contextTabLayout.insertLayout(2, resetLayout)
        contextTabLayout.addStretch(1)

        tabs.addTab(pieMenuTab, "PieMenu")
        tabs.addTab(toolListWidget, "Tools")
        tabs.addTab(contextTab, "Context")

        pieButtons = QtGui.QWidget()
        pieButtonsLayout = QtGui.QVBoxLayout()
        pieButtons.setLayout(pieButtonsLayout)
        pieButtonsLayout.setContentsMargins(0, 0, 0, 0)
        pieButtonsLayout.addWidget(buttonListWidget)

        buttonsLayout = QtGui.QHBoxLayout()
        buttonsLayout.addStretch(1)
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

        pieMenuDialog = QtGui.QDialog(mw)
        pieMenuDialog.resize(800, 450)
        pieMenuDialog.setObjectName("PieMenuPreferences")
        pieMenuDialog.setWindowTitle("PieMenu " + PIE_MENU_VERSION)
        pieMenuDialogLayout = QtGui.QVBoxLayout()
        pieMenuDialog.setLayout(pieMenuDialogLayout)
        pieMenuDialog.show()

        pieMenuDialogLayout.addWidget(preferencesWidget)
        
        cBoxUpdate()

        
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
        PieMenuInstance = PieMenu()
        actionKey = QtGui.QAction(mw)
        actionKey.setText("Invoke pie menu")
        actionKey.setObjectName("PieMenuShortCut")
        getGlobalShortcutKey()
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
