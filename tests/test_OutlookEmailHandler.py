import pathlib
import unittest
from unittest import mock
from unittest.mock import patch, Mock, MagicMock

from EasyLoggerAJM.logger_parts import OutlookEmailHandler


@unittest.skip("Skipping OutlookEmailHandler tests, they are not ready")
class TestOutlookEmailHandler(unittest.TestCase):

    def setUp(self):
        # Provide required arguments for OutlookEmailHandler's parent class constructor
        email_msg = self.get_mock_outlook_email()  # Assuming this could be configured as needed
        logger_dir_path = pathlib.Path("/path/to/logs")  # Placeholder directory path
        recipient = "recipient@test.com"

        self.handler = OutlookEmailHandler(email_msg, logger_dir_path, recipient, dev_mode=True)
        self.record = mock.Mock()

    @patch("win32com.client.Dispatch")
    def get_mock_outlook_email(self, mock_dispatch):
        # Create a mock for the mail item
        mock_mail_item = MagicMock()
        mock_dispatch.return_value.CreateItem.return_value = mock_mail_item

        # Simulate handling Outlook interaction
        import win32com.client
        outlook = win32com.client.Dispatch("Outlook.Application")
        mail_item = outlook.CreateItem(0)  # Equivalent to creating a new mail item
        mail_item.To = "test@recipient.com"  # Mock setting the recipient
        mail_item.Subject = "Test Subject"  # Mock setting the subject
        mail_item.Body = "This is a test email."  # Mock setting the body
        #mail_item.Send()  # Mock sending the email

        # Assertions to ensure the expected interactions occurred
        #mock_dispatch.assert_called_once_with("Outlook.Application")
        mock_mail_item.To = "test@recipient.com"
        mock_mail_item.Subject = "Test Subject"
        mock_mail_item.Body = "This is a test email"
        return mock_mail_item
        #mock_mail_item.Send.assert_called_once()  # Ensures the 'Send' method was called

    @patch("EasyLoggerAJM.handlers.ZipFile", autospec=True)
    @patch("pathlib.Path", autospec=True)
    def test_emit(self, mock_path, mock_zip):
        print(self.handler.email_msg)
        self.record.levelname = "Error"
        self.handler.project_name = "ProjectName"
        self.handler.format = Mock()
        self.handler.recipient = "recipient@test.com"

        mock_path.is_file.return_value = True
        mock_path.resolve.return_value = pathlib.Path('mock_resolved_path')

        with patch.object(self.handler, '_prep_logfile_attachment') as mock_prep_func:
            mock_prep_func.return_value = (mock_path, mock_path)

            self.handler.emit(self.record)
            self.handler.format.assert_called_once_with(self.record)  # Ensure format is called
            self.handler._prep_logfile_attachment.assert_called_once()

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
                self.handler.format.assert_called_once_with(self.record)  # Ensure format is called
                self.handler._prep_logfile_attachment.assert_called_once()
                mocked_print.assert_called_once_with('Error sending email: Test exception')


if __name__ == "__main__":
    unittest.main()
