import pytest
import logging
from EasyLoggerAJM.logger_parts import ColorizedFormatter, NO_COLORIZER
from EasyLoggerAJM.logger_parts.formatters import CleanANSIFileFormatter

def test_colorized_formatter():
    formatter = ColorizedFormatter("%(levelname)s: %(message)s")
    record = logging.LogRecord("test", logging.INFO, "path", 1, "info msg", None, None)
    formatted = formatter.format(record)
    
    if NO_COLORIZER:
        assert formatted == "INFO: info msg"
    else:
        # Check if it contains some ANSI escape codes or at least the content
        assert "INFO: info msg" in formatted

def test_clean_ansi_file_formatter():
    formatter = CleanANSIFileFormatter("%(message)s")
    # Simulate a message with ANSI codes (Colorizer usually adds these)
    msg_with_ansi = "\033[31mRed Message\033[0m"
    record = logging.LogRecord("test", logging.INFO, "path", 1, msg_with_ansi, None, None)
    
    # We need to manually format it because CleanANSIFileFormatter.format calls clean_log_message
    formatted = formatter.format(record)
    
    # It should have removed the ANSI escape sequences
    # Note: CleanANSIFileFormatter._remove_ansi_escape_sequences uses r"\[\w.*?m"
    # Wait, \033[ is ESC [. 
    # Let's see the implementation again.
    
    assert "Red Message" in formatted
    assert "\033[" not in formatted

def test_clean_ansi_file_formatter_non_printable():
    formatter = CleanANSIFileFormatter("%(message)s")
    msg = "Hello\x00World" # \x00 is non-printable
    record = logging.LogRecord("test", logging.INFO, "path", 1, msg, None, None)
    formatted = formatter.format(record)
    assert "HelloWorld" in formatted
    assert "\x00" not in formatted

def test_clean_ansi_file_formatter_with_args():
    formatter = CleanANSIFileFormatter("%(message)s")
    record = logging.LogRecord("test", logging.INFO, "path", 1, "Hello %s", ("World",), None)
    formatted = formatter.format(record)
    assert formatted == "Hello World"
