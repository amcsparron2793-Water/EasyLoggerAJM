import pathlib
import unittest
from unittest import mock
from unittest.mock import patch, Mock

from EasyLoggerAJM.handlers import OutlookEmailHandler


class TestOutlookEmailHandler(unittest.TestCase):

    def setUp(self):
        # Provide required arguments for OutlookEmailHandler's parent class constructor
        email_msg = Mock()  # Assuming this could be configured as needed
        logger_dir_path = pathlib.Path("/path/to/logs")  # Placeholder directory path
        recipient = "recipient@test.com"

        self.handler = OutlookEmailHandler(email_msg, logger_dir_path, recipient, dev_mode=True)
        self.record = mock.Mock()

    @patch("EasyLoggerAJM.handlers.ZipFile", autospec=True)
    @patch("pathlib.Path", autospec=True)
    def test_emit(self, mock_path, mock_zip):
        self.record.levelname = "Error"
        self.handler.project_name = "ProjectName"
        self.handler.format = Mock()
        self.handler.recipient = "recipient@test.com"

        mock_path.is_file.return_value = True
        mock_path.resolve.return_value = pathlib.Path('mock_resolved_path')

        with patch.object(self.handler, '_cleanup_logfile_zip') as mock_cleanup_func:
            with patch.object(self.handler, '_prep_logfile_attachment') as mock_prep_func:
                # Adjusting mock return value to return `mock_path` instead of a string
                mock_prep_func.return_value = (mock_path, mock_path)

                self.handler.emit(self.record)
                self.handler.format.assert_called_once_with(self.record)
                self.handler._prep_logfile_attachment.assert_called_once()

                # Fix assertion to match the correct expected behavior
                self.handler._cleanup_logfile_zip.assert_called_once_with(mock_path, mock_path)

                self.assertEqual(self.handler.email_msg.To, self.handler.recipient)
                self.assertTrue(mock_path.is_file.called)
                self.assertTrue(mock_path.resolve.called)

    def test_emit_with_exception(self):
        self.record.levelname = "Error"
        self.handler.project_name = "ProjectName"
        self.handler.format = Mock()
        self.handler.recipient = "recipient@test.com"

        with patch('builtins.print') as mocked_print:
            with patch.object(self.handler, '_prep_logfile_attachment') as mock_prep_func:
                mock_prep_func.side_effect = Exception("Test exception")

                self.handler.emit(self.record)
                self.handler.format.assert_called_once_with(self.record)
                self.handler._prep_logfile_attachment.assert_called_once()

                mocked_print.assert_called_once_with('Error sending email: Test exception')


if __name__ == "__main__":
    unittest.main()
