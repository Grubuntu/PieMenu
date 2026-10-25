"""Helpers to discover FreeCAD workbenches, actions and toolbars.

These functions query the running FreeCAD GUI (through FreeCADGui) to
build the list of available commands/workbenches used by the PieMenu
preferences and the toolbar importer.
"""

from piemenu import config, constants, log


def get_gui_action_map_all():
    """Return a map of every GUI action, keyed by object name."""
    import FreeCADGui as Gui
    from PySide import QtGui

    mw = Gui.getMainWindow()

    # WBs workaround 0.22.37436
    available_actions = {}
    duplicates = []

    wb_container = mw.findChild(QtGui.QAction, "Std_Workbench")
    parent_wb_container = wb_container.parent()
    wb_group = parent_wb_container.findChild(QtGui.QActionGroup)
    for i in wb_group.actions():
        if i.objectName() != "" and i.icon():
            available_actions[i.objectName()] = i
        else:
            pass

    for i in mw.findChildren(QtGui.QAction):
        if i.objectName() is not None:
            if i.objectName() != "" and i.icon():
                if i.objectName() in available_actions:
                    pass
                else:
                    available_actions[i.objectName()] = i
            else:
                pass
        else:
            pass

    for d in duplicates:
        del available_actions[d]

    return available_actions


def extract_workbench(command):
    """Return the workbench name from a FreeCAD command name."""
    cmd_parts = command.split("_")
    if cmd_parts[0] == "":
        workbench = "None"
    else:
        workbench = cmd_parts[0]
    return workbench


def resolve_workbench_name(workbench):
    """Return the FreeCAD workbench id for a (short) workbench name.

    ``"Part"`` becomes ``"PartWorkbench"``, ``"Arch"`` resolves through
    ``constants.workbench_map`` to ``"BIMWorkbench"``, and names that already
    end with ``"Workbench"`` (tool list entries such as
    ``"PartDesignWorkbench"``) are kept as-is instead of being turned into
    invalid ids like ``"PartDesignWorkbenchWorkbench"``.
    """
    mapped = constants.workbench_map.get(workbench)
    if mapped is not None:
        return mapped
    if workbench.endswith("Workbench"):
        return workbench
    return workbench + "Workbench"


def get_action_data(action, actions, commands, workbenches):
    """Append an action and its command/workbench to the given lists."""
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
        workbench = extract_workbench(command)
    if workbenches is not None:
        if workbench not in workbenches:
            workbenches.append(workbench)


def get_gui_tool_button_data(id_tool_bar, actions, commands, workbenches):
    """Collect data for every action associated with a given toolbar."""
    from PySide import QtCore

    action_map_all = get_gui_action_map_all()

    qt_version = QtCore.qVersion()
    qt_major_version = int(qt_version.split('.')[0])

    for i in action_map_all:
        action = action_map_all[i]

        if qt_major_version >= 6:
            # for Qt6
            associated_items = action.associatedObjects()
        else:
            # for Qt5
            associated_items = action.associatedWidgets()
        for widgets in associated_items:
            if widgets.windowTitle() == id_tool_bar:
                get_action_data(action, actions, commands, workbenches)


def actualize_workbench_actions(actions, tool_list, action_map):
    """Activate the workbenches referenced by a tool list.

    This forces FreeCAD to load workbenches whose actions are not yet
    available in the action map.
    """
    import FreeCADGui as Gui

    for i in tool_list:
        # rule out special case: there has to be an entry
        if i == "":
            pass
        elif i in action_map:
            actions.append(action_map[i])
        else:
            workbench = extract_workbench(i)
            # rule out special case: unknown Std action
            if workbench == "Std":
                pass
            else:
                wb_name = resolve_workbench_name(workbench)
                try:
                    Gui.activateWorkbench(wb_name)
                except KeyError:
                    # The command belongs to a workbench that is not installed
                    # (e.g. a macro prefixed with "Custom_"): nothing to
                    # activate, skip silently.
                    pass
                except Exception as exc:
                    # retried on every refresh: warn only once per workbench
                    log.log_warning_once(
                        "wb:" + wb_name,
                        "cannot activate workbench %s (needed by tool %s)" % (wb_name, i),
                        exc)
    return False


def get_list_workbenches():
    """Return a sorted list of workbench names for a combobox."""
    import FreeCADGui as Gui

    workbench_list = Gui.listWorkbenches()
    wb_list = []
    for i in workbench_list:
        wb_name = i.replace("Workbench", "")
        wb_list.append(wb_name)
    wb_list.sort()
    if 'None' in wb_list:
        wb_list.remove('None')
        wb_list.insert(0, 'None')

    return wb_list


def get_pie_name(wb_name):
    """Return the PieMenu name matching a 'DefaultWorkbench' setting."""
    text = None
    index_list = config.get_index_list()
    for i in index_list:
        pie = config.get_param_index(str(i))
        group = config.get_params()["index"].GetGroup(str(i))
        def_wb = group.GetString(constants.PARAM_DEFAULT_WORKBENCH)
        if def_wb == wb_name:
            text = pie
    return text
