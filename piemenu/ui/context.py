"""Context-tab handlers for the preferences dialog.

`on_add_context_conditions()` and `on_del_context_conditions()` create and
delete context rules, `on_row_selected()` loads a rule into the comboboxes and
spinboxes of the Context tab, `update_info_shortcut()` refreshes the hint label
and `on_clear_context_selection()` resets the current selection.

The tab is built by `combo_box()` and `spin_box()`, which create the comparison
widgets, `set_context_conditions()` / `update_context_conditions()` fill the
rules table, `parse_context_conditions()` renders a rule as text and
`on_reset_context_table()` clears the current selection.

The widgets and callbacks below are created by `pieMenuStart()` after this
module is imported, so they are declared as module attributes here and
published by `pieMenuStart()` through `publish()`.
"""

from functools import partial

import FreeCAD as App
from PySide import QtCore, QtGui
from PySide.QtCore import Qt
from PySide.QtWidgets import QCheckBox

from piemenu import config, resources, state
from piemenu.config import get_index_list, get_param_index
from piemenu.context import context_list
from piemenu.theme import get_style


def translate(context, text):
    """Translate a string with the FreeCAD Qt translator."""
    return App.Qt.translate(context, text)


# Widgets created by `pieMenuStart()` and injected via `publish()`.
add_context_conditions = None
axis_combo_box = None
axis_spin = None
c_box = None
edge_combo_box = None
edge_spin = None
face_combo_box = None
face_spin = None
get_group = None
info_shortcut = None
label_list_context = None
list_context_conditions = None
object_combo_box = None
object_spin = None
pie_menu_dialog = None
plane_combo_box = None
plane_spin = None
vertex_combo_box = None
vertex_spin = None


def publish(**references):
    """Publish the runtime references used by the context handlers."""
    globals().update(references)


def update_info_shortcut():
    info_shortcut.setText(translate(
        "ContextTab", "Select an existing rule to modify it or create a new one."))

def on_add_context_conditions(subgroup=None):
    """ Add new context rule in context Tab """
    indexList = get_index_list()
    numGroup = 0
    for i in indexList:
        pieName = get_param_index(str(i))
        if pieName == c_box.currentText():
            group = config.get_params()["index"].GetGroup(str(i))
            contexts = ["Context", "Context2", "Context3", "Context4"]
            for subGroup in contexts:
                groupContext = group.GetGroup(subGroup)
                groupContents = groupContext.GetContents()
                if groupContents:
                    numGroup += 1
                else:
                    info_shortcut.setText('')
                    groupContext.SetString(
                        "VertexSign", vertex_combo_box.currentText())
                    groupContext.SetString(
                        "EdgeSign", edge_combo_box.currentText())
                    groupContext.SetString(
                        "FaceSign", face_combo_box.currentText())
                    groupContext.SetString(
                        "ObjectSign", object_combo_box.currentText())
                    groupContext.SetString(
                        "AxisSign", axis_combo_box.currentText())
                    groupContext.SetString(
                        "PlaneSign", plane_combo_box.currentText())

                    groupContext.SetInt("VertexValue", vertex_spin.value())
                    groupContext.SetInt("EdgeValue", edge_spin.value())
                    groupContext.SetInt("FaceValue", face_spin.value())
                    groupContext.SetInt("ObjectValue", object_spin.value())
                    groupContext.SetInt("AxisValue", axis_spin.value())
                    groupContext.SetInt("PlaneValue", plane_spin.value())

                    groupContext.SetBool("Enabled", 1)

                    update_context_conditions()
                    break

def on_del_context_conditions(subgroup=None):
    """ Delete a context rule """
    if subgroup:
        indexList = get_index_list()
        for index in indexList:
            pieName = get_param_index(str(index))
            if pieName == c_box.currentText():
                group = config.get_params()["index"].GetGroup(str(index))
                if group.GetGroup(subgroup):
                    group.RemGroup(subgroup)
                    # workaround to refresh the window to avoid bug
                    # https://github.com/Grubuntu/PieMenu/issues/125
                    # Closing the dialog rebuilds the rules table, which
                    # destroys the remove button currently emitting `clicked`;
                    # doing it from inside the slot crashes FreeCAD, so the
                    # refresh is deferred to the next event-loop cycle.
                    QtCore.QTimer.singleShot(0, refresh_context_window)


def refresh_context_window():
    """ Refresh the preferences window after a context rule removal """
    pie_menu_dialog.close()
    pie_menu_dialog.show()

def on_row_selected():
    """ Update values in comboboxes and spinboxes according to selected rule """
    selectedItems = list_context_conditions.currentItem()
    if not selectedItems:
        return

    row = selectedItems.row()  # Récupère la ligne sélectionnée
    subGroup = state.app_state.row_subgroup_map.get(row)  # Récupère le subGroup associé

    # if already selectd, we deselect it
    if subGroup == state.app_state.sub_group_selected:
        on_clear_context_selection()
    else:
        state.app_state.sub_group_selected = subGroup
        if subGroup:
            indexList = get_index_list()
            group = None
            # Trouve le groupe associé à la sélection
            for i in indexList:
                pieName = get_param_index(str(i))
                if pieName == c_box.currentText():
                    group = config.get_params()["index"].GetGroup(str(i))
                    break

            if group:
                groupContext = group.GetGroup(subGroup)
                # Mise à jour des combobox et spinbox
                update_combo_box(
                    vertex_combo_box, groupContext.GetString("VertexSign"))
                vertex_spin.setValue(groupContext.GetInt("VertexValue"))
                update_combo_box(
                    edge_combo_box, groupContext.GetString("EdgeSign"))
                edge_spin.setValue(groupContext.GetInt("EdgeValue"))
                update_combo_box(
                    face_combo_box, groupContext.GetString("FaceSign"))
                face_spin.setValue(groupContext.GetInt("FaceValue"))
                update_combo_box(
                    object_combo_box, groupContext.GetString("ObjectSign"))
                object_spin.setValue(groupContext.GetInt("ObjectValue"))
                update_combo_box(
                    axis_combo_box, groupContext.GetString("AxisSign"))
                axis_spin.setValue(groupContext.GetInt("AxisValue"))
                update_combo_box(
                    plane_combo_box, groupContext.GetString("PlaneSign"))
                plane_spin.setValue(groupContext.GetInt("PlaneValue"))

            update_context_conditions()

def update_combo_box(comboBox, value):
    """Met à jour la sélection d'une combobox avec une valeur donnée."""
    index = comboBox.findText(value)
    if index != -1:
        comboBox.setCurrentIndex(index)

def on_context_enabled(state, group, subGroup):
    """ Update 'Enabled' parameter when checkboxstate change """
    groupContext = group.GetGroup(subGroup)
    if state == 2:
        groupContext.SetBool("Enabled", 1)
    else:
        groupContext.SetBool("Enabled", 0)

def on_clear_context_selection():
    """ Clear the selection in the list of rules """
    state.app_state.sub_group_selected = None
    update_context_conditions()

def combo_box(TopoType):
    """ Set combobox for context conditions """
    signList = ["<", "<=", "==", "!=", ">", ">="]
    model = QtGui.QStandardItemModel()
    for i in signList:
        item = QtGui.QStandardItem()
        item.setText(i)
        item.setData(TopoType, QtCore.Qt.UserRole)
        model.setItem(signList.index(i), 0, item)
    comboBoxSign = QtGui.QComboBox()
    comboBoxSign.setObjectName("styleCombo")
    comboBoxSign.setModel(model)
    styleCurrentTheme = get_style()
    comboBoxSign.setStyleSheet(styleCurrentTheme)

    def onCurrentIndexChanged():
        if state.app_state.sub_group_selected:
            group = get_group()
            groupContext = group.GetGroup(state.app_state.sub_group_selected)
            text = comboBoxSign.currentText()
            topo = comboBoxSign.itemData(comboBoxSign.currentIndex(),
                                         QtCore.Qt.UserRole)
            groupContext.SetString(topo, text)
            context_list()
            update_context_conditions()
            info_shortcut.setText("")
        else:
            update_info_shortcut()

    comboBoxSign.currentIndexChanged.connect(onCurrentIndexChanged)
    return comboBoxSign

def spin_box(TopoValue):
    """ Spinbox in context tab """
    spin_box = QtGui.QSpinBox()
    spin_box.setFrame(False)

    def onSpinBox():
        if state.app_state.sub_group_selected:
            group = get_group()
            groupContext = group.GetGroup(state.app_state.sub_group_selected)
            value = spin_box.value()
            groupContext.SetInt(TopoValue, value)
            context_list()
            update_context_conditions()
            info_shortcut.setText("")
        else:
            update_info_shortcut()

    spin_box.valueChanged.connect(onSpinBox)
    return spin_box

def update_context_conditions():
    """ Update context rules in Context Tab """

    indexList = get_index_list()
    selectedPie = c_box.currentText()

    # Efface les anciennes données du tableau
    list_context_conditions.setUpdatesEnabled(False)
    list_context_conditions.setRowCount(0)

    state.app_state.row_subgroup_map.clear()
    row = -1
    for index in indexList:
        pieName = get_param_index(str(index))
        if pieName == selectedPie:
            group = config.get_params()["index"].GetGroup(str(index))
            if not group:
                continue  # Skip if group is invalid

            subgroups = group.GetGroups()
            if not subgroups:
                continue  # Skip if no subgroups found

            for subGroup in subgroups:
                groupContext = group.GetGroup(subGroup)
                groupContents = groupContext.GetContents()
                if groupContents:
                    row = list_context_conditions.rowCount()
                    list_context_conditions.insertRow(row)

                    # Add checkbox for enabling/disabling
                    subgroupContextEnabled = QCheckBox(
                        translate("ContextTab", ""))
                    subgroupContextEnabled.setCheckable(True)
                    subgroupContextEnabled.setToolTip(translate(
                        "ContextTab", "Ticked the box to enable the contextual rule."))

                    subgroupContextEnabled.setChecked(
                        groupContext.GetBool("Enabled"))
                    subgroupContextEnabled.stateChanged.connect(
                        lambda state, group=group, subGroup=subGroup: on_context_enabled(
                            state, group, subGroup)
                    )
                    list_context_conditions.setCellWidget(
                        row, 0, subgroupContextEnabled)

                    # Add condition description
                    conditionItem = QtGui.QTableWidgetItem(
                        parse_context_conditions(subGroup))
                    conditionItem.setTextAlignment(
                        Qt.AlignLeft | Qt.AlignVCenter)
                    conditionItem.setFlags(
                        Qt.ItemIsSelectable | Qt.ItemIsEnabled)
                    conditionItem.setToolTip(
                        translate("ContextTab", "Select a rule to modify it. If the rule is active and the selection matches the criteria chosen, this PieMenu will open."))
                    list_context_conditions.setItem(row, 1, conditionItem)

                    # Add remove button
                    buttonRemoveCondition = QtGui.QToolButton()
                    buttonRemoveCondition.setIcon(QtGui.QIcon(resources.iconRemove))
                    buttonRemoveCondition.setIconSize(QtCore.QSize(18, 18))
                    buttonRemoveCondition.setToolTip(
                        translate("ContextTab", "Delete this rule"))
                    buttonRemoveCondition.clicked.connect(
                        partial(on_del_context_conditions, subGroup))
                    list_context_conditions.setCellWidget(
                        row, 2, buttonRemoveCondition)

                    # Map the row number to subGroup
                    state.app_state.row_subgroup_map[row] = subGroup

                    # Mettre en gras si le subGroup correspond au state.app_state.sub_group_selected global
                    if state.app_state.sub_group_selected == subGroup:
                        for c in range(list_context_conditions.columnCount()):
                            item = list_context_conditions.item(row, c)
                            if item:
                                font = item.font()
                                font.setBold(True)  # Appliquer le gras
                                item.setFont(font)

    label_list_context.setText(
        translate("ContextTab", "List of current selection rules: {}/4").format(row+1))

    # Disable ability to add new rule when max (4) is reached (row : 0,1,2,3)
    if row > 2:
        add_context_conditions.setEnabled(False)
    else:
        add_context_conditions.setEnabled(True)

    list_context_conditions.setUpdatesEnabled(True)

def parse_context_conditions(subGroup=None):
    """ Generates the String representing the context rule conditions """
    indexList = get_index_list()
    for i in indexList:
        pieName = get_param_index(str(i))
        if pieName == c_box.currentText():
            group = config.get_params()["index"].GetGroup(str(i))
            if subGroup:
                a = group.GetGroup(subGroup)
                liste = a.GetContents()

                signs = {}
                values = {}

                if liste:
                    # Remplir les dictionnaires
                    for item in liste:
                        if item[0] == 'String':
                            # Sauvegarder les éléments de type String (nom + signe)
                            # Suppression de 'Sign' pour obtenir juste le nom
                            key = item[1].replace('Sign', '')
                            # Ici on récupère le signe
                            signs[key] = item[2]
                        elif item[0] == 'Integer':
                            # Sauvegarder les valeurs
                            # Suppression de 'Value' pour obtenir juste le nom
                            key = item[1].replace('Value', '')
                            values[key] = item[2]

                # Construction de la chaîne de texte finale
                result = ', '.join(
                    f"{key} {signs[key]} {values[key]}" for key in signs)
    return result

def on_reset_context_table():
    """ Reset combobox and spinbox values in context tab """
    group = get_group()
    if state.app_state.sub_group_selected:
        groupContext = group.GetGroup(state.app_state.sub_group_selected)
        groupContext.SetBool("Enabled", 0)

    # Initialisation des combobox et spinbox
    update_combo_box(vertex_combo_box, "==")
    vertex_spin.setValue(10)
    update_combo_box(edge_combo_box, "==")
    edge_spin.setValue(10)
    update_combo_box(face_combo_box, "==")
    face_spin.setValue(10)
    update_combo_box(object_combo_box, "==")
    object_spin.setValue(10)
    update_combo_box(axis_combo_box, "==")
    axis_spin.setValue(10)
    update_combo_box(plane_combo_box, "==")
    plane_spin.setValue(10)
    update_context_conditions()

def set_context_conditions():
    """Initializes the context conditions depending on parameters."""
    def update_sign(group_context, key, combo_box, default="=="):
        """Update the sign value and set the combo box index."""
        sign_value = group_context.GetString(key)
        if sign_value not in state.app_state.signs:
            group_context.SetString(key, default)
            sign_value = default
        for i in range(combo_box.count()):
            if combo_box.itemText(i) == sign_value:
                combo_box.setCurrentIndex(i)
                break

    def update_value(group_context, key, spin_box, default=10):
        """Update the value and set the spin box."""
        value = group_context.GetInt(key)
        if not value:
            a = group_context.GetInt(key, True)
            b = group_context.GetInt(key, False)
            value = 0 if a == b else default
            group_context.SetInt(key, value)
        spin_box.setValue(value)

    index_list = get_index_list()
    contexts = ["Context", "Context2", "Context3", "Context4"]

    for i in index_list:
        group = config.get_params()["index"].GetGroup(str(i))
        for sub_group in contexts:
            group_context = group.GetGroup(sub_group)
            group_contents = group_context.GetContents()

            if group_contents:
                enabled = group_context.GetBools()
                if enabled:
                    break
                else:
                    group_context.SetBool("Enabled", 0)

                # Update signs and values for each component
                update_sign(group_context, "VertexSign", vertex_combo_box)
                update_value(group_context, "VertexValue", vertex_spin)
                update_sign(group_context, "EdgeSign", edge_combo_box)
                update_value(group_context, "EdgeValue", edge_spin)
                update_sign(group_context, "FaceSign", face_combo_box)
                update_value(group_context, "FaceValue", face_spin)
                update_sign(group_context, "ObjectSign", object_combo_box)
                update_value(group_context, "ObjectValue", object_spin)
                update_sign(group_context, "AxisSign", axis_combo_box)
                update_value(group_context, "AxisValue", axis_spin)
                update_sign(group_context, "PlaneSign", plane_combo_box)
                update_value(group_context, "PlaneValue", plane_spin)
    context_list()
