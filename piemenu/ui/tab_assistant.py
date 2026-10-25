"""Assistant panel for the preferences dialog.

A narrow side panel on the left of the PieMenu preferences window.

It does not duplicate any feature: it explains, in plain language, what the
view that is currently open is for, and gives step-by-step advice to a
beginner. No action buttons are shown: the user keeps using the existing
controls (the "+" button, the tabs, ...) described in the text.
"""

import FreeCAD as App
from PySide import QtCore, QtGui
from PySide.QtWidgets import (
    QLabel, QPushButton, QScrollArea, QVBoxLayout, QWidget,
)


def translate(context, text):
    return App.Qt.translate(context, text)


# Guidance for each view of the preferences dialog.
#
# The first entries follow the order in which the tabs are added in
# InitGui.py (PieMenu, Tools, Context, Global settings), so the index of a
# guide is also the index of the matching tab: the "goto_*" actions use it
# to switch tab. The last entry describes the "ToolBars" view, which
# replaces the tab widget.
GUIDES = [
    {
        "title": "PieMenu",
        "summary": "Un menu radial (PieMenu) est le menu circulaire qui "
                   "s'ouvre quand vous appuyez sur la touche globale (Tab par "
                   "défaut). Cette page sert à le choisir et le régler.",
        "steps": [
            "Choisissez un menu dans la liste déroulante en haut, ou "
            "cliquez sur « + » pour en créer un nouveau (le nom doit être "
            "unique).",
            "Cochez « Set this PieMenu as default » pour que ce menu "
            "s'ouvre par défaut, et choisissez l'atelier FreeCAD qui lui est "
            "lié (groupe « Assignment »).",
            "Dans le groupe « Shape », choisissez la forme visuelle du menu : "
            "Pie, Star, Table, UpDown…",
            "Réglez la taille du menu et la taille des boutons : plus grand "
            "= icônes plus lisibles.",
            "L'espacement des icônes et le nombre de colonnes s'adaptent à "
            "la forme choisie.",
            "Dans le groupe « Trigger mode », choisissez si le menu s'ouvre "
            "à l'appui ou au survol de la souris, et le délai de survol.",
            "Dans le groupe « Tools shortcuts », activez l'affichage des "
            "raccourcis clavier sur les boutons.",
            "L'aperçu en bas à droite se met à jour en direct : observez le "
            "résultat avant de valider.",
        ],
        "note": "Astuce : commencez par la forme « Pie », la plus simple, "
                "puis passez à la page « Tools » pour ajouter vos outils.",
        "actions": [],
    },
    {
        "title": "Tools",
        "summary": "Cette page sert à choisir les outils de votre menu.",
        "steps": [
            "Le menu sélectionné en haut (onglet PieMenu) est celui auquel "
            "les outils sont ajoutés.",
            "Cochez les outils que vous voulez dans votre menu, dans la "
            "liste.",
            "Tapez dans la barre de recherche pour trouver un outil "
            "rapidement.",
            "Utilisez les boutons sous la liste pour ajouter un séparateur, "
            "supprimer, déplacer un outil vers le haut ou vers le bas.",
            "Les outils cochés sont enregistrés avec le menu.",
        ],
        "note": "Astuce : un séparateur permet de grouper visuellement les "
                "outils dans le menu radial.",
        "actions": [],
    },
    {
        "title": "Context",
        "summary": "Le mode Context ouvre automatiquement un menu selon ce "
                   "que vous avez sélectionné dans la vue 3D.",
        "steps": [
            "Choisissez un menu dans la liste déroulante en haut (onglet "
            "PieMenu).",
            "Pour chaque type d'élément (sommet, arête, face, objet, axe, "
            "plan), choisissez la condition de déclenchement (==, !=, >=, "
            "...) et le nombre minimum.",
            "Cliquez sur « + » pour ajouter une règle (jusqu'à 4 règles), "
            "chacune activable séparément.",
            "Cochez « Immediate triggering » pour que le menu s'ouvre tout "
            "de suite quand les conditions sont remplies.",
            "Choisissez l'atelier associé aux conditions contextuelles.",
        ],
        "note": "Attention : ce mode n'est pas encore totalement stable et "
                "peut provoquer des comportements inattendus. Le mode "
                "Context est prioritaire sur les autres modes.",
        "actions": [],
    },
    {
        "title": "Global settings",
        "summary": "Cette page contient les réglages communs à tous les "
                   "menus.",
        "steps": [
            "Choisissez le thème (clair ou sombre) dans la liste déroulante.",
            "Cochez « Show QuickMenu » pour afficher le menu contextuel "
            "ajouté à FreeCAD.",
            "Cochez « Global context » pour activer le mode Context "
            "(prioritaire sur les autres modes).",
            "Cochez « Shortcuts behavior: Toggle » pour que la touche "
            "globale bascule l'affichage du menu.",
            "Cochez « Long right-click to open default PieMenu » pour "
            "ouvrir le menu par défaut avec un clic droit long.",
            "Cochez « Direct SpinBox display » pour afficher directement la "
            "boîte de spin.",
            "Assignez le raccourci global (Tab par défaut) avec le champ et "
            "le bouton « Assigner ».",
            "Utilisez « Export » / « Import » pour sauvegarder ou restaurer "
            "vos réglages.",
        ],
        "actions": [],
    },
    {
        "title": "ToolBars",
        "summary": "Cette page sert à ajouter une barre d'outils existante "
                   "de FreeCAD à votre menu.",
        "steps": [
            "Cliquez sur « Barres d'outils des Ateliers... » dans l'onglet "
            "PieMenu pour ouvrir cette vue.",
            "Sélectionnez une barre d'outils dans la liste.",
            "Cliquez sur « + » pour l'ajouter au menu courant.",
            "Cliquez sur « Retourner aux paramètres... » pour revenir aux "
            "réglages.",
        ],
        "actions": [],
    },
]

# Index of the guide describing the "ToolBars" view.
TOOLBAR_GUIDE_INDEX = len(GUIDES) - 1


def _clear_layout(layout):
    """Remove and delete every widget held by a layout."""
    while layout.count():
        item = layout.takeAt(0)
        widget = item.widget()
        if widget is not None:
            widget.setParent(None)
            widget.deleteLater()


class AssistantPanel(QWidget):
    """Guidance panel shown on the left of the preferences dialog."""

    def __init__(self, tabs=None, toolbar_view=None, parent=None):
        super().__init__(parent)
        self._tabs = tabs
        self._toolbar_view = toolbar_view

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(8, 8, 8, 8)
        content_layout.setSpacing(6)

        self.title_label = QLabel()
        title_font = self.title_label.font()
        title_font.setBold(True)
        self.title_label.setFont(title_font)
        content_layout.addWidget(self.title_label)

        self.summary_label = QLabel()
        self.summary_label.setWordWrap(True)
        content_layout.addWidget(self.summary_label)

        self.steps_layout = QVBoxLayout()
        self.steps_layout.setContentsMargins(0, 0, 0, 0)
        self.steps_layout.setSpacing(4)
        content_layout.addLayout(self.steps_layout)

        content_layout.addStretch(1)

        # The panel can be made narrow or short, so keep it scrollable.
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QtGui.QFrame.NoFrame)
        scroll.setWidget(content)
        outer.addWidget(scroll)

        if tabs is not None:
            tabs.currentChanged.connect(self.refresh)

    def current_guide_index(self):
        """Index in GUIDES of the view that is currently open."""
        if self._toolbar_view is not None and self._toolbar_view.isVisible():
            return TOOLBAR_GUIDE_INDEX
        if self._tabs is None:
            return 0
        return self._tabs.currentIndex()

    def refresh(self, *_args):
        """Show the guidance of the view that is currently open."""
        index = self.current_guide_index()
        guide = GUIDES[index] if 0 <= index < len(GUIDES) else None

        _clear_layout(self.steps_layout)

        if guide is None:
            self.title_label.setText(translate("AssistantTab", "Assistant"))
            self.summary_label.setText(
                translate("AssistantTab", "Aucune aide disponible."))
            return

        self.title_label.setText(translate("AssistantTab", guide["title"]))
        self.summary_label.setText(translate("AssistantTab", guide["summary"]))

        for number, step in enumerate(guide["steps"], 1):
            label = QLabel("%d. %s" % (
                number, translate("AssistantTab", step)))
            label.setWordWrap(True)
            self.steps_layout.addWidget(label)

        note = guide.get("note")
        if note:
            note_label = QLabel(translate("AssistantTab", note))
            note_label.setWordWrap(True)
            note_font = note_label.font()
            note_font.setItalic(True)
            note_label.setFont(note_font)
            self.steps_layout.addWidget(note_label)
def build(tabs=None, toolbar_view=None):
    """Build the assistant side panel of the preferences dialog.

    tabs: the QTabWidget of the preferences dialog, its current page
        drives the guidance.
    toolbar_view: the widget of the "ToolBars" view, shown instead of the
        tab widget.
    """
    panel = AssistantPanel(tabs=tabs, toolbar_view=toolbar_view)
    panel.refresh()
    return {
        "assistantTab": panel,
        "assistantPanel": panel,
    }
