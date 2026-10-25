"""Tests for the piemenu.log helpers (no GUI required)."""

import unittest

from piemenu import log


class TestLog(unittest.TestCase):
    def test_log_error_without_exception(self):
        # Must never raise, whatever the environment (GUI, headless, tests).
        log.log_error("test context")

    def test_log_error_with_exception(self):
        log.log_error("test context", ValueError("boom"))

    def test_log_warning_without_exception(self):
        log.log_warning("test context")

    def test_log_warning_with_exception(self):
        log.log_warning("test context", KeyError("missing"))

    def test_log_warning_once_deduplicates(self):
        calls = []
        original = log.log_warning
        log.log_warning = lambda context, exc=None: calls.append(context)
        try:
            log.log_warning_once("same-key", "first time")
            log.log_warning_once("same-key", "repeated")
            log.log_warning_once("other-key", "second key")
        finally:
            log.log_warning = original
        self.assertEqual(calls, ["first time", "second key"])


if __name__ == "__main__":
    unittest.main()
