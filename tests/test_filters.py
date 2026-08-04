import pytest
import logging
from EasyLoggerAJM.logger_parts import ConsoleOneTimeFilter

def test_console_one_time_filter():
    filt = ConsoleOneTimeFilter()
    record1 = logging.LogRecord("test", logging.WARNING, "path", 1, "Repeated message", None, None)
    record2 = logging.LogRecord("test", logging.WARNING, "path", 1, "Repeated message", None, None)
    record3 = logging.LogRecord("test", logging.WARNING, "path", 1, "Different message", None, None)
    
    assert filt.filter(record1) is True
    assert filt.filter(record2) is False # Same message, should be filtered out
    assert filt.filter(record3) is True # Different message, should pass
