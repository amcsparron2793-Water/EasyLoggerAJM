import string
from logging import Formatter, LogRecord
from re import sub

NO_COLORIZER = False
try:
    from ColorizerAJM import Colorizer
except (ModuleNotFoundError, ImportError):
    NO_COLORIZER = True


class ColorizedFormatter(Formatter):
    """
    Class that extends logging.Formatter to provide colored output based on log level.
    It includes methods to format log messages and exceptions with colors specified for
     warnings, errors, and other log levels.
    """
    def __init__(self, fmt=None, datefmt=None, style='%', validate=True):
        super().__init__(fmt, datefmt, style, validate)
        if NO_COLORIZER:
            return
        else:
            self.colorizer = Colorizer()

        self.debug_color = self.colorizer.__class__.LIGHT_GRAY
        self.info_color = self.colorizer.__class__.WHITE
        self.warning_color = self.colorizer.__class__.YELLOW
        self.error_color = self.colorizer.__class__.RED
        self.other_color = self.colorizer.__class__.GRAY

    def _get_record_color(self, record):
        if record.levelname == "WARNING":
            return self.warning_color
        elif record.levelname == "ERROR":
            return self.error_color
        elif record.levelname == "DEBUG":
            return self.debug_color
        elif record.levelname == "INFO":
            return self.info_color
        elif record.levelname == "CRITICAL":
            return self.error_color
        else:
            return self.other_color

    def formatMessage(self, record):
        if NO_COLORIZER:
            return super().formatMessage(record)
        else:
            return self.colorizer.colorize(text=super().formatMessage(record),
                                           color=self._get_record_color(record), bold=True)

    def formatException(self, ei):
        if NO_COLORIZER:
            return super().formatException(ei)
        else:
            return self.colorizer.colorize(text=super().formatException(ei),
                                           color=self._get_record_color(ei), bold=True)


class CleanANSIFileFormatter(Formatter):
    """
    Custom formatter to handle log record messages.

    This class provides custom handling of log messages, particularly ensuring
    that the messages are cleaned to contain only printable characters, and
    any issues with interpolation of modified log messages are avoided. Inherits
    from `Formatter`.
    """

    @staticmethod
    def _manual_arg_format(record: LogRecord):
        """ Format the message with its arguments before cleaning"""
        if record.args:
            # Manually format the message
            record.msg = record.msg % record.args
            # Optional: Clear the args to avoid reformatting issues downstream
            record.args = None
        return record

    def format(self, record: LogRecord) -> str:
        record = self._manual_arg_format(record)

        # Clean the fully formatted log message
        record.msg = self.clean_log_message(record.msg)

        # Now use the parent class to complete formatting
        return super().format(record)

    @staticmethod
    def _remove_ansi_escape_sequences(msg: str) -> str:
        """Remove ANSI escape sequences from a string."""
        # sub out any string that starts with [ and ends with m with ''
        pattern = r"\[\w.*?m"
        return sub(pattern, "", msg)

    def clean_log_message(self, msg: str) -> str:
        """ Ensures only characters that are printable per Unicode
        and part of `string.printable` are retained. This covers
        both common printable characters and certain Unicode
        characters that might also be "printable" but aren't
        in the ASCII set. The self._remove_ansi_escape_sequences()
        method covers any leftovers from Colorizer. """

        if not isinstance(msg, str):
            return msg

        # filter out any non-printable chars from the results of self._remove_ansi_escape_sequences
        filtered_msg_list = filter(lambda x: x in string.printable and x.isprintable(),
                                   self._remove_ansi_escape_sequences(msg))
        return ''.join(filtered_msg_list)
