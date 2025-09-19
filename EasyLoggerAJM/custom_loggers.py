from logging import Logger, getLevelName, StreamHandler


class _EasyLoggerCustomLogger(Logger):
    """
    A custom logger class that extends the standard Python Logger class, providing
    additional functionality such as selective message printing and message sanitization.

    Methods:
    --------
    _logger_should_print_normal_msg(self) -> bool:
        Determines if the logger should print normal messages based on the
        StreamHandler logging levels.

    sanitize_msg(msg: str) -> str: (staticmethod)
        Sanitizes the input message by encoding and decoding it using cp1250
        encoding, removing unsupported characters.

    _print_msg(self, msg: str, **kwargs) -> None:
        Prints the message to the console, if allowed by the logger's state and
        the method's arguments.

    _log(self, level: int, msg: str, args: tuple, exc_info=None, extra=None,
         stack_info=False, **kwargs) -> None:
        Logs a message at the specified logging level, optionally sanitizing
        and printing the message.

    info(self, msg: str, *args, **kwargs) -> None:
        Logs an informational message.

    warning(self, msg: str, *args, **kwargs) -> None:
        Logs a warning message.

    error(self, msg: str, *args, **kwargs) -> None:
        Logs an error message.

    debug(self, msg: str, *args, **kwargs) -> None:
        Logs a debug message.

    critical(self, msg: str, *args, **kwargs) -> None:
        Logs a critical message.
    """

    def _logger_should_print_normal_msg(self) -> bool:
        """
        Determines whether the logger should print normal messages based on the
        logging levels of its StreamHandler instances.

        :return: True if no StreamHandler is set to DEBUG or INFO level,
                 otherwise False.
        :rtype: bool
        """
        stream_handler_levels = [getLevelName(x.level) for x in
                                 self.handlers
                                 if type(x) is StreamHandler]
        if stream_handler_levels:
            if any([x for x in stream_handler_levels if x in ['DEBUG', 'INFO']]):
                return False
        return True

    @staticmethod
    def sanitize_msg(msg):
        """
        Sanitizes the input message by encoding it using 'cp1250' encoding with error ignoring
        and decoding it back.

        :param msg: The input message string to sanitize.
        :type msg: str
        :return: The sanitized message string.
        :rtype: str
        """
        msg = msg.encode('cp1250', errors='ignore').decode('cp1250')
        return msg

    def _print_msg(self, msg, **kwargs):
        """
        :param msg: The message to be printed.
        :type msg: str
        :param kwargs: Optional keyword arguments, which include 'print_msg' to control whether the message should be printed.
        :type kwargs: dict
        :return: None
        :rtype: None
        """
        if kwargs.get('print_msg', False) and self._logger_should_print_normal_msg():
            print(msg)

    def _log(self, level, msg, args, exc_info=None, extra=None, stack_info=False, **kwargs):
        """
        :param level: The logging level specified for the log message.
        :type level: int
        :param msg: The message that needs to be logged.
        :type msg: str
        :param args: Arguments to be merged into the log message.
        :type args: tuple
        :param exc_info: Indicator or exception information for the log message. Can be a tuple, exception, or boolean.
        :type exc_info: Optional[Union[tuple, Exception, bool]]
        :param extra: Additional context information to include in the log record.
        :type extra: Optional[dict]
        :param stack_info: Whether stack information should be added to the log record.
        :type stack_info: bool
        :param kwargs: Additional keyword arguments to modify the log behavior.
        :type kwargs: dict
        :return: None
        :rtype: None
        """
        self._print_msg(msg, print_msg=kwargs.pop('print_msg', False))
        msg = self.sanitize_msg(msg)
        # noinspection PyProtectedMember
        super()._log(level, msg, args,
                     exc_info=exc_info,
                     extra=extra, stack_info=stack_info,
                     **kwargs)

    def info(self, msg, *args, **kwargs):
        super().info(msg, *args, **kwargs)

    def warning(self, msg, *args, **kwargs):
        super().warning(msg, *args, **kwargs)

    def error(self, msg, *args, **kwargs):
        super().error(msg, *args, **kwargs)

    def debug(self, msg, *args, **kwargs):
        super().debug(msg, *args, **kwargs)

    def critical(self, msg, *args, **kwargs):
        super().critical(msg, *args, **kwargs)
