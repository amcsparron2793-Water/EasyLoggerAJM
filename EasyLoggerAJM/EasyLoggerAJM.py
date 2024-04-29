"""
EasyLoggerAJM.py

logger with already set up generalized file handlers

"""
import logging
from datetime import datetime
from os import makedirs
from os.path import join, isdir


class EasyLogger:
    def __init__(self, project_name=None, root_log_location="../logs",
                 chosen_format='%(asctime)s | %(name)s | %(levelname)s | %(message)s', logger=None, **kwargs):

        self._project_name = project_name
        self._root_log_location = root_log_location
        self._inner_log_fstructure = None
        self._log_location = None

        if kwargs:
            if 'timestamp' in kwargs and (isinstance(kwargs['timestamp'], datetime)
                                          or isinstance(kwargs['timestamp'], str)):
                self.timestamp = kwargs['timestamp']
            else:
                raise AttributeError("timestamp must be a datetime object or a string")
        else:
            self.timestamp = datetime.now().isoformat(timespec='minutes').replace(':',
                                                                              '')  # datetime.now().date().isoformat()
        self.formatter = logging.Formatter(chosen_format)
        self.logger_levels = ["DEBUG", "INFO", "ERROR"]
        if not logger:
            # Create a logger with a specified name and make sure propagate is True
            self.logger = logging.getLogger('logger')
        else:
            self.logger: logging.getLogger = logger
        self.logger.propagate = True

        self.make_file_handlers()

        # set the logger level back to DEBUG, so it handles all messages
        self.logger.setLevel(10)
        self.logger.info(f"Starting {project_name} with the following FileHandlers:"
                         f"{self.logger.handlers[0]}"
                         f"{self.logger.handlers[1]}"
                         f"{self.logger.handlers[2]}")
        # print("logger initialized")

    @classmethod
    def UseLogger(cls, **kwargs):
        return cls(**kwargs, logger=logging.getLogger('logger'))

    @property
    def project_name(self):
        return self._project_name

    @project_name.getter
    def project_name(self):
        if self._project_name:
            pass
        else:
            self._project_name = __file__.split('\\')[-1].split(".")[0]

        return self._project_name

    @property
    def inner_log_fstructure(self):
        return self._inner_log_fstructure

    @inner_log_fstructure.getter
    def inner_log_fstructure(self):
        self._inner_log_fstructure = "{}/{}".format(datetime.now().date().isoformat(),
                                                    ''.join(
                                                        datetime.now().time().isoformat().split(
                                                            '.')[0].split(":")[:-1]))
        return self._inner_log_fstructure

    @property
    def log_location(self):
        return self._log_location

    @log_location.getter
    def log_location(self):
        self._log_location = join(self._root_log_location, self.inner_log_fstructure)
        if isdir(self._log_location):
            pass
        else:
            makedirs(self._log_location)
        return self._log_location

    def make_file_handlers(self):
        """ Add three filehandlers to the logger then set the log level to debug.
        This way all messages will be sorted into their appropriate spots"""
        for lvl in self.logger_levels:
            self.logger.setLevel(lvl)
            if self.logger.level == 10:
                level_string = "DEBUG"
            elif self.logger.level == 20:
                level_string = "INFO"
            elif self.logger.level == 40:
                level_string = "ERROR"
            else:
                print("other logger level detected, defaulting to DEBUG")
                level_string = "DEBUG"
            log_path = join(self.log_location, '{}-{}-{}.log'.format(level_string, self.project_name, self.timestamp))

            # Create a file handler for the logger, and specify the log file location
            file_handler = logging.FileHandler(log_path)
            # Set the logging format for the file handler
            file_handler.setFormatter(self.formatter)
            file_handler.setLevel(self.logger.level)
            # Add the file handlers to the loggers
            self.logger.addHandler(file_handler)
