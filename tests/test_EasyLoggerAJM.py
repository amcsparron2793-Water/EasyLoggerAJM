import unittest
import re
from datetime import datetime
from os.path import dirname

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


if __name__ == "__main__":
    unittest.main()
