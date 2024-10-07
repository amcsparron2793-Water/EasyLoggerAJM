import unittest
from unittest.mock import patch
from EasyLoggerAJM.EasyLoggerAJM import EasyLogger, _EasyLoggerCustomLogger


class TestEasyLoggerCustomLogger(unittest.TestCase):
    def setUp(self):
        self.logger = EasyLogger().UseLogger().logger  # ._EasyLoggerCustomLogger("TestLogger")

    @patch.object(_EasyLoggerCustomLogger, '_print_msg')
    def test_info_print(self, mock_print):
        self.logger.info("info_msg", stack_info=True, print_msg=True)
        mock_print.assert_called_once_with("info_msg", print_msg=True)

    @patch.object(_EasyLoggerCustomLogger, '_print_msg')
    def test_warning_print(self, mock_print):
        self.logger.warning("warning_msg", stack_info=True, print_msg=True)
        mock_print.assert_called_once_with("warning_msg", print_msg=True)

    @patch.object(_EasyLoggerCustomLogger, '_print_msg')
    def test_error_print(self, mock_print):
        self.logger.error("error_msg", stack_info=True, print_msg=True)
        mock_print.assert_called_once_with("error_msg", print_msg=True)

    @patch.object(_EasyLoggerCustomLogger, '_print_msg')
    def test_debug_print(self, mock_print):
        self.logger.debug("debug_msg", stack_info=True, print_msg=True)
        mock_print.assert_called_once_with("debug_msg", print_msg=True)

    @patch.object(_EasyLoggerCustomLogger, '_print_msg')
    def test_critical_print(self, mock_print):
        self.logger.critical("critical_msg", stack_info=True, print_msg=True)
        mock_print.assert_called_once_with("critical_msg", print_msg=True)


if __name__ == "__main__":
    unittest.main()
