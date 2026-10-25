"""First-run wizard for PieMenu.

Shown automatically when no PieMenu exists yet (fresh install). Guides the
user through creating a first radial menu: name, shape, tools (template or
manual selection) and an optional global shortcut.
"""

from piemenu import config, constants, log, state
from piemenu.config import get_index_list, get_param_index, get_parameter_group
from piemenu.defaults import set_default_pie, set_default_values
from piemenu.ui import menus as menus_ui
from piemenu.ui import settings as settings_ui

import FreeCAD as App
import FreeCADGui as Gui
from PySide import QtCore, QtGui
from PySide.QtWidgets import (
    QComboBox, QFormLayout, QLabel, QLineEdit, QListWidget, QListWidgetItem,
    QRadioButton, QWizard, QWizardPage, QVBoxLayout, QWidget, QButtonGroup,
)


def translate(context, text):
    return App.Qt.translate(context, text)


TEMPLATES = [
    ("View (navigation)", "View", constants.defaultTools),
    ("PartDesign (conception)", "PartDesign", constants.defaultToolsPartDesign),
    ("Sketcher (esquisse)", "Sketcher", constants.defaultToolsSketcher),
    ("Vide (à remplir plus tard)", None, []),
]


class WelcomePage(QWizardPage):
    def __init__(self):
        super().__init__()
        self.setTitle(translate("Wizard", "Bienvenue dans PieMenu"))
        layout = QVBoxLayout(self)
        intro = QLabel(translate(
            "Wizard",
            "PieMenu ajoute un menu radial contextuel à FreeCAD.\n\n"
            "Cet assistant crée votre premier menu en quelques clics.\n"
            "Vous pourrez ensuite le personnaliser dans les préférences."))
        intro.setWordWrap(True)
        layout.addWidget(intro)
        layout.addStretch(1)


class NameShapePage(QWizardPage):
    def __init__(self):
        super().__init__()
        self.setTitle(translate("Wizard", "Nom et forme"))
        layout = QFormLayout(self)

        self.name_edit = QLineEdit("MonPie")
        self.name_edit.setPlaceholderText(translate("Wizard", "Nom du menu"))
        layout.addRow(translate("Wizard", "Nom :"), self.name_edit)

        self.shape_combo = QComboBox()
        self.shape_combo.addItems(constants.available_shape)
        self.shape_combo.setCurrentText("Pie")
        layout.addRow(translate("Wizard", "Forme :"), self.shape_combo)

        hint = QLabel(translate(
            "Wizard",
            "La forme « Pie » est recommandée pour commencer."))
        hint.setWordWrap(True)
        layout.addRow(hint)

        self.registerField("pieName*", self.name_edit)
        self.registerField("pieShape", self.shape_combo, "currentText")

    def validatePage(self):
        name = self.name_edit.text().strip()
        if not name:
            QtGui.QMessageBox.warning(
                self, translate("Wizard", "Nom invalide"),
                translate("Wizard", "Le nom ne peut pas être vide."))
            return False
        try:
            existing = [config.get_params()["index"].GetString(str(i))
                        for i in config.get_index_list()]
        except Exception:
            existing = []
        if name in existing:
            QtGui.QMessageBox.warning(
                self, translate("Wizard", "Nom déjà utilisé"),
                translate("Wizard", "Un menu portant ce nom existe déjà."))
            return False
        return True


class ToolsPage(QWizardPage):
    def __init__(self):
        super().__init__()
        self.setTitle(translate("Wizard", "Outils"))
        layout = QVBoxLayout(self)

        self.radio_template = QRadioButton(
            translate("Wizard", "Modèle prêt à l'emploi"))
        self.radio_manual = QRadioButton(
            translate("Wizard", "Sélection manuelle"))
        self.radio_empty = QRadioButton(
            translate("Wizard", "Menu vide (à remplir plus tard)"))
        self.radio_template.setChecked(True)

        group = QButtonGroup(self)
        group.addButton(self.radio_template)
        group.addButton(self.radio_manual)
        group.addButton(self.radio_empty)

        layout.addWidget(self.radio_template)
        self.template_combo = QComboBox()
        for label, _wb, _tools in TEMPLATES:
            self.template_combo.addItem(label)
        layout.addWidget(self.template_combo)

        self.template_preview = QListWidget()
        self.template_preview.setEnabled(False)
        self.template_preview.setMaximumHeight(120)
        layout.addWidget(self.template_preview)

        layout.addWidget(self.radio_manual)
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText(
            translate("Wizard", "Rechercher une commande…"))
        self.search_edit.setEnabled(False)
        layout.addWidget(self.search_edit)

        self.tool_list = QListWidget()
        self.tool_list.setEnabled(False)
        self.tool_list.setSelectionMode(QListWidget.MultiSelection)
        layout.addWidget(self.tool_list)

        self.selected_count_label = QLabel(translate("Wizard", "0 outil(s) sélectionné(s)"))
        layout.addWidget(self.selected_count_label)

        layout.addWidget(self.radio_empty)
        layout.addStretch(1)

        self.radio_template.toggled.connect(self._on_mode_changed)
        self.radio_manual.toggled.connect(self._on_mode_changed)
        self.radio_empty.toggled.connect(self._on_mode_changed)
        self.search_edit.textChanged.connect(self._filter_tools)
        self.template_combo.currentIndexChanged.connect(self._update_template_preview)

        self._all_tools = []
        self._populate_tools()
        self.tool_list.itemChanged.connect(self._update_selected_count)
        self._update_template_preview()

    def _populate_tools(self):
        """Fill the manual tool list from the available action map."""
        try:
            action_map = menus_ui.get_gui_action_map_all() if hasattr(menus_ui, "get_gui_action_map_all") else None
        except Exception:
            action_map = None
        if action_map is None:
            try:
                from piemenu.workbench import get_gui_action_map_all as _g
                action_map = _g()
            except Exception:
                action_map = {}
        self._all_tools = sorted(action_map.keys()) if action_map else []
        self._action_map = action_map or {}
        self._refresh_tool_list("")
        self.tool_list.itemChanged.connect(self._update_selected_count)
        self._update_template_preview()

    def _refresh_tool_list(self, query):
        self.tool_list.clear()
        q = query.lower()
        for name in self._all_tools:
            if q and q not in name.lower():
                continue
            item = QListWidgetItem(name)
            item.setFlags(item.flags() | QtCore.Qt.ItemIsUserCheckable)
            item.setCheckState(QtCore.Qt.Unchecked)
            action = self._action_map.get(name)
            if action is not None:
                try:
                    item.setIcon(action.icon())
                except Exception:
                    pass
            self.tool_list.addItem(item)

    def _filter_tools(self, text):
        self._refresh_tool_list(text)

    def _update_selected_count(self, _item=None):
        n = sum(1 for i in range(self.tool_list.count())
                if self.tool_list.item(i).checkState() == QtCore.Qt.Checked)
        self.selected_count_label.setText(
            translate("Wizard", "%d outil(s) sélectionné(s)") % n)

    def _on_mode_changed(self):
        template = self.radio_template.isChecked()
        manual = self.radio_manual.isChecked()
        self.template_combo.setEnabled(template)
        self.search_edit.setEnabled(manual)
        self.tool_list.setEnabled(manual)
        self._update_template_preview()

    def _update_template_preview(self):
        """Show the tools of the selected template."""
        self.template_preview.clear()
        idx = self.template_combo.currentIndex()
        templates = TEMPLATES
        if idx < 0 or idx >= len(templates):
            return
        _label, _wb, tools = templates[idx]
        try:
            from piemenu.workbench import get_gui_action_map_all as _g
            amap = _g()
        except Exception:
            amap = {}
        for name in tools:
            item = QListWidgetItem(name)
            action = amap.get(name)
            if action is not None:
                try:
                    item.setIcon(action.icon())
                except Exception:
                    pass
            self.template_preview.addItem(item)
        if not tools:
            self.template_preview.addItem(translate("Wizard", "(aucun outil)"))

    def selected_tools(self):
        """Return the list of tool names chosen by the user."""
        if self.radio_template.isChecked():
            idx = self.template_combo.currentIndex()
            if 0 <= idx < len(TEMPLATES):
                return list(TEMPLATES[idx][2])
            return []
        if self.radio_empty.isChecked():
            return []
        tools = []
        for i in range(self.tool_list.count()):
            item = self.tool_list.item(i)
            if item.checkState() == QtCore.Qt.Checked:
                tools.append(item.text())
        return tools

    def validatePage(self):
        if self.radio_manual.isChecked() and not self.selected_tools():
            QtGui.QMessageBox.warning(
                self, translate("Wizard", "Aucun outil"),
                translate("Wizard", "Sélectionnez au moins un outil, ou choisissez un modèle."))
            return False
        return True


class ShortcutPage(QWizardPage):
    def __init__(self):
        super().__init__()
        self.setTitle(translate("Wizard", "Raccourcio (optionnel)"))
        layout = QVBoxLayout(self)

        self.enable_shortcut = QtGui.QCheckBox(
            translate("Wizard", "Activer un raccourcio global pour ouvrir ce menu"))
        self.enable_shortcut.setChecked(True)
        layout.addWidget(self.enable_shortcut)

        form = QFormLayout()
        self.shortcut_edit = QLineEdit("Tab")
        form.addRow(translate("Wizard", "Touche :"), self.shortcut_edit)
        layout.addLayout(form)

        hint = QLabel(translate(
            "Wizard",
            "Vous pourrez modifier le raccourcio plus tard dans les préférences."))
        hint.setWordWrap(True)
        layout.addWidget(hint)
        layout.addStretch(1)


class SummaryPage(QWizardPage):
    def __init__(self):
        super().__init__()
        self.setTitle(translate("Wizard", "Terminé"))
        self.setFinalPage(True)
        layout = QVBoxLayout(self)
        self.summary = QLabel()
        self.summary.setWordWrap(True)
        layout.addWidget(self.summary)

        self.preview_label = QLabel(translate("Wizard", "Aperçu des outils :"))
        layout.addWidget(self.preview_label)
        self.preview_list = QListWidget()
        self.preview_list.setEnabled(False)
        self.preview_list.setMaximumHeight(200)
        layout.addWidget(self.preview_list)

        hint = QLabel(translate(
            "Wizard",
            "Le menu radial complet sera visible dans les préférences après création."))
        hint.setWordWrap(True)
        layout.addWidget(hint)
        layout.addStretch(1)

        self._pie_created_here = False
        self._created_group = None
        self._created_name = None

    def initializePage(self):
        name = self.wizard().field("pieName")
        shape = self.wizard().field("pieShape")
        tools_page = self.wizard().page(2)
        tools = tools_page.selected_tools() if tools_page else []
        ntools = len(tools)
        self.summary.setText(translate(
            "Wizard",
            "Menu « %s »\nForme : %s\nOutils : %d"
            % (name, shape, ntools)))

        self.preview_list.clear()
        try:
            from piemenu.workbench import get_gui_action_map_all as _g
            amap = _g()
        except Exception:
            amap = {}
        for name_tool in tools:
            item = QListWidgetItem(name_tool)
            action = amap.get(name_tool)
            if action is not None:
                try:
                    item.setIcon(action.icon())
                except Exception:
                    pass
            self.preview_list.addItem(item)
        if not tools:
            self.preview_list.addItem(translate("Wizard", "(aucun outil)"))

        # create the pie early so accept() can finalize it
        if not self._pie_created_here:
            from piemenu import state
            state.app_state.wizard_running = True
            try:
                group = menus_ui.create_pie(name)
                self._pie_created_here = True
                self._created_name = name
                self._created_group = group
            except Exception as exc:
                from piemenu import log
                log.log_error("wizard: create_pie failed", exc)
            finally:
                state.app_state.wizard_running = False

    def cleanupPage(self):
        pass


class FirstRunWizard(QWizard):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(translate("Wizard", "Assistant de configuration PieMenu"))
        self.setWizardStyle(QWizard.ModernStyle)
        self.addPage(WelcomePage())
        self.addPage(NameShapePage())
        self.addPage(ToolsPage())
        self.addPage(ShortcutPage())
        self.addPage(SummaryPage())

    def reject(self):
        summary_page = self.page(4)
        if summary_page is not None and getattr(summary_page, "_pie_created_here", False):
            try:
                menus_ui.on_button_remove_pie_menu()
            except Exception:
                pass
        super().reject()

    def accept(self):
        if getattr(self, "_accepted", False):
            return
        self._accepted = True
        try:
            name = self.field("pieName").strip()
            shape = self.field("pieShape")
            tools_page = self.page(2)
            tools = tools_page.selected_tools() if tools_page else []
            shortcut_page = self.page(3)
            enable_sc = shortcut_page.enable_shortcut.isChecked() if shortcut_page else True
            shortcut_key = shortcut_page.shortcut_edit.text().strip() if shortcut_page else "Tab"

            summary_page = self.page(4)
            group = getattr(summary_page, "_created_group", None) if summary_page else None
            if group is None:
                from piemenu import state
                state.app_state.wizard_running = True
                try:
                    group = menus_ui.create_pie(name)
                finally:
                    state.app_state.wizard_running = False
                from piemenu.defaults import set_default_values
                set_default_values(group)

            group.SetString(constants.PARAM_SHAPE, shape)
            if tools:
                group.SetString(constants.PARAM_TOOL_LIST, ".,.".join(tools))
            if enable_sc and shortcut_key:
                group.SetString(constants.PARAM_SHORTCUT_KEY, shortcut_key)

            menus_ui.c_box_update(name)
            menus_ui.on_pie_change()
            menus_ui.create_nested_pie_menus()
            menus_ui.reload_workbench()
            from piemenu import log
            log.log_warning("first-run wizard created pie '%s'" % name)
        except Exception as exc:
            from piemenu import log
            log.log_error("first-run wizard failed", exc)
            QtGui.QMessageBox.critical(
                self, translate("Wizard", "Erreur"),
                translate("Wizard", "La creation du menu a echoue : %s") % exc)
            return
        super().accept()


def show_wizard(parent=None):
    """Show the first-run wizard (modal). Returns True if a pie was created."""
    wiz = FirstRunWizard(parent)
    result = wiz.exec_()
    return result == QWizard.Accepted


def maybe_show(parent=None):
    """Show the wizard only if no PieMenu exists yet."""
    try:
        pies = get_index_list()
        if pies:
            return False
    except Exception:
        pass
    return show_wizard(parent)