import logging
import unittest
from io import StringIO
import sys

from EasyLoggerAJM.logger_parts.handlers import StreamHandlerIgnoreExecInfo


class TestStreamHandlerIgnoreExecInfo(unittest.TestCase):

    def setUp(self):
        # Set up a StreamHandlerIgnoreExecInfo with a StringIO as its stream.
        self.stream = StringIO()
        self.handler = StreamHandlerIgnoreExecInfo(self.stream)

    def tearDown(self):
        # Close the StringIO stream and the handler after each test.
        self.stream.close()
        self.handler.close()

    def test_emit_without_exc_info(self):
        # If the record has no exc_info, the message should still be logged normally.
        record = logging.LogRecord("my_logger", logging.INFO, "dummy_path", 0, "Hello, world!", None, None)
        self.handler.emit(record)
        self.assertEqual(self.stream.getvalue(), "Hello, world!\n")

    def test_emit_with_exc_info(self):
        # If the record has exc_info, it should be temporarily removed before logging.
        try:
            raise Exception("This is a dummy exception")
        except Exception:
            record = logging.LogRecord("my_logger", logging.ERROR, "dummy_path", 0,
                                       "An error has occurred!", None, sys.exc_info())
        self.handler.emit(record)
        self.assertNotIn("This is a dummy exception", self.stream.getvalue())

    def test_emit_restores_exc_info(self):
        # exc_info should be restored to the record after logging.
        try:
            raise Exception("This is another dummy exception")
        except Exception:
            record = logging.LogRecord("my_logger", logging.ERROR, "dummy_path", 0,
                                       "Another error has occurred!", None, sys.exc_info())
            old_exc_info = record.exc_info
            self.handler.emit(record)
            self.assertEqual(old_exc_info, record.exc_info)


if __name__ == '__main__':
    unittest.main()