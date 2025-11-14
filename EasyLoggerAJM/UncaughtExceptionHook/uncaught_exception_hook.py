import sys
from logging import basicConfig, error
from pathlib import Path
from . import UncaughtLogger, UncaughtLoggerEmail
from ..backend import LogFilePrepError


def clear_screen():
    import os
    if os.name == 'nt':  # For Windows
        os.system('cls')
    else:  # For Unix/Linux/macOS
        os.system('clear')


class UncaughtExceptionHook:
    """
    Class to handle uncaught exceptions in a Python application,
    log them to a file, send email notifications, and exit the application gracefully.

    Class Components:
    1. Initialization:
       - Initializes an instance of `UncaughtLogger`.
       - Prepares a logger with an email handler for administrator notification.
       - Defines the log file path for unhandled exceptions.

    2. Methods:
       - `_basic_log_to_file(exc_type, exc_value, tb)`:
           Logs the details of the uncaught exception into a specified file.
           Ensures the existing log file is removed if already present to avoid conflicts.
           Handles any errors during logging gracefully.

       - `show_exception_and_exit(exc_type, exc_value, tb)`:
           Handles the uncaught exception by:
           a. Logging the exception details using `_basic_log_to_file`.
           b. Calling the default exception hook to print the traceback information to the console.
           c. Logging the exception using the uncaught logger.
           d. Initializing a new email notification via the associated emailer.
           e. Displaying a console message to inform where the exception logs are stored.
           f. Prompting the user to press enter to exit the program.
           g. Exiting the application with a status code of -1.

    Use example:
        in __init__.py:
        ueh = UncaughtExceptionHook()

        sys.excepthook = ueh.show_exception_and_exit
    """
    UNCAUGHT_LOG_MSG = ('\n********\n if exception could be logged, it is logged in \'{log_file_name}\' '
                        'even if it does not appear in other log files \n********\n')

    def __init__(self, **kwargs):
        self.uncaught_logger_class = kwargs.pop('uncaught_logger_class', UncaughtLogger)
        self.uncaught_logger_class = self.uncaught_logger_class(logger_name='UncaughtExceptionLogger',
                                   **kwargs)
        self.uc_logger = self.uncaught_logger_class()

        self.log_file_name = Path('./unhandled_exception.log')

    @staticmethod
    def wait_for_key_and_exit():
        try:
            input("Press enter to exit.")
        except (UnicodeDecodeError, EOFError, OSError):
            # Fallback: use msvcrt on Windows or a simple delay on other platforms
            try:
                clear_screen()
                import msvcrt
                print("Press any key to exit...")
                msvcrt.getch()
            except ImportError:
                # On non-Windows systems or if msvcrt fails, just wait briefly
                import time
                print("Exiting in 3 seconds...")
                time.sleep(3)

        sys.exit(-1)

    def _check_and_initialize_new_email_file(self):
        if hasattr(self.uncaught_logger_class, 'emailer') and hasattr(self.uncaught_logger_class.emailer,
                                                                      'initialize_new_email'):
            self.uncaught_logger_class.emailer.initialize_new_email()

    def _basic_log_to_file(self, exc_type, exc_value, tb):
        if self.log_file_name.is_file():
            self.log_file_name.unlink()
        else:
            pass
        try:
            basicConfig(filename=self.log_file_name, level='ERROR')
            error("Uncaught exception", exc_info=(exc_type, exc_value, tb))
        except Exception:
            print('could not log unhandled exception to file due to error.')

    def _log_exception(self, exc_type, exc_value, tb):
        self.uc_logger.error(msg='Uncaught exception', exc_info=(exc_type, exc_value, tb),
                             extra={'uncaught_exception': True})

    def show_exception_and_exit(self, exc_type, exc_value, tb):
        """
        This code defines a function `show_exception_and_exit` which is used to handle uncaught exceptions in
         a Python program. When an uncaught exception occurs, this function is called with the exception type,
          exception value, and traceback as arguments.

        The function performs the following steps:

        1. It imports the necessary modules: `basicConfig` and `error` from the `logging` module, and `Path` from the `pathlib` module.

        2. It creates a `Path` object called `log_file_name` with the path './unhandled_exception.log'.

        3. If the `log_file_name` already exists, it is deleted using the `unlink()` method. Otherwise, no action is taken.

        4. It tries to configure the logging module to write the error messages to the `log_file_name`. The logging level is set to 'ERROR'.

        5. If an exception occurs while configuring the logging, a message 'could not log unhandled exception due to error' is printed.

        6. If the logging was successfully configured, an error message 'Uncaught exception' is logged using the `error()` method of the logging module. The exception information is passed using the `exc_info` parameter.

        7. The `sys.__excepthook__` function is called with the exception type, exception value, and traceback. This will print the exception information to the console.

        8. A message is printed to inform that if the exception could be logged, it is logged in './unhandled_exception.log' even if it does not appear in other log files.

        9. The program waits for the user to press enter to exit.

        10. Finally, the program exits with a status code of -1 using the `sys.exit()` function.
        """
        # self._basic_log_to_file(exc_type, exc_value, tb)
        if exc_type == LogFilePrepError:
            exit(-1)

        sys.__excepthook__(exc_type, exc_value, tb)

        self._log_exception(exc_type, exc_value, tb)

        print(self.__class__.UNCAUGHT_LOG_MSG.format(log_file_name=self.log_file_name))

        self.wait_for_key_and_exit()


class UncaughtExceptionHookEmail(UncaughtExceptionHook):
    def __init__(self, logger_admins: list, **kwargs):
        self.uncaught_logger_class = kwargs.pop('uncaught_logger_class', UncaughtLoggerEmail)

        super().__init__(uncaught_logger_class=self.uncaught_logger_class, **kwargs)

        self._validate_and_run_setup_email_method(logger_admins=logger_admins, **kwargs)

    def _validate_and_run_setup_email_method(self, logger_admins: list, **kwargs):
        if hasattr(self.uncaught_logger_class, 'setup_email_handler'):
            self.uncaught_logger_class.setup_email_handler(email_subject='placeholder',
                                                           logger_admins=logger_admins,
                                                           **kwargs)
        else:
            raise AttributeError('setup_email_handler method not found in uncaught_logger_class')

    def _log_exception(self, exc_type, exc_value, tb):
        self._check_and_initialize_new_email_file()

        self.uc_logger.error(msg='Uncaught exception', exc_info=(exc_type, exc_value, tb),
                             extra={'uncaught_exception': True})

        self._check_and_initialize_new_email_file()