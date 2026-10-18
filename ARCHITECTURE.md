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
| `piemenu/pie_menu.py` | The `PieMenu` widget: `add_commands`, event filter, rendering |
| `piemenu/bootstrap.py` | Startup orchestration (publish + shortcut + context) |
| `piemenu/widgets.py` | `HoverButton`, `PreselectButton`, `CustomLineEdit` |
| `piemenu/ui/preferences.py` | Preferences dialog + all its handlers |
| `piemenu/ui/tab_piemenu.py` | Builder for the PieMenu tab |
| `piemenu/ui/tab_context.py` | Builder for the Context tab |
| `piemenu/ui/tab_toolbar.py` | Builder for the ToolBar tab |
| `piemenu/ui/tab_settings.py` | Builder for the Global settings tab |
| `piemenu/ui/misc.py` | Generic UI helpers (close button, info popup, reload) |
| `piemenu/ui/settings.py` | Settings-tab callbacks (theme, shape, sizes) |
| `piemenu/ui/options.py` | Display-option callbacks (trigger, preselect) |
| `piemenu/ui/context.py` | Context-tab callbacks (add/remove rules) |
| `piemenu/ui/menus.py` | PieMenu create/rename/copy/remove |
| `piemenu/ui/tool_list.py` | Tool list widget + buttons |
| `piemenu/ui/toolbar.py` | Toolbar-tab callbacks |
| `piemenu/ui/icons.py` | Icon picker |

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
workbench and module imports. GUI smoke tests require a display and are run
manually.
