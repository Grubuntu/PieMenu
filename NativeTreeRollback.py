# -*- coding: utf-8 -*-
"""Rollback bar aligned with FreeCAD's native model tree.

Instead of a separate panel, this overlays a draggable bar on top of FreeCAD's
own model tree view, so the bar sits exactly on the rows of the Body's
features. It reuses the same preview/commit transaction logic.
"""
import FreeCAD
try:
    import FreeCADGui as Gui
except Exception:
    Gui = None

from PySide import QtGui, QtCore

# reuse helpers from RollbackPanel if available
try:
    from RollbackPanel import (active_body, body_features, target_for_row,
                               feature_index, recompute_doc, set_visibility)
except Exception:
    # fallback minimal helpers
    def active_body():
        doc = FreeCAD.ActiveDocument
        if not doc:
            return None
        try:
            sel = Gui.Selection.getSelection() if Gui else []
        except Exception:
            sel = []
        for o in sel:
            if getattr(o, "isDerivedFrom", lambda x: False)("PartDesign::Body"):
                return o
        ao = getattr(doc, "ActiveObject", None)
        if getattr(ao, "isDerivedFrom", lambda x: False)("PartDesign::Body"):
            return ao
        for o in doc.Objects:
            if getattr(o, "isDerivedFrom", lambda x: False)("PartDesign::Body"):
                return o
        return None

    def body_features(body):
        return list(getattr(body, "Group", []) or [])

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
            if vo is not None:
                try:
                    vo.Visibility = (f.Name == tip_name)
                except Exception:
                    pass

    def target_for_row(features, row):
        if not features:
            return None
        row = max(0, min(len(features) - 1, row))
        for i in range(row, -1, -1):
            f = features[i]
            try:
                if f.isDerivedFrom("PartDesign::Feature"):
                    return f
            except Exception:
                pass
        return features[0]


def find_tree_view():
    if Gui is None:
        return None
    mw = Gui.getMainWindow()
    # prefer a tree view inside a dock whose title mentions model/combo
    candidates = []
    for dock in mw.findChildren(QtGui.QDockWidget):
        title = (dock.windowTitle() or "").lower()
        if any(k in title for k in ("model", "modèle", "combo", "arbre", "tree")):
            for tv in dock.findChildren(QtGui.QTreeView):
                candidates.append(tv)
    if not candidates:
        candidates = mw.findChildren(QtGui.QTreeView)
    # pick the one with the most rows
    best = None
    best_rows = -1
    for tv in candidates:
        try:
            m = tv.model()
            rows = m.rowCount(tv.rootIndex()) if m is not None else 0
        except Exception:
            rows = 0
        if rows > best_rows:
            best_rows = rows
            best = tv
    return best


class NativeBar(QtGui.QWidget):
    def __init__(self, tree):
        super().__init__(tree.viewport())
        self.tree = tree
        self.dragging = False
        self.ending = False
        self.applying = False
        self.bar_y_override = None
        self.body = None
        self.features = []
        self.feature_indices = {}   # name -> QModelIndex
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
        self._update_timer = QtCore.QTimer(self)
        self._update_timer.setInterval(800)
        self._update_timer.timeout.connect(self._auto_update)
        self._update_timer.start()
        self.setMouseTracking(True)
        self._connect_tree()
        self.update_bar()

    # -- tree wiring ------------------------------------------------------- #
    def _connect_tree(self):
        try:
            self.tree.verticalScrollBar().valueChanged.connect(self.update_bar)
        except Exception:
            pass
        for sig_name in ("expanded", "collapsed"):
            sig = getattr(self.tree, sig_name, None)
            if sig is not None:
                try:
                    sig.connect(lambda *a: self.update_bar())
                except Exception:
                    pass
        try:
            self.tree.model().dataChanged.connect(lambda *a: self.update_bar())
        except Exception:
            pass
        try:
            self.tree.model().rowsInserted.connect(lambda *a: self.update_bar())
            self.tree.model().rowsRemoved.connect(lambda *a: self.update_bar())
        except Exception:
            pass

    def _auto_update(self):
        if not self.dragging:
            self.update_bar()

    # -- mapping ----------------------------------------------------------- #
    def _map_features(self):
        body = active_body()
        self.body = body
        self.features = body_features(body) if body is not None else []
        self.feature_indices = {}
        if body is None or not self.features:
            return
        model = self.tree.model()
        if model is None:
            return
        root = self.tree.rootIndex()
        for f in self.features:
            try:
                matches = model.match(root, QtCore.Qt.DisplayRole, f.Name, 1,
                                     QtCore.Qt.MatchExactly | QtCore.Qt.MatchRecursive)
                if not matches:
                    matches = model.match(root, QtCore.Qt.DisplayRole, f.Name, 1,
                                         QtCore.Qt.MatchContains | QtCore.Qt.MatchRecursive)
                if matches:
                    self.feature_indices[f.Name] = matches[0]
            except Exception:
                pass

    def _feature_rects(self):
        """Return list of (feature, QRect) for visible features."""
        out = []
        for f in self.features:
            idx = self.feature_indices.get(f.Name)
            if idx is None or not idx.isValid():
                continue
            try:
                r = self.tree.visualRect(idx)
            except Exception:
                r = QtCore.QRect()
            if r.isValid() and r.height() > 0:
                out.append((f, r))
        return out

    # -- geometry ---------------------------------------------------------- #
    def update_bar(self):
        self._map_features()
        vp = self.tree.viewport()
        self.setGeometry(0, 0, vp.width(), vp.height())
        self.update()

    def paintEvent(self, event):
        rects = self._feature_rects()
        if not rects or self.body is None:
            return
        # determine resting row
        if self.dragging and self.bar_y_override is not None:
            y = self.bar_y_override
        else:
            # rest below wanted_row
            if self.wanted_tip is not None:
                wr = feature_index(self.features, self.wanted_tip)
            else:
                idx = feature_index(self.features, self.body.Tip) if self.body else -1
                wr = idx if idx >= 0 else len(self.features) - 1
            wr = max(0, min(len(rects) - 1, wr))
            # find rect for that feature
            r = rects[wr][1] if wr < len(rects) else rects[-1][1]
            y = r.bottom() + 2
            # gap to next
            if wr + 1 < len(rects):
                y = (r.bottom() + rects[wr + 1][1].top()) // 2
        y = max(6, min(self.height() - 6, y))
        p = QtGui.QPainter(self)
        p.setRenderHint(QtGui.QPainter.Antialiasing)
        pen = QtGui.QPen(QtGui.QColor(80, 160, 255), 2)
        p.setPen(pen)
        p.drawLine(8, y, self.width() - 8, y)
        p.setBrush(QtGui.QBrush(QtGui.QColor(80, 160, 255)))
        p.setPen(QtCore.Qt.NoPen)
        p.drawEllipse(QtCore.QPoint(6, y), 5, 5)
        p.drawEllipse(QtCore.QPoint(self.width() - 6, y), 5, 5)
        p.end()

    # -- drag -------------------------------------------------------------- #
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
        self.wanted_tip = self.features[self.wanted_row] if self.wanted_row < len(self.features) else None
        doc = body.Document
        try:
            doc.openTransaction("Move tip (native tree bar)")
        except Exception:
            FreeCAD.Console.PrintError("could not open transaction\n")

    def _update_wanted(self, y):
        rects = self._feature_rects()
        if not rects:
            return
        # find feature at or before y
        row = 0
        for i, (f, r) in enumerate(rects):
            if y >= r.top():
                row = i
            else:
                break
        row = max(0, min(len(rects) - 1, row))
        self.wanted_row = row
        new_tip = rects[row][0] if row < len(rects) else None
        # map to target_for_row semantics: last feature at or before row
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
        self.feature_indices = {}
        self.update_bar()

    def _finish_pending(self):
        commit = self._pending_finish
        self._pending_finish = None
        if commit is not None:
            self._end_drag(commit)

    def cancel(self):
        if self.dragging:
            self._end_drag(commit=False)


# singleton
_bar = None


def show():
    global _bar
    if Gui is None:
        FreeCAD.Console.PrintError("Interface graphique requise.\n")
        return None
    tree = find_tree_view()
    if tree is None:
        FreeCAD.Console.PrintError("Arbre FreeCAD introuvable.\n")
        return None
    if _bar is not None:
        try:
            _bar.update_bar()
            _bar.show()
            return _bar
        except Exception:
            _bar = None
    _bar = NativeBar(tree)
    _bar.show()
    return _bar


show()
