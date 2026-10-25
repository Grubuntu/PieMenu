"""Lightweight error logging for PieMenu.

FreeCAD exposes ``FreeCAD.Console`` only in the GUI build; in headless or
test environments it may be absent, so every helper degrades gracefully.
"""

try:
    import FreeCAD as App
except Exception:  # pragma: no cover - FreeCAD always present at runtime
    App = None


def log_error(context, exc=None):
    """Print an error message to the FreeCAD console (or stderr as fallback)."""
    message = "PieMenu: %s" % context
    if exc is not None:
        message = "%s -> %r" % (message, exc)
    try:
        if App is not None and hasattr(App, "Console"):
            App.Console.PrintError(message + "\n")
            return
    except Exception:
        pass
    try:
        import sys
        sys.stderr.write(message + "\n")
    except Exception:
        pass


def log_warning(context, exc=None):
    message = "PieMenu: %s" % context
    if exc is not None:
        message = "%s -> %r" % (message, exc)
    try:
        if App is not None and hasattr(App, "Console"):
            App.Console.PrintWarning(message + "\n")
            return
    except Exception:
        pass
    try:
        import sys
        sys.stderr.write(message + "\n")
    except Exception:
        pass


_warned_once = set()


def log_warning_once(key, context, exc=None):
    """Like :func:`log_warning` but only for the first occurrence of ``key``.

    Used by paths that are retried on every pie menu refresh (workbench
    activation, icon refresh) so the console is not flooded with the same
    message during a session.
    """
    if key in _warned_once:
        return
    _warned_once.add(key)
    log_warning(context, exc)
