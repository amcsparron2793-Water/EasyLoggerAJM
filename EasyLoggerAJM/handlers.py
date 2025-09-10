from logging import Handler, NOTSET
from logging.handlers import SMTPHandler
from pathlib import Path
from shutil import rmtree, copytree
from typing import Optional, Union
from zipfile import ZipFile


class _BaseCustomEmailHandler:
    VALID_EMAIL_MSG_TYPES = []

    def __init__(self, email_msg, logger_dir_path, recipient: Union[str, list],
                 project_name='default_project_name',
                 level=NOTSET, **kwargs):
        self._email_msg = None
        self._recipient = None

        self.email_msg = email_msg  # kwargs.pop('email_msg', None)
        self.recipient = recipient
        self.project_name = project_name
        self.logger_dir_path = logger_dir_path

        super().__init__(level=level)
        if not self.email_msg or not self.recipient:
            raise ValueError("email_msg and or recipient not provided.")

    def __init_subclass__(cls, **kwargs):
        if not cls.VALID_EMAIL_MSG_TYPES:
            raise ValueError("VALID_EMAIL_MSG_TYPES not defined.")

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
            if callable(self._email_msg):
                self._email_msg = value()
            else:
                self._email_msg = value

        raise ValueError(f"email_msg must be one of {self.VALID_EMAIL_MSG_TYPES}.")

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


class OutlookEmailHandler(_BaseCustomEmailHandler, Handler):
    VALID_EMAIL_MSG_TYPES = []

    def emit(self, record):
        try:
            self.email_msg.To = self.recipient  # Replace with your recipient
            self.email_msg.Subject = f"{record.levelname} in {self.project_name}"
            self.email_msg.HTMLBody = self.format(record)

            zip_to_attach, copy_dir_path = self._prep_logfile_attachment()
            if zip_to_attach and zip_to_attach.is_file():
                self.email_msg.Attachments.Add(str(zip_to_attach.resolve()))

            self.email_msg.Send()
            self._cleanup_logfile_zip(copy_dir_path, zip_to_attach)
        except Exception as e:
            print(f"Error sending email: {e}")
