import pytest
import logging
from io import StringIO
import sys
from EasyLoggerAJM.logger_parts.handlers import StreamHandlerIgnoreExecInfo

@pytest.fixture
def stream():
    return StringIO()

@pytest.fixture
def handler(stream):
    h = StreamHandlerIgnoreExecInfo(stream)
    yield h
    h.close()

def test_emit_without_exc_info(handler, stream):
    record = logging.LogRecord("my_logger", logging.INFO, "dummy_path", 0, "Hello, world!", None, None)
    handler.emit(record)
    assert stream.getvalue() == "Hello, world!\n"

def test_emit_with_exc_info(handler, stream):
    try:
        raise Exception("This is a dummy exception")
    except Exception:
        record = logging.LogRecord("my_logger", logging.ERROR, "dummy_path", 0,
                                   "An error has occurred!", None, sys.exc_info())
    
    handler.emit(record)
    # The exception info should NOT be in the output
    assert "This is a dummy exception" not in stream.getvalue()
    assert "An error has occurred!" in stream.getvalue()

def test_emit_restores_exc_info(handler, stream):
    try:
        raise Exception("This is another dummy exception")
    except Exception:
        exc_info = sys.exc_info()
        record = logging.LogRecord("my_logger", logging.ERROR, "dummy_path", 0,
                                   "Another error has occurred!", None, exc_info)
        
        handler.emit(record)
        assert record.exc_info == exc_info
