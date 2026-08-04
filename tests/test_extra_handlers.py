import pytest
import logging
import time
from pathlib import Path
from EasyLoggerAJM.logger_parts import BufferedRecordHandler, LastRecordHandler, HourlyRotatingFileHandler

def test_buffered_record_handler():
    handler = BufferedRecordHandler(buffer_size=3)
    logger = logging.getLogger("test_buffered")
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)
    
    logger.info("msg 1")
    logger.info("msg 2")
    logger.info("msg 3")
    logger.info("msg 4")
    
    assert handler.get_last_message() == "msg 4"
    assert len(handler.get_all_messages()) == 3
    # Check messages
    messages = [r.msg if hasattr(r, 'msg') else r for r in handler.get_all_messages()]
    assert messages == ["msg 2", "msg 3", "msg 4"]
    
    last_n = [r.msg if hasattr(r, 'msg') else r for r in handler.get_last_n_messages(2)]
    assert last_n == ["msg 3", "msg 4"]

def test_last_record_handler():
    handler = LastRecordHandler()
    logger = logging.getLogger("test_last")
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)
    
    logger.info("first")
    assert handler.get_last_message() == "first"
    
    logger.info("second")
    assert handler.get_last_message() == "second"
    assert handler.get_last_record().msg == "second"

def test_hourly_rotating_file_handler(tmp_path):
    log_file = tmp_path / "hourly.log"
    handler = HourlyRotatingFileHandler(str(log_file))
    assert handler.when.upper() == 'H'
    # In some python versions, interval is stored in seconds
    assert handler.interval == 1 or handler.interval == 3600
    handler.close()
