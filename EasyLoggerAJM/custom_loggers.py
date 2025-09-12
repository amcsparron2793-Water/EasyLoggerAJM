from logging import Logger, getLevelName, StreamHandler
from typing import Union


class _EasyLoggerCustomLogger(Logger):
    """
    This class defines a custom logger that extends the logging.Logger class.
    It includes methods for logging at different levels such as info, warning, error, debug, and critical.
     Additionally, there is a private static method _print_msg that can be used to print a log message
     based on the provided kwargs. Each logging method in this class calls _print_msg before delegating
     the actual logging to the corresponding method in the parent class.
     The logging methods accept parameters for the log message, additional arguments,
     exception information, stack information, stack level, and extra information.
      Additional keyword arguments can be provided to control printing behavior.
    """

    def __getattribute__(self, __name):
        if __name in ['info', 'warning', 'error', 'debug', 'critical']:
            try:
                raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{__name}' "
                                     f"use log() instead")
            except AttributeError as e:
                super().error(e, exc_info=True)
        return object.__getattribute__(self, __name)

    def _raise_and_log_no_log_func(self, level: Union[int, str],
                                   message: str, **kwargs):
        try:
            raise ValueError(f"Unknown log level: {level}, defaulting to INFO")
        except ValueError as e:
            self.warning(e)
            self.info(message, **kwargs)

    def _get_log_func(self, level: Union[int, str]):
        log_levels = {
            "info": self.info,
            "warning": self.warning,
            "error": self.error,
            "debug": self.debug,
            "critical": self.critical,
        }
        if isinstance(level, str):
            pass
        elif isinstance(level, int):
            level = getLevelName(level).lower()

        log_func = log_levels.get(level)
        return log_func

    def _print_msg(self, msg, **kwargs):
        if kwargs.get('print_msg', False) and self.logger_should_print_normal_msg:
            print(msg)

    @property
    def logger_should_print_normal_msg(self) -> bool:
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

    def log(self, level: Union[int, str], message: str, **kwargs):
        log_func = self._get_log_func(level)
        if log_func:
            log_func(message, **kwargs)
        else:
            self._raise_and_log_no_log_func(level, message, **kwargs)

    def info(self, msg: object, *args: object, exc_info=None,
             stack_info: bool = False, stacklevel: int = 1,
             extra=None, **kwargs):
        self._print_msg(msg, print_msg=kwargs.get('print_msg', False))
        super().info(msg, *args, exc_info=exc_info,
                     stack_info=stack_info, stacklevel=stacklevel,
                     extra=extra)

    def warning(self, msg: object, *args: object, exc_info=None,
                stack_info: bool = False, stacklevel: int = 1,
                extra=None, **kwargs):
        self._print_msg(msg, print_msg=kwargs.get('print_msg', False))
        super().warning(msg, *args, exc_info=exc_info,
                        stack_info=stack_info, stacklevel=stacklevel,
                        extra=extra)

    def error(self, msg: object, *args: object, exc_info=None,
              stack_info: bool = False, stacklevel: int = 1,
              extra=None, **kwargs):
        self._print_msg(msg, print_msg=kwargs.get('print_msg', False))
        super().error(msg, *args, exc_info=exc_info,
                      stack_info=stack_info, stacklevel=stacklevel,
                      extra=extra)

    def debug(self, msg: object, *args: object, exc_info=None,
              stack_info: bool = False, stacklevel: int = 1,
              extra=None, **kwargs):
        self._print_msg(msg, print_msg=kwargs.get('print_msg', False))
        super().debug(msg, *args, exc_info=exc_info,
                      stack_info=stack_info, stacklevel=stacklevel,
                      extra=extra)

    def critical(self, msg: object, *args: object, exc_info=None,
                 stack_info: bool = False, stacklevel: int = 1,
                 extra=None, **kwargs):
        self._print_msg(msg, print_msg=kwargs.get('print_msg', False))
        super().critical(msg, *args, exc_info=exc_info,
                         stack_info=stack_info, stacklevel=stacklevel,
                         extra=extra)
