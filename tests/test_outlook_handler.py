import pytest
import pathlib
from unittest.mock import MagicMock
from EasyLoggerAJM.logger_parts import OutlookEmailHandler

# We need a subclass that defines VALID_EMAIL_MSG_TYPES to avoid ValueError if subclassed
# But we can also just use the class itself if we don't subclass it in tests.
# However, the setter for email_msg checks VALID_EMAIL_MSG_TYPES.

class MockEmailMsg:
    def __init__(self):
        self.To = ""
        self.Subject = ""
        self.HTMLBody = ""
        self.Attachments = MagicMock()
    def Send(self):
        pass

@pytest.fixture
def mock_email_msg():
    return MockEmailMsg()

@pytest.fixture
def outlook_handler(mock_email_msg, tmp_path):
    # Patch VALID_EMAIL_MSG_TYPES to allow MockEmailMsg
    OutlookEmailHandler.VALID_EMAIL_MSG_TYPES = [MockEmailMsg]
    handler = OutlookEmailHandler(mock_email_msg, tmp_path, "recipient@test.com", project_name="TestProject")
    return handler

def test_outlook_handler_initialization(outlook_handler, tmp_path):
    assert outlook_handler.recipient == "recipient@test.com"
    assert outlook_handler.project_name == "TestProject"
    assert outlook_handler.logger_dir_path == tmp_path

def test_outlook_handler_recipient_list(mock_email_msg, tmp_path):
    OutlookEmailHandler.VALID_EMAIL_MSG_TYPES = [MockEmailMsg]
    handler = OutlookEmailHandler(mock_email_msg, tmp_path, ["a@test.com", "b@test.com"])
    assert handler.recipient == "a@test.com ;b@test.com"

def test_emit_basic(outlook_handler, mocker):
    record = MagicMock()
    record.levelname = "ERROR"
    record.msg = "Test error"
    
    mocker.patch.object(outlook_handler, 'format', return_value="Formatted message")
    spy_send = mocker.spy(outlook_handler.email_msg, 'Send')
    
    # Mock _prep_and_attach_logfile to avoid actual zip creation in this test
    mocker.patch.object(outlook_handler, '_prep_and_attach_logfile', return_value=(None, None))
    
    outlook_handler.emit(record)
    
    assert outlook_handler.email_msg.To == "recipient@test.com"
    assert "ERROR" in outlook_handler.email_msg.Subject
    assert outlook_handler.email_msg.HTMLBody == "Formatted message"
    # Note: emit calls Send() multiple times in the current implementation (once in try, once in finally)
    assert spy_send.called

def test_prep_logfile_attachment(outlook_handler, tmp_path):
    log_file = tmp_path / "test.log"
    log_file.write_text("log content")
    
    zip_path, copy_dest = outlook_handler._prep_logfile_attachment()
    
    assert zip_path.exists()
    assert zip_path.suffix == ".zip"
    assert copy_dest.exists()
    assert copy_dest.name == "copy_of_logfile"
    
    outlook_handler._cleanup_logfile_zip(copy_dest, zip_path)
    assert not zip_path.exists()
    assert not copy_dest.exists()
