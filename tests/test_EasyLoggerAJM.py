import unittest
import re
from datetime import datetime

from EasyLoggerAJM.EasyLoggerAJM import EasyLogger


class TestEasyLogger(unittest.TestCase):

    def setUp(self):
        self.logger = EasyLogger(project_name="TestProject", root_log_location="./test_logs")
        self.test_dir = self.logger._root_log_location

    @classmethod
    def tearDownClass(cls):
        print("DONT FORGET TO REMOVE TEST DIRS")

    def test_creation(self):
        self.assertIsInstance(self.logger, EasyLogger)

    def test_project_name(self):
        self.assertEqual(self.logger.project_name, "TestProject")

    def test_default_format(self):
        self.assertEqual(self.logger.DEFAULT_FORMAT, '%(asctime)s | %(name)s | %(levelname)s | %(message)s')

    def test_inner_log_fstructure(self):
        self.assertIsNotNone(self.logger.inner_log_fstructure)

    def test_log_location(self):
        self.assertTrue(re.match(f"{self.test_dir}.*", self.logger.log_location))

    def test_useLogger_creation(self):
        logger_cl = EasyLogger.UseLogger(project_name="TestProject2", root_log_location=f"{self.test_dir}2")
        self.assertIsInstance(logger_cl, EasyLogger)
        self.assertEqual(logger_cl.project_name, "TestProject2")
        self.assertTrue(re.match(f"{self.test_dir}2.*", logger_cl.log_location))

    def test_make_file_handlers(self):
        self.logger.make_file_handlers()
        self.assertIsNotNone(self.logger.logger.handlers)
        self.assertGreaterEqual(len(self.logger.logger.handlers), len(self.logger.file_logger_levels))

    def test_logger_level_normalization_with_kwargs(self):
        self.logger = EasyLogger(project_name="TestProject", root_log_location="./test_logs", file_logger_levels=['DEBUG', 'INFO','WARNING', 'ERROR'])
        self.logger.make_file_handlers()
        for x in self.logger.file_logger_levels:
            self.assertIn(x, [x.level for x in self.logger.logger.handlers])
            self.assertIsInstance(x, int)

    def test_is_daily_log_spec(self):
        dls_logger = EasyLogger(project_name="TestProject3",
                                root_log_location=f"{self.test_dir}3",
                                is_daily_log_spec=True)
        dls_logger.make_file_handlers()
        self.assertEqual(dls_logger.inner_log_fstructure.split('/')[0], dls_logger.DAILY_LOG_SPEC_FORMAT)

    def test_given_dictionary_when_getting_log_spec_then_return_value(self):
        self.logger._log_spec = {'name': 'minute'}
        self.assertEqual(self.logger.log_spec, self.logger.LOG_SPECS['minute'])

    def test_given_incorrect_key_dictionary_when_getting_log_spec_then_raise_exception(self):
        self.logger._log_spec = {'wrong_key': 'minute'}
        with self.assertRaises(KeyError):
            self.logger.log_spec

    def test_given_string_when_getting_log_spec_then_return_value(self):
        self.logger._log_spec = 'minute'
        self.assertEqual(self.logger.log_spec, self.logger.LOG_SPECS['minute'])

    def test_given_wrong_string_when_getting_log_spec_then_raise_exception(self):
        self.logger._log_spec = 'wrong_string'
        with self.assertRaises(AttributeError):
            self.logger.log_spec

    def test_given_none_when_getting_log_spec_then_return_default_value(self):
        self.logger._log_spec = None
        self.assertEqual(self.logger.log_spec, self.logger.LOG_SPECS['minute'])



if __name__ == "__main__":
    unittest.main()

