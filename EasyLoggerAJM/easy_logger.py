"""
easy_logger.py

logger with already set up generalized file handlers

"""
import logging
from typing import Union, List, Optional, Callable

from EasyLoggerAJM import _EasyLoggerCustomLogger
from EasyLoggerAJM.logger_parts import NO_COLORIZER
from EasyLoggerAJM.backend import EasyLoggerInitializer


class EasyLogger(EasyLoggerInitializer):
    """

    EasyLogger
    ==========

    Class to provide an easy logging mechanism for projects.

    Attributes:
    -----------
    DEFAULT_FORMAT : str
        Default log format used in the absence of a specified format.

    INT_TO_STR_LOGGER_LEVELS : dict
        Mapping of integer logger levels to their string representations.

    STR_TO_INT_LOGGER_LEVELS : dict
        Mapping of string logger levels to their integer representations.

    MINUTE_LOG_SPEC_FORMAT : tuple
        Tuple representing the log specification format at minute granularity.

    MINUTE_TIMESTAMP : str
        Timestamp at minute granularity.

    HOUR_LOG_SPEC_FORMAT : tuple
        Tuple representing the log specification format at hour granularity.

    HOUR_TIMESTAMP : str
        Timestamp at hour granularity.

    DAILY_LOG_SPEC_FORMAT : str
        String representing the log specification format at daily granularity.

    DAILY_TIMESTAMP : str
        Timestamp at daily granularity.

    LOG_SPECS : dict
        Dictionary containing predefined logging specifications.

    Methods:
    --------
     __init__(self, project_name=None, root_log_location="../logs", chosen_format=DEFAULT_FORMAT, logger=None, **kwargs)
        Initialize EasyLogger instance with provided parameters.

    file_logger_levels(self)
        Property to handle file logger levels.

    project_name(self)
        Property method to get the project name.

    inner_log_fstructure(self)
        Get the inner log file structure.

    log_location(self)
        Get the log location for file handling.

    log_spec(self)
        Handle logging specifications.

    classmethod UseLogger(cls, **kwargs)
        Instantiate a class with a specified logger.

    Note:
    -----
    The EasyLogger class provides easy logging functionality for projects,
    allowing customization of log formats and levels.

    """
    SHOW_WARNING_LOGS_MSG = 'warning logs will be printed to console - creating stream handler'

    def __init__(self, logger=None, **kwargs):
        super().__init__(**kwargs)

        self.logger = self.initialize_logger(logger=logger)

        self.make_file_handlers()

        if self.show_warning_logs_in_console:
            self._internal_logger.info(self.__class__.SHOW_WARNING_LOGS_MSG)
            self.create_stream_handler(**kwargs)

        self.create_other_handlers()
        self.post_handler_setup()

    @staticmethod
    def _get_level_handler_string(handlers: List[logging.Handler]) -> str:
        """Return a compact string summary of handlers and their levels.

        Example: "StreamHandler - WARNING, FileHandler - INFO"
        """
        return ', '.join([' - '.join((x.__class__.__name__, logging.getLevelName(x.level)))
                          for x in handlers])

    @classmethod
    def UseLogger(cls, **kwargs):
        """
        This method is a class method that can be used to instantiate a class with a logger.
        It takes in keyword arguments and returns an instance of the class with the specified logger.

        Parameters:
        - **kwargs: Keyword arguments that are used to instantiate the class.

        Returns:
        - An instance of the class with the specified logger.

        Usage:
            MyClass.UseLogger(arg1=value1, arg2=value2)

        Note:
            The logger used for instantiation is obtained from the `logging` module and is named 'logger'.
        """
        return cls(**kwargs, logger=kwargs.get('logger', None)).logger

    def _set_logger_class(self, logger_class=_EasyLoggerCustomLogger, **kwargs):
        """Create and return a logger using the provided logger_class.

        Sets the global logger class, creates a named logger (defaults to 'logger'),
        and logs internal diagnostics during setup.
        """
        self._internal_logger.info('no passed in logger detected')
        logging.setLoggerClass(logger_class)
        self._internal_logger.info(f'logger class set to \'{logger_class.__name__}\'')
        # Create a logger with a specified name
        self.logger = logging.getLogger(kwargs.get('logger_name', 'logger'))
        self._internal_logger.info(f'logger created with name set to \'{self.logger.name}\'')
        return self.logger

    def initialize_logger(self, logger=None, **kwargs) -> Union[logging.Logger, _EasyLoggerCustomLogger]:
        """
        :param logger: The logger instance to initialize. If None, a new logger will be created using the internal method.
        :type logger: logging.Logger or None
        :param kwargs: Additional parameters to configure the logger, such as propagate settings.
        :type kwargs: dict
        :return: The initialized logger instance.
        :rtype: Union[logging.Logger, _EasyLoggerCustomLogger]

        THIS IS HOW TO FIX ISSUE WITH MULTIPLE LOGGING INSTANCES, override with this:
        self.logger = super().initialize_logger(logger=logger, **kwargs)
        self.logger.propagate = False
        return self.logger
        """
        if not logger:
            self.logger = self._set_logger_class(**kwargs)
        else:
            self._internal_logger.info(f'passed in logger ({logger}) detected')
            self.logger: logging.getLogger = logger
        self.logger.propagate = kwargs.get('propagate', True)
        self._internal_logger.info('logger initialized')
        self._internal_logger.info(f'propagate set to {self.logger.propagate}')
        return self.logger

    def post_handler_setup(self):
        """Finalize logger configuration after handlers are attached.

        - Resets the logger level to DEBUG so it receives all messages.
        - Emits an info line listing handler types and levels.
        - Warns if a colorizer is expected but not available.
        """
        # set the logger level back to DEBUG, so it handles all messages
        self.logger.setLevel(10)
        self._internal_logger.info(f'logger level set back to {self.logger.level}')
        self.logger.info(f"Starting {self.project_name} with the following handlers: "
                         f"{self._get_level_handler_string(self.logger.handlers)}")
        if not self._no_stream_color and NO_COLORIZER:
            self.logger.warning("colorizer not available, logs may not be colored as expected.")
        self._internal_logger.info("final logger initialized")
        # print("logger initialized")


class SetupLogger:
    """
    Provides methods to configure and manage a logging mechanism. This class
    ensures that a logger is properly initialized and allows fallback
    configuration for cases where no logger handlers are defined.

    :ivar log_level_to_stream: Default log level for streaming logs as a string.
    :type log_level_to_stream: str
    :ivar basic_config_level: Default log level for basic configuration as a string.
    :type basic_config_level: str
    """
    DEFAULT_CUSTOM_LOGGER = None

    def __new__(cls, *args, **kwargs):
        raise TypeError("SetupLogger cannot be instantiated. Use SetupLogger.setup_logger(...) instead.")

    @classmethod
    def setup_logger(cls, **kwargs) -> Union[logging.Logger, Callable]:
        kwargs.setdefault('log_level_to_stream', 'INFO')
        return_instance = kwargs.pop('return_instance', False)
        logger = kwargs.pop('logger', None)
        if not logger:
            # TODO: make this its own method?
            if cls.DEFAULT_CUSTOM_LOGGER is not None:
                if return_instance:
                    return cls.DEFAULT_CUSTOM_LOGGER(**kwargs)
                elif isinstance(cls.DEFAULT_CUSTOM_LOGGER, Callable):
                    logger = cls.DEFAULT_CUSTOM_LOGGER(**kwargs)()
        logger = cls._check_fallback_logger_config(logger=logger, **kwargs)
        return logger

    @classmethod
    def _check_fallback_logger_config(cls, default_logger_name: Optional[str] = None, **kwargs) -> logging.Logger:
        default_logger_name = default_logger_name or cls.__name__
        logger = kwargs.get('logger', None)
        basic_config_level = kwargs.pop('basic_config_level', 'DEBUG')

        if not logger:
            logger = logging.getLogger(default_logger_name)
        if logger.name == default_logger_name or not logger.hasHandlers():
            logging.basicConfig(level=basic_config_level)
            logger.info(f'using basic config with level: {basic_config_level}')
        else:
            logger.info(f"logger: {logger.name} already has handlers, not using basicConfig")
        logger.info(f"Using logger: {logger.name}")
        return logger


if __name__ == '__main__':
    el = SetupLogger.setup_logger(internal_verbose=True,
                                  return_instance=False,
                                  show_warning_logs_in_console=True)  #, log_level_to_stream=logging.INFO)
    print(type(el))
