from logging import Handler, StreamHandler
from pathlib import Path
from shutil import rmtree, copytree
from typing import Optional, Union
from zipfile import ZipFile

from EasyLoggerAJM import InvalidEmailMsgType, LogFilePrepError


class _BaseCustomEmailHandler(Handler):
    VALID_EMAIL_MSG_TYPES = []
    ERROR_TEMPLATE = "Error sending email: {error_msg}"

    def __init__(self, email_msg, logger_dir_path: Union[str, Path], recipient: Union[str, list], project_name='default_project_name',
                 **kwargs):
        super().__init__()
        self._email_msg = None
        self._recipient = None

        self.email_msg = email_msg  # kwargs.pop('email_msg', None)
        self.recipient = recipient
        self.project_name = project_name
        if isinstance(logger_dir_path, str):
            self.logger_dir_path = Path(logger_dir_path)
        elif isinstance(logger_dir_path, Path):
            self.logger_dir_path = logger_dir_path

        if not self.email_msg or not self.recipient:
            raise ValueError("email_msg and or recipient not provided.")

    @property
    def recipient(self) -> str:
        return self._recipient

    @recipient.setter
    def recipient(self, value: Union[str, list]):
        if not value:
            raise ValueError("recipient not provided.")
        if isinstance(value, list):
            self._recipient = ' ;'.join(value)
        else:
            self._recipient = value

    @property
    def email_msg(self):
        return self._email_msg

    @email_msg.setter
    def email_msg(self, value):
        if not value:
            raise ValueError("email_msg not provided.")

        if isinstance(value, tuple(self.VALID_EMAIL_MSG_TYPES)):
            if callable(value):
                self._email_msg = value()
            else:
                self._email_msg = value
        if (self.__class__.VALID_EMAIL_MSG_TYPES
                and len(self.__class__.VALID_EMAIL_MSG_TYPES) <= 0):
            raise InvalidEmailMsgType(
                valid_msg_types=self.__class__.VALID_EMAIL_MSG_TYPES,
                given_value=type(value))

    @staticmethod
    def _write_zip(zip_path: Union[Path, str] = None, copy_dest: Path = None):
        with ZipFile(zip_path, 'w') as zipf:
            for f in copy_dest.iterdir():
                if f.suffix == '.log':
                    zipf.write(f, arcname=f.name)

    def _prep_logfile_attachment(self, dir_path: Optional[Path] = None):
        if not dir_path:
            dir_path = Path(self.logger_dir_path.as_posix())
        if dir_path.is_dir():
            copy_dest = dir_path / 'copy_of_logfile'
            copytree(dir_path, copy_dest, dirs_exist_ok=True)
            zip_path = dir_path / 'copy_of_logfile.zip'

            self._write_zip(zip_path, copy_dest)
            return zip_path, copy_dest

    @staticmethod
    def _cleanup_logfile_zip(dir_path: Union[Path, str], zip_to_attach: Union[Path, str]):
        rmtree(dir_path, ignore_errors=True)
        zip_to_attach.unlink(missing_ok=True)


class OutlookEmailHandler(_BaseCustomEmailHandler):
    VALID_EMAIL_MSG_TYPES = []

    def __init_subclass__(cls, **kwargs):
        if not cls.VALID_EMAIL_MSG_TYPES:
            raise ValueError("VALID_EMAIL_MSG_TYPES not defined.")

    def _prepare_email(self, record):
        self.email_msg.To = self.recipient  # Replace with your recipient
        self.email_msg.Subject = f"{record.levelname} in {self.project_name}"
        self.email_msg.HTMLBody = self.format(record)

    def _prep_and_attach_logfile(self):
        zip_to_attach, copy_dir_path = self._prep_logfile_attachment()
        if zip_to_attach and zip_to_attach.is_file():
            self.email_msg.Attachments.Add(str(zip_to_attach.resolve()))
        return zip_to_attach, copy_dir_path

    def _send_and_cleanup_attachments(self, copy_dir_path, zip_to_attach, **kwargs):
        try:
            self.email_msg.Send()
            self._cleanup_logfile_zip(copy_dir_path, zip_to_attach)
        except Exception as e:
            err_string = self.__class__.ERROR_TEMPLATE.format(error_msg=e)
            print(err_string)
        finally:
            try:
                self._cleanup_logfile_zip(copy_dir_path, zip_to_attach)
            except UnboundLocalError:
                pass
            finally:
                self.email_msg.Attachments.Clear()
                self.email_msg.Send()

    def emit(self, record):
        try:
            zip_to_attach, copy_dir_path = self._prep_and_attach_logfile()
        except Exception as e:
            raise LogFilePrepError(e) from None
        self._send_and_cleanup_attachments(copy_dir_path, zip_to_attach)


class StreamHandlerIgnoreExecInfo(StreamHandler):
    """
    A custom logging StreamHandler that temporarily suppresses exception information when emitting a log record.

    This handler is useful in scenarios where the exception information (`exc_info` and `exc_text`)
    should not be included in the StreamHandler output but needs to remain intact in the original log record.

    Methods:
        emit(record):
            Handles the log record emission by temporarily removing `exc_info` and `exc_text` attributes
            from the log record (if present) and restoring them after the emission. If `exc_info` is not
            present in the record, it simply calls the parent class's `emit` method.
    """
    def emit(self, record):
        """
        :param record: Log record to be processed and possibly emitted by the handler.
        :type record: logging.LogRecord
        :return: None
        :rtype: None
        """
        # Temporarily remove exc_info and exc_text for this handler
        if record.exc_info:
            # Save the original exc_info
            orig_exc_info = record.exc_info
            orig_exc_text = getattr(record, 'exc_text', None)
            record.exc_info = None
            record.exc_text = None
            try:
                # Call the parent class emit method
                super().emit(record)
            finally:
                # Restore the original exc_info back to the record
                record.exc_info = orig_exc_info
                record.exc_text = orig_exc_text
        else:
            super().emit(record)
