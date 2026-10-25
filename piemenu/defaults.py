"""Default PieMenu definitions and legacy parameter migration."""

from piemenu import config, constants


def set_default_values(group):
    """Write the default values of a PieMenu group in user.cfg."""
    group.SetInt(constants.PARAM_RADIUS, 80)
    group.SetInt(constants.PARAM_BUTTON, 32)
    group.SetString(constants.PARAM_SHAPE, "Pie")
    group.SetString(constants.PARAM_TRIGGER_MODE, "Press")
    group.SetInt(constants.PARAM_HOVER_DELAY, 100)
    group.SetBool(constants.PARAM_ENABLE_SHORTCUT, False)
    group.SetBool(constants.PARAM_DISPLAY_PRESELECT, False)
    group.SetInt(constants.PARAM_SHORTCUT_LABEL_SIZE, 8)


def set_default_pie(restore=False):
    """Initialize the default PieMenus (View, PartDesign, Sketcher) if needed."""
    import FreeCAD as App

    index_list = config.get_index_list()
    if 0 in index_list:
        if restore:
            group = config.get_params()["index"].GetGroup("0")
            group.SetString(constants.PARAM_TOOL_LIST, ".,.".join(constants.defaultTools))
        else:
            pass
    else:
        index_list.append(0)
        index_list.append(1)
        index_list.append(2)

        temp = []

        for i in index_list:
            temp.append(str(i))

        index_list = temp

        config.get_params()["index"].SetString("0", "View")
        config.get_params()["index"].SetString(constants.PARAM_INDEX_LIST, ".,.".join(index_list))

        group = config.get_params()["index"].GetGroup("0")
        group.SetString(constants.PARAM_TOOL_LIST, ".,.".join(constants.defaultTools))
        set_default_values(group)

        config.get_params()["index"].SetString("1", "PartDesign")
        group = config.get_params()["index"].GetGroup("1")
        group.SetString(constants.PARAM_TOOL_LIST, ".,.".join(constants.defaultToolsPartDesign))
        set_default_values(group)

        config.get_params()["index"].SetString("2", "Sketcher")
        group = config.get_params()["index"].GetGroup("2")
        group.SetString(constants.PARAM_TOOL_LIST, ".,.".join(constants.defaultToolsSketcher))
        set_default_values(group)
        group.SetString(constants.PARAM_DEFAULT_WORKBENCH, "Sketcher")

    config.get_params()["main"].SetBool(constants.PARAM_TOOL_BAR, False)
    config.get_params()["main"].RemString(constants.PARAM_TOOL_BAR)
    config.get_params()["main"].SetString(constants.PARAM_CURRENT_PIE, "View")
    config.get_params()["main"].SetString(constants.PARAM_THEME, "Legacy")
    config.get_params()["main"].SetString(constants.PARAM_GLOBAL_SHORTCUT_KEY, "TAB")
    config.get_params()["main"].SetBool(constants.PARAM_SHOW_QUICK_MENU, True)
    config.get_params()["main"].SetBool(constants.PARAM_DISPLAY_SPIN_BOX, True)
    config.get_params()["main"].SetBool(constants.PARAM_ENABLE_CONTEXT, False)
    config.get_params()["main"].SetBool(constants.PARAM_GLOBAL_KEY_TOGGLE, True)
    config.get_params()["main"].SetInt(constants.PARAM_DELAY_RIGHT_CLICK, 100)
    App.saveParameter()


def legacy_fix():
    """Migrate parameters written by older PieMenu versions."""
    # Since v1.10: "Std_PieMenu_" replaced by "PieMenu_" to comply with WB naming
    index_list = config.get_index_list()
    for i in index_list:
        pie = config.get_param_index(str(i))
        group = config.get_params()["index"].GetGroup(str(i))
        tool_list = config.get_parameter_group(pie, "String", constants.PARAM_TOOL_LIST)

        if "Std_PieMenu_" in tool_list:
            tool_list = tool_list.replace("Std_PieMenu_", "PieMenu_")
            group.SetString(constants.PARAM_TOOL_LIST, tool_list)

        if 'Std_PieMenuSeparator' in tool_list:
            tool_list = tool_list.replace(
                "Std_PieMenuSeparator", "PieMenu_Separator")
            group.SetString(constants.PARAM_TOOL_LIST, tool_list)

    # v1.12: introduce the constants.PARAM_DISPLAY_SPIN_BOX setting, default True when missing.
    setting_content = config.get_params()["main"].GetContents()
    if not any(item[1] == constants.PARAM_DISPLAY_SPIN_BOX for item in setting_content):
        config.get_params()["main"].SetBool(constants.PARAM_DISPLAY_SPIN_BOX, True)
