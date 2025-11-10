from logging import Filter


class UncaughtExceptionFilter(Filter):
    def filter(self, record):
        """Allow uncaught exceptions to pass."""
        return getattr(record, "uncaught_exception", False)  # Only logs marked uncaught_exception=True


class NoEmailFilter(Filter):
    """Filter to block records that have 'no_email' flag in extra dict."""
    def filter(self, record):
        # Block the record if it has no_email=True in extra
        return not getattr(record, 'no_email', False)


class CaughtExceptionFilter(Filter):
    def filter(self, record):
        """Allow uncaught exceptions to pass."""
        return not getattr(record, "uncaught_exception", False)  # Only logs marked uncaught_exception=False
