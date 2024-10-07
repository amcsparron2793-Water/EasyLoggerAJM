import unittest
from unittest.mock import patch
from EasyLoggerAJM.EasyLoggerAJM import EasyLogger, _EasyLoggerCustomLogger


class TestEasyLoggerCustomLogger(unittest.TestCase):
    def setUp(self):
        self.logger = EasyLogger().UseLogger().logger  # ._EasyLoggerCustomLogger("TestLogger")
        self.log_methods = {
            'info': self.logger.info,
            'debug': self.logger.debug,
            'warning': self.logger.warning,
            'error': self.logger.error,
            'critical': self.logger.critical
        }

    @patch('builtins.print')
    def test_print_msg_for_all_log_levels(self, mock_print):
        should_print = True
        for level, method in self.log_methods.items():
            with self.subTest(level=level):
                with patch.object(_EasyLoggerCustomLogger, '_print_msg',
                                  wraps=_EasyLoggerCustomLogger._print_msg) as mock_print_msg:
                    method("Test message", print_msg=should_print)
                    mock_print_msg.assert_called_once_with("Test message", print_msg=should_print)
                    mock_print.assert_called_once_with("Test message")
                    mock_print.reset_mock()

    @patch('builtins.print')
    def test_not_print_msg_for_all_log_levels(self, mock_print):
        should_print = False
        for level, method in self.log_methods.items():
            with self.subTest(level=level):
                with patch.object(_EasyLoggerCustomLogger, '_print_msg',
                                  wraps=_EasyLoggerCustomLogger._print_msg) as mock_print_msg:
                    method("Test message", print_msg=should_print)
                    mock_print_msg.assert_called_once_with("Test message", print_msg=should_print)
                    mock_print.assert_not_called()
                    mock_print.reset_mock()

    # these are now deprecated
    @patch('builtins.print')
    def test_internal_print_call_within_print_msg(self, mock_print):
        with patch.object(_EasyLoggerCustomLogger, '_print_msg',
                          wraps=_EasyLoggerCustomLogger._print_msg) as mock_print_msg:
            # Call the info method to execute _print_msg
            self.logger.info("Test message", print_msg=True)

            # Assert that _print_msg was called within the scope
            mock_print_msg.assert_called_once_with("Test message", print_msg=True)
            # Now check that the print function was called within _print_msg
            mock_print.assert_called_once_with("Test message")

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
