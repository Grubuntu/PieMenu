# PieMenu architecture

PieMenu is a FreeCAD workbench addon. It is a single entry point (`InitGui.py`)
plus a Python package (`piemenu/`) that builds the UI, manages parameters and
draws the radial menu.

## Bootstrap flow

```
InitGui.py
└── pieMenuStart()                         # one giant function, runs at startup
    ├── imports piemenu.* modules and creates aliases
    ├── builds the preferences-dialog widgets
    │   ├── tab_piemenu_ui.build()        # returns a dict of widgets
    │   ├── tab_context_ui.build()
    │   ├── tab_toolbar_ui.build()
    │   └── tab_settings_ui.build()
    ├── assembles the main layout (splitter, buttons, dialog)
    └── hand-off to bootstrap
        └── bootstrap_ui.publish(**locals())   # injects every local as a module global
        └── bootstrap_ui.bootstrap()
            ├── registers the PieMenu_Separator command
            ├── creates the nested PieMenu_* commands
            ├── builds the PieMenu instance
            ├── publishes all widget/callback refs to the piemenu.ui.* modules
            ├── registers the global shortcut
            └── schedules the accessories menu
```

## Module map

| Module | Responsibility |
|---|---|
| `piemenu/config.py` | Access to FreeCAD user parameters (main, index, color) |
| `piemenu/constants.py` | Shape list, comparison signs, `compute_shape_angle` |
| `piemenu/state.py` | `AppState` dataclass (runtime mutable state) |
| `piemenu/context.py` | Context-mode conditions and topology |
| `piemenu/defaults.py` | Default values, legacy parameter migration |
| `piemenu/shortcuts.py` | Per-PieMenu and global shortcut handling |
| `piemenu/workbench.py` | Workbench/action/toolbar discovery |
| `piemenu/pie_menu.py` | The `PieMenu` widget: `add_commands`, event filter, rendering; module-level helpers extracted from `add_commands`: `read_pie_settings`, `should_show_pie`, `resolve_pie_group`, `_setup_edit_mode_buttons`, `_add_quick_menu_and_close_button`, `_handle_separator`, `_create_pie_button`, `_init_pie_layout`, `_setup_preselect_button`, `_create_shortcut_label`, `_layout_concentric`, `_layout_star`, `_layout_updown`, `_layout_table_top`, `_layout_table_down`, `_layout_table_left`, `_layout_table_right`, `_layout_pie_simple`, `_layout_leftright`, `_layout_pie_with_names`, `_build_pie_buttons` |
| `piemenu/bootstrap.py` | Startup orchestration (publish + shortcut + context) |
| `piemenu/widgets.py` | `HoverButton`, `PreselectButton`, `CustomLineEdit` |
| `piemenu/ui/preferences.py` | Preferences dialog + all its handlers |
| `piemenu/ui/tab_piemenu.py` | Builder for the PieMenu tab |
| `piemenu/ui/tab_context.py` | Builder for the Context tab |
| `piemenu/ui/tab_toolbar.py` | Builder for the ToolBar tab |
| `piemenu/ui/tab_settings.py` | Builder for the Global settings tab |
| `piemenu/ui/tab_assistant.py` | Builder for the assistant side panel (left of the preferences dialog) |
| `piemenu/ui/misc.py` | Generic UI helpers (close button, info popup, reload) |
| `piemenu/ui/settings.py` | Settings-tab callbacks (theme, shape, sizes) |
| `piemenu/ui/options.py` | Display-option callbacks (trigger, preselect) |
| `piemenu/ui/context.py` | Context-tab callbacks (add/remove rules) |
| `piemenu/ui/menus.py` | PieMenu create/rename/copy/remove |
| `piemenu/ui/tool_list.py` | Tool list widget + buttons |
| `piemenu/ui/wizard.py` | First-run wizard (QWizard) for creating the first PieMenu |
| `piemenu/ui/icons.py` | Icon picker |

## Preferences dialog layout

The preferences window is assembled in `InitGui.py:pieMenuStart()`:

```
PieMenuDialog
├── preferencesWidget
│   ├── piemenuWidget
│   └── assistantSplitter          (horizontal QSplitter)
│       ├── assistantTab           (left side panel, built by tab_assistant.py)
│       └── vSplitter              (horizontal QSplitter)
│           ├── tabs               (the tab widget)
│           ├── toolBarTab
│           ├── pieButtons
│           └── showPiemenu         (preview)
└── button_layout                  (bottom row)
    ├── info_button
    ├── close_button
    ├── assistant_button            (Hide assistant / Show assistant)
    └── doc_button
```

The assistant has its **own** horizontal splitter so that it behaves like a
real side panel: it can be dragged away with the mouse, and the
`assistant_button` in the bottom row collapses it completely
(`assistantTab.setVisible(False)` -> width 0, the tab area takes the space).
The button lives outside the panel on purpose: it must stay reachable when
the panel is collapsed.

### The assistant guide

`piemenu/ui/tab_assistant.py` holds the guidance in the module-level
`GUIDES` list: one entry per view of the preferences dialog (the entries
follow the order in which the tabs are added in `InitGui.py`, so the index
of a guide is also the index of the matching tab). Each entry has a
`title`, a `summary`, a list of `steps`, an optional `note` and a list of
`actions`.

The guide entries carry a `title`, a `summary`, a list of `steps`, an
optional `note` and an (now empty) list of `actions`: the assistant no
longer shows action buttons, it only advises. The `action_triggered`
signal and the `ACTIONS` table were removed.

`AssistantPanel.refresh()` shows the guide of the view that is currently
open. It is called when the tab widget changes and when the dialog switches
to the ToolBars view.

## The `publish()` pattern

Widgets and callbacks are created during `pieMenuStart()` and then injected
into the modules that need them via `publish(**references)`. Each module
declares module-level attributes (defaulting to `None`) that are filled at
runtime. This decouples the builder from the handlers but means a missing
reference only fails at call time (not at import).

## Logging

`piemenu/log.py` provides `log_error` / `log_warning`. They write to the
FreeCAD console when available, otherwise to stderr. Use them instead of
silent `except: pass`.

## Tests

```
run_tests.bat     # py_compile + unittest (headless, freecadcmd)
```

Tests live in `tests/` and cover constants, state, config, defaults, context,
workbench, logging, module imports and the helpers extracted from
`add_commands` (`read_pie_settings`, `should_show_pie`, `resolve_pie_group`).
GUI smoke tests require a display and are run manually in FreeCAD 1.1.4.
