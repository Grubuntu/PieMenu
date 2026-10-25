"""Context tab builder for the preferences dialog.

build() constructs all the widgets of the Context tab.
"""

import FreeCAD as App
import FreeCADGui as Gui
from PySide import QtCore, QtGui, QtWidgets
from PySide.QtWidgets import QCheckBox, QGroupBox, QHBoxLayout, QLabel, QTableWidget, QVBoxLayout, QWidget

from piemenu import config, resources
from piemenu.ui import context as context_ui
from piemenu.ui import options as options_ui
from piemenu.ui import settings as settings_ui
from piemenu.ui import preferences as preferences_ui


def translate(context, text):
    return App.Qt.translate(context, text)


def build():

    #### Tab ContextTab ####
    contextTab = QtGui.QWidget()
    contextTabLayout = QtGui.QVBoxLayout()
    contextTab.setLayout(contextTabLayout)

    vertexItem = QtGui.QTableWidgetItem()
    vertexItem.setText(translate("ContextTab", "Vertex"))
    vertexItem.setToolTip(
        translate("ContextTab", "A vertex can be a point on a 2D or 3D object, a projected point, a point of origin, DatumPoint etc."))
    vertexItem.setFlags(QtCore.Qt.ItemIsEnabled)

    edgeItem = QtGui.QTableWidgetItem()
    edgeItem.setText(translate("ContextTab", "Edge"))
    edgeItem.setToolTip(
        translate("ContextTab", "An edge can be an line, circle, etc. spline on a 2D or 3D object."))
    edgeItem.setFlags(QtCore.Qt.ItemIsEnabled)

    faceItem = QtGui.QTableWidgetItem()
    faceItem.setText(translate("ContextTab", "Face"))
    faceItem.setToolTip(
        translate("ContextTab", "A face can be a face, a curve etc. of a 2D or 3D object."))
    faceItem.setFlags(QtCore.Qt.ItemIsEnabled)

    objectItem = QtGui.QTableWidgetItem()
    objectItem.setText(translate("ContextTab", "Object"))
    objectItem.setToolTip(
        translate("ContextTab", "An object can be any element contained in the construction tree: body, part, feature, etc."))
    objectItem.setFlags(QtCore.Qt.ItemIsEnabled)

    axisItem = QtGui.QTableWidgetItem()
    axisItem.setText(translate("ContextTab", "Axis"))
    axisItem.setToolTip(
        translate("ContextTab", "An axis can be X, Y, Z axis, H or V axis in Sketcher or DatumLine"))
    axisItem.setFlags(QtCore.Qt.ItemIsEnabled)

    planeItem = QtGui.QTableWidgetItem()
    planeItem.setText(translate("ContextTab", "Plane"))
    planeItem.setToolTip(
        translate("ContextTab", "An plane can be XY, XZ or YZ plane or DatumPlane"))
    planeItem.setFlags(QtCore.Qt.ItemIsEnabled)

    vertexComboBox = context_ui.combo_box("VertexSign")
    edgeComboBox = context_ui.combo_box("EdgeSign")
    faceComboBox = context_ui.combo_box("FaceSign")
    objectComboBox = context_ui.combo_box("ObjectSign")
    axisComboBox = context_ui.combo_box("AxisSign")
    planeComboBox = context_ui.combo_box("PlaneSign")

    vertexSpin = context_ui.spin_box("VertexValue")
    edgeSpin = context_ui.spin_box("EdgeValue")
    faceSpin = context_ui.spin_box("FaceValue")
    objectSpin = context_ui.spin_box("ObjectValue")
    axisSpin = context_ui.spin_box("AxisValue")
    planeSpin = context_ui.spin_box("PlaneValue")

    # The context-tab comparison widgets must be published before
    # setContextConditions() runs at the end of pieMenuStart(); the
    # remaining context references are published later.
    context_ui.publish(
        axis_combo_box=axisComboBox,
        axis_spin=axisSpin,
        edge_combo_box=edgeComboBox,
        edge_spin=edgeSpin,
        face_combo_box=faceComboBox,
        face_spin=faceSpin,
        object_combo_box=objectComboBox,
        object_spin=objectSpin,
        plane_combo_box=planeComboBox,
        plane_spin=planeSpin,
        vertex_combo_box=vertexComboBox,
        vertex_spin=vertexSpin,
    )

    labelContextTable = QLabel(
        translate("ContextTab", "Modify or add context selection conditions:"))

    contextTable = QtGui.QTableWidget(6, 3)
    # contextTable.setMaximumHeight(160)
    # contextTable.setFrameStyle(QtGui.QFrame.NoFrame)
    contextTable.verticalHeader().setVisible(False)
    contextTable.horizontalHeader().setVisible(False)

    try:
        contextTable.horizontalHeader().setSectionResizeMode(QtGui.QHeaderView.Stretch)
        # contextTable.verticalHeader().setResizeMode(QtGui.QHeaderView.Stretch)
    except AttributeError:

        contextTable.horizontalHeader().setSectionResizeMode(QtGui.QHeaderView.Stretch)
        # contextTable.verticalHeader().setSectionResizeMode(QtGui.QHeaderView.Stretch)


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

    contextTable.setItem(4, 0, axisItem)
    contextTable.setCellWidget(4, 1, axisComboBox)
    contextTable.setCellWidget(4, 2, axisSpin)

    contextTable.setItem(5, 0, planeItem)
    contextTable.setCellWidget(5, 1, planeComboBox)
    contextTable.setCellWidget(5, 2, planeSpin)

    resetContextButton = QtGui.QToolButton()
    resetContextButton.setIcon(QtGui.QIcon(resources.iconReset))
    resetContextButton.setToolTip(translate("ContextTab", "Reset to defaults"))
    resetContextButton.setMinimumHeight(30)
    resetContextButton.setMinimumWidth(30)
    resetContextButton.clicked.connect(context_ui.on_reset_context_table)

    addContextConditions = QtGui.QToolButton()
    addContextConditions.setIcon(QtGui.QIcon(resources.iconAdd))
    addContextConditions.setToolTip(translate("ContextTab", "Add a new rule"))
    addContextConditions.setMinimumHeight(30)
    addContextConditions.setMinimumWidth(30)
    addContextConditions.clicked.connect(context_ui.on_add_context_conditions)

    resetLayout = QtGui.QHBoxLayout()
    resetLayout.addStretch(1)
    resetLayout.addWidget(addContextConditions)
    resetLayout.addWidget(resetContextButton)

    checkboxTriggerContext = QCheckBox()
    checkboxTriggerContext.setCheckable(True)
    checkboxTriggerContext.stateChanged.connect(
        lambda state: options_ui.on_trigger_context(state))

    labelTriggerContext = QtGui.QLabel(
        translate("ContextTab", "Immediate triggering when conditions are met"))
    labelTriggerContext.setToolTip(translate(
        "ContextTab", "The PieMenu will open immediately once the contextual selection conditions are met."))
    labelTriggerContext.setAlignment(
        QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)

    triggerContextLayout = QtGui.QHBoxLayout()
    triggerContextLayout.addWidget(checkboxTriggerContext)
    triggerContextLayout.addWidget(labelTriggerContext)
    triggerContextLayout.addStretch(1)

    settingContextGroup = QGroupBox(translate("GlobalSettingsTab", "Context"))

    labelContextWorkbench = QtGui.QLabel(translate(
        "ContextTab", "Set workbench for these contextual selection conditions"))

    comboContextWorkbench = QtGui.QComboBox()
    comboContextWorkbench.setMinimumWidth(160)
    comboContextWorkbench.currentIndexChanged.connect(settings_ui.set_context_workbench)

    contextWorkbenchLayout = QtGui.QHBoxLayout()
    contextWorkbenchLayout.addWidget(labelContextWorkbench)
    contextWorkbenchLayout.addStretch(1)
    contextWorkbenchLayout.addWidget(comboContextWorkbench)

    listContextConditions = QtGui.QTableWidget()
    listContextConditions.setColumnCount(3)
    listContextConditions.verticalHeader().setVisible(False)
    listContextConditions.setFrameStyle(QtGui.QFrame.NoFrame)
    listContextConditions.itemSelectionChanged.connect(context_ui.on_row_selected)

    listContextConditions.setColumnWidth(0, 70)
    listContextConditions.setColumnWidth(1, 290)
    listContextConditions.setColumnWidth(2, 15)

    listContextConditions.horizontalHeader().setSectionResizeMode(
        0, QtGui.QHeaderView.ResizeToContents)
    listContextConditions.horizontalHeader().setSectionResizeMode(1,
                                                                   QtGui.QHeaderView.Stretch)
    listContextConditions.horizontalHeader().setSectionResizeMode(2,
                                                                   QtGui.QHeaderView.Fixed)

    listContextConditions.horizontalHeader().setSectionsClickable(True)
    listContextConditions.horizontalHeader().setSectionsMovable(False)
    listContextConditions.horizontalHeader().setVisible(False)

    listContextConditions.setSizePolicy(
        QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Maximum)
    listContextConditions.setMaximumHeight(140)

    labelListContext = QLabel()

    layoutLabelContext = QtGui.QHBoxLayout()
    layoutLabelContext.addWidget(labelListContext)
    layoutLabelContext.addStretch(1)

    layoutAddContextConditions = QtGui.QVBoxLayout()
    layoutAddContextConditions.addLayout(layoutLabelContext)
    layoutAddContextConditions.addWidget(listContextConditions)

    settingContextGroup.setLayout(QtGui.QVBoxLayout())
    settingContextGroup.layout().addLayout(contextWorkbenchLayout)
    settingContextGroup.layout().addLayout(layoutAddContextConditions)
    settingContextGroup.layout().addWidget(labelContextTable)
    settingContextGroup.layout().addWidget(contextTable)
    settingContextGroup.layout().addLayout(resetLayout)
    settingContextGroup.layout().addLayout(triggerContextLayout)

    contextTabLayout.insertWidget(0, settingContextGroup)
    contextTabLayout.addStretch(1)

    return {
        'contextTab': contextTab,
        'addContextConditions': addContextConditions,
        'labelListContext': labelListContext,
        'listContextConditions': listContextConditions,
        'comboContextWorkbench': comboContextWorkbench,
        'checkboxTriggerContext': checkboxTriggerContext,
    }
