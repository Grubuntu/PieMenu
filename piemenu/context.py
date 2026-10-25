"""Selection context handling for the PieMenu workbench.

Builds the context conditions from the parameters, computes the topology of
the current selection and triggers the matching contextual PieMenu.
"""

from piemenu import config, constants, state


def context_list():
    """Build the list of enabled context conditions from the parameters."""
    state.app_state.context_all.clear()
    index_list = config.get_index_list()
    j = 0
    for i in index_list:
        group = config.get_params()["index"].GetGroup(str(i))
        for groupe in group.GetGroups():
            group_context = group.GetGroup(groupe)
            if group_context.GetBool("Enabled"):
                current = {}
                current["Index"] = str(i)
                current["VertexSign"] = group_context.GetString("VertexSign")
                current["VertexValue"] = group_context.GetInt("VertexValue")

                current["EdgeSign"] = group_context.GetString("EdgeSign")
                current["EdgeValue"] = group_context.GetInt("EdgeValue")

                current["FaceSign"] = group_context.GetString("FaceSign")
                current["FaceValue"] = group_context.GetInt("FaceValue")

                current["ObjectSign"] = group_context.GetString("ObjectSign")
                current["ObjectValue"] = group_context.GetInt("ObjectValue")

                current["AxisSign"] = group_context.GetString("AxisSign")
                current["AxisValue"] = group_context.GetInt("AxisValue")

                current["PlaneSign"] = group_context.GetString("PlaneSign")
                current["PlaneValue"] = group_context.GetInt("PlaneValue")
                state.app_state.context_all[j] = current
                j += 1


def get_context_pie(v, e, f, o, a, p):
    """Return the index of the PieMenu matching the given topology counts."""
    import FreeCAD as App
    import FreeCADGui as Gui

    translate = App.Qt.translate
    global_context_pie = False
    global_index_pie = None
    index_pie = None

    for i in state.app_state.context_all:
        current = state.app_state.context_all[i]

        def vertex():
            if state.app_state.signs[current["VertexSign"]](v, current["VertexValue"]):
                edge()

        def edge():
            if state.app_state.signs[current["EdgeSign"]](e, current["EdgeValue"]):
                face()

        def face():
            if state.app_state.signs[current["FaceSign"]](f, current["FaceValue"]):
                axis()

        def axis():
            try:
                if state.app_state.signs[current["AxisSign"]](a, current["AxisValue"]):
                    planes()
            except Exception:
                # legacy fix: no parameter for axis
                if a == current["AxisValue"]:
                    planes()

        def planes():
            try:
                if state.app_state.signs[current["PlaneSign"]](p, current["PlaneValue"]):
                    obj()
            except Exception:
                # legacy fix: no parameter for planes
                if p == current["PlaneValue"]:
                    obj()

        def obj():
            nonlocal global_context_pie, global_index_pie, index_pie
            if state.app_state.signs[current["ObjectSign"]](o, current["ObjectValue"]):
                global_index_pie = current["Index"]
                if global_index_pie:
                    pie_name = config.get_param_index(global_index_pie)
                    context_workbench = None
                    context_workbench = config.get_parameter_group(
                        pie_name, "String", constants.PARAM_CONTEXT_WORKBENCH)
                    active_wb = Gui.activeWorkbench().name()
                    active_wb = active_wb.split("Workbench")

                    if (context_workbench == active_wb[0]
                            or context_workbench == translate("ContextTab", "All Workbenches")):
                        global_context_pie = "True"
                        index_pie = current["Index"]

        vertex()

    if global_context_pie == "True":
        return index_pie
    return None


def list_topo():
    """Handle conditions to trigger context mode."""
    import FreeCAD as App
    import FreeCADGui as Gui

    translate = App.Qt.translate
    pie_menu_instance = state.app_state.pie_menu_instance

    module = None
    try:
        g = Gui.ActiveDocument.getInEdit()
        module = g.Module
    except Exception:
        # not in edit mode: keep module = None
        pass

    if module is None or module == "SketcherGui":
        sel = Gui.Selection.getSelectionEx()
        vertexes = 0
        edges = 0
        faces = 0
        objects = 0
        axis = 0
        planes = 0
        all_list = []
        list_axis = ['X_Axis', 'Y_Axis', 'Z_Axis', 'H_Axis', 'V_Axis']
        list_planes = ['XY_Plane', 'XZ_Plane', 'YZ_Plane']
        for i in sel:
            if i.ObjectName in list_axis or i.ObjectName in list_planes:
                all_list.append(i.ObjectName)
            elif i.ObjectName.startswith("DatumPlane"):
                planes = planes + 1
            elif i.ObjectName.startswith("DatumLine"):
                axis = axis + 1
            elif i.ObjectName.startswith("DatumPoint"):
                vertexes = vertexes + 1
            elif not i.SubElementNames:
                objects = objects + 1
            else:
                for a in i.SubElementNames:
                    all_list.append(a)
        for i in all_list:
            if i.startswith('Vertex') or i.startswith('ExternalVertex') or i.startswith('RootPoint'):
                vertexes = vertexes + 1
            elif i.startswith('Edge') or i.startswith('ExternalEdge'):
                edges = edges + 1
            elif i.startswith('Face'):
                faces = faces + 1
            elif i.startswith('X_Axis') or i.startswith('Y_Axis') or i.startswith('Z_Axis') or i.startswith('H_Axis') or i.startswith('V_Axis'):
                axis = axis + 1
            elif i.startswith('XY_Plane') or i.startswith('XZ_Plane') or i.startswith('YZ_Plane'):
                planes = planes + 1
            else:
                pass
        pie_index = get_context_pie(vertexes,
                                    edges,
                                    faces,
                                    objects,
                                    axis,
                                    planes)

        if pie_index:
            pie_name = config.get_param_index(pie_index)
            try:
                config.get_params()["main"].SetString(constants.PARAM_CONTEXT_PIE, pie_name)
            except TypeError:
                config.get_params()["main"].SetString(constants.PARAM_CONTEXT_PIE, pie_name)
            state.app_state.context_phase = True

            pie_menu_instance.hide()

            active_wb = Gui.activeWorkbench().name()
            active_wb = active_wb.split("Workbench")
            context_workbench = None
            context_workbench = config.get_parameter_group(
                pie_name, "String", constants.PARAM_CONTEXT_WORKBENCH)

            if (context_workbench == active_wb[0] or context_workbench is None
                    or context_workbench == translate("ContextTab", "All Workbenches")):
                immediate_trigger = config.get_parameter_group(
                    pie_name, "Bool", "ImmediateTriggerContext")
                if immediate_trigger:
                    pie_menu_instance.showAtMouseInstance()
        else:
            state.app_state.context_phase = False
    return state.app_state.context_phase


def add_observer():
    """Add or remove the selection observer according to the parameters."""
    import FreeCADGui as Gui

    sel_observer = state.app_state.sel_observer
    if config.get_params()["main"].GetBool(constants.PARAM_ENABLE_CONTEXT):
        Gui.Selection.addObserver(sel_observer)
    else:
        Gui.Selection.removeObserver(sel_observer)
