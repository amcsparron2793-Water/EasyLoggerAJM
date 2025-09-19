"""
easy_logger.py

logger with already set up generalized file handlers

"""
import logging
from datetime import datetime
from typing import Union, List

from EasyLoggerAJM import _EasyLoggerCustomLogger, ColorizedFormatter, NO_COLORIZER
from EasyLoggerAJM.sub_initializers import (_PropertiesInitializer,
                                            _InternalLoggerMethods,
                                            _HandlerInitializer)


class EasyLoggerInitializer(_PropertiesInitializer,
                            _InternalLoggerMethods,
                            _HandlerInitializer):
    DEFAULT_FORMAT = '%(asctime)s | %(name)s | %(levelname)s | %(message)s'

    def __init__(self, project_name=None, chosen_format=DEFAULT_FORMAT, **kwargs):
        super().__init__(root_log_location=kwargs.get('root_log_location', None))
        self._chosen_format = chosen_format
        self._no_stream_color = kwargs.get('no_stream_color', False)

        self.show_warning_logs_in_console = kwargs.get('show_warning_logs_in_console', False)

        # this variable is to differentiate between the unpacked kwargs,
        # and the list of kwargs that need to be used
        # it is ONLY used in this one situation and should not be reused
        kwargs_passed_in = kwargs
        self._initialize_internal_logger(kwargs_passed_in, **kwargs)

        self._set_initial_properties_value(project_name=project_name, **kwargs)

        self.timestamp = kwargs.get('timestamp', self.log_spec['timestamp'])
        self._set_timestamp_if_different()

        self.formatter, self.stream_formatter = self._setup_formatters(**kwargs)

    def set_timestamp(self, **kwargs):
        """
        This method, `set_timestamp`, is a static method that can be used to set a timestamp for logging purposes.
        The method takes in keyword arguments as parameters.

        Parameters:
            **kwargs: Keyword arguments that can contain the following keys:
                - timestamp (datetime or str, optional): A datetime object or a string representing a timestamp.
                    By default, this key is set to None.

        Returns:
            str: Returns a string representing the set timestamp.

        Raises:
            AttributeError: If the provided timestamp is not a datetime object or a string.

        Notes:
            - If the keyword argument 'timestamp' is provided, the method will return the provided timestamp if it is a
                datetime object or a string representing a timestamp.
            - If the keyword argument 'timestamp' is not provided or is set to None, the method will generate a
                timestamp using the current date and time in ISO format without seconds and colons.

        Example:
            # Set a custom timestamp
            timestamp = set_timestamp(timestamp='2022-01-01 12:34')

            # Generate a timestamp using current date and time
            current_timestamp = set_timestamp()
        """
        timestamp = kwargs.get('timestamp', None)
        if timestamp is not None:
            if isinstance(timestamp, (datetime, str)):
                self._internal_logger.info(f"timestamp set to {timestamp}")
                return timestamp
            else:
                try:
                    raise AttributeError("timestamp must be a datetime object or a string")
                except AttributeError as e:
                    self._internal_logger.error(e, exc_info=True)
                    raise e from None
        else:
            timestamp = datetime.now().isoformat(timespec='minutes').replace(':', '')
            self._internal_logger.info(f"timestamp set to {timestamp}")
            return timestamp

    def _set_timestamp_if_different(self):
        """Set the timestamp if it's different from the log specification."""
        if self.timestamp != self._log_spec.get('timestamp'):
            self.timestamp = self.set_timestamp(timestamp=self.timestamp)

    def _setup_formatters(self, **kwargs) -> (logging.Formatter, Union[ColorizedFormatter, logging.Formatter]):
        formatter = kwargs.get('formatter', logging.Formatter(self._chosen_format))

        if not self._no_stream_color:
            stream_formatter = kwargs.get('stream_formatter', ColorizedFormatter(self._chosen_format))
        else:
            stream_formatter = kwargs.get('stream_formatter', logging.Formatter(self._chosen_format))
        return formatter, stream_formatter

    def _initialize_internal_logger(self, internal_loggable_attrs: dict, **kwargs):
        self._internal_logger = self._setup_internal_logger(verbose=kwargs.get('internal_verbose', False))

        self._log_attributes_internal(internal_loggable_attrs)
        self._internal_logger.info(f'show_warning_logs_in_console set to '
                                   f'{self.show_warning_logs_in_console}')


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
        self._internal_logger.info('no passed in logger detected')
        logging.setLoggerClass(logger_class)
        self._internal_logger.info(f'logger class set to \'{logger_class.__name__}\'')
        # Create a logger with a specified name
        self.logger = logging.getLogger(kwargs.get('logger_name', 'logger'))
        self._internal_logger.info(f'logger created with name set to \'{self.logger.name}\'')
        return self.logger

    def initialize_logger(self, logger=None, **kwargs) -> Union[logging.Logger, _EasyLoggerCustomLogger]:
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
        # set the logger level back to DEBUG, so it handles all messages
        self.logger.setLevel(10)
        self._internal_logger.info(f'logger level set back to {self.logger.level}')
        self.logger.info(f"Starting {self.project_name} with the following handlers: "
                         f"{self._get_level_handler_string(self.logger.handlers)}")
        if not self._no_stream_color and NO_COLORIZER:
            self.logger.warning("colorizer not available, logs may not be colored as expected.")
        self._internal_logger.info("final logger initialized")
        # print("logger initialized")


if __name__ == '__main__':
    el = EasyLogger(internal_verbose=True,
                    show_warning_logs_in_console=True)#, log_level_to_stream=logging.INFO)
    el.logger.info("this is an info message", print_msg=True)
