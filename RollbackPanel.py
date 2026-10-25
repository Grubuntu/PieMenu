# -*- coding: utf-8 -*-
"""Custom model panel with a draggable rollback bar for PartDesign Bodies.

This is a self-contained FreeCAD macro/addon module. It does not replace
FreeCAD's native tree; it adds a docked panel that lists a Body's features
in creation order and lets you drag a bar to move the Tip (rollback) with
live preview, a single undo step and re-entrancy handling, inspired by
FreeCAD-Nxt's rollback bar.
"""
import FreeCAD
try:
    import FreeCADGui as Gui
except Exception:
    Gui = None

from PySide import QtGui, QtCore

# --------------------------------------------------------------------------- #
# helpers
# --------------------------------------------------------------------------- #
def active_body():
    doc = FreeCAD.ActiveDocument
    if not doc:
        return None
    try:
        sel = Gui.Selection.getSelection() if Gui else []
    except Exception:
        sel = []
    for o in sel:
        if _is_body(o):
            return o
    ao = getattr(doc, "ActiveObject", None)
    if _is_body(ao):
        return ao
    for o in doc.Objects:
        if _is_body(o):
            return o
    return None


def _is_body(o):
    try:
        return o is not None and o.isDerivedFrom("PartDesign::Body")
    except Exception:
        return False


def body_features(body):
    """Ordered list of objects belonging to the Body (creation order)."""
    try:
        return list(getattr(body, "Group", []) or [])
    except Exception:
        return []


def feature_index(features, obj):
    if obj is None:
        return -1
    for i, f in enumerate(features):
        if f.Name == getattr(obj, "Name", None):
            return i
    return -1


def recompute_doc(doc, body):
    try:
        doc.recompute([body])
    except TypeError:
        doc.recompute()
    except Exception:
        try:
            doc.recompute()
        except Exception:
            pass


def set_visibility(features, tip_name):
    for f in features:
        vo = getattr(f, "ViewObject", None)
        if vo is None:
            continue
        try:
            vo.Visibility = (f.Name == tip_name)
        except Exception:
            pass


def target_for_row(features, row):
    """Last feature at or before row that can be a Tip."""
    if not features:
        return None
    row = max(0, min(len(features) - 1, row))
    for i in range(row, -1, -1):
        f = features[i]
        # prefer solid-producing features; fall back to any object
        try:
            if f.isDerivedFrom("PartDesign::Feature"):
                return f
        except Exception:
            pass
    # fallback: first object
    return features[0]


# --------------------------------------------------------------------------- #
# overlay bar widget
# --------------------------------------------------------------------------- #
class BarOverlay(QtGui.QWidget):
    def __init__(self, panel):
        super().__init__(panel.list.viewport())
        self.panel = panel
        self.dragging = False
        self.ending = False
        self.applying = False
        self.bar_y_override = None
        self.body = None
        self.features = []
        self.original_tip = None
        self.current_tip = None
        self.wanted_tip = None
        self.wanted_row = 0
        self._drag_timer = QtCore.QTimer(self)
        self._drag_timer.setSingleShot(True)
        self._drag_timer.timeout.connect(self._drain)
        self._finish_timer = QtCore.QTimer(self)
        self._finish_timer.setSingleShot(True)
        self._finish_timer.timeout.connect(self._finish_pending)
        self._pending_finish = None
        self.setMouseTracking(True)
        self.setAttribute(QtCore.Qt.WA_NoSystemBackground, True)
        self.update_geometry()

    # -- painting ----------------------------------------------------------- #
    def paintEvent(self, event):
        if not self.features:
            return
        p = QtGui.QPainter(self)
        p.setRenderHint(QtGui.QPainter.Antialiasing)
        # line across viewport
        y = self._bar_y()
        pen = QtGui.QPen(QtGui.QColor(80, 160, 255), 2)
        p.setPen(pen)
        p.drawLine(8, y, self.width() - 8, y)
        # knobs
        knob = QtGui.QBrush(QtGui.QColor(80, 160, 255))
        p.setBrush(knob)
        p.setPen(QtCore.Qt.NoPen)
        p.drawEllipse(QtCore.QPoint(6, y), 5, 5)
        p.drawEllipse(QtCore.QPoint(self.width() - 6, y), 5, 5)
        p.end()

    def _bar_y(self):
        if self.bar_y_override is not None:
            return max(6, min(self.height() - 6, self.bar_y_override))
        # resting position: just below wanted row
        if not self.features:
            return self.height() // 2
        row = max(0, min(len(self.features) - 1, self.wanted_row))
        item = self.panel.list.item(row)
        if item is None:
            return self.height() // 2
        rect = self.panel.list.visualItemRect(item)
        if not rect.isValid():
            return self.height() // 2
        # gap below row
        next_top = rect.bottom() + 4
        if row + 1 < self.panel.list.count():
            nr = self.panel.list.visualItemRect(self.panel.list.item(row + 1))
            if nr.isValid():
                next_top = (rect.bottom() + nr.top()) // 2
        return max(6, min(self.height() - 6, next_top))

    def update_geometry(self):
        vp = self.panel.list.viewport()
        self.setGeometry(0, 0, vp.width(), vp.height())
        self.update()

    # -- drag handling ------------------------------------------------------ #
    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton and self.features:
            self.dragging = True
            self.ending = False
            self.bar_y_override = event.pos().y()
            self._begin_drag()
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.dragging:
            self.bar_y_override = event.pos().y()
            self._update_wanted(event.pos().y())
            self.update()
            event.accept()
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton and self.dragging:
            self._end_drag(commit=True)
            event.accept()
            return
        super().mouseReleaseEvent(event)

    def _begin_drag(self):
        body = active_body()
        if body is None or not body_features(body):
            self.dragging = False
            return
        self.body = body
        self.features = body_features(body)
        self.original_tip = body.Tip
        self.current_tip = body.Tip
        idx = feature_index(self.features, body.Tip)
        self.wanted_row = idx if idx >= 0 else len(self.features) - 1
        self.wanted_tip = (self.features[self.wanted_row]
                           if self.wanted_row < len(self.features) else None)
        doc = body.Document
        try:
            doc.openTransaction("Move tip (rollback bar)")
        except Exception:
            FreeCAD.Console.PrintError("could not open transaction\n")
        # freeze list refresh during drag handled by panel

    def _update_wanted(self, y):
        # determine row under pointer
        pt = QtCore.QPoint(5, y)
        item = self.panel.list.itemAt(pt)
        if item is None:
            if y < 20:
                row = 0
            else:
                row = len(self.features) - 1
        else:
            row = self.panel.list.row(item)
        row = max(0, min(len(self.features) - 1, row))
        self.wanted_row = row
        new_tip = target_for_row(self.features, row)
        if new_tip is None or (self.wanted_tip is not None
                               and new_tip.Name == self.wanted_tip.Name):
            return
        self.wanted_tip = new_tip
        if not self.applying:
            self._drag_timer.start()

    def _drain(self):
        if self.applying or not self.dragging or self.ending:
            return
        self.applying = True
        try:
            while (self.dragging and not self.ending
                   and self.wanted_tip is not None
                   and (self.current_tip is None
                        or self.wanted_tip.Name != self.current_tip.Name)):
                target = self.wanted_tip
                if not self._preview(target):
                    break
                self.current_tip = target
        finally:
            self.applying = False
        # if more moves arrived, schedule another pass
        if self.dragging and not self.ending and self.wanted_tip is not None and \
                (self.current_tip is None or self.wanted_tip.Name != self.current_tip.Name):
            self._drag_timer.start()

    def _preview(self, feature):
        if self.body is None or feature is None:
            return False
        try:
            set_visibility(self.features, feature.Name)
            recompute_doc(self.body.Document, self.body)
            return True
        except Exception as e:
            FreeCAD.Console.PrintError("preview failed: %s\n" % e)
            return False

    def _end_drag(self, commit):
        if not self.dragging:
            return
        if self.applying:
            self.ending = True
            self._pending_finish = commit
            self._finish_timer.start()
            return
        self.dragging = False
        self.ending = False
        body = self.body
        doc = body.Document if body else None
        try:
            if commit:
                wanted = self.wanted_tip
                if wanted is None or (self.original_tip is not None
                                      and wanted.Name == self.original_tip.Name):
                    if self.current_tip is not None and wanted is not None \
                            and self.current_tip.Name != wanted.Name:
                        self._preview(wanted)
                    if doc is not None:
                        try:
                            doc.abortTransaction()
                        except Exception:
                            pass
                else:
                    try:
                        body.Tip = doc.getObject(wanted.Name)
                        set_visibility(self.features, wanted.Name)
                        recompute_doc(doc, body)
                        if doc is not None:
                            doc.commitTransaction()
                    except Exception as e:
                        FreeCAD.Console.PrintError("commit failed: %s\n" % e)
                        self._preview(self.original_tip)
                        if doc is not None:
                            try:
                                doc.abortTransaction()
                            except Exception:
                                pass
            else:
                if doc is not None:
                    try:
                        doc.abortTransaction()
                    except Exception:
                        pass
                if self.current_tip is not None and self.original_tip is not None \
                        and self.current_tip.Name != self.original_tip.Name:
                    self._preview(self.original_tip)
        except Exception as e:
            FreeCAD.Console.PrintError("end_drag error: %s\n" % e)
        self.bar_y_override = None
        self.body = None
        self.features = []
        self.panel.refresh()

    def _finish_pending(self):
        commit = self._pending_finish
        self._pending_finish = None
        if commit is not None:
            self._end_drag(commit)

    def cancel(self):
        if self.dragging:
            self._end_drag(commit=False)


# --------------------------------------------------------------------------- #
# panel
# --------------------------------------------------------------------------- #
class RollbackPanel(QtGui.QDockWidget):
    def __init__(self, parent=None):
        super().__init__("Rollback bar (PartDesign)", parent)
        self.setObjectName("RollbackBarPanel")
        w = QtGui.QWidget()
        self.setWidget(w)
        layout = QtGui.QVBoxLayout(w)

        self.body_label = QtGui.QLabel("Body: -")
        layout.addWidget(self.body_label)

        self.list = QtGui.QListWidget()
        self.list.setIconSize(QtCore.QSize(16, 16))
        layout.addWidget(self.list)

        self.bar = BarOverlay(self)
        self.list.viewport().installEventFilter(self)
        self.list.verticalScrollBar().valueChanged.connect(self.bar.update_geometry)
        self.list.model().rowsInserted.connect(lambda *a: self.bar.update_geometry())
        self.list.model().rowsRemoved.connect(lambda *a: self.bar.update_geometry())
        self.list.model().dataChanged.connect(lambda *a: self.bar.update_geometry())

        opts = QtGui.QHBoxLayout()
        self.chk_hide = QtGui.QCheckBox("Masquer en aval")
        self.chk_gray = QtGui.QCheckBox("Griser en aval")
        opts.addWidget(self.chk_hide)
        opts.addWidget(self.chk_gray)
        layout.addLayout(opts)

        btns = QtGui.QHBoxLayout()
        self.btn_refresh = QtGui.QPushButton("Rafraîchir")
        self.btn_cancel = QtGui.QPushButton("Annuler le drag")
        btns.addWidget(self.btn_refresh)
        btns.addWidget(self.btn_cancel)
        layout.addLayout(btns)

        self.btn_refresh.clicked.connect(self.refresh)
        self.btn_cancel.clicked.connect(self.bar.cancel)

        self._refresh_timer = QtCore.QTimer(self)
        self._refresh_timer.setInterval(1500)
        self._refresh_timer.timeout.connect(self._auto_refresh)
        self._refresh_timer.start()

        self.refresh()

    def eventFilter(self, obj, event):
        if obj is self.list.viewport():
            if event.type() in (QtCore.QEvent.Resize, QtCore.QEvent.Show):
                self.bar.update_geometry()
            elif event.type() == QtCore.QEvent.Scroll:
                self.bar.update_geometry()
        return super().eventFilter(obj, event)

    def _auto_refresh(self):
        if self.bar.dragging:
            return
        self.refresh(silent=True)

    def refresh(self, silent=False):
        body = active_body()
        if body is None:
            self.body_label.setText("Body: (aucun)")
            self.list.clear()
            self.bar.features = []
            self.bar.update()
            return
        self.body_label.setText("Body: %s" % body.Name)
        feats = body_features(body)
        # only rebuild if changed
        current_names = [self.list.item(i).text() for i in range(self.list.count())]
        new_names = [f.Name for f in feats]
        if current_names != new_names or not silent:
            self.list.clear()
            for f in feats:
                item = QtGui.QListWidgetItem(f.Name)
                vo = getattr(f, "ViewObject", None)
                icon_path = getattr(vo, "Icon", None) if vo is not None else None
                if icon_path:
                    try:
                        item.setIcon(QtGui.QIcon(icon_path))
                    except Exception:
                        pass
                self.list.addItem(item)
        self.bar.features = feats
        self.bar.body = body
        self.bar.update_geometry()
        self.bar.update()

    def showEvent(self, event):
        super().showEvent(event)
        self.bar.update_geometry()


# --------------------------------------------------------------------------- #
# entry point
# --------------------------------------------------------------------------- #
def show():
    if Gui is None:
        FreeCAD.Console.PrintError("Interface graphique requise.\n")
        return None
    mw = Gui.getMainWindow()
    for dock in mw.findChildren(QtGui.QDockWidget):
        if dock.objectName() == "RollbackBarPanel":
            dock.show()
            dock.raise_()
            return dock
    panel = RollbackPanel(mw)
    mw.addDockWidget(QtCore.Qt.RightDockWidgetArea, panel)
    panel.show()
    return panel


show()
