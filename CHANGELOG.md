# CHANGELOG

## 1.14
- Refactor: extract `preferences.py`, `bootstrap.py`, `tab_piemenu.py`, `tab_context.py`, `tab_toolbar.py`, `tab_settings.py` from `InitGui.py` (InitGui reduced from 2033 to ~400 lines).
- Refactor: first slice of `PieMenu.add_commands()`: the parameter-reading block (defaults, radius/shape/toolbar override, clamps, angles, display flags) moved to the module-level `read_pie_settings(group, keyValue, commandNumber)` function, which returns a namespace; the layout code keeps its local variable names and is untouched (86 lines removed from `add_commands`).
- Refactor: second slice of `PieMenu.add_commands()`: the `showPie` decision moved to `should_show_pie(module)` (same probing code and behaviour, clearer comments about which state is normal).
- Refactor: third slice of `PieMenu.add_commands()`: the parameter group lookup (named pie via the index list / context / current pie) moved to `resolve_pie_group(keyValue, context)`.
- Refactor: fourth slice of `PieMenu.add_commands()`: the Valid/Cancel + fast PartDesign spinbox block (~113 lines) moved to `_setup_edit_mode_buttons(module, g, wbName, styleCurrentTheme)`; the `try/except` wrapper and its message stay in `add_commands`. Fixed an UnboundLocalError on `g`/`wbName` that the extraction had surfaced (initialised to `None` before the edit-context `try`).
- Refactor: micro-slice of `PieMenu.add_commands()`: the quick-menu button + close button block moved to `_add_quick_menu_and_close_button(module)` (also dropped a dead `displaySpinBox` computation).
- Refactor: micro-slice of `PieMenu.add_commands()`: the separator styling block (inside the per-button loop) moved to `_handle_separator(button, buttonPreselect, iconLabel, icon)`.
- Refactor: micro-slice of `PieMenu.add_commands()`: the per-button preamble (HoverButton + PreselectButton creation) moved to `_create_pie_button(commands, i, buttonSize, icon, radius, styleCurrentTheme)`.
- Refactor: micro-slice of `PieMenu.add_commands()`: the layout-variable init block (ecart, X, Y, shortcut code, max text length) moved to `_init_pie_layout(commandNumber)`, which returns a namespace.
- Refactor: micro-slice of `PieMenu.add_commands()`: the preselection-arrow block (buttonPreselect geometry/icon/rotation) moved to `_setup_preselect_button(...)` (10 parameters).
- Refactor: micro-slice of `PieMenu.add_commands()`: the shortcut-label block moved to `_create_shortcut_label(...)` (9 parameters, returns the updated `shortcutCode`).
- Refactor: micro-slice of `PieMenu.add_commands()`: the `Concentric` shape branch moved to `_layout_concentric(...)` (9 parameters, returns the updated layout variables; mutates `self.radius`/`self.menu`).
- Refactor: micro-slice of `PieMenu.add_commands()`: the `Star` shape branch moved to `_layout_star(...)` (8 parameters, returns the updated `X_shortcut`/`Y_shortcut`; mutates `self.radius`/`self.menu`).
- Refactor: micro-slice of `PieMenu.add_commands()`: the `UpDown` shape branch moved to `_layout_updown(...)` (7 parameters, returns the updated `num_of_column`/`X_shortcut`/`Y_shortcut`; mutates `self.menu`).
- Refactor: micro-slice of `PieMenu.add_commands()`: the `TableTop` shape branch moved to `_layout_table_top(...)` (7 parameters, returns the updated `X_shortcut`/`Y_shortcut`; mutates `self.menu`).
- Refactor: micro-slice of `PieMenu.add_commands()`: the `TableDown` shape branch moved to `_layout_table_down(...)` (7 parameters, returns the updated `X_shortcut`/`Y_shortcut`; mutates `self.menu`).
- Refactor: micro-slice of `PieMenu.add_commands()`: the `TableLeft` shape branch moved to `_layout_table_left(...)` (7 parameters, returns the updated `X_shortcut`/`Y_shortcut`; mutates `self.menu`).
- Refactor: micro-slice of `PieMenu.add_commands()`: the `TableRight` shape branch moved to `_layout_table_right(...)` (7 parameters, returns the updated `X_shortcut`/`Y_shortcut`; mutates `self.menu`).
- Refactor: micro-slice of `PieMenu.add_commands()`: the `else` branch (Pie-without-names / RainbowUp / RainbowDown) moved to `_layout_pie_simple(...)` (8 parameters, returns the updated `X_shortcut`/`Y_shortcut`; mutates `button`, `buttonPreselect`, `self.menu`).
- Fix: the extracted shape-layout helpers (`_layout_updown`, `_layout_table_*`, `_layout_leftright`) were missing `commandNumber`/`num` parameters, causing `NameError` for every shape other than Pie/Concentric/Star/Rainbow; caught by a new all-shapes GUI test (`Temp\opencode\fc_shapes_test.py`) that renders all 11 available shapes. All shapes now render without error.
- Refactor: micro-slice of `PieMenu.add_commands()`: the `LeftRight` shape branch moved to `_layout_leftright(...)` (14 parameters, returns the updated `num_of_column`/`maxTextLength`/`X_shortcut`/`Y_shortcut`/`iconLabel`; mutates `button`, `iconLabel`, `self.menu`).
- Refactor: `spin_interactif` rewritten as a dispatch by feature type: new `constants.SPINBOX_SIZE_ATTR` (feature → property) and `constants.SPINBOX_MIDPLANE_FEATURES` drive the write; ThroughAll/visibility handled separately. Removes the long `if/elif` chain (100 → ~60 lines) and the spurious "spinbox setup failed" log for `Hole`/unknown features.
- Refactor: micro-slice of `PieMenu.eventFilter`: the Wheel handler (spinbox step adjustment on Ctrl/Shift) moved to `_handle_wheel_event(event)`.
- Refactor: micro-slice of `PieMenu.eventFilter`: the right-click timer/debounce block moved to `_handle_right_click(event)` (returns `True`/`False`/`None`).
- Refactor: micro-slice of `PieMenu.eventFilter`: the KeyPress handler (Enter/Return validation + tool-list keys) moved to `_handle_key_press(event)` (returns `True`/`False`/`None`).
- Refactor: micro-slice of `PieMenu.eventFilter`: the KeyPress handler (Enter/Return validation + tool-list keys) moved to `_handle_key_press(event)` (returns `True`/`False`/`None`).
- Refactor: micro-slice of `PieMenu.eventFilter`: the left-button release handler (hide the menu on a click outside) moved to `_handle_left_button_release(event)`.
- Refactor: micro-slice of `PieMenu.eventFilter`: the WindowStateChange handler (hide the menu when the main window is minimised) moved to `_handle_window_state(obj, event)`.
- Refactor: micro-slice of `PieMenu.eventFilter`: the ShortcutOverride handler (tool shortcuts, toggle mode, global shortcut) moved to `_handle_shortcut_override(event)`.
- Refactor: micro-slice of `PieMenu.eventFilter`: the KeyRelease handler (tool-shortcut triggering, Ctrl release → context `list_topo`) moved to `_handle_key_release(event)`.
- Refactor: dedup in `_handle_key_release`: the duplicated tool-shortcut trigger body is now `_trigger_tool_shortcut(event, charKey)` (also fixes a latent bug where the second branch never reset `flag_shortcut_override`).
- Refactor: micro-slice of `PieMenu.eventFilter`: the WindowStateChange handler (hide the menu when the main window is minimised) moved to `_handle_window_state(obj, event)`.
- Refactor: micro-slice of `PieMenu.add_commands()`: the per-button dispatch loop moved to `_build_pie_buttons(ctx)` (reads/writes a shared `SimpleNamespace` state). `add_commands` is now a pure orchestrator (~83 lines).
- Refactor: micro-slice of `PieMenu.add_commands()`: the `Pie`-with-command-names branch moved to `_layout_pie_with_names(...)` (19 parameters, returns the updated `buttonSize`/`radius`/`icon`/`angle`/`X`/`Y`/`X_shortcut`/`Y_shortcut`/`maxTextLength`/`iconLabel`; mutates `button`, `buttonPreselect`, `self.menu`).
- Refactor: micro-slice of `PieMenu.add_commands()`: the per-button dispatch loop moved to `_build_pie_buttons(ctx)` (reads/writes a shared `SimpleNamespace` state). `add_commands` is now a pure orchestrator (~83 lines).
- Refactor: parameter names ("CurrentPie", "EnableShorcut", ...) centralized as `constants.PARAM_*` constants across all modules (typo `EnableShorcut` preserved for backward compatibility).
- Improvement: real failures (workbench activation, parameter reads, spinbox/icon setup, workbench reload, `eventFilter`) are now reported through `piemenu.log` instead of being silently swallowed; expected probes (widget absent, not in edit mode) are annotated with comments.
- Improvement: `log.log_warning_once()` keeps retried warnings (workbench/icon refresh) from flooding the console.
- Fix: `update_icons_pie_menus()` passed a `QIcon` to `extract_workbench()` (expects a string) -> the "load workbench for icon resources" feature silently never ran; it now uses `iconPath`.
- Fix: workbench ids are no longer double-suffixed (`PartDesignWorkbenchWorkbench`, `StartWorkbenchWorkbench`); new `workbench.resolve_workbench_name()` keeps names already ending in "Workbench".
- Feature: first-run wizard (`piemenu/ui/wizard.py`) — shown automatically when no PieMenu exists yet; guides the user through name, shape, tools (templates: View, PartDesign, Sketcher, empty) and creates the pie. Falls back to default pies if cancelled.
- Feature: wizard improvements — command icons in the manual tool list and template preview; live count of selected tools; visual summary of tools (with icons) on the final page.
- Feature: the assistant is a collapsible **left side panel** of the preferences dialog (`piemenu/ui/tab_assistant.py`): it now has its own horizontal `QSplitter`, so it can be dragged away with the mouse.
- Feature: the "Hide assistant" / "Show assistant" button in the bottom button row collapses the whole panel (its width goes to 0 and the tab area takes the freed space); the button stays visible in every state.
- Feature: the assistant panel is now a **contextual guide**: it shows, in plain language, what the currently open view is for (PieMenu, Tools, Context, Global settings, ToolBars), the steps to follow and a warning for the unfinished Context mode. No action buttons are shown: the user keeps using the existing controls (the "+" button, the tabs, ...) described in the text.
- Feature: the PieMenu guide was rewritten for a beginner: it explains what a PieMenu is, then walks through the groups of the tab (Assignment, Shape, Trigger mode, Tools shortcuts) with their real setting names, and ends with the live preview.
- Feature: the assistant follows the view: it updates when the selected tab changes and when the dialog switches to the ToolBars view and back.
- Fix: the assistant panel was a child of the main `vSplitter`, so hiding it gave its space to the pie buttons/preview instead of collapsing the side panel.
- Fix: `update_commands()` raised `UnboundLocalError` on `text` for the toolbar preview (`key_value == "toolBarTab"`), which aborted the preview and logged an error every time the "Workbenches toolbars..." button was used.
- Fix: `read_pie_settings()` logged an error when the pie menu had no parameter group (toolbar preview, pie menu that does not exist yet); the reads are now skipped and the layout keeps its default values, as before the extraction.
- Refactor: removed the dead "Enable PieMenu assistant" checkbox from the Context tab (it wrote to a non-existent parameter and was never read) and its `on_assistant_enabled` handler.
- Feature: the assistant guides for the Tools, Context, Global settings and ToolBars views were rewritten for a beginner, consistent with the actual content of each tab.
- Fix: a macro command prefixed with "Custom_" (e.g. "Custom_BasculeVue") made PieMenu try to activate a non-existent "CustomWorkbench", logging a warning on every refresh; such workbenches are now skipped silently.
- Fix: BOM (U+FEFF) removal from generated modules.
- Fix: corrupted identifier names from substring replacement in tab builders.
- Tests: `tests/test_log.py` (helpers + dedup), `tests/test_workbench.py` (`resolve_workbench_name`), new `tests/test_pie_settings.py` (`read_pie_settings`: defaults, clamps, toolbar override, shape-dependent flags, error fallback), new `tests/test_show_pie.py` (`should_show_pie`: edit/no-edit, Sketcher/Assembly, no document), new `tests/test_pie_group.py` (`resolve_pie_group`: current/context/named/unknown pie) and `tests/test_constants.py` extended (`SPINBOX_SIZE_ATTR`/`SPINBOX_MIDPLANE_FEATURES`) (51 tests total).
- Tests: two new GUI tests (`Temp\opencode\fc_assistant_collapse_test.py` and `Temp\opencode\fc_assistant_content_test.py`) check that the assistant panel is on the left, collapses and expands completely, and follows the selected tab and the ToolBars view.

## 1.13
- Refactor monolithic code https://github.com/Grubuntu/PieMenu/pull/137 (Ben-PH)

## 1.12.4
- Fix https://github.com/Grubuntu/PieMenu/issues/138
## 1.12.3
- Fix SideType/MidPlane parameter depending FreeCAD version

## 1.12.2
- Fix 'Midplane' property being set for the extrusion of Sketch is deprecated and has been replaced by the 'SideType' property in FeatureExtrude.

## 1.12.1
Fix https://github.com/Grubuntu/PieMenu/issues/130

## 1.12
- Add setting to show directly Quick Spinbox or not https://github.com/Grubuntu/PieMenu/issues/126
- Increase spinbox size a little bit
- Pre fix qt6 issues in context tab https://github.com/Grubuntu/PieMenu/issues/125
- Fix issues with Freecad version 1.1.0 (41789) : PieMenus didn't work : Rewrite self.menu : QMenu > QWidget to complie with Qt6
- Remove some redondant code

## 1.11.3
- Fix useless code
- Fix https://github.com/Grubuntu/PieMenu/issues/124
- Code factorization

## 1.11.2
- Fix issue in remove pie function
- Fix issue with plane, axis and datum in context mode
  
## 1.11.1
- Remove : take account of original axes and planes in the context in order to solve an issue
  
## 1.11
- Add ability to add up to 4 rules in context tab
- Added to take account of X,Y and Z Axis (Edge in Context), XY, XZ and YZ Plane (Face in Context) in Context selection.

## 1.10.2
- Fix context not work with external geometry : https://github.com/Grubuntu/PieMenu/issues/116

## 1.10.1
- Fix user config path and export settings extension (hasecilu)
- Fix format for translation (hasecilu)

### 1.10
- Added workbench in toollist 
- Added ability to sort column tool and workbench column ascending or descending
- Added ability to search WB in searchtool
- Added fix for replace "Std_PieMenu_" by "PieMenu_" to comply with standard WB naming 
- Factorize some code
- Removal of the ‘PieMenu’ header from the name of nested menus https://github.com/Grubuntu/PieMenu/issues/112

### 1.9.5
- Fix https://github.com/Grubuntu/PieMenu/issues/109 : circular central button was not circular with the Opentheme theme
  
### 1.9.4
- Fix [#106] : FreeCAD crash when we quit Sketcher with PieMenu validation button and 'Sketcher_Dimension'/'Sketcher_CompDimensionTools' is active
Added ability to move or delete severals command at the same time in list tools : [#105](https://github.com/Grubuntu/PieMenu/issues/105)

### 1.9.3
- Fix copy PieMenu not duplicate all parameters https://github.com/Grubuntu/PieMenu/issues/104
- Partially fix (https://github.com/Grubuntu/PieMenu/issues/106)

### 1.9.2
- Qt6 fix : pressing the global shortcut no longer opens PieMenu
- Qt6 fix : modifiers shortcut were broken
- Qt6 fix : keyValue == False in updateCommands()
 -Qt6 fix : function onToolListWidget() were broken, setting showquickmenu were broken
- Qt6 fix : workbenches toolbars were broken
- Qt6 fix : context mode and setting globalcontext were instable
- Qt6 fix : add eventfilter to catch "minimize event", remove WA_MacAlwaysShowToolWindow : not supported in the same way in Qt5
- Fix : setting immediate trigger
- Fix :problem in createpie (add onpiechange()) to update values after create a new PieMenu

### 1.9.1
- Fix window_icon that appears under the dialog window on Linux system

### 1.9
- Added the ability to use FreeCAD's built-in icons for PieMenus (https://github.com/Grubuntu/PieMenu/issues/97)

### 1.8.1
- Use join() method from path module (as WIP-UIFile)
- Fix issue : https://github.com/Grubuntu/PieMenu/issues/94
- Fix some useless code

### 1.8
- Added import/export PieMenu settings
- Clean some code
  
### 1.7.6
- Fix issue : PieMenu crash at launch with Freecad 0.22 Version above 38001 (https://github.com/Grubuntu/PieMenu/issues/89)
  
### 1.7.5
- Fix issue : when left click in PiemenuDialog, it hid the preview

### 1.7.4
- Fix error message on hover in preview toolbartab
- Fix flickering when multi selections (CTRL) on context mode
- Fix submenus in sketcher edit mode : https://github.com/Grubuntu/PieMenu/issues/87

### 1.7.3
Fix issue with the preselection buttons on hover

### 1.7.2
Fix issue with the  display of the preselection button

### 1.7.1
Fix issue https://github.com/Grubuntu/PieMenu/issues/83 and some warnings about 'font size < 0'

### 1.7

- Added Piemenu preview in Preferences
- Move cBox to the up of settings, disable it when toolBarTab is active
- Fix cBox order
- Added Preselect arrow feature
- Added ability to set a WB for Context mode
- Added added management of the CTRL key for multiple selection in Context mode
- Remove button size limitation and set mini and maxi button size (16-120)
- Remove PiemenuDialog fixed size, position and set it modal.
- Fix cBox index to CurrentPie when the Preferences settings are opened
- Fix icon definition for default PieMenu
- Introduction of context immediate trigger with setting in contextTab

### 1.6

- Added ability to add a custom icon for each PieMenu (SVG or ICO)
- Added ability to call a PieMenu in an other PieMenu (nested PieMenu)
- Added new Toolbars tab in Preferences setting for adding existing FreeCAD's toolbar as new PieMenu
- Added experimental feature : long right click can open the current PieMenu
- Added offset of 1/2 icon for outer rings for Concentric shape
- Fix pyside inconsistent imports

### 1.5.1
- Fix problem : the workbenches were no longer available in the PieMenus due to FreeCAD 0.22Dev code changes
  
### 1.5
- Added expressions in fast spinbox
- Added DEL, SUPPR, UP and DOWN key for delete and move Tools il toollist (Settins > Tools tab)
- Added documentation link to wiki
- Added Icon PieMenu to Preference dialog window
- Added toogle behavior for individuals shortcuts (Limitation : works only for -ONE KEY- shortcuts or -'Modifier' + KEY- shortcuts (not for multikeysequence shortcuts eg. -V,G-)
- Added tools shortcuts keys ('0 to 9' and 'A to Z', except 'X' which bug), update stylesheet according to this new feature
- Enable the tools shortcuts will add a column with shortcuts in toollist
- Added show/hide tools's shortcuts : + spinbox for selected font size
- Added buttons to clear shortcut and globalshortcut
- Added checkbox to set the defaut PieMenu in Preferences
- Highlighting the default PieMenubox by an arrow in front in PieMenu's list and in QuickMenu
- Added validation with 'Enter' and 'Return' keys, when buttons "Validate" and "Cancel" are visible.(as a side-effect, pressing the Enter and return keys also hides the PieMenu)
- Matches the style of the Preferences window with the style of FreeCAD Preferences: Groupboxes, Checkboxes left aligned, Spinbox stretched etc
- Rearranging code

### 1.4.2
- Fix problem: when adding WB that doesn't exist in other FreeCAD version, example: AssemblyWB exists in 0.22 but not in 0.21.
  
### 1.4.1
- Fix bug with workbench associated

### 1.4
- Added workbench associated setting
- Added triggermode setting for each PieMenu
- Added global shortcut toggle mode setting
- Clean some code
- Fix vertical alignment for labels in Preferences
- Added ability to add separators in PieMenu
- Added save settings to disk when you close the preferences window
- Update script for update translation
- Added Polish translation

### 1.3.9
- Fix spacing with command names for Pie shape
- Fix style for command name LeftRight shape
- Added shapes:"Concentric" and "Star"
- Added ability to open PieMenu without file opened

### 1.3.8.2
- Added support for theme accent color (FreeCad>Preferences>Display>Theme>Accent Color)
- Fix default stylesheet to Legacy.qss if no existing stylesheet is set
- Added stylesheet Accents.qss

### 1.3.8.1
- Fix issue with stylesheet

### 1.3.8
- Added a checkbox in fast spinbox mode for Pocket/Pad : Through all, Symmetric, Reversed
- Changing spinbox type to accept calculations and added units
- Reactivation of the quickmenu in the sketcher, the problem seems resolved (def getGroup())
- Fix some bugs : problem when create a ToolBar via QuickMenu, problem with command name setting...
- Remove some useless/duplicate code (def actualizeWorkbenchActions)  
- Rearrangement of menu priorities for Global shortcut: Sketcher, Context, ToolBar, Current Pie (def updateCommands)
- Added command name for LeftRight shape (Pgilfernandez)
- Added French Support

### 1.3.7
- Add translation support, Spanish translation, Small cleanup.(hasecilu) 
- Add Icon spacing, stylabe QuickMenu and many cosmetics improvements (Pgilfernandez)
- Add new shape Left and Right (Pgilfernandez)
- Fix random bug with eventfilter

### 1.3.6
- Update layout of PieMenu Preferences for better readability (Pgilfernandez)
- Fix some typos (Pgilfernandez)
- Added some styles for QLabel command name (Pgilfernandez)
- Added "LeftRight" shape
- Fix problem with ghosting when reload workbenches

### 1.3.5
- Factorization and clean some code
- Added differents shapes for PieMenus
- Added possibility to display the command name in the menu (only Pie shape)
- Added a button with information about developers and licence (Pgilfernandez)
  
### 1.3.4
- Move globals settings on a new tab
- Added setting for show or not the QuickMenu
- Added checkbox in parameters for Contextual activation
- Set default theme (Legacy) on a new installation
- Update stylesheets for #styleButtonMenu::menu-indicator (setting for QuickMenu)





  








