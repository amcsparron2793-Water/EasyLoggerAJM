import sys
from logging import basicConfig, error
from pathlib import Path
from . import UncaughtLogger
from ..backend import LogFilePrepError


def clear_screen():
    """Clear the terminal/console screen on the current platform.

    Uses 'cls' on Windows and 'clear' on POSIX systems. Intended only for
    cosmetic use when prompting the user to exit after an uncaught exception.
    """
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

    @classmethod
    def set_sys_excepthook(cls, **kwargs):
        """
        Set a custom system exception hook using the provided arguments.

        This method creates an instance of the class using the given keyword
        arguments and sets its `show_exception_and_exit` method as the global
        system exception hook (`sys.excepthook`). This allows unhandled
        exceptions to be handled by the custom logger or handler defined
        within the class.

        The primary purpose of this method is to replace the default Python
        exception handling mechanism with a custom one that can log
        exceptions, display detailed error messages, or execute additional
        steps before termination of the program.

        :param kwargs: Keyword arguments that will be passed to the class
                       constructor.
        :return: An instance of the class configured as the system exception
                 hook.
        :rtype: ClassName
        """
        c = cls(**kwargs)
        sys.excepthook = c.show_exception_and_exit
        return c

    @staticmethod
    def wait_for_key_and_exit():
        """Prompt the user before exiting the process with a non-zero status.

        Primary path uses input() to wait for Enter. If stdin is not usable
        (e.g., UnicodeDecodeError/EOFError in some environments), on Windows a
        fallback using msvcrt.getch() is attempted; otherwise a short timed
        delay is used so the message can be seen before exit.
        Always terminates the process with exit code -1.
        """
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
        """Initialize a fresh email draft for the uncaught-exception emailer, if present.

        Some logger configurations attach an `emailer` object with a method
        `initialize_new_email()`. If detected, this method invokes it so that
        the next emitted record results in a new email rather than appending to
        a prior one.
        """
        if hasattr(self.uncaught_logger_class, 'emailer') and hasattr(self.uncaught_logger_class.emailer,
                                                                      'initialize_new_email'):
            self.uncaught_logger_class.emailer.initialize_new_email()

    def _basic_log_to_file(self, exc_type, exc_value, tb):
        """Write a minimal error log with traceback to a local file.

        Attempts to configure logging to write to './unhandled_exception.log' and
        logs the provided exception triple. If an existing file is present, it
        is removed first to avoid appending stale content. Errors during this
        process are swallowed and a console message is printed instead.
        """
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
        """Log the uncaught exception through the configured uncaught logger.

        Attaches extra={'uncaught_exception': True} so filters/handlers can
        route these records appropriately (e.g., to email).
        """
        self.uc_logger.error(msg='Uncaught exception', exc_info=(exc_type, exc_value, tb),
                             extra={'uncaught_exception': True})

    def show_exception_and_exit(self, exc_type, exc_value, tb):
        """Handle an uncaught exception, report it, and terminate the process.

        Behavior:
        - If the exception type is LogFilePrepError, exit immediately with -1.
        - Invoke the default sys.__excepthook__ to display the traceback.
        - Log the exception via the configured uncaught logger with
          extra={'uncaught_exception': True} so filters/handlers can route it
          (e.g., to email). A minimal file log helper exists but is disabled by default.
        - Inform the user where a basic log would be written.
        - Prompt the user before exiting with status -1.
        """
        # self._basic_log_to_file(exc_type, exc_value, tb)
        if exc_type == LogFilePrepError:
            exit(-1)

        sys.__excepthook__(exc_type, exc_value, tb)

        self._log_exception(exc_type, exc_value, tb)

        print(self.__class__.UNCAUGHT_LOG_MSG.format(log_file_name=self.log_file_name))

        self.wait_for_key_and_exit()

