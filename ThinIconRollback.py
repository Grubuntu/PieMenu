# -*- coding: utf-8 -*-
"""Thin icon-only rollback column synchronized with the Combo View tree.

Shows only icons (no text) for a PartDesign Body's features, as narrow as
possible, with a draggable rollback bar. Tries to stay aligned with the
Combo View's tree (scroll + selection).
"""
import FreeCAD
try:
    import FreeCADGui as Gui
except Exception:
    Gui = None

from PySide import QtGui, QtCore

# reuse helpers
try:
    from RollbackPanel import (active_body, body_features, target_for_row,
                               feature_index, recompute_doc, set_visibility)
except Exception:
    from NativeTreeRollback import (active_body, body_features, target_for_row,
                                   feature_index, recompute_doc, set_visibility)


def find_combo_tree():
    if Gui is None:
        return None
    mw = Gui.getMainWindow()
    # Combo View dock
    for dock in mw.findChildren(QtGui.QDockWidget):
        title = (dock.windowTitle() or "").lower()
        if "combo" in title:
            for tv in dock.findChildren(QtGui.QTreeView):
                return tv
    # fallback: any tree view with many rows
    best, best_rows = None, -1
    for tv in mw.findChildren(QtGui.QTreeView):
        try:
            m = tv.model()
            rows = m.rowCount(tv.rootIndex()) if m is not None else 0
        except Exception:
            rows = 0
        if rows > best_rows:
            best_rows = rows
            best = tv
    return best


class ThinIconColumn(QtGui.QDockWidget):
    def __init__(self, parent=None):
        super().__init__("Rollback (icons)", parent)
        self.setObjectName("ThinIconRollback")
        self.setFixedWidth(44)
        w = QtGui.QWidget()
        self.setWidget(w)
        layout = QtGui.QVBoxLayout(w)
        layout.setContentsMargins(2, 2, 2, 2)
        layout.setSpacing(0)

        self.list = QtGui.QListWidget()
        self.list.setIconSize(QtCore.QSize(20, 20))
        self.list.setSpacing(0)
        self.list.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        layout.addWidget(self.list)

        self.bar = None  # created after
        self.body = None
        self.features = []

        self._combo = find_combo_tree()
        if self._combo is not None:
            try:
                self._combo.verticalScrollBar().valueChanged.connect(self._sync_scroll)
            except Exception:
                pass
            try:
                sm = self._combo.selectionModel()
                if sm is not None:
                    sm.selectionChanged.connect(self._sync_selection)
            except Exception:
                pass
            try:
                self._combo.expanded.connect(lambda *a: self._sync_scroll())
                self._combo.collapsed.connect(lambda *a: self._sync_scroll())
            except Exception:
                pass

        self.bar = BarOverlay(self)
        self.list.viewport().installEventFilter(self)
        try:
            self.list.verticalScrollBar().valueChanged.connect(self.bar.update_geometry)
        except Exception:
            pass
        try:
            self.list.itemClicked.connect(self._toggle_expand)
        except Exception:
            pass

        self._timer = QtCore.QTimer(self)
        self._timer.setInterval(1200)
        self._timer.timeout.connect(self._auto_refresh)
        self._timer.start()

        self.refresh()

    # -- sync with combo view ---------------------------------------------- #
    def _combo_feature_rects(self):
        if self._combo is None:
            return []
        out = []
        model = self._combo.model()
        if model is None:
            return out
        root = self._combo.rootIndex()
        for f in self.features:
            try:
                matches = model.match(root, QtCore.Qt.DisplayRole, f.Name, 1,
                                     QtCore.Qt.MatchExactly | QtCore.Qt.MatchRecursive)
                if not matches:
                    matches = model.match(root, QtCore.Qt.DisplayRole, f.Name, 1,
                                         QtCore.Qt.MatchContains | QtCore.Qt.MatchRecursive)
                if matches:
                    idx = matches[0]
                    r = self._combo.visualRect(idx)
                    if r.isValid() and r.height() > 0:
                        out.append((f, r))
            except Exception:
                pass
        return out

    def _sync_scroll(self):
        rects = self._combo_feature_rects()
        if not rects:
            return
        vp = self._combo.viewport()
        # find first visible feature rect
        first_visible = None
        for f, r in rects:
            if r.bottom() > 0 and r.top() < vp.height():
                first_visible = f
                break
        if first_visible is None:
            return
        # scroll our list so that item is at top
        for i in range(self.list.count()):
            it = self.list.item(i)
            if it is not None and it.data(QtCore.Qt.UserRole) == first_visible.Name:
                self.list.scrollToItem(it, QtGui.QAbstractItemView.PositionAtTop)
                break
        self._sync_visibility()
        self.bar.update_geometry()

    def _sync_selection(self):
        if self._combo is None:
            return
        try:
            idxs = self._combo.selectedIndexes()
        except Exception:
            idxs = []
        if not idxs:
            return
        name = idxs[0].data(QtCore.Qt.DisplayRole)
        for i in range(self.list.count()):
            it = self.list.item(i)
            if it is not None and it.data(QtCore.Qt.UserRole) == name:
                self.list.setCurrentRow(i)
                break

    def _toggle_expand(self, item):
        if self._combo is None or item is None:
            return
        name = item.data(QtCore.Qt.UserRole)
        model = self._combo.model()
        root = self._combo.rootIndex()
        try:
            matches = model.match(root, QtCore.Qt.DisplayRole, name, 1,
                                 QtCore.Qt.MatchExactly | QtCore.Qt.MatchRecursive)
            if not matches:
                return
            idx = matches[0]
        except Exception:
            return
        try:
            if self._combo.isExpanded(idx):
                self._combo.collapse(idx)
            else:
                self._combo.expand(idx)
        except Exception:
            pass
        self._sync_visibility()

    def _sync_visibility(self):
        if self._combo is None:
            return
        rects = self._combo_feature_rects()
        if not rects:
            # Ne pas masquer si on n'a pas pu repérer les lignes (evite barre vide)
            for i in range(self.list.count()):
                it = self.list.item(i)
                if it is not None:
                    it.setHidden(False)
            if self.bar is not None:
                self.bar.update_geometry()
            return
        visible_names = {f.Name for f, r in rects}
        for i in range(self.list.count()):
            it = self.list.item(i)
            if it is None:
                continue
            name = it.data(QtCore.Qt.UserRole)
            it.setHidden(name not in visible_names)
        if self.bar is not None:
            self.bar.update_geometry()

    # -- refresh ----------------------------------------------------------- #
    def _auto_refresh(self):
        if self.bar.dragging:
            return
        self.refresh(silent=True)

    def refresh(self, silent=False):
        body = active_body()
        self.body = body
        if body is None:
            self.body_label = None
            self.list.clear()
            self.features = []
            if self.bar is not None:
                self.bar.features = []
                self.bar.update()
            return
        feats = body_features(body)
        current = [self.list.item(i).data(QtCore.Qt.UserRole)
                   for i in range(self.list.count())]
        new = [f.Name for f in feats]
        if current != new or not silent:
            self.list.clear()
            for f in feats:
                item = QtGui.QListWidgetItem()
                item.setData(QtCore.Qt.UserRole, f.Name)
                vo = getattr(f, "ViewObject", None)
                icon_path = getattr(vo, "Icon", None) if vo is not None else None
                if icon_path:
                    try:
                        item.setIcon(QtGui.QIcon(icon_path))
                    except Exception:
                        pass
                item.setToolTip(f.Name)
                item.setText("")
                self.list.addItem(item)
        self.features = feats
        if self.bar is not None:
            self.bar.features = feats
            self.bar.body = body
            self.bar.update_geometry()
            self.bar.update()
        self._sync_visibility()
        self._sync_scroll()

    def eventFilter(self, obj, event):
        if obj is self.list.viewport():
            if event.type() in (QtCore.QEvent.Resize, QtCore.QEvent.Show):
                if self.bar is not None:
                    self.bar.update_geometry()
        return super().eventFilter(obj, event)

    def showEvent(self, event):
        super().showEvent(event)
        if self.bar is not None:
            self.bar.update_geometry()


# --------------------------------------------------------------------------- #
# overlay bar (reused logic, icon-only column)
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
        self.update_geometry()

    def update_geometry(self):
        vp = self.panel.list.viewport()
        self.setGeometry(0, 0, vp.width(), vp.height())
        self.update()

    def paintEvent(self, event):
        if not self.features:
            return
        if self.bar_y_override is not None and self.dragging:
            y = self.bar_y_override
        else:
            if self.wanted_tip is not None:
                wr = feature_index(self.features, self.wanted_tip)
            else:
                idx = feature_index(self.features, self.body.Tip) if self.body else -1
                wr = idx if idx >= 0 else len(self.features) - 1
            wr = max(0, min(len(self.features) - 1, wr))
            item = self.panel.list.item(wr)
            if item is None:
                y = self.height() // 2
            else:
                rect = self.panel.list.visualItemRect(item)
                y = rect.bottom() + 2
                if wr + 1 < self.panel.list.count():
                    nr = self.panel.list.visualItemRect(self.panel.list.item(wr + 1))
                    if nr.isValid():
                        y = (rect.bottom() + nr.top()) // 2
        y = max(4, min(self.height() - 4, y))
        p = QtGui.QPainter(self)
        p.setRenderHint(QtGui.QPainter.Antialiasing)
        pen = QtGui.QPen(QtGui.QColor(80, 160, 255), 2)
        p.setPen(pen)
        p.drawLine(4, y, self.width() - 4, y)
        p.setBrush(QtGui.QBrush(QtGui.QColor(80, 160, 255)))
        p.setPen(QtCore.Qt.NoPen)
        p.drawEllipse(QtCore.QPoint(4, y), 3, 3)
        p.drawEllipse(QtCore.QPoint(self.width() - 4, y), 3, 3)
        p.end()

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
            doc.openTransaction("Move tip (thin icon column)")
        except Exception:
            FreeCAD.Console.PrintError("could not open transaction\n")

    def _update_wanted(self, y):
        # find nearest item row by vertical position
        row = 0
        for i in range(self.panel.list.count()):
            item = self.panel.list.item(i)
            if item is None:
                continue
            rect = self.panel.list.visualItemRect(item)
            if not rect.isValid():
                continue
            if y >= rect.top():
                row = i
            else:
                break
        row = max(0, min(len(self.features) - 1, row))
        self.wanted_row = row
        new_tip = target_for_row(self.features, row)
        if new_tip is None:
            return
        if self.wanted_tip is not None and new_tip.Name == self.wanted_tip.Name:
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
        if (self.dragging and not self.ending and self.wanted_tip is not None
                and (self.current_tip is None
                     or self.wanted_tip.Name != self.current_tip.Name)):
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


_singleton = None


def show():
    global _singleton
    if Gui is None:
        FreeCAD.Console.PrintError("Interface graphique requise.\n")
        return None
    if _singleton is not None:
        try:
            _singleton.show()
            _singleton.raise_()
            _singleton.refresh()
            return _singleton
        except Exception:
            _singleton = None
    panel = ThinIconColumn(Gui.getMainWindow())
    _singleton = panel
    Gui.getMainWindow().addDockWidget(QtCore.Qt.RightDockWidgetArea, panel)
    panel.show()
    return panel


show()
