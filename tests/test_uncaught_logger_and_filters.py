import logging
import unittest
from logging import FileHandler, StreamHandler
from pathlib import Path
from unittest.mock import Mock

from EasyLoggerAJM.UncaughtExceptionHook.uncaught_logger import (
    UncaughtLogger,
    UncaughtLoggerEmail,
)
from EasyLoggerAJM.UncaughtExceptionHook.filters import (
    UncaughtExceptionFilter,
    NoEmailFilter,
    CaughtExceptionFilter,
)


class DummyEmailer:
    def __init__(self, logger=None, **kwargs):
        self.logger = logger


class TestUncaughtLogger(unittest.TestCase):
    UL_FOLDER_PATH = './test_logs_ul'

    # @classmethod
    # def tearDownClass(cls):
    #     import shutil
    #     try:
    #         shutil.rmtree(Path(cls.UL_FOLDER_PATH))
    #     except PermissionError as e:
    #         print(e)
    #         pass

    def test_callable_returns_logger(self):
        from EasyLoggerAJM.easy_logger import EasyLogger
        with unittest.mock.patch.object(EasyLogger, 'post_handler_setup', lambda self: None):
            ul = UncaughtLogger(project_name='T', root_log_location=self.__class__.UL_FOLDER_PATH)
        self.assertIsInstance(ul(), logging.Logger)

    def test_make_file_handlers_disabled(self):
        from EasyLoggerAJM.easy_logger import EasyLogger
        with unittest.mock.patch.object(EasyLogger, 'post_handler_setup', lambda self: None):
            ul = UncaughtLogger(project_name='T', root_log_location=self.__class__.UL_FOLDER_PATH)
        self.assertIsNone(ul.make_file_handlers())

    def test_setup_clean_handlers_removes_file_handlers_only(self):
        ul = UncaughtLogger(project_name='T', root_log_location=self.__class__.UL_FOLDER_PATH)
        # attach one file handler and one stream handler
        fh = FileHandler(filename='tmp_dummy.log', encoding='utf-8')
        sh = StreamHandler()
        ul.logger.addHandler(fh)
        ul.logger.addHandler(sh)
        cleaned = ul.setup_clean_handlers()
        # file handler removed, stream remains
        self.assertTrue(all(not isinstance(h, FileHandler) for h in cleaned))
        self.assertTrue(any(isinstance(h, StreamHandler) for h in cleaned))
        # Ensure we can still assign cleaned handlers without error
        ul.logger.handlers = cleaned


class TestUncaughtLoggerEmail(unittest.TestCase):
    ULE_FOLDER_PATH = './test_logs_ule'

    # @classmethod
    # def tearDownClass(cls):
    #     import shutil
    #     try:
    #         shutil.rmtree(Path(cls.ULE_FOLDER_PATH))
    #     except PermissionError as e:
    #         print(e)
    #         pass

    def test_emailer_attached(self):
        from EasyLoggerAJM.easy_logger import EasyLogger
        with unittest.mock.patch.object(EasyLogger, 'post_handler_setup', lambda self: None):
            ule = UncaughtLoggerEmail(emailer_class=DummyEmailer, project_name='T',
                                      root_log_location=self.__class__.ULE_FOLDER_PATH)
        self.assertTrue(hasattr(ule, 'emailer'))
        self.assertIsInstance(ule.emailer, DummyEmailer)
        self.assertIsNotNone(ule.emailer.logger)


class TestFilters(unittest.TestCase):
    def setUp(self):
        self.logger = logging.getLogger('test_filters')
        self.logger.setLevel(logging.DEBUG)
        self.stream = logging.StreamHandler()
        self.logger.handlers = [self.stream]

    def _make_record(self, level=logging.INFO, msg='m', **extra):
        record = self.logger.makeRecord(self.logger.name, level, __file__, 0, msg, args=(), exc_info=None)
        for k, v in extra.items():
            setattr(record, k, v)
        return record

    def test_uncaught_exception_filter(self):
        f = UncaughtExceptionFilter()
        r1 = self._make_record(uncaught_exception=True)
        r2 = self._make_record(uncaught_exception=False)
        self.assertTrue(f.filter(r1))
        self.assertFalse(f.filter(r2))

    def test_no_email_filter(self):
        f = NoEmailFilter()
        r1 = self._make_record(no_email=True)
        r2 = self._make_record(no_email=False)
        self.assertFalse(f.filter(r1))
        self.assertTrue(f.filter(r2))

    def test_caught_exception_filter(self):
        f = CaughtExceptionFilter()
        r1 = self._make_record(uncaught_exception=True)
        r2 = self._make_record(uncaught_exception=False)
        self.assertFalse(f.filter(r1))
        self.assertTrue(f.filter(r2))


if __name__ == '__main__':
    unittest.main()