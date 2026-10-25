"""Global settings tab builder for the preferences dialog.

build() constructs all the widgets of the Global settings tab.
"""

import FreeCAD as App
import FreeCADGui as Gui
from PySide import QtCore, QtGui, QtWidgets
from PySide.QtCore import QSize, Qt
from PySide.QtWidgets import QCheckBox, QGroupBox, QHBoxLayout, QLabel, QPushButton, QSpinBox, QVBoxLayout, QWidget

from piemenu import config, constants, parameters, resources, shortcuts, state
from piemenu.ui import misc as misc_ui
from piemenu.ui import options as options_ui
from piemenu.ui import preferences as preferences_ui
from piemenu.ui import settings as settings_ui
from piemenu.widgets import CustomLineEdit, HoverButton, PreselectButton


def translate(context, text):
    return App.Qt.translate(context, text)


def build(settingsTabLayout=None):
    if settingsTabLayout is None:
        settingsTabLayout = QtGui.QVBoxLayout()

    #### Global Settings ####
    labelTheme = QLabel(translate("GlobalSettingsTab", "Theme style:"))
    labelTheme.setMinimumWidth(160)
    labelTheme.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)

    comboBoxTheme = QtGui.QComboBox()
    comboBoxTheme.setMinimumWidth(120)
    comboBoxTheme.currentIndexChanged.connect(settings_ui.set_theme)

    # `preferences_ui.get_theme()` runs at build time just below and fills this combobox, so it
    # must be published before the call.
    preferences_ui.publish(combo_box_theme=comboBoxTheme)

    preferences_ui.get_theme()

    layoutThemeLeft = QtGui.QHBoxLayout()
    layoutThemeLeft.addWidget(labelTheme)
    layoutThemeRight = QtGui.QHBoxLayout()
    layoutThemeRight.addWidget(comboBoxTheme)
    layoutTheme = QtGui.QHBoxLayout()
    layoutTheme.addLayout(layoutThemeLeft, 1)
    layoutTheme.addLayout(layoutThemeRight, 1)

    checkboxQuickMenu = QCheckBox()
    checkboxQuickMenu.setCheckable(True)
    checkboxQuickMenu.setChecked(config.get_params()["main"].GetBool(constants.PARAM_SHOW_QUICK_MENU))

    checkboxQuickMenu.stateChanged.connect(
        lambda state: options_ui.on_show_quick_menu(state))

    labelShowQuickMenu = QLabel(
        translate("GlobalSettingsTab", "Show QuickMenu"))
    labelShowQuickMenu.setAlignment(
        QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)

    layoutShowQuickMenuLeft = QtGui.QHBoxLayout()
    layoutShowQuickMenuLeft.addWidget(checkboxQuickMenu)
    layoutShowQuickMenuLeft.addWidget(labelShowQuickMenu)
    layoutShowQuickMenuLeft.addStretch(1)
    layoutShowQuickMenu = QtGui.QHBoxLayout()
    layoutShowQuickMenu.addLayout(layoutShowQuickMenuLeft, 1)

    checkboxGlobalContext = QCheckBox()
    checkboxGlobalContext.setCheckable(True)
    enableContext = config.get_params()["main"].GetBool(constants.PARAM_ENABLE_CONTEXT)
    checkboxGlobalContext.setChecked(enableContext)
    checkboxGlobalContext.stateChanged.connect(lambda state: preferences_ui.on_context(state))

    labelGlobalContext = QLabel(
        translate("GlobalSettingsTab", "Global context"))
    labelGlobalContext.setAlignment(
        QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)

    layoutGlobalContextLeft = QtGui.QHBoxLayout()
    layoutGlobalContextLeft.addWidget(checkboxGlobalContext)
    layoutGlobalContextLeft.addWidget(labelGlobalContext)
    layoutGlobalContextLeft.addStretch(1)
    layoutGlobalContext = QtGui.QHBoxLayout()
    layoutGlobalContext.addLayout(layoutGlobalContextLeft, 1)

    checkboxGlobalKeyToggle = QCheckBox()
    checkboxGlobalKeyToggle.setCheckable(True)

    checkboxGlobalKeyToggle.setChecked(
        config.get_parameter_global("Bool", constants.PARAM_GLOBAL_KEY_TOGGLE))
    checkboxGlobalKeyToggle.stateChanged.connect(settings_ui.set_global_key_toggle)

    labelGlobalKeyToggle = QLabel(
        translate("GlobalSettingsTab", "Shortcuts behavior: Toggle show/hide PieMenu"))
    labelGlobalKeyToggle.setAlignment(
        QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
    layoutGlobalToggle = QtGui.QHBoxLayout()
    layoutGlobalToggle.addWidget(checkboxGlobalKeyToggle)
    layoutGlobalToggle.addWidget(labelGlobalKeyToggle)
    layoutGlobalToggle.addStretch(1)

    checkboxRightClick = QCheckBox()
    checkboxRightClick.setCheckable(True)

    checkboxRightClick.setChecked(
        config.get_parameter_global("Bool", constants.PARAM_RIGHT_CLICK_TRIGGER))
    checkboxRightClick.stateChanged.connect(
        lambda state: options_ui.on_right_click_trigger(state))

    labelDelayRightClick = QLabel(
        translate("GlobalSettingsTab", "Delay (ms):"))

    spinDelayRightClick = QtGui.QSpinBox()
    spinDelayRightClick.setMaximum(1000)
    spinDelayRightClick.setMinimum(50)
    spinDelayRightClick.setValue(config.get_parameter_global("Int", constants.PARAM_DELAY_RIGHT_CLICK))
    spinDelayRightClick.valueChanged.connect(settings_ui.on_spin_delay_right_click)

    labelRightClick = QLabel(
        translate("GlobalSettingsTab", "Long right-click to open default PieMenu"))
    labelRightClick.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
    layoutRightClick = QtGui.QHBoxLayout()
    layoutRightClick.addWidget(checkboxRightClick)
    layoutRightClick.addWidget(labelRightClick)
    layoutRightClick.addStretch(1)
    layoutRightClick.addWidget(labelDelayRightClick)
    layoutRightClick.addWidget(spinDelayRightClick)

    checkboxDisplaySpinBox = QCheckBox()
    checkboxDisplaySpinBox.setCheckable(True)
    checkboxDisplaySpinBox.setChecked(config.get_params()["main"].GetBool(constants.PARAM_DISPLAY_SPIN_BOX))

    checkboxDisplaySpinBox.stateChanged.connect(
        lambda state: misc_ui.on_display_spin_box(state))

    labelSpinBox = QLabel(
        translate("GlobalSettingsTab", "Direct SpinBox display"))
    labelSpinBox.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
    layoutSpinBox = QtGui.QHBoxLayout()
    layoutSpinBox.addWidget(checkboxDisplaySpinBox)
    layoutSpinBox.addWidget(labelSpinBox)
    layoutSpinBox.addStretch(1)

    globalSettingsGroup = QGroupBox(
        translate("GlobalSettingsTab", "Global settings"))
    globalSettingsGroup.setLayout(QtGui.QVBoxLayout())
    globalSettingsGroup.layout().addLayout(layoutTheme)
    globalSettingsGroup.layout().addLayout(layoutShowQuickMenu)
    globalSettingsGroup.layout().addLayout(layoutGlobalContext)
    globalSettingsGroup.layout().addLayout(layoutGlobalToggle)
    globalSettingsGroup.layout().addLayout(layoutSpinBox)

    experimentalGroup = QGroupBox(
        translate("GlobalSettingsTab", "Experimental"))
    experimentalGroup.setLayout(QtGui.QVBoxLayout())
    experimentalGroup.layout().addLayout(layoutRightClick)

    buttonParamExport = QtGui.QPushButton(
        translate("GlobalSettingsTab", "Export"))
    buttonParamExport.clicked.connect(parameters.export_parameters)

    buttonParamImport = QtGui.QPushButton(
        translate("GlobalSettingsTab", "Import"))
    buttonParamImport.clicked.connect(parameters.import_parameters)

    labelParamExport = QLabel(
        translate("GlobalSettingsTab", "Export PieMenu settings"))
    labelParamExport.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
    layoutParamExport = QtGui.QHBoxLayout()
    layoutParamExport.addWidget(labelParamExport)
    layoutParamExport.addStretch(1)
    layoutParamExport.addWidget(buttonParamExport)

    labelParamImport = QLabel(
        translate("GlobalSettingsTab", "Import PieMenu settings"))
    labelParamImport.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
    layoutParamImport = QtGui.QHBoxLayout()
    layoutParamImport.addWidget(labelParamImport)
    layoutParamImport.addStretch(1)
    layoutParamImport.addWidget(buttonParamImport)

    exportGroup = QGroupBox(translate("GlobalSettingsTab", "Backup settings"))
    exportGroup.setLayout(QtGui.QVBoxLayout())
    exportGroup.layout().addLayout(layoutParamExport)
    exportGroup.layout().addLayout(layoutParamImport)

    # spinBoxGroup = QGroupBox(translate("GlobalSettingsTab", "SpinBox settings"))
    # spinBoxGroup.setLayout(QtGui.QVBoxLayout())
    # spinBoxGroup.layout().addLayout(layoutSpinBox)

    state.app_state.global_shortcut_key = config.get_params()["main"].GetString(constants.PARAM_GLOBAL_SHORTCUT_KEY)

    labelGlobalShortcut = QLabel()
    labelGlobalShortcut.setAlignment(
        QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)

    globalShortcutLineEdit = CustomLineEdit()
    globalShortcutLineEdit.shortcutChanged.connect(
        lambda text: misc_ui.compare_and_display_warning(shortcuts.get_assigned_shortcut(), text))
    globalShortcutLineEdit.setText(state.app_state.global_shortcut_key)
    globalShortcutLineEdit.setToolTip(
        translate("GlobalSettingsTab", "For TAB press CTRL+TAB"))

    assignGlobalShortcutButton = QtGui.QPushButton(
        translate("PieMenuTab", "Assign"))
    assignGlobalShortcutButton.clicked.connect(
        lambda: misc_ui.update_global_shortcut_key(globalShortcutLineEdit.text()))

    deleteGlobalShortcutButton = QtGui.QPushButton()
    deleteGlobalShortcutButton.setMaximumWidth(40)
    deleteGlobalShortcutButton.setIcon(QtGui.QIcon.fromTheme(resources.iconBackspace))
    deleteGlobalShortcutButton.clicked.connect(
        lambda: misc_ui.update_global_shortcut_key(""))

    layoutGlobalShortcut = QtGui.QHBoxLayout()
    layoutGlobalShortcut.addWidget(labelGlobalShortcut)
    layoutGlobalShortcut.addStretch(1)
    layoutGlobalShortcut.addWidget(globalShortcutLineEdit)
    layoutGlobalShortcut.addWidget(assignGlobalShortcutButton)
    layoutGlobalShortcut.addWidget(deleteGlobalShortcutButton)

    settingsTabLayout.insertWidget(0, globalSettingsGroup)
    # settingsTabLayout.insertWidget(1, spinBoxGroup)
    settingsTabLayout.insertWidget(1, experimentalGroup)
    settingsTabLayout.insertWidget(2, exportGroup)
    settingsTabLayout.addStretch(1)
    settingsTabLayout.insertSpacing(3, 42)
    settingsTabLayout.insertLayout(4, layoutGlobalShortcut)
    # Hand off to the bootstrap sequence (piemenu/bootstrap.py).


    return {
        'comboBoxTheme': comboBoxTheme,
        'checkboxQuickMenu': checkboxQuickMenu,
        'checkboxGlobalKeyToggle': checkboxGlobalKeyToggle,
        'checkboxRightClick': checkboxRightClick,
        'spinDelayRightClick': spinDelayRightClick,
        'checkboxDisplaySpinBox': checkboxDisplaySpinBox,
        'labelGlobalShortcut': labelGlobalShortcut,
        'globalShortcutLineEdit': globalShortcutLineEdit,
    }

