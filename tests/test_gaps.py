import pytest
import logging
from io import StringIO
from pathlib import Path
from unittest.mock import MagicMock
from EasyLoggerAJM.easy_logger import EasyLogger, SetupLogger, _EasyLoggerCustomLogger
from EasyLoggerAJM.backend.errs import InvalidEmailMsgType, InstanceNotCallableError
from EasyLoggerAJM.logger_parts import OutlookEmailHandler, ConsoleOneTimeFilter


class TestGaps:

    # 1. _EasyLoggerCustomLogger gaps
    def test_custom_logger_sanitize_msg(self):
        logger = _EasyLoggerCustomLogger("test")
        # cp1250 doesn't support some unicode characters like emoji
        original_msg = "Hello \u263A World"
        sanitized = logger.sanitize_msg(original_msg)
        assert "\u263A" not in sanitized
        assert "Hello  World" in sanitized

        # Test with Exception
        exc = ValueError("test exception")
        assert logger.sanitize_msg(exc) == "test exception"

    def test_custom_logger_should_print_logic(self):
        logger = _EasyLoggerCustomLogger("test_should_print")
        # Initially True as no stream handlers
        assert logger._logger_should_print_normal_msg() is True

        # Add a stream handler with INFO level -> should return False for ('DEBUG', 'INFO')
        sh = logging.StreamHandler()
        sh.setLevel(logging.INFO)
        logger.addHandler(sh)
        assert logger._logger_should_print_normal_msg() is False

        # Change handler level to WARNING -> should return True
        sh.setLevel(logging.WARNING)
        assert logger._logger_should_print_normal_msg() is True

        # FileHandler should be ignored in this logic
        fh = logging.FileHandler("test.log")
        fh.setLevel(logging.INFO)
        logger.addHandler(fh)
        try:
            assert logger._logger_should_print_normal_msg() is True
        finally:
            logger.removeHandler(fh)
            fh.close()
            if Path("test.log").exists():
                Path("test.log").unlink()

    # 2. SetupLogger gaps
    def test_setup_logger_instantiation_prevention(self):
        with pytest.raises(TypeError, match="SetupLogger cannot be instantiated"):
            SetupLogger()

    def test_setup_logger_validate_inst_to_return_error(self):
        SetupLogger.DEFAULT_CUSTOM_LOGGER = EasyLogger
        with pytest.raises(TypeError, match="logger must be an instance of"):
            SetupLogger._validate_inst_to_return(True, "not_an_instance")

    def test_setup_logger_is_default_logger_instance_callable_edge_case(self):
        # Case where DEFAULT_CUSTOM_LOGGER is not None but doesn't have __dict__ (e.g. some builtins or slots)
        SetupLogger.DEFAULT_CUSTOM_LOGGER = 123
        assert SetupLogger._is_default_logger_instance_callable() is False

    # 3. EasyLogger gaps
    def test_easy_logger_propagate_kwarg(self, tmp_path):
        # We need to use a unique logger name to avoid using a cached one
        el = EasyLogger(project_name="propagate_test", root_log_location=str(tmp_path),
                        propagate=False, logger_name="prop_false")
        assert el.logger.propagate is False

        el2 = EasyLogger(project_name="propagate_test_2", root_log_location=str(tmp_path),
                         propagate=True, logger_name="prop_true")
        assert el2.logger.propagate is True

    def test_get_level_handler_string(self):
        sh = logging.StreamHandler()
        sh.setLevel(logging.INFO)
        fh = logging.FileHandler("test_string.log")
        fh.setLevel(logging.ERROR)

        try:
            res = EasyLogger._get_level_handler_string([sh, fh])
            assert "StreamHandler - INFO" in res
            assert "FileHandler - ERROR" in res
        finally:
            fh.close()
            if Path("test_string.log").exists():
                Path("test_string.log").unlink()

    # 4. OutlookEmailHandler gaps
    def test_outlook_handler_email_msg_validation(self, tmp_path):
        class WrongType:
            pass

        # Create a mock that will pass the check
        mock_msg = MagicMock()

        # We need to temporarily add MagicMock to VALID_EMAIL_MSG_TYPES to allow initialization
        orig_types = OutlookEmailHandler.VALID_EMAIL_MSG_TYPES
        OutlookEmailHandler.VALID_EMAIL_MSG_TYPES = [MagicMock]
        try:
            handler = OutlookEmailHandler(mock_msg, tmp_path, "test@test.com")

            # Now test that a wrong type raises InvalidEmailMsgType
            with pytest.raises(InvalidEmailMsgType):
                handler.email_msg = WrongType()
        finally:
            OutlookEmailHandler.VALID_EMAIL_MSG_TYPES = orig_types

    # 5. Error Classes gaps
    def test_invalid_email_msg_type_attribute_error(self):
        with pytest.raises(AttributeError, match="if msg is not given, valid_msg_types and given_value must be given"):
            InvalidEmailMsgType()

    def test_instance_not_callable_error_msg(self):
        err = InstanceNotCallableError()
        assert "Attempted to return logger" in err.message
        err2 = InstanceNotCallableError("Custom message")
        assert err2.message == "Custom message"

    # 6. Filter gaps
    def test_console_one_time_filter_repeated_msg(self):
        filt = ConsoleOneTimeFilter()
        record = logging.LogRecord("name", logging.WARNING, "path", 1, "Repeated message", None, None)
        assert filt.filter(record) is True
        assert filt.filter(record) is False

        record2 = logging.LogRecord("name", logging.WARNING, "path", 1, "New message", None, None)
        assert filt.filter(record2) is True
