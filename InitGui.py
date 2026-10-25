# PieMenu widget for FreeCAD

# Copyright (C) 2026 Ben-PH,
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
PIE_MENU_VERSION = "1.14"
def pieMenuStart():
    # piemenu directory imports
    from piemenu import bootstrap as bootstrap_ui
    from piemenu import constants, config, context, defaults, observers, parameters, pie_menu, resources, shortcuts, state, theme, workbench
    from piemenu.commands import PieMenuSeparator
    from piemenu.ui import context as context_ui
    from piemenu.ui import icons as icons_ui
    from piemenu.ui import menus as menus_ui
    from piemenu.ui import misc as misc_ui
    from piemenu.ui import options as options_ui
    from piemenu.ui import preferences as preferences_ui
    from piemenu.ui import quick_menu as quick_menu_ui
    from piemenu.ui import settings as settings_ui
    from piemenu.ui import tab_context as tab_context_ui
    from piemenu.ui import tab_settings as tab_settings_ui
    from piemenu.ui import tab_toolbar as tab_toolbar_ui
    from piemenu.ui import tab_piemenu as tab_piemenu_ui
    from piemenu.ui import tab_assistant as tab_assistant_ui
    from piemenu.ui import toolbar as toolbar_ui
    from piemenu.ui import tool_list as tool_list_ui
    from piemenu.widgets import CustomLineEdit

    """Main function that starts the Pie Menu."""
    import math
    import os
    import platform

    import FreeCAD as App
    import FreeCADGui as Gui
    from FreeCAD import Units
    from PySide import QtCore, QtGui, QtWidgets
    from PySide.QtCore import Qt
    from PySide.QtWidgets import QCheckBox, QDialog, QGroupBox, QHBoxLayout, QLabel, QLineEdit, QListWidgetItem, QMessageBox, QVBoxLayout, QWidget

    from functools import partial

    PieMenu = pie_menu.PieMenu

    # Tool-list helpers now live in piemenu/ui/tool_list.py. The aliases below
    # keep the camelCase call sites used throughout pieMenuStart() working.
    sortToolListByColumn = tool_list_ui.sort_tool_list_by_column
    onToolListWidget = tool_list_ui.on_tool_list_widget
    searchInToolList = tool_list_ui.search_in_tool_list
    onButtonUp = tool_list_ui.on_button_up
    onButtonDown = tool_list_ui.on_button_down
    onButtonRemoveCommand = tool_list_ui.on_button_remove_command
    onButtonAddSeparator = tool_list_ui.on_button_add_separator

    # Generic UI helpers now live in piemenu/ui/misc.py. The aliases below keep
    # the camelCase call sites used throughout pieMenuStart() working.
    infoPopup = misc_ui.info_popup
    documentationLink = misc_ui.documentation_link

    # Preferences-dialog handlers now live in piemenu/ui/preferences.py. The
    # aliases below keep the camelCase call sites used throughout
    # pieMenuStart() working.
    PieMenuDialog = preferences_ui.PieMenuDialog

    # `updateCommands()` now lives in piemenu/pie_menu.py, next to the PieMenu
    # class that calls it. The alias below keeps the call sites used by the
    # `publish()` blocks working.
    updateCommands = pie_menu.update_commands

    state.app_state.loaded_workbenches = config.get_loaded_workbenches()
    state.app_state.signs = constants.get_signs()
    state.app_state.sort_order = QtCore.Qt.AscendingOrder
    state.app_state.context_phase = False

    # Add translations path
    translate = App.Qt.translate
    Gui.addLanguagePath(resources.transpath)
    Gui.updateLocale()


    # HACK: workaround to avoid ghosting : we find wbs already loaded,
    # so as not to reload them again in the function 'updateCommands'
    iconDefault = QtGui.QApplication.style().standardIcon(
        QtGui.QStyle.StandardPixmap.SP_DialogApplyButton)

    #### Main code ####

    #### MainWindow Preferences Dialog ####
    #### group PieMenu ####
    # PieMenu tab (piemenu/ui/tab_piemenu.py)
    _pm_tab = tab_piemenu_ui.build()
    tabs = _pm_tab["tabs"]
    tabToolBar = _pm_tab["tabToolBar"]
    window_icons = _pm_tab["window_icons"]
    grid_layout = _pm_tab["grid_layout"]
    buttonIconPieMenu = _pm_tab["buttonIconPieMenu"]
    cBox = _pm_tab["cBox"]
    buttonExistingToolBar = _pm_tab["buttonExistingToolBar"]
    piemenuBoxGroup = _pm_tab["piemenuBoxGroup"]
    pieMenuTab = _pm_tab["pieMenuTab"]
    checkboxDefaultPie = _pm_tab["checkboxDefaultPie"]
    comboWbForPieMenu = _pm_tab["comboWbForPieMenu"]
    comboShape = _pm_tab["comboShape"]
    spinRadius = _pm_tab["spinRadius"]
    spinButton = _pm_tab["spinButton"]
    spinIconSpacing = _pm_tab["spinIconSpacing"]
    spinNumColumn = _pm_tab["spinNumColumn"]
    spinCommandPerCircle = _pm_tab["spinCommandPerCircle"]
    checkboxDisplayCommandName = _pm_tab["checkboxDisplayCommandName"]
    labeldisplayCommandName = _pm_tab["labeldisplayCommandName"]
    checkboxDisplayPreselect = _pm_tab["checkboxDisplayPreselect"]
    labelDisplayPreselect = _pm_tab["labelDisplayPreselect"]
    radioButtonPress = _pm_tab["radioButtonPress"]
    radioButtonHover = _pm_tab["radioButtonHover"]
    spinHoverDelay = _pm_tab["spinHoverDelay"]
    toolShortcutGroup = _pm_tab["toolShortcutGroup"]
    checkboxDisplayShortcut = _pm_tab["checkboxDisplayShortcut"]
    spinShortcutLabelSize = _pm_tab["spinShortcutLabelSize"]
    shortcutLineEdit = _pm_tab["shortcutLineEdit"]
    labelShortcut = _pm_tab["labelShortcut"]
    infoShortcut = _pm_tab["infoShortcut"]
    layoutInfoShortcut = _pm_tab["layoutInfoShortcut"]
    buttonListWidget = _pm_tab["buttonListWidget"]
    labelShortcutSize = _pm_tab["labelShortcutSize"]
    labelNumColumn = _pm_tab["labelNumColumn"]
    labelIconSpacing = _pm_tab["labelIconSpacing"]
    labelCommandPerCircle = _pm_tab["labelCommandPerCircle"]


    #### Tool list container ####
    searchLayout = QHBoxLayout()
    searchLineEdit = QLineEdit()
    searchLineEdit.setPlaceholderText(translate("ToolsTab", "Search"))
    searchLineEdit.textChanged.connect(searchInToolList)

    clearButton = QtGui.QToolButton()
    clearButton.setToolTip(translate("ToolsTab", "Clear search"))
    clearButton.setMaximumWidth(40)
    clearButton.setIcon(QtGui.QIcon.fromTheme(resources.iconBackspace))
    clearButton.clicked.connect(searchLineEdit.clear)

    searchLayout.addWidget(searchLineEdit)
    searchLayout.addWidget(clearButton)

    toolListWidget = QtGui.QTableWidget()
    toolListWidget.setColumnCount(3)
    toolListWidget.sortItems(1, QtCore.Qt.AscendingOrder)
    toolListWidget.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
    toolListWidget.verticalHeader().setVisible(False)
    toolListWidget.setHorizontalHeaderLabels(
        ["", translate("ToolsTab", "Tools"), translate("ToolsTab", "Workbench")])

    toolListWidget.horizontalHeader().setSectionResizeMode(
        0, QtWidgets.QHeaderView.Fixed)
    toolListWidget.setColumnWidth(0, 10)
    toolListWidget.horizontalHeader().setSectionResizeMode(
        1, QtWidgets.QHeaderView.Stretch)
    toolListWidget.horizontalHeader().setSectionResizeMode(
        2, QtWidgets.QHeaderView.Fixed)
    toolListWidget.setColumnWidth(2, 120)
    toolListWidget.horizontalHeader().setStretchLastSection(False)

    toolListWidget.horizontalHeader().setSortIndicatorShown(True)
    toolListWidget.horizontalHeader().setSortIndicator(1, QtCore.Qt.AscendingOrder)
    toolListWidget.horizontalHeader().setSectionsClickable(True)
    toolListWidget.horizontalHeader().setSectionsMovable(False)

    toolListWidget.horizontalHeader().sectionClicked.connect(sortToolListByColumn)
    toolListWidget.itemChanged.connect(onToolListWidget)

    toolListLayout = QVBoxLayout()
    toolListLayout.addLayout(searchLayout)
    toolListLayout.addWidget(toolListWidget)

    widgetContainer = QWidget()
    widgetContainer.setLayout(toolListLayout)
    widgetContainer.setMinimumHeight(380)

    # Context tab (piemenu/ui/tab_context.py)
    _ctx_tab = tab_context_ui.build()
    contextTab = _ctx_tab["contextTab"]
    addContextConditions = _ctx_tab["addContextConditions"]
    labelListContext = _ctx_tab["labelListContext"]
    listContextConditions = _ctx_tab["listContextConditions"]
    comboContextWorkbench = _ctx_tab["comboContextWorkbench"]
    checkboxTriggerContext = _ctx_tab["checkboxTriggerContext"]

    # ToolBar tab (piemenu/ui/tab_toolbar.py)
    _tb_tab = tab_toolbar_ui.build()
    buttonBackToSettings = _tb_tab["buttonBackToSettings"]
    listToolBar = _tb_tab["listToolBar"]
    toolBarTab = _tb_tab["toolBarTab"]

    #### Tab Global Settings ####
    settingsTab = QtGui.QWidget()
    settingsTabLayout = QtGui.QVBoxLayout()
    settingsTab.setLayout(settingsTabLayout)

    # tabs.addTab(assistantTab, translate("AssistantTab", "Assistant"))
    tabs.addTab(pieMenuTab, translate("PieMenuTab", "PieMenu"))
    tabs.addTab(widgetContainer, translate("ToolsTab", "Tools"))
    tabs.addTab(contextTab, translate("ContextTab", "Context"))
    tabs.addTab(settingsTab, translate("GlobalSettingsTab", "Global settings"))

    tabToolBar.addTab(toolBarTab, translate("ToolBarsTab", "ToolBars"))

    # Assistant panel on the left (piemenu/ui/tab_assistant.py). It is built
    # once every view exists so that it can follow the current one.
    _asst_tab = tab_assistant_ui.build(tabs=tabs, toolbar_view=toolBarTab)
    assistantTab = _asst_tab["assistantTab"]
    assistantPanel = _asst_tab["assistantPanel"]

    # Keep the guidance in sync when the dialog switches to the ToolBars
    # view (the way back is handled by preferences.on_back_to_settings, which
    # calls the assistant through the publish() hook).
    buttonExistingToolBar.clicked.connect(assistantPanel.refresh)

    #### buttons actions list ####
    buttonAddSeparator = QtGui.QToolButton()
    buttonAddSeparator.setIcon(QtGui.QIcon(resources.iconAddSeparator))
    buttonAddSeparator.setToolTip(translate("Commands", "Add separator"))
    buttonAddSeparator.setMinimumHeight(30)
    buttonAddSeparator.setMinimumWidth(30)
    buttonAddSeparator.clicked.connect(onButtonAddSeparator)

    buttonRemoveCommand = QtGui.QToolButton()
    buttonRemoveCommand.setIcon(QtGui.QIcon(resources.iconRemoveCommand))
    buttonRemoveCommand.setToolTip(
        translate("Commands", "Remove selected command"))
    buttonRemoveCommand.setMinimumHeight(30)
    buttonRemoveCommand.setMinimumWidth(30)
    buttonRemoveCommand.clicked.connect(onButtonRemoveCommand)

    buttonUp = QtGui.QToolButton()
    buttonUp.setIcon(QtGui.QIcon(resources.iconUp))
    buttonUp.setToolTip(translate("Commands", "Move selected command up"))
    buttonUp.setMinimumHeight(30)
    buttonUp.setMinimumWidth(30)
    buttonUp.clicked.connect(onButtonUp)

    buttonDown = QtGui.QToolButton()
    buttonDown.setIcon(QtGui.QIcon(resources.iconDown))
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
    buttonListWidget.setHorizontalHeaderLabels(
        [translate("PieMenuTab", "Shortcut"), translate("PieMenuTab", "Action")])
    buttonListWidget.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
    buttonListWidget.verticalHeader().setVisible(False)
    buttonListWidget.horizontalHeaderItem(0).setTextAlignment(
        QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter)
    buttonListWidget.horizontalHeaderItem(1).setTextAlignment(
        QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
    buttonListWidget.horizontalHeader().setSectionResizeMode(
        QtGui.QHeaderView.Interactive)
    buttonListWidget.setColumnWidth(0, 60)
    buttonListWidget.horizontalHeader().setMinimumSectionSize(60)
    buttonListWidget.horizontalHeader().setStretchLastSection(True)

    buttonListWidget.setSelectionMode(
        QtGui.QAbstractItemView.ExtendedSelection)
    pieButtons = QtGui.QWidget()
    pieButtonsLayout = QtGui.QVBoxLayout()
    pieButtons.setLayout(pieButtonsLayout)
    pieButtonsLayout.setContentsMargins(0, 0, 0, 0)
    pieButtonsLayout.addWidget(buttonListWidget)
    pieButtonsLayout.insertLayout(1, buttonsLayout)

    showPreviewWidget = QtGui.QTableWidget()
    showPreviewWidget.setColumnCount(1)
    showPreviewWidget.setHorizontalHeaderLabels(
        [translate("PieMenuTab", "Preview")])
    showPreviewWidget.setHorizontalScrollBarPolicy(
        QtCore.Qt.ScrollBarAlwaysOff)
    showPreviewWidget.verticalHeader().setVisible(False)
    showPreviewWidget.horizontalHeader().setSectionResizeMode(
        QtGui.QHeaderView.Interactive)
    showPreviewWidget.horizontalHeader().setMinimumSectionSize(100)
    showPreviewWidget.horizontalHeader().setStretchLastSection(True)

    showPiemenu = QtGui.QWidget()
    showPiemenuLayout = QtGui.QVBoxLayout()
    showPiemenu.setLayout(showPiemenuLayout)
    showPiemenuLayout.setContentsMargins(0, 0, 0, 0)
    showPiemenuLayout.addWidget(showPreviewWidget)

    #### Main Layout####
    vSplitter = QtGui.QSplitter()
    vSplitter.insertWidget(0, tabs)
    vSplitter.insertWidget(1, toolBarTab)
    vSplitter.insertWidget(2, pieButtons)
    vSplitter.insertWidget(3, showPiemenu)

    # Assistant panel on the left. The horizontal splitter gives the user a
    # draggable handle so the panel can be slid away, and the toggle button
    # in the bottom bar hides/shows it completely.
    assistantSplitter = QtGui.QSplitter()
    assistantSplitter.setOrientation(QtCore.Qt.Horizontal)
    assistantSplitter.addWidget(assistantTab)
    assistantSplitter.addWidget(vSplitter)
    assistantSplitter.setStretchFactor(0, 0)
    assistantSplitter.setStretchFactor(1, 1)
    assistantSplitter.setSizes([260, 900])

    # Toggle button for the assistant panel
    assistant_button = QtGui.QPushButton(
        translate("MainWindow", "Hide assistant"))
    assistant_button.setToolTip(
        translate("MainWindow", "Show/hide the assistant panel on the left"))
    assistant_button.setCheckable(True)
    assistant_button.setChecked(True)

    def toggle_assistant():
        visible = not assistantTab.isVisible()
        assistantTab.setVisible(visible)
        assistant_button.setChecked(visible)
        assistant_button.setText(
            translate("MainWindow", "Hide assistant")
            if visible else
            translate("MainWindow", "Show assistant"))

    assistant_button.clicked.connect(toggle_assistant)

    preferencesWidget = QtGui.QWidget()
    preferencesLayout = QtGui.QVBoxLayout()
    preferencesLayout.setContentsMargins(0, 0, 0, 0)
    preferencesWidget.setLayout(preferencesLayout)
    preferencesLayout.addWidget(piemenuWidget)
    preferencesLayout.addWidget(assistantSplitter)

    info_button = QtGui.QPushButton()
    info_button.setToolTip(translate("MainWindow", "About"))
    info_button.setMaximumWidth(80)
    info_button.setIcon(QtGui.QIcon.fromTheme(resources.iconInfo))
    info_button.clicked.connect(infoPopup)

    doc_button = QtGui.QPushButton(translate("MainWindow", "Documentation"))
    doc_button.setToolTip(translate("MainWindow", "Documentation"))
    doc_button.setIcon(QtGui.QIcon.fromTheme(resources.iconDocumentation))
    doc_button.clicked.connect(documentationLink)

    close_button = QtGui.QPushButton(translate("MainWindow", "Close"))
    close_button.setMaximumWidth(120)

    button_row_layout = QtGui.QHBoxLayout()
    button_row_layout.addWidget(assistant_button)
    button_row_layout.addStretch(1)
    button_row_layout.addWidget(info_button)
    button_row_layout.addStretch(1)
    button_row_layout.addWidget(
        close_button, 0, alignment=QtCore.Qt.AlignCenter)
    button_row_layout.addStretch(1)

    button_row_layout.addWidget(doc_button, 0, alignment=QtCore.Qt.AlignRight)

    button_layout = QtGui.QVBoxLayout()
    button_layout.addLayout(layoutInfoShortcut)
    button_layout.addLayout(button_row_layout)

    # The dialog class (piemenu/ui/preferences.py) reads its title from the
    # module-level version constant, so publish it before the dialog is built.
    preferences_ui.publish(
        pie_menu_version=PIE_MENU_VERSION,
        get_group=preferences_ui.get_group,
    )

    global pieMenuDialog
    pieMenuDialog = PieMenuDialog()
    state.app_state.pie_menu_dialog = pieMenuDialog
    pieMenuDialog.resize(preferencesWidget.sizeHint().width() + 100,
                         preferencesWidget.sizeHint().height())

    pieMenuDialogLayout = QtGui.QVBoxLayout()
    pieMenuDialog.setLayout(pieMenuDialogLayout)
    pieMenuDialogLayout.addWidget(preferencesWidget)
    pieMenuDialogLayout.addLayout(button_layout)

    close_button.clicked.connect(pieMenuDialog.close)

    # Global settings (piemenu/ui/tab_settings.py)
    _gs = tab_settings_ui.build(settingsTabLayout=settingsTabLayout)
    comboBoxTheme = _gs["comboBoxTheme"]
    checkboxQuickMenu = _gs["checkboxQuickMenu"]
    checkboxGlobalKeyToggle = _gs["checkboxGlobalKeyToggle"]
    checkboxRightClick = _gs["checkboxRightClick"]
    spinDelayRightClick = _gs["spinDelayRightClick"]
    checkboxDisplaySpinBox = _gs["checkboxDisplaySpinBox"]
    labelGlobalShortcut = _gs["labelGlobalShortcut"]
    globalShortcutLineEdit = _gs["globalShortcutLineEdit"]

    bootstrap_ui.publish(**locals(), pieMenuDialog=pieMenuDialog, PIE_MENU_VERSION=PIE_MENU_VERSION)
    bootstrap_ui.bootstrap()


pieMenuStart()
