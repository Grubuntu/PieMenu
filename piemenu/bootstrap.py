"""Startup bootstrap for the pie_menu.PieMenu workbench.

bootstrap() runs once at the end of pieMenuStart().
"""

import platform

import FreeCAD as App
import FreeCADGui as Gui
from PySide import QtCore, QtGui

from piemenu import config, context, defaults, constants, log, observers, pie_menu, shortcuts, state
from piemenu.commands import PieMenuSeparator
from piemenu.ui import context as context_ui
from piemenu.ui import icons as icons_ui
from piemenu.ui import menus as menus_ui
from piemenu.ui import misc as misc_ui
from piemenu.ui import options as options_ui
from piemenu.ui import preferences as preferences_ui
from piemenu.ui import quick_menu as quick_menu_ui
from piemenu.ui import settings as settings_ui
from piemenu.ui import tool_list as tool_list_ui
from piemenu.ui import toolbar as toolbar_ui
from piemenu.ui import wizard as wizard_ui


def translate(context, text):
    return App.Qt.translate(context, text)


# Widgets and callbacks created by pieMenuStart() and injected via publish().
AttributeError = None
Create = None
FC = None
Fix = None
FreeCAD = None
GetString = None
GlobalShortcutKey = None
Gui = None
Invoke = None
Linux = None
PIE_MENU_VERSION = None
PieMenuInstance = None
PieMenuSeparator = None
PieMenuShortCut = None
PieMenu_Separator = None
Publish = None
QAction = None
QKeySequence = None
QTimer = None
QX11Info = None
QtCore = None
QtGui = None
QuickMenu = None
References = None
Remaining = None
Separator = None
The = None
UI = None
Windows = None
button_list_widget = None
buttons_layout = None
grid_layout = None
icon_default = None
list_tool_bar = None
mw = None
piemenu_box_group = None
quick_menu = None
show_piemenu = None
show_preview_widget = None
tabs = None
tool_bar_tab = None
tool_list_widget = None
v_splitter = None
window_icons = None


def publish(**references):
    globals().update(references)


def bootstrap():
    # Create a fake command in FreeCAD to handle the pie_menu.PieMenu Separator
    Gui.addCommand('PieMenu_Separator', PieMenuSeparator())
    menus_ui.create_nested_pie_menus()

    mw = Gui.getMainWindow()
    start = True
    for action in mw.findChildren(QtGui.QAction):
        if action.objectName() == "PieMenuShortCut":
            start = False
        else:
            pass

    if start:
        state.app_state.compositing_manager = True
        if QtCore.qVersion() < "5":
            state.app_state.window_shadow = False
        else:
            state.app_state.window_shadow = True
        if platform.system() == "Linux":
            try:
                if QtGui.QX11Info.isCompositingManagerRunning():
                    state.app_state.window_shadow = True
                else:
                    state.app_state.compositing_manager = False
            except AttributeError:
                state.app_state.window_shadow = True
        if platform.system() == "Windows":
            state.app_state.window_shadow = True

        # Publish the widgets and the callbacks created above so that the
        # pie_menu.PieMenu class (now in piemenu/pie_menu.py) can reach them.
        pie_menu.publish(
            pie_menu_dialog=pieMenuDialog,
            button_list_widget=buttonListWidget,
            c_box=cBox,
            checkbox_global_key_toggle=checkboxGlobalKeyToggle,
            checkbox_quick_menu=checkboxQuickMenu,
            checkbox_right_click=checkboxRightClick,
            close_button=misc_ui.close_button,
            get_group=preferences_ui.get_group,
            get_shape=preferences_ui.get_shape,
            icon_size=misc_ui.icon_size,
            list_tool_bar=listToolBar,
            on_button_down=tool_list_ui.on_button_down,
            on_button_remove_command=tool_list_ui.on_button_remove_command,
            on_button_up=tool_list_ui.on_button_up,
            quick_menu=quick_menu_ui.quick_menu,
            radius_size=misc_ui.radius_size,
            show_piemenu=showPiemenu,
            show_preview_widget=showPreviewWidget,
            spin_delay_right_click=spinDelayRightClick,
            tabs=tabs,
            update_icons_pie_menus=settings_ui.update_icons_pie_menus,
        )

        context.context_list()
        selObserver = observers.SelObserver()
        state.app_state.sel_observer = selObserver
        context.add_observer()
        context_ui.set_context_conditions()
        PieMenuInstance = pie_menu.PieMenu()
        state.app_state.pie_menu_instance = PieMenuInstance
        pie_menu.publish(pie_menu_instance=PieMenuInstance)
        preferences_ui.publish(pie_menu_instance=PieMenuInstance)
        # References used by the generic UI helpers (piemenu/ui/misc.py).
        misc_ui.publish(
            c_box=cBox,
            combo_context_workbench=comboContextWorkbench,
            combo_wb_for_pie_menu=comboWbForPieMenu,
            get_group=preferences_ui.get_group,
            global_shortcut_line_edit=globalShortcutLineEdit,
            info_shortcut=infoShortcut,
            label_global_shortcut=labelGlobalShortcut,
            label_shortcut=labelShortcut,
            mw=mw,
            on_control=preferences_ui.on_control,
            pie_menu_dialog=pieMenuDialog,
            pie_menu_instance=PieMenuInstance,
            pie_menu_version=PIE_MENU_VERSION,
            shortcut_line_edit=shortcutLineEdit,
            update_piemenu_preview=preferences_ui.update_piemenu_preview,
        )
        # References used by the QuickMenu builder (piemenu/ui/quick_menu.py).
        quick_menu_ui.publish(
            pie_menu_instance=PieMenuInstance,
            create_pie=menus_ui.create_pie,
            icon_default=iconDefault,
            icon_size=misc_ui.icon_size,
            on_context=preferences_ui.on_context,
            on_control=preferences_ui.on_control,
            on_display_spin_box=misc_ui.on_display_spin_box,
            radius_size=misc_ui.radius_size,
        )
        # References used by the tool-list helpers (piemenu/ui/tool_list.py).
        tool_list_ui.publish(
            button_list_widget=buttonListWidget,
            c_box=cBox,
            get_group=preferences_ui.get_group,
            pie_menu_instance=PieMenuInstance,
            reload_workbench=misc_ui.reload_workbench,
            show_piemenu=showPiemenu,
            tool_list_widget=toolListWidget,
        )
        # References used by the toolbar helpers (piemenu/ui/toolbar.py).
        toolbar_ui.publish(
            button_back_to_settings=buttonBackToSettings,
            button_existing_tool_bar=buttonExistingToolBar,
            button_list_widget=buttonListWidget,
            buttons_layout=buttonsLayout,
            create_pie=menus_ui.create_pie,
            info_shortcut=infoShortcut,
            input_text_dialog=menus_ui.input_text_dialog,
            list_tool_bar=listToolBar,
            mw=mw,
            on_back_to_settings=preferences_ui.on_back_to_settings,
            piemenu_box_group=piemenuBoxGroup,
            tabs=tabs,
            tool_bar_tab=toolBarTab,
            update_piemenu_preview=preferences_ui.update_piemenu_preview,
        )
        # References used by the icon helpers (piemenu/ui/icons.py).
        icons_ui.publish(
            button_icon_pie_menu=buttonIconPieMenu,
            c_box=cBox,
            grid_layout=grid_layout,
            on_pie_change=preferences_ui.on_pie_change,
            pie_menu_dialog=pieMenuDialog,
            update_icons_pie_menus=settings_ui.update_icons_pie_menus,
            window_icons=window_icons,
        )
        # References used by the menu helpers (piemenu/ui/menus.py).
        menus_ui.publish(
            c_box=cBox,
            c_box_update=preferences_ui.c_box_update,
            get_group=preferences_ui.get_group,
            on_pie_change=preferences_ui.on_pie_change,
            pie_menu_dialog=pieMenuDialog,
            reload_workbench=misc_ui.reload_workbench,
        )
        # References used by the preferences-dialog handlers
        # (piemenu/ui/preferences.py); they are reachable from the widget
        # signals and from `preferences_ui.get_group()`, which runs at the end of
        # pieMenuStart(). The only exception is the theme combobox, published
        # right after its creation because `preferences_ui.get_theme()` runs at build time.
        preferences_ui.publish(
            button_back_to_settings=buttonBackToSettings,
            button_existing_tool_bar=buttonExistingToolBar,
            button_icon_pie_menu=buttonIconPieMenu,
            button_list_widget=buttonListWidget,
            buttons_layout=buttonsLayout,
            c_box=cBox,
            checkbox_default_pie=checkboxDefaultPie,
            checkbox_display_command_name=checkboxDisplayCommandName,
            checkbox_display_preselect=checkboxDisplayPreselect,
            checkbox_display_shortcut=checkboxDisplayShortcut,
            checkbox_display_spin_box=checkboxDisplaySpinBox,
            checkbox_global_key_toggle=checkboxGlobalKeyToggle,
            checkbox_trigger_context=checkboxTriggerContext,
            combo_shape=comboShape,
            icon_default=iconDefault,
            info_shortcut=infoShortcut,
            label_command_per_circle=labelCommandPerCircle,
            label_display_preselect=labelDisplayPreselect,
            label_global_shortcut=labelGlobalShortcut,
            label_icon_spacing=labelIconSpacing,
            label_num_column=labelNumColumn,
            label_shortcut=labelShortcut,
            label_shortcut_size=labelShortcutSize,
            labeldisplay_command_name=labeldisplayCommandName,
            mw=mw,
            on_assistant_refresh=assistantPanel.refresh,
            pie_menu_dialog=pieMenuDialog,
            piemenu_box_group=piemenuBoxGroup,
            radio_button_hover=radioButtonHover,
            radio_button_press=radioButtonPress,
            shortcut_line_edit=shortcutLineEdit,
            show_piemenu=showPiemenu,
            spin_button=spinButton,
            spin_command_per_circle=spinCommandPerCircle,
            spin_hover_delay=spinHoverDelay,
            spin_icon_spacing=spinIconSpacing,
            spin_num_column=spinNumColumn,
            spin_radius=spinRadius,
            spin_shortcut_label_size=spinShortcutLabelSize,
            tabs=tabs,
            tool_bar_tab=toolBarTab,
            tool_shortcut_group=toolShortcutGroup,
            update_commands=pie_menu.update_commands,
            v_splitter=vSplitter,
        )
        # Remaining references used by the context handlers
        # (piemenu/ui/context.py); the comparison comboboxes and spinboxes were
        # already published right after their creation.
        context_ui.publish(
            add_context_conditions=addContextConditions,
            c_box=cBox,
            get_group=preferences_ui.get_group,
            info_shortcut=infoShortcut,
            label_list_context=labelListContext,
            list_context_conditions=listContextConditions,
            pie_menu_dialog=pieMenuDialog,
        )
        # Remaining references used by the display-option handlers
        # (piemenu/ui/options.py); they are only reachable from user-triggered
        # callbacks, so they are published here once the widgets exist.
        options_ui.publish(
            pie_menu_dialog=pieMenuDialog,
            spin_delay_right_click=spinDelayRightClick,
            spin_hover_delay=spinHoverDelay,
        )
        actionKey = QtGui.QAction(mw)
        state.app_state.action_key = actionKey
        pie_menu.publish(action_key=actionKey)
        # References used by the settings handlers (piemenu/ui/settings.py).
        settings_ui.publish(
            action_key=actionKey,
            c_box=cBox,
            checkbox_global_key_toggle=checkboxGlobalKeyToggle,
            combo_box_theme=comboBoxTheme,
            combo_context_workbench=comboContextWorkbench,
            combo_shape=comboShape,
            combo_wb_for_pie_menu=comboWbForPieMenu,
            get_group=preferences_ui.get_group,
            on_shape=preferences_ui.on_shape,
            pie_menu_dialog=pieMenuDialog,
            spin_button=spinButton,
            spin_command_per_circle=spinCommandPerCircle,
            spin_delay_right_click=spinDelayRightClick,
            spin_hover_delay=spinHoverDelay,
            spin_icon_spacing=spinIconSpacing,
            spin_num_column=spinNumColumn,
            spin_radius=spinRadius,
            spin_shortcut_label_size=spinShortcutLabelSize,
            update_piemenu_preview=preferences_ui.update_piemenu_preview,
        )
        actionKey.setText("Invoke pie menu")
        actionKey.setObjectName("PieMenuShortCut")
        # fix shortcut not trigger on fresh install
        state.app_state.global_shortcut_key = config.get_params()["main"].GetString(constants.PARAM_GLOBAL_SHORTCUT_KEY)
        actionKey.setShortcut(QtGui.QKeySequence(state.app_state.global_shortcut_key))
        actionKey.triggered.connect(PieMenuInstance.showAtMouseInstance)
        mw.addAction(actionKey)
        shortcuts.get_shortcut_list()
        defaults.legacy_fix()
        # Fix errors at first init
        if not config.get_index_list():
            # First run with no PieMenu yet: offer the configuration wizard.
            # If the user cancels it, fall back to the default pies.
            wt = QtCore.QTimer()
            wt.setSingleShot(True)
            misc_ui.publish(wizard_timer=wt)

            def _show_wizard():
                try:
                    wizard_ui.maybe_show(Gui.getMainWindow())
                except Exception as exc:
                    log.log_error("first-run wizard failed", exc)
                finally:
                    if not config.get_index_list():
                        defaults.set_default_pie()
                    preferences_ui.get_group()

            wt.timeout.connect(_show_wizard)
            wt.start(1500)
        else:
            preferences_ui.get_group()
        # let the addition of the accessoriesMenu wait until FC is ready for it
        t = QtCore.QTimer()
        misc_ui.publish(timer=t)
        t.timeout.connect(misc_ui.add_accessories_menu)
        t.start(500)

    else:
        pass


