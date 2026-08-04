import pytest
import re
import logging
from pathlib import Path
from EasyLoggerAJM.easy_logger import EasyLogger
from EasyLoggerAJM.easy_logger import _EasyLoggerCustomLogger

@pytest.fixture
def test_attrs(tmp_path):
    return {"project_name": "TestProject", "root_log_location": str(tmp_path / "test_logs")}

@pytest.fixture
def easy_logger_default(test_attrs):
    return EasyLogger(**test_attrs)

@pytest.fixture
def default_logger(easy_logger_default):
    return easy_logger_default.logger

def test_creation(easy_logger_default):
    assert isinstance(easy_logger_default, EasyLogger)

def test_logger_inst_creation(default_logger):
    assert isinstance(default_logger, _EasyLoggerCustomLogger)

def test_logger_non_custom_logger_inst_creation(test_attrs):
    original_class = logging.getLoggerClass()
    logging.setLoggerClass(logging.Logger)
    try:
        non_default_logger = logging.getLogger("non_default")
        el = EasyLogger(**test_attrs, logger=non_default_logger)
        assert not isinstance(el.logger, _EasyLoggerCustomLogger)
        assert isinstance(el.logger, logging.Logger)
    finally:
        logging.setLoggerClass(original_class)

def test_project_name(easy_logger_default):
    assert easy_logger_default.project_name == "TestProject"

def test_default_format(easy_logger_default):
    assert easy_logger_default.DEFAULT_FORMAT == '%(asctime)s | %(name)s | %(levelname)s | %(message)s'

def test_inner_log_fstructure(easy_logger_default):
    assert easy_logger_default.inner_log_fstructure is not None

def test_log_location(easy_logger_default, test_attrs):
    log_loc = Path(easy_logger_default.log_location).resolve()
    expected_start = Path(test_attrs["root_log_location"]).resolve()
    # Check if log_loc is a subpath of expected_start
    assert expected_start in log_loc.parents or log_loc == expected_start

def test_use_logger_creation(test_attrs):
    # UseLogger should return the logger instance
    logger = EasyLogger.UseLogger(project_name="TestProject2", root_log_location=f"{test_attrs['root_log_location']}2")
    assert isinstance(logger, _EasyLoggerCustomLogger)

def test_make_file_handlers(easy_logger_default, default_logger):
    easy_logger_default.make_file_handlers()
    assert default_logger.handlers
    assert len(default_logger.handlers) >= len(easy_logger_default.file_logger_levels)

def test_logger_level_normalization_with_kwargs(test_attrs):
    file_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR']
    el = EasyLogger(**test_attrs, file_logger_levels=file_levels)
    el.make_file_handlers()
    handler_levels = [h.level for h in el.logger.handlers]
    for level in file_levels:
        level_int = getattr(logging, level)
        assert level_int in handler_levels

def test_is_daily_log_spec(test_attrs):
    el = EasyLogger(**test_attrs, is_daily_log_spec=True)
    el.make_file_handlers()
    assert el.inner_log_fstructure.split('/')[0] == el.DAILY_LOG_SPEC_FORMAT

@pytest.mark.parametrize("spec_input, expected_name", [
    ({'name': 'minute'}, 'minute'),
    ('minute', 'minute'),
    ('Minute', 'minute'),
    ({'name': 'Minute'}, 'minute'),
    (None, 'minute')
])
def test_log_spec_setting(easy_logger_default, spec_input, expected_name):
    easy_logger_default.log_spec = spec_input
    assert easy_logger_default.log_spec['name'] == expected_name

def test_invalid_log_spec_dict(easy_logger_default):
    with pytest.raises(KeyError):
        easy_logger_default.log_spec = {'wrong_key': 'minute'}

def test_invalid_log_spec_string(easy_logger_default):
    with pytest.raises(AttributeError):
        easy_logger_default.log_spec = 'wrong_string'

def test_show_warning_logs_in_console(test_attrs):
    el = EasyLogger(**test_attrs, show_warning_logs_in_console=True)
    # Check if a StreamHandler was added for warnings
    stream_handlers = [h for h in el.logger.handlers if isinstance(h, logging.StreamHandler) and not isinstance(h, logging.FileHandler)]
    assert any(h.level == logging.WARNING for h in stream_handlers)
