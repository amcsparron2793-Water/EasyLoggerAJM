import pytest
import logging
from io import StringIO
from EasyLoggerAJM.easy_logger import EasyLogger, _EasyLoggerCustomLogger

@pytest.fixture
def logger():
    # We use a unique name to avoid side effects between tests if they share the same logger name
    l = EasyLogger(project_name="TestCustomLogger", root_log_location="./test_logs_custom").logger
    yield l
    # Cleanup handlers to avoid interfering with other tests
    for h in l.handlers[:]:
        l.removeHandler(h)
        h.close()

@pytest.fixture
def log_capture():
    return StringIO()

@pytest.fixture
def logger_with_capture(logger, log_capture):
    handler = logging.StreamHandler(log_capture)
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)
    return logger, log_capture

@pytest.mark.parametrize("level", ['info', 'debug', 'warning', 'error', 'critical'])
def test_log_levels_output(logger_with_capture, level):
    logger, log_capture = logger_with_capture
    method = getattr(logger, level)
    log_msg = f"Test {level} message"
    method(log_msg)
    assert log_msg in log_capture.getvalue()

@pytest.mark.parametrize("level", ['info', 'debug', 'warning', 'error', 'critical'])
@pytest.mark.parametrize("should_print", [True, False])
def test_print_msg_functionality(mocker, logger_with_capture, level, should_print):
    logger, log_capture = logger_with_capture
    mock_print = mocker.patch('builtins.print')
    
    # We need to wrap _print_msg to see if it was called, but also let it run
    spy_print_msg = mocker.spy(logger, '_print_msg')
    
    method = getattr(logger, level)
    log_msg = f"Test {level} message with print={should_print}"
    
    method(log_msg, print_msg=should_print)
    
    spy_print_msg.assert_called_once_with(log_msg, print_msg=should_print)
    
    if should_print:
        mock_print.assert_called_once_with(log_msg)
    else:
        mock_print.assert_not_called()
    
    assert log_msg in log_capture.getvalue()

def test_internal_print_call_directly(mocker, logger):
    mock_print = mocker.patch('builtins.print')
    logger._print_msg("direct message", print_msg=True)
    mock_print.assert_called_once_with("direct message")

def test_internal_no_print_call_directly(mocker, logger):
    mock_print = mocker.patch('builtins.print')
    logger._print_msg("direct message", print_msg=False)
    mock_print.assert_not_called()
