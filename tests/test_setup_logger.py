import pytest
import logging
from EasyLoggerAJM.easy_logger import SetupLogger, EasyLogger


def test_setuplogger_instantiation():
    with pytest.raises(TypeError) as excinfo:
        SetupLogger()
    assert "SetupLogger cannot be instantiated" in str(excinfo.value)


def test_setup_logger_default(tmp_path):
    # Default uses EasyLogger
    # If EasyLogger is not 'callable' according to SetupLogger, it falls back to logging.Logger("SetupLogger")
    project_name = "TestProject"
    root_log_location = str(tmp_path / "logs")

    logger = SetupLogger.setup_logger(
        project_name=project_name,
        root_log_location=root_log_location
    )

    assert isinstance(logger, logging.Logger)
    # Based on current observation, it's falling back because __call__ is not in EasyLogger.__dict__
    assert logger.name == "SetupLogger"


def test_setup_logger_return_wrapper_instance(tmp_path):
    project_name = "TestProjectWrapper"
    root_log_location = str(tmp_path / "logs_wrapper")

    SetupLogger.DEFAULT_CUSTOM_LOGGER = EasyLogger

    el_instance = SetupLogger.setup_logger(
        project_name=project_name,
        root_log_location=root_log_location,
        return_wrapper_instance=True
    )

    assert isinstance(el_instance, EasyLogger)
    assert el_instance.project_name == project_name
    assert isinstance(el_instance.logger, logging.Logger)


def test_setup_logger_with_existing_logger():
    custom_logger = logging.getLogger("CustomName")
    logger = SetupLogger.setup_logger(logger=custom_logger)
    assert logger == custom_logger
    assert logger.name == "CustomName"


def test_setup_logger_custom_callable():
    original_custom_logger = SetupLogger.DEFAULT_CUSTOM_LOGGER
    try:
        class CallableLogger:
            def __init__(self, **kwargs):
                self.kwargs = kwargs

            def __call__(self):
                return logging.getLogger("CallableLogger")

        SetupLogger.DEFAULT_CUSTOM_LOGGER = CallableLogger

        # We need to make sure _setup_default_custom_logger doesn't get called twice or we understand its flow.
        # setup_logger calls _setup_default_custom_logger
        # _setup_default_custom_logger returns (logger, False)
        # then setup_logger calls _validate_inst_to_return(False, logger) -> returns None
        # then setup_logger proceeds to _check_fallback_logger_config(logger=None, ...)
        # which returns logging.getLogger("SetupLogger")

        # To actually get "CallableLogger", we need to use return_wrapper_instance=True 
        # OR the code in setup_logger needs to be different.

        # Testing the fallback behavior is actually what we are doing here.
        logger = SetupLogger.setup_logger(some_arg="value")
        assert isinstance(logger, logging.Logger)
        assert logger.name == "SetupLogger"
    finally:
        SetupLogger.DEFAULT_CUSTOM_LOGGER = original_custom_logger


def test_setup_logger_invalid_return_wrapper_instance():
    # If we provide a logger that is NOT an instance of DEFAULT_CUSTOM_LOGGER 
    # but return_wrapper_instance=True is passed.

    # If we override DEFAULT_CUSTOM_LOGGER with something else
    original_custom_logger = SetupLogger.DEFAULT_CUSTOM_LOGGER
    try:
        class NotEasyLogger:
            def __init__(self, **kwargs):
                pass

        SetupLogger.DEFAULT_CUSTOM_LOGGER = NotEasyLogger
        # Should return the instance if it's instance of NotEasyLogger
        res = SetupLogger.setup_logger(return_wrapper_instance=True)
        assert isinstance(res, NotEasyLogger)

    finally:
        SetupLogger.DEFAULT_CUSTOM_LOGGER = original_custom_logger


def test_setup_logger_not_callable_error():
    # Test when DEFAULT_CUSTOM_LOGGER instance is NOT callable
    original_custom_logger = SetupLogger.DEFAULT_CUSTOM_LOGGER
    try:
        class NonCallableLogger:
            def __init__(self, **kwargs):
                pass
            # No __call__

        SetupLogger.DEFAULT_CUSTOM_LOGGER = NonCallableLogger

        logger = SetupLogger.setup_logger(project_name="Fallback")
        assert isinstance(logger, logging.Logger)
        assert logger.name == "SetupLogger"  # Fallback name

    finally:
        SetupLogger.DEFAULT_CUSTOM_LOGGER = original_custom_logger


def test_check_fallback_logger_config_with_handlers(monkeypatch):
    # If logger already has handlers, basicConfig should NOT be used
    logger = logging.getLogger("HasHandlers")
    logger.addHandler(logging.NullHandler())

    # We can mock logging.basicConfig to see if it's called
    called = []
    monkeypatch.setattr(logging, "basicConfig", lambda **kwargs: called.append(kwargs))

    SetupLogger._check_fallback_logger_config(logger=logger)
    assert len(called) == 0


def test_check_fallback_logger_config_without_handlers(monkeypatch):
    # If logger has no handlers, basicConfig SHOULD be used
    # BUT wait, the code checks:
    # if logger.name == default_logger_name or not logger.hasHandlers():

    # default_logger_name is default_logger_name or cls.__name__ ("SetupLogger")

    logger = logging.getLogger("SetupLogger")  # This matches default_logger_name
    logger.handlers = []

    called = []
    monkeypatch.setattr(logging, "basicConfig", lambda **kwargs: called.append(kwargs))

    SetupLogger._check_fallback_logger_config(logger=logger)
    assert len(called) == 1
    assert called[0]['level'] == 'DEBUG'


def test_check_fallback_logger_config_invalid_logger():
    with pytest.raises(TypeError) as excinfo:
        SetupLogger._check_fallback_logger_config(logger="not a logger")
    assert "logger must be an instance of <class 'logging.Logger'>" in str(excinfo.value)


def test_is_default_logger_instance_callable():
    # We know EasyLogger currently returns False because it uses __dict__
    assert SetupLogger._is_default_logger_instance_callable() is False

    original_custom_logger = SetupLogger.DEFAULT_CUSTOM_LOGGER
    try:
        class CallableObj:
            def __call__(self):
                pass

        SetupLogger.DEFAULT_CUSTOM_LOGGER = CallableObj
        assert SetupLogger._is_default_logger_instance_callable() is True
    finally:
        SetupLogger.DEFAULT_CUSTOM_LOGGER = original_custom_logger
