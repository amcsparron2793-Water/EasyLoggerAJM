"""
EasyLoggerAJM.py

logger with already set up generalized file handlers

"""
import logging
from datetime import datetime
from os import makedirs
from os.path import join, isdir


class ConsoleOneTimeFilter(logging.Filter):
    def __init__(self, name="ConsoleWarnOneTime"):
        super().__init__(name)
        self.logged_messages = set()

    def filter(self, record):
        # We only log the message if it has not been logged before
        if record.msg not in self.logged_messages:
            self.logged_messages.add(record.msg)
            return True
        return False


class EasyLogger:
    """
    This module provides the EasyLogger class, which is a simple logging utility for Python.

    class EasyLogger:
        Represents a logging utility that can be used to log messages to various log files.

        Methods:
        - __init__(self, project_name=None, root_log_location="../logs",
                 chosen_format=DEFAULT_FORMAT, logger=None, **kwargs):
            Initializes a new instance of the EasyLogger class.

        - make_file_handlers(self):
            Adds three file handlers to the logger and sets the log level to debug.

        - set_timestamp(self, **kwargs):
            Sets the timestamp for the log messages.

        Properties:
        - project_name:
            Gets the project name for the logger.

        - inner_log_fstructure:
            Gets the inner log file structure for the logger.

        - log_location:
            Gets the log location for the logger.

        Static Methods:
        - UseLogger(cls, **kwargs):
            Creates a new instance of the EasyLogger class and returns it.

    Usage:
        # Create a new EasyLogger instance
        logger = EasyLogger(project_name="MyProject", root_log_location="../logs")

        # Log an info message
        logger.logger.info("This is an info message")

        # Log a debug message
        logger.logger.debug("This is a debug message")

        # Log an error message
        logger.logger.error("This is an error message")
    """
    DEFAULT_FORMAT = '%(asctime)s | %(name)s | %(levelname)s | %(message)s'

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

    def __init__(self, project_name=None, root_log_location="../logs",
                 chosen_format=DEFAULT_FORMAT, logger=None, **kwargs):

        self._log_spec = kwargs.get('log_spec', None)

        self._project_name = project_name
        self._root_log_location = root_log_location
        self._inner_log_fstructure = None
        self._log_location = None
        self.show_warning_logs_in_console = kwargs.get('show_warning_logs_in_console', False)

        self.timestamp = kwargs.get('timestamp', self.log_spec['timestamp'])
        if self.timestamp != self.log_spec['timestamp']:
            self.timestamp = self.set_timestamp(**{'timestamp': self.timestamp})

        self.formatter = logging.Formatter(chosen_format)
        self._file_logger_levels = kwargs.get('file_logger_levels', [])

        if not logger:
            # Create a logger with a specified name and make sure propagate is True
            self.logger = logging.getLogger('logger')
        else:
            self.logger: logging.getLogger = logger
        self.logger.propagate = True

        self.make_file_handlers()
        if self.show_warning_logs_in_console:
            self.create_stream_handler()

        # set the logger level back to DEBUG, so it handles all messages
        self.logger.setLevel(10)
        self.logger.info(f"Starting {project_name} with the following FileHandlers:"
                         f"{self.logger.handlers[0]}"
                         f"{self.logger.handlers[1]}"
                         f"{self.logger.handlers[2]}")
        # print("logger initialized")

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
        return cls(**kwargs, logger=logging.getLogger('logger'))

    @property
    def file_logger_levels(self):
        if self._file_logger_levels:
            if [x for x in self._file_logger_levels
                if x in self.STR_TO_INT_LOGGER_LEVELS
                   or x in self.INT_TO_STR_LOGGER_LEVELS]:
                #pass
                if any([isinstance(x, str) and not x.isdigit() for x in self._file_logger_levels]):
                    self._file_logger_levels = [self.STR_TO_INT_LOGGER_LEVELS[x] for x in self._file_logger_levels]
                elif any([isinstance(x, int) for x in self._file_logger_levels]):
                    pass
        else:
            self._file_logger_levels = [self.STR_TO_INT_LOGGER_LEVELS["DEBUG"],
                                        self.STR_TO_INT_LOGGER_LEVELS["INFO"],
                                        self.STR_TO_INT_LOGGER_LEVELS["ERROR"]]
        return self._file_logger_levels

    @property
    def project_name(self):
        """
        This is a Python method called `project_name` that is a property of a class. It returns the value of a private variable `_project_name` in the class.

        Parameters:
            None

        Returns:
            A string representing the project name.

        Example usage:
            ```
            obj = ClassName()
            result = obj.project_name
            ```"""
        return self._project_name

    @project_name.getter
    def project_name(self):
        """
        Getter for the project_name property.

        Returns the name of the project. If the project name has not been set previously, it is determined based on the filename of the current file.

        Returns:
            str: The name of the project.
        """
        if self._project_name:
            pass
        else:
            self._project_name = __file__.split('\\')[-1].split(".")[0]

        return self._project_name

    @property
    def inner_log_fstructure(self):
        """
        This property returns the inner log fstructure of an object.

        Returns:
            The inner log fstructure.

        """
        return self._inner_log_fstructure

    @inner_log_fstructure.getter
    def inner_log_fstructure(self):
        """
        Getter method for retrieving the inner log format structure.

        This method checks the type of the log_spec['format'] attribute and returns the inner log format structure accordingly.
        If the log_spec['format'] is of type str, the inner log format structure is set as "{}".format(self.log_spec['format']).
        If the log_spec['format'] is of type tuple, the inner log format structure is set as "{}/{}".format(self.log_spec['format'][0], self.log_spec['format'][1]).

        Returns:
            str: The inner log format structure.
        """
        if isinstance(self.log_spec['format'], str):
            self._inner_log_fstructure = "{}".format(self.log_spec['format'])
        elif isinstance(self.log_spec['format'], tuple):
            self._inner_log_fstructure = "{}/{}".format(self.log_spec['format'][0], self.log_spec['format'][1])
        return self._inner_log_fstructure

    @property
    def log_location(self):
        """
        This is a property method named `log_location` which returns the value of `_log_location` attribute. It can be accessed using dot notation.

        Example:
            obj = ClassName()
            print(obj.log_location)  # Output: value of _log_location attribute

        Returns:
            The value of `_log_location` attribute.

        """
        return self._log_location

    @log_location.getter
    def log_location(self):
        """
        Getter method for retrieving the log_location property.

        Returns:
            str: The absolute path of the log location.
        """
        self._log_location = join(self._root_log_location, self.inner_log_fstructure)
        if isdir(self._log_location):
            pass
        else:
            makedirs(self._log_location)
        return self._log_location

    @property
    def log_spec(self):
        if self._log_spec is not None:
            if isinstance(self._log_spec, dict):
                try:
                    self._log_spec = self._log_spec['name']
                except KeyError:
                    raise KeyError("if log_spec is given as a dictionary, "
                                   "it must include the key/value for 'name'."
                                   " otherwise it should be passed in as a string.") from None

            elif isinstance(self._log_spec, str):
                pass

            # since all the keys are in lower case, the passed in self._log_spec should be set to .lower()
            if self._log_spec.lower() in list(self.LOG_SPECS.keys()):
                self._log_spec = self.LOG_SPECS[self._log_spec.lower()]
            else:
                raise AttributeError(
                    f"log spec must be one of the following: {str(list(self.LOG_SPECS.keys()))[1:-1]}.")
        else:
            self._log_spec = self.LOG_SPECS['minute']
        return self._log_spec

    @staticmethod
    def set_timestamp(**kwargs):
        """
        This method, `set_timestamp`, is a static method that can be used to set a timestamp for logging purposes. The method takes in keyword arguments as parameters.

        Parameters:
            **kwargs (dict): Keyword arguments that can contain the following keys:
                - timestamp (datetime or str, optional): A datetime object or a string representing a timestamp. By default, this key is set to None.

        Returns:
            str: Returns a string representing the set timestamp.

        Raises:
            AttributeError: If the provided timestamp is not a datetime object or a string.

        Notes:
            - If the keyword argument 'timestamp' is provided, the method will return the provided timestamp if it is a datetime object or a string representing a timestamp.
            - If the keyword argument 'timestamp' is not provided or is set to None, the method will generate a timestamp using the current date and time in ISO format without seconds and colons.

        Example:
            # Set a custom timestamp
            timestamp = set_timestamp(timestamp='2022-01-01 12:34')

            # Generate a timestamp using current date and time
            current_timestamp = set_timestamp()
        """
        timestamp = kwargs.get('timestamp', None)
        if timestamp is not None:
            if isinstance(timestamp, (datetime, str)):
                return timestamp
            else:
                raise AttributeError("timestamp must be a datetime object or a string")
        else:
            return datetime.now().isoformat(timespec='minutes').replace(':', '')

    def make_file_handlers(self):
        """
        This method is used to create file handlers for the logger.
        It sets the logging level for each handler based on the file_logger_levels attribute.
        It also sets the log file location based on the logger level, project name, and timestamp.

        Parameters:
            None

        Returns:
            None

        Raises:
            None
        """
        for lvl in self.file_logger_levels:
            self.logger.setLevel(lvl)
            level_string = self.INT_TO_STR_LOGGER_LEVELS[self.logger.level]

            log_path = join(self.log_location, '{}-{}-{}.log'.format(level_string, self.project_name, self.timestamp))

            # Create a file handler for the logger, and specify the log file location
            file_handler = logging.FileHandler(log_path)
            # Set the logging format for the file handler
            file_handler.setFormatter(self.formatter)
            file_handler.setLevel(self.logger.level)
            # Add the file handlers to the loggers
            self.logger.addHandler(file_handler)

    def create_stream_handler(self, log_level_to_stream="WARNING", **kwargs):
        """
        Creates and configures a StreamHandler for warning messages to print to the console.

        This method creates a StreamHandler and sets its logging format.
        The StreamHandler is then set to handle only warning level log messages.

        A one-time filter is added to the StreamHandler to ensure that warning messages are only printed to the console once.

        Finally, the StreamHandler is added to the logger.

        Note: This method assumes that `self.logger` and `self.formatter` are already defined.
        """

        if log_level_to_stream not in self.INT_TO_STR_LOGGER_LEVELS and log_level_to_stream not in self.STR_TO_INT_LOGGER_LEVELS:
            raise ValueError(f"log_level_to_stream must be one of {list(self.STR_TO_INT_LOGGER_LEVELS)} or "
                             f"{list(self.INT_TO_STR_LOGGER_LEVELS)}, "
                             f"not {log_level_to_stream}")

        self.logger.info(f"creating StreamHandler() for {log_level_to_stream} messages to print to console")

        use_one_time_filter = kwargs.get('use_one_time_filter', True)

        # Create a stream handler for the logger
        stream_handler = logging.StreamHandler()
        # Set the logging format for the stream handler
        stream_handler.setFormatter(self.formatter)
        stream_handler.setLevel(log_level_to_stream)
        if use_one_time_filter:
            # set the one time filter, so that log_level_to_stream messages will only be printed to the console once.
            one_time_filter = ConsoleOneTimeFilter()
            stream_handler.addFilter(one_time_filter)

        # Add the stream handler to logger
        self.logger.addHandler(stream_handler)
        self.logger.info(
            f"StreamHandler() for {log_level_to_stream} messages added. "
            f"{log_level_to_stream}s will be printed to console")
        if use_one_time_filter:
            self.logger.info(f'Added filter {self.logger.handlers[-1].filters[0].name} to StreamHandler()')
