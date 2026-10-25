"""PieMenu tab builder for the preferences dialog.

build() constructs all the widgets of the PieMenu tab.
"""

import FreeCAD as App
import FreeCADGui as Gui
from PySide import QtCore, QtGui, QtWidgets
from PySide.QtCore import QSize, Qt
from PySide.QtWidgets import QCheckBox, QGroupBox, QHBoxLayout, QLabel, QScrollArea, QVBoxLayout, QWidget

from piemenu import config, constants, resources, shortcuts, state
from piemenu.ui import icons as icons_ui
from piemenu.ui import menus as menus_ui
from piemenu.ui import misc as misc_ui
from piemenu.ui import options as options_ui
from piemenu.ui import preferences as preferences_ui
from piemenu.ui import settings as settings_ui
from piemenu.ui import toolbar as toolbar_ui
from piemenu.widgets import CustomLineEdit, HoverButton, PreselectButton


def translate(context, text):
    return App.Qt.translate(context, text)


def build():

    tabs = QtGui.QTabWidget()
    tabToolBar = QtGui.QTabWidget()

    ### Button set Icon ####
    window_icons = QtGui.QWidget()

    grid_layout = QtGui.QGridLayout()
    grid_widget = QtGui.QWidget()
    grid_widget.setLayout(grid_layout)
    scroll_area = QtGui.QScrollArea()
    scroll_area.setWidgetResizable(True)
    scroll_area.setWidget(grid_widget)

    buttonBrowse = QtGui.QPushButton(
        translate("PieMenuTab", "Browse Icons Files..."))
    buttonBrowse.clicked.connect(icons_ui.on_button_browse_icon)

    cancel_window_icons_button = QtGui.QPushButton(
        translate("PieMenuTab", "Cancel"))
    cancel_window_icons_button.clicked.connect(icons_ui.window_icons_close)

    buttonLayoutIcons = QtGui.QHBoxLayout()
    buttonLayoutIcons.addWidget(buttonBrowse)
    buttonLayoutIcons.addStretch(1)
    buttonLayoutIcons.addWidget(cancel_window_icons_button)

    main_layout = QtGui.QVBoxLayout()
    main_layout.addWidget(scroll_area)
    main_layout.addLayout(buttonLayoutIcons)

    window_icons.setLayout(main_layout)

    buttonIconPieMenu = QtGui.QToolButton()
    buttonIconPieMenu.setToolTip(
        translate("PieMenuTab", "Set icon to current PieMenu"))
    buttonIconPieMenu.setMinimumHeight(30)
    buttonIconPieMenu.setMinimumWidth(30)
    buttonIconPieMenu.clicked.connect(icons_ui.on_button_icon_pie_menu)

    #### layout PieMenu Settings ####
    cBox = QtGui.QComboBox()
    cBox.setMinimumHeight(28)
    cBox.currentIndexChanged.connect(preferences_ui.on_pie_change)
    cBox.setMinimumWidth(140)

    buttonAddPieMenu = QtGui.QToolButton()
    buttonAddPieMenu.setIcon(QtGui.QIcon(resources.iconAdd))
    buttonAddPieMenu.setToolTip(translate("PieMenuTab", "Add new pie menu"))
    buttonAddPieMenu.setMinimumHeight(30)
    buttonAddPieMenu.setMinimumWidth(30)
    buttonAddPieMenu.clicked.connect(menus_ui.on_button_add_pie_menu)

    buttonRemovePieMenu = QtGui.QToolButton()
    buttonRemovePieMenu.setIcon(QtGui.QIcon(resources.iconRemove))
    buttonRemovePieMenu.setToolTip(
        translate("PieMenuTab", "Remove current pie menu"))
    buttonRemovePieMenu.setMinimumHeight(30)
    buttonRemovePieMenu.setMinimumWidth(30)
    buttonRemovePieMenu.clicked.connect(menus_ui.on_button_remove_pie_menu)

    buttonRenamePieMenu = QtGui.QToolButton()
    buttonRenamePieMenu.setToolTip(
        translate("PieMenuTab", "Rename current pie menu"))
    buttonRenamePieMenu.setIcon(QtGui.QIcon(resources.iconRename))
    buttonRenamePieMenu.setMinimumHeight(30)
    buttonRenamePieMenu.setMinimumWidth(30)
    buttonRenamePieMenu.clicked.connect(menus_ui.on_button_rename_pie_menu)

    buttonCopyPieMenu = QtGui.QToolButton()
    buttonCopyPieMenu.setToolTip(
        translate("PieMenuTab", "Copy current pie menu"))
    buttonCopyPieMenu.setIcon(QtGui.QIcon(resources.iconCopy))
    buttonCopyPieMenu.setMinimumHeight(30)
    buttonCopyPieMenu.setMinimumWidth(30)
    buttonCopyPieMenu.clicked.connect(menus_ui.on_button_copy_pie_menu)

    buttonExistingToolBar = QtGui.QPushButton(
        translate("PieMenuTab", "Workbenches toolbars..."))
    buttonExistingToolBar.setToolTip(
        translate("PieMenuTab", "Add one of the existing workbenches toolbars"))
    buttonExistingToolBar.setIcon(QtGui.QIcon(resources.iconRight))
    buttonExistingToolBar.setMinimumHeight(30)
    buttonExistingToolBar.setMinimumWidth(60)
    buttonExistingToolBar.clicked.connect(toolbar_ui.on_button_tool_bar)

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
    checkboxDefaultPie.stateChanged.connect(lambda state: preferences_ui.on_default_pie(state))

    labelDefaultPie = QtGui.QLabel(
        translate("GlobalSettingsTab", "Set this PieMenu as default"))
    labelDefaultPie.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)

    layoutDefaultPieLeft = QtGui.QHBoxLayout()
    layoutDefaultPieLeft.addWidget(checkboxDefaultPie)
    layoutDefaultPieLeft.addWidget(labelDefaultPie)
    layoutDefaultPieLeft.addStretch(1)
    layoutDefaultPie = QtGui.QHBoxLayout()
    layoutDefaultPie.addLayout(layoutDefaultPieLeft, 1)

    labelWbForPieMenu = QtGui.QLabel(
        translate("PieMenuTab", "Workbench associated to this PieMenu:"))
    labelWbForPieMenu.setAlignment(
        QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)

    comboWbForPieMenu = QtGui.QComboBox()
    comboWbForPieMenu.setMinimumWidth(160)
    comboWbForPieMenu.currentIndexChanged.connect(settings_ui.on_wb_for_pie_menu)

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
    comboShape.currentIndexChanged.connect(settings_ui.set_shape)

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
    spinRadius.valueChanged.connect(settings_ui.on_spin_radius)

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
    spinButton.valueChanged.connect(settings_ui.on_spin_button)

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
    spinIconSpacing.valueChanged.connect(settings_ui.on_icon_spacing)

    layoutIconSpacingLeft = QtGui.QHBoxLayout()
    layoutIconSpacingLeft.addWidget(labelIconSpacing)
    layoutIconSpacingRight = QtGui.QHBoxLayout()
    layoutIconSpacingRight.addWidget(spinIconSpacing)
    layoutIconSpacing = QtGui.QHBoxLayout()
    layoutIconSpacing.addLayout(layoutIconSpacingLeft, 1)
    layoutIconSpacing.addLayout(layoutIconSpacingRight, 1)

    labelNumColumn = QtGui.QLabel(
        translate("PieMenuTab", "Number of columns:"))
    labelNumColumn.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)

    spinNumColumn = QtGui.QSpinBox()
    spinNumColumn.setMaximum(12)
    spinNumColumn.setMinimumWidth(120)
    spinNumColumn.valueChanged.connect(settings_ui.on_num_column)

    layoutColumnLeft = QtGui.QHBoxLayout()
    layoutColumnLeft.addWidget(labelNumColumn)
    layoutColumnRight = QtGui.QHBoxLayout()
    layoutColumnRight.addWidget(spinNumColumn)
    layoutColumn = QtGui.QHBoxLayout()
    layoutColumn.addLayout(layoutColumnLeft, 1)
    layoutColumn.addLayout(layoutColumnRight, 1)

    labelCommandPerCircle = QtGui.QLabel(
        translate("PieMenuTab", "Command for first circle:"))
    labelCommandPerCircle.setAlignment(
        QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)

    spinCommandPerCircle = QtGui.QSpinBox()
    spinCommandPerCircle.setMaximum(20)
    spinCommandPerCircle.setMinimum(2)
    spinCommandPerCircle.setMinimumWidth(0)
    spinCommandPerCircle.valueChanged.connect(settings_ui.on_command_per_circle)

    layoutCommandPerCircleLeft = QtGui.QHBoxLayout()
    layoutCommandPerCircleLeft.addWidget(labelCommandPerCircle)
    layoutCommandPerCircleRight = QtGui.QHBoxLayout()
    layoutCommandPerCircleRight.addWidget(spinCommandPerCircle)
    layoutCommandPerCircle = QtGui.QHBoxLayout()
    layoutCommandPerCircle.addLayout(layoutCommandPerCircleLeft, 1)
    layoutCommandPerCircle.addLayout(layoutCommandPerCircleRight, 1)

    checkboxDisplayCommandName = QCheckBox()
    checkboxDisplayCommandName.setCheckable(True)
    checkboxDisplayCommandName.stateChanged.connect(
        lambda state: options_ui.on_display_command_name(state))

    labeldisplayCommandName = QtGui.QLabel(
        translate("PieMenuTab", "Show command names"))
    labeldisplayCommandName.setAlignment(
        QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)

    layoutDisplayCommandNameLeft = QtGui.QHBoxLayout()
    layoutDisplayCommandNameLeft.addWidget(checkboxDisplayCommandName)
    layoutDisplayCommandNameLeft.addWidget(labeldisplayCommandName)
    layoutDisplayCommandNameLeft.addStretch(1)
    layoutDisplayCommandName = QtGui.QHBoxLayout()
    layoutDisplayCommandName.addLayout(layoutDisplayCommandNameLeft, 1)

    checkboxDisplayPreselect = QCheckBox()
    checkboxDisplayPreselect.setCheckable(True)
    checkboxDisplayPreselect.stateChanged.connect(
        lambda state: options_ui.on_display_preselect(state))

    labelDisplayPreselect = QtGui.QLabel(
        translate("PieMenuTab", "Show preselect button"))
    labelDisplayPreselect.setAlignment(
        QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)

    layoutDisplayPreselectLeft = QtGui.QHBoxLayout()
    layoutDisplayPreselectLeft.addWidget(checkboxDisplayPreselect)
    layoutDisplayPreselectLeft.addWidget(labelDisplayPreselect)
    layoutDisplayPreselectLeft.addStretch(1)
    layoutDisplayPreselect = QtGui.QHBoxLayout()
    layoutDisplayPreselect.addLayout(layoutDisplayPreselectLeft, 1)

    shapeGroup = QGroupBox(translate("PieMenuTab", constants.PARAM_SHAPE))
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
    radioButtonPress = QtGui.QRadioButton(
        translate("GlobalSettingsTab", "Press"))
    radioButtonPress.toggled.connect(
        lambda checked, data="Press": options_ui.set_trigger_mode(data))

    radioButtonHover = QtGui.QRadioButton(
        translate("GlobalSettingsTab", "Hover"))
    radioButtonHover.toggled.connect(
        lambda checked, data="Hover":  options_ui.set_trigger_mode(data))

    radioGroup = QtGui.QButtonGroup()
    radioGroup.addButton(radioButtonPress)
    radioGroup.addButton(radioButtonHover)

    layoutActionHoverButton = QtGui.QVBoxLayout()
    layoutActionHoverButton.addWidget(radioButtonPress)
    layoutActionHoverButton.addWidget(radioButtonHover)

    labelHoverDelay = QtGui.QLabel(
        translate("GlobalSettingsTab", "Hover delay (ms):"))
    labelHoverDelay.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)

    spinHoverDelay = QtGui.QSpinBox()
    spinHoverDelay.setMaximum(999)
    spinHoverDelay.setMinimumWidth(90)
    spinHoverDelay.valueChanged.connect(settings_ui.on_spin_hover_delay)

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
    toolShortcutGroup.toggled.connect(lambda state: options_ui.on_enable_shortcut(state))

    checkboxDisplayShortcut = QCheckBox()
    checkboxDisplayShortcut.setCheckable(True)
    checkboxDisplayShortcut.stateChanged.connect(
        lambda state: options_ui.on_display_shortcut(state))

    labelDisplayShortcut = QtGui.QLabel(
        translate("PieMenuTab", "Display tools shortcut"))
    labelDisplayShortcut.setAlignment(
        QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)

    labelShortcutSize = QtGui.QLabel(translate("PieMenuTab", "Font size:"))
    labelShortcutSize.setAlignment(
        QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)

    spinShortcutLabelSize = QtGui.QSpinBox()
    spinShortcutLabelSize.setMinimum(6)
    spinShortcutLabelSize.setMaximum(50)
    spinShortcutLabelSize.setMinimumWidth(90)
    spinShortcutLabelSize.valueChanged.connect(settings_ui.on_spin_shortcut_label_size)

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

    enableShortcut = config.get_parameter_group(
        cBox.currentText(), "Bool", constants.PARAM_ENABLE_SHORTCUT)
    if enableShortcut == "":
        enableShortcut = False

    # keep this line here
    buttonListWidget = QtGui.QTableWidget()

    # `toolShortcutGroup.setChecked()` below emits `toggled` during the build, so
    # the references used by the option handlers must be published before that.
    options_ui.publish(
        button_list_widget=buttonListWidget,
        c_box=cBox,
        checkbox_display_shortcut=checkboxDisplayShortcut,
        spin_shortcut_label_size=spinShortcutLabelSize,
        update_piemenu_preview=preferences_ui.update_piemenu_preview,
    )

    toolShortcutGroup.setTitle(translate("PieMenuTab", "Tools shortcuts"))
    toolShortcutGroup.setCheckable(True)
    toolShortcutGroup.setChecked(enableShortcut)
    toolShortcutGroup.setLayout(QtGui.QVBoxLayout())
    toolShortcutGroup.layout().addLayout(layoutDisplayShortcut)

    #### group Individual Shortcut ####
    shortcutKey = config.get_parameter_group(
        cBox.currentText(), "String", constants.PARAM_SHORTCUT_KEY)

    labelShortcut = QLabel()
    labelShortcut.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
    labelShortcut.setText(
        translate("PieMenuTab", "Current shortcut: ") + shortcutKey)

    shortcutLineEdit = CustomLineEdit()
    shortcutLineEdit.shortcutChanged.connect(
        lambda text: misc_ui.compare_and_display_warning(shortcuts.get_assigned_shortcut(), text))
    shortcutLineEdit.setText(shortcutKey)

    assignShortcutButton = QtGui.QPushButton(
        translate("GlobalSettingsTab", "Assign"))
    assignShortcutButton.clicked.connect(
        lambda: misc_ui.update_shortcut_key(shortcutLineEdit.text()))

    deleteShortcutButton = QtGui.QPushButton()
    deleteShortcutButton.setMaximumWidth(40)
    deleteShortcutButton.setIcon(QtGui.QIcon.fromTheme(resources.iconBackspace))
    deleteShortcutButton.clicked.connect(lambda: misc_ui.update_shortcut_key(""))

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


    return {
        'tabs': tabs,
        'tabToolBar': tabToolBar,
        'window_icons': window_icons,
        'grid_layout': grid_layout,
        'buttonIconPieMenu': buttonIconPieMenu,
        'cBox': cBox,
        'buttonExistingToolBar': buttonExistingToolBar,
        'piemenuBoxGroup': piemenuBoxGroup,
        'pieMenuTab': pieMenuTab,
        'checkboxDefaultPie': checkboxDefaultPie,
        'comboWbForPieMenu': comboWbForPieMenu,
        'comboShape': comboShape,
        'spinRadius': spinRadius,
        'spinButton': spinButton,
        'spinIconSpacing': spinIconSpacing,
        'spinNumColumn': spinNumColumn,
        'spinCommandPerCircle': spinCommandPerCircle,
        'checkboxDisplayCommandName': checkboxDisplayCommandName,
        'labeldisplayCommandName': labeldisplayCommandName,
        'checkboxDisplayPreselect': checkboxDisplayPreselect,
        'labelDisplayPreselect': labelDisplayPreselect,
        'radioButtonPress': radioButtonPress,
        'radioButtonHover': radioButtonHover,
        'spinHoverDelay': spinHoverDelay,
        'toolShortcutGroup': toolShortcutGroup,
        'checkboxDisplayShortcut': checkboxDisplayShortcut,
        'spinShortcutLabelSize': spinShortcutLabelSize,
        'shortcutLineEdit': shortcutLineEdit,
        'labelShortcut': labelShortcut,
        'infoShortcut': infoShortcut,
        'layoutInfoShortcut': layoutInfoShortcut,
        'buttonListWidget': buttonListWidget,
        'labelShortcutSize': labelShortcutSize,
        'labelNumColumn': labelNumColumn,
        'labelIconSpacing': labelIconSpacing,
        'labelCommandPerCircle': labelCommandPerCircle,
        'labelDisplayPreselect': labelDisplayPreselect,
    }
