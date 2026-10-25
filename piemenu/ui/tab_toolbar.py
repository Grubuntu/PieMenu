"""ToolBar tab builder for the preferences dialog.

build() constructs all the widgets of the ToolBar tab.
"""

import FreeCAD as App
import FreeCADGui as Gui
from PySide import QtCore, QtGui, QtWidgets
from PySide.QtCore import QSize, Qt
from PySide.QtWidgets import QGroupBox, QHBoxLayout, QLabel, QListWidget, QPushButton, QToolButton, QVBoxLayout, QWidget

from piemenu import resources
from piemenu.ui import preferences as preferences_ui
from piemenu.ui import toolbar as toolbar_ui


def translate(context, text):
    return App.Qt.translate(context, text)


def build():

    #### Tab ToolBar ####
    buttonBackToSettings = QtGui.QPushButton(
        translate("ToolBarTab", "Return to settings..."))
    buttonBackToSettings.setToolTip(
        translate("ToolBarTab", "Return to general settings"))
    buttonBackToSettings.setIcon(QtGui.QIcon(resources.iconLeft))
    buttonBackToSettings.setMinimumHeight(30)
    buttonBackToSettings.setMinimumWidth(60)
    buttonBackToSettings.clicked.connect(preferences_ui.on_back_to_settings)
    buttonBackToSettings.setVisible(False)

    listToolBar = QtGui.QListWidget()
    listToolBar.setSortingEnabled(True)
    listToolBar.sortItems(QtCore.Qt.AscendingOrder)
    listToolBar.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
    listToolBar.setMinimumSize(QSize(385, 460))
    listToolBar.itemSelectionChanged.connect(toolbar_ui.show_list_tool_bar)

    listToolBarLayout = QtGui.QVBoxLayout()
    listToolBarLayout.addWidget(listToolBar)
    labelAddToolBar = QLabel(
        translate("ToolBarTab", "Add the selected toolbar as a new PieMenu"))

    buttonAddToolBar = QtGui.QToolButton()
    buttonAddToolBar.setToolTip(
        translate("ToolBarTab", "Add selected ToolBar as PieMenu"))
    buttonAddToolBar.setIcon(QtGui.QIcon(resources.iconAdd))
    buttonAddToolBar.setMinimumHeight(30)
    buttonAddToolBar.setMinimumWidth(30)
    buttonAddToolBar.clicked.connect(toolbar_ui.on_add_tool_bar)

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



    return {
        'buttonBackToSettings': buttonBackToSettings,
        'listToolBar': listToolBar,
        'toolBarTab': toolBarTab,
    }


