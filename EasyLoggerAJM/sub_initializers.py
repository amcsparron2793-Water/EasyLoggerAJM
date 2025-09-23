import logging
from abc import abstractmethod
from datetime import datetime
from pathlib import Path
from typing import Union, Optional

from EasyLoggerAJM import (ConsoleOneTimeFilter,
                           __project_root__, __project_name__)


class _LogSpec:
    """
        Class `_LogSpec` is a container for predefined log specifications and timestamp formats,
        organized by time intervals (daily, hourly, and minute-based).
        These specifications are auto-generated based on the current date and time.

        Attributes:
            MINUTE_LOG_SPEC_FORMAT : tuple
                A tuple containing the current date (ISO formatted) and time up to minutes in string format without colons.
            MINUTE_TIMESTAMP : str
                A compact ISO formatted timestamp up to minutes excluding colons.

            HOUR_LOG_SPEC_FORMAT : tuple
                A tuple containing the current date (ISO formatted) and time truncated to the hour in string format
                    (e.g., "1400" for 2 PM).
            HOUR_TIMESTAMP : str
                A compact ISO formatted timestamp indicating the hour without colons.

            DAILY_LOG_SPEC_FORMAT : str
                The current date as an ISO formatted string.
            DAILY_TIMESTAMP : str
                The current date truncated to the hour component formatted in ISO standard.

            LOG_SPECS : dict
                A dictionary containing log specifications for daily, hourly, and minute time intervals.
                    Each key corresponds to the time interval ('daily', 'hourly', 'minute') and its value is another dictionary with:
                    - 'name': Name of the log interval.
                    - 'format': Predefined time format of the given interval.
                    - 'timestamp': Compact timestamp matching the logical interval.
    """

    # TODO: replace these with checks using logging.getlevelname()
    INT_TO_STR_LOGGER_LEVELS = {
        10: 'DEBUG',
        20: 'INFO',
        30: 'WARNING',
        40: 'ERROR',
        50: 'CRITICAL'
    }

    STR_TO_INT_LOGGER_LEVELS = {
        'DEBUG': 10,
        'INFO': 20,
        'WARNING': 30,
        'ERROR': 40,
        'CRITICAL': 50
    }

    # this is a tuple of the date and the time down to the minute
    MINUTE_LOG_SPEC_FORMAT = (datetime.now().date().isoformat(),
                              ''.join(datetime.now().time().isoformat().split('.')[0].split(":")[:-1]))
    MINUTE_TIMESTAMP = datetime.now().isoformat(timespec='minutes').replace(':', '')

    HOUR_LOG_SPEC_FORMAT = datetime.now().date().isoformat(), (
            datetime.now().time().isoformat().split('.')[0].split(':')[0] + '00')
    HOUR_TIMESTAMP = datetime.now().time().isoformat().split('.')[0].split(':')[0] + '00'

    DAILY_LOG_SPEC_FORMAT = datetime.now().date().isoformat()
    DAILY_TIMESTAMP = datetime.now().isoformat(timespec='hours').split('T')[0]

    LOG_SPECS = {
        'daily': {
            'name': 'daily',
            'format': DAILY_LOG_SPEC_FORMAT,
            'timestamp': DAILY_TIMESTAMP
        },
        'hourly': {
            'name': 'hourly',
            'format': HOUR_LOG_SPEC_FORMAT,
            'timestamp': HOUR_TIMESTAMP
        },
        'minute': {
            'name': 'minute',
            'format': MINUTE_LOG_SPEC_FORMAT,
            'timestamp': MINUTE_TIMESTAMP
        }
    }


# noinspection PyUnresolvedReferences
class _InternalLoggerMethods:
    """
    This class contains internal utility methods for configuring and logging internal
    operations of the logger. These methods are designed for internal use and handle
    logging of initial attributes, setting up file and stream handlers, and initializing
    the internal logger.

    Methods
    -------
    _log_attributes_internal(logger_kwargs)
        Logs the initial state of key instance attributes and any additional keyword
        arguments passed during initialization.

    _setup_internal_logger_handlers(verbose=False)
        Sets up handlers for the internal logger, including a file handler to log into
        a predefined file and, optionally, a stream handler for console output.

    _setup_internal_logger(**kwargs)
        Initializes and configures the internal logger with a designated logging level
        and handlers. Returns the initialized logger.
    """

    def _log_attributes_internal(self, logger_kwargs):
        """
        Logs internal attributes and initialization parameters for debugging purposes.

        :param logger_kwargs: Arguments passed during the initialization of the instance.
        :type logger_kwargs: dict
        """
        self._internal_logger.info(f"root_log_location set to {self._root_log_location}")
        self._internal_logger.info(f"chosen_format set to {self._chosen_format}")
        self._internal_logger.info(f"no_stream_color set to {self._no_stream_color}")
        self._internal_logger.info(f"kwargs passed to __init__ are {logger_kwargs}")

    def _setup_internal_logger_handlers(self, verbose=False):
        """
        :param verbose: Indicates whether to enable verbose logging. If True, adds a StreamHandler to log messages to the console.
        :type verbose: bool
        :return: None
        :rtype: None
        """
        log_file_path = Path(self._root_log_location,
                             'EasyLogger_internal.log'.replace('\\', '/'))
        fmt = logging.Formatter(self._chosen_format)

        log_file_mode = 'w'
        if not log_file_path.exists():
            Path(self._root_log_location).mkdir(parents=True, exist_ok=True)
        h = logging.FileHandler(log_file_path, mode=log_file_mode)
        h.setFormatter(fmt)
        self._internal_logger.addHandler(h)

        if verbose:
            h2 = logging.StreamHandler()
            h2.setFormatter(fmt)
            self._internal_logger.addHandler(h2)

    def _setup_internal_logger(self, **kwargs):
        """
        Sets up the internal logger for the application.

        :param kwargs: Optional keyword arguments for configuring the logger.
            The key 'verbose' can be used to enable or disable verbose logging.
        :return: The configured internal logger instance.
        :rtype: logging.Logger
        """
        self._internal_logger = logging.getLogger('EasyLogger_internal')
        self._internal_logger.propagate = False
        self._internal_logger.setLevel(10)
        self._setup_internal_logger_handlers(verbose=kwargs.get('verbose', False))

        self._internal_logger.info("internal logger initialized")
        return self._internal_logger


class _PropertiesInitializer(_LogSpec):
    # TODO: test me/ see what it resolves to if EasyLogger is just an imported module?
    ROOT_LOG_LOCATION_DEFAULT = Path(__project_root__, 'logs').resolve()

    def __init__(self, root_log_location=None):
        self._file_logger_levels = None
        self._project_name = None
        self._log_spec = None
        # noinspection SpellCheckingInspection
        self._inner_log_fstructure = None
        self._log_location = None
        self._root_log_location = root_log_location
        if self._root_log_location is None:
            self._root_log_location = self.__class__.ROOT_LOG_LOCATION_DEFAULT

    @classmethod
    def get_default_file_logger_levels(cls):
        return [cls.STR_TO_INT_LOGGER_LEVELS["DEBUG"],
                cls.STR_TO_INT_LOGGER_LEVELS["INFO"],
                cls.STR_TO_INT_LOGGER_LEVELS["ERROR"]]

    def _set_initial_properties_value(self, **kwargs):
        # properties
        self.file_logger_levels = kwargs.get('file_logger_levels', [])
        self.project_name = kwargs.get('project_name', None)
        self.log_spec = kwargs.get('log_spec', None)

    def _validate_file_logger_levels(self, fll: list):
        if [x for x in fll
            if x in self.__class__.STR_TO_INT_LOGGER_LEVELS
               or x in self.__class__.INT_TO_STR_LOGGER_LEVELS]:
            if any([isinstance(x, str) and not x.isdigit() for x in fll]):
                fll = [self.__class__.STR_TO_INT_LOGGER_LEVELS[x] for x in
                       fll]
            elif any([isinstance(x, int) for x in fll]):
                pass
        return fll

    @property
    def file_logger_levels(self):
        if not self._file_logger_levels:
            self._file_logger_levels = self.get_default_file_logger_levels()
        return self._file_logger_levels

    @file_logger_levels.setter
    def file_logger_levels(self, value):
        if not value:
            self._file_logger_levels = self.get_default_file_logger_levels()
        else:
            self._file_logger_levels = self._validate_file_logger_levels(value)
        self._internal_logger.info(f"file_logger_levels set to {self._file_logger_levels}")

    @property
    def project_name(self):
        """
        Getter for the project_name property.

        Returns the name of the project. If the project name has not been set previously,
         it is determined based on the filename of the current file.

        Returns:
            str: The name of the project.
        """
        return self._project_name

    @project_name.setter
    def project_name(self, value):
        self._project_name = value
        if not self._project_name:
            self._project_name = __project_name__
        self._internal_logger.info(f"project_name set to {self._project_name}")

    # noinspection SpellCheckingInspection
    @property
    def inner_log_fstructure(self):
        """
        Getter method for retrieving the inner log format structure.

        This method checks the type of the log_spec['format'] attribute and returns
            the inner log format structure accordingly.
        If the log_spec['format'] is of type str, the inner log format structure is set as
            "{}".format(self.log_spec['format']).
        If the log_spec['format'] is of type tuple, the inner log format structure is set as
            "{}/{}".format(self.log_spec['format'][0], self.log_spec['format'][1]).

        Returns:
            str: The inner log format structure.
        """
        if isinstance(self.log_spec['format'], str):
            self._inner_log_fstructure = "{}".format(self.log_spec['format'])
        elif isinstance(self.log_spec['format'], tuple):
            self._inner_log_fstructure = "{}/{}".format(self.log_spec['format'][0], self.log_spec['format'][1])
        return self._inner_log_fstructure

    @property
    def log_location(self) -> Path:
        """
        Getter method for retrieving the log_location property.

        Returns:
            str: The absolute path of the log location.
        """
        self._log_location = Path(self._root_log_location,
                                  self.inner_log_fstructure)
        if self._log_location.is_dir():
            pass
        else:
            self._log_location.mkdir(parents=True, exist_ok=True)
        return self._log_location

    @property
    def log_spec(self):
        return self._log_spec

    @log_spec.setter
    def log_spec(self, value):
        if value is None:
            value = self.LOG_SPECS['minute']
        if isinstance(value, dict):
            try:
                self._log_spec = self.LOG_SPECS[value['name'].lower()]
            except KeyError:
                raise KeyError("if log_spec is given as a dictionary, "
                               "it must include the key/value for 'name'."
                               " otherwise it should be passed in as a string.") from None
        elif isinstance(value, str):
            # since all the keys are in lower case, the passed in self._log_spec should be set to .lower()
            if value.lower() in list(self.__class__.LOG_SPECS.keys()):
                self._log_spec = self.LOG_SPECS[value.lower()]
            else:
                raise AttributeError(
                    f"log spec must be one of the following: {str(list(self.LOG_SPECS.keys()))[1:-1]}.")
        else:
            raise AttributeError("log spec value must be a string or a dict")


class _HandlerInitializer(_LogSpec):
    # noinspection PyTypeChecker
    def __init__(self):
        self._internal_logger: logging.Logger = None
        self.logger: logging.Logger = None
        self.formatter: logging.Formatter = None
        self.stream_formatter: logging.Formatter = None
        self.timestamp: str = None

    @property
    @abstractmethod
    def file_logger_levels(self):
        ...

    @property
    @abstractmethod
    def log_location(self) -> Path:
        ...

    @property
    @abstractmethod
    def project_name(self):
        ...

    def _add_filter_to_file_handler(self, handler: logging.FileHandler):
        """
        this is meant to be overwritten in a subclass to allow for filters
        to be added to file handlers without rewriting the entire method.

        Ex: new_filter = MyFilter()
        handler.addFilter(new_filter)
        :param handler:
        :type handler:
        :return:
        :rtype:
        """
        pass

    def _add_filter_to_stream_handler(self, handler: logging.StreamHandler):
        """
        this is meant to be overwritten in a subclass to allow for filters
        to be added to stream handlers without rewriting the entire method.

        Ex: new_filter = MyFilter()
        handler.addFilter(new_filter)

        :param handler:
        :type handler:
        :return:
        :rtype:
        """
        pass

    def make_file_handlers(self):
        """
        This method is used to create file handlers for the logger.
        It sets the logging level for each handler based on the file_logger_levels attribute.
        It also sets the log file location based on the logger level, project name, and timestamp.

        Parameters:
            self

        Returns:
            None

        Raises:
            None
        """
        self._internal_logger.info("creating file handlers for each logger level and log file location")
        for lvl in self.file_logger_levels:
            self.logger.setLevel(lvl)
            level_string = self.__class__.INT_TO_STR_LOGGER_LEVELS[self.logger.level]

            log_path = Path(self.log_location, '{}-{}-{}.log'.format(level_string,
                                                                     self.project_name, self.timestamp))

            # Create a file handler for the logger, and specify the log file location
            file_handler = logging.FileHandler(log_path)
            # Set the logging format for the file handler
            file_handler.setFormatter(self.formatter)
            file_handler.setLevel(self.logger.level)
            # doesn't do anything unless subclassed
            self._add_filter_to_file_handler(file_handler)

            # Add the file handlers to the loggers
            self.logger.addHandler(file_handler)

    def create_stream_handler(self, log_level_to_stream=logging.WARNING, **kwargs):
        """
        Creates and configures a StreamHandler for warning messages to print to the console.

        This method creates a StreamHandler and sets its logging format.
        The StreamHandler is then set to handle only warning level log messages.

        A one-time filter is added to the StreamHandler to ensure that warning messages are only printed to the console once.

        Finally, the StreamHandler is added to the logger.

        Note: This method assumes that `self.logger` and `self.formatter` are already defined.
        """

        if (log_level_to_stream not in self.__class__.INT_TO_STR_LOGGER_LEVELS
                and log_level_to_stream not in self.__class__.STR_TO_INT_LOGGER_LEVELS):
            raise ValueError(f"log_level_to_stream must be one of {list(self.__class__.STR_TO_INT_LOGGER_LEVELS)} or "
                             f"{list(self.__class__.INT_TO_STR_LOGGER_LEVELS)}, "
                             f"not {log_level_to_stream}")

        self._internal_logger.info(
            f"creating StreamHandler() for {logging.getLevelName(log_level_to_stream)} messages to print to console")

        use_one_time_filter = kwargs.get('use_one_time_filter', True)
        self._internal_logger.info(f"use_one_time_filter set to {use_one_time_filter}")

        # Create a stream handler for the logger
        stream_handler = kwargs.get('stream_handler_instance', logging.StreamHandler())
        # Set the logging format for the stream handler
        stream_handler.setFormatter(self.stream_formatter)
        stream_handler.setLevel(log_level_to_stream)
        if use_one_time_filter:
            # set the one time filter, so that log_level_to_stream messages will only be printed to the console once.
            one_time_filter = ConsoleOneTimeFilter()
            stream_handler.addFilter(one_time_filter)

        # doesn't do anything unless subclassed
        self._add_filter_to_stream_handler(stream_handler)

        # Add the stream handler to logger
        self.logger.addHandler(stream_handler)
        self._internal_logger.info(
            f"StreamHandler() for {logging.getLevelName(log_level_to_stream)} messages added. "
            f"{logging.getLevelName(log_level_to_stream)}s will be printed to console")
        if use_one_time_filter:
            self._internal_logger.info(f'Added filter {self.logger.handlers[-1].filters[0].name} to StreamHandler()')

    def _create_handler_instance(self, handler_to_create, handler_args, **kwargs):
        if handler_args is not None and isinstance(handler_to_create, type):
            instance = handler_to_create(**handler_args, **kwargs)
            self._internal_logger.info(f"{handler_to_create.__class__.__name__} handler created")
            self._internal_logger.debug(f"handler has the following args {dict(**handler_args, **kwargs)}")
        else:
            instance = handler_to_create
            self._internal_logger.info(f"instance of {handler_to_create.__class__.__name__} handler detected, moving to set up")
        return instance

    def create_other_handlers(self, handler_to_create: Union[type(logging.Handler), set[type(logging.Handler)]] = None,
                              handler_args: Optional[dict] = None, **kwargs):
        if handler_to_create and (callable(handler_to_create) or isinstance(handler_to_create, logging.Handler)):
            self._internal_logger.info(f"creating {handler_to_create.__class__.__name__} handler")
            instance = self._create_handler_instance(handler_to_create, handler_args, **kwargs)
            self._setup_other_handler(instance, **kwargs)
        else:
            self._internal_logger.debug(f"no other handlers created")

    def _setup_other_handler(self, handler_instance: logging.Handler, **kwargs):
        handler_instance.setLevel(kwargs.get('logging_level', self.logger.level))
        self._internal_logger.info(f"handler level set to {logging.getLevelName(handler_instance.level)}")

        handler_instance.setFormatter(kwargs.get('formatter', self.formatter))
        self._internal_logger.info(f"handler formatter set to {handler_instance.formatter.__class__.__name__}")

        self.logger.addHandler(handler_instance)
        self._internal_logger.info(f"{handler_instance.__class__.__name__} handler added")