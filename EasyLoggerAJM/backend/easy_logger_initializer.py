import logging
from datetime import datetime
from typing import Union

from EasyLoggerAJM.logger_parts import ColorizedFormatter
from EasyLoggerAJM.sub_initializers import _PropertiesInitializer, _InternalLoggerMethods, _HandlerInitializer


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
