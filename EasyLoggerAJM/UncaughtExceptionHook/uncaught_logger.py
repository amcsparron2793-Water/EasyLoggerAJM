from EasyLoggerAJM import EasyLogger
from .filters import UncaughtExceptionFilter


# FIXME: WIP
class UncaughtLogger(EasyLogger):
    def __init__(self, **kwargs):
        # Initialize base logger (may attach default handlers)
        kwargs.setdefault('log_spec', 'hourly')
        super().__init__(**kwargs)
        # self.emailer = PyEmailer(False, False, logger=self.logger)
        # Ensure this special logger only handles uncaught exceptions and does not interfere with others
        self.logger.filters.clear()
        self.logger.addFilter(UncaughtExceptionFilter())

        self.logger.handlers = self.setup_clean_handlers()

    def setup_clean_handlers(self):
        # Remove any file-based handlers that the base class may have attached; we only want email here
        # Keep non-file handlers (e.g., SMTP/email handlers) intact
        cleaned_handlers = []
        for h in list(self.logger.handlers):
            try:
                from logging import FileHandler
                from logging.handlers import TimedRotatingFileHandler
                is_file = isinstance(h, FileHandler) or isinstance(h, TimedRotatingFileHandler)
            except Exception:
                is_file = False
            if not is_file:
                cleaned_handlers.append(h)
        return cleaned_handlers

    def _set_logger_class(self, **kwargs):
        return super()._set_logger_class(logger_name=kwargs.pop('logger_name',
                                                                'uncaught_logger'), **kwargs)

    def make_file_handlers(self, **kwargs):
        """Override to disable creation of file handlers for the uncaught-exception logger."""
        return None
